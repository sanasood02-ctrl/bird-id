"""Get a bird's photo and a short fact from Wikipedia, by scientific name."""

import requests

# Wikipedia's page-summary API. The page title goes on the end.
SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# Wikipedia requires a User-Agent saying who is asking and how to reach them.
HEADERS = {"User-Agent": "FowlPlay/1.0 (college project; https://github.com/sanasood02-ctrl/bird-id)"}


def first_sentences(text, how_many):
    """Return the first few sentences of text, unchanged.

    Simple rule: a sentence ends at ". ". This can occasionally cut early at
    abbreviations (like "c." or "e.g."), which is fine for a short fact.
    """
    sentences = text.split(". ")
    result = ". ".join(sentences[:how_many])
    if result != "" and not result.endswith("."):
        result = result + "."
    return result


def get_wikipedia_summary(scientific_name):
    """Look up a species on Wikipedia and return a dictionary with:
      "photo_url":   web address of the photo, or None if there is no photo
      "fun_fact":    first two sentences of the summary ("" if none)
      "article_url": web address of the Wikipedia article

    Returns None if the lookup fails (no internet, no article, Wikipedia slow).
    Wikipedia redirects scientific names to the bird's article automatically.
    """
    # Page titles use underscores instead of spaces.
    url = SUMMARY_API + scientific_name.strip().replace(" ", "_")

    try:
        # timeout=10: give up after 10 seconds instead of waiting forever.
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException:
        # No internet, or Wikipedia did not answer in time.
        return None

    # Status code 200 means "OK". Anything else (like 404, "not found")
    # means there is no usable article.
    if response.status_code != 200:
        return None

    data = response.json()

    # Not every article has a photo, so check before using it.
    photo_url = None
    if "thumbnail" in data:
        photo_url = data["thumbnail"]["source"]

    return {
        "photo_url": photo_url,
        "fun_fact": first_sentences(data.get("extract", ""), 2),
        "article_url": data["content_urls"]["desktop"]["page"],
    }
