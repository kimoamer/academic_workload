"""Aggregation by Employee, Department, Program or Company."""

from __future__ import annotations

from frappe import _
from academic_workload.utils.calculations import group_summary
from academic_workload.utils.report_data import get_workload_rows

GROUP_TYPES = {
    "employee": ("Employee", "Link", "Employee"),
    "department": ("Department", "Link", "Department"),
    "program": ("Program", "Link", "Program"),
    "company": ("Company", "Link", "Company"),
    "grade": ("Employee Grade", "Link", "Employee Grade"),
    "employment_type": ("Employment Type", "Link", "Employment Type"),
}


def execute(filters=None):
    filters = filters or {}
    group_by = str(filters.get("group_by") or "Employee").lower().replace(" ", "_")
    if group_by not in GROUP_TYPES:
        group_by = "employee"
    sheets, weeks = get_workload_rows(filters)
    data = group_summary(sheets, weeks, group_by=group_by)
    group_label, group_fieldtype, group_options = GROUP_TYPES[group_by]
    columns = [
        {"fieldname": "group", "label": _(group_label), "fieldtype": group_fieldtype,
         "options": group_options, "width": 185},
        {"fieldname": "sheet_count", "label": _("Staff / Sheets"), "fieldtype": "Int", "width": 115},
        {"fieldname": "planned_weeks", "label": _("Planned Weeks"), "fieldtype": "Int", "width": 115},
        {"fieldname": "recorded_weeks", "label": _("Recorded Weeks"), "fieldtype": "Int", "width": 115},
        {"fieldname": "planned_hours", "label": _("Planned Hours"), "fieldtype": "Float", "width": 120},
        {"fieldname": "target_hours", "label": _("Target Hours (Recorded Weeks)"), "fieldtype": "Float", "width": 180},
        {"fieldname": "actual_hours", "label": _("Actual Hours"), "fieldtype": "Float", "width": 115},
        {"fieldname": "total_gap", "label": _("Total Gap (Target - Actual)"), "fieldtype": "Float", "width": 180},
        {"fieldname": "target_teaching_hours", "label": _("Target Teaching Hours"), "fieldtype": "Float", "width": 170},
        {"fieldname": "actual_teaching_hours", "label": _("Actual Teaching Hours"), "fieldtype": "Float", "width": 170},
        {"fieldname": "teaching_gap", "label": _("Teaching Gap"), "fieldtype": "Float", "width": 135},
    ]
    chart_rows = sorted(data, key=lambda row: row["actual_hours"], reverse=True)[:12]
    chart = {
        "data": {
            "labels": [row["group"] for row in chart_rows],
            "datasets": [
                {"name": _("Actual Hours"), "values": [row["actual_hours"] for row in chart_rows]},
                {"name": _("Target Hours"), "values": [row["target_hours"] for row in chart_rows]},
            ],
        },
        "type": "bar",
        "height": 290,
    } if chart_rows else None
    recorded = sum(row["recorded_weeks"] for row in data)
    summary = [
        {"label": _("Staff / Sheets"), "value": sum(row["sheet_count"] for row in data), "datatype": "Int"},
        {"label": _("Recorded Weeks"), "value": recorded, "datatype": "Int"},
        {"label": _("Actual Hours"), "value": round(sum(row["actual_hours"] for row in data), 2), "datatype": "Float"},
        {"label": _("Unrecorded Weeks"), "value": sum(row["planned_weeks"] - row["recorded_weeks"] for row in data), "datatype": "Int"},
    ]
    return columns, data, None, chart, summary
