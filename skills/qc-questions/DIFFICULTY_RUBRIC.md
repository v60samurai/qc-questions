# IRT-Aligned Difficulty Rubric (Pre-Calibration QC)

## Difficulty Is Audience-Conditional (read this first)

The same item is not the same difficulty for every bank. A 2-step weighted-average question is EASY for a tier-1 CAT-prep cohort that has drilled the pattern for two years, MEDIUM for tier-2 state-engineering aspirants who have seen the shape but not internalised it, and HARD for tier-3 entry-level IT candidates who have not. The step-count of the canonical solve doesn't change across audiences; what changes is the Angoff_pct the MQC of each tier would produce — and Angoff is what maps to the band.

Therefore: **conceptual-step count is the ANCHOR; Angoff-for-the-stated-MQC is the BAND.** The relationship is like a thermometer: calibration (step count) is what makes the reading defensible — without it, Angoff estimates are vibes — but the body-temperature reading (Angoff_pct landing in an audience-conditional window) is the actual answer. You need both. Step count alone tells you the cognitive shape; the band tells you whether that shape will discriminate in this cohort at this cut score.

Why this matters operationally: a 2-step weighted-average item is EASY for tier-1 because the MQC there has drilled the pattern enough that Angoff lands ~85%, but the same item is HARD for tier-3 because their MQC's Angoff lands ~40%. Same stem, same canonical solve, same step count, three different correct difficulty bands. Tag the band based on where Angoff-for-the-stated-MQC lands, not on absolute step count.

The Angoff windows below are audience-conditional defaults. The user can override them at invocation if their assessment uses different cut scores, different MQC anchors, or a different band carving:

| Audience | HARD | MEDIUM | EASY |
|---|---|---|---|
| Tier 1 (IIT/NIT-top, CAT-prep saturated) | 10-25% | 40-65% | 80-95% |
| Tier 2 (state engineering, moderate prep) | 25-45% | 50-70% | 75-90% |
| Tier 3 (entry-level IT, light prep) | 35-55% | 55-75% | 75-95% |
| General / unknown MQC | 25-50% | 50-75% | 75-95% |

Note the tier-1 HARD window is 10-25%, not the general default of 25-50%. This is because tier-1 cohorts have prep saturation: to discriminate the top 15% of candidates from the rest of the tier-1 cohort at the HARD cut, the item must operate ABOVE the routine-pattern layer the entire cohort has already drilled. An item that lands at Angoff 40% for tier-1 is MEDIUM there, not HARD, even though 40% would be HARD for tier-2/3.

This rubric judges items the way an IRT-aligned bank judges them: by **b** (difficulty), **a** (discrimination), and **c** (pseudo-guessing). Because pre-deployment items have no response data yet, we use **content-expert proxies** — Angoff-for-stated-MQC anchored by intrinsic solve complexity for b, distractor-functioning analysis for a, and effective-options counting for c. Once the bank has empirical response data, these proxies are replaced by calibrated parameters; until then, this is the rigorous substitute.

## The Cardinal Rule — Layer Separation

> **Anchor difficulty with conceptual-step count. Land the band via Angoff-for-stated-MQC in the audience-conditional window. Distractor design is a SEPARATE evaluation, scored after.**

The two layers are independent IRT parameters and must be evaluated independently:

| Parameter | What it measures | Where it lives | How to score |
|---|---|---|---|
| **b (difficulty)** | Where Angoff-for-stated-MQC lands in the audience-conditional window, anchored by intrinsic solve complexity | **The STEM** | Count conceptual steps to anchor the estimate, then estimate Angoff_pct for the MQC, then map to the audience-conditional band |
| **a (discrimination)** | Trap-resistance — how well the item separates prepared from unprepared candidates of the *same* intrinsic skill | **The DISTRACTORS** | Score how many distractors map to distinct, named MQC misconceptions |
| **c (pseudo-guessing)** | Effective guess floor from throwaway options | **The DISTRACTORS** | Count functioning distractors |

**Why this matters.** A 3-operation textbook ratio anchored at 1 conceptual step is EASY in b for any cohort that has drilled the pattern; the step count anchors the estimate but the Angoff landing in the audience window is the band. Sharp distractors raise a (better discrimination), they do NOT raise b. Conflating the two means you're using distractor sharpness to fake difficulty — that shifts the empirical p-value by catching carelessness, but it doesn't change the latent trait, and it adds noise to IRT calibration once the bank is deployed.

**Operational consequence.** When Angoff-for-stated-MQC falls outside the marked band's audience-conditional window, the fix is **always a stem rewrite that adds (or removes) a conceptual step** — which shifts the anchor and therefore shifts where Angoff lands. It is NEVER "swap the weakest distractor". Distractor edits are reserved for proxy_a / proxy_c failures, not for moving b.

Conceptual-step count anchors the Angoff estimate so it isn't vibes; Angoff-for-the-stated-MQC landing inside the audience-conditional window is the actual band call.

## Default Band ↔ b Mapping

The audience-conditional Angoff windows in the opening section are the primary band-mapping reference. The general-purpose table below is the fallback when the MQC tier is unspecified — it assumes a 3PL MCQ with `c ≈ 0.25` (four options) and an MQC sitting at `θ = 0` (cut score). Override defaults if the assessment uses different a/c assumptions, anchors MQC elsewhere, or carves the bank into 4+ difficulty bands.

| Marked band | Target b range | Angoff % for MQC (general / unknown MQC) |
|---|---|---|
| EASY        | b ≤ −0.5        | 75–95% |
| MEDIUM      | −0.5 < b ≤ +0.5 | 50–75% |
| HARD        | b > +0.5        | 25–50% |

For tier-1 / tier-2 / tier-3 cohorts, use the audience-conditional windows above; the same step-count anchor maps to a different Angoff and therefore a different band per tier.

Edge zones:
- Angoff > 95% → item is **floor** (no information; everyone passes) → flag P1 even if "EASY" tag.
- Angoff < the lower bound of the audience's HARD window (and item is correct) → item sits below pseudo-guessing floor → suggests defective distractors raising effective c, or broken item.

## The Three IRT Proxies

### B-proxy — Conceptual-Step Anchor + Angoff-for-MQC (Primary)

**Procedure — two stages, in this order:**

**Stage 1: Count the conceptual steps in the canonical solve to anchor the Angoff estimate.** Without this anchor, Angoff estimates are vibes. The step count constrains the plausible Angoff range so the estimate is defensible; it does NOT itself fix the band.

A "conceptual step" is a discrete reasoning operation MQC must execute — not an arithmetic operation. Three arithmetic operations chained in service of one concept (e.g., "sum the parts, divide total by sum, multiply by share") count as **one** conceptual step (apply-a-ratio). Three arithmetic operations crossing **conceptual boundaries** (e.g., "compute the ratio share, then apply a purity adjustment, then convert units") count as **three** conceptual steps.

The step-count → Angoff anchor varies by audience. The table below gives the cognitive shape; the band is determined by where Angoff-for-the-stated-MQC lands in the audience-conditional window.

| Conceptual-step count | Tier-1 anchor Angoff (drilled patterns) | Tier-2 anchor Angoff | Tier-3 anchor Angoff |
|---|---|---|---|
| 1 conceptual step, fully canonical / no abstraction | ~90% (EASY) | ~85% (EASY) | ~80% (EASY) |
| 2 conceptual steps, OR 1 step with a genuinely non-trivial choice | ~80% (EASY) | ~65% (MEDIUM) | ~45% (HARD) |
| 3+ conceptual steps, OR multi-constraint reasoning with binding-constraint identification, OR domain-specific abstraction MQC has not drilled | ~35% (MEDIUM-to-HARD) | ~30% (HARD) | ~15% (HARD) |

Examples (the band shifts by audience even though the step count doesn't):
- "Ratio 3:22 of 475 L" = 1 step (apply ratio) → EASY across all tiers.
- "Ratio 3:22 of 475 L, but stock concentrate is 80% pure" = 2 steps (apply ratio, then adjust for purity) → EASY for tier-1, MEDIUM for tier-2, HARD for tier-3.
- "Cost ≤ ₹22k, time ≤ 9h, time ≥ 7.25h, find max v" = 3+ steps (set up cost, identify the binding constraint among three, solve) → MEDIUM-to-HARD for tier-1, HARD for tier-2/3.

**Stage 2: Estimate Angoff_pct against the MQC and map to the audience-conditional window.** This is the band call.

1. Hold the construct of the **minimally-qualified candidate (MQC)** in mind. State your MQC definition explicitly in `qc_notes` for transparency — including which tier (1/2/3/general).
2. Imagine 100 such MQCs attempting the item independently.
3. Estimate the count answering correctly, anchored by the step-count expectations above. That % is your **Angoff_pct**.
4. Map Angoff_pct to a band using the audience-conditional windows from the opening section.

**Estimation aids (use whichever helps for the item type):**

- For verbal/grammar items: how confident would a candidate at MQC level be in the named rule? Did they likely encounter it in school but not master edge cases (→ ~65% for tier-2/3, ~80% for tier-1) vs. a high-school staple (→ ~85% across tiers)?
- For quant items: each conceptual step ≈ 0.85 chance for tier-1 MQC, ~0.75 for tier-2, ~0.65 for tier-3 → multiply.
- For domain knowledge: is the fact part of the canonical curriculum for MQC's role (→ 70–90%) or a niche extension (→ 30–50%)?
- For applied/scenario items: how readable is the scenario? Reading load that exceeds MQC literacy hurts Angoff even when content is "easy" — and the hurt is bigger for lower-tier MQCs.

**Reconciling step-count anchor and Angoff-for-MQC:**

| Step-count anchor implies | Angoff-for-MQC lands | Diagnosis | Fix |
|---|---|---|---|
| Matches marked band | Inside marked band's audience-conditional window | ALIGNED | None |
| Matches marked band | Outside marked band's window | Distractor quality issue (proxy_a or proxy_c) is pulling p-value off, but **b-anchor is fine** | Fix distractors, not the stem |
| Mismatches marked band | Outside marked band's window in same direction | b is genuinely wrong for this audience — step count anchors Angoff outside the marked band's window | **Rewrite stem to add/remove a conceptual step** so Angoff lands in the marked band's audience window. NEVER fix this with a distractor swap. |
| Mismatches marked band | Inside marked band's window anyway (i.e., empirical p-value "feels" right despite mismatched step count) | Distractor-engineering is masking a parameter problem | Stem still needs rewriting; current distractor-engineered look is parameter contamination |

**Hard rule:** the conceptual-step count anchors the Angoff estimate so it isn't vibes. The Angoff-for-stated-MQC landing inside the audience-conditional window is the band call. If the anchor and the Angoff disagree, look at the distractor set to explain the gap before moving the band.

### A-proxy — Discrimination

A high-discrimination item separates high-ability from low-ability candidates sharply. Score 1–5:

| A-proxy | Anchor |
|---|---|
| 1 | Item answerable by surface heuristics (length bias, position bias, "looks technical"). Top and bottom candidates pass roughly equally. Reject. |
| 2 | Distractors all target the same misconception → ability differences along *that one* dimension only. |
| 3 | At least two distinct misconceptions tested by the distractor set; correct option requires the named construct. |
| 4 | Each distractor maps to a *distinct, plausible* misconception that a lower-ability candidate would actually hold. Construct alignment tight (no construct-irrelevant variance from reading load, etc.). |
| 5 | Distractors form a graded difficulty ladder — the most attractive distractor would catch a near-passer; the least attractive would catch only the weakest. |

**Construct-alignment sub-checks (any failure caps a-proxy at 2):**
- The item primarily measures the named `subject`/`topics` — not a confound (reading speed, language proficiency, cultural reference).
- The stem is free of clues that telegraph the answer (length, grammar agreement between stem and only one option, repeated stem keywords in correct option only).
- No "test-wiseness" path: alphabetical position pattern, "All of the above"/"None of the above", or a single option that contradicts every other.

### C-proxy — Effective Guessing Floor

Count distractors that a randomly-guessing MQC could plausibly select (i.e., not obviously wrong on inspection).

| Functioning distractors (out of 3 in a 4-option MCQ) | C-proxy | Effective guess floor |
|---|---|---|
| 3 | 1 | 25% |
| 2 | 2 | ~33% |
| 1 | 3 | ~50% |
| 0 | 5 | ~100% (item is broken) |

For 5-option or 6-option items, scale proportionally. Flag any item with C-proxy ≥ 3 as P1 regardless of b alignment — it leaks information through poor distractors.

## Anti-Pattern: Formula-Recall Mistagged as HARD

A common mistagging pattern across many published banks: items tagged HARD when their only barrier is recalling a standard formula (weighted mean, harmonic mean for average speed, percentage change, mixture/dilution `(1 − r/v)^n`, simple-interest vs compound-interest, ratio-of-totals, time-and-work LCM). These items are EASY-to-MEDIUM for any audience that has drilled the formula — they are NEVER intrinsically HARD.

**Diagnostic test.** If the canonical solve reduces to "remember formula X, plug in numbers" the item is EASY. If it reduces to "remember formula X, plug in numbers, then do one more reasoning step that the formula doesn't cover" the item is MEDIUM. HARD requires one of:
- **3+ chained CONCEPTS** (not chained operations within one concept)
- **Non-obvious problem decomposition** — the right approach isn't pattern-matchable from the stem; the MQC must construct the method, not retrieve it
- **Multi-constraint integration where constraints INTERACT** (not independent filters that can be checked one-by-one)
- **Domain-specific abstraction the cohort has not drilled** — genuinely novel framing within the marked subject/topic

**How this manifests.** When > 50% of a section's HARD-tagged items reduce to "recall formula X" under the dead-constraint + step-count audit, the section is suffering from formula-recall mistagging. The fix is NOT to swap distractors or add a dead constraint to the stem; it's to RE-AUTHOR with the multi-concept / non-obvious-decomposition / multi-constraint-integration criteria above.

**Subagent emit.** When the subagent rates a stem as EASY-or-MEDIUM blind but the marked tag is HARD AND the canonical solve fits the "recall formula X + plug in numbers" shape, emit `mistag_reason: formula_recall_overrated` in qc_notes. This lets the aggregate report identify the anti-pattern as a class, not just as a set of isolated 2-band gaps.

**Operational rule.** Formula recall ≠ HARD. Multi-step formula recall = MEDIUM at most. HARD = the cohort can't pattern-match their way to the method.

## Putting It Together

| Diagnostic | What it means | Default severity |
|---|---|---|
| Angoff-for-stated-MQC outside marked band's audience-conditional window | Mistagged difficulty for this audience | P0 if EASY-tagged-but-HARD in screening; else P1 |
| A-proxy ≤ 2 | Item won't separate abilities → low information | P1 |
| C-proxy ≥ 3 | Effective guess floor inflated → noisy data once deployed | P1 |
| Construct-alignment failure | Item measures wrong construct | P0 — item must be rewritten or removed |
| Length / position giveaway | Test-wiseness shortcut | P1 |
| Floor item (Angoff > 95% for any tier) | No information at any θ | P1 (keep only if used for confidence-building) |
| Below-floor item (Angoff < lower bound of HARD window for stated audience, with correct key) | Likely broken; verify correctness | P0 (re-audit correctness) |
| Tier-1 two-band gap: blind Angoff lands in EASY window (80-95%) but marked HARD (10-25%) | Pattern is drilled; single stem-add cannot bridge two bands | P0 — re-author with 3+ chained constraints or relax marked tag to MEDIUM/EASY in blueprint review |

## Edit Prescription Library

**Foundational rules for this section:**

1. The marked `subject`, `topics`, and `difficulty` are the SPEC. Every prescription below adjusts `content` / `option1..option6` / `correctOption` to move the item INTO the marked band. **Never retag.** If the item cannot reasonably be brought into the marked band without changing what subject/topic it tests, that is a construct mismatch — flag `confidence: LOW` and recommend escalation, do not change the tags.

2. **Layer separation is non-negotiable.** Difficulty (b) is fixed by STEM edits. Discrimination (a) and guessing-floor (c) are fixed by DISTRACTOR edits. Crossing the layers is parameter contamination — it shifts empirical p-value via carelessness-catching without changing the latent trait, and it adds noise to IRT calibration once the bank is deployed.

### To raise difficulty (Angoff-for-stated-MQC lands above the marked band's audience-conditional window)

**Rule: rewrite the STEM to add ONE conceptual step. Do NOT swap a distractor.**

WHEN to use: Angoff-for-stated-MQC falls above the upper bound of the marked band's audience-conditional window (e.g., Angoff 85% for tier-2 on a MEDIUM-marked item where the tier-2 MEDIUM window is 50-70%). The step-count anchor confirms the item is under-built for the audience. The fix is to introduce a second concept the candidate must reason about — not to make an existing concept harder to spot. The answer will likely change; update `correctOption` accordingly (and any options that need to display new numbers).

| Pattern of the over-easy item | Stem-rewrite prescription | Worked sketch |
|---|---|---|
| Single-step ratio / proportion | Add a purity, efficiency, or wastage adjustment that operates on the ratio result | "Ratio 3:22 of 475 L → fertilizer" becomes "Ratio 3:22 of 475 L → fertilizer, but stock is only 80% pure" |
| Single-step unit conversion | Add a sub-group or scaling factor that must be applied AFTER conversion | "Convert 14,400/tonne to per-kg" becomes "Convert 14,400/tonne to per-kg, then apply a 15% bulk discount" |
| Single-step percent change | Replace with a target-vs-input distinction (reverse direction) | "Grew 25%, find new value" becomes "Grew 25% to reach 100,000, find original value AND amount of growth" |
| Single-step weighted average | Add a third group, or a sub-group with a fractional weight | "Two groups, find weighted avg" becomes "Three groups with one sub-group reported separately" |
| Direct arithmetic | Add a constraint that bounds the candidate's choice (e.g., "the highest value of v such that all of these hold") | One-shot calculation becomes constraint-satisfaction |

**Special case — tier-1 two-band gap (blind=EASY, marked=HARD):** when the blind Angoff-for-stated-MQC lands in the tier-1 EASY window (80-95%) but marked HARD (target 10-25%), that is a TWO-BAND gap. A single stem-add (one extra conceptual step) shifts Angoff by ~15-20 percentage points for tier-1 — not enough to bridge two bands. The dominant cause is overtagging HARD on a pattern the tier-1 cohort has already drilled. Prescription: `confidence: LOW`, surface as `"item won't discriminate at tier-1 cut score; either re-author with 3+ chained constraints (introducing genuinely novel composition the cohort has not drilled) or relax marked tag to MEDIUM/EASY in blueprint review."` Do not attempt the single-step bridge — it will look harder but Angoff will still land in MEDIUM at best.

**Anti-patterns when raising difficulty (these do NOT work and represent the parameter-contamination failure mode):**
- Swapping the weakest distractor for a "near-miss" trap — moves p-value via carelessness, does not change b. The question is still EASY, just with sharper traps.
- Making numbers uglier (decimals, primes) — fails the construct (it's now testing arithmetic precision, not the named topic) and doesn't add a conceptual step.
- Lengthening the wording without adding a step — adds reading load, not cognitive load. Caps proxy_a, doesn't move b.
- Adding "All of the above" / "None of the above" — drops proxy_a, doesn't move b.
- Adding more options (5th, 6th) — drops proxy_c, doesn't move b.

### To lower difficulty (Angoff-for-stated-MQC lands below the marked band's audience-conditional window)

**Rule: rewrite the STEM to remove ONE conceptual step. Do NOT soften a distractor.**

WHEN to use: Angoff-for-stated-MQC falls below the lower bound of the marked band's audience-conditional window (e.g., Angoff 35% for tier-2 on a MEDIUM-marked item where the tier-2 MEDIUM window is 50-70%). The step-count anchor confirms the item is over-built for the audience.

| Pattern of the over-hard item | Stem-rewrite prescription |
|---|---|
| Multi-step item where step 1 is the only real cognitive load | Pre-compute step 1 in the stem and state its result, leaving step 2 as the candidate's task |
| Item with technical vocabulary unfamiliar to MQC | Replace with plain-language equivalent if the construct allows ("amortised cost" → "average cost per operation"); leave construct-relevant terms intact |
| Item with implicit unit conversion | State the converted unit explicitly in the stem |
| Multi-constraint item where one constraint is non-binding for all options | Drop the redundant constraint — it adds reading load without cognitive load |

**Anti-pattern when lowering difficulty:**
- Softening a distractor (replacing a sharp near-miss with a throwaway) — reduces a, may reduce empirical p-value the wrong way, leaves b unchanged. The question is still HARD.

### To fix discrimination (proxy_a ≤ 2) — distractor layer

WHEN to use: proxy_a ≤ 2 AND Angoff-for-stated-MQC sits inside the marked band's audience-conditional window (i.e., the difficulty is fine for this audience but discrimination is the failure mode).

| Symptom | Edit |
|---|---|
| All distractors target same misconception | Rewrite 1–2 distractors to test *different* misconceptions a lower-ability candidate would hold. Spell out which misconception each distractor catches in `qc_notes`. |
| Throwaway distractor (nobody picks) | Replace with a plausible near-miss that maps to a named MQC misconception. |
| Correct answer detectable by length | Pad shorter options or trim the correct one to equalise lengths. |
| Construct-irrelevant variance (reading load) | Simplify stem language without changing the construct (shorter sentences, common vocabulary, remove subordinate clauses). |
| Stem-option keyword leakage | Reword the correct option so it doesn't echo stem keywords more than distractors do. |

### To fix guessing-floor (proxy_c ≥ 3) — distractor layer

WHEN to use: proxy_c ≥ 3 regardless of where Angoff-for-stated-MQC lands — guess-floor is an information-leak problem independent of the band call.

| Symptom | Edit |
|---|---|
| Two or more obvious throwaways | Rewrite each as a *plausible* wrong answer mapped to a real misconception. |
| Negation-only distractor | Replace with a substantive alternative (negations are usually weak distractors). |
| Distractors share a structural giveaway | Restructure so each option has similar surface form (units, length, grammar). |

### To fix `WRONG_KEY` / `MULTIPLE_CORRECT` / `NO_CORRECT` / `AMBIGUOUS`

(Same as before — see prior version: switch `correctOption`, tighten stem qualifier, add precision constraint, etc.)

### Worked-example prescriptions (auto-prescribed by the QC)

The autonomous-by-default rule (SKILL.md rule 6) requires the QC to write a concrete edit for every NEEDS_EDITS row at HIGH or MED confidence. Pattern library below — each line gives an item shape, the diagnostic, and a paste-able edit shape. Use these as templates when the matching pattern fires.

**Layer separation reminder:** difficulty fixes go in the STEM. Distractor fixes go in the options. The examples below tag each pattern with the layer it operates on. Do not blend them.

**Too-easy ratio / proportion item (Angoff-for-stated-MQC above marked band's window; step-count anchor = 1): add a purity / efficiency / wastage adjustment in the stem.**
- *Diagnostic:* step-count anchor = 1 step (EASY-anchor); Angoff-for-stated-MQC lands above the upper bound of the marked band's audience-conditional window; existing distractors may or may not be sharp — doesn't matter, b is wrong for this audience.
- *Layer:* STEM (b-parameter).
- *Edit:* introduce a second concept the candidate must reason about AFTER applying the ratio. Common templates: "stock is only X% pure", "Y% of the solution evaporates before application", "the mixture must be diluted by factor Z post-mixing".
- *Worked example:* "Ratio 3:22 of 475 L solution, find fertilizer concentrate" (1-step anchor; Angoff ~85% for tier-2 → EASY). Marked MEDIUM (tier-2 MEDIUM window 50-70%) → Angoff outside window above. Rewrite stem: "Ratio 3:22 of 475 L solution, but stock concentrate is only 80% pure (inert filler excluded from the 475 L target)" (2-step anchor; Angoff ~65% for tier-2 → lands in MEDIUM window). Answer changes from 57 L to 71.25 L; flip `correctOption` accordingly on key reveal.

**Too-easy unit-conversion item: add a downstream scaling factor in the stem.**
- *Diagnostic:* step-count anchor = 1 (the conversion); Angoff-for-stated-MQC lands above the marked band's audience-conditional window.
- *Layer:* STEM.
- *Edit:* require the candidate to apply the converted value within a second operation. "Convert ₹/tonne to ₹/kg" becomes "convert ₹/tonne to ₹/kg, then apply a 15% bulk-order discount".

**Too-hard item (Angoff-for-stated-MQC below marked band's window): pre-compute one step in the stem.**
- *Diagnostic:* step-count anchor = 3+; Angoff-for-stated-MQC lands below the lower bound of the marked band's audience-conditional window (e.g., Angoff 35% for tier-2 on MEDIUM-marked item).
- *Layer:* STEM.
- *Edit:* state the result of step 1 in the stem so the candidate only has to execute steps 2 and 3. E.g., "Convert the 480 km route into hours at 60 km/h" becomes "The route takes 8 hours at 60 km/h. What is …".

**Low-discrimination item (proxy_a ≤ 2), difficulty itself aligned: rewrite throwaway distractors as named-misconception traps.**
- *Diagnostic:* Angoff-for-stated-MQC sits inside the marked band's audience-conditional window (difficulty is fine for this audience); one or more distractors are throwaways nobody would pick; proxy_a ≤ 2.
- *Layer:* DISTRACTORS (a-parameter).
- *Edit:* identify each throwaway and replace with a plausible wrong answer tied to a *named* misconception MQC would actually make. Spell the misconception out in `why`.
- *Worked example:* "Net profit/loss on the trade" with correct `+₹240`. Distractors include obvious throwaway. Replace with `−₹240` (sign-flip trap), `+₹60` (forgot to multiply by quantity), `+₹2,400` (off-by-10 unit slip). Difficulty unchanged, discrimination lifted from 2 to 4.

**Low-discrimination speed/rate item: add the arithmetic-mean trap as a distractor.**
- *Diagnostic:* item involves harmonic mean (average speed for round-trip at speeds A and B); Angoff-for-stated-MQC sits inside the marked band's audience-conditional window; distractor set contains no `(A+B)/2` option; proxy_a low.
- *Layer:* DISTRACTORS.
- *Edit:* compute `(A+B)/2` and include it as a distractor. Doesn't change the step-count anchor (solve is still "apply harmonic mean") and doesn't shift Angoff into a different band, but it catches candidates who reach for the naive average — lifting proxy_a from 2 to 4.

**Ambiguous number-property item: tighten range or add a div-by-3 constraint.**
- *Diagnostic:* `ambiguity_risk: yes` on an item like "How many two-digit numbers satisfy property P?" where P admits multiple defensible counts depending on whether range endpoints are inclusive, or whether divisibility by 1 / by 3 / etc. is required.
- *Edit:* tighten the stem with an explicit range (`"between 10 and 99 inclusive"`) and an additional constraint that narrows to a unique count (`"and divisible by 3"`).
- *Example:* "How many two-digit multiples of 5 are there?" admits 18 (inclusive of both endpoints) or 16 (exclusive). Tighten to "How many positive integers between 10 and 99 inclusive are multiples of 15?" — unique answer 6 (15, 30, 45, 60, 75, 90).

**Over-constrained Constraint Deduction item: loosen one constraint to break the must-true chain.**
- *Diagnostic:* `multiple_correct_risk: yes` because the puzzle's constraints force EVERY listed option to be true (any of them satisfies the deduction). Common in seating-arrangement, ordering, and logic-grid items.
- *Edit:* remove or weaken one premise so that exactly one of the listed conclusions remains forced. Test which constraint is "redundant" by checking which can be dropped without changing the unique-answer property of the puzzle.
- *Example:* "A, B, C, D sit in a row. A is to the left of B. B is to the left of C. C is to the left of D. Which must be true?" — every option (A<B, B<D, A<D, etc.) is forced by the chain. Drop "B is to the left of C" so the puzzle has only `A<B` and `C<D`. Now `A<B` is forced but `A<D` is not — only one option is must-true.

Each of these is paste-able into a `proposed_edits` entry: pick the field, copy the current cell value into `from`, write the new value into `to`, and tag `why` with the diagnostic ("too-hard distractor softened", "added arithmetic-mean trap", etc.).

## Worked Examples

### Example 1 — EASY-tagged grammar item (too hard because of an in-option complexity layer)

Item: "Identify the grammatically incorrect sentence." Four options testing subject-verb agreement, collective nouns, and "along with" constructions. Correct option violates SVA — but with an intervening prepositional phrase that obscures the violation. MQC stated as tier-2.

- **Step-count anchor**: For verbal "spot the error" items, the conceptual load lives in the OPTION the candidate must analyse (the "stem" of the per-option judgement is the option text itself). The error in option2 — "The list of pending tasks were reviewed" — requires two concepts: (1) identify the head noun behind the prepositional phrase, (2) apply SVA. 2-step anchor.
- **Angoff-for-stated-MQC (tier-2)**: ~60% → lands in tier-2 MEDIUM window (50-70%).
- **Marked**: EASY (tier-2 EASY window 75-90%).
- **Diagnosis**: Angoff lands below the marked EASY window → too-hard mismatch for this audience. The cognitive layer that needs simplifying is INSIDE the offending option, not the stem itself (since verbal-error items work this way).
- **A-proxy**: 3 — two distinct misconceptions tested across the distractor set.
- **C-proxy**: 1 — three functioning distractors.
- **Edit (operates on the cognitive complexity of the option text — the verbal-item analogue of a stem rewrite):**
  - Rewrite the offending option to remove one conceptual layer: "The list of pending tasks were reviewed" → "The list were reviewed". The SVA error is now a one-concept solve (no intervening phrase to navigate).
  - Expected post-edit anchor = 1 concept; expected post-edit Angoff ≈ 85% for tier-2 → lands in EASY window.
- **What this is NOT**: a distractor swap. The option text being edited is structurally part of the construct under test, not a discrimination layer.

### Example 2 — HARD-tagged quant item with weak distractors

Item: A 3-step probability problem. Distractors include one off-by-one, one with reversed sign, and one obvious throwaway (10× the right answer). MQC stated as tier-2.

- **Step-count anchor**: 3 steps → HARD anchor.
- **Angoff-for-stated-MQC (tier-2)**: 35% → lands in tier-2 HARD window (25-45%) → ALIGNED with marked HARD.
- **A-proxy**: 2 — the throwaway makes near-passers' false confidence high; only two misconception traps actually function.
- **C-proxy**: 2 — effective guess floor is ~33%, not 25%. With Angoff at 35%, the item is barely above the guess floor → low information.
- **Verdict**: difficulty ALIGNED, but a-proxy + c-proxy combine to make this a P1 item-information failure. Edit the throwaway distractor into a third real distractor (e.g., a candidate who forgets the conditional). Marked HARD tag is preserved; the edit improves discrimination without moving the item's difficulty band. Expected post-edit a-proxy = 4, c-proxy = 1.

### Example 3 — Construct mismatch (cannot be aligned to marked tags)

Item: A multi-step arithmetic word problem, marked `subject = Verbal Ability`, `topics = Grammar and Sentence Correction`, `difficulty = EASY`.

- **Angoff-for-stated-MQC**: 40% → lands in HARD window for any tier.
- **Subject/topic check**: item tests arithmetic, NOT grammar. Construct misalignment.
- **Verdict**: cannot be fixed by editing content/options — the item would have to be rewritten as a completely different grammar question to match the marked subject/topic. This is OUT OF SCOPE for QC.
- **Output**: `confidence: LOW`, `correctness_issue: "Construct mismatch — item tests arithmetic but marked as Verbal Ability/Grammar. Cannot align via content edits; needs a from-scratch rewrite by the author."`, `edits: []`. The xlsx writer leaves the Corrected row showing the original content (un-fixable rows are surfaced via the red row fill).

### Example 4 — Tier-1 two-band gap (HARD-tagged item on a drilled pattern)

Item: 2-step weighted-average problem with one sub-group reported separately. Marked HARD. MQC stated as tier-1 (CAT-prep saturated).

- **Step-count anchor**: 2 steps → MEDIUM anchor for general, but tier-1 has drilled this pattern.
- **Angoff-for-stated-MQC (tier-1)**: ~85% → lands in tier-1 EASY window (80-95%).
- **Marked**: HARD (tier-1 HARD window 10-25%).
- **Diagnosis**: blind Angoff lands in EASY window, marked HARD → TWO-BAND gap. The tier-1 cohort has drilled this exact pattern; a single stem-add will shift Angoff by ~15-20pp at best (still landing in MEDIUM, not HARD).
- **Verdict**: `confidence: LOW`, surface as `"item won't discriminate at tier-1 cut score; either re-author with 3+ chained constraints introducing novel composition the cohort has not drilled, or relax marked tag to MEDIUM/EASY in blueprint review."` Do not attempt the single-step bridge.

### Example 5 — Dead-constraint detection (Chetan stem rewrite case)

Item: Number-theory stem of the form "Find N such that 95 < N < 200, N mod 9 = 4, N mod 7 = 3, and N is odd." Emitted as a `to_one_band_harder` alignment prescription on a prior pass. MQC stated as tier-2.

- **Step-count anchor (as emitted)**: 4 constraints → 3 conceptual steps (CRT residue solve via mod 9 ∩ mod 7, then parity filter, then range filter). MEDIUM-to-HARD anchor.
- **Dead-constraint check (Step 5b-bis)**:
  - Enumerate full solution set: CRT gives N ≡ 31 (mod 63) → candidates in (95, 200) are 94 + 63 = 157 (next is 220, out of range). Single candidate 157.
  - Drop parity: candidates are still {157}. 157 is odd; parity filters nothing.
  - **`dead_constraints: ["odd"]`** — parity adds zero filtering. An MQC who skips parity gets the same answer.
- **Diagnosis**: emitted stem-edit prescription is itself defective. True intrinsic difficulty is step count MINUS dead parity = 2 conceptual steps (CRT residue solve + range filter). The stem masquerades as a 3-step solve but rewards skipping a step.
- **Re-prescribed stem (parity becomes load-bearing)**: widen range so multiple CRT candidates exist and parity actually filters. Replace `95 < N < 250` (instead of `< 200`). Now candidates in (95, 250) are {157, 220}; parity drops 220 (even) → unique answer 157, and parity is load-bearing because dropping it yields {157, 220} — two candidates, ambiguous answer.
- **Verdict**: re-emit the alignment prescription with the widened range. Self-check the new stem against Step 5b-bis before passing through — confirm no constraint is still dead under the rewrite.
- **Mirror case (informational)**: original Jatin item (300 < P < 360, mod 9 = 5, mod 7 = 2, odd) has empty solution set (338 is the unique CRT candidate, fails parity). Same defect class — constraint structure misrepresents the filtering work, just in the over-filter direction. Both are caught by Step 5b-bis.

## Reporting Fields (changes from the cognitive-load rubric)

Replace the old `difficulty_axes: {C1..C5, total}` with:

```yaml
irt_proxies:
  angoff_pct: <0-100>            # Angoff-for-stated-MQC; the band call
  step_count_anchor: <int>       # conceptual-step count; anchors the Angoff estimate
  audience_tier: <tier-1|tier-2|tier-3|general>   # which audience-conditional window applies
  proxy_b: <float, signed>       # derived from Angoff via the audience-conditional mapping
  proxy_a: 1-5                   # discrimination proxy
  proxy_c: 1-5                   # effective guess-floor proxy
  mqc_definition: |
    <one-line statement of the MQC for this assessment / row, including audience tier>
```

Plus the existing verdict fields (`correctness`, `difficulty_check`, `severity`, `confidence`, `proposed_edits`, `qc_notes`).
