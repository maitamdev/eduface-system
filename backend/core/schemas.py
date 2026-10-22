"""
core/schemas.py
Pydantic v2 models for all API request and response payloads.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Person ────────────────────────────────────────────────────────────────────
class PersonCreate(BaseModel):
    name:       str = Field(..., min_length=2, max_length=120)
    student_id: Optional[str] = None
    email:      Optional[str] = None
    department: Optional[str] = None


class PersonUpdate(BaseModel):
    name:            Optional[str] = Field(None, min_length=2, max_length=120)
    student_id:      Optional[str] = Field(None, max_length=60)
    email:           Optional[str] = Field(None, max_length=120)
    department:      Optional[str] = Field(None, max_length=120)
    phone:           Optional[str] = Field(None, max_length=30)
    date_of_birth:   Optional[str] = Field(None, max_length=30)
    gender:          Optional[str] = Field(None, max_length=20)
    cohort:          Optional[str] = Field(None, max_length=40)
    major:           Optional[str] = Field(None, max_length=120)
    advisor:         Optional[str] = Field(None, max_length=120)
    academic_status: Optional[str] = Field(None, max_length=40)
    notes:           Optional[str] = Field(None, max_length=500)


class PersonOut(BaseModel):
    id:              str
    name:            str
    student_id:      Optional[str] = None
    email:           Optional[str] = None
    department:      Optional[str] = None
    phone:           Optional[str] = None
    date_of_birth:   Optional[str] = None
    gender:          Optional[str] = None
    cohort:          Optional[str] = None
    major:           Optional[str] = None
    advisor:         Optional[str] = None
    academic_status: Optional[str] = "active"
    notes:           Optional[str] = None
    photo_url:       Optional[str] = None
    enrolled_at:     datetime
    is_active:       bool
    enrolled_by:     Optional[str] = None

    model_config = {"from_attributes": True}


# ── Session ───────────────────────────────────────────────────────────────────
class SessionCreate(BaseModel):
    label:              str = Field(..., min_length=2, max_length=200)
    department:         Optional[str] = None
    late_after_minutes: Optional[int] = Field(15, ge=0, le=240)


class SessionOut(BaseModel):
    id:                 str
    label:              str
    department:         Optional[str]
    started_at:         datetime
    ended_at:           Optional[datetime]
    is_active:          bool
    late_after_minutes: Optional[int] = 15

    model_config = {"from_attributes": True}


# ── Attendance ────────────────────────────────────────────────────────────────
class AttendanceOut(BaseModel):
    id:            str
    person_id:     str
    person_name:   str
    student_id:    Optional[str] = None
    department:    Optional[str]
    session_id:    str
    session_label: str
    marked_at:     datetime
    confidence:    Optional[float]
    status:        str
    marked_by:     Optional[str] = None

    model_config = {"from_attributes": True}


class ManualAttendancePayload(BaseModel):
    person_id:  str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    status:     str = Field(..., pattern="^(present|late|excused|absent)$")


class IdentifyResult(BaseModel):
    azure_person_id: str
    name:            str
    confidence:      float
    face_box:        dict
    already_marked:  bool = False
    is_live:         bool = True
    liveness_score:  Optional[float] = None
    spoof_reason:    Optional[str] = None


class MarkAttendanceResponse(BaseModel):
    session_id:  str
    identified:  List[IdentifyResult]
    new_records: int                    # how many were freshly marked


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardMetrics(BaseModel):
    total_enrolled:   int
    sessions_today:   int
    present_today:    int
    attendance_rate:  float             # percentage


class ActivityItem(BaseModel):
    id:            str
    person_name:   str
    department:    Optional[str]
    session_label: str
    marked_at:     str
    confidence:    Optional[float]
    status:        str


# ── Reports ───────────────────────────────────────────────────────────────────
class DailyAttendanceStat(BaseModel):
    date:             str               # ISO date string
    total_sessions:   int
    total_present:    int
    attendance_rate:  float


class PersonAttendanceStat(BaseModel):
    person_id:        str
    name:             str
    department:       Optional[str]
    total_sessions:   int
    present_count:    int
    attendance_rate:  float
    is_defaulter:     bool              # True if rate < 75%


# ── Authentication & Users (Step 11) ──────────────────────────────────────────
class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserCreate(BaseModel):
    username:  str = Field(..., min_length=3, max_length=50)
    password:  str = Field(..., min_length=6, max_length=128)
    role:      str = Field("operator", pattern="^(operator|admin|student)$")
    person_id: Optional[str] = None


class UserUpdate(BaseModel):
    role:      Optional[str] = Field(None, pattern="^(operator|admin|student)$")
    is_active: Optional[bool] = None
    password:  Optional[str] = Field(None, min_length=6, max_length=128)
    person_id: Optional[str] = None


class UserOut(BaseModel):
    id:            str
    username:      str
    display_name:  Optional[str] = None
    role:          str
    is_active:     bool
    created_at:    datetime
    person_id:     Optional[str] = None
    google_email:  Optional[str] = None
    microsoft_oid: Optional[str] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int
    role:         str
    username:     str


class StudentSessionItem(BaseModel):
    session_id: str
    label:      str
    department: Optional[str] = None
    started_at: datetime
    ended_at:   Optional[datetime] = None
    is_active:  bool
    attended:   bool
    marked_at:  Optional[datetime] = None
    confidence: Optional[float] = None
    status:     str


class StudentPortalSummary(BaseModel):
    person:          Optional[PersonOut] = None
    total_sessions:  int
    present_count:   int
    absent_count:    int
    attendance_rate: float
    is_defaulter:    bool
    sessions:        List[StudentSessionItem]


# ── Academic & Student Management Suite ───────────────────────────────────────
class CourseCreate(BaseModel):
    code:       str = Field(..., min_length=2, max_length=40)
    name:       str = Field(..., min_length=2, max_length=160)
    department: str = Field(..., min_length=1, max_length=100)
    credits:    int = Field(3, ge=1, le=15)
    lecturer:   Optional[str] = Field(None, max_length=120)
    schedule:   Optional[str] = Field(None, max_length=120)
    room:       Optional[str] = Field(None, max_length=80)
    semester:   Optional[str] = Field("HK1 2026-2027", max_length=60)


class CourseOut(BaseModel):
    id:         str
    code:       str
    name:       str
    department: str
    credits:    int
    lecturer:   Optional[str] = None
    schedule:   Optional[str] = None
    room:       Optional[str] = None
    semester:   Optional[str] = None
    created_at: datetime


class GradeUpsert(BaseModel):
    person_id:     str = Field(..., min_length=1)
    midterm_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    final_score:   Optional[float] = Field(None, ge=0.0, le=10.0)
    bonus_score:   Optional[float] = Field(0.0, ge=0.0, le=2.0)
    note:          Optional[str] = Field(None, max_length=300)


class StudentGradeRow(BaseModel):
    person_id:        str
    name:             str
    student_id:       Optional[str] = None
    department:       Optional[str] = None
    total_sessions:   int
    present_count:    int
    attendance_rate:  float
    attendance_score: float
    midterm_score:    Optional[float] = None
    final_score:      Optional[float] = None
    bonus_score:      float = 0.0
    total_10:         Optional[float] = None
    gpa_4:            Optional[float] = None
    letter_grade:     Optional[str] = None
    exam_eligible:    bool
    note:             Optional[str] = None


class LeaveRequestCreate(BaseModel):
    session_id:   Optional[str] = None
    leave_date:   str = Field(..., min_length=4, max_length=40)
    reason:       str = Field(..., min_length=3, max_length=500)
    evidence_url: Optional[str] = Field(None, max_length=300)


class LeaveRequestDecision(BaseModel):
    status:        str = Field(..., pattern="^(approved|rejected)$")
    reviewer_note: Optional[str] = Field(None, max_length=300)


class LeaveRequestOut(BaseModel):
    id:            str
    person_id:     str
    person_name:   str
    student_id:    Optional[str] = None
    department:    Optional[str] = None
    session_id:    Optional[str] = None
    session_label: Optional[str] = None
    leave_date:    str
    reason:        str
    evidence_url:  Optional[str] = None
    status:        str
    reviewer_note: Optional[str] = None
    created_at:    datetime
    reviewed_at:   Optional[datetime] = None


class AnnouncementCreate(BaseModel):
    title:      str = Field(..., min_length=2, max_length=200)
    content:    str = Field(..., min_length=2, max_length=2000)
    department: Optional[str] = Field(None, max_length=100)
    priority:   str = Field("normal", pattern="^(normal|important|exam)$")


class AnnouncementOut(BaseModel):
    id:         str
    title:      str
    content:    str
    department: Optional[str] = None
    priority:   str
    author:     str
    created_at: datetime


class BulkStudentRow(BaseModel):
    student_id:    str = Field(..., min_length=2, max_length=50)
    name:          str = Field(..., min_length=2, max_length=120)
    department:    str = Field(..., min_length=1, max_length=100)
    email:         Optional[str] = None
    phone:         Optional[str] = None
    gender:        Optional[str] = None
    date_of_birth: Optional[str] = None
    cohort:        Optional[str] = None
    major:         Optional[str] = None


class BulkStudentImportPayload(BaseModel):
    students:              List[BulkStudentRow]
    create_login_accounts: bool = True
    default_password:      str = Field("123456", min_length=6, max_length=64)
