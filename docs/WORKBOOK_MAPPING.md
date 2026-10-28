# Workload XLSX source mapping and important distinctions

Based on the provided `Weekly Workload` and `Committees List` worksheets.
The main header row is row 7 and data begins at row 8. Do not commit the
source staff workbook to a public GitHub repository.

| Workbook column | Data field | Meaning |
|---|---|---|
| A–C | `week_number`, `week_start`, `week_end` | Week number and inclusive dates |
| D–K | `lecture_in_faculty`, `lecture_outside`, `tutorials`, `labs`, `practical`, `clinical`, `workshop`, `postgraduate` | Planned teaching categories |
| L | `planned_teaching_hours` | Sum(D:K) |
| M | `actual_teaching_hours` | Independently entered teaching actual |
| N / O | `planned_office_hours` / `actual_office_hours` | Office Hours |
| P / Q | `planned_advising` / `actual_advising` | Advising |
| R | `committee` | Name from the Committees List |
| S / T | `planned_committee_hours` / `actual_committee_hours` | Committee duties |
| U / V | `planned_research` / `actual_research` | Research |
| W / X | `planned_meetings` / `actual_meetings` | Meetings |
| Y / Z | `planned_quality` / `actual_quality` | Quality |
| AA / AB | `planned_other_activities` / `actual_other_activities` | Other Activities |
| AC | `planned_total_hours` | Planned Teaching + planned other duties |
| AD | `actual_total_hours` | Actual Teaching + actual other duties |
| AE | `workload_status` | Compare actual to **employee-specific target** |
| AF / AG | `hod_comment`, `dean_comment` | Text feedback, not workflow |
| AH | Parent `standard_teaching_hours` | Teaching target stored per employee/term |
| AI | **not imported** | Spreadsheet formula references L (planned teaching), despite label 'Actual Teaching Hours'; correct actual input is M |
| AJ | `teaching_gap` | Target teaching minus actual teaching |
| AK | `total_gap` | Employee's target weekly hours minus actual total |

## Critical interpretation

1. The sample workbook has 20 weeks and a 40-hour weekly status formula, but
   other contracts may have different targets. Store those values per person.
2. The workbook has *planned* teaching broken down by category and a separate
   *actual* teaching total. Do not silently equate the two.
3. Most future weeks have planned hours but blank actual input cells. This is
   **not an underperformance of 40 hours**; actual is **Not Recorded**.
4. `Committees List` supplies 17 names and weekly caps. These caps are advisory
   in version 0.1.0 to avoid disallowing genuine recorded work.
5. Head of Department and Dean comments from the workbook remain fields without
   an approval workflow.
6. The provided HTML dashboard uses a different institution-wide dataset.
   This app does **not** copy its employee records or synthetic adjustments.
   Its current summary report is computed only from saved Frappe Sheet records.
