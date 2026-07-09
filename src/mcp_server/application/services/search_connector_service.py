from typing import Any

from mcp_server.application.ports import CacheStats, IBackendApiPort, ISopCachePort
from mcp_server.application.service_interfaces.search_connector_service_interface import (
    ConnectorStatus,
    ISearchConnectorService,
)
from mcp_server.domain import BackendApiException
from mcp_server.domain.search import SearchDocument

_SOP_PAGE_SIZE = 100


class SearchConnectorService(ISearchConnectorService):
    """Orchestrates the Slack Enterprise Search connector: cache-backed live search over SOPs."""

    __backend_api: IBackendApiPort
    __sop_cache: ISopCachePort
    __sop_base_url: str

    def __init__(self, backend_api: IBackendApiPort, sop_cache: ISopCachePort, sop_base_url: str) -> None:
        self.__backend_api = backend_api
        self.__sop_cache = sop_cache
        self.__sop_base_url = sop_base_url

    async def handle_search(self, query: str, filters: dict[str, str]) -> list[SearchDocument]:
        return await self.__sop_cache.search(query, filters)

    async def test_search(self, query: str) -> list[SearchDocument]:
        return await self.__sop_cache.search(query, {})

    async def handle_entity_details(self, external_ref: dict[str, Any]) -> dict[str, Any]:
        return await self.__backend_api.get_sop(external_ref["id"])

    async def refresh_cache(self) -> CacheStats:
        documents = await self._fetch_all_sops()
        await self.__sop_cache.refresh(documents)
        return await self.__sop_cache.get_stats()

    async def get_status(self) -> ConnectorStatus:
        backend_reachable = await self._is_backend_reachable()
        return ConnectorStatus(
            backend_reachable=backend_reachable,
            cache=await self.__sop_cache.get_stats(),
            is_stale=await self.__sop_cache.is_stale(),
        )

    async def _is_backend_reachable(self) -> bool:
        try:
            await self.__backend_api.search_sops(page=1, size=1)
            return True
        except BackendApiException:
            return False

    async def _fetch_all_sops(self) -> list[SearchDocument]:
        documents: list[SearchDocument] = []
        page = 1
        while True:
            result = await self.__backend_api.search_sops(page=page, size=_SOP_PAGE_SIZE)
            items = result.get("items", [])
            documents.extend(SearchDocument.from_sop(sop, base_url=self.__sop_base_url) for sop in items)

            if page >= result.get("total_pages", 1):
                break
            page += 1

        return documents
