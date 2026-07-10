from unittest.mock import AsyncMock

import pytest

from mcp_server.application.ports.slack_auth import SlackAuthResult
from mcp_server.application.services.slack_auth_service import SlackAuthService


@pytest.fixture
def mock_slack_auth_port():
    port = AsyncMock()
    port.generate_auth_url = AsyncMock(return_value="https://slack.com/oauth/v2/authorize?...")
    port.exchange_auth_code = AsyncMock(
        return_value=SlackAuthResult(slack_user_id="U1", team_id="T1", access_token="xoxp-test")
    )
    return port


@pytest.fixture
def service(mock_slack_auth_port):
    return SlackAuthService(mock_slack_auth_port)


class TestGenerateAuthUrl:
    @pytest.mark.anyio
    async def test_delegates_to_port(self, service, mock_slack_auth_port):
        url = await service.generate_auth_url(state="oauth")

        assert url == "https://slack.com/oauth/v2/authorize?..."
        mock_slack_auth_port.generate_auth_url.assert_awaited_once_with("oauth")


class TestExchangeAuthCode:
    @pytest.mark.anyio
    async def test_delegates_to_port(self, service, mock_slack_auth_port):
        result = await service.exchange_auth_code("code123")

        assert result["slack_user_id"] == "U1"
        mock_slack_auth_port.exchange_auth_code.assert_awaited_once_with("code123")
