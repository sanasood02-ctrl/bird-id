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

## Using the skill in Claude Code

The same instructions work as a Claude Code skill. Start Claude Code in this
folder and type `/identify-bird` followed by a description and location.
