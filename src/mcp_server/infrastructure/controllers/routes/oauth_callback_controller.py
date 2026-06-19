import logging

from mcp.server import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse

from mcp_server.application.service_interfaces import IJiraAuthService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.templates import render_template

logger = logging.getLogger(__name__)


class OAuthCallbackController(BaseController):
    """Handles the OAuth 2.0 redirect callback from Atlassian."""

    __jira_auth_service: IJiraAuthService

    def __init__(self, server: FastMCP, jira_auth_service: IJiraAuthService) -> None:
        super().__init__(server)
        self.__jira_auth_service = jira_auth_service

    def register(self) -> None:
        @self._server.custom_route("/callback", methods=["GET"])
        async def oauth_callback(request: Request) -> HTMLResponse:
            code = request.query_params.get("code")

            if not code:
                return HTMLResponse(
                    render_template("oauth_error.html", error="Missing required parameter: code."),
                    status_code=400,
                )

            try:
                result = await self.__jira_auth_service.exchange_auth_code(code)
            except Exception as exc:
                logger.exception("OAuth callback failed")
                return HTMLResponse(
                    render_template("oauth_error.html", error=str(exc)),
                    status_code=500,
                )

            return HTMLResponse(render_template("oauth_success.html", email=result["email"]))
