"""
core/database.py
Async MongoDB setup using Motor.
Collections: persons, sessions, attendance
"""

import os
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Optional, Union
from contextvars import ContextVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from dotenv import load_dotenv
from fastapi import Depends

load_dotenv()
logger = logging.getLogger(__name__)

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGODB_DB_NAME", "attendance_db")
VN_TZ     = timezone(timedelta(hours=7))

_client: Optional[AsyncIOMotorClient] = None
_transaction_db = ContextVar("transaction_db", default=None)


class _SessionCollection:
    def __init__(self, collection, session):
        self.collection, self.session = collection, session

    def __getattr__(self, name):
        method = getattr(self.collection, name)
        def call(*args, **kwargs):
            return method(*args, **{**kwargs, "session": self.session})
        return call


class _SessionDatabase:
    def __init__(self, db, session):
        self.db, self.session = db, session

    def __getattr__(self, name):
        return _SessionCollection(self.db[name], self.session)




def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            MONGO_URL,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            tz_aware=True,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    scoped = _transaction_db.get()
    return scoped if scoped is not None else get_client()[DB_NAME]


async def get_db() -> AsyncIOMotorDatabase:
    return get_database()


async def get_write_db(db=Depends(get_db)):
    """Atomic multi-document mutations. MongoDB must be a replica set (Atlas is).

    No fallback to partial writes when transactions are unavailable.
    """
    if not isinstance(db, AsyncIOMotorDatabase):
        yield db
        return
    async with await db.client.start_session() as session:
        scoped = _SessionDatabase(db, session)
        token = _transaction_db.set(scoped)
        try:
            async with session.start_transaction():
                yield scoped
        finally:
            _transaction_db.reset(token)
            from core.azure_face import invalidate_cache
            invalidate_cache()


async def init_db() -> None:
    db = get_database()

    await db.command("ping")
    logger.info("MongoDB connection successful!")

    # ── persons indexes ───────────────────────────────────────────────────────
    await db.persons.create_index([("name", ASCENDING)])
    await db.persons.create_index([("is_active", ASCENDING)])

    # Names are not identities: different students can share a name.
    await db.persons.create_index("student_id", unique=True,
        partialFilterExpression={"student_id": {"$type": "string"}, "is_active": True},
        collation={"locale": "en", "strength": 2}, name="student_id_active_unique")
    await db.users.create_index("person_id", unique=True,
        partialFilterExpression={"person_id": {"$type": "string"}}, name="person_account_unique")
    await db.courses.create_index([("code", 1), ("department", 1), ("semester", 1)], unique=True)
    await db.grades.create_index([("person_id", 1), ("course_id", 1)], unique=True)
    await db.leave_requests.create_index([("person_id", 1), ("created_at", -1)])
    await db.audit_logs.create_index([("timestamp", -1)])

    # ── sessions indexes ──────────────────────────────────────────────────────
    await db.sessions.create_index([("is_active", ASCENDING)])
    await db.sessions.create_index([("started_at", DESCENDING)])

    # ── attendance — compound unique prevents double-marking ─────────────────
    await db.attendance.create_index(
        [("person_id", ASCENDING), ("session_id", ASCENDING)], unique=True
    )
    await db.attendance.create_index([("marked_at", DESCENDING)])
    await db.attendance.create_index([("status", ASCENDING)])

    # ── face_encodings indexes ───────────────────────────────────────────────
    await db.face_encodings.create_index([("name", ASCENDING)])

    # ── users indexes (per-user identity) ────────────────────────────────────
    await db.users.create_index([("username", ASCENDING)], unique=True)
    await db.users.create_index(
        [("google_email", ASCENDING)],
        unique=True,
        partialFilterExpression={"google_email": {"$type": "string"}},
        name="google_email_unique",
    )
    await db.users.create_index(
        [("microsoft_tenant_id", ASCENDING), ("microsoft_oid", ASCENDING)],
        unique=True, partialFilterExpression={"microsoft_oid": {"$type": "string"}},
        name="microsoft_identity_unique",
    )
    await db.auth_challenges.create_index("expires_at", expireAfterSeconds=0)

    await db.toeic_attempts.create_index([("user_id", 1), ("status", 1), ("started_at", -1)])
    await db.toeic_attempts.create_index([("user_id", 1), ("status", 1), ("submitted_at", -1), ("_id", -1)], name="toeic_recent_submission")
    await db.toeic_cards.create_index([("user_id", 1), ("due", 1)])
    await db.toeic_activity.create_index([("user_id", 1), ("day", -1)])

    await _seed_accounts(db)
    logger.info("MongoDB indexes created on '%s'", DB_NAME)


async def _seed_accounts(db) -> None:
    """Keep known demo passwords out of production bootstrap."""
    production = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development")).lower() in {"production", "prod"}
    try:
        from core.auth import hash_password
        default_user = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        demo_enabled = not production and os.getenv("SEED_DEMO_ACCOUNTS", "false").lower() == "true"
        default_pass = os.getenv("DEFAULT_ADMIN_PASSWORD", "") or ("admin123" if demo_enabled else "")
        if not demo_enabled and (len(default_pass) < 12 or default_pass in {"admin123", "operator123", "123456"}):
            logger.warning("Account bootstrap skipped: set a unique DEFAULT_ADMIN_PASSWORD of at least 12 characters or provision an admin using the admin API key.")
            return
        admin_doc = await db.users.find_one({"username": default_user})
        if not admin_doc:
            await db.users.insert_one({
                "username": default_user,
                "password_hash": hash_password(default_pass),
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
            })
            logger.info("Initialized default administrator account '%s'", default_user)
        if production or os.getenv("SEED_DEMO_ACCOUNTS", "false").lower() != "true":
            return

        if not await db.users.find_one({"username": "operator"}):
            await db.users.insert_one({
                "username": "operator",
                "password_hash": hash_password("operator123"),
                "role": "operator",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
            })
            logger.info("Initialized default instructor/operator account 'operator'")

        student_doc = await db.users.find_one({"username": "maitam"})
        if not student_doc:
            first_person = await db.persons.find_one({"is_active": True}, sort=[("enrolled_at", -1)]) if hasattr(db, "persons") else None
            await db.users.insert_one({
                "username": "maitam",
                "password_hash": hash_password("123456"),
                "role": "student",
                "person_id": str(first_person["_id"]) if first_person else None,
                "google_email": "2305ct2070@dhv.edu.vn",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
            })
            logger.info("Initialized default student account 'maitam'")
        elif not student_doc.get("google_email") and hasattr(db.users, "update_one"):
            await db.users.update_one(
                {"_id": student_doc["_id"]},
                {"$set": {"google_email": "2305ct2070@dhv.edu.vn"}},
            )
    except Exception as e:
        logger.warning("Could not auto-seed default accounts: %s", e)

async def get_person_by_azure_id(db: AsyncIOMotorDatabase, azure_id: str) -> Optional[dict]:
    return await db.persons.find_one({"_id": azure_id, "is_active": True})


async def person_already_marked(db: AsyncIOMotorDatabase, person_id: str, session_id: Union[str, ObjectId]) -> bool:
    if isinstance(session_id, str) and ObjectId.is_valid(session_id):
        sess_oid = ObjectId(session_id)
        doc = await db.attendance.find_one({
            "person_id": person_id,
            "session_id": {"$in": [sess_oid, session_id]},
        })
    else:
        doc = await db.attendance.find_one({"person_id": person_id, "session_id": session_id})
    return doc is not None


async def count_persons(db: AsyncIOMotorDatabase) -> int:
    return await db.persons.count_documents({"is_active": True})


async def count_sessions_today(db: AsyncIOMotorDatabase) -> int:
    today_vn = datetime.now(VN_TZ).date()
    today_start = datetime.combine(today_vn, datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)
    today_end   = today_start + timedelta(days=1)
    return await db.sessions.count_documents({
        "started_at": {"$gte": today_start, "$lt": today_end}
    })


async def count_present_today(db: AsyncIOMotorDatabase) -> int:
    today_vn = datetime.now(VN_TZ).date()
    today_start = datetime.combine(today_vn, datetime.min.time(), tzinfo=VN_TZ).astimezone(timezone.utc)
    today_end   = today_start + timedelta(days=1)
    pipeline = [
        {"$match": {"marked_at": {"$gte": today_start, "$lt": today_end},
                    "status": {"$in": ["present", "late", "excused"]}}},
        {"$group": {"_id": "$person_id"}},
        {"$lookup": {"from": "persons", "localField": "_id", "foreignField": "_id", "as": "person"}},
        {"$match": {"person.is_active": True}},
        {"$count": "count"},
    ]
    async for row in db.attendance.aggregate(pipeline):
        return row["count"]
    return 0



async def get_recent_activity(db: AsyncIOMotorDatabase, limit: int = 8) -> list:
    pipeline = [
        {"$sort": {"marked_at": -1}},
        {"$limit": limit},
        {"$lookup": {"from": "persons", "localField": "person_id", "foreignField": "_id", "as": "person"}},
        {"$set": {"session_oid": {"$convert": {"input": "$session_id", "to": "objectId", "onError": None, "onNull": None}}}},
        {"$lookup": {
            "from": "sessions",
            "localField": "session_oid",
            "foreignField": "_id",
            "as": "session",
        }},
        {"$unwind": "$person"},
        {"$unwind": "$session"},
        {"$project": {
            "id":            {"$toString": "$_id"},
            "person_name":   "$person.name",
            "department":    "$person.department",
            "session_label": "$session.label",
            "marked_at":     {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%SZ", "date": "$marked_at"}},
            "confidence":    1,
            "status":        1,
        }},
    ]
    rows = []
    async for doc in db.attendance.aggregate(pipeline):
        rows.append(doc)
    return rows
