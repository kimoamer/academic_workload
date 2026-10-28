import frappe
from frappe import _
from frappe.model.document import Document
from academic_workload.utils.calculations import hours


class AcademicWorkloadCommittee(Document):
    def validate(self):
        try:
            hours(self.max_weekly_hours, "max_weekly_hours")
        except ValueError as exc:
            frappe.throw(_(str(exc)))
