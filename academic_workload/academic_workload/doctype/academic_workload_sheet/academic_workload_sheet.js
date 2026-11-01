const AWL_PLAN_FIELDS = [
    "planned_office_hours", "planned_advising", "planned_committee_hours",
    "planned_research", "planned_meetings", "planned_cbl", "planned_projects",
    "planned_quality", "planned_other_activities",
];
frappe.ui.form.on("Academic Workload Sheet", {
    refresh(frm) {
        const roles = frappe.user_roles || [];
        const manager = roles.includes("System Manager") || roles.includes("Academic Workload Manager");
        frm.set_df_property("weeks", "cannot_add_rows", !manager);
        frm.set_df_property("weeks", "cannot_delete_rows", !manager);
        if (!manager) {
            ["employee", "academic_department", "academic_year", "academic_term",
                "planned_teaching_load", "standard_teaching_hours",
                "target_weekly_hours", "first_week_start", "number_of_weeks",
                "days_per_week", "entry_note", "program", "instructor"].forEach(
                name => frm.set_df_property(name, "read_only", 1)
            );
            frm.fields_dict.weeks.grid.grid_rows.forEach(gridrow => {
                const old = frappe.datetime.get_today();
                const locked = gridrow.doc.week_end && gridrow.doc.week_end < old;
                if (locked) gridrow.toggle_editable && gridrow.toggle_editable(false);
            });
            return;
        }
        frm.add_custom_button(__("Generate Weeks"), () => {
            if ((frm.doc.weeks || []).length) return frappe.msgprint(__("Week rows already exist."));
            if (!frm.doc.first_week_start) return frappe.msgprint(__("Enter First Week Start."));
            const count = Number(frm.doc.number_of_weeks), days = Number(frm.doc.days_per_week);
            if (!Number.isInteger(count) || count < 1 || count > 60 ||
                !Number.isInteger(days) || days < 1 || days > 7)
                return frappe.msgprint(__("Weeks: 1-60; Days: 1-7."));
            for (let i = 0; i < count; i++) {
                const row = frm.add_child("weeks");
                row.week_number = i + 1;
                row.week_start = frappe.datetime.add_days(frm.doc.first_week_start, 7 * i);
                row.week_end = frappe.datetime.add_days(row.week_start, days - 1);
            }
            frm.refresh_field("weeks");
            frm.dirty();
        }, __("Actions"));
        frm.add_custom_button(__("Copy Week 1 Plan to Empty Weeks"), () => {
            const weeks = frm.doc.weeks || [];
            if (weeks.length < 2) return;
            frappe.confirm(__("Copy the first week's plan to empty future weeks?"), () => {
                const source = weeks[0];
                weeks.slice(1).forEach(row => {
                    if (row.week_end < frappe.datetime.get_today()) return;
                    if (AWL_PLAN_FIELDS.some(key => Number(row[key] || 0))) return;
                    AWL_PLAN_FIELDS.forEach(key => row[key] = source[key] || 0);
                    if (!row.committee) row.committee = source.committee || "";
                });
                frm.refresh_field("weeks");
                frm.dirty();
            });
        }, __("Actions"));
    },
});
