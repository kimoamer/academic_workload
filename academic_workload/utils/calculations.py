"""Pure calculations shared by Frappe controllers, reports, and unit tests.

The workbook records planned teaching by eight category columns but actual
teaching as a separate total. Do not infer that actual equals planned.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

TEACHING_FIELDS = (
    "lecture_in_faculty", "lecture_outside", "tutorials", "labs",
    "practical", "clinical", "workshop", "postgraduate",
)
DUTY_KEYS = (
    "office_hours", "advising", "committee_hours", "research",
    "meetings", "quality", "other_activities",
)
PLANNED_DUTY_FIELDS = tuple("planned_" + key for key in DUTY_KEYS)
ACTUAL_DUTY_FIELDS = tuple("actual_" + key for key in DUTY_KEYS)
ALL_INPUT_HOUR_FIELDS = (
    *TEACHING_FIELDS, "actual_teaching_hours",
    *PLANNED_DUTY_FIELDS, *ACTUAL_DUTY_FIELDS,
)


def value(row, key, default=None):
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def hours(raw, field="hours") -> Decimal:
    if raw is None or raw == "":
        return Decimal("0")
    try:
        number = Decimal(str(raw))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field} must be a number") from exc
    if not number.is_finite() or number < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return number


def round_hours(amount):
    return float(amount.quantize(Decimal("0.01")))


def calculate_week(row, target_teaching_hours, target_weekly_hours):
    """Return totals and gaps with deliberate Not Recorded semantics.

    Actual 0 is distinct from not recorded, controlled by `actual_recorded`.
    A positive actual value implicitly means recorded, even if unchecked.
    """
    teaching = sum((hours(value(row, f), f) for f in TEACHING_FIELDS), Decimal("0"))
    plan_duties = sum((hours(value(row, f), f) for f in PLANNED_DUTY_FIELDS), Decimal("0"))
    actual_duties = sum((hours(value(row, f), f) for f in ACTUAL_DUTY_FIELDS), Decimal("0"))
    actual_teaching = hours(value(row, "actual_teaching_hours"), "actual_teaching_hours")
    target_teaching = hours(target_teaching_hours, "standard_teaching_hours")
    target_weekly = hours(target_weekly_hours, "target_weekly_hours")
    has_actual = bool(int(value(row, "actual_recorded") or 0)) or any(
        hours(value(row, f), f) > 0 for f in (*ACTUAL_DUTY_FIELDS, "actual_teaching_hours")
    )
    actual_total = actual_teaching + actual_duties
    gap = target_weekly - actual_total
    status = ("Not Recorded" if not has_actual else
              "On Target" if gap == 0 else "Under" if gap > 0 else "Over")
    return {
        "planned_teaching_hours": round_hours(teaching),
        "planned_total_hours": round_hours(teaching + plan_duties),
        "actual_total_hours": round_hours(actual_total) if has_actual else 0.0,
        "teaching_gap": round_hours(target_teaching - actual_teaching) if has_actual else 0.0,
        "total_gap": round_hours(gap) if has_actual else 0.0,
        "workload_status": status,
        "actual_recorded": int(has_actual),
    }


def parse_date(raw):
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    if not raw:
        raise ValueError("Week start and end dates are required")
    return date.fromisoformat(str(raw)[:10])


def validate_weeks(rows):
    """Reject duplicate numbers and dates overlapping in the same sheet."""
    used_numbers = set()
    spans = []
    for row in rows:
        number = int(value(row, "week_number") or 0)
        if number < 1 or number > 60:
            raise ValueError("Week number must be between 1 and 60")
        if number in used_numbers:
            raise ValueError(f"Duplicate week number: {number}")
        used_numbers.add(number)
        start, end = parse_date(value(row, "week_start")), parse_date(value(row, "week_end"))
        if start > end:
            raise ValueError(f"Week {number}: end date precedes start date")
        if (end - start).days >= 7:
            raise ValueError(f"Week {number}: more than seven calendar days")
        spans.append((start, end, number))
    spans.sort()
    for prev, curr in zip(spans, spans[1:]):
        if prev[1] >= curr[0]:
            raise ValueError(f"Week {prev[2]} and week {curr[2]} have overlapping dates")


def group_summary(sheets, weeks, group_by="employee"):
    """Aggregate only actual-recorded weeks for performance vs target.

    `sheets` is a dict keyed by parent name; `weeks` are rows with `parent`.
    Each week is counted once even if its planned hours are zero.
    """
    allowed = {"employee", "department", "program", "company", "grade", "employment_type"}
    if group_by not in allowed:
        raise ValueError("Invalid group_by")
    grouped = {}
    for week in weeks:
        sheet = sheets.get(value(week, "parent"))
        if sheet is None:
            continue
        key = value(sheet, group_by) or "Not Set"
        bucket = grouped.setdefault(key, {
            "group": key, "sheets": set(), "planned_weeks": 0,
            "recorded_weeks": 0, "planned_hours": 0.0,
            "actual_hours": 0.0, "actual_teaching_hours": 0.0,
            "target_hours": 0.0, "target_teaching_hours": 0.0,
        })
        bucket["sheets"].add(value(week, "parent"))
        bucket["planned_weeks"] += 1
        bucket["planned_hours"] += float(value(week, "planned_total_hours") or 0)
        if int(value(week, "actual_recorded") or 0):
            bucket["recorded_weeks"] += 1
            bucket["actual_hours"] += float(value(week, "actual_total_hours") or 0)
            bucket["actual_teaching_hours"] += float(value(week, "actual_teaching_hours") or 0)
            bucket["target_hours"] += float(value(sheet, "target_weekly_hours") or 0)
            bucket["target_teaching_hours"] += float(value(sheet, "standard_teaching_hours") or 0)
    result = []
    for group in grouped.values():
        group["sheet_count"] = len(group.pop("sheets"))
        group["total_gap"] = round(group["target_hours"] - group["actual_hours"], 2)
        group["teaching_gap"] = round(group["target_teaching_hours"] - group["actual_teaching_hours"], 2)
        for field in ("planned_hours", "actual_hours", "actual_teaching_hours", "target_hours", "target_teaching_hours"):
            group[field] = round(group[field], 2)
        result.append(group)
    return sorted(result, key=lambda r: str(r["group"]).casefold())
