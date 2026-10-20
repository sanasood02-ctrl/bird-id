from pathlib import Path

import streamlit as st

# fieldnotes.md sits in the main project folder, one level up from this file.
# Building the path from this file's location means it is found no matter
# which folder Streamlit was started from.
FIELDNOTES_FILE = Path(__file__).parent.parent / "fieldnotes.md"

st.title("Field Notes Tutorial")

if FIELDNOTES_FILE.exists():
    # Show the owner's notes exactly as written (no AI, no changes).
    notes = FIELDNOTES_FILE.read_text(encoding="utf-8")
    st.markdown(notes)
else:
    st.info("Fieldnotes file not found. Add fieldnotes.md to the project folder to show your notes here.")
