# Academic Workload — Frappe Education

A focused data-entry and reporting app for academic staff workload. Built for
**Frappe Framework / ERPNext / Frappe Education v15**. This is **not** a timetable
planner, an HR approval engine, or a full academic scheduling system.

## The data model

| DocType | Purpose |
|---|---|
| **Academic Workload Sheet** | One employee × academic year × academic term, with targets and 1–60 weekly rows |
| **Academic Workload Week** | Child table with planned teaching categories, manually entered actual teaching, other duties, comments and totals |
| **Academic Workload Committee** | Optional committee/duty reference and advisory weekly hours cap |

Reuses ERPNext `Employee`, `Department`, `Company`, plus Education `Instructor`,
`Program`, `Academic Year`, and `Academic Term`. No changes or overrides to their
schemas. HRMS is optional, and there is **no dependency on Course Schedule**.

The weekly child record preserves the supplied spreadsheet's categories:

- Planned teaching: in-faculty lectures, outside lectures, tutorials, labs,
  practical, clinical, workshops, postgraduate.
- Actual teaching: a **separate manually entered total** (not copied from plan).
- Other duties: office hours, advising, committee hours, research, meetings,
  quality, and other activities — with separate planned and actual values.
- Committee name, HOD and Dean comments, week number and dates.

Target teaching hours and target total hours are stored **per sheet**. Do not
assume a 40-hour weekly target or a 10-hour teaching target for every staff member.

## Recording logic

- `Planned Teaching = sum(eight planned teaching categories)`
- `Planned Total = Planned Teaching + planned other duties`
- `Actual Total = actual teaching + actual other duties`
- `Teaching Gap = teaching target - actual teaching`
- `Total Gap = weekly target - actual total`
- Status: **Not Recorded / Under / On Target / Over**

**Not Recorded** is different from **zero actual**: a newly generated week has
`Actual Recorded` unchecked; entering any positive actual value also marks it
recorded. To explicitly record an all-zero week, check `Actual Recorded`.
Unreported weeks do not count as under-target hours in reports. Over-target
workloads have a negative gap (target minus actual), matching the workbook.

## Reports (live Frappe Script Reports)

1. **Weekly Workload Report** — Excel-style weekly detail, including all eight
   planned teaching categories, seven planned/actual duty pairs, targets,
   variances and HOD / Dean comments. Filters by year, term, company, department,
   program, employee, grade, employment type, and week. Unrecorded actuals display as **blank**.
2. **Academic Workload Summary** — Group by Employee / Department / Program /
   Company / Grade / Employment Type. Shows planned and recorded weeks, planned and actual hours, target
   hours for **recorded weeks only**, teaching gaps, totals and bar chart.

The **Academic Workload** workspace links to the forms and both reports.

## Install (only when you choose to deploy)

Requirements: Frappe/ERPNext 15 and Frappe Education installed on the same site.
Your bench, site and credentials are not accessed by this repository.

From a local copy of this repository:

```bash
cd /home/frappe/frappe-bench
bench get-app /absolute/path/to/academic_workload
bench --site YOUR-SITE install-app academic_workload
bench --site YOUR-SITE migrate
```

Assign the new **Academic Workload Manager** role only to authorized reporting
staff. System Managers can already access the app. The app does **not** grant
university-wide workload access to all Academics Users by default. The install
hook creates the manager role and adds the **17 reference committee/duty names**
from the example workbook, without adding any employee or workload records.

## Data entry

1. Create **Academic Workload Sheet** and select Employee, Academic Year and
   Academic Term. Optionally choose Instructor and Program.
2. Enter this employee's *Standard Teaching Hours / Week* and *Target Total
   Hours / Week* (do not blindly use 10 and 40).
3. Enter `First Week Start`, `Number of Weeks`, and `Days per Week`. From
   **Actions → Generate Weeks**, create 20 rows (or your actual term length).
4. Expand the first row to enter planned contact hours and other duties. Optionally
   use **Copy Week 1 Plan to Empty Weeks** to reduce repetitive entry.
5. Enter actual hours and tick **Actual Recorded** each reporting week. Save.
6. Open the reports from the workspace. Export as Excel / CSV using standard
   Frappe report functions.

HOD and Dean comments are **text fields only**. There is intentionally no
submission/approval workflow in version 0.1.0.

## XLSX reference parsing

The included helper `academic_workload.importers.weekly_workbook.preview_workbook`
parses the original *Weekly Workload* worksheet in **read-only preview mode**:

```python
from academic_workload.importers.weekly_workbook import preview_workbook
preview = preview_workbook("/path/to/workbook.xlsx", target_weekly_hours=40)
print(len(preview["weeks"]), preview["weeks"][0]["workload_status"])
```

It **does not create documents or write to the database**. You can review
mapped rows before deciding to import them. The original workbook and personal
staff information are intentionally **not committed** to this repository.

## Validation and tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q academic_workload
```

The pure-Python calculations and schema tests run without a Frappe instance.
Installation, desk navigation, role provisioning, permissions and report queries
must be verified on a **separate test Frappe site** before production rollout.

## Roadmap

- Spreadsheet-style multi-week matrix editor (native child table works now).
- A reviewed import wizard with explicit Employee mapping and duplicate checks.
- Richer dashboard (faculty and rank filters), and optional multi-program
  allocations if the institution wants them.
- Optional reviewer permissions / approvals only if later requested.

## License

Proprietary. Copyright © 2026 Innomate. All rights reserved.
