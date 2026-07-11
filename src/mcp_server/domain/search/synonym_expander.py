from __future__ import annotations

from mcp_server.domain.search.token_normalizer import TokenNormalizer

# Small, curated groups of interchangeable SOP-search concepts. Each group is stemmed once at
# construction time, so any conjugation/plural of a member expands to the whole group.
# Extend by adding a new frozenset here -- keep groups small and domain-relevant to avoid
# over-broad matches.
_SYNONYM_GROUPS: tuple[frozenset[str], ...] = (
    frozenset({"deploy", "release", "ship"}),
    frozenset({"hire", "onboard", "recruit"}),
    frozenset({"offboard", "leave", "depart", "exit"}),
    frozenset({"issue", "ticket", "bug"}),
    frozenset({"guide", "manual", "doc", "documentation"}),
)


class SynonymExpander:
    """Expands a single stemmed token into its curated synonym group, if any."""

    def __init__(self, normalizer: TokenNormalizer, groups: tuple[frozenset[str], ...] = _SYNONYM_GROUPS) -> None:
        self.__stem_groups: dict[str, frozenset[str]] = {}
        for group in groups:
            stemmed_group = frozenset(normalizer.token_set(" ".join(group)))
            for stem in stemmed_group:
                self.__stem_groups[stem] = stemmed_group

    def expand(self, stem: str) -> frozenset[str]:
        """Return `stem` plus any synonym stems in its curated group (just `{stem}` if none)."""
        return self.__stem_groups.get(stem, frozenset({stem}))
