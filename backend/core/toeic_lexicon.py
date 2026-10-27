"""Local, separately licensed English lexicon; never fetched at request time."""
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data/toeic/lexicon.json"


def normalize(value):
    return "".join(c for c in unicodedata.normalize("NFKD", value.casefold().replace("e-mail", "email"))
                   if not unicodedata.combining(c)).strip()


@lru_cache(maxsize=1)
def lexicon():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["license"] == "CC BY-SA 4.0"
    assert len(data["words"]) == data["word_count"]
    assert len({w["id"] for w in data["words"]}) == data["word_count"]
    return data


@lru_cache(maxsize=1)
def index():
    return {w["id"]: w for w in lexicon()["words"]}


@lru_cache(maxsize=1)
def search_text():
    return {w["id"]: normalize(w["term"] + " " + " ".join(d["text"] for d in w["definitions"]))
            for w in lexicon()["words"]}


def search_words(deck="all", query=""):
    query = normalize(query)
    words = [w for w in lexicon()["words"]
             if (deck == "all" or any(s["id"] == deck for s in w["lists"]))
             and (not query or query in search_text()[w["id"]])]
    if deck != "all":
        words.sort(key=lambda w: (next(s["rank"] for s in w["lists"] if s["id"] == deck) or 100000, w["term"]))
    if query:
        # Exact headword matches precede matches found only in a definition.
        words.sort(key=lambda w: (normalize(w["term"]) != query, not normalize(w["term"]).startswith(query)))
    return words


def card_view(word, stored=None):
    current = stored or {}
    return word | {"lesson_id": "open-lexicon", "meaning": " / ".join(dict.fromkeys(d["text"] for d in word["definitions"])),
                   "example": "", "version": current.get("version", 0), "due": current.get("due"),
                   "reviews": current.get("reviews", 0)}
