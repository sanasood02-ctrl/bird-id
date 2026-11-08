"""Evaluation script: runs every test description in a CSV file through the
same identification function the app uses, compares the app's answers with
the expected answers, and saves a results table plus summary scores.

How to run it (from the bird-id folder, with the virtual environment active):
    python eval/run_eval.py                  demo mode (free, fake answers)
    python eval/run_eval.py --real           real Haiku answers (costs money:
                                             one API call per test row)
    python eval/run_eval.py my_tests.csv     use a different test file
"""

import csv
import math
import sys
import tomllib
from datetime import datetime
from pathlib import Path

# This script lives in the eval folder, but bird_identifier.py and
# name_check.py are one folder up. Adding that folder to sys.path (the list
# of places Python looks for files to import) lets us import them.
PROJECT_FOLDER = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_FOLDER))

from bird_identifier import (  # noqa: E402 (must come after the sys.path line)
    IdentificationError,
    build_description,
    has_description,
    identify_bird,
)
from name_check import check_species, is_known_species, normalise  # noqa: E402

EVAL_FOLDER = Path(__file__).parent
DEFAULT_TEST_FILE = EVAL_FOLDER / "test_cases.csv"
SECRETS_FILE = PROJECT_FOLDER / ".streamlit" / "secrets.toml"

# Each optional CSV column, paired with the label of the matching box on the
# Identify page, so the test text is built exactly like the form builds it.
SPECIFICS_COLUMNS = {
    "size_shape": "Size and shape",
    "wing_type": "Wing type",
    "colour_patterns": "Colour patterns",
    "beak_type": "Beak type",
    "foot_type": "Foot type",
    "behaviours": "Behaviours",
}
REQUIRED_COLUMNS = ["description", "location", "expected_outcome", "expected_species"]
OUTCOMES = ["confident", "possible", "not_enough"]

# Verdicts that count as a right answer when working out the accuracy.
RIGHT_VERDICTS = ["Correct", "Correctly declined"]
# The worst mistakes: the app confidently misleads the user.
WORST_VERDICTS = ["Wrong", "Guessed"]
ALL_VERDICTS = ["Correct", "Correctly declined", "Too cautious",
                "Lucky (overconfident)", "Wrong", "Guessed", "Error"]


def read_api_key():
    """Return the API key from .streamlit/secrets.toml, or None if there
    isn't one. The key is only passed on to Haiku; never print it."""
    if not SECRETS_FILE.exists():
        return None
    # tomllib needs the file opened in "rb" (read bytes) mode.
    with open(SECRETS_FILE, "rb") as file:
        return tomllib.load(file).get("ANTHROPIC_API_KEY")


def read_test_rows(test_file):
    """Read the test CSV and return its rows as a list of dictionaries.
    Completely empty rows (which spreadsheet apps sometimes add) are skipped."""
    # "utf-8-sig" also handles the invisible marker Excel puts at the start
    # of CSV files, which would otherwise end up in the first column's name.
    with open(test_file, encoding="utf-8-sig", newline="") as file:
        rows = []
        for row in csv.DictReader(file):
            # "or ''" turns a missing cell (None) into an empty string.
            if any((value or "").strip() != "" for value in row.values()):
                rows.append(row)
    return rows


def get_specifics(row):
    """Return the row's specifics as {box label: text}, like the form does."""
    specifics = {}
    for column, label in SPECIFICS_COLUMNS.items():
        specifics[label] = row.get(column) or ""
    return specifics


def find_problems(rows):
    """Check the test file before spending any money on API calls.
    Returns a list of problem messages (empty if everything is fine)."""
    if not rows:
        return ["The test file has no rows."]

    problems = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in rows[0]]
    if missing_columns:
        return ["Missing column(s): " + ", ".join(missing_columns)]

    # Row numbers start at 2, because row 1 of the spreadsheet is the header.
    for row_number, row in enumerate(rows, start=2):
        outcome = (row["expected_outcome"] or "").strip()
        species = (row["expected_species"] or "").strip()
        if not has_description(row["description"] or "", get_specifics(row)):
            problems.append(f"Row {row_number}: no description of the bird.")
        if (row["location"] or "").strip() == "":
            problems.append(f"Row {row_number}: location is empty.")
        if outcome not in OUTCOMES:
            problems.append(f"Row {row_number}: expected_outcome must be confident, possible or not_enough.")
        if outcome in ["confident", "possible"] and species == "":
            problems.append(f"Row {row_number}: expected_species is needed when an answer is expected.")
        if species != "" and not is_known_species(species):
            problems.append(f"Row {row_number}: '{species}' is not on the AviList checklist.")
    return problems


def get_verdict(expected_outcome, expected_species, app_outcome, app_species_names):
    """Compare the app's answer with the expected answer (see Step 17 in PLAN.md)."""
    if expected_outcome == "not_enough":
        if app_outcome == "not_enough":
            return "Correctly declined"
        return "Guessed"

    # From here on, an answer was expected.
    if app_outcome == "not_enough":
        return "Too cautious"
    if normalise(expected_species) not in app_species_names:
        return "Wrong"
    if app_outcome == expected_outcome:
        return "Correct"
    if expected_outcome == "confident":
        # The right species was among the app's possible matches.
        return "Too cautious"
    # Expected "possible", but the app was confident (and happened to be right).
    return "Lucky (overconfident)"


def evaluate_row(row, api_key):
    """Run one test row through the app's identification and return one
    row of the results table, as a dictionary."""
    full_description = build_description(row["description"] or "", row["location"], get_specifics(row))
    expected_outcome = row["expected_outcome"].strip()
    expected_species = (row["expected_species"] or "").strip()

    result_row = {
        "full_description": full_description,
        "expected_outcome": expected_outcome,
        "expected_species": expected_species,
        "app_outcome": "",
        "app_species": "",
        "name_check": "",
        "verdict": "",
        "records_used": "",
        "reasoning": "",
    }

    try:
        result = identify_bird(full_description, api_key)
    except IdentificationError as error:
        # Record the problem and carry on with the next row.
        result_row["verdict"] = "Error"
        result_row["reasoning"] = str(error)
        return result_row

    # Run each species through the same name check the app uses. Its
    # (possibly corrected) scientific name is the one compared with the
    # expected species, just like the app shows the corrected name.
    app_species_names = []
    shown_names = []
    statuses = []
    for species in result["species"]:
        status, scientific_name = check_species(species)
        app_species_names.append(normalise(scientific_name))
        shown_names.append(f"{species['common_name']} ({scientific_name})")
        statuses.append(status)

    result_row["app_outcome"] = result["outcome"]
    result_row["app_species"] = "; ".join(shown_names)
    result_row["name_check"] = "; ".join(statuses)
    result_row["reasoning"] = result["reasoning"]
    result_row["records_used"] = "; ".join(result["records_used"])
    result_row["verdict"] = get_verdict(expected_outcome, expected_species,
                                        result["outcome"], app_species_names)
    return result_row


def save_results(results, mode):
    """Save the results table as a new CSV in the eval folder, with the date
    and time in its name, so earlier runs are kept for comparison."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    results_file = EVAL_FOLDER / f"results_{mode}_{timestamp}.csv"
    with open(results_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    return results_file


def print_summary(results):
    """Print the summary scores."""
    # Rows that hit an error never got an answer, so they are not scored.
    scored = [row for row in results if row["verdict"] != "Error"]
    error_count = len(results) - len(scored)

    print()
    print("=== Summary ===")
    print(f"Rows tested: {len(results)}  (scored: {len(scored)}, errors: {error_count})")
    if not scored:
        return

    # Accuracy, with its 95% margin of error: how far the true accuracy could
    # be from this score, just because only a limited number of rows were tested.
    right_count = sum(1 for row in scored if row["verdict"] in RIGHT_VERDICTS)
    accuracy = right_count / len(scored)
    margin = 1.96 * math.sqrt(accuracy * (1 - accuracy) / len(scored))
    print(f"Accuracy: {accuracy:.0%} ± {margin:.0%}  ({right_count} of {len(scored)} rows right)")

    print()
    print("Verdicts:")
    for verdict in ALL_VERDICTS:
        count = sum(1 for row in results if row["verdict"] == verdict)
        print(f"  {verdict:<24}{count}")
    worst_count = sum(1 for row in scored if row["verdict"] in WORST_VERDICTS)
    print(f"Worst errors (Wrong + Guessed): {worst_count}")

    failed_names = sum(row["name_check"].count("unverified") for row in scored)
    print(f"Names that failed the name check: {failed_names}")

    print()
    print("Accuracy for each expected outcome:")
    for outcome in OUTCOMES:
        rows = [row for row in scored if row["expected_outcome"] == outcome]
        if rows:
            right = sum(1 for row in rows if row["verdict"] in RIGHT_VERDICTS)
            print(f"  {outcome:<12}{right / len(rows):.0%}  ({right} of {len(rows)})")

    # RAG only affects rows that matched a field record, so score those separately.
    rag_rows = [row for row in scored if row["records_used"] != ""]
    if rag_rows:
        right = sum(1 for row in rag_rows if row["verdict"] in RIGHT_VERDICTS)
        print()
        print(f"Rows given a field record: {len(rag_rows)}  ({right / len(rag_rows):.0%} right)")

    # Each line is one expected outcome; each column counts what the app said.
    print()
    print("Expected (rows) vs what the app said (columns):")
    print(" " * 14 + "".join(f"{outcome:>12}" for outcome in OUTCOMES))
    for expected in OUTCOMES:
        counts = ""
        for actual in OUTCOMES:
            count = sum(1 for row in scored
                        if row["expected_outcome"] == expected and row["app_outcome"] == actual)
            counts += f"{count:>12}"
        print(f"  {expected:<12}{counts}")


def main():
    # sys.argv is the list of words typed after "python": sys.argv[0] is the
    # script's name, and anything after it is an option or a file name.
    use_real_api = "--real" in sys.argv
    file_names = [word for word in sys.argv[1:] if word != "--real"]
    test_file = Path(file_names[0]) if file_names else DEFAULT_TEST_FILE

    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return

    rows = read_test_rows(test_file)
    problems = find_problems(rows)
    if problems:
        print("Please fix these problems in the test file first (nothing was run):")
        for problem in problems:
            print("  - " + problem)
        return

    if use_real_api:
        api_key = read_api_key()
        if api_key is None:
            print("No API key found in .streamlit/secrets.toml, so --real can't be used.")
            return
        mode = "real"
        print(f"REAL mode: asking Claude Haiku about {len(rows)} rows (one paid API call each).")
    else:
        # No key means identify_bird() returns its fake demo answers.
        api_key = None
        mode = "demo"
        print("DEMO mode: fake sample answers, no API calls. Add --real for real answers.")

    results = []
    for number, row in enumerate(rows, start=1):
        result_row = evaluate_row(row, api_key)
        results.append(result_row)
        print(f"Row {number} of {len(rows)}: {result_row['verdict']}")

    results_file = save_results(results, mode)
    print_summary(results)
    print()
    print(f"Full results saved to: {results_file}")


# Only run main() when this file is run as a script (not when imported).
if __name__ == "__main__":
    main()
