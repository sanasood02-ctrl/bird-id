"""The identification logic, kept separate from the Streamlit page code
so the evaluation script can use these functions directly."""

import json

import anthropic

MODEL = "claude-haiku-4-5"

# Haiku's instructions (the "system prompt"). It follows these for every request.
SYSTEM_PROMPT = """You are a careful bird-identification assistant. The user describes a \
bird they saw in plain language, sometimes with labeled details such as size and \
shape, wing type, colour patterns, beak type, foot type, and behaviours. The \
location where they saw it is always given.

Never guess. First, in "reasoning", list the species the description could fit. \
For each look-alike, say whether a detail in the description rules it out, and name \
that detail. Only then choose one outcome, based on how many species remain:
- "confident": the description rules out all similar species (taking location and \
season into account). Return exactly 1 species.
- "possible": 2 or 3 species remain. Return them, and for each one give the \
distinguishing trait: the field mark that would tell it apart from the others.
- "not_enough": more than 3 species remain. Return an empty species list.
When you are unsure between two outcomes, pick the more cautious one \
("possible" over "confident", "not_enough" over "possible").

Only rule out a species using details the user actually wrote. Never add details \
they did not mention. A vague size word on its own ("small", "big") does not rule \
out a look-alike; a size compared to a known bird ("smaller than a robin") can.

For each species give its common English name and its scientific name. The \
scientific name must be the species name in the form "Genus species" (two words), \
never a family, order or genus name on its own. Use AviList v2025 names; every name \
is checked against the AviList global bird checklist. For a "confident" result, \
leave distinguishing_trait as an empty string. Do not write fun facts or any other \
extra information."""

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

    With an API key, asks Claude Haiku. Without one, returns a demo result.
    Raises IdentificationError (with a friendly message) if Haiku can't be asked.
    """
    if api_key is None:
        return demo_identify(description)
    return ask_haiku(description, api_key)


class IdentificationError(Exception):
    """Raised when the bird could not be identified because something went
    wrong (no internet, bad key, unreadable answer...). Its message is a
    friendly sentence that can be shown to the user as it is."""


def ask_haiku(description, api_key):
    """Ask Claude Haiku to identify the bird, and return its answer as a dictionary.

    Raises IdentificationError with a friendly message if anything goes wrong.
    """
    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": description}],
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
