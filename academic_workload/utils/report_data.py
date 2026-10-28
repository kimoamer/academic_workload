"""Permission-respecting workload report retrieval.

Read parent sheets with get_list (enforces parent permission), then child rows
only for those authorized parents. Never use raw SQL over all employees.
"""

import frappe

SHEET_FIELDS = [
    "name", "employee", "employee_name", "company", "department",
    "program", "instructor", "grade", "employment_type", "academic_year", "academic_term",
    "standard_teaching_hours", "target_weekly_hours",
]

WEEK_FIELDS = [
    "name", "parent", "idx", "week_number", "week_start", "week_end", "actual_recorded",
    "lecture_in_faculty", "lecture_outside", "tutorials", "labs", "practical",
    "clinical", "workshop", "postgraduate",
    "planned_teaching_hours", "actual_teaching_hours", "committee",
    "planned_office_hours", "actual_office_hours",
    "planned_advising", "actual_advising",
    "planned_committee_hours", "actual_committee_hours",
    "planned_research", "actual_research",
    "planned_meetings", "actual_meetings",
    "planned_quality", "actual_quality",
    "planned_other_activities", "actual_other_activities",
    "planned_total_hours", "actual_total_hours", "teaching_gap", "total_gap",
    "workload_status", "hod_comment", "dean_comment", "notes",
]


def get_workload_rows(filters=None):
    filters = filters or {}
    allowed = {"employee", "company", "department", "program", "academic_year", "academic_term", "grade", "employment_type"}
    parent_filters = {key: filters[key] for key in allowed if filters.get(key)}
    sheets = frappe.get_list(
        "Academic Workload Sheet", filters=parent_filters, fields=SHEET_FIELDS,
        limit_page_length=0, order_by="employee asc",
    )
    if not sheets:
        return {}, []
    sheet_map = {sheet["name"]: dict(sheet) for sheet in sheets}
    weeks = []
    # Bound `IN` filters to small batches to avoid large SQL parameter lists.
    names = list(sheet_map)
    for offset in range(0, len(names), 200):
        batch = names[offset:offset + 200]
        child_filters = {"parent": ["in", batch], "parenttype": "Academic Workload Sheet"}
        if filters.get("week_number"):
            child_filters["week_number"] = int(filters["week_number"])
        weeks.extend(frappe.get_all(
            "Academic Workload Week", filters=child_filters,
            fields=WEEK_FIELDS, limit_page_length=0,
            order_by="parent asc, week_number asc",
        ))
    if filters.get("actual_only"):
        weeks = [row for row in weeks if row.get("actual_recorded")]
    weeks.sort(key=lambda row: (
        sheet_map[row["parent"]].get("employee") or "",
        sheet_map[row["parent"]].get("academic_year") or "",
        sheet_map[row["parent"]].get("academic_term") or "",
        int(row.get("week_number") or 0),
    ))
    return sheet_map, weeks
