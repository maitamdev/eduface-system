"""Inspect/upgrade indexes and normalize identifiers; never infer historical rosters/grades.
Run with the service stopped and a verified backup. Default is read-only.
"""
import argparse
import asyncio
import json
import os
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


async def plan(db):
    collisions = {}
    normal_student = {"$toUpper": {"$trim": {"input": "$student_id"}}}
    normal_session = {"$convert": {"input": "$session_id", "to": "objectId", "onError": "$session_id", "onNull": None}}
    specs = [
        ("persons", {"is_active": True, "student_id": {"$type": "string"}}, normal_student),
        ("users", {"person_id": {"$type": "string"}}, "$person_id"),
        ("grades", {}, {"person_id": "$person_id", "course_id": {"$ifNull": ["$course_id", None]}}),
        ("courses", {}, {"code": "$code", "department": "$department", "semester": "$semester"}),
        ("attendance", {}, {"person_id": "$person_id", "session_id": normal_session}),
    ]
    for collection, match, key in specs:
        collisions[collection] = await db[collection].aggregate([
            {"$match": match}, {"$group": {"_id": key, "ids": {"$push": {"$toString": "$_id"}}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}, {"$project": {"_id": 0, "ids": 1, "count": 1}},
        ]).to_list(None)
    return {"database": db.name, "collisions": collisions,
            "legacy_name_index": "name_unique_active" in await db.persons.index_information(),
            "unassigned_grades": await db.grades.count_documents({"course_id": None}),
            "sessions_without_roster": await db.sessions.count_documents({"roster_ids": {"$exists": False}})}


async def migrate(db):
    report = await plan(db)
    if any(report["collisions"].values()):
        raise ValueError("Resolve the reported duplicate IDs before applying; no records were changed")
    # Normalization is atomic; DDL is intentionally separate and repeatable.
    async with await db.client.start_session() as session:
        async with session.start_transaction():
            await db.persons.update_many({"student_id": {"$type": "string"}},
                [{"$set": {"student_id": {"$toUpper": {"$trim": {"input": "$student_id"}}}}}], session=session)
            async for record in db.attendance.find({"session_id": {"$type": "string"}}, session=session):
                if ObjectId.is_valid(record["session_id"]):
                    await db.attendance.update_one({"_id": record["_id"]}, {"$set": {"session_id": ObjectId(record["session_id"])}}, session=session)
    await db.persons.create_index("student_id", unique=True, partialFilterExpression={"student_id": {"$type": "string"}, "is_active": True}, collation={"locale": "en", "strength": 2}, name="student_id_active_unique")
    await db.users.create_index("person_id", unique=True, partialFilterExpression={"person_id": {"$type": "string"}}, name="person_account_unique")
    await db.courses.create_index([("code", 1), ("department", 1), ("semester", 1)], unique=True)
    await db.grades.create_index([("person_id", 1), ("course_id", 1)], unique=True)
    await db.attendance.create_index([("person_id", 1), ("session_id", 1)], unique=True)
    if report["legacy_name_index"]:
        await db.persons.drop_index("name_unique_active")
    return await plan(db)


async def main(args):
    uri = os.environ.get("MONGODB_URL")
    if not uri: raise SystemExit("Set MONGODB_URL explicitly; this script does not load .env")
    if args.apply and not args.backup_confirmed:
        raise SystemExit("Take/verify a backup and stop application writes, then pass --backup-confirmed")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000, tz_aware=True)
    try:
        result = await (migrate(client[args.database]) if args.apply else plan(client[args.database]))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(any(result["collisions"].values()))
    finally: client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup-confirmed", action="store_true")
    raise SystemExit(asyncio.run(main(parser.parse_args())))
