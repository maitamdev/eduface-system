"""Pure normalization shared by the dictionary importer and query service."""
import re
import unicodedata


def normalize(value):
    value = unicodedata.normalize("NFKC", value).casefold().replace("đ", "d")
    value = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
    # Curly apostrophes, hyphens, tabs and multiple spaces are equivalent for lookup.
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def compact(value):
    return normalize(value).replace(" ", "")


def valid_ipa(value):
    return bool(value and not any(c in value for c in "?\ufffd0123456789") and len(value) < 180)
