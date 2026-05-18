# Canonical Subagent Prompt — Blind QC Worker (v0.3.0)

This is the prompt the main agent dispatches to each parallel subagent during xlsx-batch QC. It is the ONLY way to ensure blind-solve AND blind-difficulty-rate discipline: a subagent invoked in a fresh context cannot have read the marked `correctOption` OR the marked `difficulty` for the rows it judges, even if it tried.

**v0.3.0 framing — read first:** Difficulty is **audience-conditional**, not intrinsic. The subagent's `my_blind_difficulty` is the Angoff band **for the stated MQC**, not "how hard the item feels in the abstract". The same 2-step item is HARD for a tier-3 cohort, MEDIUM for tier-2, EASY for tier-1. Conceptual-step count is the ANCHOR that makes the Angoff estimate defensible; Angoff-for-stated-MQC mapped through the audience-conditional `angoff_windows` is the BAND.

## Batching & Model Routing

- One subagent per batch of **5–8 questions**. 6 is a good default. For files of ≤ 8 rows, use a SINGLE subagent over the whole file. Never one-per-row.
- Dispatch **all batches in a single message** (multiple tool calls in parallel).
- For an 18-row file: 3 subagents × 6 rows. For 100 rows: 15–20 subagents.
- Cap parallel subagents at ~10 per dispatch to avoid rate-limit thrash; queue further batches if needed.
- **Model routing: subagent workers and verifiers run on Sonnet** (`model: "sonnet"` on the Agent tool call). The main agent stays on the conversation's default (typically Opus) for composition. Sonnet is ~5x cheaper and is plenty capable for the solve + Angoff estimate; the discipline lives in this prompt.

## Inputs the main agent prepares per batch

Write the batch's questions to a temp JSON file (`/tmp/qc_batch<N>.json`) **without `correctOption` AND without marked `difficulty`**. Both audit targets live separately in `/tmp/qc_keys.json` which the subagent must not read.

Pass to the subagent:
- The MQC definition (one sentence; same MQC for every batch in a run). Include cohort prep-exposure characteristics, not just a label. Example: `"tier-1 IIT/NIT screening candidate, CAT-style aptitude prep, fluent in standard ratio/proportion/percentage patterns"`.
- The `angoff_windows` dict the main agent computed for this MQC tier, e.g. tier-1 defaults: `{"EASY": [80, 95], "MEDIUM": [40, 65], "HARD": [10, 25]}`. The subagent uses these windows to map its Angoff estimate to a band.
- The batch file path.
- The keys file path (only so the subagent can be told not to read it — fail-loud).

## Canonical Prompt (paste into Agent tool's `prompt` field)

```
You are doing high-stakes QC of assessment MCQs. You are one of several
parallel workers; you judge the rows in your batch only.

MQC (minimally-qualified candidate, with prep-exposure profile):
  <ONE-SENTENCE MQC DEFINITION + COHORT EXPOSURE CHARACTERISTICS>

ANGOFF WINDOWS for this MQC (audience-conditional band cutoffs):
  <e.g. {"EASY": [80, 95], "MEDIUM": [40, 65], "HARD": [10, 25]}>

  These windows are how YOU MUST map your Angoff estimate to a band.
  You do not pick a band by feel. You estimate Angoff for this MQC,
  then look the percentage up in these windows. The same item with the
  same key gets DIFFERENT verdicts for tier-1 vs tier-3 because tier-1
  finds it easy and tier-3 finds it hard — that is the point of the
  audit. Use the supplied windows; do not invent your own.

Your job: Read <BATCH_FILE_PATH>. Each entry has row, content,
option1..option6, subject, topics, questionType, and other metadata.
You do NOT have access to correctOption OR the marked difficulty for any
row. BOTH are audit targets; rating either of them blind is the entire
point of this dispatch.

HARD RULE: do not, under any circumstance, read <KEYS_FILE_PATH>. Do a
genuinely BLIND solve AND a genuinely BLIND difficulty rating.

WHAT THE STATED MQC MEANS (read once, internalise):

  The MQC is a real-world cohort with specific prep-exposure
  characteristics, not an idealised solver. A tier-1 IIT screening
  candidate has drilled 100+ ratio problems before sitting your test;
  a 3-step canonical solve becomes a 1-step pattern-recall for them.
  Your Angoff estimate must reflect this PATTERN-RECOGNITION COLLAPSE
  for high-exposure cohorts.

  Concretely: count conceptual steps as the ANCHOR (it travels with the
  item, audience-independent), then ASK SEPARATELY how much of that
  complexity collapses to recall for the stated MQC. The Angoff
  percentage is the audience-conditional output; the step count is the
  audience-independent provenance the main agent reads to check your
  reasoning.

For each question, return:

- row: <int>

- my_answer: option<N>

- my_reasoning: 2 sentences. Name the rule/concept tested + why each
  non-chosen option is wrong (one phrase each).

- multiple_correct_risk: yes|no — is a second option also defensibly
  correct?

- ambiguity_risk: yes|no — stem ambiguous, trick, or missing context?

- conceptual_steps: <int> — the audience-independent anchor: how many
  distinct conceptual moves does an unprepared solver execute?
    1 step / no abstraction
    2 steps / one non-trivial choice
    3+ steps / multi-constraint / domain abstraction

- conceptual_steps_note: <one line> — describe the steps the solver
  walks through. This is your audience-independent provenance.

- pattern_exposure_note: <one line> — does this MQC, given the stated
  cohort and prep-exposure profile, have HIGH exposure to this exact
  pattern (drilled in standard prep, near-instant pattern-recall) or
  LOW exposure (genuinely novel, must work the steps)? State which and
  in one phrase WHY. Example HIGH: "tier-1 has saturated exposure to
  ratio-of-total problems; conceptual-step count overstates effective
  complexity." Example LOW: "case-based legal-reasoning stem; no
  standard pattern collapses for tier-3."

- angoff_pct_for_stated_mqc: <int 0-100> — of 100 MQCs as defined
  above (cohort + prep exposure included), how many would get this
  correct? This is an AUDIENCE-CONDITIONAL number. If
  pattern_exposure_note says HIGH, this should be materially higher
  than the conceptual-step count alone would predict.

- angoff_reasoning: 1 sentence on which misconception trips MQCs and
  ~what % is tripped, given the stated cohort's prep exposure.

- my_blind_difficulty: EASY|MEDIUM|HARD — COMPUTED, not chosen. Look
  up angoff_pct_for_stated_mqc in the supplied angoff_windows:
    angoff_pct ∈ EASY window   → my_blind_difficulty = EASY
    angoff_pct ∈ MEDIUM window → my_blind_difficulty = MEDIUM
    angoff_pct ∈ HARD window   → my_blind_difficulty = HARD
  If angoff_pct falls in a GAP between two windows (e.g. windows are
  MEDIUM=[40,65] and EASY=[80,95] and your estimate is 72), pick the
  CLOSER band and add a `boundary_flag: "<estimate>% sits between
  MEDIUM upper 65 and EASY lower 80; chose <band> as closer"`. Do not
  default-pick a side; do not adjust your Angoff estimate to land
  inside a window. Honest estimate first, closer band second, flag
  third.

- proxy_a: 1-5 (discrimination — 1=surface heuristics; 3=two distinct
  misconceptions tested; 5=graded distractor ladder).

- proxy_c: 1-5 (effective guess floor — 1=3 functioning distractors;
  3=only 1 functioning; 5=broken).

- confidence: HIGH|MED|LOW.

- proposed_edits: array of {field, from, to, why}

    These are CORRECTNESS and DISCRIMINATION edits only — issues you
    can detect without the marked answer key and without the marked
    difficulty band. Difficulty-alignment edits live in a separate
    field below (alignment_prescriptions) because they depend on the
    marked band you can't see.

    field: one of content | option1..option6
           (NEVER subject/topics/difficulty/correctOption — subject/
           topics/difficulty are the spec; correctOption can only be
           flipped by the main agent after key reveal).
    from:  the EXACT verbatim current value of that cell (paste-able).
    to:    the EXACT verbatim replacement value (paste-able).
    why:   one phrase tying the edit to the issue it fixes.

  Write the edit yourself — you have full content visibility. Do NOT
  defer to a human or to the main agent.

  HARD LAYER-SEPARATION RULE (read before using the table):

    Difficulty (IRT's b) measures AUDIENCE-CONDITIONAL solve complexity
    for the stated MQC — conceptual steps minus pattern-recall
    collapse for that cohort. It lives in the STEM.

    Discrimination (IRT's a) measures how well the item separates
    high-ability from low-ability candidates *within* the stated MQC
    pool given the same intrinsic complexity. It lives in the
    DISTRACTORS.

    These are separate parameters. To fix a discrimination problem you
    REWRITE DISTRACTORS in proposed_edits. To fix a difficulty
    mismatch you REWRITE THE STEM via alignment_prescriptions below.
    NEVER swap a distractor to "fix" difficulty.

  Prescription table for proposed_edits (correctness + discrimination):

  | Issue you detected | Edit to write in proposed_edits |
  |---|---|
  | multiple_correct_risk: yes | Rewrite the second-defensible option so it no longer satisfies the stem. (correctness layer) |
  | ambiguity_risk: yes | Rewrite the ambiguous span in the stem with a tighter version. (correctness layer) |
  | proxy_a ≤ 2 — poor discrimination | Rewrite 1-2 distractors so each targets a *distinct, named* misconception the stated MQC would plausibly hold. State the misconception in `why`. (discrimination layer = distractors) |
  | proxy_c ≥ 3 — guess floor inflated | Replace each obvious-throwaway distractor with a plausible wrong answer mapped to a real misconception. (discrimination layer = distractors) |
  | construct_mismatch (e.g., missing chart / wrong subject) | proposed_edits: [] AND confidence: LOW. This is the ONLY case where empty proposed_edits is allowed. |

- alignment_prescriptions: { to_one_band_harder: {...}|null, to_one_band_easier: {...}|null }

    Forward-looking PAIR of stem-edit candidates. You don't know the
    marked difficulty band, so you can't know which direction (if any)
    will be needed. You write BOTH directional candidates and the main
    agent — after revealing the marked band — picks the one that
    closes the gap with my_blind_difficulty, or neither if
    my_blind_difficulty already matches.

    Each candidate is either:
      { field: "content",
        from: "<exact current stem>",
        to:   "<exact rewritten stem>",
        why:  "<one phrase: adds/removes the Nth conceptual step — name it>" }
    OR null, if no defensible one-band move exists within the marked
    subject/topics.

    Layer rule restated: alignment_prescriptions edits ALWAYS target
    the STEM (`field: "content"`). Never propose alignment via a
    distractor swap.

    to_one_band_harder: add ONE conceptual step that this MQC's prep
    exposure does NOT collapse to recall. Patterns:
      - insert a purity / efficiency adjustment
      - add a sub-group split
      - introduce a compound ratio
      - add a reverse-direction twist
      - add an extra unit conversion
      - add a target-vs-input distinction
      - add a second constraint
      The answer may change — note that in `why`.

    to_one_band_easier: remove ONE conceptual step OR convert a
    novel-to-this-MQC step into a recall step. Patterns:
      - pre-compute one intermediate value
      - state a converted unit instead of asking the candidate to convert
      - drop one of the chained constraints
      - remove a target-vs-input distinction
      - replace a compound ratio with a single ratio
      The answer may change — same note applies.

    If neither direction is defensible within subject/topics, emit
    both as null and set confidence: LOW.

  HARD RULE — every row with any correctness/discrimination issue
  MUST have a non-empty proposed_edits array unless confidence: LOW
  AND the obstruction is external. The alignment_prescriptions pair
  is REQUIRED on every row regardless of correctness/discrimination
  state — if both directions are null, set confidence: LOW.

Output: a single JSON array. Pure JSON, no markdown, no prose, parseable.

Honesty discipline:
- angoff_pct sits in a window gap → pick CLOSER band + boundary_flag.
  Do NOT round to the nearest window; do NOT adjust your estimate.
- Unsure between two options → confidence: LOW AND multiple_correct_risk: yes.
- angoff_pct_for_stated_mqc above the EASY window upper → floor item;
  flag implicitly via the high estimate.
- angoff_pct_for_stated_mqc below the HARD window lower → likely you
  got it wrong OR the item is at the guess floor; flag via confidence: LOW.
- Quantitative items: solve by two independent methods. If they
  disagree, confidence: LOW.

Constraint on the spec (STRENGTHENED):
- The marked `subject`, `topics`, and `difficulty` are the SPEC for
  HOW THIS ITEM SHOULD BEHAVE FOR THE STATED MQC. The difficulty
  field is not a description of the item in the abstract — it's a
  prediction that the stated MQC will land in band X. You will NEVER
  see the marked difficulty. Your job is to predict how the item will
  behave for the stated MQC (via angoff_pct_for_stated_mqc →
  my_blind_difficulty) and let the main agent compare on reveal.
- You may NOT propose edits to subject/topics/difficulty. Edit
  `content` / `option1..option6` to align the item TO the marked spec.
- If the item's construct fundamentally mismatches the marked subject
  or topics, add `construct_mismatch: "<one-line description>"`, set
  confidence: LOW, and emit `proposed_edits: []` AND
  `alignment_prescriptions: { to_one_band_harder: null, to_one_band_easier: null }`.

Return under 1600 words.

Example output for one row (tier-1 MQC, windows EASY=[80,95]
MEDIUM=[40,65] HARD=[10,25]):

[
  {
    "row": 5,
    "my_answer": "option1",
    "my_reasoning": "Ratio 3:22 sums to 25 parts; fertilizer = (3/25) × 475 = 57 L. Cross-check: 475/25 = 19 L/part, 19 × 3 = 57. Other options trap students who misread the ratio.",
    "multiple_correct_risk": "no",
    "ambiguity_risk": "no",
    "conceptual_steps": 1,
    "conceptual_steps_note": "Single-concept solve: apply a given ratio to a total. Three arithmetic ops (sum→divide→multiply) collapse into one conceptual step (proportional allocation).",
    "pattern_exposure_note": "HIGH — tier-1 IIT/NIT prep cohort has saturated exposure to ratio-of-total problems; this is near-instant pattern-recall, conceptual-step count overstates effective complexity for this MQC.",
    "angoff_pct_for_stated_mqc": 90,
    "angoff_reasoning": "Tier-1 candidates recognise the pattern in seconds; only careless arithmetic or ratio-misread trips ~10%.",
    "my_blind_difficulty": "EASY",
    "proxy_a": 3,
    "proxy_c": 2,
    "confidence": "HIGH",
    "proposed_edits": [],
    "alignment_prescriptions": {
      "to_one_band_harder": {
        "field": "content",
        "from": "<p>Geetanjali prepares a drip-irrigation solution where fertilizer concentrate and water are mixed in the ratio <strong>3 : 22</strong>. The total solution required for one field section is <strong>475 litres</strong>. How many litres of fertilizer concentrate are needed?</p>",
        "to": "<p>Geetanjali needs <strong>475 litres</strong> of a drip-irrigation mix where <em>pure</em> fertilizer concentrate and water are combined in the ratio <strong>3 : 22</strong>. Her stock fertilizer is only <strong>80% pure</strong> (the remaining 20% is inert filler excluded from the 475 L target). How many litres of stock concentrate must she add?</p>",
        "why": "adds purity-adjustment as a second conceptual step (proportional allocation → purity scaling) that tier-1 prep does NOT pre-drill; answer changes 57 L → 71.25 L — main agent will flip correctOption on key reveal if this branch is taken"
      },
      "to_one_band_easier": null
    }
  }
]

Notes on the example:
- angoff_pct_for_stated_mqc = 90 (tier-1 finds it trivial).
- 90 falls inside the supplied EASY window [80, 95] → my_blind_difficulty = EASY (computed, not chosen).
- conceptual_steps = 1 and pattern_exposure_note = HIGH together justify the high Angoff; the main agent reads both to verify the audience-conditional reasoning.
- proposed_edits is empty — no correctness or discrimination flags.
- to_one_band_harder adds purity-adjustment as a step tier-1 prep does NOT drill (genuinely novel for this cohort, not just a step they'd pattern-recall).
- to_one_band_easier is null — can't make a 1-step item easier without leaving the marked topic.
- For a tier-3 MQC with HARD window [10, 25], the SAME item with the SAME 90% Angoff (or whatever lower number tier-3 yields) would land in a different band — that is the audit's whole point.
```

## What the Main Agent Does After Subagents Return

The main agent is a **pass-through composer**, not an editor.

1. Collect all subagent JSON outputs into a single list (key = row).
2. Read `/tmp/qc_keys.json` (now and only now).
3. For each row, compose the verdict:
   - **correctness:** compare `my_answer` to marked `correctOption`.
     - match + no risk flags → no correctness_issue
     - match BUT `multiple_correct_risk: yes` → "Two defensibly-correct options"
     - mismatch + HIGH confidence → "Marked X but Y is the only defensible answer"; **ADD a `correctOption` flip edit** (cross-row exception)
     - mismatch + LOW confidence → escalate, no auto-flip
     - `ambiguity_risk: yes` → "Stem is ambiguous: …"
   - **difficulty:** compare `my_blind_difficulty` to marked `difficulty`.
     - match → no difficulty_issue
     - blind one band easier than marked → **PASS THROUGH `alignment_prescriptions.to_one_band_harder`**. If null → confidence: LOW.
     - blind one band harder than marked → **PASS THROUGH `alignment_prescriptions.to_one_band_easier`**. If null → confidence: LOW.
     - two-band mismatch → confidence: LOW, no auto-edit; construct-drift escalation.
     - **NEVER re-rate.** The gap closes via alignment_prescriptions, never via "on second look it's actually MEDIUM".
   - **status:** ALIGNED iff both issues null and no edits added.
   - **edits:** subagent `proposed_edits` PASS-THROUGH, plus optional `correctOption` flip, plus optional alignment stem edit from `alignment_prescriptions`. Do NOT regenerate.
   - **confidence:** subagent confidence PASS-THROUGH unless an alignment branch was needed and its entry was null (down-grade to LOW).
4. Write `verdicts.json`.
5. Run `python3 scripts/qc_xlsx.py write <input.xlsx> verdicts.json <output.xlsx>`.

## Why This Structure Matters

- **Both audit targets are structurally blind.** A subagent in a fresh context literally cannot have seen the row's `correctOption` OR marked `difficulty` — its only inputs are the batch JSON (key-and-difficulty stripped), the prompt, and the angoff_windows dict. Eliminates the dominant LLM failure mode on QC twice over.
- **Audience-conditional bands.** The subagent uses the supplied `angoff_windows` to map its Angoff estimate to a band. This is what makes the audit operationally useful — the same item with the same key gets DIFFERENT verdicts for tier-1 vs tier-3, because tier-1 finds it easy and tier-3 finds it hard, and the marked band must match the audience the assessment is for.
- **Anchor + collapse, not anchor alone.** `conceptual_steps` is the audience-independent anchor; `pattern_exposure_note` is the audience-conditional collapse; `angoff_pct_for_stated_mqc` is their product. The main agent reads all three to verify reasoning didn't skip a layer.
- **Boundary discipline.** Estimates that fall between windows surface as `boundary_flag` instead of getting silently rounded — the main agent treats those as MED-confidence and may dispatch a verifier.
- **Single round-trip.** The `alignment_prescriptions` pair lets the subagent emit both directional stem-edit candidates in one pass; no second dispatch on difficulty mismatch.
- **Pass-through preserves provenance.** Every edit on the verdict came from a context that didn't see the audit target it's aligning to. Regeneration at compose time would leak that provenance.
- **Parallelism reduces wall-clock time ~Nx** with N subagents.
- **IRT reasoning stays internal to the subagent.** The lean verdict the main agent composes never surfaces Angoff numbers.
- **Quant/logic gets two-method self-consistency for free.**
