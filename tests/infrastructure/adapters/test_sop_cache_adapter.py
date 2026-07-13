import pytest

from mcp_server.domain.search import RelevanceScorer, SearchDocument, SynonymExpander, TokenNormalizer
from mcp_server.infrastructure.adapters.sop_cache import InMemorySopCacheAdapter

_DOC_A = SearchDocument(
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
_DOC_B = SearchDocument(
    external_id="2",
    title="Onboard new hire",
    description="Onboard new hire",
    content="Onboarding checklist for new employees.",
    link="https://x/sops/2",
    author="U2",
    tags=["hr"],
    origin_channel="C2",
    date_updated="2026-01-02",
)


@pytest.fixture
def cache():
    normalizer = TokenNormalizer()
    scorer = RelevanceScorer(normalizer=normalizer, expander=SynonymExpander(normalizer))
    return InMemorySopCacheAdapter(ttl_seconds=60, scorer=scorer)


class TestSearch:
    @pytest.mark.anyio
    async def test_empty_cache_returns_no_results(self, cache):
        results = await cache.search("deploy", filters={})

        assert results == []

    @pytest.mark.anyio
    async def test_matches_query_in_title_content_and_tags(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        results = await cache.search("deploy", filters={})

        assert results == [_DOC_A]

    @pytest.mark.anyio
    async def test_search_is_case_insensitive(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        results = await cache.search("DEPLOY", filters={})

        assert results == [_DOC_A]

    @pytest.mark.anyio
    async def test_matches_by_tag(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        results = await cache.search("hr", filters={})

        assert results == [_DOC_B]

    @pytest.mark.anyio
    async def test_caps_results_at_50(self, cache):
        docs = [_DOC_A.model_copy(update={"external_id": str(i)}) for i in range(60)]
        await cache.refresh(docs)

        results = await cache.search("deploy", filters={})

        assert len(results) == 50

    @pytest.mark.anyio
    async def test_matches_plural_query_against_singular_field(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        results = await cache.search("deploys", filters={})

        assert results == [_DOC_A]

    @pytest.mark.anyio
    async def test_matches_synonym_query(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        results = await cache.search("release", filters={})

        assert results == [_DOC_A]

    @pytest.mark.anyio
    async def test_orders_by_relevance_title_match_before_content_only_match(self, cache):
        title_hit = _DOC_A.model_copy(update={"external_id": "title-hit"})
        content_only_hit = _DOC_B.model_copy(
            update={
                "external_id": "content-hit",
                "title": "Onboard new hire",
                "content": "Onboarding checklist. Also involves a deploy step.",
                "tags": [],
            }
        )
        await cache.refresh([content_only_hit, title_hit])

        results = await cache.search("deploy", filters={})

        assert [doc.external_id for doc in results] == ["title-hit", "content-hit"]


class TestRefresh:
    @pytest.mark.anyio
    async def test_refresh_replaces_document_set(self, cache):
        await cache.refresh([_DOC_A])
        await cache.refresh([_DOC_B])

        results = await cache.search("deploy", filters={})
        assert results == []

        results = await cache.search("onboard", filters={})
        assert results == [_DOC_B]


class TestStats:
    @pytest.mark.anyio
    async def test_stats_before_refresh(self, cache):
        stats = await cache.get_stats()

        assert stats["total_docs"] == 0
        assert stats["last_refresh"] is None

    @pytest.mark.anyio
    async def test_stats_after_refresh(self, cache):
        await cache.refresh([_DOC_A, _DOC_B])

        stats = await cache.get_stats()

        assert stats["total_docs"] == 2
        assert stats["last_refresh"] is not None

    @pytest.mark.anyio
    async def test_hit_and_miss_counts_tracked(self, cache):
        await cache.refresh([_DOC_A])

        await cache.search("deploy", filters={})
        await cache.search("nonexistent", filters={})

        stats = await cache.get_stats()
        assert stats["hit_count"] == 1
        assert stats["miss_count"] == 1


class TestIsStale:
    @pytest.mark.anyio
    async def test_never_refreshed_is_stale(self, cache):
        assert await cache.is_stale() is True

    @pytest.mark.anyio
    async def test_freshly_refreshed_is_not_stale(self, cache):
        await cache.refresh([_DOC_A])

        assert await cache.is_stale() is False
