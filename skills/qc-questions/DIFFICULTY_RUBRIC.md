# IRT-Aligned Difficulty Rubric (Pre-Calibration QC)

This rubric judges items the way an IRT-aligned bank judges them: by **b** (difficulty), **a** (discrimination), and **c** (pseudo-guessing). Because pre-deployment items have no response data yet, we use **content-expert proxies** — intrinsic solve complexity for b, distractor-functioning analysis for a, and effective-options counting for c. Once the bank has empirical response data, these proxies are replaced by calibrated parameters; until then, this is the rigorous substitute.

## The Cardinal Rule — Layer Separation

> **Score intrinsic solve complexity FIRST, then map to band. Distractor design is a SEPARATE evaluation, scored after.**

The two layers are independent IRT parameters and must be evaluated independently:

| Parameter | What it measures | Where it lives | How to score |
|---|---|---|---|
| **b (difficulty)** | Intrinsic cognitive complexity of the canonical solve | **The STEM** | Count conceptual steps, depth of abstraction, domain-knowledge level required |
| **a (discrimination)** | Trap-resistance — how well the item separates prepared from unprepared candidates of the *same* intrinsic skill | **The DISTRACTORS** | Score how many distractors map to distinct, named MQC misconceptions |
| **c (pseudo-guessing)** | Effective guess floor from throwaway options | **The DISTRACTORS** | Count functioning distractors |

**Why this matters.** A 3-operation textbook ratio is EASY in b, full stop, regardless of how sharp the distractors are. Sharp distractors raise a (better discrimination), they do NOT raise b. Conflating the two means you're using distractor sharpness to fake difficulty — that shifts the empirical p-value by catching carelessness, but it doesn't change the latent trait, and it adds noise to IRT calibration once the bank is deployed.

**Operational consequence.** When the marked difficulty band ≠ the intrinsic solve complexity, the fix is **always a stem rewrite that adds (or removes) a conceptual step**. It is NEVER "swap the weakest distractor". Distractor edits are reserved for proxy_a / proxy_c failures, not for moving b.

Angoff_pct is used downstream as a sanity check that the stem rewrite actually moved the cognitive load — not as the primary driver of the difficulty call.

## Default Band ↔ b Mapping

Override these defaults if the platform's calibration spec differs. The mapping below assumes a 3PL MCQ with `c ≈ 0.25` (four options) and the minimally-qualified candidate (MQC) sitting at `θ = 0` (cut score). Override defaults if the assessment uses different a/c assumptions, anchors MQC elsewhere, or carves the bank into 4+ difficulty bands.

| Marked band | Target b range | Angoff % for MQC (expected) |
|---|---|---|
| EASY        | b ≤ −0.5        | 75–95% |
| MEDIUM      | −0.5 < b ≤ +0.5 | 50–75% |
| HARD        | b > +0.5        | 25–50% |

Edge zones:
- Angoff > 95% → item is **floor** (no information; everyone passes) → flag P1 even if "EASY" tag.
- Angoff < 25% (and item is correct) → item sits below pseudo-guessing floor → suggests defective distractors raising effective c, or broken item.

## The Three IRT Proxies

### B-proxy — Intrinsic Solve Complexity (Primary) + Angoff Sanity Check

**Procedure — two stages, in this order:**

**Stage 1: Count the conceptual steps in the canonical solve.** This is the b-parameter. Do this BEFORE estimating Angoff so the answer isn't anchored on empirical p-value (which is contaminated by distractor sharpness).

A "conceptual step" is a discrete reasoning operation MQC must execute — not an arithmetic operation. Three arithmetic operations chained in service of one concept (e.g., "sum the parts, divide total by sum, multiply by share") count as **one** conceptual step (apply-a-ratio). Three arithmetic operations crossing **conceptual boundaries** (e.g., "compute the ratio share, then apply a purity adjustment, then convert units") count as **three** conceptual steps.

| Intrinsic solve complexity | Maps to band |
|---|---|
| 1 conceptual step, fully canonical / no abstraction | EASY |
| 2 conceptual steps, OR 1 step with a genuinely non-trivial choice (e.g., reverse-direction, target-vs-input distinction) | MEDIUM |
| 3+ conceptual steps, OR multi-constraint reasoning with a binding-constraint identification, OR domain-specific abstraction MQC has not specifically drilled | HARD |

Examples:
- "Ratio 3:22 of 475 L" = 1 step (apply ratio) → EASY, even if distractors are sharp.
- "Ratio 3:22 of 475 L, but stock concentrate is 80% pure" = 2 steps (apply ratio, then adjust for purity) → MEDIUM.
- "Cost ≤ ₹22k, time ≤ 9h, time ≥ 7.25h, find max v" = 3+ steps (set up cost, identify the binding constraint among three, solve) → HARD.

**Stage 2: Estimate Angoff_pct against the MQC** for sanity-check purposes only.

1. Hold the construct of the **minimally-qualified candidate (MQC)** in mind. State your MQC definition explicitly in `qc_notes` for transparency.
2. Imagine 100 such MQCs attempting the item independently.
3. Estimate the count answering correctly. That % is your **Angoff_pct**.

**Estimation aids (use whichever helps for the item type):**

- For verbal/grammar items: how confident would a candidate at MQC level be in the named rule? Did they likely encounter it in school but not master edge cases (→ ~65%) vs. a high-school staple (→ ~85%)?
- For quant items: each conceptual step ≈ 0.85 chance for MQC → multiply.
- For domain knowledge: is the fact part of the canonical curriculum for MQC's role (→ 70–90%) or a niche extension (→ 30–50%)?
- For applied/scenario items: how readable is the scenario? Reading load that exceeds MQC literacy hurts Angoff even when content is "easy".

**Reconciling Stage 1 and Stage 2:**

| Stage 1 (intrinsic) | Stage 2 (Angoff) | Diagnosis | Fix |
|---|---|---|---|
| Matches marked band | Inside marked band's window | ALIGNED | None |
| Matches marked band | Outside marked band's window | Distractor quality issue (proxy_a or proxy_c) is pulling p-value off, but **b is fine** | Fix distractors, not the stem |
| Mismatches marked band | Roughly tracks Stage 1 | b is genuinely wrong — intrinsic complexity ≠ marked band | **Rewrite stem to add/remove a conceptual step**. NEVER fix this with a distractor swap. |
| Mismatches marked band | Tracks marked band (i.e., empirical p-value "feels" right despite mismatched intrinsic complexity) | Distractor-engineering is masking a parameter problem | Stem still needs rewriting; current distractor-engineered look is parameter contamination |

**Hard rule:** Stage 1 is the source of truth for b. Stage 2 is a sanity check that the distractor set is reasonable. If they disagree, trust Stage 1 and look at the distractor set to explain the gap.

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

## Putting It Together

| Diagnostic | What it means | Default severity |
|---|---|---|
| Angoff_pct outside marked band's range | Mistagged difficulty | P0 if EASY-tagged-but-HARD in screening; else P1 |
| A-proxy ≤ 2 | Item won't separate abilities → low information | P1 |
| C-proxy ≥ 3 | Effective guess floor inflated → noisy data once deployed | P1 |
| Construct-alignment failure | Item measures wrong construct | P0 — item must be rewritten or removed |
| Length / position giveaway | Test-wiseness shortcut | P1 |
| Floor item (Angoff > 95%) | No information at any θ | P1 (keep only if used for confidence-building) |
| Below-floor item (Angoff < 25% with correct key) | Likely broken; verify correctness | P0 (re-audit correctness) |

## Edit Prescription Library

**Foundational rules for this section:**

1. The marked `subject`, `topics`, and `difficulty` are the SPEC. Every prescription below adjusts `content` / `option1..option6` / `correctOption` to move the item INTO the marked band. **Never retag.** If the item cannot reasonably be brought into the marked band without changing what subject/topic it tests, that is a construct mismatch — flag `confidence: LOW` and recommend escalation, do not change the tags.

2. **Layer separation is non-negotiable.** Difficulty (b) is fixed by STEM edits. Discrimination (a) and guessing-floor (c) are fixed by DISTRACTOR edits. Crossing the layers is parameter contamination — it shifts empirical p-value via carelessness-catching without changing the latent trait, and it adds noise to IRT calibration once the bank is deployed.

### To raise difficulty (intrinsic solve complexity is too low for the marked band)

**Rule: rewrite the STEM to add ONE conceptual step. Do NOT swap a distractor.**

The fix is to introduce a second concept the candidate must reason about — not to make an existing concept harder to spot. The answer will likely change; update `correctOption` accordingly (and any options that need to display new numbers).

| Pattern of the over-easy item | Stem-rewrite prescription | Worked sketch |
|---|---|---|
| Single-step ratio / proportion | Add a purity, efficiency, or wastage adjustment that operates on the ratio result | "Ratio 3:22 of 475 L → fertilizer" becomes "Ratio 3:22 of 475 L → fertilizer, but stock is only 80% pure" |
| Single-step unit conversion | Add a sub-group or scaling factor that must be applied AFTER conversion | "Convert 14,400/tonne to per-kg" becomes "Convert 14,400/tonne to per-kg, then apply a 15% bulk discount" |
| Single-step percent change | Replace with a target-vs-input distinction (reverse direction) | "Grew 25%, find new value" becomes "Grew 25% to reach 100,000, find original value AND amount of growth" |
| Single-step weighted average | Add a third group, or a sub-group with a fractional weight | "Two groups, find weighted avg" becomes "Three groups with one sub-group reported separately" |
| Direct arithmetic | Add a constraint that bounds the candidate's choice (e.g., "the highest value of v such that all of these hold") | One-shot calculation becomes constraint-satisfaction |

**Anti-patterns when raising difficulty (these do NOT work and represent the parameter-contamination failure mode):**
- Swapping the weakest distractor for a "near-miss" trap — moves p-value via carelessness, does not change b. The question is still EASY, just with sharper traps.
- Making numbers uglier (decimals, primes) — fails the construct (it's now testing arithmetic precision, not the named topic) and doesn't add a conceptual step.
- Lengthening the wording without adding a step — adds reading load, not cognitive load. Caps proxy_a, doesn't move b.
- Adding "All of the above" / "None of the above" — drops proxy_a, doesn't move b.
- Adding more options (5th, 6th) — drops proxy_c, doesn't move b.

### To lower difficulty (intrinsic solve complexity is too high for the marked band)

**Rule: rewrite the STEM to remove ONE conceptual step. Do NOT soften a distractor.**

| Pattern of the over-hard item | Stem-rewrite prescription |
|---|---|
| Multi-step item where step 1 is the only real cognitive load | Pre-compute step 1 in the stem and state its result, leaving step 2 as the candidate's task |
| Item with technical vocabulary unfamiliar to MQC | Replace with plain-language equivalent if the construct allows ("amortised cost" → "average cost per operation"); leave construct-relevant terms intact |
| Item with implicit unit conversion | State the converted unit explicitly in the stem |
| Multi-constraint item where one constraint is non-binding for all options | Drop the redundant constraint — it adds reading load without cognitive load |

**Anti-pattern when lowering difficulty:**
- Softening a distractor (replacing a sharp near-miss with a throwaway) — reduces a, may reduce empirical p-value the wrong way, leaves b unchanged. The question is still HARD.

### To fix discrimination (proxy_a ≤ 2) — distractor layer

| Symptom | Edit |
|---|---|
| All distractors target same misconception | Rewrite 1–2 distractors to test *different* misconceptions a lower-ability candidate would hold. Spell out which misconception each distractor catches in `qc_notes`. |
| Throwaway distractor (nobody picks) | Replace with a plausible near-miss that maps to a named MQC misconception. |
| Correct answer detectable by length | Pad shorter options or trim the correct one to equalise lengths. |
| Construct-irrelevant variance (reading load) | Simplify stem language without changing the construct (shorter sentences, common vocabulary, remove subordinate clauses). |
| Stem-option keyword leakage | Reword the correct option so it doesn't echo stem keywords more than distractors do. |

### To fix guessing-floor (proxy_c ≥ 3) — distractor layer

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

**Too-easy ratio / proportion item (intrinsic solve is 1 conceptual step but marked MEDIUM): add a purity / efficiency / wastage adjustment in the stem.**
- *Diagnostic:* intrinsic-solve scoring returns 1 step → EASY; marked MEDIUM; existing distractors may or may not be sharp — doesn't matter, b is wrong.
- *Layer:* STEM (b-parameter).
- *Edit:* introduce a second concept the candidate must reason about AFTER applying the ratio. Common templates: "stock is only X% pure", "Y% of the solution evaporates before application", "the mixture must be diluted by factor Z post-mixing".
- *Worked example:* "Ratio 3:22 of 475 L solution, find fertilizer concentrate" (1 step, EASY). Rewrite stem: "Ratio 3:22 of 475 L solution, but stock concentrate is only 80% pure (inert filler excluded from the 475 L target)" (2 steps: apply ratio → adjust for purity = MEDIUM). Answer changes from 57 L to 71.25 L; flip `correctOption` accordingly on key reveal.

**Too-easy unit-conversion item: add a downstream scaling factor in the stem.**
- *Diagnostic:* intrinsic solve is just the conversion → EASY; marked MEDIUM.
- *Layer:* STEM.
- *Edit:* require the candidate to apply the converted value within a second operation. "Convert ₹/tonne to ₹/kg" becomes "convert ₹/tonne to ₹/kg, then apply a 15% bulk-order discount".

**Too-hard item (intrinsic solve is too complex for marked band): pre-compute one step in the stem.**
- *Diagnostic:* intrinsic-solve scoring returns 3+ steps → HARD; marked MEDIUM.
- *Layer:* STEM.
- *Edit:* state the result of step 1 in the stem so the candidate only has to execute steps 2 and 3. E.g., "Convert the 480 km route into hours at 60 km/h" becomes "The route takes 8 hours at 60 km/h. What is …".

**Low-discrimination item (proxy_a ≤ 2), difficulty itself aligned: rewrite throwaway distractors as named-misconception traps.**
- *Diagnostic:* difficulty band matches intrinsic solve; one or more distractors are throwaways nobody would pick; proxy_a ≤ 2.
- *Layer:* DISTRACTORS (a-parameter).
- *Edit:* identify each throwaway and replace with a plausible wrong answer tied to a *named* misconception MQC would actually make. Spell the misconception out in `why`.
- *Worked example:* "Net profit/loss on the trade" with correct `+₹240`. Distractors include obvious throwaway. Replace with `−₹240` (sign-flip trap), `+₹60` (forgot to multiply by quantity), `+₹2,400` (off-by-10 unit slip). Difficulty unchanged, discrimination lifted from 2 to 4.

**Low-discrimination speed/rate item: add the arithmetic-mean trap as a distractor.**
- *Diagnostic:* item involves harmonic mean (average speed for round-trip at speeds A and B), distractor set contains no `(A+B)/2` option, proxy_a low.
- *Layer:* DISTRACTORS.
- *Edit:* compute `(A+B)/2` and include it as a distractor. Doesn't change intrinsic difficulty (the solve is still "apply harmonic mean"), but it catches candidates who reach for the naive average — lifting proxy_a from 2 to 4.

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

Item: "Identify the grammatically incorrect sentence." Four options testing subject-verb agreement, collective nouns, and "along with" constructions. Correct option violates SVA — but with an intervening prepositional phrase that obscures the violation.

- **Intrinsic solve complexity (Stage 1)**: For verbal "spot the error" items, the conceptual load lives in the OPTION the candidate must analyse (the "stem" of the per-option judgement is the option text itself). The error in option2 — "The list of pending tasks were reviewed" — requires two concepts: (1) identify the head noun behind the prepositional phrase, (2) apply SVA. Two concepts → MEDIUM intrinsic complexity.
- **Marked**: EASY.
- **Diagnosis**: intrinsic complexity is MEDIUM but marked EASY → too-hard mismatch. The cognitive layer that needs simplifying is INSIDE the offending option, not the stem itself (since verbal-error items work this way).
- **A-proxy**: 3 — two distinct misconceptions tested across the distractor set.
- **C-proxy**: 1 — three functioning distractors.
- **Edit (operates on the cognitive complexity of the option text — the verbal-item analogue of a stem rewrite):**
  - Rewrite the offending option to remove one conceptual layer: "The list of pending tasks were reviewed" → "The list were reviewed". The SVA error is now a one-concept solve (no intervening phrase to navigate).
  - Expected post-edit intrinsic complexity = 1 concept → EASY-band alignment. Sanity-check Angoff ≈ 85%.
- **What this is NOT**: a distractor swap. The option text being edited is structurally part of the construct under test, not a discrimination layer.

### Example 2 — HARD-tagged quant item with weak distractors

Item: A 3-step probability problem. Distractors include one off-by-one, one with reversed sign, and one obvious throwaway (10× the right answer).

- **B-proxy / Modified Angoff**: 35% → maps to HARD band → ALIGNED with marked HARD.
- **A-proxy**: 2 — the throwaway makes near-passers' false confidence high; only two misconception traps actually function.
- **C-proxy**: 2 — effective guess floor is ~33%, not 25%. With Angoff at 35%, the item is barely above the guess floor → low information.
- **Verdict**: difficulty ALIGNED, but a-proxy + c-proxy combine to make this a P1 item-information failure. Edit the throwaway distractor into a third real distractor (e.g., a candidate who forgets the conditional). Marked HARD tag is preserved; the edit improves discrimination without moving the item's difficulty band. Expected post-edit a-proxy = 4, c-proxy = 1.

### Example 3 — Construct mismatch (cannot be aligned to marked tags)

Item: A multi-step arithmetic word problem, marked `subject = Verbal Ability`, `topics = Grammar and Sentence Correction`, `difficulty = EASY`.

- **B-proxy / Modified Angoff**: 40% → HARD band.
- **Subject/topic check**: item tests arithmetic, NOT grammar. Construct misalignment.
- **Verdict**: cannot be fixed by editing content/options — the item would have to be rewritten as a completely different grammar question to match the marked subject/topic. This is OUT OF SCOPE for QC.
- **Output**: `confidence: LOW`, `correctness_issue: "Construct mismatch — item tests arithmetic but marked as Verbal Ability/Grammar. Cannot align via content edits; needs a from-scratch rewrite by the author."`, `edits: []`. The xlsx writer leaves the Corrected row showing the original content (un-fixable rows are surfaced via the red row fill).

## Reporting Fields (changes from the cognitive-load rubric)

Replace the old `difficulty_axes: {C1..C5, total}` with:

```yaml
irt_proxies:
  angoff_pct: <0-100>            # Modified Angoff estimate for MQC
  proxy_b: <float, signed>       # derived from Angoff via the mapping table
  proxy_a: 1-5                   # discrimination proxy
  proxy_c: 1-5                   # effective guess-floor proxy
  mqc_definition: |
    <one-line statement of the MQC for this assessment / row>
```

Plus the existing verdict fields (`correctness`, `difficulty_check`, `severity`, `confidence`, `proposed_edits`, `qc_notes`).
