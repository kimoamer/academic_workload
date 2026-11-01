"""Server-enforced employee scope for every sheet access path."""
import frappe


def is_manager(user=None):
    roles = frappe.get_roles(user or frappe.session.user)
    return "System Manager" in roles or "Academic Workload Manager" in roles


def employee_for_user(user=None):
    user = user or frappe.session.user
    return frappe.db.get_value("Employee", {"user_id": user}, "name")


def permission_query_conditions(user=None):
    user = user or frappe.session.user
    if is_manager(user):
        return ""
    employee = employee_for_user(user)
    if not employee:
        return "1=0"
    return "tabAcademic Workload Sheet.employee = " + frappe.db.escape(employee)


def has_permission(doc, ptype=None, user=None):
    user = user or frappe.session.user
    if is_manager(user):
        return True
    if ptype in ("delete", "create", "submit", "cancel", "amend", "share", "import", "export"):
        return False
    return bool(employee_for_user(user) and doc.employee == employee_for_user(user))
