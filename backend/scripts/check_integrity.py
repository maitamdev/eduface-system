"""Read-only pre-upgrade checks. Never migrates, deletes or rewrites user data."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.database import get_database, get_client


async def main():
    db = get_database()
    problems = {}
    for collection, fields, match in [
        ("persons", ["student_id"], {"is_active": True, "student_id": {"$type": "string"}}),
        ("users", ["person_id"], {"person_id": {"$type": "string"}}),
        ("grades", ["person_id", "course_id"], {}),
        ("courses", ["code", "department", "semester"], {}),
    ]:
        key = {field: {"$toUpper": f"${field}"} if field == "student_id" else f"${field}" for field in fields}
        rows = await db[collection].aggregate([
            {"$match": match}, {"$group": {"_id": key, "ids": {"$push": {"$toString": "$_id"}}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
        ]).to_list(length=None)
        # IDs are enough to locate collisions; avoid exposing names/emails in reports.
        problems[collection + "_duplicates"] = [{"ids": r["ids"], "count": r["count"]} for r in rows]
    problems["legacy_sessions_without_roster"] = await db.sessions.count_documents({"roster_ids": {"$exists": False}})
    problems["legacy_grades_without_course"] = await db.grades.count_documents({"course_id": None})
    problems["admins_with_google_link_to_review"] = [str(u["_id"]) async for u in db.users.find({"role": "admin", "google_email": {"$type": "string"}}, {"_id": 1})]
    problems["legacy_name_index_present"] = "name_unique_active" in await db.persons.index_information()
    print(json.dumps(problems, indent=2))
    get_client().close()
    return int(any(problems[k] for k in problems if k.endswith("_duplicates")))


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
