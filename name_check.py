"""Check species names against the official AviList bird checklist,
to catch made-up or wrong scientific names."""

import csv
from pathlib import Path

# The checklist sits in the data folder next to this file.
CHECKLIST_FILE = Path(__file__).parent / "data" / "avilist_species.csv"


def normalise(name):
    """Lowercase the name and squash extra spaces, so "passer  Domesticus"
    and "Passer domesticus" count as the same name."""
    return " ".join(name.split()).lower()


def load_checklist():
    """Read the checklist and return two things:
      - a set of every scientific name (a set is built for fast
        "is this in here?" checks)
      - a dictionary from each English name to its scientific name
    """
    scientific_names = set()
    scientific_from_english = {}
    with open(CHECKLIST_FILE, encoding="utf-8", newline="") as file:
        # DictReader reads each row as a dictionary, using the header row
        # ("scientific_name", "english_name") as the keys.
        for row in csv.DictReader(file):
            scientific_names.add(normalise(row["scientific_name"]))
            scientific_from_english[normalise(row["english_name"])] = row["scientific_name"]
    return scientific_names, scientific_from_english


# Load the checklist once, when this file is first imported, instead of
# re-reading 11,131 names on every click.
KNOWN_SPECIES, SCIENTIFIC_FROM_ENGLISH = load_checklist()


def is_known_species(scientific_name):
    """Return True if the scientific name is on the checklist, else False."""
    return normalise(scientific_name) in KNOWN_SPECIES


def check_species(species):
    """Check one species from Haiku against the checklist.

    Returns two things: a status, and the scientific name to use.
      "verified":   the scientific name is on the checklist.
      "corrected":  the scientific name is not, but the common name exactly
                    matches a checklist English name, so the checklist's
                    scientific name is used instead.
      "unverified": neither name matches; don't show it as a real species.
    """
    if is_known_species(species["scientific_name"]):
        return "verified", species["scientific_name"]

    checklist_name = SCIENTIFIC_FROM_ENGLISH.get(normalise(species["common_name"]))
    if checklist_name is not None:
        return "corrected", checklist_name

    return "unverified", species["scientific_name"]
