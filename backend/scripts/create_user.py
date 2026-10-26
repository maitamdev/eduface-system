"""
backend/scripts/create_user.py

Helper script to create a user account in the MongoDB `users` collection.
Useful for bootstrapping the initial admin or operator accounts.

Usage:
    python backend/scripts/create_user.py --username <username> --password <password> [--role admin|operator]
"""

import argparse
import getpass
import logging
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
import pymongo

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.auth import hash_password

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("create_user")


def create_user(username: str, password: str, role: str):
    if not 3 <= len(username.strip()) <= 50 or not 12 <= len(password) <= 128:
        raise ValueError("Username must be 3–50 characters and password 12–128 characters")
    if role not in {"admin", "operator"}:
        raise ValueError("Role must be admin or operator")
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "attendance_db")

    client = pymongo.MongoClient(mongo_url)
    db = client[db_name]

    username = username.strip()
    existing = db.users.find_one({"username": username})
    if existing:
        logger.error("User '%s' already exists!", username)
        client.close()
        sys.exit(1)

    doc = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = db.users.insert_one(doc)
    logger.info("Successfully created user '%s' (role=%s, id=%s)", username, role, result.inserted_id)
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a user for Smart Attendance System.")
    parser.add_argument("--username", required=True, help="Unique username")
    parser.add_argument("--password", help="Password (omit for a hidden prompt)")
    parser.add_argument("--role", default="operator", choices=["operator", "admin"], help="User role")
    args = parser.parse_args()

    try:
        create_user(args.username, args.password or getpass.getpass("Password: "), args.role)
    except ValueError as exc:
        parser.error(str(exc))
