"""Regression cases from actual learner lookup failures, using the shipped index."""
import gzip
import hashlib
import json
from pathlib import Path
import pytest
from core.toeic_lexicon import lookup_result, read_words, search_ids, card_view, all_words, lexicon
from core.dictionary_text import normalize, valid_ipa

ROOT=Path(__file__).resolve().parents[2]

@pytest.mark.parametrize("query,expected", [
    ("xin chào","hello"),("xin chao","hello"),("tình yêu","love"),("tinh yeu","love"),
    ("hoa don","invoice"),("hóa đơn","invoice"),("   INVOICE  ","invoice"),
    ("accommodation","accommodation"),("social media","social media"),
    ("work from home","work from home"),("went","go"),("studies","study"),
    ("café","café"),("résumé","résumé"),("resume","resume"),
])
def test_real_queries_return_a_useful_first_result(query, expected):
    ids,_,_=lookup_result(query=query)
    assert read_words(ids[:1])[0]["term"] == expected


@pytest.mark.parametrize("query,expected",[("e mail","email"),("e‐mail","email"),("check   in","check in"),("wi fi","wi-fi"),("WiFi","wi-fi"),("you’re welcome","you're welcome")])
def test_punctuation_whitespace_and_aliases_do_not_hide_words(query, expected):
    assert expected in {w["term"] for w in read_words(search_ids(query=query)[:5])}


@pytest.mark.parametrize("query,expected",[("accomodation","accommodation"),("recieve","receive"),("inovice","invoice"),("enviroment","environment")])
def test_typo_suggestions_do_not_silently_rewrite_the_query(query, expected):
    ids,suggestions,_=lookup_result(query=query)
    assert not ids and expected in suggestions


def test_hidden_results_have_a_global_escape_route_and_whole_word_matching():
    ids,_,global_count=lookup_result(deck="ngsl",query="invoice",letter="z")
    assert not ids and global_count > 0
    ids,_,_=lookup_result(query="invoice")
    words=read_words(ids[:30])
    assert words[0]["term"] == "invoice"
    assert all("invoice" in normalize(w["term"]+" "+" ".join(w["inflections"])) or "invoice" in normalize(w["meaning_vi"]) for w in words)


def test_english_definition_search_is_explicit_and_queries_are_literal():
    assert any(w["term"]=="smartphone" for w in read_words(search_ids("tsl","applications",scope="full")[:50]))
    assert search_ids(query='!!!') == ()
    assert search_ids(query='zzzxqv_987_no_dictionary_entry') == ()
    assert search_ids(query='" OR 1=1 --') == ()


def test_full_vietnamese_senses_examples_and_pronunciation_provenance():
    accommodation=read_words(search_ids(query="accommodation")[:1])[0]
    assert "chỗ ở" in accommodation["meaning_vi"]
    assert any("thích nghi" in s["text"] for s in accommodation["senses_vi"])
    assert accommodation["examples"][0]["en"] and accommodation["examples"][0]["vi"]
    love=read_words(search_ids(query="love")[:1])[0]
    assert {"n","v"} <= {s["pos"] for s in love["senses_vi"]}
    assert "tình yêu" in love["meaning_vi"]
    card=card_view(read_words(search_ids(query="went")[:1])[0],query="went")
    assert card["match_kind"]=="form" and card["meaning_language"]=="vi"
    for word in all_words():
        assert word["meaning_vi"] and word["senses_vi"]
        assert not word["ipa"] or valid_ipa(word["ipa"])
        if word["ipa"]: assert word.get("ipa_source")


def test_every_legacy_headword_keeps_its_review_id():
    core=json.loads((ROOT/"backend/data/toeic/lexicon.json").read_text(encoding="utf-8"))
    ext=json.loads(gzip.decompress((ROOT/"backend/data/toeic/lexicon_100k.json.gz").read_bytes()))
    before={w["term"]:w["id"] for w in core["words"]}
    before.update({r[0]:f"lex-th-{i:06d}" for i,r in enumerate(ext,1)})
    checked=0
    for word in all_words():
        if word["term"] in before:
            assert word["id"]==before[word["term"]]; checked+=1
    assert checked==147245


def test_published_index_and_shards_have_pinned_hashes_and_complete_meanings():
    meta=lexicon(); folder=ROOT/"frontend/public/toeic/dictionary"
    assert (ROOT/"backend/data/toeic/dictionary-meta.json").read_bytes()==(ROOT/"frontend/public/toeic/dictionary-meta.json").read_bytes()
    for name,expected in meta["files"].items():
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected["sha256"]
    rows=json.loads(gzip.decompress((folder/"search.json.gz").read_bytes()))
    assert len(rows)==meta["word_count"] and len({r[0] for r in rows})==len(rows)
    total=0
    for name in meta["files"]:
        if name.startswith("entries-"):
            shard=json.loads(gzip.decompress((folder/name).read_bytes()))
            assert len(shard)<=512
            assert all(w["meaning_vi"] for w in shard.values())
            total+=len(shard)
    assert total==len(rows)
