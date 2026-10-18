import streamlit as st


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


st.title("Fowl Play")

main_text = st.text_area(
    "Enter your plain-language description of the bird you saw here, "
    "and let's find out what it is!"
)

st.subheader("Additional specifics")
size_and_shape = st.text_input("Size and shape", placeholder="e.g. smaller than a pigeon, stout body")
wing_type = st.text_input("Wing type", placeholder="e.g. long and pointed, short and rounded")
colour_patterns = st.text_input("Colour patterns", placeholder="e.g. brown back, streaky chest, white eye ring")
beak_type = st.text_input("Beak type", placeholder="e.g. short and conical, hooked")
foot_type = st.text_input("Foot type", placeholder="e.g. webbed, strong talons")
behaviours_and_location = st.text_input(
    "Behaviours and location",
    placeholder="e.g. hopping on the ground, city park in Delhi, winter morning",
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

# st.button is True only on the run right after the user clicks it.
if st.button("Identify"):
    full_description = build_description(main_text, specifics)
    if full_description == "":
        st.warning("Please describe the bird to identify it!")
    else:
        # Placeholder: Step 8 replaces this echo with the identification.
        st.write("**This is what will be sent for identification:**")
        st.text(full_description)
