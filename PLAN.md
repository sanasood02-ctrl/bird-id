# Build plan — main app

Each step is small and can be tested before moving on. Tick the box when the
step works **and** has been committed to Git.

How to run the app (from Step 3 onward): open Terminal in the project folder,
activate the virtual environment with `source .venv/bin/activate`, then run
`streamlit run app.py`. The app opens in your browser.

---

## Phase 1 — Set up the project

- [x] **1. Git and .gitignore.** Run `git init`, create `.gitignore` containing
  at least `.venv/`, `__pycache__/`, `.DS_Store`, and `.streamlit/secrets.toml`.
  Make the first commit.
  *Test:* `git status` shows a clean working tree; `git log` shows one commit.

- [x] **2. Virtual environment and libraries.** Create `.venv`, install
  `streamlit`, `anthropic`, and `requests`, and save them in `requirements.txt`.
  *Test:* `streamlit hello` opens Streamlit's demo page in the browser.

- [x] **3. Hello page.** A minimal `app.py` that shows the app title.
  *Test:* `streamlit run app.py` shows the title in the browser.

- [x] **4. Connect to GitHub.** Create a GitHub repository (private is
  recommended until the project is graded) and push.
  *Test:* the files appear on GitHub, and `secrets.toml` is **not** among them.

## Phase 2 — Pages and layout (no AI yet)

- [x] **5. Two pages.** Add navigation between an "Identify a bird" page and a
  "Fieldnotes tutorial" page (placeholder text for now).
  *Test:* you can click between both pages in the sidebar.

- [x] **6. Fieldnotes tutorial content.** Add your class notes as
  `fieldnotes.md` in the project folder. The page reads the file and displays
  it exactly as written (Markdown formatting like headings and lists is shown
  as formatted text; no AI involved).
  *Test:* the page matches your notes word for word, with headings and lists
  showing correctly.

- [x] **7. Description form.** On the Identify page: a main text box
  ("Enter your plain-language description of the bird you saw here, and let's
  find out what it is!"), a required "Location" box under it, then an
  "Additional specifics" heading with six optional one-line boxes (size and
  shape, wing type, colour patterns, beak type, foot type, behaviours), and an
  "Identify" button. The app joins every filled-in box into one labeled text.
  Show a friendly message if nothing describes the bird, or if the location is
  empty. (Location was made required after testing showed wrong results
  without it.)
  *Test:* no description shows "Please describe the bird to identify it!";
  a description with no location shows "Please add where you saw the bird!";
  a description (main box or any specifics box) plus a location gives a
  result.

## Phase 3 — Demo mode and results display

- [x] **8. Demo identification function.** Write
  `identify_bird(description)` (in its own file, separate from the UI; it
  receives the combined labeled text from the form) that returns a fake **confident** result: outcome, common name,
  scientific name. (No fun fact here; that comes from Wikipedia in Phase 4.)
  Show a
  "Demo mode" notice on the page.
  *Test:* typing anything and clicking Identify shows the fake species and the
  demo notice.

- [x] **9. All three outcomes in demo mode.** Make the demo function able to
  return each outcome (for example, chosen by a keyword in the description,
  like "vague" or "lookalike"), and build the display for each:
  confident / possible matches (up to 3, with the "how to tell them apart"
  tip) / not enough data.
  *Test:* you can trigger and see all three layouts in the browser.

## Phase 4 — Wikipedia photos and fun facts

- [x] **10. Wikipedia lookup.** Write a function that takes a scientific name
  and gets the Wikipedia page summary, which contains both a photo and the
  article's opening text. Show the photo, and the first sentence or two of the
  text as the fun fact, labeled "From Wikipedia" with a link to the article.
  If there's no summary, show "No Wikipedia summary available".
  *Test:* the demo species shows a real photo and text that matches the start
  of its Wikipedia article; try 3–4 scientific names you know.

- [x] **11. Missing-photo fallback.** If no photo is found or it fails to load,
  show "Image not found" in its place. The rest of the result still shows.
  *Test:* put a made-up scientific name in the demo data; "Image not found"
  appears and nothing crashes.

- [x] **12. Name check.** Download an official bird checklist (a free CSV file
  of all bird species with common and scientific names; we'll choose which
  one together at this step) and write a function that checks whether a
  scientific name is on it. Species not on the list are not shown as real
  identifications; the app says "Could not verify this species name" instead.
  *Test:* the demo species passes; a made-up name in the demo data is caught.

## Phase 5 — Real AI (needs the API key)

- [x] **13. Secrets file and mode switch.** Create `.streamlit/secrets.toml`
  with your key. The app uses real mode when a key is present, demo mode when
  not. Set a monthly spending limit in the Anthropic Console.
  *Test:* `git status` does **not** list `secrets.toml`; the demo notice
  disappears when the key is present and comes back if you rename the file.

- [x] **14. Real identification.** Replace the fake result with a call to Claude
  Haiku 4.5 that returns structured data in the same shape as the demo
  result. Its instructions include the "enough information" rule from
  `CLAUDE.md` and tell it to prefer the cautious outcome when unsure.
  *Test:* try a clear description of a common bird (confident), a look-alike
  pair (possible matches), and "it was a brown bird" (not enough data). Then
  try the same description with different locations and compare.

- [x] **15. Error handling.** Friendly messages for: no internet, API errors
  (e.g. bad key, no credit), and unexpected responses.
  *Test:* temporarily break the key in `secrets.toml` and turn Wi-Fi off; the
  app shows a message instead of crashing. Restore the key afterwards.

## Phase 6 — Evaluation

- [x] **16. Test cases CSV.** Write `eval/test_cases.csv` with columns
  `description` and `location` (required), one optional column per
  "Additional specifics" box (`size_shape`, `wing_type`, `colour_patterns`,
  `beak_type`, `foot_type`, `behaviours`; all joined into one text the same
  way the form does it), `expected_outcome` (confident / possible /
  not_enough), `expected_species` (scientific name; for look-alikes, the
  species it really was), and `source` (where the row's information comes
  from). The owner writes this file from their own records. You decide the expected
  outcome for each row, using your birding knowledge. Include:
  - clear descriptions of distinctive birds,
  - look-alike pairs,
  - deliberately vague ones,
  - "detail ladders": the same bird described with 1 trait, then 2, then 3+,
    to find where the app switches from "not enough data" to an answer.
  *Test:* the file opens correctly in a spreadsheet app.

- [x] **17. Evaluation script and scoring.** `eval/run_eval.py` runs every row
  through `identify_bird()` and saves a results table with one verdict per row:

  | Expected | App said | Verdict |
  |---|---|---|
  | confident | confident, right species | Correct |
  | confident | possible, right species in list | Too cautious |
  | possible | possible, right species in list | Correct |
  | possible | confident, right species | Lucky (overconfident) |
  | not enough | not enough | Correctly declined |
  | any | not enough (but an answer was expected) | Too cautious |
  | any | right species missing / wrong species | **Wrong** |
  | not enough | confident or possible | **Guessed** |

  Species are matched by scientific name. The script also prints summary
  scores: % correct overall, number of **Wrong** + **Guessed** (the worst
  errors — confidently misleading the user), number of names that failed the
  name check, accuracy per expected outcome (with a ± margin of error), and a
  small expected-vs-actual outcome table. It uses free demo answers unless
  run with `--real` (one paid API call per row; ask the owner first). Each
  run saves `eval/results_<demo|real>_<date-time>.csv`, so runs can be compared.
  *Test:* run it on 3 rows first, check the verdicts by hand, then run all.

- [ ] **18. Improve accuracy.** Run the evaluation once before any change and
  save those scores as the starting point. Then make one change at a time,
  re-run the evaluation after each one, and write down what changed and how
  the scores moved, for your report. Pay most attention to **Wrong** and
  **Guessed**.

  - [x] **18a. Better clues from users.** Add short tips under the
    "Additional specifics" boxes, taken from your field notes (e.g. compare
    the size to a bird you know). You approve the wording.
    *Test:* the tips show under the right boxes on the Identify page.

  - [x] **RAG sample.** Save your seven species records in
    `data/field_records.txt`. `rag.py` finds the records that share the most
    words with the description and hands the best two to Haiku. The page shows
    which records were used.
    *Test:* describe a Red-vented Bulbul; the "Checked using RAG against field
    records" line appears. Re-run the evaluation and compare with the starting
    point.

  - [x] **Skill file.** Move Haiku's instructions, word for word, into
    `.claude/skills/identify-bird/SKILL.md`. The app reads them from there.
    *Test:* the instructions the app loads match the old text exactly; a demo
    identification still works.

  - [x] **18b. Context engineering.** Give Haiku better material in its
    instructions: 2–3 worked examples with the correct reasoning (including a
    cautious one, like Downy vs Hairy Woodpecker) and your `fieldnotes.md` as a
    reference (passed along exactly as written).
    *Test:* re-run the evaluation and compare the scores with the starting point.

  - [x] **18c. Sharpen the instructions.** Look at the remaining mistakes and
    the detail ladders, look for patterns, and adjust the prompt or the
    "enough information" rule to fix them.
    *Test:* re-run the evaluation and compare the scores with the previous run.

## Phase 7 — Finish

- [ ] **19. Tidy up.** Write a short `README.md` (what the app does, how to run
  it, how to add your own key). Remove leftover test code.
  *Test:* follow your own README from a fresh Terminal window and the app runs.

- [ ] **20. Final commit and push.**
  *Test:* GitHub has the latest code and still no secrets file.

- [ ] **21. Deploy online.** Put the app on Streamlit Community Cloud, straight
  from the GitHub repo. The API key goes into the app's Secrets settings on
  the Streamlit Cloud website (never into the repo). Use the app's Sharing
  settings to limit who can open it, so strangers can't spend your credit.
  *Test:* open the app's web address in a browser where you're not logged in
  and check it's blocked; then open it while logged in and identify a bird.
