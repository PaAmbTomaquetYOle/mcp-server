"""Entrypoint for the BrainTrust MCP server."""

from __future__ import annotations

import uvicorn

from mcp_server.infrastructure.config.settings import get_settings


def main() -> None:
    """Run the MCP server over HTTP."""

    def run(self) -> None:
        factory = ServerFactory.get_instance(self._settings)
        server = factory.create()

        async def _run_with_cache_refresh() -> None:
            await self._warm_up_sop_cache(factory)
            asyncio.create_task(self._refresh_sop_cache_periodically(factory))
            await server.run_streamable_http_async()

        anyio.run(_run_with_cache_refresh)

    async def _warm_up_sop_cache(self, factory: ServerFactory) -> None:
        """Populate the SOP cache once before serving traffic, so searches never see it empty."""
        service = factory.get_search_connector_service()
        try:
            await service.refresh_cache()
        except Exception:
            logger.exception("Initial SOP cache warm-up failed")

    async def _refresh_sop_cache_periodically(self, factory: ServerFactory) -> None:
        service = factory.get_search_connector_service()
        while True:
            await asyncio.sleep(self._settings.sop_cache_ttl_seconds)
            try:
                await service.refresh_cache()
            except Exception:
                logger.exception("Periodic SOP cache refresh failed")


def main():
    Application().run()


if __name__ == "__main__":
    main()
