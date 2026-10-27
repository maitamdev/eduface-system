"""Exercise real authenticated pagination and FSRS writes against isolated Mongo."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from tests.test_mongo_integration import live, URI
from tests.test_toeic_integration import student

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(not URI, reason="Local Mongo replica set required")]


async def test_lexicon_pagination_search_and_private_progress(live):
    db, http = live
    _, headers = await student(db)
    assert (await http.get("/api/toeic/lexicon")).status_code == 403
    first = (await http.get("/api/toeic/lexicon?deck=ngsl&limit=30", headers=headers)).json()
    second = (await http.get("/api/toeic/lexicon?deck=ngsl&limit=30&offset=30", headers=headers)).json()
    assert first["total"] == 2809 and first["word_count"] == 4060
    assert len(first["items"]) == len(second["items"]) == 30
    assert not {w["id"] for w in first["items"]} & {w["id"] for w in second["items"]}
    assert first["items"][0]["term"] == "the" and first["license"] == "CC BY-SA 4.0"
    cafe = (await http.get("/api/toeic/lexicon", params={"deck":"tsl", "q":"cafe"}, headers=headers)).json()
    assert any(w["term"] == "café" and w["meaning_language"] == "en" and w["ipa"] == "/kæˈfeɪ/" for w in cafe["items"])
    vi_search = (await http.get("/api/toeic/lexicon", params={"deck":"tsl", "q":"hoa don"}, headers=headers)).json()
    assert any(w["term"] == "invoice" and "hóa đơn" in w["meaning_vi"] for w in vi_search["items"])
    pos_letter = (await http.get("/api/toeic/lexicon", params={"deck":"tsl", "pos":"v", "letter":"r"}, headers=headers)).json()
    assert pos_letter["total"] > 0 and all("v" in w["pos"] and w["term"].startswith("r") for w in pos_letter["items"])
    legacy = (await http.get("/api/toeic/vocabulary", headers=headers)).json()
    assert len(legacy) == 200 and all(not w["id"].startswith("lex-") for w in legacy)
    catalog = (await http.get("/api/toeic/catalog", headers=headers)).json()
    assert catalog["lexicon_count"] == 4060 and catalog["vocabulary_count"] == 200


async def test_new_lexicon_review_is_idempotent_private_and_respects_due_date(live, monkeypatch):
    db, http = live
    uid, headers = await student(db)
    _, other = await student(db, "another-lexicon-student")
    card = (await http.get("/api/toeic/lexicon?deck=tsl&q=smartphone", headers=headers)).json()["items"][0]
    assert card["term"] == "smartphone"
    body = {"rating":3, "expected_version":0, "event_id":str(uuid4())}
    url = f"/api/toeic/vocabulary/{card['id']}/review"
    saved = await http.post(url, json=body, headers=headers)
    assert saved.status_code == 200, saved.text
    retry = await http.post(url, json=body, headers=headers)
    assert retry.status_code == 200 and retry.json() == saved.json()
    stored = await db.toeic_cards.find_one({"user_id":uid, "vocabulary_id":card["id"]})
    assert stored["reviews"] == stored["version"] == 1
    premature = await http.post(url, headers=headers, json=body | {"event_id":str(uuid4()), "expected_version":1})
    assert premature.status_code == 409
    own = (await http.get("/api/toeic/lexicon?state=learned", headers=headers)).json()
    foreign = (await http.get("/api/toeic/lexicon?state=learned", headers=other)).json()
    assert own["total"] == 1 and foreign["total"] == 0
    assert (await http.get("/api/toeic/progress", headers=headers)).json()["cards_learned"] == 1
    assert (await http.get("/api/toeic/progress", headers=other)).json()["cards_learned"] == 0
    assert (await http.get("/api/toeic/lexicon?state=due", headers=headers)).json()["total"] == 0
    later = datetime.fromisoformat(saved.json()["due"]) + timedelta(seconds=1)
    monkeypatch.setattr("routers.toeic.now", lambda: later.astimezone(timezone.utc))
    due = (await http.get("/api/toeic/lexicon?state=due", headers=headers)).json()
    assert due["total"] == 1 and due["items"][0]["id"] == card["id"]
    again = await http.post(url, headers=headers, json=body | {"event_id":str(uuid4()), "expected_version":1})
    assert again.status_code == 200 and again.json()["version"] == 2


@pytest.mark.parametrize("query", ["limit=51", "limit=0", "offset=-1", "offset=10001", "deck=unknown", "state=unknown", "q=" + "a" * 121])
async def test_lexicon_rejects_unbounded_or_invalid_filters(live, query):
    db, http = live
    _, headers = await student(db)
    assert (await http.get("/api/toeic/lexicon?" + query, headers=headers)).status_code == 422


async def test_unknown_lexicon_card_cannot_be_written(live):
    db, http = live
    _, headers = await student(db)
    result = await http.post("/api/toeic/vocabulary/lex-not-a-card/review", headers=headers,
                             json={"rating":3, "expected_version":0, "event_id":str(uuid4())})
    assert result.status_code == 404
    assert await db.toeic_cards.count_documents({}) == 0
