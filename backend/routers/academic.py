"""
routers/academic.py
Hệ thống Quản trị Sinh viên & Học vụ Toàn diện (EduFace Academic Management Suite):
  1. Quản lý Học phần & Thời khóa biểu (Courses & Schedules)
  2. Quản lý Điểm số, Điểm Chuyên cần AI Tự động, GPA hệ 4 & Xét Điều kiện Dự thi (Grades & GPA)
  3. Cổng Đơn xin nghỉ phép trực tuyến & Tự động đồng bộ Vắng có phép (Online Leave Requests)
  4. Bảng Thông báo Học vụ & Lớp học (Class Announcements)
  5. Nhập danh sách Sinh viên hàng loạt & Tự động cấp tài khoản (Bulk Student Import)
"""

import re
import secrets
import asyncio
import uuid
from datetime import date, datetime, UTC
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from core.auth import (
    AuthenticatedUser,
    get_user_id_from_request,
    hash_password,
    require_authenticated,
    require_operator,
)
from core.database import get_db, get_write_db
from core.attendance_policy import (
    ATTENDED_STATUSES,
    attendance_status,
    is_session_assessed,
    session_applies_to_person,
    session_local_day,
)
from core.schemas import (
    AnnouncementCreate,
    AnnouncementOut,
    BulkStudentImportPayload,
    CourseCreate,
    CourseOut,
    GradeUpsert,
    LeaveRequestCreate,
    LeaveRequestDecision,
    LeaveRequestOut,
    StudentGradeRow,
)

router = APIRouter()


async def _linked_person_id(db, user) -> Optional[str]:
    """Use the administrator's explicit link, never a query, name or email guess."""
    if not isinstance(user, AuthenticatedUser) or user.auth_type != "jwt" or not ObjectId.is_valid(user.id):
        return None
    account = await db.users.find_one({"_id": ObjectId(user.id), "is_active": True})
    return account.get("person_id") if account else None


def _iso_leave_date(value: str) -> str:
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            raise ValueError
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError:
        raise HTTPException(422, "Ngày nghỉ phải có định dạng YYYY-MM-DD và là ngày hợp lệ.")


async def _leave_session(db, session_id: str, person: dict, leave_date: str) -> dict:
    if not ObjectId.is_valid(session_id):
        raise HTTPException(422, "Mã phiên điểm danh không hợp lệ.")
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(404, "Không tìm thấy phiên điểm danh.")
    if not session_applies_to_person(session, person):
        raise HTTPException(422, "Phiên điểm danh không thuộc lớp hoặc thời gian học của sinh viên.")
    session_day = session_local_day(session)
    if session_day is None or session_day.isoformat() != leave_date:
        raise HTTPException(422, "Ngày nghỉ phải trùng ngày của phiên điểm danh.")
    return session


async def _approve_leave_attendance(db, doc: dict, session: dict, reviewer: str, now: datetime):
    """Excuse an absence without downgrading a real scan or a manual attendance mark."""
    sid = session["_id"]
    query = {"person_id": doc["person_id"], "session_id": {"$in": [sid, str(sid)]}}
    existing = await db.attendance.find_one(query)
    fields = {
        "status": "excused", "marked_at": now, "marked_by": reviewer,
        "person_name": doc["person_name"], "student_id": doc.get("student_id"),
        "department": doc.get("department") or session.get("department"),
        "session_label": session.get("label", ""), "leave_request_id": str(doc["_id"]),
    }
    if existing:
        if attendance_status(existing) == "absent":
            await db.attendance.update_one(
                {"_id": existing["_id"], "status": "absent"}, {"$set": fields},
            )
        return
    try:
        await db.attendance.update_one(
            {"person_id": doc["person_id"], "session_id": sid},
            {"$setOnInsert": {**fields, "person_id": doc["person_id"], "session_id": sid, "confidence": None}},
            upsert=True,
        )
    except DuplicateKeyError:
        # A scanner won the unique person/session insert race; retain its mark.
        return


def _score_to_gpa_and_letter(total_10: Optional[float]) -> tuple[Optional[float], Optional[str]]:
    if total_10 is None:
        return None, None
    if total_10 >= 8.5:
        return 4.0, "A"
    if total_10 >= 8.0:
        return 3.5, "B+"
    if total_10 >= 7.0:
        return 3.0, "B"
    if total_10 >= 6.5:
        return 2.5, "C+"
    if total_10 >= 5.5:
        return 2.0, "C"
    if total_10 >= 5.0:
        return 1.5, "D+"
    if total_10 >= 4.0:
        return 1.0, "D"
    return 0.0, "F"


async def _compute_student_grade_rows(
    db: AsyncIOMotorDatabase,
    department: Optional[str] = None,
    person_id_filter: Optional[str] = None,
    course_id: Optional[str] = None,
) -> List[StudentGradeRow]:
    course = None
    if course_id:
        if not ObjectId.is_valid(course_id):
            raise HTTPException(422, "Mã học phần không hợp lệ.")
        course = await db.courses.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(404, "Không tìm thấy học phần.")
        department = course["department"]
    person_query: dict = {"is_active": True}
    if department and department.strip():
        person_query["department"] = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
    if person_id_filter:
        person_query["_id"] = person_id_filter

    all_sessions = await db.sessions.find({"course_id": course_id} if course_id else {"course_id": None}).to_list(length=None)
    historical_ids = {pid for session in all_sessions for pid in session.get("roster_ids", [])}
    if course_id:
        historical_ids.update([g["person_id"] async for g in db.grades.find({"course_id": course_id})])
    if historical_ids:
        person_query = {"$or": [person_query, {"_id": {"$in": list(historical_ids)}}]}
    if person_id_filter and historical_ids:
        person_query = {"$and": [person_query, {"_id": person_id_filter}]}
    persons = await db.persons.find(person_query).sort("name", 1).to_list(length=None)
    if not persons:
        return []

    person_ids = [p["_id"] for p in persons]

    att_records = await db.attendance.find({"person_id": {"$in": person_ids}}).to_list(length=None)
    records_by_person: dict[str, dict[str, dict]] = {pid: {} for pid in person_ids}
    for rec in att_records:
        pid = rec.get("person_id")
        if pid in records_by_person:
            records_by_person[pid][str(rec.get("session_id"))] = rec

    grades_docs = {}
    if hasattr(db, "grades"):
        async for gdoc in db.grades.find({"person_id": {"$in": person_ids}, "course_id": course_id}):
            grades_docs[gdoc["person_id"]] = gdoc

    rows: List[StudentGradeRow] = []
    for p in persons:
        pid = p["_id"]
        matching_sids = set()
        records = records_by_person.get(pid, {})
        for s in all_sessions:
            sid = str(s["_id"])
            if session_applies_to_person(s, p) and is_session_assessed(s, records.get(sid)):
                matching_sids.add(sid)

        total_sess = len(matching_sids)
        present_cnt = sum(attendance_status(records.get(sid)) in ATTENDED_STATUSES for sid in matching_sids)
        rate = round(present_cnt / total_sess * 100, 1) if total_sess > 0 else 100.0
        att_score = round(rate / 10.0, 1)
        eligible = (total_sess == 0) or (rate >= 75.0)

        gdoc = grades_docs.get(pid, {})
        midterm = gdoc.get("midterm_score")
        final = gdoc.get("final_score")
        bonus = float(gdoc.get("bonus_score") or 0.0)
        note = gdoc.get("note")

        total_10: Optional[float] = None
        if midterm is not None and final is not None:
            raw_total = 0.10 * att_score + 0.30 * float(midterm) + 0.60 * float(final) + bonus
            total_10 = round(min(10.0, max(0.0, raw_total)), 2)

        gpa_4, letter = _score_to_gpa_and_letter(total_10)

        rows.append(
            StudentGradeRow(
                person_id=pid,
                course_id=course_id,
                course_name=course.get("name") if course else None,
                semester=course.get("semester") if course else None,
                credits=course.get("credits", 0) if course else 0,
                name=p["name"],
                student_id=p.get("student_id"),
                department=p.get("department"),
                total_sessions=total_sess,
                present_count=present_cnt,
                attendance_rate=rate,
                attendance_score=att_score,
                midterm_score=midterm,
                final_score=final,
                bonus_score=bonus,
                total_10=total_10,
                gpa_4=gpa_4,
                letter_grade=letter,
                exam_eligible=eligible,
                note=note,
            )
        )
    return rows


# ── 1. Courses & Class Schedules ─────────────────────────────────────────────

@router.get("/courses", response_model=List[CourseOut], dependencies=[Depends(require_authenticated)])
async def list_courses(
    request: Request,
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not hasattr(db, "courses"):
        return []
    user = getattr(request.state, "user", None)
    query: dict = {}
    if isinstance(user, AuthenticatedUser) and user.role == "student":
        linked_pid = await _linked_person_id(db, user)
        person = await db.persons.find_one({"_id": linked_pid, "is_active": True}) if linked_pid else None
        if not person:
            return []
        department = (person.get("department") or "").strip()
        historical = set()
        for collection, match in [(db.grades, {"person_id": linked_pid}), (db.sessions, {"roster_ids": linked_pid})]:
            async for item in collection.find(match):
                cid = item.get("course_id")
                if cid and ObjectId.is_valid(cid): historical.add(ObjectId(cid))
        clauses = [{"_id": {"$in": list(historical)}}]
        if department: clauses.append({"department": {"$regex": f"^{re.escape(department)}$", "$options": "i"}})
        query = {"$or": clauses}
    elif department and department.strip():
        query["department"] = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
    docs = []
    async for doc in db.courses.find(query).sort("code", 1):
        doc["id"] = str(doc.pop("_id"))
        docs.append(CourseOut(**doc))
    return docs


@router.post(
    "/courses",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator)],
)
async def create_course(body: CourseCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_code = body.code.strip().upper()
    existing = await db.courses.find_one({"code": clean_code, "department": body.department.strip(), "semester": (body.semester or "HK1 2026-2027").strip()})
    if existing:
        raise HTTPException(409, f"Mã học phần '{clean_code}' đã tồn tại.")
    doc = {
        "code":       clean_code,
        "name":       body.name.strip(),
        "department": body.department.strip(),
        "credits":    body.credits,
        "lecturer":   (body.lecturer or "").strip() or None,
        "schedule":   (body.schedule or "").strip() or None,
        "room":       (body.room or "").strip() or None,
        "semester":   (body.semester or "HK1 2026-2027").strip(),
        "created_at": datetime.now(UTC),
    }
    res = await db.courses.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return CourseOut(**doc)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_operator)])
async def delete_course(course_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not ObjectId.is_valid(course_id):
        raise HTTPException(404, "Course not found.")
    if await db.grades.find_one({"course_id": course_id}) or await db.sessions.find_one({"course_id": course_id}):
        raise HTTPException(409, "Học phần đã có điểm hoặc phiên điểm danh. Không thể xóa lịch sử.")
    res = await db.courses.delete_one({"_id": ObjectId(course_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Course not found.")


# ── 2. Grades, GPA & Exam Eligibility ────────────────────────────────────────

@router.get("/grades", response_model=List[StudentGradeRow], dependencies=[Depends(require_operator)])
async def list_grades(
    course_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _compute_student_grade_rows(db, department=department, course_id=course_id)


@router.get("/my-grade", response_model=Optional[StudentGradeRow], dependencies=[Depends(require_authenticated)])
async def get_my_grade(
    request: Request,
    course_id: Optional[str] = Query(None),
    person_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = getattr(request.state, "user", None)
    target_pid = person_id
    if isinstance(user, AuthenticatedUser):
        linked_pid = await _linked_person_id(db, user)
        # A student's ?person_id must never grant access to another grade row.
        target_pid = linked_pid if user.role == "student" else (person_id or linked_pid)
    if not target_pid:
        return None
    rows = await _compute_student_grade_rows(db, person_id_filter=target_pid, course_id=course_id)
    return rows[0] if rows else None


@router.put("/grades", response_model=StudentGradeRow, dependencies=[Depends(require_operator)])
async def upsert_grade(body: GradeUpsert, request: Request, db: AsyncIOMotorDatabase = Depends(get_write_db, scope="function")):
    person = await db.persons.find_one({"_id": body.person_id, "is_active": True})
    if not person:
        raise HTTPException(404, "Không tìm thấy hồ sơ sinh viên.")

    if not body.course_id or not ObjectId.is_valid(body.course_id):
        raise HTTPException(422, "Chọn học phần trước khi nhập điểm. Điểm cũ chỉ được xem lại.")
    course = await db.courses.find_one({"_id": ObjectId(body.course_id)})
    historical_member = await db.sessions.find_one({"course_id": body.course_id, "roster_ids": body.person_id}) or await db.grades.find_one({"person_id": body.person_id, "course_id": body.course_id})
    if not course or (not historical_member and course["department"].strip().casefold() != (person.get("department") or "").strip().casefold()):
        raise HTTPException(422, "Học phần không thuộc lớp của sinh viên.")
    key = {"person_id": body.person_id, "course_id": body.course_id}
    previous = await db.grades.find_one(key)
    request.state.audit_metadata = {"before": {k: v for k, v in (previous or {}).items() if k != "_id"},
                                    "after": body.model_dump()}
    update_doc = {
        "course_id": body.course_id,
        "person_id":     body.person_id,
        "midterm_score": body.midterm_score,
        "final_score":   body.final_score,
        "bonus_score":   body.bonus_score if body.bonus_score is not None else 0.0,
        "note":          (body.note or "").strip() or None,
        "updated_at":    datetime.now(UTC),
    }
    await db.grades.update_one(
        key,
        {"$set": update_doc},
        upsert=True,
    )
    rows = await _compute_student_grade_rows(db, person_id_filter=body.person_id, course_id=body.course_id)
    if not rows:
        raise HTTPException(404, "Không thể tính điểm cho sinh viên này.")
    return rows[0]


# ── 3. Online Leave Requests (Đơn xin nghỉ phép) ──────────────────────────────

@router.get("/leaves", response_model=List[LeaveRequestOut], dependencies=[Depends(require_authenticated)])
async def list_leave_requests(
    request: Request,
    department: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not hasattr(db, "leave_requests"):
        return []
    user = getattr(request.state, "user", None)
    query: dict = {}
    if isinstance(user, AuthenticatedUser) and user.role == "student":
        linked_pid = await _linked_person_id(db, user)
        if linked_pid:
            query["person_id"] = linked_pid
        else:
            return []
    else:
        if department and department.strip():
            query["department"] = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
        if status_filter and status_filter.strip():
            query["status"] = status_filter.strip()

    docs = []
    async for doc in db.leave_requests.find(query).sort("created_at", -1).limit(200):
        doc["id"] = str(doc.pop("_id"))
        docs.append(LeaveRequestOut(**doc))
    return docs


@router.post(
    "/leaves",
    response_model=LeaveRequestOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_authenticated)],
)
async def create_leave_request(
    request: Request,
    body: LeaveRequestCreate,
    person_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = getattr(request.state, "user", None)
    target_pid = person_id
    if isinstance(user, AuthenticatedUser) and user.role == "student":
        target_pid = await _linked_person_id(db, user)
    if not target_pid and isinstance(user, AuthenticatedUser):
        target_pid = await _linked_person_id(db, user)

    if not target_pid:
        raise HTTPException(400, "Bạn cần đăng ký hồ sơ sinh viên trước khi gửi đơn xin phép.")

    person = await db.persons.find_one({"_id": target_pid, "is_active": True})
    if not person:
        raise HTTPException(404, "Không tìm thấy hồ sơ sinh viên.")

    leave_date = _iso_leave_date(body.leave_date)
    if not body.reason.strip() or len(body.reason.strip()) < 3:
        raise HTTPException(422, "Vui lòng nhập lý do xin nghỉ có ít nhất 3 ký tự.")
    session_label = None
    if body.session_id:
        sess = await _leave_session(db, body.session_id, person, leave_date)
        session_label = sess.get("label")

    doc = {
        "person_id":     target_pid,
        "person_name":   person["name"],
        "student_id":    person.get("student_id"),
        "department":    person.get("department"),
        "session_id":    body.session_id or None,
        "session_label": session_label,
        "leave_date":    leave_date,
        "reason":        body.reason.strip(),
        "evidence_url":  (body.evidence_url or "").strip() or None,
        "status":        "pending",
        "reviewer_note": None,
        "created_at":    datetime.now(UTC),
        "reviewed_at":   None,
    }
    res = await db.leave_requests.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return LeaveRequestOut(**doc)


@router.patch(
    "/leaves/{leave_id}",
    response_model=LeaveRequestOut,
    dependencies=[Depends(require_operator)],
)
async def review_leave_request(
    request: Request,
    leave_id: str,
    body: LeaveRequestDecision,
    db: AsyncIOMotorDatabase = Depends(get_write_db, scope="function"),
):
    if not ObjectId.is_valid(leave_id):
        raise HTTPException(404, "Không tìm thấy đơn xin phép.")
    doc = await db.leave_requests.find_one({"_id": ObjectId(leave_id)})
    if not doc:
        raise HTTPException(404, "Không tìm thấy đơn xin phép.")
    if doc.get("status") != "pending":
        raise HTTPException(409, "Đơn này đã được xét duyệt. Không thể thay đổi quyết định.")

    session = None
    if body.status == "approved" and doc.get("session_id"):
        person = await db.persons.find_one({"_id": doc["person_id"], "is_active": True})
        if not person:
            raise HTTPException(404, "Không tìm thấy hồ sơ sinh viên.")
        session = await _leave_session(db, doc["session_id"], person, _iso_leave_date(doc["leave_date"]))

    now = datetime.now(UTC)
    updates = {
        "status":        body.status,
        "reviewer_note": (body.reviewer_note or "").strip() or None,
        "reviewed_at":   now,
    }
    doc = await db.leave_requests.find_one_and_update(
        {"_id": ObjectId(leave_id), "status": "pending"},
        {"$set": updates}, return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise HTTPException(409, "Đơn này vừa được người khác xét duyệt. Vui lòng tải lại.")

    if session:
        try:
            await _approve_leave_attendance(db, doc, session, get_user_id_from_request(request) or "leave_approved", now)
        except Exception:
            # Keep an unsuccessful database write reviewable on the next attempt.
            await db.leave_requests.update_one(
                {"_id": doc["_id"], "status": "approved", "reviewed_at": now},
                {"$set": {"status": "pending", "reviewer_note": None, "reviewed_at": None}},
            )
            raise

    doc["id"] = str(doc.pop("_id"))
    return LeaveRequestOut(**doc)


# ── 4. Class & Academic Announcements (Bảng thông báo học vụ) ────────────────

@router.get("/announcements", response_model=List[AnnouncementOut], dependencies=[Depends(require_authenticated)])
async def list_announcements(
    request: Request,
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not hasattr(db, "announcements"):
        return []
    user = getattr(request.state, "user", None)
    student = isinstance(user, AuthenticatedUser) and user.role == "student"
    if student:
        linked_pid = await _linked_person_id(db, user)
        person = await db.persons.find_one({"_id": linked_pid, "is_active": True}) if linked_pid else None
        department = (person.get("department") or "").strip() if person else ""
    query: dict = {}
    if student or (department and department.strip()):
        query["$or"] = [{"department": None}, {"department": ""}]
        if department:
            query["$or"].append(
                {"department": {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}},
            )
    docs = []
    async for doc in db.announcements.find(query).sort("created_at", -1).limit(50):
        doc["id"] = str(doc.pop("_id"))
        docs.append(AnnouncementOut(**doc))
    return docs


@router.post(
    "/announcements",
    response_model=AnnouncementOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_operator)],
)
async def create_announcement(
    request: Request,
    body: AnnouncementCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = getattr(request.state, "user", None)
    author = (
        (getattr(user, "display_name", None) or user.username)
        if isinstance(user, AuthenticatedUser)
        else "Giảng viên / Quản trị viên"
    )
    doc = {
        "title":      body.title.strip(),
        "content":    body.content.strip(),
        "department": (body.department or "").strip() or None,
        "priority":   body.priority,
        "author":     author,
        "created_at": datetime.now(UTC),
    }
    res = await db.announcements.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return AnnouncementOut(**doc)


@router.delete(
    "/announcements/{ann_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_operator)],
)
async def delete_announcement(ann_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not ObjectId.is_valid(ann_id):
        raise HTTPException(404, "Announcement not found.")
    res = await db.announcements.delete_one({"_id": ObjectId(ann_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Announcement not found.")


# ── 5. Bulk Student Import (Nhập danh sách sinh viên hàng loạt từ CSV) ───────

@router.post("/import-students", dependencies=[Depends(require_operator)])
async def bulk_import_students(
    request: Request,
    body: BulkStudentImportPayload,
    db: AsyncIOMotorDatabase = Depends(get_write_db, scope="function"),
):
    if not body.students:
        raise HTTPException(400, "Danh sách sinh viên trống.")
    if len(body.students) > 500:
        raise HTTPException(400, "Tối đa 500 sinh viên mỗi lần nhập.")

    # Validate the entire input before changing profiles. A name is not an
    # identity key: matching it could replace another student's face/account.
    planned = []
    seen_ids: set[str] = set()
    new_account_emails: set[str] = set()
    for row in body.students:
        clean_mssv = row.student_id.strip().upper()
        clean_name = row.name.strip()
        clean_dept = row.department.strip()
        if len(clean_mssv) < 2 or len(clean_name) < 2 or not clean_dept:
            raise HTTPException(422, "Mã sinh viên, họ tên và lớp không được để trống.")
        if body.create_login_accounts and len(clean_mssv) < 3:
            raise HTTPException(422, "Mã sinh viên phải có ít nhất 3 ký tự để tạo tài khoản.")
        if clean_mssv in seen_ids:
            raise HTTPException(409, f"Mã sinh viên '{clean_mssv}' bị lặp trong danh sách.")
        seen_ids.add(clean_mssv)
        matches = await db.persons.find({
            "student_id": {"$regex": f"^{re.escape(clean_mssv)}$", "$options": "i"},
            "is_active": True,
        }).to_list(length=2)
        if len(matches) > 1:
            raise HTTPException(409, f"Có nhiều hồ sơ cùng mã '{clean_mssv}'. Vui lòng xử lý trùng trước khi nhập.")
        existing = matches[0] if matches else None
        if body.create_login_accounts:
            account = await db.users.find_one({"username": {"$regex": f"^{re.escape(clean_mssv)}$", "$options": "i"}})
            if account and (not existing or account.get("person_id") != existing["_id"]):
                raise HTTPException(409, f"Tài khoản '{clean_mssv}' đã tồn tại và chưa liên kết đúng hồ sơ. Vui lòng kiểm tra trong quản trị tài khoản.")
            email = (row.email or "").strip().lower()
            if not account and email:
                email_owner = await db.users.find_one({"google_email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}})
                if email in new_account_emails or email_owner:
                    raise HTTPException(409, f"Email '{email}' đã được dùng cho tài khoản khác. Vui lòng kiểm tra trước khi nhập.")
                new_account_emails.add(email)
        planned.append((row, clean_mssv, clean_name, clean_dept, existing))

    enrolled_by = get_user_id_from_request(request)
    created_count = 0
    updated_count = 0
    accounts_created = 0
    credentials = []

    for row, clean_mssv, clean_name, clean_dept, existing in planned:
        clean_email = (row.email or "").strip().lower() or None

        if existing:
            pid = existing["_id"]
            updates = {
                "name":          clean_name,
                "student_id":    clean_mssv,
                "department":    clean_dept,
                "email":         clean_email or existing.get("email"),
                "phone":         (row.phone or "").strip() or existing.get("phone"),
                "gender":        (row.gender or "").strip() or existing.get("gender"),
                "date_of_birth": (row.date_of_birth or "").strip() or existing.get("date_of_birth"),
                "cohort":        (row.cohort or "").strip() or existing.get("cohort"),
                "major":         (row.major or "").strip() or existing.get("major"),
            }
            await db.persons.update_one({"_id": pid}, {"$set": updates})
            updated_count += 1
        else:
            pid = str(uuid.uuid4())
            person_doc = {
                "_id":             pid,
                "name":            clean_name,
                "student_id":      clean_mssv,
                "email":           clean_email,
                "department":      clean_dept,
                "phone":           (row.phone or "").strip() or None,
                "gender":          (row.gender or "").strip() or None,
                "date_of_birth":   (row.date_of_birth or "").strip() or None,
                "cohort":          (row.cohort or "").strip() or None,
                "major":           (row.major or "").strip() or None,
                "academic_status": "active",
                "photo_url":       None,
                "enrolled_at":     datetime.now(UTC),
                "is_active":       True,
                "enrolled_by":     enrolled_by,
            }
            await db.persons.insert_one(person_doc)
            created_count += 1

        if body.create_login_accounts and hasattr(db, "users") and len(clean_mssv) >= 3:
            existing_u = await db.users.find_one({"username": {"$regex": f"^{re.escape(clean_mssv)}$", "$options": "i"}})
            if not existing_u:
                password = secrets.token_urlsafe(18)
                await db.users.insert_one({
                    "username":      clean_mssv,
                    "display_name":  clean_name,
                    "password_hash": await asyncio.to_thread(hash_password, password),
                    "role":          "student",
                    "person_id":     pid,
                    "google_email":  clean_email,
                    "is_active":     True,
                    "created_at":    datetime.now(UTC),
                })
                accounts_created += 1
                credentials.append({"username": clean_mssv, "password": password, "student_id": clean_mssv})

    return {
        "created":          created_count,
        "updated":          updated_count,
        "accounts_created": accounts_created,
        "total_processed":  len(body.students),
        "credentials": credentials,
    }


@router.get("/my-transcript", dependencies=[Depends(require_authenticated)])
async def get_transcript(request: Request, person_id: Optional[str] = Query(None), db=Depends(get_db)):
    user = request.state.user
    linked = await _linked_person_id(db, user)
    pid = linked if user.role == "student" else (person_id or linked)
    if not pid:
        return {"courses": [], "credits_graded": 0, "weighted_gpa": None}
    grade_ids = [g.get("course_id") async for g in db.grades.find({"person_id": pid, "course_id": {"$type": "string"}})]
    rows = []
    for cid in dict.fromkeys(grade_ids):
        rows.extend(await _compute_student_grade_rows(db, person_id_filter=pid, course_id=cid))
    graded = [row for row in rows if row.gpa_4 is not None]
    credits = sum(row.credits for row in graded)
    return {"courses": rows, "credits_graded": credits,
            "weighted_gpa": round(sum(row.gpa_4 * row.credits for row in graded) / credits, 2) if credits else None}
