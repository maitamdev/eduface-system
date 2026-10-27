"""Regression checks for licensed imports, stable legacy content and vocabulary."""
import hashlib
import json
from collections import Counter
from pathlib import Path

from core.toeic_content import content, select_questions, PART_COUNTS
from core.toeic_lexicon import lexicon, search_words, card_view

ROOT = Path(__file__).resolve().parents[2]


def test_all_legacy_scored_questions_are_unchanged():
    # Fingerprint of all 727 question objects in the approved c489794 release.
    questions = content()["questions"][:727]
    digest = hashlib.sha256(json.dumps(questions, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert digest == "ca5725a196341c9e6bd47e4da0949425f4dfc4258a0bf27a6024fbebba4e2bae"


def test_complete_upstream_inventory_is_accounted_for_and_translated():
    data = content()
    snapshot = json.loads((ROOT / "backend/data/toeic/vendor/ocean-complete-snapshot.json").read_text(encoding="utf-8"))
    upstream = {q["id"] for q in snapshot["questions"]}
    imported = {q["provenance"]["upstream_id"] for q in data["questions"] if q.get("provenance", {}).get("upstream_id")}
    excluded = set(data["expansion"]["excluded"])
    assert len(upstream) == 1107 and len(imported) == 1048 and len(excluded) == 59
    assert imported | excluded == upstream and not imported & excluded
    assert len(data["questions"][727:]) == 649
    for question in data["questions"][727:]:
        assert any(ord(c) > 127 for c in question["explanation"])
        assert not any("\u4e00" <= c <= "\u9fff" for c in question["explanation"])
        assert question["provenance"]["license"] == "MIT"
        assert snapshot["revision"] in question["provenance"]["url"]
        if question["part"] == 6:
            assert question["passage"].count("_____") == 4


def test_three_complete_full_forms_are_disjoint():
    forms = [form for form in content()["exams"] if form["type"] == "full"]
    assert len(forms) == 3
    used = set()
    for form in forms:
        rows = select_questions("exam", exam_id=form["id"])
        assert len(rows) == 200 and form["minutes"] == 120
        assert Counter(q["part"] for q in rows) == PART_COUNTS
        ids = {q["id"] for q in rows}
        assert not ids & used
        used |= ids


def test_generated_forms_do_not_repeat_an_alternate_listening_context():
    for seed in range(30):
        groups = {}
        for question in select_questions("mock", seed=seed):
            if question["part"] in (3, 4):
                groups[question["group_id"]] = (question["part"], " ".join(question["transcript"].split()))
        assert len(set(groups.values())) == len(groups)


def test_real_photos_keep_their_own_license_and_image_credit():
    photos = [q for q in content()["questions"] if q.get("provenance", {}).get("image_license") == "Pexels License"]
    assert len(photos) == 5
    assert all("Pexels" in q["image_credit"] and "pexels.com/photo/" in q["provenance"]["image_source"] for q in photos)
    assert all("AI" not in q["image_credit"] and "MIT" not in q["image_credit"] for q in photos)


def test_lexicon_keeps_ranks_extra_entries_definitions_and_sharealike_notice():
    data = lexicon()
    assert data["word_count"] == len(data["words"]) == 4060
    assert data["license"] == "CC BY-SA 4.0"
    assert data["ranked_counts"] == {"ngsl": 2809, "tsl": 1250}
    words = {w["term"]: w for w in data["words"]}
    assert words["word"]["definitions"][0]["text"] != "Definition"
    assert len(words["criteria"]["definitions"]) == 2
    assert words["born"]["lists"] == [{"id": "tsl", "rank": None, "supplemental": True}]
    adapted = {w["term"] for w in data["words"] if any(d["adapted_by_dhv"] for d in w["definitions"])}
    assert adapted == {"by-law", "café", "e-book", "entrée", "résumé", "smartphone"}
    assert len(search_words("ngsl")) == 2809 and len(search_words("tsl")) == 1252
    for deck, count in data["ranked_counts"].items():
        ranks = [s["rank"] for w in data["words"] for s in w["lists"] if s["id"] == deck and s["rank"]]
        assert sorted(ranks) == list(range(1, count + 1))
    assert (ROOT / "backend/data/toeic/lexicon.json").read_bytes() == (ROOT / "frontend/public/toeic/lexicon.json").read_bytes()


def test_search_matches_accents_aliases_and_definitions_without_fabricating_examples():
    assert search_words("all", "e-mail")[0]["term"] == "email"
    assert any(w["term"] == "café" for w in search_words("tsl", "cafe"))
    assert any(w["term"] == "smartphone" for w in search_words("tsl", "applications"))
    assert search_words("all", "no-match-xyz-9911") == []
    card = card_view(search_words("tsl", "smartphone")[0])
    assert card["meaning_language"] == "en" and card["example"] == ""
    assert card["due"] is None and card["reviews"] == card["version"] == 0
