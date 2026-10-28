import unittest

from academic_workload.utils.calculations import calculate_week, validate_weeks, group_summary


class CalculationTests(unittest.TestCase):
    def test_first_week_matches_40_hour_workbook_example(self):
        week = {
            "lecture_in_faculty": 3, "lecture_outside": 1, "actual_teaching_hours": 4,
            "planned_office_hours": 4, "actual_office_hours": 5,
            "planned_advising": 4, "actual_advising": 2,
            "planned_committee_hours": 4, "actual_committee_hours": 2,
            "planned_research": 8, "actual_research": 4,
            "planned_meetings": 4, "actual_meetings": 9,
            "planned_quality": 4, "actual_quality": 3,
            "planned_other_activities": 8, "actual_other_activities": 11,
            "actual_recorded": 1,
        }
        got = calculate_week(week, 10, 40)
        self.assertEqual(got["planned_teaching_hours"], 4)
        self.assertEqual(got["planned_total_hours"], 40)
        self.assertEqual(got["actual_total_hours"], 40)
        self.assertEqual(got["teaching_gap"], 6)
        self.assertEqual(got["total_gap"], 0)
        self.assertEqual(got["workload_status"], "On Target")

    def test_pending_week_is_not_automatically_under_target(self):
        got = calculate_week({"lecture_in_faculty": 3, "actual_recorded": 0}, 10, 40)
        self.assertEqual(got["workload_status"], "Not Recorded")
        self.assertEqual(got["actual_recorded"], 0)
        self.assertEqual(got["total_gap"], 0)

    def test_explicit_zero_actual_counts_as_reported(self):
        got = calculate_week({"actual_recorded": 1}, 10, 40)
        self.assertEqual(got["workload_status"], "Under")
        self.assertEqual(got["total_gap"], 40)

    def test_unchecked_nonzero_actual_is_recorded(self):
        got = calculate_week({"actual_recorded": 0, "actual_research": 2}, 10, 40)
        self.assertEqual(got["workload_status"], "Under")
        self.assertEqual(got["actual_recorded"], 1)

    def test_over_target(self):
        got = calculate_week({"actual_recorded": 1, "actual_teaching_hours": 46}, 10, 40)
        self.assertEqual(got["workload_status"], "Over")
        self.assertEqual(got["total_gap"], -6)

    def test_reject_negative_and_nan_hours(self):
        for value in (-1, "NaN", float("inf"), "abc"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calculate_week({"actual_recorded": 1, "actual_research": value}, 10, 40)

    def test_week_dates_and_numbers(self):
        valid = [
            {"week_number": 1, "week_start": "2026-09-19", "week_end": "2026-09-24"},
            {"week_number": 2, "week_start": "2026-09-26", "week_end": "2026-10-01"},
        ]
        validate_weeks(valid)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            validate_weeks(valid + [dict(valid[0])])
        with self.assertRaisesRegex(ValueError, "overlapping"):
            validate_weeks(valid + [{"week_number": 3, "week_start": "2026-09-24", "week_end": "2026-09-25"}])
        with self.assertRaisesRegex(ValueError, "end date"):
            validate_weeks([{"week_number": 1, "week_start": "2026-09-20", "week_end": "2026-09-19"}])

    def test_summary_targets_only_recorded_weeks(self):
        sheets = {"AWL-1": {"employee": "E1", "department": "Math", "target_weekly_hours": 40,
                            "standard_teaching_hours": 10}}
        weeks = [
            {"parent": "AWL-1", "planned_total_hours": 40, "actual_recorded": 1,
             "actual_total_hours": 40, "actual_teaching_hours": 4},
            {"parent": "AWL-1", "planned_total_hours": 40, "actual_recorded": 0,
             "actual_total_hours": 0, "actual_teaching_hours": 0},
        ]
        result = group_summary(sheets, weeks, "employee")[0]
        self.assertEqual(result["planned_weeks"], 2)
        self.assertEqual(result["recorded_weeks"], 1)
        self.assertEqual(result["planned_hours"], 80)
        self.assertEqual(result["target_hours"], 40)
        self.assertEqual(result["actual_hours"], 40)
        self.assertEqual(result["teaching_gap"], 6)


if __name__ == "__main__":
    unittest.main()
