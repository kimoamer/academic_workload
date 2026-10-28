import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "academic_workload" / "academic_workload"


class SchemaTests(unittest.TestCase):
    def test_doctype_metadata_is_consistent(self):
        doctypes = (
            "academic_workload_sheet", "academic_workload_week", "academic_workload_committee"
        )
        for name in doctypes:
            with self.subTest(doctype=name):
                path = ROOT / "doctype" / name / f"{name}.json"
                meta = json.loads(path.read_text())
                names = [field["fieldname"] for field in meta["fields"]]
                self.assertEqual(names, meta["field_order"])
                self.assertEqual(len(names), len(set(names)))
                self.assertEqual(meta["doctype"], "DocType")
                self.assertEqual(meta["istable"], int(name == "academic_workload_week"))

    def test_week_has_all_excel_metrics(self):
        meta = json.loads((ROOT / "doctype" / "academic_workload_week" / "academic_workload_week.json").read_text())
        fields = {item["fieldname"] for item in meta["fields"]}
        expected = {"actual_recorded", "planned_total_hours", "actual_total_hours", "teaching_gap", "total_gap",
                    "lecture_in_faculty", "lecture_outside", "tutorials", "labs", "practical", "clinical", "workshop", "postgraduate",
                    "hod_comment", "dean_comment"}
        self.assertTrue(expected <= fields)

    def test_reports_and_workspace_present(self):
        workspace = json.loads((ROOT / "workspace" / "academic_workload" / "academic_workload.json").read_text())
        json.loads(workspace["content"])
        linked = {x.get("link_to") for x in workspace["links"]}
        for report in ("Weekly Workload Report", "Academic Workload Summary"):
            self.assertIn(report, linked)
            slug = report.lower().replace(" ", "_")
            path = ROOT / "report" / slug / f"{slug}.json"
            self.assertEqual(json.loads(path.read_text())["ref_doctype"], "Academic Workload Sheet")


if __name__ == "__main__":
    unittest.main()
