# Changelog

All notable changes to this plugin will be documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Corrected sheet is now upload-ready as-is.** `ALIGNED` rows previously
  appeared as blank green cells; they now carry the original row content
  verbatim with a green fill. A PM can drop the fill colours and re-upload the
  sheet directly — it is the single post-QC source of truth.
- **QC now auto-prescribes distractor rewrites for difficulty drift,
  multi-correct risks, and ambiguity; previously these were flagged for human
  review.** The subagent has full content visibility (the parse script holds
  back only `correctOption`), so it is the right place to write the edit. The
  subagent prompt now requires a `proposed_edits` array per row and includes
  a prescription table mapping each detected issue to a paste-able edit
  shape. The main agent on compose is a pass-through composer — it does not
  regenerate edits; it only adds a `correctOption` flip on key reveal as the
  documented cross-row exception. SKILL.md rule 5 is tightened: empty edits
  are only allowed when `confidence: LOW` AND the obstruction is external
  (construct mismatch / missing chart / malformed source).

### Added
- **`qc_changes` audit column** on the original sheet, placed immediately after
  `qc_status`. For each `NEEDS_EDITS` row it carries a wrap-text narrative with
  `CORRECTNESS:` / `DIFFICULTY:` sections (omitted when null) and an
  `EDITS APPLIED:` bulleted list of every applied edit. Rows with
  `confidence: LOW` and no auto-applied edits get a `human review required`
  line. The cell fill mirrors `qc_status` (amber / red) and the column width
  is set to 80 for at-a-glance reading.
- **Writer auto-LOW guard.** A `NEEDS_EDITS` verdict at MED or HIGH confidence
  with an empty `edits` array is now treated as a subagent regression: the
  writer emits a stderr warning, bumps the row's effective confidence to LOW
  for fill colour (RED on `qc_status`, `qc_changes`, and the Corrected row),
  and switches the `qc_changes` narrative to `EDITS: none auto-applied —
  human review required`. The write does not fail — the gap is surfaced
  without blocking the pipeline.
- **Worked-example prescription patterns** in `DIFFICULTY_RUBRIC.md`:
  soften-weakest-distractor (too-hard items), arithmetic-mean trap for
  speed/rate items (too-easy), sign-flipped distractor for arithmetic
  (too-easy), tighten-range / divisibility constraints for ambiguous
  number-property items, loosen-one-premise for over-constrained Constraint
  Deduction items.

## [0.1.0] - 2026-05-13

Initial public release.

### Added
- `qc-questions` skill: blind-solve QC for MCQ assessment banks with
  IRT-aligned difficulty estimation (Modified Angoff + discrimination
  proxy + pseudo-guessing proxy).
- `/qc-questions` slash command: end-to-end run on a .xlsx with parallel
  subagent dispatch (6 rows per worker by default).
- `scripts/qc_xlsx.py`: xlsx I/O. `read` strips HTML and holds the
  `correctOption` keys back from the question payload; `write` produces
  a three-sheet output workbook (Original + qc_status, QC Legend,
  Corrected) with colour-coded edits.
- `subject`, `topics`, `difficulty` are treated as the immutable spec the
  question must match; the writer rejects any edit targeting them and
  emits a stderr warning. Override with `--allow-retag` for legacy
  cleanup workflows.
- Construct-mismatch escalation path (`confidence: LOW`, empty edits,
  red row fill) for items that cannot be aligned via content edits.
- Synthetic 8-row sample bank (`examples/sample_bank.xlsx`) with planted
  errors covering each failure mode + expected post-QC workbook.
- MQC preset library (`examples/mqc_presets.md`).
- Pytest smoke suite covering parser, writer, colour fills, immutable
  field rejection, and the `--allow-retag` override.
- GitHub Actions CI running pytest + ruff on push and pull request.
