"""Preview an existing weekly workload XLSX without altering an ERPNext site.

Designed for the supplied 'Weekly Workload' sheet. Return a ready-to-review
mapping; data insertion is deliberately not automatic and must be explicit.
"""

from __future__ import annotations

from academic_workload.utils.calculations import calculate_week

TEACHING_COLUMNS = {
    "lecture_in_faculty": "D", "lecture_outside": "E", "tutorials": "F",
    "labs": "G", "practical": "H", "clinical": "I", "workshop": "J",
    "postgraduate": "K",
}
DUTY_COLUMNS = {
    "planned_office_hours": "N", "actual_office_hours": "O",
    "planned_advising": "P", "actual_advising": "Q",
    "planned_committee_hours": "S", "actual_committee_hours": "T",
    "planned_research": "U", "actual_research": "V",
    "planned_meetings": "W", "actual_meetings": "X",
    "planned_quality": "Y", "actual_quality": "Z",
    "planned_other_activities": "AA", "actual_other_activities": "AB",
}
ACTUAL_COLUMNS = ("M", "O", "Q", "T", "V", "X", "Z", "AB")


def preview_workbook(path, *, target_weekly_hours):
    """Parse the workbook as data, not formulas, and distinguish blank from 0.

    `target_weekly_hours` must be provided explicitly: Excel's Status cell
    hard-codes 40, which must NOT become an institution-wide assumption.
    """
    from openpyxl import load_workbook

    book = load_workbook(path, read_only=True, data_only=False)
    try:
        if "Weekly Workload" not in book.sheetnames:
            raise ValueError("Expected worksheet 'Weekly Workload'")
        sheet = book["Weekly Workload"]
        # Verify a few headings before mapping fixed column letters.
        if "Teaching" not in str(sheet["D6"].value) or "Week" not in str(sheet["A7"].value):
            raise ValueError("Workbook has an unknown header format")
        records = []
        standard_hours = None
        for row_index in range(8, 200):
            week_no = sheet[f"A{row_index}"].value
            if week_no in (None, ""):
                break
            if not isinstance(week_no, (int, float)):
                break  # Average and footer rows
            mapped = {
                "week_number": int(week_no),
                "week_start": sheet[f"B{row_index}"].value,
                "week_end": sheet[f"C{row_index}"].value,
                "committee": sheet[f"R{row_index}"].value,
                "hod_comment": sheet[f"AF{row_index}"].value,
                "dean_comment": sheet[f"AG{row_index}"].value,
                "actual_teaching_hours": sheet[f"M{row_index}"].value,
            }
            for field, column in {**TEACHING_COLUMNS, **DUTY_COLUMNS}.items():
                mapped[field] = sheet[f"{column}{row_index}"].value
            # 0 is a valid actual if explicitly typed; all blank = pending.
            mapped["actual_recorded"] = int(any(
                sheet[f"{column}{row_index}"].value is not None
                for column in ACTUAL_COLUMNS
            ))
            standard_value = sheet[f"AH{row_index}"].value
            if isinstance(standard_value, (int, float)):
                if standard_hours is None:
                    standard_hours = float(standard_value)
                elif standard_hours != float(standard_value):
                    raise ValueError("Standard teaching target differs between rows")
            mapped.update(calculate_week(mapped, standard_hours or 0, target_weekly_hours))
            records.append(mapped)
        return {"standard_teaching_hours": standard_hours, "target_weekly_hours": target_weekly_hours, "weeks": records}
    finally:
        book.close()
