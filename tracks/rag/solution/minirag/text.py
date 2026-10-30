"""Turn text into search terms. (Lab 1.)"""
import re

# Words too common to help ranking. Removing them is optional; BM25's IDF already
# gives them little weight. Keeping the list short avoids dropping meaningful words.
STOPWORDS = frozenset("""
a an and are as at be by can do does for from has have how i if in is it its me my
of on or our should so than that the their then there these this to was we were what
when where which who why will with you your
""".split())

TOKEN = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")


def tokenize(text):
    """Lowercase `text` and return its search terms, in order.

    Rules (the tests check each one):
    - Terms are runs of letters and digits; anything else separates terms.
    - A compound joined by '-' or '_' (PLAY-4012, eu-west-2, CATALOG_DEADLINE_MS)
      is kept whole AND split into its parts, so both "play-4012" and "4012" match.
    - Stopwords are removed (also from compound parts).

    >>> tokenize("How do I fix PLAY-4012?")
    ['fix', 'play-4012', 'play', '4012']
    """
    # LAB1-BEGIN
    # Task: Use TOKEN.findall on the lowercased text. For each match, emit the match
    #       itself, then (if it contains '-' or '_') each of its parts. Skip stopwords.
    terms = []
    for match in TOKEN.findall(text.lower()):
        pieces = [match]
        if "-" in match or "_" in match:
            pieces += re.split(r"[-_]", match)
        terms += [p for p in pieces if p not in STOPWORDS]
    return terms
    # LAB1-END
