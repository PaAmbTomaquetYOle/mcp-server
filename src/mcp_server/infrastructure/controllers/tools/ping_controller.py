from mcp_server.infrastructure.controllers import BaseController
from mcp_server.infrastructure.dto.tools import PingResult


class PingToolController(BaseController):
    """Controller for the ping tool, a health-check endpoint verifying the MCP server is reachable and responding."""

    def register(self) -> None:
        self._server.add_tool(
            self.ping,
            name="ping",
            description=(
                "Health-check tool. Returns 'pong' to verify"
                " the MCP server is reachable and responding."
            ),
        )

    async def ping(self) -> PingResult:
        """Check server health.

        Returns:
            PingResult: A fixed 'pong' response confirming connectivity.
        """
        return PingResult(message="pong")
