import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP
from starlette.testclient import TestClient

from mcp_server.domain.search import SearchDocument
from mcp_server.infrastructure.controllers.routes.slack_events_controller import SlackEventsRouteController

_SIGNING_SECRET = "test-signing-secret"

_DOC = SearchDocument(
    external_id="1",
    title="Restart deploy pipeline",
    description="Restart deploy pipeline",
    content="Restart deploy pipeline",
    link="https://x/sops/1",
    author="U1",
    tags=["deploy"],
    origin_channel="C1",
    date_updated="2026-01-01",
)


def _sign(body: bytes, timestamp: str) -> str:
    basestring = f"v0:{timestamp}:{body.decode()}".encode()
    digest = hmac.new(_SIGNING_SECRET.encode(), basestring, hashlib.sha256).hexdigest()
    return f"v0={digest}"


def _signed_headers(body: bytes, timestamp: str | None = None) -> dict[str, str]:
    timestamp = timestamp or str(int(time.time()))
    return {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": _sign(body, timestamp),
        "Content-Type": "application/json",
    }


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.handle_search = AsyncMock(return_value=[_DOC])
    service.handle_entity_details = AsyncMock(return_value={"id": "1", "content": "Restart deploy pipeline"})
    return service


@pytest.fixture
def mock_slack_api():
    api = AsyncMock()
    api.complete_search_success = AsyncMock()
    api.complete_search_error = AsyncMock()
    api.present_entity_details = AsyncMock()
    api.update_user_connection = AsyncMock()
    return api


@pytest.fixture
def app(mock_service, mock_slack_api):
    server = FastMCP(name="test-slack-events")
    SlackEventsRouteController(server, mock_service, mock_slack_api, signing_secret=_SIGNING_SECRET).register()
    return server.streamable_http_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class TestSignatureVerification:
    def test_rejects_missing_signature(self, client):
        response = client.post("/slack/events", content=b"{}")

        assert response.status_code == 401

    def test_rejects_invalid_signature(self, client):
        body = b'{"event": {"type": "function_executed"}}'
        headers = {
            "X-Slack-Request-Timestamp": str(int(time.time())),
            "X-Slack-Signature": "v0=invalid",
        }
        response = client.post("/slack/events", content=body, headers=headers)

        assert response.status_code == 401

    def test_rejects_stale_timestamp(self, client):
        body = b'{"event": {"type": "function_executed"}}'
        stale_timestamp = str(int(time.time()) - 301)
        headers = _signed_headers(body, timestamp=stale_timestamp)

        response = client.post("/slack/events", content=body, headers=headers)

        assert response.status_code == 401

    def test_rejects_non_integer_timestamp(self, client):
        body = b'{"event": {"type": "function_executed"}}'
        headers = {
            "X-Slack-Request-Timestamp": "not-a-number",
            "X-Slack-Signature": _sign(body, "not-a-number"),
        }
        response = client.post("/slack/events", content=body, headers=headers)

        assert response.status_code == 401


class TestFunctionExecuted:
    def test_handles_search_and_reports_success(self, client, mock_service, mock_slack_api):
        payload = {
            "event": {
                "type": "function_executed",
                "function_execution_id": "fx1",
                "inputs": {"query": "deploy", "filters": {}},
            }
        }
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_service.handle_search.assert_awaited_once_with("deploy", {})
        mock_slack_api.complete_search_success.assert_awaited_once()
        call_args = mock_slack_api.complete_search_success.await_args.args
        assert call_args[0] == "fx1"
        assert call_args[1][0]["external_ref"] == {"id": "1"}
        assert call_args[1][0]["title"] == "Restart deploy pipeline"

    def test_reports_error_when_search_fails(self, client, mock_service, mock_slack_api):
        mock_service.handle_search.side_effect = Exception("boom")
        payload = {
            "event": {
                "type": "function_executed",
                "function_execution_id": "fx1",
                "inputs": {"query": "deploy", "filters": {}},
            }
        }
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_slack_api.complete_search_error.assert_awaited_once()
        assert mock_slack_api.complete_search_error.await_args.args[0] == "fx1"


class TestEntityDetailsRequested:
    def test_handles_entity_details_and_presents_them(self, client, mock_service, mock_slack_api):
        payload = {
            "event": {
                "type": "entity_details_requested",
                "trigger_id": "trigger1",
                "external_ref": {"id": "1"},
            }
        }
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_service.handle_entity_details.assert_awaited_once_with({"id": "1"})
        mock_slack_api.present_entity_details.assert_awaited_once()
        assert mock_slack_api.present_entity_details.await_args.args[0] == "trigger1"


class TestUserConnection:
    def test_disconnect_updates_status(self, client, mock_slack_api):
        payload = {"event": {"type": "user_connection", "subtype": "disconnect", "user": "U1"}}
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_slack_api.update_user_connection.assert_awaited_once_with("U1", "disconnected")

    def test_connect_updates_status(self, client, mock_slack_api):
        payload = {"event": {"type": "user_connection", "subtype": "connect", "user": "U1"}}
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_slack_api.update_user_connection.assert_awaited_once_with("U1", "connected")


class TestUnknownEventType:
    def test_ignores_unknown_event_type(self, client, mock_slack_api):
        payload = {"event": {"type": "something_else"}}
        body = json.dumps(payload).encode()

        response = client.post("/slack/events", content=body, headers=_signed_headers(body))

        assert response.status_code == 200
        mock_slack_api.complete_search_success.assert_not_awaited()
