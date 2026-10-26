"""
routers/sessions.py - MongoDB version
"""

from datetime import datetime, UTC
import re
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db, get_write_db
from core.attendance_policy import session_applies_to_person
from core.schemas import SessionCreate, SessionOut
from core.auth import require_operator

router = APIRouter()


def _doc_to_session(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    if "late_after_minutes" not in out or out["late_after_minutes"] is None:
        out["late_after_minutes"] = 15
    return out


def _parse_object_id(session_id: str) -> ObjectId:
    """
    Safely parse a session_id path param into an ObjectId.

    Phase 0 fix: previously `ObjectId(session_id)` was called directly at
    each call site. A malformed ID (typo, bot probe, stale frontend cache)
    raised an uncaught bson.errors.InvalidId, which FastAPI turned into an
    unhandled 500 instead of a clean, informative 4xx.
    """
    try:
        return ObjectId(session_id)
    except (InvalidId, TypeError):
        raise HTTPException(400, f"Invalid session_id format: '{session_id}'.")


@router.get("", response_model=List[SessionOut], dependencies=[Depends(require_operator)])
async def list_sessions(
    active: Optional[bool] = Query(None),
    limit:  int            = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    query = {}
    if active is not None:
        query["is_active"] = active
    docs = []
    async for doc in db.sessions.find(query).sort([("started_at", -1), ("_id", -1)]).skip(offset).limit(limit):
        docs.append(SessionOut(**_doc_to_session(doc)))
    return docs


@router.post(
    "",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator)],
)
async def create_session(
    body: SessionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if body.course_id:
        if not ObjectId.is_valid(body.course_id):
            raise HTTPException(422, "Mã học phần không hợp lệ.")
        course = await db.courses.find_one({"_id": ObjectId(body.course_id)})
        if not course:
            raise HTTPException(404, "Học phần không tồn tại.")
        body.department = course["department"]
    roster_query = {"is_active": True}
    if body.department:
        roster_query["department"] = {"$regex": f"^{re.escape(body.department.strip())}$", "$options": "i"}
    roster_ids = [str(p["_id"]) async for p in db.persons.find(roster_query)]
    doc = {
        "course_id": body.course_id,
        "roster_ids": roster_ids,
        "label":              body.label,
        "department":         body.department,
        "started_at":         datetime.now(UTC),
        "ended_at":           None,
        "is_active":          True,
        "late_after_minutes": body.late_after_minutes if body.late_after_minutes is not None else 15,
    }
    result = await db.sessions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return SessionOut(**_doc_to_session(doc))


@router.get("/{session_id}", response_model=SessionOut, dependencies=[Depends(require_operator)])
async def get_session(session_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    oid = _parse_object_id(session_id)
    doc = await db.sessions.find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Session not found.")
    return SessionOut(**_doc_to_session(doc))


@router.patch(
    "/{session_id}/end",
    response_model=SessionOut,
    dependencies=[Depends(require_operator)],
)
async def end_session(session_id: str, db: AsyncIOMotorDatabase = Depends(get_write_db, scope="function")):
    oid = _parse_object_id(session_id)
    doc = await db.sessions.find_one({"_id": oid})
    if not doc:
        raise HTTPException(404, "Session not found.")
    if not doc.get("is_active"):
        return SessionOut(**_doc_to_session(doc))
    now = datetime.now(UTC)
    await db.sessions.update_one(
        {"_id": oid},
        {"$set": {"ended_at": now, "is_active": False}},
    )
    doc["ended_at"]  = now
    doc["is_active"] = False

    # Automatically mark absent for active students in the session's class/department
    if hasattr(db, "persons") and hasattr(db, "attendance"):
        try:
            person_query: dict = {"is_active": True}
            dept = (doc.get("department") or "").strip()
            if "roster_ids" in doc:
                person_query = {"_id": {"$in": doc["roster_ids"]}}
            elif dept:
                person_query["department"] = {"$regex": f"^{re.escape(dept)}$", "$options": "i"}
            marked_ids = set()
            async for att in db.attendance.find({"session_id": {"$in": [oid, session_id]}}):
                marked_ids.add(att.get("person_id"))
            async for person in db.persons.find(person_query):
                pid = person["_id"]
                if pid not in marked_ids and session_applies_to_person(doc, person):
                    try:
                        await db.attendance.insert_one({
                            "person_id":  pid,
                            "session_id": oid,
                            "marked_at":  now,
                            "confidence": None,
                            "status":     "absent",
                            "marked_by":  "system_auto_close",
                        })
                    except DuplicateKeyError:
                        pass
        except Exception as exc:
            raise HTTPException(503, "Không thể hoàn tất đóng phiên. Vui lòng thử lại.") from exc

    return SessionOut(**_doc_to_session(doc))
