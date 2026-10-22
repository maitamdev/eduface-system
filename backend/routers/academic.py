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
import uuid
from datetime import datetime, UTC
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.auth import (
    AuthenticatedUser,
    get_user_id_from_request,
    hash_password,
    require_authenticated,
    require_operator,
)
from core.database import get_db
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
) -> List[StudentGradeRow]:
    person_query: dict = {"is_active": True}
    if department and department.strip():
        person_query["department"] = {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}
    if person_id_filter:
        person_query["_id"] = person_id_filter

    persons = await db.persons.find(person_query).sort("name", 1).to_list(length=2000)
    if not persons:
        return []

    all_sessions = await db.sessions.find({}).to_list(length=2000)
    person_ids = [p["_id"] for p in persons]

    att_records = await db.attendance.find({"person_id": {"$in": person_ids}}).to_list(length=50000)
    attended_by_person: dict[str, set[str]] = {pid: set() for pid in person_ids}
    for rec in att_records:
        st = rec.get("status", "present")
        if st in ("present", "late", "excused"):
            pid = rec.get("person_id")
            sid = str(rec.get("session_id"))
            if pid in attended_by_person:
                attended_by_person[pid].add(sid)

    grades_docs = {}
    if hasattr(db, "grades"):
        async for gdoc in db.grades.find({"person_id": {"$in": person_ids}}):
            grades_docs[gdoc["person_id"]] = gdoc

    rows: List[StudentGradeRow] = []
    for p in persons:
        pid = p["_id"]
        p_dept = (p.get("department") or "").strip().lower()
        matching_sids = set()
        for s in all_sessions:
            s_dept = (s.get("department") or "").strip().lower()
            if not p_dept or not s_dept or s_dept == p_dept:
                matching_sids.add(str(s["_id"]))

        total_sess = len(matching_sids)
        present_cnt = len(attended_by_person.get(pid, set()) & matching_sids)
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
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not hasattr(db, "courses"):
        return []
    query: dict = {}
    if department and department.strip():
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
    existing = await db.courses.find_one({"code": clean_code})
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
    res = await db.courses.delete_one({"_id": ObjectId(course_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Course not found.")


# ── 2. Grades, GPA & Exam Eligibility ────────────────────────────────────────

@router.get("/grades", response_model=List[StudentGradeRow], dependencies=[Depends(require_operator)])
async def list_grades(
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    return await _compute_student_grade_rows(db, department=department)


@router.get("/my-grade", response_model=Optional[StudentGradeRow], dependencies=[Depends(require_authenticated)])
async def get_my_grade(
    request: Request,
    person_id: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user = getattr(request.state, "user", None)
    target_pid = person_id
    if not target_pid and isinstance(user, AuthenticatedUser):
        target_pid = user.person_id
        if not target_pid and user.username:
            p = await db.persons.find_one(
                {"$or": [
                    {"student_id": {"$regex": f"^{re.escape(user.username)}$", "$options": "i"}},
                    {"email": {"$regex": f"^{re.escape(user.username)}$", "$options": "i"}},
                ], "is_active": True}
            )
            if p:
                target_pid = p["_id"]
    if not target_pid:
        return None
    rows = await _compute_student_grade_rows(db, person_id_filter=target_pid)
    return rows[0] if rows else None


@router.put("/grades", response_model=StudentGradeRow, dependencies=[Depends(require_operator)])
async def upsert_grade(body: GradeUpsert, db: AsyncIOMotorDatabase = Depends(get_db)):
    person = await db.persons.find_one({"_id": body.person_id, "is_active": True})
    if not person:
        raise HTTPException(404, "Không tìm thấy hồ sơ sinh viên.")

    update_doc = {
        "person_id":     body.person_id,
        "midterm_score": body.midterm_score,
        "final_score":   body.final_score,
        "bonus_score":   body.bonus_score if body.bonus_score is not None else 0.0,
        "note":          (body.note or "").strip() or None,
        "updated_at":    datetime.now(UTC),
    }
    await db.grades.update_one(
        {"person_id": body.person_id},
        {"$set": update_doc},
        upsert=True,
    )
    rows = await _compute_student_grade_rows(db, person_id_filter=body.person_id)
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
        if user.person_id:
            query["person_id"] = user.person_id
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
        target_pid = user.person_id
    if not target_pid and isinstance(user, AuthenticatedUser):
        target_pid = user.person_id

    if not target_pid:
        raise HTTPException(400, "Bạn cần đăng ký hồ sơ sinh viên trước khi gửi đơn xin phép.")

    person = await db.persons.find_one({"_id": target_pid, "is_active": True})
    if not person:
        raise HTTPException(404, "Không tìm thấy hồ sơ sinh viên.")

    session_label = None
    if body.session_id and ObjectId.is_valid(body.session_id):
        sess = await db.sessions.find_one({"_id": ObjectId(body.session_id)})
        if sess:
            session_label = sess.get("label")

    doc = {
        "person_id":     target_pid,
        "person_name":   person["name"],
        "student_id":    person.get("student_id"),
        "department":    person.get("department"),
        "session_id":    body.session_id or None,
        "session_label": session_label,
        "leave_date":    body.leave_date.strip(),
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
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not ObjectId.is_valid(leave_id):
        raise HTTPException(404, "Không tìm thấy đơn xin phép.")
    doc = await db.leave_requests.find_one({"_id": ObjectId(leave_id)})
    if not doc:
        raise HTTPException(404, "Không tìm thấy đơn xin phép.")

    now = datetime.now(UTC)
    updates = {
        "status":        body.status,
        "reviewer_note": (body.reviewer_note or "").strip() or None,
        "reviewed_at":   now,
    }
    await db.leave_requests.update_one({"_id": ObjectId(leave_id)}, {"$set": updates})
    doc.update(updates)

    # Nếu duyệt đơn (approved) và đơn gắn với một phiên điểm danh -> Tự động cập nhật Vắng có phép (excused)
    if body.status == "approved" and doc.get("session_id") and ObjectId.is_valid(doc["session_id"]):
        sid_obj = ObjectId(doc["session_id"])
        sess = await db.sessions.find_one({"_id": sid_obj})
        if sess:
            await db.attendance.update_one(
                {"person_id": doc["person_id"], "session_id": sid_obj},
                {
                    "$set": {
                        "status":        "excused",
                        "marked_at":     now,
                        "marked_by":     get_user_id_from_request(request) or "leave_approved",
                        "person_name":   doc["person_name"],
                        "student_id":    doc.get("student_id"),
                        "department":    doc.get("department") or sess.get("department"),
                        "session_label": sess.get("label", ""),
                    },
                    "$setOnInsert": {
                        "person_id":  doc["person_id"],
                        "session_id": sid_obj,
                        "confidence": None,
                    },
                },
                upsert=True,
            )

    doc["id"] = str(doc.pop("_id"))
    return LeaveRequestOut(**doc)


# ── 4. Class & Academic Announcements (Bảng thông báo học vụ) ────────────────

@router.get("/announcements", response_model=List[AnnouncementOut], dependencies=[Depends(require_authenticated)])
async def list_announcements(
    department: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not hasattr(db, "announcements"):
        return []
    query: dict = {}
    if department and department.strip():
        query["$or"] = [
            {"department": None},
            {"department": ""},
            {"department": {"$regex": f"^{re.escape(department.strip())}$", "$options": "i"}},
        ]
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
        (user.display_name or user.username)
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
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not body.students:
        raise HTTPException(400, "Danh sách sinh viên trống.")
    if len(body.students) > 500:
        raise HTTPException(400, "Tối đa 500 sinh viên mỗi lần nhập.")

    enrolled_by = get_user_id_from_request(request)
    created_count = 0
    updated_count = 0
    accounts_created = 0

    for row in body.students:
        clean_mssv = row.student_id.strip().upper()
        clean_name = row.name.strip()
        clean_dept = row.department.strip()
        clean_email = (row.email or "").strip().lower() or None

        existing = await db.persons.find_one(
            {
                "$or": [
                    {"student_id": {"$regex": f"^{re.escape(clean_mssv)}$", "$options": "i"}},
                    {"name": {"$regex": f"^{re.escape(clean_name)}$", "$options": "i"}},
                ],
                "is_active": True,
            }
        )

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
                await db.users.insert_one({
                    "username":      clean_mssv,
                    "display_name":  clean_name,
                    "password_hash": hash_password(body.default_password),
                    "role":          "student",
                    "person_id":     pid,
                    "google_email":  clean_email,
                    "is_active":     True,
                    "created_at":    datetime.now(UTC),
                })
                accounts_created += 1

    return {
        "created":          created_count,
        "updated":          updated_count,
        "accounts_created": accounts_created,
        "total_processed":  len(body.students),
    }
