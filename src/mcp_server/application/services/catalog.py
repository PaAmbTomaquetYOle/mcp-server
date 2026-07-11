"""Prompt and tool catalog for the BrainTrust MCP server."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from secrets import token_urlsafe
from typing import Literal
from urllib.parse import urlencode, urlparse

from mcp.server.fastmcp import FastMCP

from mcp_server.infrastructure.config.settings import Settings

Provider = Literal["jira", "trello"]


@dataclass(slots=True)
class OAuthSession:
    """Represents an in-memory OAuth exchange."""

    provider: Provider
    user_id: str
    state: str
    authorization_url: str
    issued_at: str
    completed_at: str | None = None
    authorization_code: str | None = None


class OAuthMemoryStore:
    """Minimal in-memory OAuth state store for hackathon development."""

    def __init__(self) -> None:
        self._pending: dict[tuple[Provider, str], OAuthSession] = {}
        self._completed: dict[tuple[Provider, str], OAuthSession] = {}

    def generate_authorization(self, provider: Provider, user_id: str, settings: Settings) -> OAuthSession:
        state = token_urlsafe(18)
        issued_at = datetime.now(UTC).isoformat()
        params = self._authorization_params(provider, state, settings)
        base_url = settings.jira_auth_base_url if provider == "jira" else settings.trello_auth_base_url
        session = OAuthSession(
            provider=provider,
            user_id=user_id,
            state=state,
            authorization_url=f"{base_url}?{urlencode(params)}",
            issued_at=issued_at,
        )
        self._pending[(provider, user_id)] = session
        return session

    def complete_authorization(
        self,
        provider: Provider,
        user_id: str,
        code: str,
        state: str | None,
    ) -> OAuthSession:
        key = (provider, user_id)
        session = self._pending.get(key)
        if session is None:
            raise ValueError(f"No pending {provider} authorization exists for user '{user_id}'.")
        if state is not None and state != session.state:
            raise ValueError(f"State mismatch for {provider} authorization.")

        completed = OAuthSession(
            provider=provider,
            user_id=user_id,
            state=session.state,
            authorization_url=session.authorization_url,
            issued_at=session.issued_at,
            completed_at=datetime.now(UTC).isoformat(),
            authorization_code=code,
        )
        self._pending.pop(key, None)
        self._completed[key] = completed
        return completed

    def auth_status(self, provider: Provider, user_id: str) -> str:
        key = (provider, user_id)
        if key in self._completed:
            return "authenticated"
        if key in self._pending:
            return "pending"
        return "not_started"

    @staticmethod
    def _authorization_params(provider: Provider, state: str, settings: Settings) -> dict[str, str]:
        if provider == "jira":
            return {
                "audience": "api.atlassian.com",
                "client_id": settings.jira_client_id,
                "scope": "read:jira-work offline_access",
                "redirect_uri": settings.jira_redirect_uri,
                "state": state,
                "response_type": "code",
                "prompt": "consent",
            }
        return {
            "key": settings.trello_client_id,
            "return_url": settings.trello_redirect_uri,
            "callback_method": "fragment",
            "scope": "read",
            "expiration": "30days",
            "name": "BrainTrust",
            "state": state,
        }


SEARCH_FIXTURES = [
    {
        "external_id": "kb-incident-rollback",
        "title": "Rollback checklist for production incidents",
        "link": "https://braintrust.local/knowledge/incident-rollback",
        "keywords": {"rollback", "incident", "deploy", "production"},
    },
    {
        "external_id": "kb-jira-auth",
        "title": "How to reconnect Jira after token expiry",
        "link": "https://braintrust.local/knowledge/jira-auth",
        "keywords": {"jira", "token", "oauth", "auth", "expired"},
    },
    {
        "external_id": "kb-volunteer-handover",
        "title": "Volunteer handover dossier template",
        "link": "https://braintrust.local/knowledge/volunteer-handover",
        "keywords": {"handover", "offboarding", "dossier", "knowledge"},
    },
    {
        "external_id": "kb-trello-boards",
        "title": "Finding Trello cards before offboarding",
        "link": "https://braintrust.local/knowledge/trello-cards",
        "keywords": {"trello", "board", "cards", "tasks"},
    },
]


def create_mcp_server(settings: Settings) -> FastMCP:
    """Create and configure the FastMCP server instance."""

    server = FastMCP(
        name=settings.app_name,
        instructions=(
            "BrainTrust MCP server for Slack-driven offboarding workflows, Jira/Trello auth, "
            "task extraction prompts, and knowledge lookup."
        ),
        host=settings.host,
        port=settings.port,
        streamable_http_path="/mcp",
        log_level=settings.log_level,
    )
    store = OAuthMemoryStore()

    @server.prompt(
        name="jira_login",
        description="Explain how to authenticate Jira access for the BrainTrust Slack workflows.",
    )
    def jira_login() -> str:
        return (
            "Jira authentication is required before task extraction can run.\n"
            "Next step for the interactive Slack flow: call the MCP tool `generate_jira_auth_url` "
            "with the Slack user id, open the returned URL, then send the callback code to "
            "`complete_jira_auth`."
        )

    @server.prompt(
        name="trello_login",
        description="Explain how to authenticate Trello access for the BrainTrust Slack workflows.",
    )
    def trello_login() -> str:
        return (
            "Trello authentication is required before card extraction can run.\n"
            "Next step for the interactive Slack flow: call the MCP tool `generate_trello_auth_url` "
            "with the Slack user id, open the returned URL, then send the callback code to "
            "`complete_trello_auth`."
        )

    @server.prompt(
        name="extract_pending_jira_tasks",
        description="Return a prompt-friendly summary of pending Jira tasks for an assignee.",
    )
    def extract_pending_jira_tasks(assignee: str) -> str:
        normalized = assignee.strip() or "the departing teammate"
        return (
            f"Pending Jira tasks for {normalized} (development fixture data):\n"
            f"1. Audit open bug triage for {normalized}\n"
            f"2. Hand over release checklist ownership\n"
            f"3. Confirm documentation links for current sprint items\n"
            "These are placeholder results until live Jira integration is implemented."
        )

    @server.prompt(
        name="extract_pending_trello_tasks",
        description="Return a prompt-friendly summary of pending Trello cards for an assignee.",
    )
    def extract_pending_trello_tasks(assignee: str) -> str:
        normalized = assignee.strip() or "the departing teammate"
        return (
            f"Pending Trello cards for {normalized} (development fixture data):\n"
            f"1. Review onboarding board ownership transition\n"
            f"2. Reassign volunteer coordination cards\n"
            f"3. Validate links inside the knowledge-transfer checklist\n"
            "These are placeholder results until live Trello integration is implemented."
        )

    @server.tool(
        name="generate_jira_auth_url",
        description="Create a Jira OAuth authorization URL for a Slack user.",
    )
    def generate_jira_auth_url(user_id: str) -> str:
        session = store.generate_authorization("jira", user_id, settings)
        return json.dumps(
            {
                "provider": "jira",
                "user_id": user_id,
                "status": "pending",
                "authorization_url": session.authorization_url,
                "state": session.state,
                "issued_at": session.issued_at,
            }
        )

    @server.tool(
        name="complete_jira_auth",
        description="Complete the Jira OAuth flow by storing the returned authorization code.",
    )
    def complete_jira_auth(user_id: str, code: str, state: str | None = None) -> str:
        session = store.complete_authorization("jira", user_id, code, state)
        return json.dumps(
            {
                "provider": "jira",
                "user_id": user_id,
                "status": "authenticated",
                "completed_at": session.completed_at,
            }
        )

    @server.tool(
        name="generate_trello_auth_url",
        description="Create a Trello authorization URL for a Slack user.",
    )
    def generate_trello_auth_url(user_id: str) -> str:
        session = store.generate_authorization("trello", user_id, settings)
        return json.dumps(
            {
                "provider": "trello",
                "user_id": user_id,
                "status": "pending",
                "authorization_url": session.authorization_url,
                "state": session.state,
                "issued_at": session.issued_at,
            }
        )

    @server.tool(
        name="complete_trello_auth",
        description="Complete the Trello auth flow by storing the returned token or code.",
    )
    def complete_trello_auth(user_id: str, code: str, state: str | None = None) -> str:
        session = store.complete_authorization("trello", user_id, code, state)
        return json.dumps(
            {
                "provider": "trello",
                "user_id": user_id,
                "status": "authenticated",
                "completed_at": session.completed_at,
            }
        )

    @server.tool(
        name="get_auth_status",
        description="Check whether a Slack user has authenticated Jira or Trello in this dev server.",
    )
    def get_auth_status(user_id: str, provider: Provider) -> str:
        return json.dumps(
            {
                "provider": provider,
                "user_id": user_id,
                "status": store.auth_status(provider, user_id),
            }
        )

    @server.tool(
        name="test_search_query",
        description="Return simple knowledge matches for a free-text query.",
    )
    def test_search_query(query: str) -> str:
        terms = {term.lower() for term in query.replace("?", " ").replace(",", " ").split() if term}
        scored = []
        for item in SEARCH_FIXTURES:
            score = len(terms.intersection(item["keywords"]))
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda pair: (-pair[0], pair[1]["title"]))
        results = [
            {
                "external_id": item["external_id"],
                "title": item["title"],
                "link": build_search_link(settings.search_results_base_url, item["link"]),
            }
            for _, item in scored[: settings.search_max_results]
        ]
        return json.dumps({"results": results})

    return server


def build_search_link(base_url: str, source_link: str) -> str:
    """Project a fixture link onto the configured search base URL."""

    base = base_url.rstrip("/")
    base_path = urlparse(base_url).path.strip("/")
    source_path = urlparse(source_link).path.strip("/")
    if not source_path:
        return base
    if base_path and source_path.startswith(f"{base_path}/"):
        source_path = source_path[len(base_path) + 1 :]
    elif base_path and source_path == base_path:
        source_path = ""
    if not source_path:
        return base
    return f"{base}/{source_path}"
