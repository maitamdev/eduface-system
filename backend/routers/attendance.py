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

from core.database import get_db, get_database, person_already_marked, get_person_by_azure_id
from core.schemas import AttendanceOut, MarkAttendanceResponse, IdentifyResult
from core import azure_face
from core.auth import require_operator, require_admin, get_user_id_from_request
from core.rate_limit import limiter
from core.validation import read_and_validate_image
from core.audit import record_audit_event
from core.metrics import record_attendance_mark
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


@router.post(
    "/identify",
    response_model=List[IdentifyResult],
    dependencies=[Depends(require_operator)],
)
@limiter.limit("20/minute")
async def identify_frame(
    request:    Request,
    frame:      UploadFile = File(...),
    confidence: float      = Query(0.40, ge=0.1, le=1.0),
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
    request:    Request,
    session_id: str,
    frame:      UploadFile = File(...),
    confidence: float      = Query(0.40, ge=0.1, le=1.0),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        session_oid = ObjectId(session_id)
    except (InvalidId, TypeError):
        raise HTTPException(400, f"Invalid session_id format: '{session_id}'.")

    session = await db.sessions.find_one({"_id": session_oid, "is_active": True})
    if not session:
        raise HTTPException(404, "Active session not found.")

    image_bytes = await read_and_validate_image(frame)
    try:
        raw_results = await azure_face.identify_faces(image_bytes, confidence)
    except Exception:
        logger.exception("Identify error during mark")
        raise HTTPException(503, "Face recognition service temporarily unavailable.")

    identified: List[IdentifyResult] = []
    new_records = 0

    for r in raw_results:
        person = await get_person_by_azure_id(db, r["azure_person_id"])
        if not person:
            logger.warning("Azure person %s not in DB — skipping.", r["azure_person_id"])
            continue

        already = await person_already_marked(db, person["_id"], session_oid)

        if not already:
            try:
                user_id = get_user_id_from_request(request)
                att_doc = {
                    "person_id":  person["_id"],
                    "session_id": session_oid,
                    "marked_at":  datetime.now(UTC),
                    "confidence": r["confidence"],
                    "status":     "present",
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
    limit:         int            = Query(200, le=1000),
    db: AsyncIOMotorDatabase      = Depends(get_db),
):
    match: dict = {}
    if session_id:
        try:
            match["session_id"] = ObjectId(session_id)
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
        {"$sort": {"marked_at": -1}},
        {"$limit": limit},
        # persons._id is a string UUID — direct match works
        {"$lookup": {"from": "persons", "localField": "person_id", "foreignField": "_id", "as": "person"}},
        # sessions._id is an ObjectId and attendance.session_id is stored as ObjectId
        {"$lookup": {"from": "sessions", "localField": "session_id", "foreignField": "_id", "as": "session"}},
        {"$unwind": "$person"},
        {"$unwind": "$session"},
    ]

    rows = []
    async for doc in db.attendance.aggregate(pipeline):
        rows.append(AttendanceOut(
            id=str(doc["_id"]),
            person_id=doc["person_id"],
            person_name=doc["person"]["name"],
            department=doc["person"].get("department"),
            session_id=str(doc["session_id"]),
            session_label=doc["session"]["label"],
            marked_at=doc["marked_at"],
            confidence=doc.get("confidence"),
            status=doc["status"],
            marked_by=doc.get("marked_by"),
        ))
    return rows


@router.get("/export/csv", dependencies=[Depends(require_admin)])
async def export_csv(
    session_id:  Optional[str]  = Query(None),
    date_filter: Optional[date] = Query(None, alias="date"),
    db: AsyncIOMotorDatabase     = Depends(get_db),
):
    records = await list_attendance(
        session_id=session_id, person_id=None,
        date_filter=date_filter, status_filter=None,
        limit=10000, db=db,
    )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "person_name", "department", "session_label",
        "marked_at", "confidence", "status"
    ])
    writer.writeheader()
    vn_tz = timezone(timedelta(hours=7))
    for r in records:
        marked_dt = r.marked_at if r.marked_at.tzinfo else r.marked_at.replace(tzinfo=UTC)
        marked_vn = marked_dt.astimezone(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow({key: _safe_csv_cell(value) for key, value in {
            "id":            r.id,
            "person_name":   r.person_name,
            "department":    r.department or "",
            "session_label": r.session_label,
            "marked_at":     marked_vn,
            "confidence":    r.confidence if r.confidence is not None else "",
            "status":        r.status,
        }.items()})
    output.seek(0)
    filename = f"attendance_{datetime.now(vn_tz).date().isoformat()}.csv"
    return StreamingResponse(
        iter(["\ufeff" + output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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
    allowed_origins = {
        "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080",
        "https://ai-attendance-system-mauve.vercel.app",
        *(origin.strip() for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",") if origin.strip()),
    }
    origin = websocket.headers.get("origin")
    if origin and origin not in allowed_origins:
        await websocket.close(code=1008)
        return
    await websocket.accept()
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
        )
        confidence = float(auth.get("confidence", 0.4))
        if not 0.1 <= confidence <= 1.0:
            raise ValueError("Invalid confidence")
    except (HTTPException, ValueError, TypeError, asyncio.TimeoutError, WebSocketDisconnect):
        await websocket.close(code=1008)
        return
    db = get_database()
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
