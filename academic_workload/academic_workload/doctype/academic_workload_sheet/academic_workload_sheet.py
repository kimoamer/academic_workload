"""Weekly workload sheet: calculated hours, employee scope and historical lock."""

import frappe
from frappe import _
from frappe.model.document import Document

from academic_workload.permissions import is_manager, employee_for_user
from academic_workload.utils.calculations import (
    calculate_week, hours, validate_weeks, parse_date,
)

# Fields staff may populate. They cannot revise targets, employee, or old weeks.
STAFF_FIELDS = {
    "week_number", "week_start", "week_end", "actual_recorded", "committee",
    "lecture_in_faculty", "lecture_outside", "tutorials", "labs", "practical",
    "clinical", "workshop", "postgraduate",
    "actual_office_hours", "actual_advising", "actual_committee_hours",
    "actual_research", "actual_meetings", "actual_cbl", "actual_projects",
    "actual_quality", "actual_other_activities", "mission_hours",
    "vacation_hours", "notes",
}
COMPUTED_FIELDS = {
    "planned_teaching_hours", "actual_teaching_hours", "planned_total_hours",
    "actual_total_hours", "teaching_gap", "total_gap", "adjusted_target_hours",
    "workload_status",
}


def _normalized(value):
    if value in (None, ""):
        return ""
    return str(value)


def check_historical_lock(current, previous, today, manager):
    """Persisted weeks ending before today cannot be modified by any staff.

    Manager corrections are allowed but always tracked by Version history.
    Deleting/reordering a past child row is also rejected.
    """
    if manager:
        return
    old_by_name = {row.name: row for row in (previous.weeks or []) if row.name}
    new_by_name = {row.name: row for row in (current.weeks or []) if row.name}
    for name, old in old_by_name.items():
        old_end = parse_date(old.week_end)
        if name not in new_by_name and old_end < today:
            raise ValueError("Previously recorded weeks cannot be removed")
        new = new_by_name.get(name)
        if new and old_end < today:
            fields = STAFF_FIELDS | COMPUTED_FIELDS | {
                "planned_office_hours", "planned_advising", "planned_committee_hours",
                "planned_research", "planned_meetings", "planned_cbl",
                "planned_projects", "planned_quality", "planned_other_activities",
                "hod_comment", "dean_comment", "attendance_hours",
            }
            if any(_normalized(getattr(old, key, None)) != _normalized(getattr(new, key, None)) for key in fields):
                raise ValueError(f"Week {old.week_number} is locked because its end date has passed")


class AcademicWorkloadSheet(Document):
    def validate(self):
        manager = is_manager()
        try:
            if not manager:
                employee = employee_for_user()
                if not employee or self.employee != employee:
                    raise ValueError("You may only edit your own academic workload")
                if self.is_new():
                    raise ValueError("Academic workload sheets must be created by a manager")

            hours(self.standard_teaching_hours, "standard_teaching_hours")
            hours(self.target_weekly_hours, "target_weekly_hours")
            hours(self.planned_teaching_load, "planned_teaching_load")
            if not self.target_weekly_hours or float(self.target_weekly_hours) <= 0:
                raise ValueError("Target Total Hours / Week must be greater than zero")
            if not 1 <= int(self.number_of_weeks or 0) <= 60:
                raise ValueError("Number of weeks must be from 1 to 60")
            if not 1 <= int(self.days_per_week or 0) <= 7:
                raise ValueError("Days per week must be from 1 to 7")
            validate_weeks(self.weeks or [])

            if not self.is_new():
                old = self.get_doc_before_save() or frappe.get_doc(self.doctype, self.name)
                if not manager:
                    # The user's edit is restricted to week actuals / notes only.
                    fixed_fields = (
                        "employee", "academic_year", "academic_term", "company",
                        "department", "academic_department", "employment_type",
                        "grade", "program", "instructor", "standard_teaching_hours",
                        "planned_teaching_load", "target_weekly_hours", "first_week_start",
                        "number_of_weeks", "days_per_week", "entry_note",
                    )
                    for field in fixed_fields:
                        if _normalized(getattr(self, field, None)) != _normalized(getattr(old, field, None)):
                            raise ValueError(f"{field} can only be changed by the manager")
                    old_rows = {row.name: row for row in old.weeks or [] if row.name}
                    if len(self.weeks or []) != len(old.weeks or []) or set(
                        row.name for row in self.weeks or []
                    ) != set(old_rows):
                        raise ValueError("Staff cannot add or remove week rows")
                    for row in self.weeks or []:
                        prev = old_rows[row.name]
                        # Prevent changes to the planned baseline and reviewer feedback.
                        protected = set(row.as_dict()) - STAFF_FIELDS - COMPUTED_FIELDS
                        protected -= {"idx", "modified", "modified_by"}
                        for key in protected:
                            if key.startswith("_") or key in ("__islocal",):
                                continue
                            if _normalized(row.get(key)) != _normalized(prev.get(key)):
                                raise ValueError(f"Week {row.week_number}: {key} cannot be edited")
                from frappe.utils import getdate, nowdate
                check_historical_lock(self, old, getdate(nowdate()), manager)

            for row in self.weeks or []:
                result = calculate_week(
                    row, self.standard_teaching_hours,
                    self.target_weekly_hours, self.planned_teaching_load,
                )
                for fieldname, calculated in result.items():
                    setattr(row, fieldname, calculated)
        except (ValueError, TypeError) as exc:
            frappe.throw(_("Invalid academic workload: {0}").format(str(exc)))

        if frappe.db.exists("Academic Workload Sheet", {
            "employee": self.employee,
            "academic_year": self.academic_year,
            "academic_term": self.academic_term,
            "name": ["!=", self.name],
        }):
            frappe.throw(_("A workload sheet already exists for this employee, year and term."))
        if self.academic_term and self.academic_year and frappe.get_meta("Academic Term").has_field("academic_year"):
            expected_year = frappe.db.get_value("Academic Term", self.academic_term, "academic_year")
            if expected_year and expected_year != self.academic_year:
                frappe.throw(_("Academic Term does not belong to the selected Academic Year."))
