"""Private learning progress, server grading, resumable practice and FSRS reviews."""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictBool
from pymongo.errors import DuplicateKeyError
from fsrs import Card, Rating, Scheduler

from core.auth import require_authenticated
from core.database import get_db, get_write_db, VN_TZ
from core.toeic_content import content, public_question, select_questions, grade
from core.rate_limit import limiter

router = APIRouter(dependencies=[Depends(require_authenticated)])
UTC = timezone.utc
scheduler = Scheduler(desired_retention=.9, enable_fuzzing=False)


def learner(request):
    user = request.state.user
    if user.auth_type != "jwt":
        raise HTTPException(403, "Hãy đăng nhập bằng tài khoản cá nhân để lưu tiến độ học.")
    return user.id


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Preferences(StrictBody):
    target: Literal[350, 550, 650, 750, 900] = 650
    daily_minutes: Literal[15, 30, 45, 60] = 30


class SessionCompletion(StrictBody):
    completed: StrictBool


class Start(StrictBody):
    kind: Literal["lesson", "part", "diagnostic", "mock"]
    lesson_id: str | None = Field(None, max_length=60)
    part: int | None = Field(None, ge=1, le=7)
    request_id: UUID


class Answers(StrictBody):
    revision: StrictInt = Field(default=0, ge=0)
    answers: dict[str, Annotated[StrictInt, Field(ge=0, le=3)] | None] = Field(default_factory=dict, max_length=200)


class Review(StrictBody):
    rating: StrictInt = Field(ge=1, le=4)
    expected_version: StrictInt = Field(ge=0)
    event_id: UUID


def now():
    timestamp = datetime.now(UTC)
    # BSON stores milliseconds; return the same precision on first write and retry.
    return timestamp.replace(microsecond=(timestamp.microsecond // 1000) * 1000)


def attempt_view(doc):
    done = doc["status"] == "submitted"
    return {"id": doc["_id"], "kind": doc["kind"], "lesson_id": doc.get("lesson_id"),
            "status": doc["status"], "started_at": doc["started_at"], "deadline": doc["deadline"],
            "server_now": now(), "revision": doc.get("revision", 0), "answers": doc.get("answers", {}), "result": doc.get("result"),
            "questions": [public_question(q, review=done) for q in doc["questions"]]}


async def owned_attempt(db, uid, aid):
    doc = await db.toeic_attempts.find_one({"_id": aid, "user_id": uid})
    if not doc:
        raise HTTPException(404, "Không tìm thấy lượt luyện tập.")
    return doc


def validated_answers(doc, answers):
    questions = {q["id"]: q for q in doc["questions"]}
    for qid, value in answers.items():
        if qid not in questions or (value is not None and value >= len(questions[qid]["options"])):
            raise HTTPException(422, "Câu trả lời không thuộc đề hoặc lựa chọn không hợp lệ.")
    return answers


async def activity(db, uid, field, amount, timestamp):
    day = timestamp.astimezone(VN_TZ).date().isoformat()
    await db.toeic_activity.update_one({"_id": f"{uid}:{day}"},
        {"$set": {"user_id": uid, "day": day}, "$inc": {field: amount}}, upsert=True)


@router.get("/catalog")
async def catalog():
    data = content()
    return {"version": data["version"], "stages": data["stages"], "sources": data["sources"],
            "curriculum": data["curriculum"],
            "notice": data["notice"], "question_count": len(data["questions"]),
            "vocabulary_count": len(data["vocabulary"]),
            "lessons": [{k: v for k, v in lesson.items() if k != "sections"} |
                        {"question_count": sum(q["lesson_id"] == lesson["id"] for q in data["questions"])}
                        for lesson in data["lessons"]]}


@router.get("/lessons/{lesson_id}")
async def lesson(lesson_id: str):
    data = content()
    row = next((x for x in data["lessons"] if x["id"] == lesson_id), None)
    if not row:
        raise HTTPException(404, "Không tìm thấy bài học.")
    return row | {"vocabulary": [c for c in data["vocabulary"] if c["lesson_id"] == lesson_id]}


@router.put("/preferences")
async def preferences(body: Preferences, request: Request, db=Depends(get_db)):
    uid = learner(request)
    await db.toeic_profiles.update_one({"_id": uid}, {"$set": body.model_dump()}, upsert=True)
    return body


@router.get("/progress")
async def progress(request: Request, db=Depends(get_db)):
    uid = learner(request)
    profile = await db.toeic_profiles.find_one({"_id": uid}) or {}
    recent = await db.toeic_attempts.find({"user_id": uid, "status": "submitted"},
        {"questions": 0, "answers": 0, "user_id": 0}).sort("submitted_at", -1).limit(20).to_list(None)
    active = await db.toeic_attempts.find({"user_id": uid, "status": "active"},
        {"questions": 0, "answers": 0, "user_id": 0}).sort("started_at", -1).limit(5).to_list(None)
    for doc in recent + active:
        doc["id"] = doc.pop("_id")
    days = await db.toeic_activity.find({"user_id": uid}, {"_id": 0, "user_id": 0}).sort("day", -1).to_list(None)
    day_set = {d["day"] for d in days}
    today = now().astimezone(VN_TZ).date()
    cursor = today if today.isoformat() in day_set else today - timedelta(days=1)
    streak = 0
    while cursor.isoformat() in day_set:
        streak += 1
        cursor -= timedelta(days=1)
    learned = await db.toeic_cards.count_documents({"user_id": uid})
    due = await db.toeic_cards.count_documents({"user_id": uid, "due": {"$lte": now()}})
    return {"target": profile.get("target", 650), "daily_minutes": profile.get("daily_minutes", 30),
            "curriculum_completed": profile.get("curriculum_completed", []),
            "lessons": profile.get("lessons", {}), "recent": recent, "active": active,
            "days": days[:90], "streak": streak, "cards_learned": learned, "cards_due": due}


@router.put("/curriculum/sessions/{session_id}")
@limiter.limit("60/minute")
async def complete_session(session_id: str, body: SessionCompletion, request: Request, db=Depends(get_db)):
    """Learner-reported study completion; never awards quiz scores or a certificate."""
    uid = learner(request)
    if session_id not in {row["id"] for row in content()["curriculum"]["sessions"]}:
        raise HTTPException(404, "Không tìm thấy buổi học.")
    update = {"$addToSet" if body.completed else "$pull": {"curriculum_completed": session_id}}
    try:
        await db.toeic_profiles.update_one({"_id": uid}, update, upsert=True)
    except DuplicateKeyError:
        # Concurrent first writes may both try to create the same learner profile.
        await db.toeic_profiles.update_one({"_id": uid}, update)
    return {"session_id": session_id, "completed": body.completed}


@router.post("/attempts")
@limiter.limit("20/minute")
async def start_attempt(body: Start, request: Request, db=Depends(get_db)):
    uid = learner(request)
    if body.kind == "lesson" and body.lesson_id not in {x["id"] for x in content()["lessons"]}:
        raise HTTPException(422, "Chọn một bài học hợp lệ.")
    if body.kind == "part" and body.part is None:
        raise HTTPException(422, "Chọn Part 1–7.")
    if (body.kind != "lesson" and body.lesson_id is not None) or (body.kind != "part" and body.part is not None):
        raise HTTPException(422, "Tham số bài học hoặc Part không phù hợp loại bài.")
    aid = hashlib.sha256(f"{uid}:{body.request_id}".encode()).hexdigest()[:40]
    existing = await db.toeic_attempts.find_one({"_id": aid, "user_id": uid})
    if existing:
        if (existing["kind"], existing.get("lesson_id"), existing.get("part")) != (body.kind, body.lesson_id, body.part):
            raise HTTPException(409, "Mã yêu cầu đã được dùng cho một đề khác.")
        return attempt_view(existing)
    if await db.toeic_attempts.count_documents({"user_id": uid, "status": "active", "deadline": {"$gt": now()}}) >= 5:
        raise HTTPException(409, "Bạn đang có 5 bài chưa kết thúc. Tiếp tục và nộp một bài trong mục Tiến độ trước khi mở bài mới.")
    questions = select_questions(body.kind, body.lesson_id, body.part, seed=aid)
    minutes = 120 if body.kind == "mock" else 25 if body.kind == "diagnostic" else max(10, len(questions) * 2)
    timestamp = now()
    doc = {"_id": aid, "user_id": uid, "kind": body.kind, "lesson_id": body.lesson_id, "part": body.part,
           "content_version": content()["version"], "started_at": timestamp,
           "deadline": timestamp + timedelta(minutes=minutes), "status": "active", "revision": 0, "questions": questions, "answers": {}}
    try:
        await db.toeic_attempts.insert_one(doc)
    except DuplicateKeyError:
        existing = await owned_attempt(db, uid, aid)
        if (existing["kind"], existing.get("lesson_id"), existing.get("part")) != (body.kind, body.lesson_id, body.part):
            raise HTTPException(409, "Mã yêu cầu đã được dùng cho một đề khác.")
        return attempt_view(existing)
    return attempt_view(doc)


@router.get("/attempts/{attempt_id}")
async def get_attempt(attempt_id: str, request: Request, db=Depends(get_db)):
    return attempt_view(await owned_attempt(db, learner(request), attempt_id))


@router.put("/attempts/{attempt_id}/answers")
async def save_answers(attempt_id: str, body: Answers, request: Request, db=Depends(get_db)):
    uid = learner(request)
    doc = await owned_attempt(db, uid, attempt_id)
    if doc["status"] != "active" or now() > doc["deadline"]:
        raise HTTPException(409, "Lượt luyện đã kết thúc hoặc hết thời gian. Hãy nộp bài đã lưu.")
    answers = validated_answers(doc, body.answers)
    changed = await db.toeic_attempts.update_one({"_id": attempt_id, "user_id": uid, "status": "active", "revision": body.revision}, {"$set": {"answers": answers}, "$inc": {"revision": 1}})
    if not changed.matched_count:
        raise HTTPException(409, "Bài vừa thay đổi ở cửa sổ khác. Mở lại bài để nhận bản mới nhất.")
    return {"saved": True, "revision": body.revision + 1}


@router.post("/attempts/{attempt_id}/submit")
async def submit(attempt_id: str, body: Answers, request: Request, db=Depends(get_write_db, scope="function")):
    uid = learner(request)
    doc = await owned_attempt(db, uid, attempt_id)
    if doc["status"] == "submitted":
        return attempt_view(doc)
    timestamp = now()
    if timestamp <= doc["deadline"] + timedelta(seconds=3) and body.revision != doc.get("revision", 0):
        raise HTTPException(409, "Bài vừa thay đổi ở cửa sổ khác. Mở lại bài trước khi nộp.")
    answers = validated_answers(doc, body.answers) if timestamp <= doc["deadline"] + timedelta(seconds=3) else doc.get("answers", {})
    result = grade(doc["questions"], answers)
    fields = {"status": "submitted", "submitted_at": timestamp, "answers": answers, "result": result}
    changed = await db.toeic_attempts.update_one({"_id": attempt_id, "user_id": uid, "status": "active"}, {"$set": fields})
    if changed.matched_count:
        if doc.get("lesson_id"):
            await db.toeic_profiles.update_one({"_id": uid}, {"$max": {f"lessons.{doc['lesson_id']}": result["percent"]}}, upsert=True)
        await activity(db, uid, "questions", len(doc["questions"]), timestamp)
    else:
        return attempt_view(await owned_attempt(db, uid, attempt_id))
    return attempt_view(doc | fields)


@router.get("/vocabulary")
async def vocabulary(request: Request, lesson_id: str | None = None, db=Depends(get_db)):
    uid = learner(request)
    stored = {d["vocabulary_id"]: d async for d in db.toeic_cards.find({"user_id": uid})}
    rows = []
    for card in content()["vocabulary"]:
        if lesson_id and card["lesson_id"] != lesson_id:
            continue
        current = stored.get(card["id"], {})
        rows.append(card | {"version": current.get("version", 0), "due": current.get("due"), "reviews": current.get("reviews", 0)})
    return rows


@router.post("/vocabulary/{card_id}/review")
async def review(card_id: str, body: Review, request: Request, db=Depends(get_write_db, scope="function")):
    uid = learner(request)
    if card_id not in {c["id"] for c in content()["vocabulary"]}:
        raise HTTPException(404, "Không tìm thấy từ vựng.")
    key = f"{uid}:{card_id}"
    previous = await db.toeic_cards.find_one({"_id": key})
    if previous and previous.get("last_event") == str(body.event_id):
        return {"due": previous["due"], "version": previous["version"]}
    version = previous.get("version", 0) if previous else 0
    if version != body.expected_version:
        raise HTTPException(409, "Thẻ đã được ôn ở nơi khác. Tải lại danh sách thẻ.")
    timestamp = now()
    if previous and previous["due"] > timestamp:
        raise HTTPException(409, "Thẻ chưa đến hạn ôn. Chọn một thẻ khác.")
    card = Card.from_dict(previous["fsrs"]) if previous else Card()
    card, _ = scheduler.review_card(card, Rating(body.rating), review_datetime=timestamp)
    card.due = card.due.replace(microsecond=(card.due.microsecond // 1000) * 1000)
    doc = {"user_id": uid, "vocabulary_id": card_id, "fsrs": card.to_dict(), "due": card.due,
           "version": version + 1, "reviews": (previous.get("reviews", 0) if previous else 0) + 1,
           "last_event": str(body.event_id)}
    if previous:
        updated = await db.toeic_cards.update_one({"_id": key, "version": version}, {"$set": doc})
        if not updated.matched_count:
            raise HTTPException(409, "Thẻ vừa được cập nhật. Tải lại danh sách.")
    else:
        await db.toeic_cards.insert_one({"_id": key, **doc})
    await activity(db, uid, "reviews", 1, timestamp)
    return {"due": card.due, "version": version + 1}
