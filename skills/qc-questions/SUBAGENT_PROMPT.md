# Canonical Subagent Prompt — Blind QC Worker

This is the prompt the main agent dispatches to each parallel subagent during xlsx-batch QC. It is the ONLY way to ensure blind-solve discipline: a subagent invoked in a fresh context cannot have read the marked `correctOption` for the rows it judges, even if it tried.

## Batching

- One subagent per batch of **5–8 questions**. Smaller batches = more parallelism but more dispatch overhead; 6 is a good default.
- Dispatch **all batches in a single message** (multiple tool calls in parallel) so they run concurrently.
- For an 18-row file: 3 subagents × 6 rows. For 100 rows: 15–20 subagents.
- Cap parallel subagents at ~10 per dispatch to avoid rate-limit thrash; queue further batches if needed.

## Inputs the main agent prepares per batch

Write the batch's questions to a temp JSON file (`/tmp/qc_batch<N>.json`) **without `correctOption`**. The keys live separately in `/tmp/qc_keys.json` which the subagent must not read.

Pass to the subagent:
- The MQC definition (one sentence; same MQC for every batch in a run)
- The batch file path
- The keys file path (only so the subagent can be told not to read it — fail-loud)

## Canonical Prompt (paste into Agent tool's `prompt` field)

```
You are doing high-stakes QC of assessment MCQs. You are one of several
parallel workers; you judge the rows in your batch only.

MQC (minimally-qualified candidate): <ONE-SENTENCE MQC DEFINITION>

Your job: Read <BATCH_FILE_PATH>. Each entry has row, content,
option1..option6, subject, topics, marked difficulty, and other metadata.
You do NOT have access to correctOption for any row.

HARD RULE: do not, under any circumstance, read <KEYS_FILE_PATH>. Do a
genuinely BLIND solve.

For each question, return:
- row: <int>
- my_answer: option<N>
- my_reasoning: 2 sentences. Name the rule/concept tested + why each
  non-chosen option is wrong (one phrase each).
- multiple_correct_risk: yes|no — is a second option also defensibly
  correct?
- ambiguity_risk: yes|no — stem ambiguous, trick, or missing context?
- angoff_pct: <int 0-100> — of 100 MQCs as defined above, how many would
  get this correct?
- angoff_reasoning: 1 sentence on which misconception trips MQCs and
  ~what % is tripped.
- proxy_a: 1-5 (discrimination — 1=surface heuristics; 3=two distinct
  misconceptions tested; 5=graded distractor ladder).
- proxy_c: 1-5 (effective guess floor — 1=3 functioning distractors;
  3=only 1 functioning; 5=broken).
- confidence: HIGH|MED|LOW.

Output: a single JSON array. Pure JSON, no markdown, no prose, parseable.

Reference Angoff-band mapping (do not output): EASY=75–95%,
MEDIUM=50–75%, HARD=25–50%.

Honesty discipline:
- Unsure between two options → confidence: LOW AND multiple_correct_risk: yes.
- MQC would get >95% → floor item; flag implicitly via high angoff_pct.
- MQC would get <25% → likely you got it wrong OR the item is at the
  guess floor; flag via confidence: LOW.
- For quantitative items: solve by two independent methods. If they
  disagree, confidence: LOW.

Constraint on the spec:
- The marked `subject`, `topics`, and `difficulty` are FIXED targets, not
  things you propose changes to. Your job is to inform the main agent
  where this item drifts from those targets (via angoff_pct, proxy_a,
  proxy_c, multiple_correct_risk, ambiguity_risk). The main agent will
  prescribe `content` / `option1..option6` / `correctOption` edits to
  pull the item back to the marked spec. You do not propose edits.
- If the item's construct fundamentally mismatches the marked subject
  or topics (e.g., it's an arithmetic problem tagged Verbal Ability),
  add a field `construct_mismatch: "<one-line description>"` to your
  output for that row and set confidence: LOW. The main agent will
  surface this as an escalation rather than retagging.

Return under 1000 words.
```

## What the Main Agent Does After Subagents Return

1. Collect all subagent JSON outputs into a single list (key = row).
2. Read `/tmp/qc_keys.json` (now and only now — the main agent's context did see `correctOption` during xlsx parsing, but the parse script kept it in a separate block).
3. For each row, compute:
   - **correctness:** compare `my_answer` to marked key.
     - match + no `multiple_correct_risk` + no `ambiguity_risk` → no correctness_issue
     - match BUT `multiple_correct_risk: yes` → correctness_issue = "Two defensibly-correct options" + edit one distractor
     - mismatch + HIGH confidence → correctness_issue = "Marked X but Y is the only defensible answer" + flip `correctOption`
     - mismatch + LOW confidence → escalate (confidence: LOW in output, mark for human review)
     - `ambiguity_risk: yes` → correctness_issue = "Stem is ambiguous: …" + edit stem
   - **difficulty:** map `angoff_pct` to band (EASY 75–95, MEDIUM 50–75, HARD 25–50). Compare to marked.
     - same band → no difficulty_issue
     - different band → difficulty_issue = "Marked X but Angoff … → Y band" + emit ONE edit path (retag is usually the smaller change; rewrite if user has explicitly said tag is fixed).
   - **status:** ALIGNED iff both issues null; otherwise NEEDS_EDITS.
   - **edits:** concrete, paste-able edits with `from` / `to` / `why`.
   - **confidence:** lowest of subagent confidence and main-agent compose confidence.
4. Write `verdicts.json` (list of lean verdict objects).
5. Run `python3 scripts/qc_xlsx.py write <input.xlsx> verdicts.json <output.xlsx>`.

## Why This Structure Matters

- **Blind-solve is structurally enforced.** A subagent in a fresh context literally cannot have seen the row's `correctOption` — its only inputs are the batch JSON (key-stripped) and the prompt. This eliminates the dominant LLM failure mode on QC: rationalising the marked answer.
- **Parallelism reduces wall-clock time ~Nx** with N subagents.
- **IRT reasoning stays internal to the subagent.** The lean verdict the main agent composes never surfaces Angoff numbers — those served their purpose at decision time.
- **Quant/logic gets two-method self-consistency for free** because the prompt mandates it; failures surface as `confidence: LOW` which the main agent treats as P0.
