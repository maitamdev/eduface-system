"""Regression tests for class-scoped reports, without a MongoDB connection."""

from datetime import datetime, timezone
import re
from types import SimpleNamespace

from bson import ObjectId
import pytest

from core.attendance_policy import (
    VN_TZ, as_utc, attendance_status, is_session_assessed,
    session_applies_to_person,
)
from routers import reports


def local(day, hour=9, minute=0):
    return datetime(2026, 10, day, hour, minute, tzinfo=VN_TZ)


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        now = datetime(2026, 10, 23, 3, tzinfo=timezone.utc)
        return now.astimezone(tz) if tz else now.replace(tzinfo=None)


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    monkeypatch.setattr(reports, "datetime", FixedDatetime)


def matches(doc, query):
    for key, expected in query.items():
        if key == "$or":
            if not any(matches(doc, alternative) for alternative in expected):
                return False
            continue
        value = doc.get(key)
        if not isinstance(expected, dict):
            if value != expected:
                return False
            continue
        if "$regex" in expected:
            if not isinstance(value, str) or not re.search(expected["$regex"], value, re.I if expected.get("$options") == "i" else 0):
                return False
        if "$in" in expected and value not in expected["$in"]:
            return False
        if "$gte" in expected and as_utc(value) < as_utc(expected["$gte"]):
            return False
        if "$lt" in expected and as_utc(value) >= as_utc(expected["$lt"]):
            return False
    return True


class Cursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, key, direction):
        self.docs.sort(key=lambda doc: doc[key], reverse=direction < 0)
        return self

    def __aiter__(self):
        async def rows():
            for doc in self.docs:
                yield doc
        return rows()


class Collection:
    def __init__(self, docs):
        self.docs = docs
        self.queries = []

    def find(self, query, projection=None):
        self.queries.append(query)
        docs = [dict(doc) for doc in self.docs if matches(doc, query)]
        if projection:
            docs = [{key: value for key, value in doc.items() if projection.get(key)} for doc in docs]
        return Cursor(docs)


def database(persons=(), sessions=(), attendance=()):
    return SimpleNamespace(persons=Collection(persons), sessions=Collection(sessions), attendance=Collection(attendance))


def person(pid="alice", department="A", enrolled_at=None, active=True):
    return {"_id": pid, "name": pid.title(), "department": department,
            "enrolled_at": enrolled_at or local(1), "is_active": active}


def session(sid="a", department="A", day=23, active=False):
    return {"_id": sid, "department": department, "started_at": local(day), "is_active": active}


def record(pid="alice", sid="a", status="present", marked_at=None, rid="1"):
    return {"_id": rid, "person_id": pid, "session_id": sid, "status": status, "marked_at": marked_at or local(23)}


@pytest.mark.asyncio
async def test_each_person_is_assessed_only_for_their_class_and_shared_sessions():
    db = database(
        [person(), person("bob", "B"), person("removed", "A", active=False)],
        [session(), session("b", "B"), session("shared", None), session("open", "A", active=True)],
        [record(status="late"), record(sid="shared", status="excused"), record("bob", "shared"),
         record("alice", "b"), record("removed", "a")],
    )
    stats = {row.person_id: row for row in await reports.person_stats(7, None, db)}
    assert set(stats) == {"alice", "bob"}
    assert (stats["alice"].total_sessions, stats["alice"].present_count, stats["alice"].attendance_rate) == (2, 2, 100)
    assert (stats["bob"].total_sessions, stats["bob"].present_count, stats["bob"].attendance_rate) == (2, 1, 50)
    daily = (await reports.daily_stats(7, None, db))[-1]
    assert (daily.total_sessions, daily.total_present, daily.attendance_rate) == (3, 3, 75)


@pytest.mark.asyncio
async def test_open_unmarked_or_absent_sessions_are_not_assessed_until_closed():
    db = database([person(), person("bob")], [session(active=True)], [record("bob", status="absent")])
    stats = await reports.person_stats(1, None, db)
    assert all(row.total_sessions == 0 and not row.is_defaulter for row in stats)
    assert (await reports.heatmap(1, None, db))["persons"][0]["data"] == [None]
    assert (await reports.daily_stats(1, None, db))[0].total_sessions == 0
    db.sessions.docs[0]["is_active"] = False
    stats = await reports.person_stats(1, None, db)
    assert all(row.total_sessions == 1 and row.is_defaulter for row in stats)
    assert (await reports.heatmap(1, None, db))["persons"][0]["data"] == [0]


@pytest.mark.asyncio
async def test_open_session_with_attendance_is_assessed_only_for_checked_in_person():
    db = database([person(), person("bob")], [session(active=True)], [record(status="late")])
    stats = {row.person_id: row for row in await reports.person_stats(1, None, db)}
    assert stats["alice"].attendance_rate == 100
    assert stats["bob"].total_sessions == 0
    daily = (await reports.daily_stats(1, None, db))[0]
    assert (daily.total_sessions, daily.total_present, daily.attendance_rate) == (1, 1, 100)


@pytest.mark.asyncio
async def test_enrollment_day_excludes_earlier_sessions_and_allows_same_local_day():
    db = database([person(enrolled_at=local(23, 23))],
                  [session("before", day=22), session("same-day")],
                  [record(sid="before"), record(sid="same-day")])
    row = (await reports.person_stats(7, None, db))[0]
    assert (row.total_sessions, row.present_count, row.attendance_rate) == (1, 1, 100)
    heatmap = await reports.heatmap(2, None, db)
    assert heatmap["persons"][0]["data"] == [None, 1]


@pytest.mark.asyncio
async def test_exact_local_date_window_and_cross_midnight_checkin():
    sessions = [session("too-old", day=21), session("yesterday", day=22), session("today"), session("future", day=24)]
    sessions[1]["started_at"] = local(22, 23, 50).astimezone(timezone.utc).replace(tzinfo=None)
    db = database([person()], sessions, [
        record(sid="too-old"), record(sid="yesterday", marked_at=local(23, 0, 5)), record(sid="future"),
    ])
    daily = await reports.daily_stats(2, None, db)
    assert [row.date for row in daily] == ["2026-10-22", "2026-10-23"]
    assert [row.total_present for row in daily] == [1, 0]
    assert [row.total_sessions for row in daily] == [1, 1]
    row = (await reports.person_stats(2, None, db))[0]
    assert (row.total_sessions, row.present_count, row.attendance_rate) == (2, 1, 50)
    one_day = (await reports.person_stats(1, None, db))[0]
    assert (one_day.total_sessions, one_day.present_count) == (1, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize("reverse", [False, True])
async def test_heatmap_does_not_hide_a_missed_session_on_a_day_with_multiple_sessions(reverse):
    attendance = [record(sid="first"), record(sid="second", status="absent")]
    if reverse:
        attendance.reverse()
    db = database([person()], [session("first"), session("second")], attendance)
    assert (await reports.heatmap(1, None, db))["persons"][0]["data"] == [0]
    assert (await reports.daily_stats(1, None, db))[0].attendance_rate == 50


@pytest.mark.asyncio
async def test_department_filter_is_literal_case_insensitive_and_includes_shared_sessions():
    db = database([person(department=" a+b "), person("bob", "AB")],
                  [session(department="A+B"), session("common", "  "), session("other", "AB")],
                  [record(), record(sid="common")])
    row = (await reports.person_stats(1, " A+B ", db))[0]
    assert (row.person_id, row.total_sessions, row.present_count) == ("alice", 2, 2)
    assert (await reports.daily_stats(1, " A+B ", db))[0].total_sessions == 2
    assert len((await reports.heatmap(1, " A+B ", db))["persons"]) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("reverse", [False, True])
async def test_mixed_objectid_duplicates_count_once_using_latest_status(reverse):
    sid = ObjectId()
    attendance = [record(sid=sid, status="present", marked_at=local(23, 9)),
                  record(sid=str(sid), status="absent", marked_at=local(23, 10), rid="2")]
    if reverse:
        attendance.reverse()
    db = database([person()], [session(sid)], attendance)
    row = (await reports.person_stats(1, None, db))[0]
    assert (row.total_sessions, row.present_count, row.attendance_rate) == (1, 0, 0)


@pytest.mark.asyncio
async def test_zero_sessions_is_neutral_without_fake_denominator_or_false_warning():
    db = database([person()])
    row = (await reports.person_stats(1, None, db))[0]
    assert (row.total_sessions, row.present_count, row.attendance_rate, row.is_defaulter) == (0, 0, 0, False)
    assert (await reports.heatmap(1, None, db))["persons"][0]["data"] == [None]
    assert db.attendance.queries == []


def test_shared_policy_handles_legacy_naive_utc_timestamps_and_missing_status():
    session_doc = session(department="   ")
    session_doc["started_at"] = datetime(2026, 10, 22, 18)  # 23 Oct in Vietnam
    assert session_applies_to_person(session_doc, person(enrolled_at=local(23, 23)))
    assert not session_applies_to_person(session_doc, person(enrolled_at=local(24)))
    assert attendance_status({}) == "present"
    assert is_session_assessed(session(active=True), {})
    assert is_session_assessed({**session(active=True), "ended_at": local(23, 10)})
