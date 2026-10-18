import streamlit as st

from bird_identifier import build_description, identify_bird

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

        # A fixed square size keeps the frame visible even before there is
        # a result. If a result is too long, the frame scrolls inside itself.
        result_frame = st.container(border=True, width=420, height=420)

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

                species = result["species"][0]
                st.markdown("**" + species["common_name"] + "**")
                st.markdown("*" + species["scientific_name"] + "*")

                # Placeholder until Step 10 adds the real Wikipedia photo.
                with st.container(border=True, height=200):
                    st.caption("Photo will appear here.")
