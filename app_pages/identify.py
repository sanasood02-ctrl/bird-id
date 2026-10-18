import streamlit as st

from bird_identifier import build_description, identify_bird


def show_photo_placeholder(height):
    """An empty bordered box where the bird's photo will go (until Step 10)."""
    with st.container(border=True, height=height):
        st.caption("Photo will appear here.")


def show_confident(result):
    """One species: names and a large photo."""
    species = result["species"][0]
    st.markdown("**" + species["common_name"] + "**")
    st.markdown("*" + species["scientific_name"] + "*")
    show_photo_placeholder(200)


def show_possible(result):
    """2-3 species side by side, each with a small photo and how to tell it apart."""
    st.markdown("**These could be the possible options:**")
    # One narrow column per species.
    columns = st.columns(len(result["species"]))
    for column, species in zip(columns, result["species"]):
        with column:
            st.markdown("**" + species["common_name"] + "**")
            st.markdown("*" + species["scientific_name"] + "*")
            show_photo_placeholder(100)
            if species["distinguishing_trait"] != "":
                # The tip is written by the AI, so label it clearly.
                st.caption("AI suggestion: " + species["distinguishing_trait"])


def show_not_enough():
    """Shown when the description fits too many species. Never guess."""
    st.markdown("**Not enough data to make an identification.**", text_alignment="center")

# Use the full browser width on this page so the two halves have room.
# (The Fieldnotes page keeps the normal, narrower reading width.)
st.set_page_config(layout="wide")

# Split the page: the form on the left, the result frame on the right.
left, right = st.columns(2, gap="large")

with left:
    st.title("*Fowl Play*")

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
    # A centre-aligned container puts the button and the frame in the middle
    # of the right half.
    with st.container(horizontal_alignment="center"):
        # st.button is True only on the run right after the user clicks it.
        identify_clicked = st.button("Identify", key="identify")

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
