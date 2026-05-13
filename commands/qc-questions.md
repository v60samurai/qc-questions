---
description: QC an IRT-aligned question bank xlsx (or one standalone question) for correctness and difficulty alignment, then write a two-sheet output workbook.
argument-hint: <path-to-xlsx>  [--mqc "<MQC one-liner>"]  [--out <output.xlsx>]
---

Run the `qc-questions` skill on the input given in $ARGUMENTS.

Step 0 — Load the skill if not already active. The skill files are shipped with this plugin under `${CLAUDE_PLUGIN_ROOT}/skills/qc-questions/` (resolve by checking the plugin's install location if `CLAUDE_PLUGIN_ROOT` is not set):
- `SKILL.md` (workflow)
- `QC_PROTOCOL.md` (blind-solve discipline)
- `DIFFICULTY_RUBRIC.md` (IRT-aligned Modified Angoff + a-proxy + c-proxy)
- `SUBAGENT_PROMPT.md` (canonical worker prompt — use verbatim)
- `REPORT_TEMPLATE.md` (lean output schema)
- `scripts/qc_xlsx.py` (xlsx I/O)

Step 1 — Parse $ARGUMENTS:
- The first positional argument is the input xlsx path. Required.
- Optional `--mqc "<text>"`: one-sentence definition of the minimally-qualified candidate.
- Optional `--out <path>`: output workbook path. Default: `<input_dir>/<input_stem>__qc.xlsx`.
- If $ARGUMENTS is empty or doesn't point to an xlsx, ask the user for the file path. Do nothing else until they provide one.

Step 2 — Establish MQC:
- If `--mqc` was provided, use it verbatim.
- If not, infer one from the xlsx's `subject` / `topics` / `tags` columns. Propose it in one line and confirm with the user before dispatching subagents. Example: "MQC = entry-level Capgemini service-desk candidate at the screening cut, English-medium Indian schooling, conversational professional English required."

Step 3 — Run the canonical xlsx-batch workflow from SKILL.md:
1. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qc-questions/scripts/qc_xlsx.py read <input.xlsx>` → JSON with `questions` and `_keys`.
2. Split questions into batches of 6 rows. Write each batch to `/tmp/qc_batch<N>.json` (questions only — never include `correctOption`). Write `/tmp/qc_keys.json` (main-agent only).
3. **Dispatch every batch in ONE message** as parallel `Agent` tool calls. Each subagent uses the prompt template in `SUBAGENT_PROMPT.md` verbatim, substituting only `<MQC>`, `<BATCH_FILE_PATH>`, `<KEYS_FILE_PATH>`. Cap at ~10 parallel subagents per dispatch; queue further batches if the file has 60+ rows.
4. Collect subagent outputs. Reveal `correctOption` from `/tmp/qc_keys.json` per row. Compose lean verdicts per `QC_PROTOCOL.md` Step 7: `status`, `correctness_issue`, `difficulty_issue`, `edits`, `confidence`.
5. Write `/tmp/qc_verdicts.json` (list of verdict objects, keyed by `row`).
6. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/qc-questions/scripts/qc_xlsx.py write <input.xlsx> /tmp/qc_verdicts.json <output.xlsx>`

Step 4 — Output workbook structure (verify after write):
- The **original sheet** is preserved verbatim with one new column `qc_status` placed at the **next truly empty column** in the sheet (scan all cells, not just headers). Each row's `qc_status` cell is color-coded: green = ALIGNED, amber = NEEDS_EDITS, red = NEEDS_EDITS with `confidence: LOW`.
- A **`QC Legend`** sheet documents the colour code.
- A **`Corrected` sheet** is created with the same headers as the original. Per-row behaviour:
  - **ALIGNED** rows are completely blank (no values) with a light green fill across the row.
  - **NEEDS_EDITS** rows show the post-edit content for the whole row (original values + edits applied), with a light amber fill on the row and a dark-amber + bold fill on cells that were actually edited so the diff pops at a glance.
  - **NEEDS_EDITS with `confidence: LOW`** rows use a light red row fill instead of amber (signal: escalate to human review before applying).
  - Plain-text edits to `content` / `option1..option6` are auto-wrapped in `<p>…</p>` so the Corrected rows remain upload-ready for the assessment platform.

**HARD CONSTRAINT — respect the marked spec:** `subject`, `topics`, and `difficulty` are the SPEC the question must match. They are NEVER edited by the QC. If an item drifts (e.g., marked EASY but Angoff lands in MEDIUM), the edits adjust `content` / `option1..option6` / `correctOption` to bring the item back to the marked tags. If the item cannot be aligned via content edits (e.g., a quant problem mistakenly tagged Verbal Ability), the verdict is `confidence: LOW` with a `correctness_issue` of "construct mismatch — escalate to author" and zero edits. The xlsx writer rejects (with a stderr warning) any edit whose `field` is `subject`, `topics`, or `difficulty`.

Step 5 — Print to the user:
- A concise aggregate report (counts by status, must-fix-first rows with their issue + smallest edit, low-confidence escalations).
- The output workbook path.
- One sanity-check instruction: "Open the original sheet, filter `qc_status` ≠ ALIGNED, cross-reference each amber row against the same row number in the Corrected sheet."

If the user passes a single standalone question instead of a file path, skip the xlsx I/O and emit a single YAML verdict block per `REPORT_TEMPLATE.md`. Still run the blind-solve in a subagent.

If anything in the workflow fails (parse error, subagent timeout, key mismatch on row count), surface the error verbatim and stop — do not paper over it. High-stakes assessment integrity depends on the QC being trustworthy.
