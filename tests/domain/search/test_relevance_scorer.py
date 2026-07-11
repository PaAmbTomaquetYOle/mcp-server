import pytest

from mcp_server.domain.search import RelevanceScorer, SearchDocument, SynonymExpander, TokenNormalizer

_DOC = SearchDocument(
    external_id="1",
    title="Restart deploy pipeline",
    description="Restart deploy pipeline",
    content="Restart deploy pipeline. Step 1: check logs.",
    link="https://x/sops/1",
    author="U1",
    tags=["deploy", "ops"],
    origin_channel="C1",
    date_updated="2026-01-01",
)


@pytest.fixture
def scorer():
    normalizer = TokenNormalizer()
    return RelevanceScorer(normalizer=normalizer, expander=SynonymExpander(normalizer))


class TestScore:
    def test_no_match_scores_zero(self, scorer):
        assert scorer.score(_DOC, "onboarding checklist") == 0

    def test_title_match_outweighs_content_only_match(self, scorer):
        title_hit = scorer.score(_DOC, "restart")
        content_only_doc = _DOC.model_copy(update={"title": "SOP", "tags": []})
        content_hit = scorer.score(content_only_doc, "restart")

        assert title_hit > content_hit > 0

    def test_tag_match_outweighs_content_only_match(self, scorer):
        tag_hit = scorer.score(_DOC.model_copy(update={"title": "SOP"}), "deploy")
        content_only_doc = _DOC.model_copy(update={"title": "SOP", "tags": []})
        content_hit = scorer.score(content_only_doc, "restart")

        assert tag_hit > content_hit > 0

    def test_plural_query_matches_singular_field(self, scorer):
        assert scorer.score(_DOC, "deploys") > 0

    def test_synonym_query_matches(self, scorer):
        assert scorer.score(_DOC, "release") > 0

    def test_each_concept_counted_once(self, scorer):
        assert scorer.score(_DOC, "deploy") == scorer.score(_DOC, "deploy deploy")
