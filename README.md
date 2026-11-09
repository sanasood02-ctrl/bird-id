# Fowl Play

A Streamlit web app that identifies birds from a plain-language description.
Type what you noticed about a bird and where you saw it, and the app gives one
of three answers:

- **Confident:** one species, with its Wikipedia photo and summary.
- **Possible matches:** up to 3 species, with an AI suggestion for telling them apart.
- **Not enough data:** the app does not guess.

## How it works

- Claude Haiku 5.5 chooses the answer, following the instructions in
  `.claude/skills/identify-bird/SKILL.md`.
- Every species name is checked against the AviList global bird checklist, so
  made-up names are not shown as real identifications.
- Photos and summaries come from Wikipedia.
- A small RAG sample (`rag.py`) hands Haiku the most relevant of seven field
  records written by the owner (`data/field_records.txt`).
- A Field Notes Tutorial page shows the owner's birdwatching notes as written.

## Why it is designed this way

Many birds look alike, and a short description often can't separate them. The
worst thing this app can do is name the wrong bird with confidence, so its main
goal is not to mislead anyone. Most of the choices below follow from that goal.

### Asking the user

- **A free-text box plus six optional boxes.** Beginners can describe a bird in
  their own words. The six boxes (size and shape, wing type, colour patterns,
  beak type, foot type, behaviours) come from standard birdwatching field notes,
  and they prompt for details that tell species apart. Hover tips taken from the
  owner's field notes explain what to look for.
- **Location is required.** Where and when a bird was seen narrows down the
  likely species. Location started as optional, and was made required after
  testing showed wrong results without it.

### Getting an answer from the AI

- **Three outcomes instead of one answer.** If the app always had to name a
  bird, it would have to guess on vague descriptions. "Possible matches" and
  "Not enough data" give it honest ways to answer.
- **A rule based on counting species.** The outcome depends on how many species
  remain after the description is applied: one, two or three, or more than
  three. When Haiku is unsure between Confident and Possible, it must pick
  Possible. "Most likely" is not treated as "ruled out".
- **Reasoning comes first.** Haiku writes which look-alikes the description rules
  out before it picks an outcome, so the decision follows from the check. The
  reasoning is not shown on the page, but the evaluation saves it to help explain
  mistakes.
- **Only details the user wrote can rule out a species.** This stops the AI from
  filling gaps with details nobody observed.
- **A fixed reply format (structured output).** The page and the evaluation both
  need the same fields every time. The format can't limit the list to 3 species
  or require species to be listed, so the code checks those two things itself.
- **One instruction file.** Haiku's rules are in `SKILL.md`, which the app reads
  and Claude Code can also run as a skill, so there is only one copy to maintain.

### Not trusting the AI with facts

- **Every name is checked.** An AI can invent a name that sounds real, so each
  species is checked against AviList (11,131 species). If a scientific name isn't
  listed but the common name is, the checklist's scientific name is used.
  Otherwise the app says it could not verify the name. In the final evaluation,
  this check caught a name that isn't on AviList, *Milvus lineatus*.
- **Photos and summaries come from Wikipedia.** Haiku does not write fun facts,
  and no image is AI-generated, so what the user reads and sees comes from a
  source they can follow through the link. If a photo is missing, the page says
  "Image not found" and does not substitute anything.
- **AI-written text is labelled.** The tip for telling species apart is written
  by Haiku, so it is labelled "AI suggestion".
- **The owner's notes are never rewritten.** The Field Notes page and the field
  records are used exactly as written.

### The RAG sample

RAG means finding relevant stored text and giving it to the AI with the question.
Here it is a small sample of how that works, over seven species from the owner's
own records. Records are matched by shared words: a record needs at least 4 in
common with the description, and the best 2 are used. Two embedding models were
also tested. They did no better, because bird descriptions all use similar words,
and word matching is simpler to explain. A matched record may be about a
different bird, so Haiku is told to use it only as facts about that record's
species.

### Building and testing it

- **The identification code is separate from the page.** The evaluation script
  calls the same function as the app, so it tests what users actually get.
- **Demo mode.** Without an API key, the app returns sample answers in the same
  format as real ones, so everything else can be built and tested for free.
- **The key stays out of the code.** It is kept in a secrets file that Git
  ignores, and access to the online app is restricted so strangers can't spend
  the credit.
- **Simple code.** The project is plain Python with few libraries, because the
  owner has to understand and explain every line.
- **The evaluation counts the worst errors separately.** Overall accuracy treats
  a cautious answer and a wrong bird as equal misses. "Wrong" and "Guessed" are
  counted on their own because those are the answers that mislead the user.

### Trade-offs

- **Safety cost some helpfulness.** Across the six evaluation runs, wrong answers
  fell from 7 to 1, but overly cautious answers rose from 6 to 18. Most of that
  rise came with the move from Haiku 4.5 to 5.5. It fits the main goal, but the
  app now holds back on some birds it could have named.
- **"Possible matches" is the weakest outcome.** Only 11 of the 25 possible rows
  were right in the final run, and 13 were answered "Not enough data".
- **RAG was not shown to improve identification.** In the final run, 50 test rows
  received a record, and only 3 of those included the right bird's record. Only 2
  of the 7 record species appear in the test list.
- **The test list has limits.** 22 of the 100 rows are marked as Claude drafts
  that were not checked against a field guide. The expected answers are also
  judgment calls.

## How to run it

You need Python 3.11. In Terminal:

```
git clone https://github.com/sanasood02-ctrl/bird-id.git
cd bird-id
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Without an API key it runs in **demo mode**,
which shows sample answers and costs nothing.

## How to add your own API key

Create a file called `.streamlit/secrets.toml` containing this line, with your
own key from the Anthropic Console:

```
ANTHROPIC_API_KEY = "your-key-here"
```

Then restart the app. This file is listed in `.gitignore`. Never commit it.

## How to run the evaluation

With the virtual environment active:

```
python eval/run_eval.py          # free: fake demo answers
python eval/run_eval.py --real   # real answers: one paid API call per test row
```

The 100 test descriptions are in `eval/test_cases.csv`. Each run saves a results
table in `eval/`, and `eval/score_history.md` records how the scores changed
with each change to the app.

## Results

On the final run, the app was right on 79 of the 100 test descriptions, with a
margin of error of about ±8 points. It started at 83 of 100, so overall accuracy
did not measurably change. The number of answers that named the wrong bird fell from 7 to 1, but
overly cautious answers rose from 6 to 18. It correctly declined all 25
descriptions that had too little detail.

The instructions were tuned on these same 100 rows, so the score may be
optimistic for new descriptions. The full results and limits are in
`report/report_materials.md`.

## Using the skill in Claude Code

The same instructions work as a Claude Code skill. They are in
`.claude/skills/identify-bird/SKILL.md`. Start Claude Code in this folder and
type `/identify-bird` followed by a description and location. The skill has the
identification rules only: the field notes, field records, name check and
Wikipedia lookup are added by the app.
