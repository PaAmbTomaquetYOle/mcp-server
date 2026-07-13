from __future__ import annotations

from mcp_server.domain.search.search_document import SearchDocument
from mcp_server.domain.search.synonym_expander import SynonymExpander
from mcp_server.domain.search.token_normalizer import TokenNormalizer

_TITLE_WEIGHT = 3
_TAGS_WEIGHT = 2
_CONTENT_WEIGHT = 1


class RelevanceScorer:
    """Scores how relevant a `SearchDocument` is to a free-text query.

    Tokenizes and stems both the query and the document's fields, expands each query token to its
    synonym group, and awards points per matched query concept -- weighted by which field it was
    found in (title highest, then tags, then content/description). A document with score 0 doesn't
    match the query at all.
    """

    def __init__(self, normalizer: TokenNormalizer, expander: SynonymExpander) -> None:
        self.__normalizer = normalizer
        self.__expander = expander

    def score(self, document: SearchDocument, query: str) -> int:
        query_stems = self.__normalizer.token_set(query)
        if not query_stems:
            return 0

        title_tokens = self.__normalizer.token_set(document.title)
        tags_tokens = self.__normalizer.token_set(" ".join(document.tags))
        content_tokens = self.__normalizer.token_set(document.content)

        total = 0
        for stem in query_stems:
            concept = self.__expander.expand(stem)
            if concept & title_tokens:
                total += _TITLE_WEIGHT
            elif concept & tags_tokens:
                total += _TAGS_WEIGHT
            elif concept & content_tokens:
                total += _CONTENT_WEIGHT

        return total
