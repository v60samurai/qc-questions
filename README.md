# qc-questions

A Claude Code plugin that QCs IRT-aligned MCQ assessment banks for **correctness** and **difficulty alignment**, then emits a colour-coded Corrected workbook with the exact edits applied in-cell.

Catches the failures that humans miss when reviewing hundreds of items: silently wrong answer keys, two defensibly-correct options, items mistagged into the wrong difficulty band, distractors so weak they leak information. Built for high-stakes assessment use where 100% accuracy matters.

## Why this exists

LLMs are bad at QCing answer keys because once they see `correctOption=option2`, they rationalise option2 as right. This plugin breaks that failure mode structurally: every blind solve happens in a fresh subagent context that has *literally never seen* the marked key. Then the main agent reveals keys, composes verdicts, and writes an edit-centric output.

Three things distinguish this from "just ask Claude to QC my questions":

1. **Blind-solve protocol via parallel subagents.** Six rows per worker, all batches dispatched concurrently. The subagent context cannot leak the marked answer because it never received it.
2. **IRT-anchored difficulty estimation, not vibes.** Each item gets a Modified Angoff %-correct estimate (for a minimally-qualified candidate at the cut), a discrimination proxy (`a`), and a pseudo-guessing proxy (`c`). The marked EASY/MEDIUM/HARD band is checked against this estimate.
3. **The marked tags are the spec, not editable.** `subject`, `topics`, `difficulty` are immutable. If an item drifts, the plugin edits `content` / `options` / `correctOption` to pull it back to the marked tags. Never silently retag.

## Install

```bash
# In Claude Code:
/plugin install v60samurai/qc-questions
```

Manual install (until plugin manager is set up):
```bash
git clone https://github.com/v60samurai/qc-questions.git ~/qc-questions
ln -s ~/qc-questions/skills/qc-questions ~/.claude/skills/qc-questions
ln -s ~/qc-questions/commands/qc-questions.md ~/.claude/commands/qc-questions.md
```

Python deps: `openpyxl`. Install once: `pip install openpyxl`.

## Use

### Slash command (xlsx batch)

```
/qc-questions /path/to/Bulk\ Upload.xlsx --mqc "entry-level IT-services screening candidate at the cut, English-medium Indian schooling"
```

### Auto-trigger (no slash)

Just describe what you want — the skill auto-loads on phrases like "QC my question bank", "audit this xlsx", "verify difficulty alignment".

### Standalone question

Paste a question with options + metadata; ask "QC this MCQ". You get a single YAML verdict block back.

## Required xlsx columns

| Header | Required? | Notes |
|---|---|---|
| `content` | yes | stem text (HTML wrappers OK) |
| `option1`..`option4` | yes | populated |
| `option5`, `option6` | optional | for 5/6-option items |
| `correctOption` | yes | enum: `option1`..`option6` |
| `questionType` | yes | `MULTIPLE_CHOICE_QUESTION` |
| `subject` | yes | the marked subject — **immutable** |
| `topics` | yes | the marked topic — **immutable** |
| `difficulty` | yes | `EASY` / `MEDIUM` / `HARD` — **immutable** |

Any additional columns (`hints`, `tags`, `reportParameter`, etc.) are preserved untouched.

## Output structure

Running the skill on `<file>.xlsx` produces `<file>__qc.xlsx` with three sheets:

| Sheet | What it contains |
|---|---|
| **Original** (e.g. `Sheet1`) | Your input verbatim + one new column `qc_status` (`ALIGNED` / `NEEDS_EDITS`) placed at the next truly empty column. Colour-coded: green = aligned, amber = needs edits, red = needs edits with LOW confidence (escalate). |
| **QC Legend** | Small reference sheet documenting the colour code. |
| **Corrected** | Same headers as Original. **ALIGNED rows are blank with a green fill.** **NEEDS_EDITS rows are fully populated with the post-edit content** (original + edits applied), with an amber row fill and *dark-amber bold* on the specific cells that changed so the diff pops at a glance. LOW-confidence rows are red-filled. |

### Visual example

ALIGNED row in Corrected sheet (just the colour, no values):
```
[ green ][ green ][ green ][ green ]   ...   [ green ]
```

NEEDS_EDITS row where `option3` and `correctOption` were edited:
```
[ amber: content ][ amber: option1 ][ amber: option2 ]
[ DARK AMBER BOLD: <new option3> ]
[ amber: option4 ]   ...   [ DARK AMBER BOLD: option1 ]   ...
```

You scan the Original sheet's `qc_status` column, jump to the same row number in Corrected, and the dark-amber cells tell you exactly what changed.

## What it catches

| Failure mode | How it's detected | Output |
|---|---|---|
| Wrong answer key | Blind solve disagrees with marked `correctOption` | `correctOption` edit |
| Two defensibly-correct options | Subagent flags `multiple_correct_risk` | distractor rewrite |
| Ambiguous stem | Subagent flags `ambiguity_risk` | stem rewrite |
| Item mistagged into wrong band | Angoff_pct outside marked band's window | `content`/`option` edits to pull Angoff back into the marked band |
| Weak distractors (low `a`) | proxy_a ≤ 2 | distractor rewrite |
| Inflated guess floor (high `c`) | proxy_c ≥ 3 | distractor rewrite |
| Construct mismatch (item tests wrong subject/topic) | Subagent flags `construct_mismatch` | `confidence: LOW` + escalation note (no auto-edit) |

## What it does NOT do (anti-features)

This is not a magic wand. It deliberately refuses to do certain things.

- **Does not grade candidate responses.** This QCs *items*, not test takers.
- **Does not work on constructed-response / essay / coding items.** MCQ only.
- **Does not replace empirical IRT calibration.** Once you have real response data (200+ candidates per item), the discrimination, difficulty, and guessing parameters should be estimated empirically. The Modified Angoff estimate here is the pre-calibration proxy.
- **Does not retag `subject`, `topics`, or `difficulty`.** Those are the spec the question must match. If an item drifts, the plugin edits the question; if alignment is impossible, it escalates with `confidence: LOW`. Override with `--allow-retag` for legacy cleanup, but the default keeps your bank composition stable.
- **Does not auto-apply edits on `LOW` confidence rows.** The writer paints them red so you escalate to a human reviewer before merging.
- **Does not validate against a curriculum or syllabus map.** It checks whether the item measures roughly the marked subject/topic, not whether it covers a specific learning objective.
- **Does not detect plagiarism, language quality, accessibility, or cultural bias.** Those are separate audits.

## How the IRT proxies map to difficulty bands

Defaults assume a 4-option MCQ with pseudo-guessing `c ≈ 0.25` and the minimally-qualified candidate (MQC) sitting at `θ = 0`:

| Marked band | Target `b` | Angoff %-correct for MQC |
|---|---|---|
| EASY   | b ≤ −0.5         | 75–95% |
| MEDIUM | −0.5 < b ≤ +0.5  | 50–75% |
| HARD   | b > +0.5         | 25–50% |

Override these defaults if your platform calibrates differently. See [`skills/qc-questions/DIFFICULTY_RUBRIC.md`](skills/qc-questions/DIFFICULTY_RUBRIC.md) for the full anchors and edit prescription library.

## Repository layout

```
qc-questions/
├── plugin.json
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── commands/
│   └── qc-questions.md        # /qc-questions slash command
├── skills/
│   └── qc-questions/
│       ├── SKILL.md
│       ├── QC_PROTOCOL.md     # blind-solve discipline
│       ├── DIFFICULTY_RUBRIC.md
│       ├── SUBAGENT_PROMPT.md # canonical blind-solve worker prompt
│       ├── REPORT_TEMPLATE.md
│       └── scripts/
│           └── qc_xlsx.py     # xlsx I/O
├── examples/
│   ├── sample_bank.xlsx
│   ├── sample_bank__qc.expected.xlsx
│   └── mqc_presets.md
├── tests/
│   └── test_qc_xlsx.py
└── .github/workflows/ci.yml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). TL;DR: the writing-skills Iron Law applies — no edit to the skill files without a failing test first.

## License

MIT. See [LICENSE](LICENSE).
