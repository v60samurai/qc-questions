# Canonical Subagent Prompt — Blind QC Worker

This is the prompt the main agent dispatches to each parallel subagent during xlsx-batch QC. It is the ONLY way to ensure blind-solve AND blind-difficulty-rate discipline: a subagent invoked in a fresh context cannot have read the marked `correctOption` OR the marked `difficulty` for the rows it judges, even if it tried.

## Batching & Model Routing

- One subagent per batch of **5–8 questions**. Smaller batches = more parallelism but more dispatch overhead; 6 is a good default. For files of ≤ 8 rows, use a SINGLE subagent over the whole file. Never one-per-row — that 7x's the cost with no quality benefit.
- Dispatch **all batches in a single message** (multiple tool calls in parallel) so they run concurrently.
- For an 18-row file: 3 subagents × 6 rows. For 100 rows: 15–20 subagents.
- Cap parallel subagents at ~10 per dispatch to avoid rate-limit thrash; queue further batches if needed.
- **Model routing: subagent workers and verifiers run on Sonnet** (`model: "sonnet"` on the Agent tool call). The main agent stays on the conversation's default (typically Opus) for composition. Sonnet is ~5x cheaper and is plenty capable for the solve + intrinsic-complexity scoring; the discipline lives in this prompt, not in raw model headroom.

## Inputs the main agent prepares per batch

Write the batch's questions to a temp JSON file (`/tmp/qc_batch<N>.json`) **without `correctOption` AND without marked `difficulty`**. Both audit targets live separately in `/tmp/qc_keys.json` which the subagent must not read.

Pass to the subagent:
- The MQC definition (one sentence; same MQC for every batch in a run)
- The batch file path
- The keys file path (only so the subagent can be told not to read it — fail-loud)

## Canonical Prompt (paste into Agent tool's `prompt` field)

```
You are doing high-stakes QC of assessment MCQs. You are one of several
parallel workers; you judge the rows in your batch only.

MQC (minimally-qualified candidate): <ONE-SENTENCE MQC DEFINITION>

Your job: Read <BATCH_FILE_PATH>. Each entry has row, content,
option1..option6, subject, topics, questionType, and other metadata.
You do NOT have access to correctOption OR the marked difficulty for any
row. BOTH are audit targets; rating either of them blind is the entire
point of this dispatch.

HARD RULE: do not, under any circumstance, read <KEYS_FILE_PATH>. Do a
genuinely BLIND solve AND a genuinely BLIND difficulty rating.

For each question, return:
- row: <int>
- my_answer: option<N>
- my_reasoning: 2 sentences. Name the rule/concept tested + why each
  non-chosen option is wrong (one phrase each).
- multiple_correct_risk: yes|no — is a second option also defensibly
  correct?
- ambiguity_risk: yes|no — stem ambiguous, trick, or missing context?
- my_blind_difficulty: EASY|MEDIUM|HARD — your committed band based on
  intrinsic solve complexity (count of conceptual steps an MQC must
  execute). Commit this before you do anything else with the row.
- conceptual_steps: <int> — the count that justifies the band:
    1 step / no abstraction → EASY
    2 steps / one non-trivial choice → MEDIUM
    3+ steps / multi-constraint / domain abstraction → HARD
- conceptual_steps_note: <one line> — describe the steps the MQC walks
  through. This is your provenance — the main agent reads it to verify
  the band is structurally earned, not vibes.
- angoff_pct: <int 0-100> — of 100 MQCs as defined above, how many would
  get this correct?
- angoff_reasoning: 1 sentence on which misconception trips MQCs and
  ~what % is tripped.
- proxy_a: 1-5 (discrimination — 1=surface heuristics; 3=two distinct
  misconceptions tested; 5=graded distractor ladder).
- proxy_c: 1-5 (effective guess floor — 1=3 functioning distractors;
  3=only 1 functioning; 5=broken).
- confidence: HIGH|MED|LOW.

- proposed_edits: array of {field, from, to, why}
    These are CORRECTNESS and DISCRIMINATION edits only — issues you can
    detect without the marked answer key and without the marked difficulty
    band. Difficulty-alignment edits live in a separate field below
    (alignment_prescriptions) because they depend on the marked band
    you can't see.

    field: one of content | option1..option6
           (NEVER subject/topics/difficulty/correctOption — subject/topics/
           difficulty are the spec; correctOption can only be flipped by
           the main agent after key reveal).
    from:  the EXACT verbatim current value of that cell (paste-able).
    to:    the EXACT verbatim replacement value (paste-able).
    why:   one phrase tying the edit to the issue it fixes.

  Write the edit yourself — you have full content visibility. Do NOT
  defer to a human or to the main agent.

  HARD LAYER-SEPARATION RULE (read before using the table):

    Difficulty (IRT's b) measures the INTRINSIC SOLVE COMPLEXITY of the
    item — # of conceptual steps an MQC must execute, depth of
    abstraction, domain knowledge level. It lives in the STEM.

    Discrimination (IRT's a) measures how well the item separates
    high-ability from low-ability candidates given the same intrinsic
    complexity. It lives in the DISTRACTORS.

    These are separate parameters. To fix a discrimination problem you
    REWRITE DISTRACTORS in proposed_edits. To fix a difficulty mismatch
    you REWRITE THE STEM via alignment_prescriptions below. NEVER swap
    a distractor to "fix" difficulty — the swap moves empirical p-value
    by catching carelessness, but it does NOT change the latent
    b-parameter. Conflating the two is parameter contamination.

  Prescription table for proposed_edits (correctness + discrimination):

  | Issue you detected | Edit to write in proposed_edits |
  |---|---|
  | multiple_correct_risk: yes | Rewrite the second-defensible option so it no longer satisfies the stem. (correctness layer) |
  | ambiguity_risk: yes | Rewrite the ambiguous span in the stem with a tighter version. (correctness layer) |
  | proxy_a ≤ 2 — poor discrimination | Rewrite 1-2 distractors so each targets a *distinct, named* misconception the MQC would plausibly hold. State the misconception in `why`. (discrimination layer = distractors) |
  | proxy_c ≥ 3 — guess floor inflated | Replace each obvious-throwaway distractor with a plausible wrong answer mapped to a real misconception. (discrimination layer = distractors) |
  | construct_mismatch (e.g., missing chart / wrong subject) | proposed_edits: [] AND confidence: LOW. This is the ONLY case where empty proposed_edits is allowed — the obstruction is external to the QC pipeline. |

  (You do NOT see the marked correctOption, so do not write correctOption
  flip edits — the main agent owns that one cross-row case on key reveal.)

- alignment_prescriptions: { to_one_band_harder: {...}|null, to_one_band_easier: {...}|null }

    This is a forward-looking PAIR of stem-edit candidates. You don't know
    the marked difficulty band, so you can't know which direction (if any)
    will be needed. You write BOTH directional candidates and the main
    agent — after revealing the marked band — picks the one that closes
    the gap with my_blind_difficulty, or neither if my_blind_difficulty
    already matches.

    For EACH candidate, emit either:
      { field: "content",
        from: "<exact current stem>",
        to:   "<exact rewritten stem>",
        why:  "<one phrase: adds/removes the Nth conceptual step — name it>" }
    OR null, if no defensible one-band move exists within the marked
    subject/topics (e.g., a single-step arithmetic item that cannot be
    made HARD without leaving its topic, or a 4-concept item already at
    HARD floor).

    Layer rule restated: alignment_prescriptions edits ALWAYS target the
    STEM (`field: "content"`). Never propose alignment via a distractor
    swap — that's parameter contamination.

    to_one_band_harder: add ONE conceptual step. Patterns:
      - insert a purity / efficiency adjustment
      - add a sub-group split
      - introduce a compound ratio
      - add a reverse-direction twist
      - add an extra unit conversion
      - add a target-vs-input distinction
      - add a second constraint MQC must reason about
      The answer may change — note that in `why` so the main agent
      knows a correctOption flip may follow on key reveal.

    to_one_band_easier: remove ONE conceptual step. Patterns:
      - pre-compute one intermediate value
      - state a converted unit instead of asking the candidate to convert
      - drop one of the chained constraints
      - remove a target-vs-input distinction
      - replace a compound ratio with a single ratio
      The answer may change — same note applies.

    If neither direction is defensible within subject/topics, emit both
    as null and set confidence: LOW. The main agent will surface this as
    a construct-mismatch escalation if the marked band requires alignment.

  HARD RULE — every row with any of the correctness/discrimination
  issues above MUST have a non-empty proposed_edits array unless
  confidence: LOW AND the obstruction is external (missing chart /
  malformed source cell / construct mismatch). Flagging drift for
  human review when you have full content visibility is a failure mode,
  not a deferral. The alignment_prescriptions pair is REQUIRED on every
  row regardless of correctness/discrimination state — if both directions
  are null, set confidence: LOW.

Output: a single JSON array. Pure JSON, no markdown, no prose, parseable.

Reference Angoff-band mapping (do not output): EASY=75–95%,
MEDIUM=50–75%, HARD=25–50%.

Honesty discipline:
- Unsure between two options → confidence: LOW AND multiple_correct_risk: yes.
- MQC would get >95% → floor item; flag implicitly via high angoff_pct.
- MQC would get <25% → likely you got it wrong OR the item is at the
  guess floor; flag via confidence: LOW.
- For quantitative items: solve by two independent methods. If they
  disagree, confidence: LOW.

Constraint on the spec:
- The marked `subject`, `topics`, and `difficulty` are FIXED targets — the
  PM-planned spec. You may NOT propose edits to these fields. Edit
  `content` / `option1..option6` to align the item TO the marked spec.
- If the item's construct fundamentally mismatches the marked subject
  or topics (e.g., it's an arithmetic problem tagged Verbal Ability),
  add a field `construct_mismatch: "<one-line description>"` to your
  output, set confidence: LOW, and emit `proposed_edits: []` AND
  `alignment_prescriptions: { to_one_band_harder: null, to_one_band_easier: null }`.
  The main agent will surface this as an escalation rather than retagging.

Return under 1500 words.

Example output for one row (illustrates my_blind_difficulty + alignment_prescriptions pair):

[
  {
    "row": 5,
    "my_answer": "option1",
    "my_reasoning": "Ratio 3:22 sums to 25 parts; fertilizer = (3/25) × 475 = 57 L. Cross-check: 475/25 = 19 L/part, 19 × 3 = 57. Other options trap students who misread the ratio.",
    "multiple_correct_risk": "no",
    "ambiguity_risk": "no",
    "my_blind_difficulty": "EASY",
    "conceptual_steps": 1,
    "conceptual_steps_note": "Single-concept solve: apply a given ratio to a total. Three arithmetic ops (sum→divide→multiply) collapse into one conceptual step (proportional allocation).",
    "angoff_pct": 85,
    "angoff_reasoning": "Intrinsic solve is 3 elementary ops; a prepared MQC handles it in seconds, so Angoff is high-EASY band.",
    "proxy_a": 3,
    "proxy_c": 2,
    "confidence": "HIGH",
    "proposed_edits": [],
    "alignment_prescriptions": {
      "to_one_band_harder": {
        "field": "content",
        "from": "<p>Geetanjali prepares a drip-irrigation solution where fertilizer concentrate and water are mixed in the ratio <strong>3 : 22</strong>. The total solution required for one field section is <strong>475 litres</strong>. How many litres of fertilizer concentrate are needed?</p>",
        "to": "<p>Geetanjali needs <strong>475 litres</strong> of a drip-irrigation mix where <em>pure</em> fertilizer concentrate and water are combined in the ratio <strong>3 : 22</strong>. Her stock fertilizer is only <strong>80% pure</strong> (the remaining 20% is inert filler excluded from the 475 L target). How many litres of stock concentrate must she add?</p>",
        "why": "adds purity-adjustment as a second conceptual step (proportional allocation → purity scaling); answer changes from 57 L to 71.25 L — main agent will need to flip correctOption on key reveal if marked is MEDIUM and this branch is taken"
      },
      "to_one_band_easier": null
    }
  }
]

Notes on the example:
- my_blind_difficulty was committed as EASY based on 1 conceptual step. The
  conceptual_steps_note is the provenance the main agent reads to verify.
- proposed_edits is empty because no correctness or discrimination flags
  fired.
- to_one_band_harder is supplied: if marked is MEDIUM, main agent picks it
  up and applies the stem rewrite. The `why` warns about the answer change.
- to_one_band_easier is null because you can't make a 1-step item easier
  without leaving the marked topic.
- The alignment stem rewrite lives in `content`, NOT in a distractor. The
  stem rewrite is what moves intrinsic solve complexity.
```

## What the Main Agent Does After Subagents Return

The main agent is a **pass-through composer**, not an editor. The subagent
has full content visibility and is the authority on what to write into
each cell — the main agent re-validates correctness and dual-target
alignment, but it does not regenerate edits.

1. Collect all subagent JSON outputs into a single list (key = row).
2. Read `/tmp/qc_keys.json` (now and only now — the main agent's context did see `correctOption` AND marked `difficulty` during xlsx parsing, but the parse script kept them in a separate block).
3. For each row, compose the verdict:
   - **correctness:** compare `my_answer` to the marked `correctOption`.
     - match + no `multiple_correct_risk` + no `ambiguity_risk` → no correctness_issue
     - match BUT `multiple_correct_risk: yes` → correctness_issue = "Two defensibly-correct options"
     - mismatch + HIGH confidence → correctness_issue = "Marked X but Y is the only defensible answer"; **ADD a `correctOption` flip edit** (this is the canonical cross-row exception — the subagent could not write this edit because it never saw the marked key)
     - mismatch + LOW confidence → escalate (confidence: LOW, no auto-flip)
     - `ambiguity_risk: yes` → correctness_issue = "Stem is ambiguous: …"
   - **difficulty:** compare `my_blind_difficulty` to the marked `difficulty`.
     - match → no difficulty_issue, no alignment edit added
     - `my_blind_difficulty` one band easier than marked (e.g., blind=EASY, marked=MEDIUM) → difficulty_issue = "Blind-rated {X}, marked {Y} → align via stem-add"; **PASS THROUGH `subagent.alignment_prescriptions.to_one_band_harder`** as a verdict edit (do NOT regenerate). If it's null → confidence: LOW, no auto-edit, surface as escalation.
     - `my_blind_difficulty` one band harder than marked (e.g., blind=HARD, marked=MEDIUM) → difficulty_issue = "Blind-rated {X}, marked {Y} → align via stem-remove"; **PASS THROUGH `subagent.alignment_prescriptions.to_one_band_easier`** as a verdict edit. If it's null → confidence: LOW.
     - two-band mismatch (blind=EASY, marked=HARD or vice versa) → confidence: LOW, no auto-edit; surface as construct-drift escalation. A one-band stem edit won't bridge a two-band gap defensibly.
     - **NEVER re-rate.** If `my_blind_difficulty` ≠ marked, the subagent's rating is the diagnostic; the marked band is the target; the gap closes via the appropriate alignment_prescriptions branch, never via "on second look it's actually MEDIUM".
   - **status:** ALIGNED iff both issues null and no edits added; otherwise NEEDS_EDITS.
   - **edits:** `subagent.proposed_edits` PASS-THROUGH, plus optional `correctOption` flip (correctness-side cross-row exception), plus optional alignment stem edit picked from `subagent.alignment_prescriptions` (difficulty-side cross-row exception). Do NOT regenerate, rewrite, or rephrase the subagent's edits — they are paste-able as-is.
   - **confidence:** `subagent.confidence` PASS-THROUGH unless an alignment branch was needed and the corresponding `alignment_prescriptions` entry was null, in which case down-grade to LOW.
4. Write `verdicts.json` (list of lean verdict objects).
5. Run `python3 scripts/qc_xlsx.py write <input.xlsx> verdicts.json <output.xlsx>`.

**The only edits the main agent adds on top of `subagent.proposed_edits`** are the two cross-row corrections the subagent structurally could not write: the `correctOption` flip on key mismatch, and the chosen alignment stem edit on difficulty mismatch. Both come from the subagent's existing output — the main agent only chooses which branch applies, never invents the edit text.

## Why This Structure Matters

- **Both audit targets are structurally blind.** A subagent in a fresh context literally cannot have seen the row's `correctOption` OR marked `difficulty` — its only inputs are the batch JSON (key-and-difficulty stripped) and the prompt. This eliminates the dominant LLM failure mode on QC twice over: rationalising the marked answer AND rationalising the marked difficulty band.
- **Single round-trip.** The `alignment_prescriptions` pair lets the subagent emit both directional stem-edit candidates in one pass, so the main agent doesn't need a second dispatch on difficulty mismatch.
- **Pass-through preserves provenance.** Every edit on the verdict came from a context that didn't see the audit target it's aligning to. Regeneration at compose time would leak that provenance.
- **Parallelism reduces wall-clock time ~Nx** with N subagents.
- **IRT reasoning stays internal to the subagent.** The lean verdict the main agent composes never surfaces Angoff numbers — those served their purpose at decision time.
- **Quant/logic gets two-method self-consistency for free** because the prompt mandates it; failures surface as `confidence: LOW` which the main agent treats as P0.
