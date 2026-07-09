import asyncio
import logging

import anyio

from mcp_server.infrastructure.config import McpServerSettings, ServerFactory

logger = logging.getLogger(__name__)


class Application:
    def __init__(self) -> None:
        self._settings = McpServerSettings()

    def run(self) -> None:
        factory = ServerFactory.get_instance(self._settings)
        server = factory.create()

        async def _run_with_cache_refresh() -> None:
            asyncio.create_task(self._refresh_sop_cache_periodically(factory))
            await server.run_streamable_http_async()

        anyio.run(_run_with_cache_refresh)

    async def _refresh_sop_cache_periodically(self, factory: ServerFactory) -> None:
        service = factory.get_search_connector_service()
        while True:
            try:
                await service.refresh_cache()
            except Exception:
                logger.exception("Periodic SOP cache refresh failed")
            await asyncio.sleep(self._settings.sop_cache_ttl_seconds)


def main():
    Application().run()


if __name__ == "__main__":
    main()
