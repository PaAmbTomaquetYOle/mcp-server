from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

from mcp_server.application.ports import IBackendApiPort
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import resource_error_handler
from mcp_server.infrastructure.dto import DossierSearchResult


class DossierResourceController(BaseController):
    """Controller exposing offboarding handover dossiers as an MCP resource, keyed by process_id.

    Reuses ``IBackendApiPort.search_dossiers`` — the same path ``GetDossierToolController``
    uses — rather than opening a new fetch path.
    """

    __backend_api: IBackendApiPort

    def __init__(self, server: FastMCP, backend_api: IBackendApiPort) -> None:
        super().__init__(server)
        self.__backend_api = backend_api

    def register(self) -> None:
        self._server.resource(
            "dossier://offboardme/dossiers/{process_id}",
            name="dossier_detail",
            title="Handover dossier",
            description="Handover dossier documenting what a departing volunteer left pending, by process_id.",
            mime_type="application/json",
        )(self.get_dossier)

    @resource_error_handler
    async def get_dossier(self, process_id: str) -> str:
        """Retrieve a handover dossier by its offboarding process_id.

        Args:
            process_id (str): The offboarding process ID.
        Returns:
            A JSON-encoded DossierSearchResult.
        """
        raw_results = await self.__backend_api.search_dossiers(process_id=process_id)
        if not raw_results:
            raise ResourceError(f"No dossier found for process_id: {process_id}")

        dossier = DossierSearchResult.model_validate(raw_results[0])
        return dossier.model_dump_json()
