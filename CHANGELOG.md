# Changelog

All notable changes to this plugin will be documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
