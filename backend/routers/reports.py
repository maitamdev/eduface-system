"""
routers/reports.py - MongoDB version
"""

from datetime import date, datetime, timedelta, timezone
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db
from core.schemas import DailyAttendanceStat, PersonAttendanceStat
from core.auth import require_operator

router = APIRouter()
VN_TZ = timezone(timedelta(hours=7))
ATTENDED_STATUSES = ["present", "late", "excused"]


@router.get("/daily", response_model=List[DailyAttendanceStat], dependencies=[Depends(require_operator)])
async def daily_stats(
    days: int = Query(30, ge=1, le=365),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    today_vn = datetime.now(VN_TZ).date()
    since = datetime.combine(today_vn - timedelta(days=days), datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)

    person_query: dict = {"is_active": True}
    sess_match: dict = {"started_at": {"$gte": since}}
    allowed_person_ids = None
    if department and department.strip():
        dept_regex = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
        person_query["department"] = dept_regex
        sess_match["$or"] = [{"department": dept_regex}, {"department": None}, {"department": ""}]
        allowed_person_ids = [doc["_id"] async for doc in db.persons.find(person_query, {"_id": 1})]

    att_match: dict = {"marked_at": {"$gte": since}, "status": {"$in": ATTENDED_STATUSES}}
    if allowed_person_ids is not None:
        att_match["person_id"] = {"$in": allowed_person_ids}

    # Present counts per day (Vietnam local day +07:00)
    pipeline = [
        {"$match": att_match},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$marked_at", "timezone": "+07:00"}},
            "present": {"$addToSet": "$person_id"},
        }},
    ]
    present_map = {}
    async for doc in db.attendance.aggregate(pipeline):
        present_map[doc["_id"]] = len(doc["present"])

    # Sessions per day (Vietnam local day +07:00)
    sess_pipeline = [
        {"$match": sess_match},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$started_at", "timezone": "+07:00"}},
            "count": {"$sum": 1},
        }},
    ]
    session_map = {}
    async for doc in db.sessions.aggregate(sess_pipeline):
        session_map[doc["_id"]] = doc["count"]

    total_enrolled = await db.persons.count_documents(person_query) or 1

    stats = []
    for i in range(days):
        d = (today_vn - timedelta(days=days - i - 1)).isoformat()
        present = present_map.get(d, 0)
        rate = round((present / total_enrolled) * 100, 1)
        stats.append(DailyAttendanceStat(
            date=d,
            total_sessions=session_map.get(d, 0),
            total_present=present,
            attendance_rate=rate,
        ))
    return stats


@router.get("/persons", response_model=List[PersonAttendanceStat], dependencies=[Depends(require_operator)])
async def person_stats(
    days: int = Query(30, ge=1, le=365),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    today_vn = datetime.now(VN_TZ).date()
    since = datetime.combine(today_vn - timedelta(days=days), datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)

    person_query: dict = {"is_active": True}
    sess_query: dict = {"started_at": {"$gte": since}}
    if department and department.strip():
        dept_regex = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
        person_query["department"] = dept_regex
        sess_query["$or"] = [{"department": dept_regex}, {"department": None}, {"department": ""}]

    total_sessions = await db.sessions.count_documents(sess_query) or 1

    pipeline = [
        {"$match": {"marked_at": {"$gte": since}, "status": {"$in": ATTENDED_STATUSES}}},
        {"$group": {"_id": "$person_id", "present_count": {"$sum": 1}}},
    ]
    present_map = {}
    async for doc in db.attendance.aggregate(pipeline):
        present_map[doc["_id"]] = doc["present_count"]

    stats = []
    async for p in db.persons.find(person_query).sort("name", 1):
        present = present_map.get(p["_id"], 0)
        rate = round((present / total_sessions) * 100, 1)
        stats.append(PersonAttendanceStat(
            person_id=str(p["_id"]),
            name=p["name"],
            department=p.get("department"),
            total_sessions=total_sessions,
            present_count=present,
            attendance_rate=rate,
            is_defaulter=rate < 75.0,
        ))

    return sorted(stats, key=lambda x: x.attendance_rate)


@router.get("/heatmap", dependencies=[Depends(require_operator)])
async def heatmap(
    days: int = Query(14, ge=1, le=60),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    today_vn = datetime.now(VN_TZ).date()
    since = datetime.combine(today_vn - timedelta(days=days), datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)
    date_range = [
        (today_vn - timedelta(days=days - i - 1)).isoformat()
        for i in range(days)
    ]

    person_query: dict = {"is_active": True}
    if department and department.strip():
        person_query["department"] = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}

    pipeline = [
        {"$match": {"marked_at": {"$gte": since}}},
        {"$project": {
            "person_id": 1,
            "status":    1,
            "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$marked_at", "timezone": "+07:00"}},
        }},
    ]
    att_map: dict = {}
    async for doc in db.attendance.aggregate(pipeline):
        att_map.setdefault(doc["person_id"], {})[doc["day"]] = doc["status"]

    persons = []
    async for p in db.persons.find(person_query).sort("name", 1):
        pid = str(p["_id"])
        persons.append({
            "person_id":  pid,
            "name":       p["name"],
            "department": p.get("department"),
            "data": [
                1 if att_map.get(pid, {}).get(d) in ATTENDED_STATUSES else
                0 if d in att_map.get(pid, {}) else None
                for d in date_range
            ],
        })

    return {"dates": date_range, "persons": persons}
