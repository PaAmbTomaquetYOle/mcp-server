import logging

from mcp.server import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse

from mcp_server.application.service_interfaces import ISlackAuthService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.templates import render_template

logger = logging.getLogger(__name__)


class SlackOAuthCallbackController(BaseController):
    """Handles the OAuth 2.0 redirect callback from Slack for the workspace search connector."""

    __slack_auth_service: ISlackAuthService

    def __init__(self, server: FastMCP, slack_auth_service: ISlackAuthService) -> None:
        super().__init__(server)
        self.__slack_auth_service = slack_auth_service

    def register(self) -> None:
        @self._server.custom_route("/slack/oauth/callback", methods=["GET"])
        async def slack_oauth_callback(request: Request) -> HTMLResponse:
            code = request.query_params.get("code")

            if not code:
                return HTMLResponse(
                    render_template("slack_oauth_error.html", error="Missing required parameter: code."),
                    status_code=400,
                )

            try:
                result = await self.__slack_auth_service.exchange_auth_code(code)
            except Exception as exc:
                logger.exception("Slack OAuth callback failed")
                return HTMLResponse(
                    render_template("slack_oauth_error.html", error=str(exc)),
                    status_code=500,
                )

            return HTMLResponse(render_template("slack_oauth_success.html", slack_user_id=result["slack_user_id"]))
