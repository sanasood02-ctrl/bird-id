"""The RAG part of the app (Retrieval-Augmented Generation). It finds which of
the owner's field records match a description, so they can be handed to Haiku
along with it. Records are matched by the words they share with the
description, which keeps the matching plain Python with no extra libraries."""

import re
from pathlib import Path

RECORDS_FILE = Path(__file__).parent / "data" / "field_records.txt"

# At most this many records are handed to Haiku for one description.
MAX_RECORDS = 2

# A record must share at least this many meaningful words with the description.
# Below this, the match is too weak to be worth showing Haiku.
MIN_SHARED_WORDS = 4

# Words that say nothing about which bird it is. Without this list, nearly every
# record would "match" just by sharing words like "the". It also holds the labels
# the form adds ("Beak type: ..."), and words most of the records use.
IGNORED_WORDS = {
    "a", "an", "and", "are", "around", "at", "but", "by", "for", "from", "had",
    "has", "have", "in", "into", "is", "it", "its", "near", "of", "on", "or",
    "out", "over", "that", "the", "then", "this", "to", "under", "very", "was",
    "were", "when", "which", "while", "with", "i", "my", "saw", "seen", "often",
    "found", "some", "like", "looked", "looks", "quite", "really",
    "description", "location", "located", "size", "shape", "wing", "type",
    "colour", "patterns", "beak", "foot", "behaviours",
    "bird", "birds", "small", "medium", "sized", "large", "big", "male", "female",
}


def load_records():
    """Read the field records file and return a list of records. Each record
    is a dictionary with its "name" (the first line) and its full "text"."""
    all_text = RECORDS_FILE.read_text(encoding="utf-8")
    records = []
    # A blank line ("\n\n") separates one record from the next.
    for block in all_text.strip().split("\n\n"):
        first_line = block.split("\n")[0]
        # Some first lines end in a colon ("Jungle babbler:"); the name doesn't need it.
        records.append({"name": first_line.strip().rstrip(":"), "text": block.strip()})
    return records


def meaningful_words(text):
    """Return the set of lowercase words in the text, minus the ignored ones.
    A set keeps each word once, so repeating a word doesn't raise the score."""
    # re.findall picks out every run of letters, which leaves punctuation behind.
    words = set(re.findall(r"[a-z]+", text.lower()))
    return words - IGNORED_WORDS


def get_score(match):
    """Return a match's score. Used to tell sort() what to sort by."""
    return match["score"]


def find_matching_records(description):
    """Return the records that best match the description (best first).
    The list is empty if no record shares enough words with it."""
    description_words = meaningful_words(description)
    matches = []
    for record in load_records():
        # "&" keeps only the words that appear in both sets.
        shared_words = description_words & meaningful_words(record["text"])
        if len(shared_words) >= MIN_SHARED_WORDS:
            matches.append({"score": len(shared_words), "record": record})

    matches.sort(key=get_score, reverse=True)

    best_records = []
    for match in matches[:MAX_RECORDS]:
        best_records.append(match["record"])
    return best_records
