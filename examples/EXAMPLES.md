# Walkthrough — `sample_bank.xlsx`

A 9-row demo bank with planted errors, designed so each row teaches one failure mode the dual-blind QC discipline catches. Run it locally with:

```bash
python3 skills/qc-questions/scripts/qc_xlsx.py read examples/sample_bank.xlsx
# (Claude Code / Claude.ai then solves blind, composes verdicts.json, runs:)
python3 skills/qc-questions/scripts/qc_xlsx.py write \
  examples/sample_bank.xlsx \
  examples/sample_bank.expected_verdicts.json \
  examples/sample_bank__qc.actual.xlsx
```

Open `sample_bank__qc.expected.xlsx` to see the precomputed output side-by-side with the input.

## The two audit targets

```
input.xlsx
   ↓
qc_xlsx.py read
   ↓
   ┌─────────────────────────────┐    ┌─────────────────────────────┐
   │ questions   (visible)       │    │ _keys       (held back)     │
   │   • content                 │    │   • correctOption           │
   │   • option1..option6        │    │   • difficulty   ← NEW v0.2 │
   │   • subject                 │    │                             │
   │   • topics                  │    │                             │
   │   • questionType            │    │                             │
   └─────────────────────────────┘    └─────────────────────────────┘
            ↓                                       ↓
   blind solve     ────────────────────────►   reveal + compare
   blind difficulty rate
```

Before v0.2.0 only `correctOption` was held back. The subagent saw the marked difficulty, which means its difficulty rating was a post-hoc rationalization of the tag, not an audit signal. v0.2.0 holds back both fields so both ratings are structurally blind, and a mismatch on EITHER becomes a P1 edit prescription.

## Row-by-row

| Row | Tag | What's planted | What QC catches | Audit target |
|----|-----|----------------|-----------------|--------------|
| 2 | EASY, Grammar | clean item | ALIGNED — both targets match | control |
| 3 | EASY, Register | clean item | ALIGNED | control |
| 4 | MEDIUM, Grammar | `correctOption=option3` is wrong; only option2 is defensible | **correctOption flip** (option3 → option2) | correctOption |
| 5 | EASY, Grammar | "Identify the incorrect sentence" with a prepositional-phrase trap → intrinsically MEDIUM | option-text edit removes the trap so the item returns to EASY-band behaviour | difficulty (in-option case) |
| 6 | MEDIUM, Grammar | clean nearer-noun SVA item | ALIGNED | control |
| 7 | EASY, Grammar | two defensibly-correct options | rewrite one to break the tie | correctness (ambiguity) |
| 8 | EASY, Verbal Ability, but the question is an arithmetic problem | construct mismatch — `subject`/`topics` cannot be retagged (immutable spec) and the item can't be rewritten to grammar without a full rebuild | **LOW confidence escalation**, no auto-edits, red row | construct |
| 9 | MEDIUM, Reading Comp | clean item | ALIGNED | control |
| **10** | **MEDIUM, Quant** | **single-step proportion problem (1 conceptual step → intrinsically EASY)** | **dual-blind canonical case**: subagent's `my_blind_difficulty=EASY`, marked `difficulty=MEDIUM` → main agent picks `alignment_prescriptions.to_one_band_harder` → applies a **stem rewrite** that adds a purity-adjustment step (the second conceptual step). The post-edit correct answer changes from `option1` (57 L) to `option4` (71.25 L), so the main agent also flips `correctOption` as a cross-row exception. | **both targets — dual-blind** |

## Why row 10 matters

Row 10 is the row a single-blind QC (correctOption-held-back only, marked difficulty visible) would have **let through**.

- A single-blind subagent reads the row, sees `difficulty: MEDIUM`, and rationalises: "this proportion-with-a-total framing is the kind of step a MEDIUM-band MQC struggles with — Angoff ~65%, calls it MEDIUM, ALIGNED." The intrinsic complexity (1 conceptual step) gets absorbed into a story about MQC psychology.
- A dual-blind subagent reads the row with `difficulty` stripped, counts conceptual steps from first principles, commits `my_blind_difficulty: EASY` (1 step: apply ratio to total). The main agent reveals `difficulty: MEDIUM`, sees the one-band gap, picks the subagent's pre-written `to_one_band_harder` stem edit (adds purity adjustment as the second conceptual step) and applies it. The marked band is honoured by changing the item to fit, not by re-rating the item to fit the tag.

This is Rule 4: **the marked band is the spec; the blind rating is the audit signal; the gap closes via stem edit, never via re-rate.**

## Reading the output workbook

`sample_bank__qc.expected.xlsx` has three sheets:

1. **`Sheet1` (original + audit columns)** — every row preserved verbatim, with two new columns:
   - `qc_status` — `ALIGNED` (green) | `NEEDS_EDITS` (amber) | LOW-confidence flag (red)
   - `qc_changes` — human-readable narrative of what was off and which edits were applied
2. **`QC Legend`** — colour-code reference.
3. **`Corrected`** — production-ready post-edit version:
   - ALIGNED rows are the original content **verbatim**, green-filled. Drop the fill, re-upload.
   - NEEDS_EDITS rows have edits applied in-cell, with dark-amber + bold on the specific cells that changed.
   - LOW-confidence rows are red and carry original content un-edited — a human must review.

The `subject`, `topics`, and `difficulty` columns are **never modified** by the QC. They are the spec the item must align TO. If an item can't be aligned without changing them, that's the construct-mismatch escalation case (row 8).

## Regenerating the sample

```bash
python3 examples/_build_sample.py
python3 skills/qc-questions/scripts/qc_xlsx.py write \
  examples/sample_bank.xlsx \
  examples/sample_bank.expected_verdicts.json \
  examples/sample_bank__qc.expected.xlsx
```

The `_build_sample.py` script is the single source of truth for the demo bank — edit it to add rows, then regenerate.
