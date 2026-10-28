frappe.query_reports["Academic Workload Summary"] = {
    filters: [
        {
            fieldname: "group_by", label: __("Group By"), fieldtype: "Select",
            options: "Employee\nDepartment\nProgram\nCompany\nGrade\nEmployment Type", default: "Employee", reqd: 1,
        },
        { fieldname: "academic_year", label: __("Academic Year"), fieldtype: "Link", options: "Academic Year" },
        { fieldname: "academic_term", label: __("Academic Term"), fieldtype: "Link", options: "Academic Term" },
        { fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company" },
        { fieldname: "department", label: __("Department"), fieldtype: "Link", options: "Department" },
        { fieldname: "program", label: __("Program"), fieldtype: "Link", options: "Program" },
        { fieldname: "employee", label: __("Employee"), fieldtype: "Link", options: "Employee" },
        { fieldname: "grade", label: __("Employee Grade"), fieldtype: "Link", options: "Employee Grade" },
        { fieldname: "employment_type", label: __("Employment Type"), fieldtype: "Link", options: "Employment Type" },
        { fieldname: "actual_only", label: __("Recorded Actual Only"), fieldtype: "Check", default: 0 },
    ],
};
