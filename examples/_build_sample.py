"""
Build examples/sample_bank.xlsx and examples/sample_bank__qc.expected.xlsx
for regression testing and onboarding.

The sample bank is 8 questions with deliberately planted errors so QC has
something interesting to find:

  row 2  ALIGNED clean grammar item, EASY band
  row 3  ALIGNED clean register item, EASY band
  row 4  NEEDS_EDITS — wrong key (option3 marked but option2 is the only
         defensibly-correct answer). HIGH confidence.
  row 5  NEEDS_EDITS — band misaligned: MEDIUM-band item tagged EASY.
         Edit one option to drop the trap so Angoff returns to EASY band.
  row 6  ALIGNED clean SVA item, MEDIUM band
  row 7  NEEDS_EDITS — ambiguous: two grammatically valid options.
         Rewrite one to break the tie. HIGH confidence.
  row 8  NEEDS_EDITS — construct mismatch: arithmetic problem tagged
         Verbal Ability. LOW confidence escalation, no auto-edits.
  row 9  ALIGNED clean reading comprehension item, MEDIUM band
"""
from __future__ import annotations

import json
from pathlib import Path

import openpyxl


HERE = Path(__file__).resolve().parent
SAMPLE_XLSX = HERE / "sample_bank.xlsx"
EXPECTED_XLSX = HERE / "sample_bank__qc.expected.xlsx"
EXPECTED_VERDICTS = HERE / "sample_bank.expected_verdicts.json"


HEADERS = [
    "content",
    "option1",
    "option2",
    "option3",
    "option4",
    "option5",
    "option6",
    "correctOption",
    "questionType",
    "subject",
    "topics",
    "difficulty",
]


def _p(text: str) -> str:
    return f"<p>{text}</p>"


ROWS = [
    # row 2 — ALIGNED, EASY, grammar
    {
        "content": _p("Identify the grammatically correct sentence."),
        "option1": _p("She don't likes coffee in the morning."),
        "option2": _p("She doesn't like coffee in the morning."),
        "option3": _p("She doesn't likes coffee in the morning."),
        "option4": _p("She don't like coffee in the morning."),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Grammar and Sentence Correction",
        "difficulty": "EASY",
    },
    # row 3 — ALIGNED, EASY, register
    {
        "content": _p("Which is the most appropriate opening for a first-time business email to a senior client?"),
        "option1": _p("Yo!"),
        "option2": _p("Dear Mr. Sharma,"),
        "option3": _p("Hey Sharma,"),
        "option4": _p("Sup boss,"),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Business Communication",
        "difficulty": "EASY",
    },
    # row 4 — NEEDS_EDITS, wrong key (option3 marked but option2 is correct)
    {
        "content": _p("Choose the option with correct subject-verb agreement."),
        "option1": _p("The committee are deciding the budget next week."),
        "option2": _p("The committee is deciding the budget next week."),
        "option3": _p("The committee were decided the budget next week."),
        "option4": _p("The committee was deciding the budget next week tomorrow."),
        "option5": None,
        "option6": None,
        "correctOption": "option3",  # wrong: option2 is the only correct one
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Grammar and Sentence Correction",
        "difficulty": "MEDIUM",
    },
    # row 5 — NEEDS_EDITS, band misaligned (tagged EASY, actually MEDIUM)
    {
        "content": _p("Identify the grammatically incorrect sentence."),
        "option1": _p("The team has finished its work on schedule."),
        "option2": _p("The list of pending tasks were reviewed during the morning call."),
        "option3": _p("Each participant needs to complete the registration on time."),
        "option4": _p("The manager, along with two analysts, is attending the workshop."),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Grammar and Sentence Correction",
        "difficulty": "EASY",  # actually MEDIUM — prepositional-phrase trap
    },
    # row 6 — ALIGNED, MEDIUM, SVA with trickier construction
    {
        "content": _p("Identify the grammatically incorrect sentence."),
        "option1": _p("Neither the manager nor the analysts have submitted the report."),
        "option2": _p("Neither the analysts nor the manager has submitted the report."),
        "option3": _p("Neither the manager nor the analyst has submitted the report."),
        "option4": _p("Neither the analysts nor the manager have submitted the report."),
        "option5": None,
        "option6": None,
        "correctOption": "option4",  # nearer-noun rule violated
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Grammar and Sentence Correction",
        "difficulty": "MEDIUM",
    },
    # row 7 — NEEDS_EDITS, ambiguous (two valid answers)
    {
        "content": _p("Which sentence is grammatically correct?"),
        "option1": _p("She have completed her work yesterday."),
        "option2": _p("She completed her work yesterday."),
        "option3": _p("She has completed her work yesterday."),  # also defensible in casual register
        "option4": _p("She is completed her work yesterday."),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Grammar and Sentence Correction",
        "difficulty": "EASY",
    },
    # row 8 — NEEDS_EDITS, construct mismatch (arithmetic tagged Verbal Ability)
    {
        "content": _p("If a train covers 240 km in 4 hours, what is its average speed in km/h?"),
        "option1": _p("40"),
        "option2": _p("60"),
        "option3": _p("80"),
        "option4": _p("100"),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",  # mismatch — this is arithmetic
        "topics": "Grammar and Sentence Correction",
        "difficulty": "EASY",
    },
    # row 9 — ALIGNED, MEDIUM, reading comprehension
    {
        "content": _p(
            "Passage: A small team of researchers introduced a new metric for measuring "
            "code quality that combined cyclomatic complexity with test coverage. Adoption "
            "in industry was limited because most teams already used coverage alone and "
            "found the new metric harder to explain to leadership."
            "<br><br>What is the most likely reason adoption was limited?"
        ),
        "option1": _p("The new metric was less accurate than existing measures."),
        "option2": _p("The new metric added explanatory cost without a clearly perceived gain."),
        "option3": _p("The researchers refused to share the formula publicly."),
        "option4": _p("Coverage alone is already a perfect quality measure."),
        "option5": None,
        "option6": None,
        "correctOption": "option2",
        "questionType": "MULTIPLE_CHOICE_QUESTION",
        "subject": "Verbal Ability",
        "topics": "Reading Comprehension",
        "difficulty": "MEDIUM",
    },
]


# Expected verdicts the QC pass should emit on this bank.
# Used to seed the expected output workbook and as ground truth in tests.
EXPECTED_VERDICTS_LIST = [
    {
        "row": 2,
        "status": "ALIGNED",
        "correctness_issue": None,
        "difficulty_issue": None,
        "edits": [],
        "confidence": "HIGH",
    },
    {
        "row": 3,
        "status": "ALIGNED",
        "correctness_issue": None,
        "difficulty_issue": None,
        "edits": [],
        "confidence": "HIGH",
    },
    {
        "row": 4,
        "status": "NEEDS_EDITS",
        "correctness_issue": (
            "Marked option3 but option3 has two grammatical errors ('were decided'). "
            "Only option2 is the defensibly-correct SVA construction."
        ),
        "difficulty_issue": None,
        "edits": [
            {
                "field": "correctOption",
                "from": "option3",
                "to": "option2",
                "why": "fixes correctness",
            }
        ],
        "confidence": "HIGH",
    },
    {
        "row": 5,
        "status": "NEEDS_EDITS",
        "correctness_issue": None,
        "difficulty_issue": (
            "Marked EASY but the prepositional-phrase-between-subject-and-verb trap "
            "trips ~30% of MQCs (Angoff ~70%, MEDIUM-band behaviour). Simplify the "
            "stem of option2 to drop the trap and return to EASY-band Angoff."
        ),
        "edits": [
            {
                "field": "option2",
                "from": _p(
                    "The list of pending tasks were reviewed during the morning call."
                ),
                "to": "The list were reviewed during the morning call.",
                "why": (
                    "removes the intervening prepositional phrase so the SVA error is "
                    "obvious; Angoff returns to ~85% EASY band"
                ),
            }
        ],
        "confidence": "HIGH",
    },
    {
        "row": 6,
        "status": "ALIGNED",
        "correctness_issue": None,
        "difficulty_issue": None,
        "edits": [],
        "confidence": "HIGH",
    },
    {
        "row": 7,
        "status": "NEEDS_EDITS",
        "correctness_issue": (
            "Two defensibly-correct options: option2 (simple past) and option3 (present "
            "perfect, which native speakers accept with 'yesterday' in casual register). "
            "Rewrite option3 to break the tie."
        ),
        "difficulty_issue": None,
        "edits": [
            {
                "field": "option3",
                "from": _p("She has completed her work yesterday."),
                "to": "She has completed her work today.",
                "why": (
                    "switches the time adverb so present-perfect aligns with the verb "
                    "form; option2 remains the only correct answer for the marked stem"
                ),
            }
        ],
        "confidence": "HIGH",
    },
    {
        "row": 8,
        "status": "NEEDS_EDITS",
        "correctness_issue": (
            "Construct mismatch — item tests arithmetic but is tagged subject='Verbal "
            "Ability', topics='Grammar and Sentence Correction'. Cannot align via "
            "content edits without rewriting the entire question as a grammar item. "
            "Escalate to the author."
        ),
        "difficulty_issue": None,
        "edits": [],
        "confidence": "LOW",
    },
    {
        "row": 9,
        "status": "ALIGNED",
        "correctness_issue": None,
        "difficulty_issue": None,
        "edits": [],
        "confidence": "HIGH",
    },
]


def build_input_workbook(path: Path) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(HEADERS)
    for r in ROWS:
        ws.append([r.get(h) for h in HEADERS])
    wb.save(path)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    build_input_workbook(SAMPLE_XLSX)
    EXPECTED_VERDICTS.write_text(json.dumps(EXPECTED_VERDICTS_LIST, indent=2))
    print(f"wrote {SAMPLE_XLSX}")
    print(f"wrote {EXPECTED_VERDICTS}")


if __name__ == "__main__":
    main()
