import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_server.main import Application


@pytest.fixture
def application():
    app = Application.__new__(Application)
    return app


class TestApplicationWarmUpSopCache:
    @pytest.mark.anyio
    async def test_refreshes_cache_once(self, application):
        service = AsyncMock()
        factory = MagicMock()
        factory.get_search_connector_service.return_value = service

        await application._warm_up_sop_cache(factory)

        service.refresh_cache.assert_awaited_once()

    @pytest.mark.anyio
    async def test_swallows_and_logs_failure(self, application, caplog):
        service = AsyncMock()
        service.refresh_cache.side_effect = RuntimeError("backend unreachable")
        factory = MagicMock()
        factory.get_search_connector_service.return_value = service

        with caplog.at_level(logging.ERROR):
            await application._warm_up_sop_cache(factory)

        assert "warm-up failed" in caplog.text.lower()
