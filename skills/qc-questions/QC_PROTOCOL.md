# QC Protocol — Step-by-Step Discipline

The protocol is rigid because the default LLM failure mode on this task is **post-hoc rationalization of the marked answer**. Once you see `correctOption=option2`, every neuron in your network leans toward making option2 correct. The discipline below prevents that.

## The Iron Rule

> **You commit to (a) your answer AND (b) your difficulty rating before you see either marked value. Period.**

Two audit targets are held back simultaneously: `correctOption` (answer key) and `difficulty` (band tag). Both are subject to the same LLM failure mode — post-hoc rationalization of the marked value. If at any point you read either field before writing down your own committed value, the QC is invalid for that row. Start over for that row.

**For xlsx batch:** the main agent's context has seen every `correctOption` AND every marked `difficulty` during parsing. The only way to do a *structurally* blind solve AND a *structurally* blind difficulty rating is to dispatch the work to a fresh subagent whose prompt was built from the questions list only (both audit targets stripped by `scripts/qc_xlsx.py read`). This is mandatory, not optional. The canonical subagent prompt is in [SUBAGENT_PROMPT.md](SUBAGENT_PROMPT.md). Dispatch all batches in a single message (parallel) for both correctness and speed.

## Step 1 — Sanitize Input

For each question:
1. Strip HTML tags from `content` and each option. Keep inner text. Preserve `<math>`, `<code>`, `<table>` semantic content as plain text or markdown.
2. Note `subject`, `topics`, `questionType`. These three anchor the construct + MQC.
3. **Hide BOTH `correctOption` AND the marked `difficulty` value.** For batch xlsx, the script already strips both from the `questions` list and holds them in `_keys`; the main agent must never write either field into a subagent prompt. For standalone, mentally box both fields.
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

## Step 5 — Audience-Conditional Difficulty Estimation

See [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md) for full anchors. **Difficulty is the Angoff band predicted for the stated MQC, anchored by conceptual-step count.** Step counting is the ANCHOR (it keeps Angoff defensible — without it, Angoff is vibes); the BAND comes from where Angoff-for-this-MQC lands in the audience-conditional windows. Distractor design is a separate scoring step that drives a/c, not b.

**5a. Define MQC + lock the Angoff windows.** Write a one-sentence MQC definition for this item: who is sitting at the cut score the assessment is designed to enforce? Reuse across rows in the batch unless the assessment has multiple cut scores by section. Then look up the audience-conditional Angoff windows from SKILL.md Rule 6 (or use user-provided custom windows). State them explicitly in `qc_notes`:

```
mqc: <one-sentence>
angoff_windows: { EASY: <%>-<%>, MEDIUM: <%>-<%>, HARD: <%>-<%> }
```

Defaults from SKILL.md Rule 6:
- **Tier 1** (IIT / NIT-top, CAT-prep saturated): HARD 10-25%, MEDIUM 40-65%, EASY 80-95%
- **Tier 2** (state engineering, moderate prep): HARD 25-45%, MEDIUM 50-70%, EASY 75-90%
- **Tier 3** (entry-level IT-services, light prep): HARD 35-55%, MEDIUM 55-75%, EASY 75-95%
- **General / unknown**: HARD 25-50%, MEDIUM 50-75%, EASY 75-95%

The same 2-step item lands in DIFFERENT bands across these windows. That is the point.

**5b. Anchor — Count conceptual steps in the canonical solve.** A conceptual step is a discrete *reasoning* operation, not an arithmetic operation — three arithmetic operations in service of one concept count as one step. Record:
- `conceptual_steps`: <int>
- `conceptual_steps_note`: one line describing each step

This anchors the Angoff estimate in 5c. The step count is NOT the band — it's the input that makes the Angoff estimate non-arbitrary. A 1-step item with high prep exposure for the stated MQC may still produce a 90% Angoff (EASY for that audience); a 3-step item with low prep exposure may produce a 30% Angoff (HARD for that audience). Counting steps prevents Angoff from drifting into pure vibes.

**5b-bis. Dead-constraint check (constraint-based items only).** For items whose canonical solve relies on filtering a finite solution set against multiple stated constraints — modular arithmetic, Diophantine, multi-condition number-theory, multi-premise logic, constraint deduction — verify each stated constraint contributes to the final answer set:

1. Enumerate the candidate set against ALL stated constraints. Record the final answer(s).
2. For each constraint C: enumerate again with C removed. If the answer set is unchanged, C is DEAD — it adds apparent step count without adding filtering work.
3. Flag every dead constraint in `qc_notes` as `dead_constraints: [<list>]`. If any constraint is dead:
   - The item's true intrinsic difficulty is the step count MINUS the dead constraint(s) — the conceptual_steps anchor must be REDUCED accordingly before the Angoff estimate in 5c.
   - Prescribe a stem edit: either (a) tighten the range / conditions / coefficients so the dead constraint becomes load-bearing (preferred — preserves authorial intent), or (b) remove the dead constraint and accept the lower difficulty band.
   - Emit the alignment_prescriptions pair regardless — the dead-constraint fix is INDEPENDENT of the audience-conditional band alignment.

**Dead constraints + empty solution sets are mirror failures.** Both are stem defects where the constraint structure misrepresents the actual filtering work. The dead-constraint check catches both: a constraint that doesn't filter (vestigial) AND a constraint that over-filters (broken).

**Example.** Original Jatin item: (300, 360) × mod 9 = 5 × mod 7 = 2 × odd → empty set (338 fails parity). Mirror case (proposed Chetan rewrite): (95, 200) × mod 9 = 4 × mod 7 = 3 × odd → unique answer 157, parity dead. Fix the first by widening range to admit a CRT candidate that satisfies parity; fix the second by widening range so multiple CRT candidates exist and parity actually filters.

**5c. Estimate Angoff for THIS stated MQC. COMMIT BLIND.** Predict what % of the stated MQC cohort would solve this item correctly. Include:
- The conceptual-step anchor from 5b
- Prep-exposure adjustment: has this MQC cohort almost certainly seen this exact pattern in standardised prep (CAT, GMAT, GRE, NIIT-style sheets)? If yes, raise Angoff substantially — pattern recognition collapses the solve to a single recall step regardless of intrinsic complexity. If no, Angoff reflects the cohort's raw problem-solving ability.
- Construct-irrelevant variance: reading load, English proficiency, cultural reference, calculator availability. Cap or lower the estimate if any of these apply.

State the number in `qc_notes` with the reasoning chain. Avoid round 50% defaults — those are usually a refusal to estimate.

**5d. Map Angoff to band via the audience-conditional windows from 5a.** Take the Angoff % from 5c and look up which band it falls in using the windows you locked in 5a:

- Angoff in EASY window → `my_blind_difficulty = EASY`
- Angoff in MEDIUM window → `my_blind_difficulty = MEDIUM`
- Angoff in HARD window → `my_blind_difficulty = HARD`
- Angoff falls between windows (boundary) → pick the closer band and flag in `qc_notes`
- Angoff > EASY upper bound → floor item (P1 even if band matches)
- Angoff below HARD lower bound with the key marked correct → likely broken / verify correctness

**This is `my_blind_difficulty`** — the audience-conditional band. Commit it before any reveal. If you find yourself thinking "the marked tag is probably MEDIUM because…", stop. Compute Angoff for the stated MQC from the step-count anchor; map to band via the locked windows. The marked tag is unseen and irrelevant to this committed rating.

**5e. Sanity check — does the step count vs Angoff relationship make sense?** If the conceptual-step count is high (3+) but Angoff for this MQC is also high (80%+), the item has a recognised pattern for this cohort — note this in `qc_notes` as "high-exposure floor item: nominal complexity, low effective difficulty for stated MQC". If the conceptual-step count is low (1) but Angoff is also low (30%), the distractors must be doing extreme heavy lifting — note this too. These are not failures; they are accurate diagnoses of where information lives in the item.

**5d. Discrimination (a-proxy, 1–5).** Score against the rubric. Anchors: 1 = answerable by surface heuristics; 3 = at least two distinct misconceptions in distractors; 5 = graded distractor ladder catching candidates at distinct ability levels. Any construct-irrelevant variance (reading load, language proficiency, cultural reference) caps a-proxy at 2.

**5e. Pseudo-guessing (c-proxy, 1–5).** Count distractors that are *not obviously wrong* on inspection. For 4-option MCQs: 3 functioning → c=1; 2 functioning → c=2; 1 functioning → c=3; 0 functioning → c=5 (broken).

**5f. Reveal marked difficulty + compare to your committed blind rating.** Only at this point does `_keys` get opened for the row's `difficulty` (and `correctOption`, if not already revealed for the correctness comparison in Step 4). In batch mode the main agent does the reveal; the subagent never sees `_keys`. The comparison is between (a) your `my_blind_difficulty` — the Angoff-band-for-stated-MQC you committed in 5d — and (b) the marked tag, which is the spec for "how this item should behave for the stated audience". A mismatch means the item will not behave as marked when shipped to the stated MQC cohort.

- **Match** → `ALIGNED` on the difficulty layer. The item's Angoff for the stated MQC lands in the same band the spec claims; it will behave as tagged when shipped.
- **Your blind > marked** (item harder for this audience than tagged — e.g., blind HARD but marked MEDIUM; blind MEDIUM but marked EASY) → `TOO_HARD` — Angoff-for-stated-MQC sits in a lower-success window than the tag implies. Stem currently carries an extra conceptual step that the tag doesn't admit for this cohort. Prescribe stem-remove via [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md) `alignment_prescriptions.to_one_band_easier`.
- **Your blind < marked** (item easier for this audience than tagged — e.g., blind EASY but marked MEDIUM/HARD) → `TOO_EASY` — Angoff-for-stated-MQC sits in a higher-success window than the tag implies. Stem is missing a conceptual step that the tag implies for this cohort. Prescribe stem-add via [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md) `alignment_prescriptions.to_one_band_harder`.

**Tier-1 windows are STRICTER.** Tier-1 HARD is 10-25% Angoff (vs the default 25-50%), because CAT-prep saturation collapses routine patterns. A 1-step item with high pattern exposure produces ~90% Angoff for tier-1 → EASY; a 2-step item with no pattern exposure for tier-1 may still produce ~55% Angoff → MEDIUM. The same item marked HARD for a tier-1 cohort easily lands as a **two-band gap** (blind EASY vs marked HARD) — escalate as `confidence: LOW` and flag for human review, since two-band gaps usually indicate either an audience-misspec or a construct mismatch that single-step stem additions can't bridge.

**The marked tags are the spec, not a suggestion.** If the item drifts away from the marked `subject` / `topics` / `difficulty`, prescribe edits to `content` / `option1..option6` / `correctOption` that bring the item BACK into the marked tags for the stated MQC. Never propose retagging. If alignment requires changing what subject/topic the item tests (e.g., the item is arithmetic but tagged Verbal), that is a construct mismatch — emit `confidence: LOW` with a `correctness_issue` flagging the mismatch and recommend author escalation, do not retag.

**Every effort to align on difficulty mismatch.** Per SKILL.md Rule 4, a difficulty mismatch is a P1 ship-blocker that MUST carry a concrete stem-edit prescription that closes the gap. Defaulting to `confidence: LOW` with no edit is only allowed when the gap is too large to bridge without a construct-mismatch rewrite (e.g., a single-step arithmetic item marked HARD-for-tier-1 with no defensible chained extension inside the marked `topics`). For one-band gaps (EASY↔MEDIUM, MEDIUM↔HARD), the prescription library in [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md) gives you paste-able stem additions/removals — use them.

**Re-rating to match the marked band is forbidden.** If your blind rating disagrees with the marked band, the blind rating is the audit signal of drift, not an error to be corrected. Re-rating after the reveal corrupts the blind Angoff-for-MQC prediction — the whole point of committing `my_blind_difficulty` before reveal is to preserve an audit signal that hasn't been contaminated by knowing the spec. Saying "on reflection it's MEDIUM" after seeing the marked tag is the difficulty-side equivalent of "rationalizing the marked answer" — the failure mode the whole blind-rating discipline exists to prevent. The fix is a STEM edit, not a re-rate. In batch mode, the subagent's `my_blind_difficulty` is final and the main agent passes through the subagent's proposed stem edits without regenerating.

**The fix for `TOO_EASY` / `TOO_HARD` is ALWAYS a stem rewrite.** Add a conceptual step to raise Angoff-for-MQC into the next-harder window; remove a conceptual step to lower Angoff-for-MQC into the next-easier window. NEVER swap a distractor to "fix" a difficulty mismatch — distractor swaps move empirical p-value via carelessness-catching but do NOT change the conceptual-step anchor that drives Angoff-for-MQC. That is parameter contamination. Distractor edits are reserved for proxy_a / proxy_c failures.

**5g. Side-flags (even if difficulty ALIGNED) — these are distractor-layer issues, fixed in distractors:**
- `proxy_a ≤ 2` → flag for distractor rewrite (P1) — replace throwaways with named-misconception traps.
- `proxy_c ≥ 3` → flag for distractor strengthening (P1) — see above.
- Angoff > 95% → floor item (P1) — usually means distractors are all throwaways; rewrite them.
- Angoff < 25% with marked key correct → re-audit step 4; this is unusual for a non-trick item (P0).

Record in the verdict:

```yaml
irt_proxies:
  my_blind_difficulty: EASY | MEDIUM | HARD     # committed by subagent BEFORE _keys reveal
  conceptual_steps: <int>                       # the step count that justifies the band
  conceptual_steps_note: |
    <one-line description of the steps an MQC walks through>
  marked_difficulty: EASY | MEDIUM | HARD       # revealed by main agent from _keys
  difficulty_alignment: ALIGNED | TOO_EASY | TOO_HARD
  angoff_pct: <int>
  proxy_b: <signed float, derived from Angoff>
  proxy_a: <1-5>
  proxy_c: <1-5>
  mqc_definition: |
    <one sentence>
```

## Step 6 — Prescribe Edits (if any flag fires)

You — solver — write the edit. You have full content visibility (in batch mode the subagent is the solver; in standalone mode you are). Deferring drift to a "human review" downstream is a failure mode: by the time the row reaches a reviewer, the QC has already lost its judgement. Write the edit now.

Edits must be operationally executable. Bad:
> "Make the question harder."

Good:
> "In `option3`, replace 'plays' with 'play' — currently a clearly-wrong distractor (subject-verb agreement violated). Replace with a more tempting distractor that fails on a *different* rule (e.g., dangling modifier) to raise C4 from 2 to 4."

Use the prescription library in [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md). Every edit names the field (`stem` / `option1` / etc.), the operation (`replace` / `add` / `remove`), and the exact text change. Empty `edits` arrays are allowed **only** when the obstruction is external to the QC pipeline (missing chart, malformed source cell, construct mismatch) — and only with `confidence: LOW` so the row gets red-painted and surfaced for human attention.

## Step 7 — Emit Verdict (Lean, Edit-Centric)

The user wants only two things per row: **what's off** and **exactly what to change**. Internal IRT reasoning (Angoff_pct, proxy_a, proxy_c, MQC) drove your judgement in Step 5 — it does NOT appear in the output.

**Batch mode — main agent is a pass-through composer over TWO blind audit targets.** When this protocol runs inside the parallel subagent pipeline, the subagent has already produced per row, all generated without ever seeing `correctOption` or marked `difficulty`:

- (a) `my_answer` — committed before any reveal in Step 3.
- (b) `my_blind_difficulty` — the **Angoff-band-for-stated-MQC**, mapped through the audience-conditional windows the subagent locked at Step 5a against the stated MQC. The audience-conditional band decision is already baked into this field; the main agent does NOT re-window at compose time. Windows were locked at Step 5a and applied at 5d.
- (c) `proposed_edits` — paste-able edits for correctness issues (distractor flaws, `correctOption` corrections within the option set) and discrimination issues (`proxy_a` / `proxy_c` weak distractors).
- (d) `alignment_prescriptions` pair — `to_one_band_harder` and `to_one_band_easier` stem-edit prescriptions per [DIFFICULTY_RUBRIC.md](DIFFICULTY_RUBRIC.md), pre-written by the subagent against the stated MQC's windows. The main agent picks the appropriate one at reveal based on the direction of the blind-vs-marked gap.

(See [SUBAGENT_PROMPT.md](SUBAGENT_PROMPT.md) — the prescription table maps each detected issue to a paste-able edit, and the subagent has full content visibility so it is the right place to write the edit.)

The main agent's job on compose is:

1. Pass `subagent.proposed_edits` straight into `verdict.edits` with **no regeneration**. The subagent already wrote the edit; rewriting it on compose loses the blind-rate provenance.
2. Set `verdict.confidence = subagent.confidence`. **Do not down-grade for drift.** The autonomous-by-default rule means the subagent's confidence already accounts for whether it could prescribe a fix.
3. Add at most TWO cross-row edits the subagent structurally could not produce (these are the documented exceptions to pass-through, because the subagent never saw either audit target):
   - a `correctOption` flip when `my_answer` ≠ marked `correctOption` and `subagent.confidence == HIGH`.
   - a stem-edit ratification when `my_blind_difficulty` ≠ marked `difficulty` — the main agent picks the matching prescription from `subagent.alignment_prescriptions` (`to_one_band_harder` if blind < marked, `to_one_band_easier` if blind > marked) and passes it through verbatim with `why: "aligns from blind-rated {X} to marked {Y} for stated MQC via stem rewrite"`. The main agent does NOT re-window for the marked tag — the subagent already evaluated the stated-MQC windows at Step 5a and the prescriptions are pre-sized for those windows. If the subagent emitted no `alignment_prescriptions` for a difficulty mismatch at HIGH/MED confidence, that's a subagent regression (writer flags it RED) — the main agent does NOT invent the alignment edit at compose time.
4. **Never re-rate the item to match the marked difficulty, and never re-window the bands.** Both are rationalization-on-difficulty. The subagent's `my_blind_difficulty` is the audit signal for the stated MQC; the marked `difficulty` is the spec; the gap closes via stem edit, not via re-rate or re-window.

Anything else the main agent invents is a regeneration and breaks the architecture. If the subagent flagged drift but emitted no edits at HIGH/MED confidence, that is a subagent regression — the writer (`scripts/qc_xlsx.py`) catches it with a stderr warning and bumps the row's fill to RED, but the main agent should NOT paper over it by inventing edits at compose time.

**Standalone mode** (no subagent): you are both solver and prescriber. Run Steps 1–6 yourself with both audit targets mentally boxed, then emit the verdict below. Every NEEDS_EDITS row MUST carry at least one concrete edit unless the obstruction is genuinely external (construct mismatch, missing chart, malformed source cell, or a difficulty gap so large it requires a from-scratch rewrite) — in which case `confidence: LOW` and `edits: []`.

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
- If the item is misaligned with its marked subject/topic AND no `content`/`option` edit can fix it (construct mismatch), emit `correctness_issue` describing the mismatch + `confidence: LOW` + empty `edits` — escalate to a human author rather than silently retagging. This is the canonical case for empty `edits`.
- `confidence: LOW` → still emit any edits you are confident in, but the writer will paint the row red so the user knows to escalate before applying.
- **Autonomous-by-default:** every NEEDS_EDITS row MUST carry at least one concrete edit in `edits`. Empty `edits` are allowed ONLY when `confidence: LOW` AND the obstruction is external (construct mismatch, missing chart, malformed source). The xlsx writer enforces this with a stderr warning + RED fill if a NEEDS_EDITS row at MED/HIGH has empty edits — it does not block the write but does make the regression visible.

What stays *inside* the LLM's working memory and never appears in output:

- `irt_proxies` (Angoff_pct, proxy_b, proxy_a, proxy_c, MQC definition)
- Severity bands (used only for ordering the aggregate report)
- Per-distractor diagnostics
- Self-consistency method-A / method-B traces

If a future user asks "show your IRT reasoning", expand the verdict on request — but the default surface is lean.

**Aggregate-level blueprint-review pass (batch mode only).** After all per-row verdicts are composed, the main agent runs one final scan across the verdict set BEFORE writing the aggregate report:

1. Group rows by `(subject, topic)` section.
2. Within each section, count rows where `my_blind_difficulty ≠ marked difficulty` by **exactly two bands** (EASY vs HARD in either direction). One-band gaps do not count for this pass — they are handled by the per-row stem-edit prescription per SKILL.md Rule 4.
3. Split the 2-band-gap count by direction: `overrated` (blind < marked — the section is tagged harder than the items actually behave for the stated MQC) and `underrated` (blind > marked — tagged easier than items behave).
4. If, within a section, EITHER `overrated_2band / total_in_section > 0.20` OR `underrated_2band / total_in_section > 0.20`, append a `blueprint_review_flag` to the aggregate output with:
   ```yaml
   blueprint_review_flag:
     section: "<subject> / <topic>"
     direction: overrated | underrated
     count: <int>           # rows with same-direction 2-band gap
     section_total: <int>   # rows in section
     interpretation: |
       The test author's calibration of what <BAND> means for the stated MQC
       is broken at the section level, not at the item level. Recalibrate the
       blueprint for this section before shipping; per-item stem edits will
       not fix this.
   ```
5. Mixed-direction sections (some overrated, some underrated, neither direction >20%) do NOT trigger the flag — that is item-level noise per SKILL.md Rule 4-bis, not a calibration failure. Same-direction concentration is the diagnostic signal.
6. The aggregate-report writer surfaces every `blueprint_review_flag` at the TOP of the report (above must-fix counts, above low-confidence escalations) so the PM sees the bank-level calibration problem first — it cannot be fixed by accepting per-row edits.

This pass is read-only over the verdict set; it never re-touches per-row verdicts and never changes any row's `confidence` or `edits`. The 2-band gaps already carry `confidence: LOW` with no auto-edit per SKILL.md Rule 4-bis; the aggregate flag is the additional surfacing the bank needs.

## Red Flags — Stop and Restart

If you notice yourself doing any of these, the QC pass is contaminated:

- "The key says option2, so let me figure out why option2 is right..."
- "The marked tag says MEDIUM, so on reflection 2 steps does feel about right..." (difficulty-side rationalization — same shape as the answer-key one)
- "Maybe the question intends..." (it doesn't — only what's written counts)
- "Close enough" on numerical answers (it's not — verify exactly)
- "The author probably meant..." (no — audit what is written)
- Skimming options rather than evaluating each
- Skipping self-consistency on a quant question because "method A felt right"
- Marking `OK` for a stem you'd rate `AMBIGUOUS` if no key existed
- Treating a one-band difficulty mismatch as "close enough" and skipping the stem-edit prescription
- "I'll grade against my default mental model of who's taking this assessment, not the stated MQC." → silently audience-mismatched verdict, the worst class of failure because it looks right but isn't.

**All of these = QC invalid. Start the row over with a fresh subagent (re-dispatch the affected batch with a clean prompt that never touches `_keys`).**

## Rationalizations Catalogue

| Rationalization | Counter |
|---|---|
| "The marked key is probably right, authors checked it." | The whole job exists *because* keys are wrong. Audit, don't defer. |
| "Both options work but the marked one is the *best*." | `MULTIPLE_CORRECT` = P0. "Best of two correct" is not a valid MCQ. |
| "Time is short, skip self-consistency." | High-stakes assessment. Re-derive, no shortcut. |
| "Difficulty feels MEDIUM, skip the rubric." | Score intrinsic complexity (count conceptual steps). Vibes are not evidence. |
| "I'll just count conceptual steps and call that the band, ignoring the stated MQC." | **Audience-rationalization failure.** Step count is the ANCHOR, not the band. Two-step items can be EASY for tier-1 (90% Angoff) or HARD for tier-3 (35% Angoff). Without the MQC, you don't have a band — you have an anchor. Refuse to grade without an MQC. |
| "Tier-1 HARD = 25-50%, same as the default windows. Why bother with tier-specific windows?" | Because tier-1 candidates have CAT-style prep saturation. A pattern that's MEDIUM for the unprepared population is EASY for tier-1 (they recognise it on sight). To genuinely separate the top 15% from the rest of tier-1, items must operate above the routine-pattern layer — that's the 10-25% Angoff window. |
| "I blind-rated MEDIUM but the marked tag is HARD — on reflection, with that third constraint maybe it is HARD." | **Difficulty rationalization** (Rule 4 violation). The blind rating is the audit signal of drift. The fix is a stem edit (add a conceptual step), not a re-rate. Re-rating after reveal silently approves drift and corrupts the bank's band distribution. |
| "It's only off by one band, the prescription library is overkill." | One-band gaps are exactly what the prescription library is sized for. Apply the paste-able edit. 100 items each off by one band shifts the assessment's θ curve. |
| "Marked band is wrong, I'll swap a distractor to fix it." | **Parameter contamination.** Distractor swaps move empirical p-value, not b. Fix difficulty via stem rewrite. |
| "Item is intrinsically EASY but distractors are sharp, so the Angoff is MEDIUM — call it ALIGNED." | Angoff is a sanity check, not the source of truth. Stage-1 intrinsic complexity is b. EASY stays EASY. |
| "Distractors are bad but the key is correct, so OK." | Distractor weakness is a proxy_a/c problem. Prescribe distractor edits. P1 at minimum. |
| "The HTML probably renders fine." | Strip and re-read. Renders ≠ semantically clear. |
| "Solve and check is faster than blind-solve." | "Check" is rationalization. Solve fully before reading the key. |
| "I'll flag this as LOW and let a human decide." | Flagging is not fixing. If you have full content visibility, prescribe the edit. LOW is reserved for genuinely external obstructions (missing chart, construct mismatch). |
