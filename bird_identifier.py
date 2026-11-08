"""The identification logic, kept separate from the Streamlit page code
so the evaluation script can use these functions directly."""

import json
from pathlib import Path

import anthropic

from rag import find_matching_records

MODEL = "claude-haiku-4-5"

# Haiku's instructions (the "system prompt") live in this skill file, so the
# same rules can also be used as a Claude Code skill.
SKILL_FILE = Path(__file__).parent / ".claude" / "skills" / "identify-bird" / "SKILL.md"
FIELDNOTES_FILE = Path(__file__).parent / "fieldnotes.md"


def load_system_prompt():
    """Return Haiku's instructions: the skill file without its settings block,
    followed by the owner's field notes, exactly as written."""
    file_text = SKILL_FILE.read_text(encoding="utf-8")
    # The file starts with settings between two "---" lines, so splitting at
    # the first two "---" leaves the instructions in the last piece.
    instructions = file_text.split("---", 2)[2].strip()
    field_notes = FIELDNOTES_FILE.read_text(encoding="utf-8")
    return instructions + "\n\nThe owner's birdwatching field notes, for reference:\n\n" + field_notes


# Haiku follows these instructions for every request.
SYSTEM_PROMPT = load_system_prompt()

# The fixed shape every answer must have (a JSON schema). It matches the demo
# results exactly, so the rest of the app works the same in both modes.
RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        # Listed first, so Haiku works through the look-alikes before deciding.
        "reasoning": {"type": "string"},
        "outcome": {"type": "string", "enum": ["confident", "possible", "not_enough"]},
        "species": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "common_name": {"type": "string"},
                    "scientific_name": {"type": "string"},
                    "distinguishing_trait": {"type": "string"},
                },
                "required": ["common_name", "scientific_name", "distinguishing_trait"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["reasoning", "outcome", "species"],
    "additionalProperties": False,
}


def has_description(main_text, specifics):
    """Return True if the user described the bird in at least one box.
    (The location alone is not a description of the bird.)"""
    if main_text.strip() != "":
        return True
    for value in specifics.values():
        if value.strip() != "":
            return True
    return False


def build_description(main_text, location, specifics):
    """Join the main description, the location and any filled-in specifics
    into one labeled text.

    specifics is a dictionary like {"Beak type": "short and conical", ...}.
    Empty boxes are left out, so the result only contains what the user typed.
    """
    lines = []
    if main_text.strip() != "":
        lines.append("Description: " + main_text.strip())
    if location.strip() != "":
        lines.append("Location: " + location.strip())
    for label, value in specifics.items():
        if value.strip() != "":
            lines.append(label + ": " + value.strip())
    # "\n" is a line break, so each part goes on its own line.
    return "\n".join(lines)


def identify_bird(description, api_key=None):
    """Identify a bird from a description and return the result as a dictionary.

    Every result has the same shape:
      "reasoning": Haiku's check of the look-alikes (not shown on the page;
                   saved by the evaluation script to help explain mistakes)
      "outcome": "confident", "possible", or "not_enough"
      "species": a list of species (1 for confident, 2-3 for possible,
                 empty for not_enough). Each species has a common_name,
                 scientific_name, and distinguishing_trait (only used for
                 possible matches; empty otherwise).
      "records_used": names of the owner's field records that matched the
                      description (see rag.py); empty if none did.

    With an API key, asks Claude Haiku. Without one, returns a demo result.
    Raises IdentificationError (with a friendly message) if Haiku can't be asked.
    """
    records = find_matching_records(description)
    if api_key is None:
        result = demo_identify(description)
    else:
        result = ask_haiku(description, api_key, records)

    # Added here rather than by Haiku, so real and demo results match exactly.
    result["records_used"] = [record["name"] for record in records]
    return result


def add_records_to_message(description, records):
    """Return the text to send Haiku: the description, then any matching records."""
    if not records:
        return description
    message = description + "\n\nField records from the app's owner:"
    for record in records:
        message = message + "\n\n" + record["text"]
    return message


class IdentificationError(Exception):
    """Raised when the bird could not be identified because something went
    wrong (no internet, bad key, unreadable answer...). Its message is a
    friendly sentence that can be shown to the user as it is."""


def ask_haiku(description, api_key, records):
    """Ask Claude Haiku to identify the bird, and return its answer as a dictionary.
    records is the list of field records to include with the description.

    Raises IdentificationError with a friendly message if anything goes wrong.
    """
    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": add_records_to_message(description, records)}],
            # Structured outputs: the reply must be JSON matching RESULT_SCHEMA.
            output_config={"format": {"type": "json_schema", "schema": RESULT_SCHEMA}},
            # temperature 0 = the same description gets the same answer every time,
            # which keeps the evaluation fair. (This SDK version no longer lists
            # temperature as a setting, so it is passed through extra_body.)
            extra_body={"temperature": 0},
        )
    # Each "except" catches one kind of failure and swaps the technical error
    # for a friendly message. The first matching one is used.
    except anthropic.APIConnectionError:
        # No internet, or Anthropic did not answer in time.
        raise IdentificationError(
            "Couldn't reach the identification service. "
            "Check your internet connection and try again."
        )
    except anthropic.AuthenticationError:
        raise IdentificationError("The app's API key isn't working. Please check the key in secrets.toml.")
    except anthropic.BadRequestError as error:
        # An empty account is reported as a "bad request" that mentions credit.
        if "credit" in str(error).lower():
            raise IdentificationError("The identification service is out of credit right now.")
        raise IdentificationError("Something went wrong asking for an identification. Please try again.")
    except (anthropic.RateLimitError, anthropic.OverloadedError,
            anthropic.InternalServerError, anthropic.ServiceUnavailableError):
        raise IdentificationError("The identification service is busy. Please try again in a moment.")
    except anthropic.APIError:
        # Any other problem on Anthropic's side.
        raise IdentificationError("Something went wrong asking for an identification. Please try again.")

    # "end_turn" means Haiku finished normally. Anything else (e.g. it ran out
    # of room with "max_tokens") means the answer may be cut off.
    if response.stop_reason != "end_turn":
        raise IdentificationError("Something went wrong reading the result. Please try again.")

    # The JSON answer is in the reply's text block (None if there isn't one).
    text = next((block.text for block in response.content if block.type == "text"), None)
    if text is None:
        raise IdentificationError("Something went wrong reading the result. Please try again.")

    # json.loads turns the JSON text into a Python dictionary. It fails with
    # a JSONDecodeError if the text is not valid JSON.
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        raise IdentificationError("Something went wrong reading the result. Please try again.")

    # The schema can't limit the list to 3 species, so do it here.
    result["species"] = result["species"][:3]
    return result


# Demo results need a "reasoning" too, to keep the same shape as real ones.
DEMO_REASONING = "Demo mode: sample result, no reasoning."


def demo_identify(description):
    """Demo version: returns a fake result so the app can be built without an
    API key. A keyword in the description picks which outcome to show:
      "vague"     -> not_enough
      "lookalike" -> possible
      "madeup"    -> confident, but for an invented species (to test the
                     missing-photo fallback and the name check)
      anything else -> confident
    """
    # .lower() makes the keyword check ignore upper/lower case.
    text = description.lower()

    if "vague" in text:
        return {"reasoning": DEMO_REASONING, "outcome": "not_enough", "species": []}

    if "madeup" in text:
        return {
            "reasoning": DEMO_REASONING,
            "outcome": "confident",
            "species": [
                {
                    "common_name": "Imaginary Warbler",
                    "scientific_name": "Fakeus birdus",
                    "distinguishing_trait": "",
                }
            ],
        }

    if "lookalike" in text:
        return {
            "reasoning": DEMO_REASONING,
            "outcome": "possible",
            "species": [
                {
                    "common_name": "House Sparrow",
                    "scientific_name": "Passer domesticus",
                    "distinguishing_trait": "Grey crown; male has a large black bib",
                },
                {
                    "common_name": "Eurasian Tree Sparrow",
                    "scientific_name": "Passer montanus",
                    "distinguishing_trait": "Chestnut crown and a black spot on a white cheek",
                },
                {
                    "common_name": "Spanish Sparrow",
                    "scientific_name": "Passer hispaniolensis",
                    "distinguishing_trait": "Heavy black streaks on the chest and sides",
                },
            ],
        }

    return {
        "reasoning": DEMO_REASONING,
        "outcome": "confident",
        "species": [
            {
                "common_name": "House Sparrow",
                "scientific_name": "Passer domesticus",
                "distinguishing_trait": "",
            }
        ],
    }
