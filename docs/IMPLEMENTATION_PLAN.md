# MVP implementation plan — actual state

## Completed as source code

- [x] Package and Frappe hooks for v15
- [x] Three DocTypes (one sheet per employee/year/term, weekly child rows,
      committee/duty reference)
- [x] Independent planned versus actual calculation with missing data semantics
- [x] Duplicate-week and overlapping-date validation
- [x] Controlled role, default committee reference data, and workspace
- [x] Two Script Reports and optional multi-week generation buttons
- [x] Read-only preview parser for the supplied workbook format
- [x] Local calculation/schema unit tests

## Not yet validated on a live Frappe test site

- [ ] `bench --site TEST install-app academic_workload`
- [ ] Role permissions on synced DocTypes and reports
- [ ] Layout of the 20-week child table in the Desk UI
- [ ] Large-data report performance and printable/PDF layout
- [ ] Integration variations across Education v15 minor versions

## Next iteration after test deployment

- [ ] 20-week spreadsheet-style editor with keyboard navigation and paste
- [ ] Strict import wizard with Employee mapping preview and duplicate prevention
- [ ] Report chart enhancements for rank/faculty and explicit planning targets

No server deployments, remote settings, employee imports, or database writes
were attempted in this source-code deliverable.
