// Minimal data entry enhancements: generate dates and replicate a planned
// baseline without overwriting any actual recorded data.
const AWL_PLAN_FIELDS = [
    "lecture_in_faculty", "lecture_outside", "tutorials", "labs",
    "practical", "clinical", "workshop", "postgraduate",
    "planned_office_hours", "planned_advising", "planned_committee_hours",
    "planned_research", "planned_meetings", "planned_quality",
    "planned_other_activities",
];

frappe.ui.form.on("Academic Workload Sheet", {
    refresh(frm) {
        frm.add_custom_button(__("Generate Weeks"), () => {
            if ((frm.doc.weeks || []).length) {
                frappe.msgprint(__("Week rows already exist. Clear them manually before regenerating."));
                return;
            }
            if (!frm.doc.first_week_start) {
                frappe.msgprint(__("Please enter First Week Start first."));
                return;
            }
            const count = Number(frm.doc.number_of_weeks);
            const days = Number(frm.doc.days_per_week);
            if (!Number.isInteger(count) || count < 1 || count > 60 ||
                !Number.isInteger(days) || days < 1 || days > 7) {
                frappe.msgprint(__("Weeks must be 1–60 and days per week must be 1–7."));
                return;
            }
            for (let index = 0; index < count; index++) {
                const row = frm.add_child("weeks");
                row.week_number = index + 1;
                row.week_start = frappe.datetime.add_days(frm.doc.first_week_start, 7 * index);
                row.week_end = frappe.datetime.add_days(row.week_start, days - 1);
                row.actual_recorded = 0;
                row.workload_status = "Not Recorded";
            }
            frm.refresh_field("weeks");
            frm.dirty();
        }, __("Actions"));

        frm.add_custom_button(__("Copy Week 1 Plan to Empty Weeks"), () => {
            const weeks = frm.doc.weeks || [];
            if (weeks.length < 2) {
                frappe.msgprint(__("Create at least two weeks first."));
                return;
            }
            frappe.confirm(__("Copy Week 1 planned values to weeks with no planned values? Actual hours are never copied."), () => {
                const source = weeks[0];
                weeks.slice(1).forEach(row => {
                    if (AWL_PLAN_FIELDS.some(field => Number(row[field] || 0) !== 0)) return;
                    AWL_PLAN_FIELDS.forEach(field => { row[field] = source[field] || 0; });
                    if (!row.committee) row.committee = source.committee || "";
                });
                frm.refresh_field("weeks");
                frm.dirty();
            });
        }, __("Actions"));
    },
});
