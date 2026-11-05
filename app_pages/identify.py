import streamlit as st

from bird_identifier import IdentificationError, build_description, has_description, identify_bird
from name_check import check_species
from wikipedia_lookup import download_photo, get_wikipedia_summary


def get_api_key():
    """Return the Anthropic API key from .streamlit/secrets.toml, or None if
    there isn't one. The key is only passed on to Haiku; never print or show it.
    """
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except FileNotFoundError:
        # There is no secrets.toml file at all, so there is no key.
        return None


def show_image_not_found(height):
    """A bordered box saying there is no photo, in the photo's place."""
    with st.container(border=True, height=height):
        st.caption("Image not found")


def show_photo(summary, width, placeholder_height):
    """Show the Wikipedia photo, or "Image not found" if there is no photo
    or it fails to download."""
    if summary is None or summary["photo_url"] is None:
        show_image_not_found(placeholder_height)
        return

    photo = download_photo(summary["photo_url"])
    if photo is None:
        show_image_not_found(placeholder_height)
    else:
        st.image(photo, width=width)


def show_names(species, note=""):
    """Common name in bold, with the scientific name in italics right below it,
    and an optional small note (like "Verified on AviList") right below that."""
    # Two spaces before "\n" make a Markdown line break, which keeps the
    # lines in one block, close together, instead of separate blocks.
    text = "**" + species["common_name"] + "**  \n*" + species["scientific_name"] + "*"
    if note != "":
        # :small[...] makes the note smaller and :gray[...] fades it, to match
        # the caption style of the "From Wikipedia" line.
        text = text + "  \n:small[:gray[" + note + "]]"
    st.markdown(text)


def show_unverified():
    """Shown instead of a photo for a name that is not on the official checklist."""
    st.caption("Could not verify this species name")


AVILIST_LINK = "[AviList v2025b](https://www.avilist.org/checklist/v2025b/)"
AVILIST_SHORT_LINK = "[AviList](https://www.avilist.org/checklist/v2025b/)"


def show_checked_names(species, short):
    """Check the species against AviList, then show its names with a note
    saying what the check found. short=True uses shorter notes for narrow columns.

    Returns the scientific name to use from here on, or None if the name could
    not be verified (so no photo or fun fact should be shown).
    """
    status, scientific_name = check_species(species)

    if status == "unverified":
        show_names(species)
        show_unverified()
        return None

    # Show the checklist's scientific name (it may have been corrected).
    checked = {"common_name": species["common_name"], "scientific_name": scientific_name}
    if status == "verified" and short:
        show_names(checked, "Verified on " + AVILIST_SHORT_LINK)
    elif status == "verified":
        show_names(checked, "Verified on the " + AVILIST_LINK + " global bird species list")
    elif short:
        show_names(checked, "Name corrected using " + AVILIST_SHORT_LINK)
    else:
        show_names(checked, "Scientific name corrected using the " + AVILIST_LINK + " global bird species list")
    return scientific_name


def show_confident(result):
    """One species: names, a photo, and a fun fact from Wikipedia."""
    species = result["species"][0]

    # A name that is not on the checklist is not shown as a real identification.
    scientific_name = show_checked_names(species, short=False)
    if scientific_name is None:
        return

    summary = get_wikipedia_summary(scientific_name)
    show_photo(summary, width=220, placeholder_height=160)

    if summary is not None and summary["fun_fact"] != "":
        # Wikipedia's own words, shown as written, with a link to the article.
        st.markdown(summary["fun_fact"])
        st.caption("[From Wikipedia](" + summary["article_url"] + ")")
    else:
        st.caption("No Wikipedia summary available.")


def show_possible(result):
    """2-3 species side by side, each with a small photo and how to tell it apart."""
    st.markdown("**These could be the possible options:**")
    # One narrow column per species.
    columns = st.columns(len(result["species"]))
    for column, species in zip(columns, result["species"]):
        with column:
            scientific_name = show_checked_names(species, short=True)
            if scientific_name is None:
                # "continue" skips the rest of this species and moves on to the next one.
                continue
            summary = get_wikipedia_summary(scientific_name)
            # "stretch" makes the photo fill the narrow column's width.
            show_photo(summary, width="stretch", placeholder_height=100)
            if species["distinguishing_trait"] != "":
                # The tip is written by the AI, so label it clearly.
                st.caption("AI suggestion: " + species["distinguishing_trait"])


def show_not_enough():
    """Shown when the description fits too many species. Never guess."""
    st.markdown("**Not enough data to make an identification.**", text_alignment="center")

# Use the full browser width on this page so the two halves have room.
# (The Fieldnotes page keeps the normal, narrower reading width.)
st.set_page_config(layout="wide")

# The site name sits above both columns, centred across the whole page.
st.title("*Fowl Play*", text_alignment="center")

# The Identify button sits directly below the title, also centred.
with st.container(horizontal_alignment="center"):
    # st.button is True only on the run right after the user clicks it.
    identify_clicked = st.button("Identify", key="identify")

# Split the page: the form on the left, the result frame on the right.
left, right = st.columns(2, gap="large")

with left:
    main_text = st.text_area(
        "Enter your plain-language description of the bird you saw here, "
        "and let's find out what it is!",
        height=80,
    )

    # Location is required: it is one of the strongest clues to a bird's identity.
    location = st.text_input(
        "Location (required)",
        placeholder="e.g. Lodhi Garden, Delhi, winter morning",
    )

    # help="..." adds a small "?" icon; the tip (from fieldnotes.md) shows on hover.
    st.subheader(
        "Additional specifics",
        help="You don't need all of these. Even two or three solid field marks are often enough.",
    )

    # key="specifics" lets style.css find these boxes to resize their labels.
    with st.container(key="specifics"):
        # Two columns of three boxes each, under the description box.
        specifics_left, specifics_right = st.columns(2)
        with specifics_left:
            size_and_shape = st.text_input(
                "Size and shape",
                placeholder="e.g. smaller than a pigeon, stout body",
                help="Compare it to a bird you know (sparrow, pigeon, crow), "
                "and note its proportions, like a long neck or stout body.",
            )
            wing_type = st.text_input(
                "Wing type",
                placeholder="e.g. long and pointed, short and rounded",
                help="If it flew: wing shape (broad, pointed or rounded) and "
                "flight style (soaring, flapping, swooping or hovering).",
            )
            colour_patterns = st.text_input(
                "Colour patterns",
                placeholder="e.g. brown back, streaky chest, white eye ring",
                help="Main colours plus markings like eye rings, stripes, crests, "
                "and wing or tail marks. Note the beak and feet colour too.",
            )
        with specifics_right:
            beak_type = st.text_input(
                "Beak type",
                placeholder="e.g. short and conical, hooked",
                help="Shape and length: thin and pointed, short and conical, "
                "hooked, flat and broad, or long and thin.",
            )
            foot_type = st.text_input(
                "Foot type",
                placeholder="e.g. webbed, strong talons",
                help="Webbed, long thin toes, strong curved talons, or perching "
                "feet (three toes forward, one back).",
            )
            behaviours = st.text_input(
                "Behaviours",
                placeholder="e.g. hopping on the ground, tail-bobbing, sharp chip-chip call",
                help="Tail-bobbing, hopping or walking, perching low or high, habitat, "
                'and calls (a rough guess like "chip-chip" is fine).',
            )

# A dictionary pairs each label with what the user typed in that box.
specifics = {
    "Size and shape": size_and_shape,
    "Wing type": wing_type,
    "Colour patterns": colour_patterns,
    "Beak type": beak_type,
    "Foot type": foot_type,
    "Behaviours": behaviours,
}

with right:
    # A centre-aligned container puts the frame in the middle of the right half.
    with st.container(horizontal_alignment="center"):
        # A fixed size keeps the frame visible even before there is
        # a result. If a result is too long, the frame scrolls inside itself.
        result_frame = st.container(border=True, width=560, height=440)

    with result_frame:
        if not identify_clicked:
            st.caption("Your result will appear here.")
        else:
            if not has_description(main_text, specifics):
                st.warning("Please describe the bird to identify it!")
            elif location.strip() == "":
                st.warning("Please add where you saw the bird!")
            else:
                full_description = build_description(main_text, location, specifics)
                api_key = get_api_key()
                try:
                    # The spinner shows while Haiku works, then disappears.
                    with st.spinner("Identifying…"):
                        # With a key, Haiku identifies the bird; without one, demo mode.
                        result = identify_bird(full_description, api_key)
                except IdentificationError as error:
                    # Show the friendly message instead of a crash.
                    st.error(str(error))
                else:
                    # "else" runs only if there was no error above.
                    if api_key is None:
                        st.info("Demo mode: showing a sample result, not a real identification.")

                    # Pick the layout that matches the outcome.
                    if result["outcome"] == "confident":
                        show_confident(result)
                    elif result["outcome"] == "possible":
                        show_possible(result)
                    else:
                        show_not_enough()
