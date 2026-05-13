# Contributing

Thanks for considering a contribution. This plugin gates real high-stakes assessments, so we hold a tight quality bar.

## Dev setup

```bash
git clone https://github.com/v60samurai/qc-questions.git
cd qc-questions
python3 -m venv .venv && source .venv/bin/activate
pip install openpyxl pytest ruff
pytest -q          # should be green
ruff check .       # should be clean
```

To iterate on the skill against your own data: symlink the skill into Claude Code:

```bash
ln -s "$(pwd)/skills/qc-questions" ~/.claude/skills/qc-questions
ln -s "$(pwd)/commands/qc-questions.md" ~/.claude/commands/qc-questions.md
```

Both will pick up edits live; no reinstall step.

## The Iron Law

Skill changes follow [test-driven documentation](https://github.com/anthropics/superpowers/tree/main/skills/writing-skills):

> **No skill edit without a failing test first.**

This applies to SKILL.md, QC_PROTOCOL.md, DIFFICULTY_RUBRIC.md, SUBAGENT_PROMPT.md, REPORT_TEMPLATE.md. Write a test that demonstrates the gap (a baseline scenario where Claude Code fails the desired behaviour) *before* you change the skill. Verify the edit makes that test pass. Verify it doesn't break the existing smoke suite in `tests/`.

Same applies to the script: write the pytest case for the new behaviour first, watch it fail, implement.

Untested edits get rejected at PR review. This is the bar that keeps high-stakes assessment integrity meaningful.

## What kinds of contributions are welcome

| Type | Examples | Bar |
|---|---|---|
| New edit prescriptions in DIFFICULTY_RUBRIC.md | "How to lower discrimination when proxy_a = 5 is over-discriminating at the cut" | Show the gap in a real item; cite the IRT principle |
| New MQC presets in `examples/mqc_presets.md` | NEET-PG, CFA Level I, GMAT Quant | One sentence MQC + 2-line justification |
| Script improvements | Better HTML stripping, multi-sheet xlsx support, CSV input | Pytest case + open issue first |
| Rationalization catchers | New entries in QC_PROTOCOL.md "Rationalizations Catalogue" | Must show the exact failure mode in a baseline subagent run |
| Bug fixes | Off-by-one in column placement, broken HTML edge case | Failing test → fix → green |

## What is OUT of scope

- Adding support for non-MCQ items (essay, constructed-response, coding). The IRT proxies in this skill are MCQ-specific.
- Empirical IRT calibration from response data. That's a separate tool — this plugin handles only pre-calibration content-expert QC.
- Cultural / accessibility / language-quality audits. Out of scope; the plugin focuses on construct, correctness, and difficulty.
- Tag taxonomy validation (does "Grammar and Sentence Correction" belong under "Verbal Ability"?). Tag taxonomy is owned by the assessment platform, not by QC.

## Adding a new edit prescription

1. Identify the gap. Run the existing skill on a real item where the prescription would apply. Confirm the skill currently misses it.
2. Write a pytest case in `tests/` that demonstrates the desired behaviour. Watch it fail.
3. Update `DIFFICULTY_RUBRIC.md`'s prescription library with:
   - Goal (one line, e.g. "Lower Angoff for MQC by ~8 pts").
   - Edit prescription (concrete operation on `content` / `option*` / `correctOption`).
   - Which IRT proxy it moves (`b`, `a`, or `c`).
4. Run pytest; verify your test now passes and nothing else broke.
5. Add a short example to the rubric's "Worked Examples" if the prescription targets a non-obvious case.

## Adding a new MQC preset

`examples/mqc_presets.md` is a flat one-liner-per-context list. Append at the bottom; don't reorder. Keep each preset to one sentence and link to the source assessment context if public (e.g. a job posting, a syllabus PDF).

## PR checklist

- [ ] Failing test was written before the implementation
- [ ] `pytest -q` is green on Python 3.11
- [ ] `ruff check .` is clean
- [ ] CHANGELOG.md `[Unreleased]` section has a one-line entry
- [ ] If you changed prompts in `SUBAGENT_PROMPT.md` or `QC_PROTOCOL.md`, ran one full xlsx batch end-to-end and verified the output workbook is sane
- [ ] No machine-specific paths introduced

## Code style

- Python: 4-space indent, type hints encouraged but not mandatory. Stdlib + `openpyxl` only — no new runtime deps without an issue first.
- Markdown: keep lines under 100 chars; use tables for reference content, bullets for narrative.
- Skill prompts: use the writing-skills CSO rules. The frontmatter `description` is for triggering conditions only — do NOT summarise the workflow there.

## Reporting issues

Open an issue with:
- A minimal xlsx (or pasted question) that reproduces the problem.
- What the skill emitted.
- What you expected.
- The MQC you used (or that you wanted the skill to use).

For security-sensitive issues (e.g. a sandboxing concern in a hook), email the maintainer instead of opening a public issue.
