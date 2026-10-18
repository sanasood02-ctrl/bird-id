from pathlib import Path

import streamlit as st

# Load extra styling (page link size, Identify button size) from style.css.
st.html(Path(__file__).parent / "style.css")

# List the app's pages; Streamlit turns this into the page links.
identify_page = st.Page("app_pages/identify.py", title="Identify a bird", icon="🐦", default=True)
fieldnotes_page = st.Page("app_pages/fieldnotes.py", title="Fieldnotes tutorial", icon="📓")

# Show the page links in a bar across the top, then run the page the user picked.
page = st.navigation([identify_page, fieldnotes_page], position="top")
page.run()
