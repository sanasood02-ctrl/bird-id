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
    """Read every scientific name from the checklist into a set.

    A set is a collection built for fast "is this in here?" checks.
    """
    names = set()
    with open(CHECKLIST_FILE, encoding="utf-8", newline="") as file:
        # DictReader reads each row as a dictionary, using the header row
        # ("scientific_name", "english_name") as the keys.
        for row in csv.DictReader(file):
            names.add(normalise(row["scientific_name"]))
    return names


# Load the checklist once, when this file is first imported, instead of
# re-reading 11,131 names on every click.
KNOWN_SPECIES = load_checklist()


def is_known_species(scientific_name):
    """Return True if the scientific name is on the checklist, else False."""
    return normalise(scientific_name) in KNOWN_SPECIES
