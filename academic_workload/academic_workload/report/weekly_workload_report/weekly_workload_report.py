"""Weekly workload detail mirroring the supplied 2026-27 Excel columns."""

from __future__ import annotations

import frappe
from frappe import _

from academic_workload.utils.report_data import get_workload_rows


def column(fieldname, label, fieldtype="Float", width=115, options=None, hidden=0):
    col = {"fieldname": fieldname, "label": _(label), "fieldtype": fieldtype, "width": width}
    if options:
        col["options"] = options
    if hidden:
        col["hidden"] = 1
    return col


COLUMNS = [
    column("employee", "Employee", "Link", 135, "Employee"),
    column("employee_name", "Employee Name", "Data", 190),
    column("company", "Company", "Link", 125, "Company", hidden=1),
    column("department", "Department", "Link", 150, "Department"),
    column("program", "Program", "Link", 120, "Program", hidden=1),
    column("grade", "Employee Grade", "Link", 120, "Employee Grade", hidden=1),
    column("employment_type", "Employment Type", "Link", 145, "Employment Type", hidden=1),
    column("academic_year", "Academic Year", "Link", 110, "Academic Year"),
    column("academic_term", "Academic Term", "Link", 130, "Academic Term"),
    column("sheet", "Workload Sheet", "Link", 140, "Academic Workload Sheet", hidden=1),
    column("week_number", "Week No.", "Int", 85),
    column("week_start", "Week Start", "Date", 115),
    column("week_end", "Week End", "Date", 115),
    column("lecture_in_faculty", "Lectures in Faculty"),
    column("lecture_outside", "Lectures Outside"),
    column("tutorials", "Tutorials"),
    column("labs", "Labs"),
    column("practical", "Practical"),
    column("clinical", "Clinical"),
    column("workshop", "Workshop"),
    column("postgraduate", "Postgraduate"),
    column("planned_teaching_hours", "Planned Teaching Hours"),
    column("actual_teaching_hours", "Actual Teaching Hours"),
    column("planned_office_hours", "Planned Office Hours"),
    column("actual_office_hours", "Actual Office Hours"),
    column("planned_advising", "Planned Advising"),
    column("actual_advising", "Actual Advising"),
    column("committee", "Committee", "Link", 180, "Academic Workload Committee"),
    column("planned_committee_hours", "Planned Committee Hours"),
    column("actual_committee_hours", "Actual Committee Hours"),
    column("planned_research", "Planned Research"),
    column("actual_research", "Actual Research"),
    column("planned_meetings", "Planned Meetings"),
    column("actual_meetings", "Actual Meetings"),
    column("planned_quality", "Planned Quality"),
    column("actual_quality", "Actual Quality"),
    column("planned_other_activities", "Planned Other Activities"),
    column("actual_other_activities", "Actual Other Activities"),
    column("planned_total_hours", "Planned AWL"),
    column("actual_total_hours", "Actual Total AWL"),
    column("target_weekly_hours", "Target Total Hours"),
    column("standard_teaching_hours", "Standard Teaching Hours"),
    column("teaching_gap", "Teaching Gap (Target - Actual)"),
    column("total_gap", "Total Gap (Target - Actual)"),
    column("workload_status", "Status", "Data", 115),
    column("hod_comment", "HOD Comment", "Data", 180),
    column("dean_comment", "Dean Comment", "Data", 180),
    column("notes", "Week Notes", "Data", 180, hidden=1),
]

ACTUAL_COLUMNS = {
    "actual_teaching_hours", "actual_office_hours", "actual_advising",
    "actual_committee_hours", "actual_research", "actual_meetings",
    "actual_quality", "actual_other_activities", "actual_total_hours",
    "teaching_gap", "total_gap",
}


def execute(filters=None):
    sheets, weeks = get_workload_rows(filters)
    data = []
    for week in weeks:
        sheet = sheets[week["parent"]]
        row = {**dict(week)}
        row.update({key: sheet.get(key) for key in (
            "employee", "employee_name", "company", "department", "program", "grade", "employment_type",
            "academic_year", "academic_term", "target_weekly_hours", "standard_teaching_hours",
        )})
        row["sheet"] = week["parent"]
        if not row.get("actual_recorded"):
            for key in ACTUAL_COLUMNS:
                row[key] = None  # Explicitly distinguish pending weeks from zero actual hours.
        data.append(row)
    recorded = [row for row in data if row.get("actual_recorded")]
    summary = [
        {"label": _("Weeks"), "value": len(data), "indicator": "Blue", "datatype": "Int"},
        {"label": _("Recorded Weeks"), "value": len(recorded), "indicator": "Green", "datatype": "Int"},
        {"label": _("Actual Workload (h)"), "value": round(sum(row.get("actual_total_hours") or 0 for row in recorded), 2), "datatype": "Float"},
    ]
    return COLUMNS, data, None, None, summary
