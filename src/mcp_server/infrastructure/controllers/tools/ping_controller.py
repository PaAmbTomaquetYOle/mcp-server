from mcp.server import FastMCP

from mcp_server.infrastructure.dto.tools import PingResult


class PingToolController:
    def __init__(self, server: FastMCP) -> None:
        self._server = server

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
