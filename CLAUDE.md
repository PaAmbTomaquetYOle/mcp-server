# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

MCP server (built on the official Python SDK's `FastMCP`, streamable-HTTP transport) — the tool provider for **BrainTrust** (OffboardMe). Exposes Jira/Trello/Slack integrations and the `generate_dossier` LLM tool. `slack-agent` connects as an MCP client during the guided interview (collaboration + search tools); `backend`'s `LLMDossierGenerator` connects to call only `generate_dossier`, once per completed interview. See the parent `../CLAUDE.md` for cross-repo architecture and `README.md` for the full tool/prompt tables.

## Commands

```bash
uv sync                       # install deps
uv run mcp-server             # run the server (streamable-HTTP at http://localhost:8000/mcp)
uv run mcp-inspector           # open MCP Inspector (unconnected)
uv run mcp-inspector-local      # open MCP Inspector pre-pointed at the local server
uv run pytest                  # run tests (make test)
uv run pytest tests/domain/search/test_x.py::test_name -v   # single test
uv run pytest -m unit          # only unit tests (isolated, no I/O)
uv run pytest -m integration   # only integration tests (MCP handshake, SSE, DB)
uv run pytest --cov --cov-report=html   # HTML coverage -> htmlcov/index.html (make test-cov)
uv run ruff check .            # lint (make lint)
```

Requires `.env` (copy from `.env.example`), all settings prefixed `MCP_SERVER_`. Coverage gate: `fail_under = 60` (see `pyproject.toml`).

## Architecture

**Hexagonal**, under `src/mcp_server/`:

- **`domain/`** — `collaboration_tasks/` (Jira/Trello task entities), `search/` (SOP search domain), `enums/`. Framework-agnostic.
- **`application/`** — `ports/` (interfaces for Jira/Trello/Slack clients, LLM, backend API), `service_interfaces/`, `services/` — one service per capability: `dossier_generation_service.py` (the LLM tool-use loop), `collaboration_tool_integration_service.py`, `jira_auth_service.py` / `trello_auth_service.py` / `slack_auth_service.py` (OAuth flows), `slack_workspace_search_service.py`, `search_connector_service.py` (SOP cache), `knowledge_graph_service.py`.
- **`infrastructure/controllers/`** — Primary adapters registered against `FastMCP`, split by MCP primitive:
  - `tools/` — one controller per MCP tool (`ping`, `generate_dossier`, `get_dossier`, `get_jira_issue`, `get_pending_jira_issues`, `get_trello_card`, `get_pending_trello_cards`, `generate_jira_auth_url`/`complete_jira_auth`, `generate_trello_auth_url`/`complete_trello_auth`, `generate_slack_auth_url`/`complete_slack_auth`, `search_slack_workspace`, `search_connector_status`, `test_search_query`, `refresh_search_index`, `get_search_analytics`).
  - `prompts/` — guided multi-step prompts (`extract_pending_jira_tasks`, `extract_pending_trello_tasks`, `jira_login`, `trello_login`, `slack_login`, `manage_search_connector`).
  - `routes/` — raw HTTP routes for OAuth callbacks (`oauth_callback_controller.py`, `slack_oauth_callback_controller.py`) and `slack_events_controller.py`.
  - All controllers extend `base_controller.py`; `error_handler.py` centralizes MCP error responses.
- **`infrastructure/adapters/`** — concrete Jira/Trello/Slack/Anthropic/backend-API clients implementing the application ports.
- **`infrastructure/dto/tools/`** — request/response DTOs per tool, kept separate from domain entities.
- **`infrastructure/templates/`** — Jinja2 templates (OAuth landing pages, etc.) — excluded from coverage (`omit` in `pyproject.toml`).

### The LLM call for dossier generation lives here, not in backend

`generate_dossier` (`generate_dossier_controller.py` → `DossierGenerationService`) runs Claude (Anthropic SDK) over a completed interview transcript, with `search_prior_dossiers`/`search_sops` available to the model as native tools for extra context, producing `{"summary": ..., "sections": [...]}` (typed by `section_type`: `responsibilities`, `contacts`, `pending_tasks`, `knowledge_areas`). Keeping the model here means `backend` never needs an LLM SDK or API key, and the same generation capability is reusable by any MCP client — don't move this logic into backend when touching dossier generation.

### Three independent OAuth flows

Jira uses OAuth 2.0 (3LO) via `generate_jira_auth_url`/`complete_jira_auth`, Trello uses OAuth 1.0a via `generate_trello_auth_url`/`complete_trello_auth`, Slack uses OAuth 2.0 user-token (search scopes) via `generate_slack_auth_url`/`complete_slack_auth`. Callback endpoints in `routes/` normally handle completion automatically — the `complete_*` tools exist for manual/fallback completion. `search_slack_workspace` requires the Slack flow to have completed first (uses the Real-Time Search API, `assistant.search.context`).

### SOP search cache

`search_connector_service.py` maintains an in-memory cache of SOPs refreshed from backend every `MCP_SERVER_SOP_CACHE_TTL_SECONDS`. `test_search_query` queries this cache directly (used by slack-agent's question-suggestion feature) without going through Slack; `refresh_search_index` forces an immediate refresh; `get_search_analytics`/`search_connector_status` expose cache hit/miss stats and backend reachability for debugging.
