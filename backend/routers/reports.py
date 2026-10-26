"""Attendance reports using the same eligible sessions for every metric."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.attendance_policy import (
    ATTENDED_STATUSES, VN_TZ, as_utc, attendance_status,
    is_session_assessed, session_applies_to_person, session_local_day,
)
from core.auth import require_operator
from core.database import get_db
from core.schemas import DailyAttendanceStat, PersonAttendanceStat

router = APIRouter()

class ReportPeriod:
    def __init__(self, dates, persons, sessions, attendance):
        self.dates = dates
        self.persons = persons
        self.sessions = sessions
        self.attendance = attendance

    def assessed(self, person):
        """Yield applicable sessions only after closure or a successful check-in."""
        for session in self.sessions:
            record = self.attendance.get((str(person["_id"]), str(session["_id"])))
            if session_applies_to_person(session, person) and is_session_assessed(session, record):
                yield session, attendance_status(record)


async def _load_period(db, days: int, department: Optional[str]) -> ReportPeriod:
    today = datetime.now(VN_TZ).date()
    dates = [(today - timedelta(days=days - index - 1)).isoformat() for index in range(days)]
    since = datetime.combine(today - timedelta(days=days - 1), datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)
    until = datetime.combine(today + timedelta(days=1), datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)
    person_query = {"is_active": True}
    session_query = {"started_at": {"$gte": since, "$lt": until}}
    if department and department.strip():
        dept = {"$regex": rf"^\s*{re.escape(department.strip())}\s*$", "$options": "i"}
        person_query["department"] = dept
        session_query["$or"] = [
            {"department": dept}, {"department": None},
            {"department": {"$regex": r"^\s*$"}},
        ]
    sessions = [doc async for doc in db.sessions.find(session_query, {
        "_id": 1, "department": 1, "started_at": 1, "ended_at": 1, "is_active": 1, "roster_ids": 1,
    })]
    historical_ids = list({pid for session in sessions for pid in session.get("roster_ids", [])})
    if historical_ids:
        person_query = {"$or": [person_query, {"_id": {"$in": historical_ids}}]}
    persons = [doc async for doc in db.persons.find(person_query, {
        "_id": 1, "name": 1, "department": 1, "enrolled_at": 1,
    }).sort("name", 1)]
    attendance = {}
    if persons and sessions:
        # Some older documents use string session ids instead of ObjectId.
        session_ids = list({value for session in sessions for value in (session["_id"], str(session["_id"]))})
        person_ids = list({value for person in persons for value in (person["_id"], str(person["_id"]))})
        query = {"session_id": {"$in": session_ids}, "person_id": {"$in": person_ids}}
        async for record in db.attendance.find(query, {
            "_id": 1, "person_id": 1, "session_id": 1, "status": 1, "marked_at": 1,
        }):
            key = (str(record["person_id"]), str(record["session_id"]))
            previous = attendance.get(key)
            # Resolve mixed-id legacy duplicates by timestamp, then id, so the
            # numerator and status are independent of cursor order.
            if previous is None or _record_order(record) > _record_order(previous):
                attendance[key] = record
    return ReportPeriod(dates, persons, sessions, attendance)


def _record_order(record):
    return (as_utc(record.get("marked_at") or datetime.min), str(record.get("_id", "")))


@router.get("/daily", response_model=List[DailyAttendanceStat], dependencies=[Depends(require_operator)])
async def daily_stats(
    days: int = Query(30, ge=1, le=365),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    period = await _load_period(db, days, department)
    present = defaultdict(int)
    opportunities = defaultdict(int)
    assessed_sessions = defaultdict(set)
    # Closed sessions remain visible even if no current profile applies.
    for session in period.sessions:
        if is_session_assessed(session):
            assessed_sessions[session_local_day(session).isoformat()].add(str(session["_id"]))
    for person in period.persons:
        for session, status in period.assessed(person):
            day = session_local_day(session).isoformat()
            assessed_sessions[day].add(str(session["_id"]))
            opportunities[day] += 1
            present[day] += status in ATTENDED_STATUSES
    return [DailyAttendanceStat(
        date=day, total_sessions=len(assessed_sessions[day]), total_present=present[day],
        attendance_rate=round(100 * present[day] / opportunities[day], 1) if opportunities[day] else 0.0,
    ) for day in period.dates]


@router.get("/persons", response_model=List[PersonAttendanceStat], dependencies=[Depends(require_operator)])
async def person_stats(
    days: int = Query(30, ge=1, le=365),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    period = await _load_period(db, days, department)
    stats = []
    for person in period.persons:
        statuses = [status for _, status in period.assessed(person)]
        total = len(statuses)
        present = sum(status in ATTENDED_STATUSES for status in statuses)
        rate = round(100 * present / total, 1) if total else 0.0
        stats.append(PersonAttendanceStat(
            person_id=str(person["_id"]), name=person["name"], department=person.get("department"),
            total_sessions=total, present_count=present, attendance_rate=rate,
            is_defaulter=total > 0 and rate < 75.0,
        ))
    return sorted(stats, key=lambda stat: stat.attendance_rate)


@router.get("/heatmap", dependencies=[Depends(require_operator)])
async def heatmap(
    days: int = Query(14, ge=1, le=60),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    period = await _load_period(db, days, department)
    persons = []
    for person in period.persons:
        per_day = defaultdict(list)
        for session, status in period.assessed(person):
            per_day[session_local_day(session).isoformat()].append(status in ATTENDED_STATUSES)
        persons.append({
            "person_id": str(person["_id"]), "name": person["name"],
            "department": person.get("department"),
            # Missing any assessed session makes a day absent. No applicable
            # assessed session is neutral, including an unmarked open session.
            "data": [int(all(per_day[day])) if per_day[day] else None for day in period.dates],
        })
    return {"dates": period.dates, "persons": persons}
