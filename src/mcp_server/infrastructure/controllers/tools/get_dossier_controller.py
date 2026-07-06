from mcp.server import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.application.ports import IBackendApiPort
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import DossierSearchResult, GetDossierResponse


class GetDossierToolController(BaseController):
    """Controller for the tool that searches offboarding handover dossiers via the backend API."""

    __backend_api: IBackendApiPort

    def __init__(self, server: FastMCP, backend_api: IBackendApiPort) -> None:
        super().__init__(server)
        self.__backend_api = backend_api

    def register(self) -> None:
        self._server.add_tool(
            self.get_dossier,
            name="get_dossier",
            title="Search offboarding dossiers",
            description=(
                "Search for handover dossiers documenting what a departing volunteer left "
                "pending. Search by employee_name (partial, case-insensitive match) and/or "
                "process_id. At least one of the two must be provided. Use this to answer "
                "questions about previous offboardings, e.g. 'what did Juan leave pending?'."
            ),
        )

    @tool_error_handler
    async def get_dossier(
        self,
        employee_name: str | None = None,
        process_id: str | None = None,
    ) -> GetDossierResponse:
        """Search offboarding dossiers by employee name and/or process ID.

        Args:
            employee_name (str | None): Partial, case-insensitive employee display name to search for.
            process_id (str | None): Exact offboarding process ID to filter by.
        Returns:
            GetDossierResponse containing the matching dossiers.
        """
        if employee_name is None and process_id is None:
            raise ToolError("At least one of 'employee_name' or 'process_id' must be provided.")

        raw_results = await self.__backend_api.search_dossiers(
            employee_name=employee_name, process_id=process_id
        )
        results = [DossierSearchResult.model_validate(r) for r in raw_results]
        return GetDossierResponse(results=results, count=len(results))
