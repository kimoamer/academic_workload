"""Install only reference committee names from the supplied workbook.

No employee, actual workload, or historical source data is installed.
"""

import frappe

# Academic duties and the weekly caps shown in the reference workbook's
# 'Committees List' tab. Caps are for reference, not hard validation rules.
REFERENCE_COMMITTEES = (
    ("Academic Advising", 4),
    ("Office Hours", 6),
    ("Clinic Supervision", 2),
    ("Committees Follow the University Administration", 2),
    ("Control", 4),
    ("Courses Equivalency Committee", 2),
    ("Education Development Center", 2),
    ("Field Training", 4),
    ("International Relations Committee", 1),
    ("Lab Evaluation", 2),
    ("Postgraduate Studies and Scientific Research Committee", 2),
    ("Quality Assurance", 4),
    ("Questionnaire Committee", 2),
    ("Student Activities", 2),
    ("Summer Training", 4),
    ("Timetables", 4),
    ("Others", 2),
)


def before_install():
    """Create a private-to-the-app role before DocType permissions are synced."""
    role_name = "Academic Workload Manager"
    if not frappe.db.exists("Role", role_name):
        frappe.get_doc({"doctype": "Role", "role_name": role_name, "desk_access": 1}).insert(ignore_permissions=True)


def after_install():
    for label, cap in REFERENCE_COMMITTEES:
        if frappe.db.exists("Academic Workload Committee", label):
            continue
        frappe.get_doc({
            "doctype": "Academic Workload Committee",
            "committee_name": label,
            "max_weekly_hours": cap,
            "enabled": 1,
        }).insert(ignore_permissions=True)
