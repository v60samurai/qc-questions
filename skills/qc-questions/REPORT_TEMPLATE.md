# Report Template — Lean, Edit-Centric

The output answers two questions per item: **what's off** and **exactly what to change**. Everything else (IRT proxies, MQC definition, Angoff math) stays in the LLM's working memory — it's the *method*, not the *deliverable*.

## Tier-Fit Observations (top-of-report — surface before per-row verdicts)

Per-row verdicts audit each item's marked-band-vs-blind-band fit independently. Tier-fit observations aggregate those signals to surface bank-level / section-level calibration issues that no single row can show.

Surface a tier-fit observation when any of these conditions holds:

1. **Section composition below floor.** When > 40% of items in a (subject, topic) section have blind-rated band ≤ EASY for a tier-1 MQC (or ≤ MEDIUM for tier-2), surface:
   > "**Section <subject>/<topic>:** <X>% of items (<n>/<total>) blind-rate as EASY-or-below for the stated tier-1 MQC. Information function is suboptimal at the cut score — the section under-discriminates. Recommend replacing <n> items with stems rated MEDIUM+ for tier-1 (HARD reserved for top-of-range discrimination)."

2. **Same-direction 2-band gaps cluster (blueprint review).** When > 20% of items in a section show 2-band gaps in the SAME direction:
   > "**Blueprint review — <subject>/<topic>:** <n>/<total> items are 2-band-gapped <overrated|underrated> for the stated MQC. This is a tag-calibration problem at the section level, not a per-item drift. Recommend a blueprint pass before re-uploading: either re-author the affected items to actually function at their marked bands, or relax the marked tags to match the items' actual behaviour for the audience."

3. **Formula-recall anti-pattern cluster.** When > 50% of HARD-tagged items in a section carry `mistag_reason: formula_recall_overrated`:
   > "**Anti-pattern detected — <subject>/<topic>:** <n>/<total> HARD-tagged items reduce to formula-recall + plug-in. Formula recall is not HARD-band behaviour. Recommend re-authoring the affected items with multi-concept chaining, non-obvious decomposition, or interacting constraints."

4. **Construct mismatch cluster.** When > 10% of items in a section flag construct_mismatch (item tests wrong subject/topic):
   > "**Construct drift — <subject>/<topic>:** <n>/<total> items appear to test a different construct than tagged. Recommend a tagging-taxonomy review before shipping."

Each observation is ADVISORY — it does not produce per-row edits. It informs the PM's test-design or item-authoring choices. The aggregate report carries any tier-fit observation that fires at the top, BEFORE the per-row verdict list, so PMs see calibration issues first.

**Severity.** Tier-fit observations are P0 if they fire — a section that systematically under-discriminates or systematically misrepresents difficulty corrupts every score the assessment produces. The PM should triage these before any per-row edit.

## Per-Question Verdict (YAML)

```yaml
- row: 7
  status: ALIGNED            # ALIGNED | NEEDS_EDITS
  correctness_issue: null
  difficulty_issue: null
  edits: []
  confidence: HIGH
```

When something is off:

```yaml
- row: 12
  status: NEEDS_EDITS
  correctness_issue: |
    Marked correctOption=option1, but option1 has a tense slip ("She says ... I told").
    Option2 is the only fully consistent reported-speech construction.
  difficulty_issue: null
  edits:
    - field: correctOption
      from: option1
      to: option2
      why: fixes correctness
    - field: option1
      from: "Maya contacted us yesterday. She says the approval form is missing. I told her we will investigate."
      to:   "Maya contacted us yesterday. She says the approval form is missing. I tell her we will investigate."
      why: keeps option1 as a clean distractor (all-present-tense) after the key flip
  confidence: HIGH
```

When difficulty is off (no correctness issue):

```yaml
- row: 2
  status: NEEDS_EDITS
  correctness_issue: null
  difficulty_issue: |
    Marked EASY but the prepositional-phrase-between-subject-and-verb construction
    trips ~30% of MQCs (Angoff ≈ 70%, MEDIUM-band behaviour). Editing the item to
    drop the trap brings it back into the EASY band.
  edits:
    - field: option2
      from: "The list of pending tasks were reviewed during the morning call."
      to:   "The list were reviewed during the morning call."
      why: removes the intervening prepositional phrase so the SVA error is obvious; restores EASY-band Angoff
  confidence: HIGH
```

**Rule — never retag.** The marked `subject`, `topics`, and `difficulty` are the SPEC. Every edit targets `content` / `option1..option6` / `correctOption` to pull the item back to the marked tags. Edits whose `field` is `difficulty`, `subject`, or `topics` are rejected by the writer.

When both correctness and difficulty are off:

```yaml
- row: 9
  status: NEEDS_EDITS
  correctness_issue: "Marked option3 but two options (option2 and option3) are both grammatically valid."
  difficulty_issue: |
    After the correctness fix below, Angoff lands ~85% which is the marked EASY
    band, so no further difficulty edits needed.
  edits:
    - field: option2
      from: "The team members has finished their report on time."
      to:   "The team member finished their report on time."
      why: removes second-correct option so the item has a unique answer; keeps Angoff inside EASY
  confidence: HIGH
```

When the item cannot be aligned to its marked tags (construct mismatch):

```yaml
- row: 15
  status: NEEDS_EDITS
  correctness_issue: |
    Construct mismatch — item tests arithmetic but subject="Verbal Ability",
    topics="Grammar and Sentence Correction". Cannot align via content edits
    without rewriting the entire question as a grammar item. Escalate to author.
  difficulty_issue: null
  edits: []
  confidence: LOW
```

## Mandatory Output Contract

- For every input row, emit exactly one verdict block.
- `ALIGNED` rows have empty `edits` and both issues `null`. Do not pad with commentary.
- Every `edits[].to` is **directly paste-able** into the xlsx cell. No placeholders, no "[FILL IN]".
- For `correctOption` and `difficulty` edits, `from` and `to` must be one of the valid enum values (`option1..option6` / `EASY|MEDIUM|HARD`).
- For text-field edits (`stem`, `option1..option6`), `from` is the exact current text and `to` is the exact replacement.
- `confidence: LOW` rows still get edit suggestions, but `qc_notes` (if used) should flag them for human review.

## Aggregate Report (xlsx batch)

```markdown
# QC Report — <file basename> — <date>

## Summary
- Total: <N>
- ALIGNED: <n_ok>
- NEEDS_EDITS: <n_edit>
  - correctness issues: <n_c>
  - difficulty issues:  <n_d>
  - both: <n_both>

## Must-Fix First
| Row | Subject | Issue | Smallest Edit |
|---|---|---|---|

## Other Edits (difficulty-only)
| Row | Subject | Marked → Recommended | Smallest Edit |
|---|---|---|---|

## Low-Confidence Rows (escalate to human)
| Row | Reason |
|---|---|
```

## XLSX Output — Two Sheets

The script produces ONE output workbook containing two sheets:

### 1. Original sheet (preserved + one new column)

The input sheet is copied verbatim with a single column appended:

- `qc_status` — `ALIGNED` or `NEEDS_EDITS`

Nothing else is added to this sheet. The user can scan it to see at a glance which rows need work.

### 2. `Corrected` sheet

Same headers as the original. Every row from the original appears with all proposed edits already applied in-cell:

- Edits to `correctOption` → the new option enum is in the cell
- Edits to `difficulty` → the new band (EASY / MEDIUM / HARD) is in the cell
- Edits to `content` / `option1..option6` → the new text is in the cell, auto-wrapped in `<p>…</p>` if the edit text was plain (matches the platform's HTML expectation)
- `ALIGNED` rows are copied verbatim

The `Corrected` sheet is the **upload-ready, audited bank**. The user can ship it as-is, or diff it against the original sheet to review changes per row.

### Field aliases accepted in edits

- `stem` is accepted as an alias for `content`
- Edits whose `field` is not one of `content / option1..option6 / correctOption / difficulty` are ignored (logged silently)
- Edits whose `field` is not present as a column in the original sheet are ignored
