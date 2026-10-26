"""
routers/attendance.py - MongoDB version
"""

import csv
import asyncio
import io
import json
import logging
import os
from datetime import date, datetime, timedelta, timezone, UTC
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError

import base64
from fastapi import (
    APIRouter, Depends, HTTPException, Request, UploadFile, File, Query, status,
    WebSocket, WebSocketDisconnect,
)
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.database import get_db, get_write_db, get_database, person_already_marked, get_person_by_azure_id
from core.schemas import AttendanceOut, ManualAttendancePayload, MarkAttendanceResponse, IdentifyResult
from core import azure_face
from core.auth import require_operator, require_admin, get_user_id_from_request
from core.rate_limit import limiter
from core.validation import read_and_validate_image
from core.audit import record_audit_event
from core.metrics import record_attendance_mark
from core.attendance_policy import session_applies_to_person
from limits import parse as parse_rate_limit
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

logger = logging.getLogger(__name__)
router = APIRouter()
_ws_limiter = FixedWindowRateLimiter(MemoryStorage())
_ws_rate = parse_rate_limit("20/minute")


def _safe_csv_cell(value):
    """Prevent spreadsheet formula evaluation of user-controlled strings."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
        return "'" + value
    return value


def _compute_scan_status(session: dict, now: datetime) -> str:
    """Return 'late' if session has late_after_minutes > 0 and elapsed time exceeds it."""
    late_mins = session.get("late_after_minutes")
    started = session.get("started_at")
    if isinstance(late_mins, (int, float)) and late_mins > 0 and isinstance(started, datetime):
        started_utc = started if started.tzinfo else started.replace(tzinfo=UTC)
        now_utc = now if now.tzinfo else now.replace(tzinfo=UTC)
        if (now_utc - started_utc).total_seconds() > late_mins * 60:
            return "late"
    return "present"


@router.post(
    "/identify",
    response_model=List[IdentifyResult],
    dependencies=[Depends(require_operator)],
)
@limiter.limit("20/minute")
async def identify_frame(
    request:    Request,
    frame:      UploadFile = File(...),
    confidence: float      = Query(None, ge=0.1, le=1.0),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    image_bytes = await read_and_validate_image(frame)
    try:
        results = await azure_face.identify_faces(image_bytes, confidence)
    except Exception:
        logger.exception("Identify error")
        raise HTTPException(503, "Face recognition service temporarily unavailable.")
    return [IdentifyResult(**r) for r in results]


@router.post(
    "/mark/{session_id}",
    response_model=MarkAttendanceResponse,
    dependencies=[Depends(require_operator)],
)
@limiter.limit("20/minute")
async def mark_attendance(
    request:     Request,
    session_id:  str,
    frame:       UploadFile           = File(...),
    probe_frame: Optional[UploadFile] = File(None),
    confidence:  float                = Query(None, ge=0.1, le=1.0),
    db: AsyncIOMotorDatabase          = Depends(get_write_db, scope="function"),
):
    try:
        session_oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        raise HTTPException(400, f"Invalid session_id format: '{session_id}'.")

    session = await db.sessions.find_one({"_id": session_oid, "is_active": True})
    if not session:
        raise HTTPException(404, "Active session not found.")

    if probe_frame is None:
        raise HTTPException(422, "Điểm danh cần hai khung hình camera để kiểm tra chuyển động.")
    image_bytes = await read_and_validate_image(frame)
    probe_bytes = await read_and_validate_image(probe_frame) if probe_frame is not None else None
    try:
        raw_results = await azure_face.identify_faces(image_bytes, confidence, probe_image_bytes=probe_bytes)
    except Exception:
        logger.exception("Identify error during mark")
        raise HTTPException(503, "Face recognition service temporarily unavailable.")

    gate = await db.sessions.update_one({"_id": session_oid, "is_active": True}, {"$inc": {"attendance_revision": 1}})
    if gate.matched_count == 0:
        raise HTTPException(409, "Phiên đã đóng trong lúc nhận diện. Vui lòng tải lại.")
    identified: List[IdentifyResult] = []
    new_records = 0

    for r in raw_results:
        person = await get_person_by_azure_id(db, r["azure_person_id"])
        if not person:
            logger.warning("Azure person %s not in DB — skipping.", r["azure_person_id"])
            continue

        if not session_applies_to_person(session, person):
            record_attendance_mark("rejected")
            continue
        is_live = bool(r.get("is_live", False))
        already = await person_already_marked(db, person["_id"], session_oid)

        if not is_live:
            record_attendance_mark("rejected")
            logger.warning(
                "Spoof attempt blocked for person=%s (%s): %s",
                person["_id"], r["name"], r.get("spoof_reason"),
            )
            identified.append(IdentifyResult(
                azure_person_id=r["azure_person_id"],
                name=r["name"],
                confidence=r["confidence"],
                face_box=r["face_box"],
                already_marked=already,
                is_live=False,
                liveness_score=r.get("liveness_score"),
                spoof_reason=r.get("spoof_reason") or "Phát hiện nghi vấn ảnh giả / màn hình điện thoại",
            ))
            continue

        if not already:
            try:
                user_id = get_user_id_from_request(request)
                now_utc = datetime.now(UTC)
                scan_status = _compute_scan_status(session, now_utc)
                att_doc = {
                    "person_id":  person["_id"],
                    "session_id": session_oid,
                    "marked_at":  now_utc,
                    "confidence": r["confidence"],
                    "status":     scan_status,
                }
                if user_id:
                    att_doc["marked_by"] = user_id
                await db.attendance.insert_one(att_doc)
                new_records += 1
                record_attendance_mark("new")
                await record_audit_event(
                    action="MARK_ATTENDANCE",
                    actor_id=user_id or "operator",
                    actor_role="operator",
                    ip_address=request.client.host if request.client else "unknown",
                    target_id=str(person["_id"]),
                    metadata={"session_id": session_id, "confidence": r["confidence"]},
                )
            except DuplicateKeyError:
                record_attendance_mark("duplicate")
                logger.info(
                    "Duplicate attendance mark ignored for person=%s session=%s",
                    person["_id"], session_id,
                )
        else:
            record_attendance_mark("duplicate")

        identified.append(IdentifyResult(
            azure_person_id=r["azure_person_id"],
            name=r["name"],
            confidence=r["confidence"],
            face_box=r["face_box"],
            already_marked=already,
            is_live=True,
            liveness_score=r.get("liveness_score"),
            spoof_reason=None,
        ))

    return MarkAttendanceResponse(
        session_id=session_id,
        identified=identified,
        new_records=new_records,
    )


@router.get("", response_model=List[AttendanceOut], dependencies=[Depends(require_operator)])
async def list_attendance(
    session_id:    Optional[str]  = Query(None),
    person_id:     Optional[str]  = Query(None),
    date_filter:   Optional[date] = Query(None, alias="date"),
    status_filter: Optional[str]  = Query(None, alias="status"),
    limit:         int            = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase      = Depends(get_db),
):
    match: dict = {}
    if session_id:
        try:
            match["session_id"] = {"$in": [ObjectId(session_id), session_id]}
        except (InvalidId, TypeError):
            raise HTTPException(400, f"Invalid session_id format: '{session_id}'.")
    if person_id:
        match["person_id"] = person_id
    if date_filter:
        vn_tz     = timezone(timedelta(hours=7))
        day_start = datetime.combine(date_filter, datetime.min.time(), tzinfo=vn_tz).astimezone(UTC)
        day_end   = day_start + timedelta(days=1)
        match["marked_at"] = {"$gte": day_start, "$lt": day_end}
    if status_filter:
        match["status"] = status_filter

    pipeline = [
        {"$match": match},
        {"$sort": {"marked_at": -1, "_id": -1}},
        # persons._id is a string UUID — direct match works
        {"$lookup": {"from": "persons", "localField": "person_id", "foreignField": "_id", "as": "person"}},
        {"$set": {"session_oid": {"$convert": {"input": "$session_id", "to": "objectId", "onError": None, "onNull": None}}}},
        {"$lookup": {"from": "sessions", "localField": "session_oid", "foreignField": "_id", "as": "session"}},
        {"$unwind": "$person"},
        {"$unwind": "$session"},
    ]
    if department:
        import re
        pipeline.append({"$match": {"person.department": {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}}})
    pipeline.extend([{"$skip": offset}, {"$limit": limit}])

    rows = []
    async for doc in db.attendance.aggregate(pipeline):
        rows.append(AttendanceOut(
            id=str(doc["_id"]),
            person_id=doc["person_id"],
            person_name=doc["person"]["name"],
            student_id=doc["person"].get("student_id"),
            department=doc["person"].get("department"),
            session_id=str(doc["session_id"]),
            session_label=doc["session"]["label"],
            marked_at=doc["marked_at"],
            confidence=doc.get("confidence"),
            status=doc["status"],
            marked_by=doc.get("marked_by"),
        ))
    return rows


@router.put("/manual", response_model=AttendanceOut, dependencies=[Depends(require_operator)])
async def set_manual_attendance(
    request: Request,
    body: ManualAttendancePayload,
    db: AsyncIOMotorDatabase = Depends(get_write_db, scope="function"),
):
    """Cho phép Giảng viên hoặc Admin điểm danh thủ công / đổi trạng thái (present, late, excused, absent)."""
    try:
        session_oid = ObjectId(body.session_id)
    except (InvalidId, TypeError):
        raise HTTPException(400, f"Invalid session_id format: '{body.session_id}'.")

    session = await db.sessions.find_one({"_id": session_oid})
    if not session:
        raise HTTPException(404, "Session not found.")

    person = await db.persons.find_one({"_id": body.person_id, "is_active": True})
    if not person:
        raise HTTPException(404, "Person not found.")

    if not session_applies_to_person(session, person):
        raise HTTPException(422, "Sinh viên không thuộc danh sách của phiên này.")
    now_utc = datetime.now(UTC)
    user_id = get_user_id_from_request(request) or "manual"
    existing = await db.attendance.find_one({"person_id": body.person_id, "session_id": {"$in": [session_oid, str(session_oid)]}})

    if existing:
        await db.attendance.update_one(
            {"_id": existing["_id"]},
            {"$set": {"status": body.status, "updated_at": now_utc, "updated_by": user_id}},
        )
        att_id = str(existing["_id"])
        conf = existing.get("confidence")
    else:
        res = await db.attendance.insert_one({
            "person_id":  body.person_id,
            "session_id": session_oid,
            "marked_at":  now_utc,
            "confidence": None,
            "status":     body.status,
            "marked_by":  user_id,
        })
        att_id = str(res.inserted_id)
        conf = None

    request.state.audit_metadata = {"before_status": existing.get("status") if existing else None,
                                    "after_status": body.status, "person_id": body.person_id,
                                    "session_id": body.session_id}
    return AttendanceOut(
        id=att_id,
        person_id=body.person_id,
        person_name=person["name"],
        student_id=person.get("student_id"),
        department=person.get("department"),
        session_id=str(session_oid),
        session_label=session["label"],
        marked_at=existing["marked_at"] if existing else now_utc,
        confidence=conf,
        status=body.status,
        marked_by=user_id,
    )


@router.get("/export/csv", dependencies=[Depends(require_operator)])
async def export_csv(
    session_id:  Optional[str]  = Query(None),
    date_filter: Optional[date] = Query(None, alias="date"),
    department:  Optional[str]  = Query(None),
    db: AsyncIOMotorDatabase     = Depends(get_db),
):
    # Iterate stable Mongo cursor with filters applied before streaming; no 10k truncation.
    match = {}
    if session_id:
        if not ObjectId.is_valid(session_id):
            raise HTTPException(422, "Invalid session ID")
        match["session_id"] = {"$in": [ObjectId(session_id), session_id]}
    vn_tz = timezone(timedelta(hours=7))
    if date_filter:
        start = datetime.combine(date_filter, datetime.min.time(), tzinfo=vn_tz).astimezone(UTC)
        match["marked_at"] = {"$gte": start, "$lt": start + timedelta(days=1)}
    pipeline = [{"$match": match}, {"$sort": {"marked_at": -1, "_id": -1}},
                {"$lookup": {"from": "persons", "localField": "person_id", "foreignField": "_id", "as": "person"}},
                {"$set": {"session_oid": {"$convert": {"input": "$session_id", "to": "objectId", "onError": None, "onNull": None}}}},
                {"$lookup": {"from": "sessions", "localField": "session_oid", "foreignField": "_id", "as": "session"}},
                {"$unwind": "$person"}, {"$unwind": "$session"}]
    if department:
        import re
        pipeline.append({"$match": {"person.department": {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}}})
    async def generate():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "student_id", "person_name", "department", "session_label", "marked_at", "confidence", "status"])
        yield "\ufeff" + output.getvalue()
        async for row in db.attendance.aggregate(pipeline):
            output.seek(0); output.truncate(0)
            marked = row["marked_at"]
            marked = marked if marked.tzinfo else marked.replace(tzinfo=UTC)
            values = [str(row["_id"]), row["person"].get("student_id", ""), row["person"]["name"],
                      row["person"].get("department", ""), row["session"]["label"],
                      marked.astimezone(vn_tz).isoformat(), row.get("confidence", ""), row.get("status", "present")]
            writer.writerow([_safe_csv_cell(v) for v in values])
            yield output.getvalue()
    return StreamingResponse(generate(), media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename=attendance_{datetime.now(vn_tz).date()}.csv"})


# ── Real-Time Streaming WebSocket ─────────────────────────────────────────────

@router.websocket("/ws/{session_id}")
async def attendance_websocket(
    websocket: WebSocket,
    session_id: str,
):
    """
    Real-time persistent bi-directional streaming endpoint for camera feeds.
    Accepts raw binary JPEG/WebP frames or base64 data URLs.
    Returns recognition bounding boxes and match status without HTTP overhead.
    """
    from core.origins import allowed_origins as resolve_origins
    allowed_origins = set(resolve_origins())
    origin = websocket.headers.get("origin")
    if origin and origin not in allowed_origins:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    db = get_database()
    # Browser WebSockets cannot set Authorization headers. Authenticate the
    # first message instead; credentials must never appear in URL/access logs.
    try:
        raw_auth = await asyncio.wait_for(websocket.receive_text(), timeout=10)
        if len(raw_auth) > 4096:
            raise ValueError("Authentication message too large")
        auth = json.loads(raw_auth)
        if not isinstance(auth, dict) or auth.get("type") != "auth":
            raise ValueError("Authentication required")
        await require_operator(
            request=websocket,
            x_api_key=auth.get("api_key", ""),
            authorization=auth.get("authorization"),
            db=db,
        )
        confidence = float(auth.get("confidence", 0.4))
        if not 0.1 <= confidence <= 1.0:
            raise ValueError("Invalid confidence")
    except (HTTPException, ValueError, TypeError, asyncio.TimeoutError, WebSocketDisconnect):
        await websocket.close(code=1008)
        return
    try:
        session_oid = ObjectId(session_id)
        session = await db.sessions.find_one({"_id": session_oid, "is_active": True})
        if not session:
            await websocket.send_json({"error": "Active session not found", "status": 404})
            await websocket.close()
            return
    except Exception:
        await websocket.send_json({"error": "Invalid session identifier", "status": 400})
        await websocket.close()
        return

    await websocket.send_json({"status": 200, "message": "Authenticated"})
    try:
        while True:
            data = await websocket.receive()
            if data["type"] == "websocket.disconnect":
                break
            # Recheck expiry, password reset, deactivation, and role changes
            # before every recognition frame, including on long-lived sockets.
            try:
                await require_operator(
                    request=websocket,
                    x_api_key=auth.get("api_key", ""),
                    authorization=auth.get("authorization"),
                    db=db,
                )
            except HTTPException:
                await websocket.close(code=1008)
                break
            if not _ws_limiter.hit(_ws_rate, websocket.client.host if websocket.client else "unknown"):
                await websocket.send_json({"error": "Recognition rate limit exceeded", "status": 429})
                await websocket.close(code=1008)
                break
            image_bytes = None
            if "bytes" in data and data["bytes"]:
                image_bytes = data["bytes"]
            elif "text" in data and data["text"]:
                raw_text = data["text"].strip()
                if len(raw_text) > 14 * 1024 * 1024:
                    await websocket.close(code=1009)
                    break
                if "," in raw_text:
                    raw_text = raw_text.split(",", 1)[1]
                try:
                    image_bytes = base64.b64decode(raw_text, validate=True)
                except ValueError:
                    await websocket.send_json({"error": "Invalid image encoding", "status": 400})
                    continue

            if not image_bytes:
                continue

            try:
                image_bytes = await read_and_validate_image(UploadFile(
                    filename="frame.jpg", file=io.BytesIO(image_bytes),
                    headers={"content-type": "image/jpeg"},
                ))
            except HTTPException:
                await websocket.send_json({"error": "Invalid image or image exceeds allowed limits", "status": 400})
                continue
            results = await azure_face.identify_faces(image_bytes, confidence)
            await websocket.send_json({
                "timestamp": datetime.now(UTC).isoformat(),
                "session_id": session_id,
                "matches": results,
                "faces_detected": len(results),
            })
    except WebSocketDisconnect:
        logger.info("Live WebSocket stream disconnected for session %s", session_id)
    except Exception as e:
        logger.warning("WebSocket live stream exception: %s", e)
        try:
            await websocket.close()
        except Exception:
            pass
