#!/usr/bin/env python3
"""
qc_xlsx.py — xlsx I/O for the qc-questions skill.

Two subcommands:

  read  <input.xlsx>
        Parses the xlsx, validates mandatory headers, strips HTML from
        content/option fields, and prints normalised JSON (one row per
        question) to stdout. The JSON for each question OMITS correctOption
        — that field is held back so a subagent can do a blind solve.
        The "answer key" is printed separately under "_keys" at the end
        for the main agent to consume after the subagent commits.

  write <input.xlsx> <verdicts.json> <output.xlsx>
        Reads the original xlsx and a verdicts.json (a list of verdict
        objects keyed by row), and writes <output.xlsx> with the original
        sheet preserved plus appended qc_* columns.

Verdict object expected shape (lean, edit-centric — see REPORT_TEMPLATE.md):
{
  "row": <int>,
  "status": "ALIGNED" | "NEEDS_EDITS",
  "correctness_issue": "<one-line or null>",
  "difficulty_issue":  "<one-line or null>",
  "edits": [
    { "field": "<stem|option1..option6|correctOption|difficulty>",
      "from": "<exact current value>",
      "to":   "<exact replacement>",
      "why":  "<one-line>" }
  ],
  "confidence": "HIGH" | "MED" | "LOW"
}

The mandatory headers in the input xlsx (per skill spec) are:
  content, option1..option6, correctOption, questionType, subject, topics, difficulty
option5/option6 may be blank. Other columns are preserved untouched.

Dependencies: openpyxl (already used elsewhere in the user's environment).
HTML stripping uses only stdlib (html.parser).
"""

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

# Color codes (Excel's standard Good/Neutral/Bad palette + accent)
GREEN_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")        # ALIGNED — no change
AMBER_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")        # NEEDS_EDITS — apply edits
DARK_AMBER_FILL = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid")   # changed cell accent
RED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")          # LOW confidence / escalate
BOLD_FONT = Font(bold=True)


MANDATORY_HEADERS = [
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

ORIGINAL_QC_COLUMN = "qc_status"  # Only column appended to the original sheet
CORRECTED_SHEET_NAME = "Corrected"  # New sheet containing post-edit rows
LEGEND_SHEET_NAME = "QC Legend"     # Small sheet documenting the color code

# Fields the LLM may target in `edits`. Edits to other fields are ignored
# (and IMMUTABLE_FIELDS specifically generate a warning to stderr).
EDITABLE_FIELDS = {
    "content",
    "stem",  # alias accepted; mapped to "content"
    "option1",
    "option2",
    "option3",
    "option4",
    "option5",
    "option6",
    "correctOption",
}

# These define what the question is supposed to BE — the PM-planned spec.
# The QC must edit `content`/`option*`/`correctOption` to align the item to
# these tags, never the other way around. Attempts to edit these are dropped
# and surfaced as a warning.
IMMUTABLE_FIELDS = {
    "subject",
    "topics",
    "difficulty",
}

# Cells that the bulk-upload platform expects to be HTML. Plain-text edits
# get wrapped in <p>…</p> so the corrected sheet is upload-ready.
HTML_WRAP_FIELDS = {
    "content",
    "option1",
    "option2",
    "option3",
    "option4",
    "option5",
    "option6",
}


def _normalize_field(field):
    return "content" if field == "stem" else field


def _write_legend_sheet(wb):
    """Create (or replace) the QC Legend sheet documenting the colour code."""
    if LEGEND_SHEET_NAME in wb.sheetnames:
        del wb[LEGEND_SHEET_NAME]
    ls = wb.create_sheet(LEGEND_SHEET_NAME)

    rows = [
        ("Colour", "Where it appears",                                 "Meaning"),
        ("GREEN",      "qc_status cell (Original) · whole row (Corrected)",
                       "ALIGNED — correctness and difficulty both match the marked values. No edit needed."),
        ("AMBER",      "qc_status cell (Original) · whole row (Corrected)",
                       "NEEDS_EDITS — apply the edits shown in the Corrected sheet."),
        ("DARK AMBER", "individual cell in a NEEDS_EDITS row (Corrected)",
                       "This specific cell was edited. Compare with the same cell in the Original sheet to see the change."),
        ("RED",        "qc_status cell (Original) · whole row (Corrected)",
                       "NEEDS_EDITS with LOW confidence. Escalate to a human reviewer before applying."),
    ]

    fills_for_row = {
        1: None,
        2: GREEN_FILL,
        3: AMBER_FILL,
        4: DARK_AMBER_FILL,
        5: RED_FILL,
    }

    for r, row_vals in enumerate(rows, start=1):
        for c, val in enumerate(row_vals, start=1):
            cell = ls.cell(row=r, column=c, value=val)
            if r == 1:
                cell.font = BOLD_FONT
            else:
                # Colour-block the first column so the swatch is unambiguous.
                if c == 1:
                    cell.fill = fills_for_row[r]
                    cell.font = BOLD_FONT

    # Column widths for readability when the user opens the workbook.
    ls.column_dimensions["A"].width = 14
    ls.column_dimensions["B"].width = 48
    ls.column_dimensions["C"].width = 90

    # Trailing note row
    note_row = len(rows) + 2
    note = ls.cell(
        row=note_row,
        column=1,
        value=(
            "How to use: scan the qc_status column on the original sheet. For each amber or red row, "
            "open the same row number on the 'Corrected' sheet — the cells highlighted in dark amber "
            "are the ones that changed; non-edited cells in that row are shown for context."
        ),
    )
    note.font = Font(italic=True)
    ls.merge_cells(start_row=note_row, start_column=1, end_row=note_row, end_column=3)


def _maybe_html_wrap(field, value):
    if value is None:
        return value
    if field not in HTML_WRAP_FIELDS:
        return value
    s = str(value).strip()
    if s.startswith("<"):
        return s
    return f"<p>{s}</p>"


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._in_block = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br", "li", "tr", "div"):
            self._parts.append("\n")
        elif tag in ("sup",):
            self._parts.append("^")
        elif tag in ("sub",):
            self._parts.append("_")

    def handle_endtag(self, tag):
        if tag in ("p", "li", "tr", "div"):
            self._parts.append("\n")

    def handle_data(self, data):
        self._parts.append(data)

    def text(self) -> str:
        joined = "".join(self._parts)
        # Collapse excessive whitespace but preserve line breaks loosely.
        lines = [ln.strip() for ln in joined.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines).strip()


def strip_html(value) -> str:
    if value is None:
        return ""
    s = str(value)
    if "<" not in s and "&" not in s:
        return s.strip()
    parser = _HTMLStripper()
    try:
        parser.feed(s)
        parser.close()
    except Exception:
        return s.strip()
    return parser.text()


def _read_workbook(path: Path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    raw_headers = [c.value for c in ws[1]]
    headers = [h for h in raw_headers if h is not None]
    return wb, ws, raw_headers, headers


def _validate_headers(headers):
    missing = [h for h in MANDATORY_HEADERS if h not in headers]
    if missing:
        sys.stderr.write(
            "ERROR: input xlsx is missing mandatory headers: "
            + ", ".join(missing)
            + "\n"
            + "Mandatory headers: "
            + ", ".join(MANDATORY_HEADERS)
            + "\n"
        )
        sys.exit(2)


def cmd_read(args):
    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        sys.stderr.write(f"ERROR: input file not found: {in_path}\n")
        sys.exit(2)

    _wb, ws, raw_headers, headers = _read_workbook(in_path)
    _validate_headers(headers)

    questions = []
    keys = []
    for excel_row, row in enumerate(
        ws.iter_rows(min_row=2, values_only=True), start=2
    ):
        record = dict(zip(raw_headers, row, strict=False))
        # skip blank rows
        if not any(v not in (None, "") for v in record.values()):
            continue

        stripped = {
            "row": excel_row,
            "content": strip_html(record.get("content")),
            "option1": strip_html(record.get("option1")),
            "option2": strip_html(record.get("option2")),
            "option3": strip_html(record.get("option3")),
            "option4": strip_html(record.get("option4")),
            "option5": strip_html(record.get("option5")),
            "option6": strip_html(record.get("option6")),
            "questionType": record.get("questionType"),
            "subject": record.get("subject"),
            "topics": record.get("topics"),
            "difficulty": record.get("difficulty"),
        }
        # carry through optional metadata for context (read-only)
        for h in headers:
            if h not in MANDATORY_HEADERS and h not in stripped:
                stripped[h] = record.get(h)

        # critical: hold back correctOption from the question payload
        keys.append({"row": excel_row, "correctOption": record.get("correctOption")})
        questions.append(stripped)

    out = {"questions": questions, "_keys": keys, "source": str(in_path)}
    json.dump(out, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def cmd_write(args):
    in_path = Path(args.input).expanduser().resolve()
    verdicts_path = Path(args.verdicts).expanduser().resolve()
    out_path = Path(args.output).expanduser().resolve()

    if not in_path.exists():
        sys.stderr.write(f"ERROR: input file not found: {in_path}\n")
        sys.exit(2)
    if not verdicts_path.exists():
        sys.stderr.write(f"ERROR: verdicts file not found: {verdicts_path}\n")
        sys.exit(2)

    with verdicts_path.open() as f:
        verdicts_doc = json.load(f)
    verdicts_list = (
        verdicts_doc if isinstance(verdicts_doc, list) else verdicts_doc.get("verdicts", [])
    )
    by_row = {v["row"]: v for v in verdicts_list}

    wb, ws, raw_headers, headers = _read_workbook(in_path)
    _validate_headers(headers)

    # ---- 1. ORIGINAL sheet: append qc_status to the NEXT TRULY EMPTY column.
    # Scan the entire sheet (not just the header row) so we never overwrite
    # data that happens to live past the last named header.
    refreshed_headers = [c.value for c in ws[1]]
    if ORIGINAL_QC_COLUMN in refreshed_headers:
        qc_status_col = refreshed_headers.index(ORIGINAL_QC_COLUMN) + 1
    else:
        max_col_with_data = 0
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is not None and cell.column > max_col_with_data:
                    max_col_with_data = cell.column
        qc_status_col = max_col_with_data + 1
        header_cell = ws.cell(row=1, column=qc_status_col, value=ORIGINAL_QC_COLUMN)
        header_cell.font = BOLD_FONT

    for excel_row in range(2, ws.max_row + 1):
        v = by_row.get(excel_row)
        if v is None:
            continue
        status = v.get("status")
        cell = ws.cell(row=excel_row, column=qc_status_col, value=status)
        if status == "ALIGNED":
            cell.fill = GREEN_FILL
        elif status == "NEEDS_EDITS":
            cell.fill = RED_FILL if v.get("confidence") == "LOW" else AMBER_FILL

    # ---- 2. CORRECTED sheet: rebuild from scratch.
    if CORRECTED_SHEET_NAME in wb.sheetnames:
        del wb[CORRECTED_SHEET_NAME]
    cs = wb.create_sheet(CORRECTED_SHEET_NAME)

    named_headers = [h for h in raw_headers if h is not None and h != ORIGINAL_QC_COLUMN]
    for i, h in enumerate(named_headers, start=1):
        hcell = cs.cell(row=1, column=i, value=h)
        hcell.font = BOLD_FONT

    # 3. Per row:
    #    - ALIGNED      → copy the original row content verbatim, fill GREEN.
    #                     The Corrected sheet is the production-ready post-QC
    #                     output, so a user can drop the fills and re-upload it
    #                     as-is.
    #    - NEEDS_EDITS  → write the post-edit content, fill row AMBER (or RED
    #                     if LOW confidence). Cells that were actually edited
    #                     get DARK_AMBER + bold font so the diff pops.
    for excel_row in range(2, ws.max_row + 1):
        v = by_row.get(excel_row)

        # Start from the original row content for every status.
        record = {}
        for i, h in enumerate(raw_headers, start=1):
            if h is None or h == ORIGINAL_QC_COLUMN:
                continue
            record[h] = ws.cell(row=excel_row, column=i).value

        if v is None or v.get("status") == "ALIGNED":
            for i, h in enumerate(named_headers, start=1):
                cell = cs.cell(row=excel_row, column=i, value=record.get(h))
                cell.fill = GREEN_FILL
            continue

        allow_retag = bool(getattr(args, "allow_retag", False))
        changed_fields = set()
        for edit in v.get("edits") or []:
            field = _normalize_field(edit.get("field"))
            if field in IMMUTABLE_FIELDS:
                if not allow_retag:
                    sys.stderr.write(
                        f"  ! row {excel_row}: dropped edit targeting immutable field "
                        f"'{field}' (subject/topics/difficulty are the spec, not editable). "
                        f"Edit any of content/option1..option6/correctOption to align to "
                        f"the marked spec instead, or pass --allow-retag if you really "
                        f"intend to change tags (legacy-cleanup workflows only).\n"
                    )
                    continue
                if field not in record:
                    continue
                record[field] = edit.get("to")
                changed_fields.add(field)
                continue
            if field not in EDITABLE_FIELDS or field not in record:
                continue
            record[field] = _maybe_html_wrap(field, edit.get("to"))
            changed_fields.add(field)

        row_fill = RED_FILL if v.get("confidence") == "LOW" else AMBER_FILL

        for i, h in enumerate(named_headers, start=1):
            cell = cs.cell(row=excel_row, column=i, value=record.get(h))
            if h in changed_fields:
                cell.fill = DARK_AMBER_FILL
                cell.font = BOLD_FONT
            else:
                cell.fill = row_fill

    # ---- 4. LEGEND sheet documenting the colour code.
    _write_legend_sheet(wb)

    # Reorder so the user opens to: Original → QC Legend → Corrected.
    sheet_order = []
    for name in wb.sheetnames:
        if name not in (LEGEND_SHEET_NAME, CORRECTED_SHEET_NAME):
            sheet_order.append(name)
    sheet_order.append(LEGEND_SHEET_NAME)
    sheet_order.append(CORRECTED_SHEET_NAME)
    wb._sheets = [wb[name] for name in sheet_order]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    sys.stderr.write(
        f"Wrote {out_path}\n"
        f"  - Original '{ws.title}': qc_status appended at column {qc_status_col}\n"
        f"  - '{LEGEND_SHEET_NAME}' sheet: colour-code legend\n"
        f"  - '{CORRECTED_SHEET_NAME}' sheet: ALIGNED rows populated verbatim+green "
        f"(upload-ready), NEEDS_EDITS rows show post-edit content (amber row, "
        f"dark-amber+bold on changed cells; red row if confidence=LOW)\n"
    )


def main():
    p = argparse.ArgumentParser(description="QC xlsx I/O for the qc-questions skill")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("read", help="Parse xlsx and print normalised JSON")
    pr.add_argument("input")
    pr.set_defaults(func=cmd_read)

    pw = sub.add_parser("write", help="Write verdicts back into a new xlsx")
    pw.add_argument("input")
    pw.add_argument("verdicts")
    pw.add_argument("output")
    pw.add_argument(
        "--allow-retag",
        action="store_true",
        help=(
            "Allow verdict edits that target subject/topics/difficulty. "
            "OFF by default — the marked tags are the spec the question must match, "
            "and silently retagging would change bank composition. Enable only for "
            "legacy cleanup workflows where the tags themselves are known-bad."
        ),
    )
    pw.set_defaults(func=cmd_write)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
