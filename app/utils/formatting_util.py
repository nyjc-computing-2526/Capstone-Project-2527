"""Format activity rows from the database for list and detail templates."""

from __future__ import annotations

from datetime import date, datetime

from dateutil import parser as date_parser


def parse_activity_dt(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return date_parser.parse(str(value))


def enrich_row_for_card(activity: dict, current_user_id: int | None = None) -> dict:
    row = dict(activity)
    start = parse_activity_dt(row.get("started_at") or row.get("date"))
    row["display_time"] = start.strftime("%H:%M") if start else "—"
    row["display_date"] = start.strftime("%d %b %Y") if start else "—"
    row["is_current_user_organizer"] = (
        current_user_id is not None and row.get("created_by") == current_user_id
    )
    return row


def enrich_for_cards(activities: list[dict] | None, current_user_id: int | None = None) -> list[dict]:
    return [enrich_row_for_card(a, current_user_id) for a in (activities or [])]


def schedule_for_detail(activity: dict) -> dict:
    start = parse_activity_dt(activity.get("started_at") or activity.get("date"))
    end = parse_activity_dt(activity.get("ended_at"))

    def fmt_d(dt: datetime | None) -> str:
        return dt.strftime("%d %b %Y") if dt else "—"

    def fmt_t(dt: datetime | None) -> str:
        return dt.strftime("%H:%M") if dt else "—"

    return {
        "start_date": fmt_d(start),
        "start_time": fmt_t(start),
        "end_date": fmt_d(end),
        "end_time": fmt_t(end),
    }


def merge_by_id(*lists: list[dict]) -> list[dict]:
    seen = set()
    out: list[dict] = []
    for lst in lists:
        for item in lst or []:
            iid = item.get("id")
            if iid is None or iid in seen:
                continue
            seen.add(iid)
            out.append(item)
    return out
