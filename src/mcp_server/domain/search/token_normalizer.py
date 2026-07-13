from __future__ import annotations

import re

import snowballstemmer

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class TokenNormalizer:
    """Normalizes free text into a set of stemmed tokens for word-form-insensitive matching.

    Reduces plural/singular and conjugation variants (e.g. "deploys"/"deploying" -> "deploy") to
    a common stem via the Porter2 (Snowball) English algorithm, so search matching doesn't depend
    on the exact word form used in the query or in the indexed text.
    """

    def __init__(self) -> None:
        self.__stemmer = snowballstemmer.stemmer("english")

    def token_set(self, text: str) -> set[str]:
        """Return the distinct stemmed tokens found in `text`."""
        words = _TOKEN_PATTERN.findall(text.lower())
        return set(self.__stemmer.stemWords(words))
