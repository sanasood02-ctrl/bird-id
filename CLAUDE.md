# Bird ID — project guide for Claude

## What this app is

A Streamlit web app (college course term project) that identifies birds from a
plain-language description.

- The user types what they noticed about a bird in one large box ("Enter your
  plain-language description of the bird you saw here, and let's find out what
  it is!"). Below it, under "Additional specifics", are six optional one-line
  boxes from standard birdwatching field-notes practice: size and shape, wing
  type, colour patterns, beak type, foot type, behaviours and location.
- At least one box must be filled in. The app joins every filled-in box into
  one labeled text (e.g. "Description: ...", "Beak type: ...") and passes that
  single text to the identification function. Location and season (in the
  "Behaviours and location" box) narrow down the likely species.
- The app asks Claude Haiku 4.5 to identify the species and returns one of
  three outcomes:
  - **Confident** — one species: common name, scientific name, Wikipedia photo, fun fact.
  - **Possible matches** — up to 3 species, each with name and photo, under a
    heading like "These could be the possible options", plus (if possible) the
    trait that would tell them apart.
  - **Not enough data** — show "Not enough data to make an identification".
    Never guess.
- Haiku returns only: the outcome type, and for each species its common name,
  scientific name, and (for possible matches) the distinguishing trait. Haiku
  does **not** write fun facts.
- Photos and fun facts both come from Wikipedia's API (one page-summary
  request), looked up by **scientific name**. The fun fact is the opening of
  the Wikipedia summary, shown as written and labeled "From Wikipedia" with a
  link to the article. If there is no summary, show a short "No Wikipedia
  summary available" message instead. Never use AI-generated images. If no
  photo can be found or loaded, show "Image not found" in its place.
- **Name check (guards against made-up names):** every species Haiku returns
  is checked against a downloaded official bird checklist file. A species
  whose scientific name is not on the checklist is not shown as a real
  identification; the app says it could not verify that name.
- **"Enough information" rule (given to Haiku in its instructions):**
  Confident = the description rules out all similar species (taking location
  into account); Possible matches = 2–3 species remain; Not enough data = more
  than 3 remain. When unsure between two outcomes, pick the more cautious one.
  The distinguishing-trait tip is AI-written, so label it "AI suggestion".
- A **Fieldnotes tutorial** page shows the owner's own birdwatching class notes
  (the Markdown file `fieldnotes.md`) **exactly as written**. Do not rewrite, summarize, or
  "improve" this content with AI.
- An **evaluation script** runs test descriptions from a CSV through the
  identification function and produces a results table (expected vs. actual)
  with a verdict per row and summary scores (see Step 17 in `PLAN.md`).
- **Later, only if time allows:** a RAG layer over ~30 species from the owner's
  own records. Do not start this unless asked.

The build plan and progress checklist live in `PLAN.md`. Tick off steps there as
they are finished and tested.

## Tech stack

- Python 3.11, in a virtual environment (`.venv/`)
- Streamlit for the UI (multi-page app)
- `anthropic` Python SDK, model `claude-haiku-4-5`, using structured outputs
  so the response always matches a fixed shape
- `requests` for the Wikipedia API (send a descriptive `User-Agent` header —
  Wikipedia requires one)
- Git + GitHub for version control
- Dependencies listed in `requirements.txt`

## Rules for working with the owner

1. **The owner is a beginner.** Explain what you are doing in plain language.
   The first time a new concept comes up (e.g. virtual environment, function,
   API, JSON, session state), explain it briefly before using it.
2. **Simple and readable over clever.** The owner must understand and explain
   every line for the course. Prefer clear names, short functions, comments
   that explain *why*, and no advanced tricks or unnecessary libraries.
3. **One small feature at a time.** After each step, tell the owner exactly how
   to test it (what command to run, what to click, what they should see) and
   wait for them to confirm before moving on.
4. **Plan before bigger changes.** Before anything bigger than a small edit
   (new file, new library, restructuring, changing how something works),
   describe the plan and wait for the owner's OK.
5. **The API key must NEVER appear in code or in any Git-tracked file.**
   - It lives only in `.streamlit/secrets.toml`, read with `st.secrets`.
   - `.streamlit/secrets.toml` must be listed in `.gitignore`.
   - Never print, log, or display the key. Never paste it into chat output.
   - Before any commit, check `git status` to confirm `secrets.toml` is not staged.
6. **Demo mode until there is a key.** If no API key is found in
   `st.secrets`, the app runs in demo mode: the identification function
   returns a fake sample result (in the same shape as a real one) and the UI
   shows a visible "Demo mode" notice. Everything else in the app must work
   in demo mode, so it can be built and tested without spending money.

## Conventions

- Keep the identification logic in its own plain Python function (separate
  from the Streamlit UI code) so the evaluation script can call it directly.
- Real and demo results must use the exact same data shape.
- Handle failures gracefully (no internet, API error, Wikipedia miss) with a
  friendly message instead of a crash.
- Commit to Git after each working step, with a short clear message.
