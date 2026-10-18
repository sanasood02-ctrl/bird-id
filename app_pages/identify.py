import streamlit as st

from bird_identifier import build_description, identify_bird
from name_check import is_known_species
from wikipedia_lookup import download_photo, get_wikipedia_summary


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


def show_confident(result):
    """One species: names, a photo, and a fun fact from Wikipedia."""
    species = result["species"][0]

    # A name that is not on the checklist is not shown as a real identification.
    if not is_known_species(species["scientific_name"]):
        show_names(species)
        show_unverified()
        return

    # Tell the user the name was checked, and against which list.
    show_names(species, "Verified on the [AviList v2025b](https://www.avilist.org/checklist/v2025b/) global bird species list")

    summary = get_wikipedia_summary(species["scientific_name"])
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
            if not is_known_species(species["scientific_name"]):
                show_names(species)
                show_unverified()
                # "continue" skips the rest of this species and moves on to the next one.
                continue
            # A short version of the "verified" note, to fit the narrow column.
            show_names(species, "Verified on [AviList](https://www.avilist.org/checklist/v2025b/)")
            summary = get_wikipedia_summary(species["scientific_name"])
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
        height=120,
    )

    st.subheader("Additional specifics")

    # key="specifics" lets style.css find these boxes to resize their labels.
    with st.container(key="specifics"):
        # Two columns of three boxes each, under the description box.
        specifics_left, specifics_right = st.columns(2)
        with specifics_left:
            size_and_shape = st.text_input("Size and shape", placeholder="e.g. smaller than a pigeon, stout body")
            wing_type = st.text_input("Wing type", placeholder="e.g. long and pointed, short and rounded")
            colour_patterns = st.text_input("Colour patterns", placeholder="e.g. brown back, streaky chest, white eye ring")
        with specifics_right:
            beak_type = st.text_input("Beak type", placeholder="e.g. short and conical, hooked")
            foot_type = st.text_input("Foot type", placeholder="e.g. webbed, strong talons")
            behaviours_and_location = st.text_input(
                "Behaviours and location",
                placeholder="e.g. hopping on the ground, Delhi park, winter morning",
            )

# A dictionary pairs each label with what the user typed in that box.
specifics = {
    "Size and shape": size_and_shape,
    "Wing type": wing_type,
    "Colour patterns": colour_patterns,
    "Beak type": beak_type,
    "Foot type": foot_type,
    "Behaviours and location": behaviours_and_location,
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
            full_description = build_description(main_text, specifics)
            if full_description == "":
                st.warning("Please describe the bird to identify it!")
            else:
                result = identify_bird(full_description)

                # There is no API key yet, so every result is a demo result.
                # (Step 13 will show this only when no key is found.)
                st.info("Demo mode: showing a sample result, not a real identification.")

                # Pick the layout that matches the outcome.
                if result["outcome"] == "confident":
                    show_confident(result)
                elif result["outcome"] == "possible":
                    show_possible(result)
                else:
                    show_not_enough()
