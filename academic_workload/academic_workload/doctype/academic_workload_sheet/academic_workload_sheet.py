"""One Academic Workload Sheet per employee, academic year, and term."""

import frappe
from frappe import _
from frappe.model.document import Document

from academic_workload.utils.calculations import (
    calculate_week, hours, validate_weeks,
)


class AcademicWorkloadSheet(Document):
    def validate(self):
        try:
            hours(self.standard_teaching_hours, "standard_teaching_hours")
            hours(self.target_weekly_hours, "target_weekly_hours")
            if not self.target_weekly_hours or float(self.target_weekly_hours) <= 0:
                raise ValueError("Target Total Hours / Week must be greater than zero")
            if not 1 <= int(self.number_of_weeks or 0) <= 60:
                raise ValueError("Number of weeks must be from 1 to 60")
            if not 1 <= int(self.days_per_week or 0) <= 7:
                raise ValueError("Days per week must be from 1 to 7")
            validate_weeks(self.weeks or [])
            for week in self.weeks or []:
                result = calculate_week(
                    week, self.standard_teaching_hours, self.target_weekly_hours
                )
                for fieldname, value in result.items():
                    setattr(week, fieldname, value)
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
