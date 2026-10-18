"""The identification logic, kept separate from the Streamlit page code
so the evaluation script can use these functions directly."""


def build_description(main_text, specifics):
    """Join the main description and any filled-in specifics into one labeled text.

    specifics is a dictionary like {"Beak type": "short and conical", ...}.
    Empty boxes are left out, so the result only contains what the user typed.
    """
    lines = []
    if main_text.strip() != "":
        lines.append("Description: " + main_text.strip())
    for label, value in specifics.items():
        if value.strip() != "":
            lines.append(label + ": " + value.strip())
    # "\n" is a line break, so each part goes on its own line.
    return "\n".join(lines)


def identify_bird(description):
    """Identify a bird from a description and return the result as a dictionary.

    Every result has the same shape:
      "outcome": "confident", "possible", or "not_enough"
      "species": a list of species (1 for confident, 2-3 for possible,
                 empty for not_enough). Each species has a common_name,
                 scientific_name, and distinguishing_trait (only used for
                 possible matches; empty otherwise).

    Demo version: ignores the description and always returns the same fake
    confident result, so the app can be built without an API key.
    """
    return {
        "outcome": "confident",
        "species": [
            {
                "common_name": "House Sparrow",
                "scientific_name": "Passer domesticus",
                "distinguishing_trait": "",
            }
        ],
    }
