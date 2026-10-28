app_name = "academic_workload"
app_title = "Academic Workload"
app_publisher = "Innomate"
app_description = "Academic teaching and other-duty workload entry and reporting"
app_license = "Proprietary"
app_version = "0.1.0"

# Frappe/ERPNext and Education are expected to already be installed on the target site.
# No ERPNext/HRMS schema is modified by this app.
required_apps = ["erpnext", "education"]

before_install = "academic_workload.setup.install.before_install"
after_install = "academic_workload.setup.install.after_install"
