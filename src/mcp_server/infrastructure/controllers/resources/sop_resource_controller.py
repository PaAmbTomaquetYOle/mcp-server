from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ISearchConnectorService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import resource_error_handler
from mcp_server.infrastructure.dto import SopDetail, SopListItem, SopListResponse


class SopResourceController(BaseController):
    """Controller exposing SOPs as MCP resources: a browsable list and per-id detail.

    Reuses the same ``ISearchConnectorService`` (and its underlying SOP cache /
    backend API) already used by the ``test_search_query`` and ``get_sop``
    flows, so resource reads stay consistent with tool reads.
    """

    __service: ISearchConnectorService

    def __init__(self, server: FastMCP, service: ISearchConnectorService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.resource(
            "sop://offboardme/sops",
            name="sop_list",
            title="Standard Operating Procedures",
            description="All SOPs currently cached for Slack search, as a JSON list of id/title/tags.",
            mime_type="application/json",
        )(self.list_sops)

        self._server.resource(
            "sop://offboardme/sops/{sop_id}",
            name="sop_detail",
            title="SOP detail",
            description="Full content of a single SOP, by id.",
            mime_type="application/json",
        )(self.get_sop)

    @resource_error_handler
    async def list_sops(self) -> str:
        """List all SOPs currently cached for Slack search.

        Returns:
            A JSON-encoded SopListResponse (id, title, tags per SOP).
        """
        documents = await self.__service.test_search("")
        sops = [SopListItem(id=doc.external_id, title=doc.title, tags=doc.tags) for doc in documents]
        return SopListResponse(sops=sops, count=len(sops)).model_dump_json()

    @resource_error_handler
    async def get_sop(self, sop_id: str) -> str:
        """Retrieve a single SOP's full content by id.

        Args:
            sop_id (str): The SOP's ID.
        Returns:
            A JSON-encoded SopDetail.
        """
        raw = await self.__service.handle_entity_details({"id": sop_id})
        detail = SopDetail(
            id=str(raw["id"]),
            title=raw.get("title", ""),
            content=raw["content"],
            author=raw["author"],
            tags=list(raw.get("tags", [])),
            origin_channel=raw["origin_channel"],
            version=raw.get("version", 0),
            created_at=str(raw["created_at"]),
            updated_at=str(raw["updated_at"]),
        )
        return detail.model_dump_json()
