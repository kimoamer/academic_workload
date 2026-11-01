"""Preview-only parser for the updated Rania Nadeem workbook (no writes)."""
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
    "planned_cbl": "Y", "actual_cbl": "Z",
    "planned_projects": "AA", "actual_projects": "AB",
    "planned_quality": "AC", "actual_quality": "AD",
    "planned_other_activities": "AE", "actual_other_activities": "AF",
    "mission_hours": "AJ", "vacation_hours": "AK",
    "attendance_hours": "AR",
}
ACTUAL_COLUMNS = ("M", "O", "Q", "T", "V", "X", "Z", "AB", "AD", "AF", "AJ", "AK")


def preview_workbook(path, *, target_weekly_hours):
    from openpyxl import load_workbook
    book = load_workbook(path, read_only=True, data_only=False)
    try:
        if "Weekly Workload" not in book.sheetnames:
            raise ValueError("Expected worksheet 'Weekly Workload'")
        sheet = book["Weekly Workload"]
        if "Teaching" not in str(sheet["D6"].value) or "Week" not in str(sheet["A7"].value):
            raise ValueError("Workbook has an unknown header format")
        if "CBL" not in str(sheet["Y7"].value) or "Projects" not in str(sheet["AA7"].value):
            raise ValueError("Expected the updated 2026 workbook (CBL and Projects)")
        records = []
        standard_hours = None
        for i in range(8, 200):
            week_number = sheet[f"A{i}"].value
            if not isinstance(week_number, (int, float)):
                break
            mapped = {
                "week_number": int(week_number),
                "week_start": sheet[f"B{i}"].value,
                "week_end": sheet[f"C{i}"].value,
                "committee": sheet[f"R{i}"].value,
                "hod_comment": sheet[f"AL{i}"].value,
                "dean_comment": sheet[f"AM{i}"].value,
            }
            for field, col in {**TEACHING_COLUMNS, **DUTY_COLUMNS}.items():
                v = sheet[f"{col}{i}"].value
                mapped[field] = v if not (isinstance(v, str) and v.startswith("=")) else None
            mapped["actual_recorded"] = int(any(sheet[f"{col}{i}"].value is not None for col in ACTUAL_COLUMNS))
            standard = sheet[f"AN{i}"].value
            if isinstance(standard, (float, int)):
                if standard_hours is None:
                    standard_hours = float(standard)
                elif standard_hours != float(standard):
                    raise ValueError("Standard teaching target differs between rows")
            # Excel M includes historical manually-entered actual totals. The new
            # app derives actual teaching from D:K instead: no M import.
            mapped.update(calculate_week(mapped, standard_hours or 0, target_weekly_hours))
            records.append(mapped)
        return {
            "standard_teaching_hours": standard_hours,
            "target_weekly_hours": target_weekly_hours,
            "weeks": records,
        }
    finally:
        book.close()
