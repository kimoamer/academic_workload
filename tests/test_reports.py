"""Report behavior tested with a minimal fake Frappe ORM (no site connection)."""

import importlib
import sys
import types
import unittest
from unittest.mock import patch


class ReportTests(unittest.TestCase):
    def test_weekly_and_summary_reports_do_not_count_pending_week(self):
        fake = types.ModuleType("frappe")
        fake._ = lambda s: s
        fake.get_list = lambda dt, **kwargs: [{
            "name": "AWL-1", "employee": "EMP-001", "employee_name": "Sample",
            "company": "Sample Company", "department": "Science", "program": "BSc",
            "academic_year": "2026-2027", "academic_term": "Fall",
            "standard_teaching_hours": 10, "target_weekly_hours": 40,
        }]
        fake.get_all = lambda dt, **kwargs: [
            {"name": "CHILD-1", "parent": "AWL-1", "week_number": 1,
             "actual_recorded": 1, "planned_total_hours": 40,
             "actual_teaching_hours": 4, "actual_total_hours": 40,
             "teaching_gap": 6, "total_gap": 0, "workload_status": "On Target"},
            {"name": "CHILD-2", "parent": "AWL-1", "week_number": 2,
             "actual_recorded": 0, "planned_total_hours": 40,
             "actual_teaching_hours": 0, "actual_total_hours": 0,
             "teaching_gap": 0, "total_gap": 0, "workload_status": "Not Recorded"},
        ]
        with patch.dict(sys.modules, {"frappe": fake}):
            weekly = importlib.import_module(
                "academic_workload.academic_workload.report.weekly_workload_report.weekly_workload_report"
            )
            summary = importlib.import_module(
                "academic_workload.academic_workload.report.academic_workload_summary.academic_workload_summary"
            )
            _, rows, _, _, kpis = weekly.execute({})
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["actual_total_hours"], 40)
            self.assertIsNone(rows[1]["actual_total_hours"])
            self.assertEqual(rows[1]["workload_status"], "Not Recorded")
            self.assertEqual(kpis[1]["value"], 1)
            cols, data, _, chart, _ = summary.execute({"group_by": "Department"})
            self.assertEqual(cols[0]["options"], "Department")
            self.assertEqual(data[0]["group"], "Science")
            self.assertEqual(data[0]["target_hours"], 40)
            self.assertEqual(data[0]["planned_weeks"], 2)
            self.assertEqual(data[0]["recorded_weeks"], 1)
            self.assertEqual(chart["data"]["datasets"][0]["values"], [40])


if __name__ == "__main__":
    unittest.main()
