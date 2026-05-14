# Canonical Subagent Prompt — Blind QC Worker

This is the prompt the main agent dispatches to each parallel subagent during xlsx-batch QC. It is the ONLY way to ensure blind-solve discipline: a subagent invoked in a fresh context cannot have read the marked `correctOption` for the rows it judges, even if it tried.

## Batching

- One subagent per batch of **5–8 questions**. Smaller batches = more parallelism but more dispatch overhead; 6 is a good default.
- Dispatch **all batches in a single message** (multiple tool calls in parallel) so they run concurrently.
- For an 18-row file: 3 subagents × 6 rows. For 100 rows: 15–20 subagents.
- Cap parallel subagents at ~10 per dispatch to avoid rate-limit thrash; queue further batches if needed.

## Inputs the main agent prepares per batch

Write the batch's questions to a temp JSON file (`/tmp/qc_batch<N>.json`) **without `correctOption`**. The keys live separately in `/tmp/qc_keys.json` which the subagent must not read.

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
option1..option6, subject, topics, marked difficulty, and other metadata.
You do NOT have access to correctOption for any row.

HARD RULE: do not, under any circumstance, read <KEYS_FILE_PATH>. Do a
genuinely BLIND solve.

For each question, return:
- row: <int>
- my_answer: option<N>
- my_reasoning: 2 sentences. Name the rule/concept tested + why each
  non-chosen option is wrong (one phrase each).
- multiple_correct_risk: yes|no — is a second option also defensibly
  correct?
- ambiguity_risk: yes|no — stem ambiguous, trick, or missing context?
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
    field: one of content | option1..option6 | correctOption
           (NEVER subject/topics/difficulty — those are the spec).
    from:  the EXACT verbatim current value of that cell (paste-able).
    to:    the EXACT verbatim replacement value (paste-able).
    why:   one phrase tying the edit to the issue it fixes.

  Write the edit yourself — you have full content visibility. Do NOT
  defer to a human or to the main agent. Use this prescription table:

  | Issue you detected              | Edit to write |
  |---|---|
  | multiple_correct_risk: yes      | Rewrite the second-defensible option so it no longer satisfies the stem. |
  | ambiguity_risk: yes             | Rewrite the ambiguous span in the stem with a tighter version. |
  | angoff_pct above marked band (too easy) | Pick the weakest distractor and rewrite it as a near-miss exploiting a specific named misconception. Target landing the Angoff inside the marked band. |
  | angoff_pct below marked band (too hard) | Soften one distractor or simplify one numeric step. |
  | construct_mismatch (e.g., missing chart / wrong subject) | proposed_edits: [] AND confidence: LOW. This is the ONLY case where empty proposed_edits is allowed — the obstruction is external to the QC pipeline. |

  (You do NOT see the marked correctOption, so do not write correctOption
  flip edits — the main agent owns that one cross-row case on key reveal.)

  HARD RULE — every row with any of the issues above MUST have a
  non-empty proposed_edits array unless confidence: LOW AND the obstruction
  is external (missing chart / malformed source cell / construct
  mismatch). Flagging drift for human review when you have full content
  visibility is a failure mode, not a deferral.

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
  output, set confidence: LOW, and emit `proposed_edits: []`. The main
  agent will surface this as an escalation rather than retagging.

Return under 1000 words.

Example output for one row (illustrates the proposed_edits shape):

[
  {
    "row": 5,
    "my_answer": "option2",
    "my_reasoning": "Tests subject-verb agreement; option2 is the only sentence where the singular subject 'list' takes 'were' instead of 'was'. Others are SVA-correct.",
    "multiple_correct_risk": "no",
    "ambiguity_risk": "no",
    "angoff_pct": 70,
    "angoff_reasoning": "MQC knows SVA but trips on the intervening prepositional phrase 'of pending tasks' — ~30% miss it.",
    "proxy_a": 3,
    "proxy_c": 1,
    "confidence": "HIGH",
    "proposed_edits": [
      {
        "field": "option2",
        "from": "<p>The list of pending tasks were reviewed during the morning call.</p>",
        "to": "The list were reviewed during the morning call.",
        "why": "removes the prepositional-phrase trap so the SVA error is obvious; Angoff returns to ~85% EASY band"
      }
    ]
  }
]
```

## What the Main Agent Does After Subagents Return

The main agent is a **pass-through composer**, not an editor. The subagent
has full content visibility and is the authority on what to write into
each cell — the main agent re-validates correctness and assembles the
verdict, but it does not regenerate edits.

1. Collect all subagent JSON outputs into a single list (key = row).
2. Read `/tmp/qc_keys.json` (now and only now — the main agent's context did see `correctOption` during xlsx parsing, but the parse script kept it in a separate block).
3. For each row, compose the verdict:
   - **correctness:** compare `my_answer` to the marked key.
     - match + no `multiple_correct_risk` + no `ambiguity_risk` → no correctness_issue
     - match BUT `multiple_correct_risk: yes` → correctness_issue = "Two defensibly-correct options"
     - mismatch + HIGH confidence → correctness_issue = "Marked X but Y is the only defensible answer"; **ADD a `correctOption` flip edit** (this is the canonical cross-row exception — the subagent could not write this edit because it never saw the marked key)
     - mismatch + LOW confidence → escalate (confidence: LOW, no auto-flip)
     - `ambiguity_risk: yes` → correctness_issue = "Stem is ambiguous: …"
   - **difficulty:** map `angoff_pct` to band (EASY 75–95, MEDIUM 50–75, HARD 25–50). Compare to marked. Same band → no difficulty_issue. Different band → difficulty_issue = "Marked X but Angoff … → Y band".
   - **status:** ALIGNED iff both issues null and `proposed_edits` empty; otherwise NEEDS_EDITS.
   - **edits:** `subagent.proposed_edits` PASS-THROUGH, plus the optional `correctOption` flip described above if the key mismatch fires. Do NOT regenerate, rewrite, or rephrase the subagent's edits — they are paste-able as-is.
   - **confidence:** `subagent.confidence` PASS-THROUGH. Do NOT down-grade for drift (the autonomous-by-default rule means the subagent's prescribed edits are the right confidence anchor — if the subagent says HIGH and provided edits, the row is HIGH).
4. Write `verdicts.json` (list of lean verdict objects).
5. Run `python3 scripts/qc_xlsx.py write <input.xlsx> verdicts.json <output.xlsx>`.

**The only edits the main agent adds on top of `subagent.proposed_edits`** are cross-row corrections the subagent structurally could not write — at present, only the `correctOption` flip on key mismatch (the subagent never sees the marked key). Anything else is a regeneration and breaks the architecture's blind-solve guarantee.

## Why This Structure Matters

- **Blind-solve is structurally enforced.** A subagent in a fresh context literally cannot have seen the row's `correctOption` — its only inputs are the batch JSON (key-stripped) and the prompt. This eliminates the dominant LLM failure mode on QC: rationalising the marked answer.
- **Parallelism reduces wall-clock time ~Nx** with N subagents.
- **IRT reasoning stays internal to the subagent.** The lean verdict the main agent composes never surfaces Angoff numbers — those served their purpose at decision time.
- **Quant/logic gets two-method self-consistency for free** because the prompt mandates it; failures surface as `confidence: LOW` which the main agent treats as P0.
