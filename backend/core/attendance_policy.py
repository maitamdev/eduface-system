"""Shared attendance rules for reports, student summaries and grade eligibility.

There is currently no historical class roster. Eligibility uses the profile's
current department and enrollment day, with unassigned sessions shared by all.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Optional

VN_TZ = timezone(timedelta(hours=7))
ATTENDED_STATUSES = frozenset({"present", "late", "excused"})


def as_utc(value: datetime) -> datetime:
    """MongoDB's legacy naive timestamps represent UTC, never server local time."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def session_local_day(session: dict) -> date:
    return as_utc(session["started_at"]).astimezone(VN_TZ).date()


def session_applies_to_person(session: dict, person: dict) -> bool:
    if "roster_ids" in session:
        return str(person["_id"]) in session["roster_ids"]
    department = (session.get("department") or "").strip().casefold()
    if department and department != (person.get("department") or "").strip().casefold():
        return False
    enrolled_at = person.get("enrolled_at")
    return enrolled_at is None or session_local_day(session) >= as_utc(enrolled_at).astimezone(VN_TZ).date()


def attendance_status(record: Optional[dict]) -> Optional[str]:
    # Older attendance documents did not store a status; an existing record
    # represented a successful check-in.
    return record.get("status", "present") if record is not None else None


def is_session_assessed(session: dict, record: Optional[dict] = None) -> bool:
    return (session.get("is_active") is False or session.get("ended_at") is not None
            or attendance_status(record) in ATTENDED_STATUSES)
