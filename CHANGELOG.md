# Changelog

All notable changes to this plugin will be documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-05-18

### Changed
- **Difficulty is now audience-conditional, not intrinsic.** This is the largest philosophical change since v0.1.0 and reverses a load-bearing assumption from v0.2.0. The skill previously claimed "marked difficulty = intrinsic complexity (conceptual-step count)"; in practice this caused silent audit failures whenever the user invoked QC for a specific cohort (tier-1, tier-2, etc.) — items that were intrinsically 1-2 steps but trivially recalled by tier-1 CAT-prep candidates were getting passed as ALIGNED to a HARD tag, even though tier-1 Angoff for those items is 85-95% (EASY behaviour, not HARD). The v0.3.0 framing: **difficulty is the Angoff band predicted for the stated MQC, anchored by conceptual-step count.** The step count travels with the item; the band travels with the audience. The same 2-step weighted-average item is EASY for tier-1, MEDIUM for tier-2, HARD for tier-3 — because each cohort's Angoff lands in a different audience-conditional window.
- **Audience-conditional Angoff windows.** SKILL.md Rule 6 now ships defaults per tier:
  - Tier 1 (IIT/NIT-top, CAT-prep saturated): HARD 10-25%, MEDIUM 40-65%, EASY 80-95%
  - Tier 2 (state engineering, moderate prep): HARD 25-45%, MEDIUM 50-70%, EASY 75-90%
  - Tier 3 (entry-level IT-services, light prep): HARD 35-55%, MEDIUM 55-75%, EASY 75-95%
  - General / unknown MQC: HARD 25-50%, MEDIUM 50-75%, EASY 75-95%
  Tier-1 HARD is 10-25% (stricter than the 25-50% default) because tier-1 has prep saturation; to discriminate the top 15% from the rest, items must operate above the routine-pattern layer. Users can override windows at invocation.
- **SUBAGENT_PROMPT.md** schema changed substantially:
  - Subagents now receive an `angoff_windows` dict from the main agent and MUST use it to map Angoff estimates to bands (no by-feel band picking).
  - New output fields: `pattern_exposure_note` (HIGH/LOW + one phrase why — does the stated MQC have saturated exposure to this pattern), `angoff_pct_for_stated_mqc` (renamed from `angoff_pct` to make audience-relativity explicit), `boundary_flag` (when estimate lands in a window gap).
  - `my_blind_difficulty` is now COMPUTED by looking up `angoff_pct_for_stated_mqc` in the supplied `angoff_windows`, not chosen by feel.
- **QC_PROTOCOL.md Step 5 reordered**: 5a locks the audience-conditional windows, 5b counts steps as the anchor, 5c estimates Angoff for the stated MQC including prep-exposure adjustment, 5d maps to band, 5e sanity-checks. The old "Stage 1 intrinsic complexity is the source of truth" framing is removed.
- **DIFFICULTY_RUBRIC.md opens with a new "Difficulty Is Audience-Conditional" section** that explains the thermometer analogy (step count = calibration, Angoff for stated MQC = reading; you need both). Worked examples now state the MQC tier explicitly, and a new Example 4 demonstrates the tier-1 two-band-gap on a drilled weighted-average pattern (the canonical case that single-blind audits passed silently).

### Added
- **MQC is now mandatory load-bearing input.** The skill refuses to grade without an explicit MQC at invocation. Without an MQC, the Angoff windows aren't anchored and every verdict is silently wrong.
- **Audience-conditional invariant test** (planned for next minor — currently the test suite still asserts the v0.2.0 dual-blind invariant; v0.3.x will add `test_my_blind_difficulty_uses_supplied_windows`).
- **Past-mistakes memory entry** (local) documenting the audience-mismatch failure mode the v0.2.0 skill kept hitting on Test.xlsx.

### Migration notes
- Existing `verdicts.json` files remain consumable by `qc_xlsx.py write` unchanged — the writer's contract is unchanged.
- The `read` script output schema is unchanged from v0.2.0 (both `correctOption` and `difficulty` still held back in `_keys`). Only the subagent prompt + the interpretation of `my_blind_difficulty` changed.
- If you invoked v0.2.0 without an MQC, you got a silently-wrong verdict against an implicit "neutral MQC". In v0.3.0 the skill asks for an MQC before proceeding. There is no v0.3.0 default MQC.
- The local Claude Code skill, the Claude.ai-uploadable skill bundle, and this repo all carry the same v0.3.0 logic. The Claude.ai bundle continues to omit `SUBAGENT_PROMPT.md` (single-context flow); subagent-specific instructions in `SKILL.md` and `QC_PROTOCOL.md` apply to local CC + repo only.

## [0.2.0] - 2026-05-18

### Changed
- **Dual-blind discipline.** The audit now holds back BOTH `correctOption` AND
  the marked `difficulty` band as audit targets. Previously only `correctOption`
  was stripped from subagent prompts; the subagent saw the marked difficulty
  and rated it post-hoc, which is the same rationalization failure mode the
  blind-solve discipline was built to prevent (applied to difficulty instead
  of correctness). `scripts/qc_xlsx.py read` now drops `difficulty` from each
  entry in `questions` and emits it inside `_keys` alongside `correctOption`.
  Subagents commit `my_blind_difficulty` per row before the main agent reveals
  `_keys`; on mismatch, the main agent picks the subagent's pre-written stem
  alignment edit and applies it. **The marked band is the spec; the blind
  rating is the audit signal; the gap closes via stem edit, never via
  re-rate.** (SKILL.md Rule 4, new.)
- **`SUBAGENT_PROMPT.md` output schema extended.** Subagents now return
  `my_blind_difficulty`, `conceptual_steps`, `conceptual_steps_note`, and an
  `alignment_prescriptions` pair (`to_one_band_harder`, `to_one_band_easier`)
  per row. The pair is forward-looking — the subagent doesn't know the marked
  band, so it emits both directional stem-edit candidates and the main agent
  picks the one that closes the gap (or neither, if `my_blind_difficulty`
  matches). Single round-trip preserved.
- **Hard Rules renumbered.** The skill's "Seven Hard Rules" (already 8) became
  9 with the new Rule 4 (blind difficulty rating + mandatory stem-edit
  alignment on mismatch + the "never re-rate" prohibition). Header dropped the
  count.
- **`QC_PROTOCOL.md` Step 5 restructured.** 5b commits the blind difficulty
  band before any reveal; 5f does the reveal + compare + mandatory alignment.
  Step 7 reframed as a dual-target pass-through composer with TWO documented
  cross-row exceptions (correctOption flip; alignment stem edit picked from
  the subagent's `alignment_prescriptions`).

### Added
- **`examples/EXAMPLES.md`** walkthrough — annotates every row of
  `sample_bank.xlsx` with the failure mode it teaches, and explains why row
  10 is the canonical case the dual-blind discipline catches that a
  single-blind audit would have missed.
- **`sample_bank.xlsx` row 10** — single-step proportion problem tagged
  MEDIUM. Demonstrates the full dual-blind flow: subagent commits
  `my_blind_difficulty: EASY` → main agent reveals MEDIUM → picks
  `to_one_band_harder` stem edit (adds purity-adjustment) → flips
  `correctOption` from option1 to option4 because the post-edit answer
  changed.
- **`test_read_holds_back_both_audit_targets`** locks the dual-blind invariant
  into the test suite. The test asserts neither `correctOption` nor
  `difficulty` appears in any `questions` entry, and both appear in every
  `_keys` entry. A future regression that lets marked difficulty leak back
  into subagent prompts fails this test immediately.
- **Difficulty-side rationalization counters** in `QC_PROTOCOL.md`'s
  Rationalizations Catalogue — twins for every correctness-side counter so
  the difficulty layer gets the same defensive scaffolding.

### Migration notes
- Existing `verdicts.json` files remain consumable by `qc_xlsx.py write`
  unchanged — the writer's contract is unchanged. Only the `read` output and
  the subagent's intermediate output schema changed.
- The local Claude Code skill and the Claude.ai-uploadable skill bundle both
  carry these updates. The local version uses subagent dispatch for the
  blind solve + blind rate; the Claude.ai version uses the code interpreter
  with explicit "stop scrolling before `_keys`" discipline.

## [0.1.1] - 2026-05-17

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
