import hashlib
import hmac
import json
import logging
import time
from typing import Any

from mcp.server import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_server.application.ports import ISlackApiPort
from mcp_server.application.service_interfaces import ISearchConnectorService
from mcp_server.domain.search import SearchDocument
from mcp_server.infrastructure.controllers.base_controller import BaseController

logger = logging.getLogger(__name__)

_SIGNATURE_HEADER = "X-Slack-Signature"
_TIMESTAMP_HEADER = "X-Slack-Request-Timestamp"
_MAX_TIMESTAMP_SKEW_SECONDS = 300


class SlackEventsRouteController(BaseController):
    """Handles Slack Enterprise Search live-query events: search, entity details, and connections."""

    __search_connector_service: ISearchConnectorService
    __slack_api: ISlackApiPort
    __signing_secret: str

    def __init__(
        self,
        server: FastMCP,
        search_connector_service: ISearchConnectorService,
        slack_api: ISlackApiPort,
        signing_secret: str,
    ) -> None:
        super().__init__(server)
        self.__search_connector_service = search_connector_service
        self.__slack_api = slack_api
        self.__signing_secret = signing_secret

    def register(self) -> None:
        @self._server.custom_route("/slack/events", methods=["POST"])
        async def slack_events(request: Request) -> JSONResponse:
            body = await request.body()

            if not self._verify_signature(request, body):
                return JSONResponse({"error": "invalid_signature"}, status_code=401)

            payload = json.loads(body or b"{}")
            event = payload.get("event", payload)
            await self._dispatch(event)

            return JSONResponse({"ok": True})

    def _verify_signature(self, request: Request, body: bytes) -> bool:
        timestamp = request.headers.get(_TIMESTAMP_HEADER)
        signature = request.headers.get(_SIGNATURE_HEADER)
        if not timestamp or not signature:
            return False

        try:
            timestamp_age = abs(int(time.time()) - int(timestamp))
        except ValueError:
            return False
        if timestamp_age > _MAX_TIMESTAMP_SKEW_SECONDS:
            return False

        basestring = f"v0:{timestamp}:{body.decode()}".encode()
        expected = "v0=" + hmac.new(self.__signing_secret.encode(), basestring, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def _dispatch(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")

        if event_type == "function_executed":
            await self._handle_function_executed(event)
        elif event_type == "entity_details_requested":
            await self._handle_entity_details_requested(event)
        elif event_type == "user_connection":
            await self._handle_user_connection(event)
        else:
            logger.info("Ignoring unhandled Slack event type: %s", event_type)

    async def _handle_function_executed(self, event: dict[str, Any]) -> None:
        function_execution_id = event["function_execution_id"]
        inputs = event.get("inputs", {})

        try:
            documents = await self.__search_connector_service.handle_search(
                inputs.get("query", ""), inputs.get("filters", {})
            )
            results = [self._to_slack_result(doc) for doc in documents]
            await self.__slack_api.complete_search_success(function_execution_id, results)
        except Exception as exc:
            logger.exception("Search function execution failed")
            await self.__slack_api.complete_search_error(function_execution_id, str(exc))

    @staticmethod
    def _to_slack_result(doc: SearchDocument) -> dict[str, Any]:
        return {
            "external_ref": {"id": doc.external_id},
            "title": doc.title,
            "description": doc.description,
            "link": doc.link,
            "date_updated": doc.date_updated,
            "content": doc.content,
        }

    async def _handle_entity_details_requested(self, event: dict[str, Any]) -> None:
        trigger_id = event["trigger_id"]
        external_ref = event["external_ref"]

        sop = await self.__search_connector_service.handle_entity_details(external_ref)
        await self.__slack_api.present_entity_details(trigger_id, sop)

    async def _handle_user_connection(self, event: dict[str, Any]) -> None:
        subtype = event.get("subtype")
        user_id = event["user"]

        if subtype == "connect":
            await self.__slack_api.update_user_connection(user_id, "connected")
        elif subtype == "disconnect":
            await self.__slack_api.update_user_connection(user_id, "disconnected")
