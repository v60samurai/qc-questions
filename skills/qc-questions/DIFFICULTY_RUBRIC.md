# IRT-Aligned Difficulty Rubric (Pre-Calibration QC)

This rubric judges items the way an IRT-aligned bank judges them: by **b** (difficulty), **a** (discrimination), and **c** (pseudo-guessing). Because pre-deployment items have no response data yet, we use **content-expert proxies** — Modified Angoff for b, distractor-functioning analysis for a, and effective-options counting for c. Once the bank has empirical response data, these proxies are replaced by calibrated parameters; until then, this is the rigorous substitute.

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

### B-proxy — Modified Angoff Estimate

**Procedure (single-judge variant):**

1. Hold the construct of the **minimally-qualified candidate (MQC)** in mind. MQC is the candidate sitting exactly at the assessment's cut score for the role/subject. State your MQC definition explicitly in `qc_notes` for transparency.
2. Imagine 100 such MQCs attempting the item independently.
3. Estimate the count answering correctly. That % is your **Angoff_pct**.
4. Map Angoff_pct to a band via the table above.

**Estimation aids (use whichever helps for the item type):**

- For verbal/grammar items: how confident would a candidate at MQC level be in the named rule? Did they likely encounter it in school but not master edge cases (→ ~65%) vs. a high-school staple (→ ~85%)?
- For quant items: how many steps must MQC chain without slip? Each independent step ≈ 0.85 chance for MQC → multiply.
- For domain knowledge: is the fact part of the canonical curriculum for MQC's role (→ 70–90%) or a niche extension (→ 30–50%)?
- For applied/scenario items: how readable is the scenario? Reading load that exceeds MQC literacy hurts Angoff even when content is "easy".

**Hard rule:** if your point estimate falls in a band's window, declare the band aligned. If it falls outside, declare `TOO_EASY` (Angoff above the marked band's range) or `TOO_HARD` (Angoff below it). State the Angoff_pct and your derivation in `qc_notes`.

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

**Foundational rule for this section:** The marked `subject`, `topics`, and `difficulty` are the SPEC. Every prescription below adjusts `content` / `option1..option6` / `correctOption` to move the item INTO the marked band. **Never retag.** If the item cannot reasonably be brought into the marked band without changing what subject/topic it tests, that is a construct mismatch — flag `confidence: LOW` and recommend escalation, do not change the tags.

### To raise difficulty (Angoff_pct too high for marked band)

| Goal | Edit prescription | Targets |
|---|---|---|
| Lower Angoff for MQC by ~10 pts | Replace the most obvious distractor with one that targets a textbook misconception MQC commonly holds. | a-proxy ↑, b ↑ |
| Lower Angoff for MQC by ~15 pts | Add a sequential reasoning step in the stem (e.g., "given X, then computing Y, what is Z?") — only if construct still aligns. | b ↑ |
| Lower Angoff for MQC by ~5 pts | Tighten distractor language so superficial elimination fails (equalise lengths, parallel grammar). | a-proxy ↑ |
| Lift the discrimination ceiling | Replace a "throwaway" distractor with one that catches a near-passing candidate's specific blind spot. | a-proxy ↑ |

### To lower difficulty (Angoff_pct too low for marked band)

| Goal | Edit prescription | Targets |
|---|---|---|
| Raise Angoff for MQC by ~10 pts | Pre-compute one intermediate step in the stem. | b ↓ |
| Raise Angoff for MQC by ~10 pts | Replace technical vocabulary with plain-language equivalent (if the construct allows). | b ↓ |
| Raise Angoff for MQC by ~5 pts | Soften one near-miss distractor → reduces near-passer false-negatives. | b ↓ (do NOT use if a-proxy is already low) |

### To fix discrimination (a-proxy ≤ 2)

| Symptom | Edit |
|---|---|
| All distractors target same misconception | Rewrite 1–2 distractors to test *different* misconceptions a lower-ability candidate would hold. Spell out which misconception each distractor catches in `qc_notes`. |
| Correct answer detectable by length | Pad shorter options or trim the correct one to equalise lengths. |
| Construct-irrelevant variance (reading load) | Simplify stem language without changing the construct (shorter sentences, common vocabulary, remove subordinate clauses). |
| Stem-option keyword leakage | Reword the correct option so it doesn't echo stem keywords more than distractors do. |

### To fix guessing-floor (c-proxy ≥ 3)

| Symptom | Edit |
|---|---|
| Two or more obvious throwaways | Rewrite each as a *plausible* wrong answer mapped to a real misconception. |
| Negation-only distractor | Replace with a substantive alternative (negations are usually weak distractors). |
| Distractors share a structural giveaway | Restructure so each option has similar surface form (units, length, grammar). |

### To fix `WRONG_KEY` / `MULTIPLE_CORRECT` / `NO_CORRECT` / `AMBIGUOUS`

(Same as before — see prior version: switch `correctOption`, tighten stem qualifier, add precision constraint, etc.)

### Worked-example prescriptions (auto-prescribed by the subagent)

The autonomous-by-default rule (SKILL.md rule 5) requires the subagent to write a concrete edit for every NEEDS_EDITS row at HIGH or MED confidence. Pattern library below — each line gives an item shape, the diagnostic, and a paste-able edit shape. Use these as templates when the matching pattern fires.

**Too-hard item (Angoff below the marked band): soften the weakest distractor by 1 step.**
- *Diagnostic:* `angoff_pct` below the marked band's window; one distractor is doing the heavy lifting and tripping near-passers.
- *Edit:* identify the distractor with the highest near-miss density (typically the most plausible wrong answer for MQC), and step its difficulty down by one — e.g., replace a multi-step trap with a single-step trap, or replace a numerical trap that requires an extra computation with one that doesn't.
- *Example:* HARD-tagged speed/distance item, Angoff 22%. Distractor "55" requires both `total = 240`, `time = 4` AND remembering to divide. Soften to "240" so the trap is "forgot to divide" (one step instead of two) — Angoff lifts to ~30%.

**Too-easy speed/rate item (Angoff above the marked band): add a near-miss distractor that swaps mean-of-means for harmonic mean.**
- *Diagnostic:* `angoff_pct` above marked band's window on an item involving average speed, average rate, or "round-trip at speeds A and B" — and the distractor set contains no option matching the naive arithmetic-mean answer.
- *Edit:* compute the arithmetic mean of the two speeds and use it as a distractor. MQCs who reach for `(A+B)/2` instead of `2AB/(A+B)` will land on it — drops Angoff by ~15 pts and lifts a-proxy.
- *Example:* "A car travels 60 km at 30 km/h and returns at 60 km/h. Average speed?" Correct: 40. If options are `35, 40, 45, 50`, swap one for `45` (= the arithmetic mean of 30 and 60) — Angoff falls from ~80% to ~65%.

**Too-easy arithmetic item (Angoff above marked band): flip sign in one option text.**
- *Diagnostic:* `angoff_pct` above marked band on a signed-arithmetic, profit/loss, or net-change item. Distractors include no "wrong sign" option, so the answer pops out as the only positive (or only negative).
- *Edit:* take the correct numeric answer and emit a sign-flipped twin as a distractor. Captures candidates who get the magnitude right but misread the direction.
- *Example:* "Net profit/loss on the trade." Correct: `+₹240`. Add `−₹240` to the distractor pool, drop the obvious throwaway.

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

### Example 1 — EASY-tagged grammar item

Item: "Identify the grammatically incorrect sentence." Four options testing subject-verb agreement, collective nouns, and "along with" constructions. Correct option violates SVA.

- **B-proxy / Modified Angoff**: MQC = a candidate at the screening cut for an entry-level analyst role. Most have encountered SVA in school but trip on prepositional-phrase-between-subject-and-verb constructions. Estimate 70% MQC correct → Angoff_pct = 70.
- **Maps to**: MEDIUM (50–75% range).
- **Marked**: EASY.
- **Verdict**: `TOO_HARD` for an EASY tag. The marked tag is the spec → the item must be edited to come back into the EASY band (75–95%).
- **A-proxy**: 3 — two distinct misconceptions tested (collective nouns, "along with"); one mostly-throwaway option.
- **C-proxy**: 1 — three functioning distractors.
- **Edits** (only `content` and options are touched; `difficulty` stays EASY):
  - Rewrite the stem of the offending option to remove the prepositional-phrase trap. Example: change "The list of pending tasks were reviewed" to "The list were reviewed" so the SVA error is obvious without the intervening phrase.
  - Expected post-edit Angoff_pct ≈ 85% → EASY-band alignment.

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
