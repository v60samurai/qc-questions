# QC Protocol — Step-by-Step Discipline

The protocol is rigid because the default LLM failure mode on this task is **post-hoc rationalization of the marked answer**. Once you see `correctOption=option2`, every neuron in your network leans toward making option2 correct. The discipline below prevents that.

## The Iron Rule

> **You commit to your answer before you see the marked key. Period.**

If at any point you read `correctOption` before writing down your own answer, the QC is invalid. Start over.

**For xlsx batch:** the main agent's context has seen every `correctOption` during parsing. The only way to do a *structurally* blind solve is to dispatch the work to a fresh subagent. This is mandatory, not optional. The canonical subagent prompt is in [SUBAGENT_PROMPT.md](SUBAGENT_PROMPT.md). Dispatch all batches in a single message (parallel) for both correctness and speed.

## Step 1 — Sanitize Input

For each question:
1. Strip HTML tags from `content` and each option. Keep inner text. Preserve `<math>`, `<code>`, `<table>` semantic content as plain text or markdown.
2. Note `subject`, `topics`, `questionType`, `difficulty` (marked).
3. **Hide `correctOption` value.** For batch xlsx, the script already does this when dispatching to subagents. For standalone, mentally box it.
4. Note how many options are populated (4, 5, or 6).

## Step 2 — Comprehension Pass

Read the stem once. Answer in your head:
- What is being asked? (Identify the *exact* task verb: identify / compute / select / infer / fix.)
- What domain knowledge does this require?
- Is the stem unambiguous? Are there contradictory clauses?

If the stem is genuinely ambiguous (e.g., "which sentence is correct" when two are grammatically correct), STOP. Flag `AMBIGUOUS` → P0 → no further work needed.

## Step 3 — Independent Solve

Solve the question. Write down:
- Your chosen option (e.g., `option2`).
- A 1–3 sentence justification.
- A check on each *other* option: why is it wrong? If you cannot give a concrete reason why a non-chosen option is wrong, it may be defensibly correct → `MULTIPLE_CORRECT`.

For **quantitative / logical** questions, solve twice with independent methods:
- Method A: direct computation
- Method B: substitution, dimensional check, edge-case verification, or alternative algorithm
- If A ≠ B → `LOW_CONFIDENCE` → P0 escalation.

For **verbal / language** questions: identify the specific rule being tested (e.g., subject-verb agreement, tense consistency, parallelism). State the rule. Verify each option against the rule.

For **knowledge recall** questions: state the canonical fact and source-of-truth class (textbook fact / widely-accepted / disputed). If "disputed" → `AMBIGUOUS` → P0.

## Step 4 — Reveal & Compare

NOW read `correctOption`. Compare:

| Your answer vs marked | Outcome |
|---|---|
| Match, all distractors clearly wrong, single defensible answer | `OK` |
| Match, but you also found another defensibly-correct option | `MULTIPLE_CORRECT` (P0) |
| Mismatch, your answer is defensible and marked one is wrong | `WRONG_KEY` (P0) |
| Mismatch, you could defend either | `AMBIGUOUS` (P0) |
| Marked answer is one of the options but none is genuinely correct | `NO_CORRECT` (P0) |
| Your confidence in your own solve was LOW | `LOW_CONFIDENCE` (P0) — never default to "trust the key" |

**Rationalization-resistance rule:** Discovering that your answer differs from the key is NOT evidence the key is right. Re-derive from scratch. If your re-derivation still disagrees, the key is wrong. The marked key is the artifact under audit — it has no authority.

## Step 5 — IRT-Aligned Difficulty Estimation

See [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md) for full anchors. Three proxies, then map to band.

**5a. Define MQC (minimally-qualified candidate).** Write a one-sentence MQC definition for this item: who is sitting at the cut score the assessment is designed to enforce? Reuse the same MQC across rows in a batch unless the assessment intentionally has multiple cut scores by section.

**5b. Modified Angoff (b-proxy).** Estimate the % of MQCs who would answer this item correctly. State the number in `qc_notes` along with the reasoning chain ("MQC knows rule X but trips on edge case Y; ~65% correct"). Avoid round 50% defaults — those are usually a refusal to estimate. Use estimation aids in the rubric for the item type (verbal, quant, recall, applied).

**5c. Map Angoff to band (defaults; override if platform spec differs):**
- EASY: 75–95%
- MEDIUM: 50–75%
- HARD: 25–50%
- Out-of-range: Angoff > 95% → floor item; Angoff < 25% with the key marked correct → likely broken / verify correctness.

**5d. Discrimination (a-proxy, 1–5).** Score against the rubric. Anchors: 1 = answerable by surface heuristics; 3 = at least two distinct misconceptions in distractors; 5 = graded distractor ladder catching candidates at distinct ability levels. Any construct-irrelevant variance (reading load, language proficiency, cultural reference) caps a-proxy at 2.

**5e. Pseudo-guessing (c-proxy, 1–5).** Count distractors that are *not obviously wrong* on inspection. For 4-option MCQs: 3 functioning → c=1; 2 functioning → c=2; 1 functioning → c=3; 0 functioning → c=5 (broken).

**5f. Compare to marked.** If Angoff falls inside the marked band's window → `ALIGNED`. If Angoff above (item is easier than tagged) → `TOO_EASY`. If Angoff below (harder than tagged) → `TOO_HARD`.

**The marked tags are the spec, not a suggestion.** If the item drifts away from the marked `subject` / `topics` / `difficulty`, prescribe edits to `content` / `option1..option6` / `correctOption` that bring the item BACK into the marked tags. Never propose retagging. If alignment requires changing what subject/topic the item tests (e.g., the item is arithmetic but tagged Verbal), that is a construct mismatch — emit `confidence: LOW` with a `correctness_issue` flagging the mismatch and recommend author escalation, do not retag.

**5g. Side-flags (even if difficulty ALIGNED):**
- `proxy_a ≤ 2` → flag for distractor / construct rewrite (P1).
- `proxy_c ≥ 3` → flag for distractor strengthening (P1).
- Angoff > 95% → floor item (P1).
- Angoff < 25% with marked key correct → re-audit step 4; this is unusual for a non-trick item (P0).

Record in the verdict:

```yaml
irt_proxies:
  angoff_pct: <int>
  proxy_b: <signed float, derived from Angoff>
  proxy_a: <1-5>
  proxy_c: <1-5>
  mqc_definition: |
    <one sentence>
```

## Step 6 — Prescribe Edits (if any flag fires)

Edits must be operationally executable. Bad:
> "Make the question harder."

Good:
> "In `option3`, replace 'plays' with 'play' — currently a clearly-wrong distractor (subject-verb agreement violated). Replace with a more tempting distractor that fails on a *different* rule (e.g., dangling modifier) to raise C4 from 2 to 4."

Use the prescription library in [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md). Every edit names the field (`stem` / `option1` / etc.), the operation (`replace` / `add` / `remove`), and the exact text change.

## Step 7 — Emit Verdict (Lean, Edit-Centric)

The user wants only two things per row: **what's off** and **exactly what to change**. Internal IRT reasoning (Angoff_pct, proxy_a, proxy_c, MQC) drove your judgement in Step 5 — it does NOT appear in the output.

Emit a single YAML block per row:

```yaml
- row: <int or "standalone">
  status: ALIGNED | NEEDS_EDITS
  correctness_issue: <one-line or null>
  difficulty_issue:  <one-line or null>
  edits:
    - field: <stem | option1..option6 | correctOption | difficulty>
      from: "<exact current value>"
      to:   "<exact replacement>"
      why:  "<one-line: fixes correctness | aligns to <BAND> | both>"
  confidence: HIGH | MED | LOW
```

Output rules:

- `ALIGNED` rows: empty `edits`, both issues `null`. No commentary, no IRT scores.
- **Editable fields:** `content` (a.k.a. `stem`), `option1..option6`, `correctOption`. NOTHING ELSE.
- **Immutable fields (the SPEC):** `subject`, `topics`, `difficulty`. Never emit an edit whose `field` is one of these. The xlsx writer rejects them.
- Every `edits[].to` is paste-able into the xlsx cell. No placeholders.
- For `correctOption` edits, `from` and `to` are enum values (`option1..option6`).
- For text edits, `from` must be the verbatim current text (not a paraphrase) and `to` is the verbatim replacement.
- If correctness AND difficulty are both off, list correctness edits first; check whether the correctness fix already resolves the difficulty issue before adding more edits.
- If the item is misaligned with its marked subject/topic AND no `content`/`option` edit can fix it (construct mismatch), emit `correctness_issue` describing the mismatch + `confidence: LOW` + empty `edits` — escalate to a human author rather than silently retagging.
- `confidence: LOW` → still emit any edits you are confident in, but the writer will paint the row red so the user knows to escalate before applying.

What stays *inside* the LLM's working memory and never appears in output:

- `irt_proxies` (Angoff_pct, proxy_b, proxy_a, proxy_c, MQC definition)
- Severity bands (used only for ordering the aggregate report)
- Per-distractor diagnostics
- Self-consistency method-A / method-B traces

If a future user asks "show your IRT reasoning", expand the verdict on request — but the default surface is lean.

## Red Flags — Stop and Restart

If you notice yourself doing any of these, the QC pass is contaminated:

- "The key says option2, so let me figure out why option2 is right..."
- "Maybe the question intends..." (it doesn't — only what's written counts)
- "Close enough" on numerical answers (it's not — verify exactly)
- "The author probably meant..." (no — audit what is written)
- Skimming options rather than evaluating each
- Skipping self-consistency on a quant question because "method A felt right"
- Marking `OK` for a stem you'd rate `AMBIGUOUS` if no key existed

**All of these = QC invalid. Start the row over with a fresh subagent.**

## Rationalizations Catalogue

| Rationalization | Counter |
|---|---|
| "The marked key is probably right, authors checked it." | The whole job exists *because* keys are wrong. Audit, don't defer. |
| "Both options work but the marked one is the *best*." | `MULTIPLE_CORRECT` = P0. "Best of two correct" is not a valid MCQ. |
| "Time is short, skip self-consistency." | High-stakes assessment. Re-derive, no shortcut. |
| "Difficulty feels MEDIUM, skip the rubric." | Score the axes. Vibes are not evidence. |
| "Distractors are bad but the key is correct, so OK." | Mark `TOO_EASY` and prescribe distractor edits. P2 at minimum. |
| "The HTML probably renders fine." | Strip and re-read. Renders ≠ semantically clear. |
| "Solve and check is faster than blind-solve." | "Check" is rationalization. Solve fully before reading the key. |
