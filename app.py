import streamlit as st

# List the app's pages; Streamlit turns this into the sidebar menu.
identify_page = st.Page("app_pages/identify.py", title="Identify a bird", icon="🐦", default=True)
fieldnotes_page = st.Page("app_pages/fieldnotes.py", title="Fieldnotes tutorial", icon="📓")

# Show the menu, then run whichever page the user picked.
page = st.navigation([identify_page, fieldnotes_page])
page.run()
