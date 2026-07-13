<div align="center">

![BrainTrust · MCP Server](https://capsule-render.vercel.app/api?type=waving&color=0:2B0B3F,50:6E56CF,100:1a1a2e&height=200&section=header&text=BrainTrust%20%C2%B7%20MCP%20Server&fontSize=44&fontColor=ffffff&desc=Tools%2C%20prompts%20%26%20the%20LLM%20dossier%20writer%20for%20the%20offboarding%20agent&descSize=17&descAlignY=62&animation=fadeIn&reversal=false)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)](pyproject.toml)
[![MCP SDK 1.28](https://img.shields.io/badge/MCP%20SDK-1.28-6E56CF)](https://modelcontextprotocol.io)
[![Transport: streamable-HTTP](https://img.shields.io/badge/transport-streamable--HTTP-informational)](#)
[![Anthropic](https://img.shields.io/badge/LLM-Claude%20(Anthropic)-D97757)](https://www.anthropic.com/)

**🔌 mcp-server** &nbsp;·&nbsp; **🗄️ [backend](https://github.com/PaAmbTomaquetYOle/backend)** &nbsp;·&nbsp; **💬 [slack-agent](https://github.com/PaAmbTomaquetYOle/slack-agent)**

</div>

The tool provider of **BrainTrust**: an [MCP](https://modelcontextprotocol.io) server, built with the official Python SDK's `FastMCP`, that exposes Jira/Trello/Slack integrations and offboarding-dossier tools over streamable HTTP. **slack-agent**'s Gemini-driven interview agent connects to it as an MCP client during the guided interview; **backend**'s `LLMDossierGenerator` connects to it to generate the handover dossier itself — the LLM call for dossier writing lives *here*, not in the backend, so it's reusable by any MCP client and the backend never needs an LLM SDK or API key.

### 📚 Contents

- [🧰 Tools](#-tools)
- [💬 Prompts](#-prompts)
- [🏗 Architecture role](#-architecture-role)
- [🚀 Local development](#-local-development)
- [⚙️ Configuration](#️-configuration)
- [🧪 Testing](#-testing)

## 🧰 Tools

| Tool | What it does |
|---|---|
| `ping` | Health check — returns `pong` to verify the server is reachable. |
| `generate_dossier` | **The dossier writer.** Runs an LLM (Claude) over a completed interview transcript to produce a summary + typed sections, optionally consulting `search_prior_dossiers`/`search_sops` as native tools for extra context. `review_scope` (`offboarding` default / `monthly` / `annual`, MCP-15) selects the prompt and token budget: offboarding/monthly stay lightweight, annual is exhaustive with a larger token budget. Backed by `DossierGenerationService`. |
| `get_dossier` | Search past offboarding dossiers by `employee_name` and/or `process_id` (proxies backend's API). |
| `get_jira_issue` / `get_pending_jira_issues` | Fetch a specific Jira issue, or all pending issues assigned to a user. Requires Jira auth. |
| `get_trello_card` / `get_pending_trello_cards` | Fetch a specific Trello card, or all pending cards assigned to a user. Requires Trello auth. |
| `generate_jira_auth_url` / `complete_jira_auth` | Atlassian OAuth 2.0 (3LO) flow — the callback endpoint normally handles `complete_jira_auth` automatically. |
| `generate_trello_auth_url` / `complete_trello_auth` | Trello OAuth 1.0a flow — resolves and stores the Trello username as `user_id`. |
| `generate_slack_auth_url` / `complete_slack_auth` | Slack OAuth 2.0 user-token flow (search scopes) — required before `search_slack_workspace`. |
| `search_slack_workspace` | Search Slack's own messages/files/channels/users on behalf of an authenticated user via the **Real-Time Search API** (`assistant.search.context`). |
| `search_connector_status` | Health of the Slack Enterprise Search connector: backend reachability + SOP cache stats. |
| `test_search_query` | Search the cached SOP index directly, without going through Slack — used by slack-agent's question-suggestion feature (SA-8). |
| `refresh_search_index` | Force a full refresh of the SOP search cache from the backend. |
| `get_search_analytics` | Cache hit/miss statistics for the search connector. |

## 💬 Prompts

| Prompt | Purpose |
|---|---|
| `extract_pending_jira_tasks` | Guided extraction of a given assignee's pending Jira issues. |
| `extract_pending_trello_tasks` | Guided extraction of a given assignee's pending Trello cards. |
| `jira_login` | Walk the user through the Jira OAuth 2.0 authorization flow. |
| `trello_login` | Walk the user through the Trello OAuth 1.0a authorization flow. |
| `slack_login` | Walk the user through the Slack OAuth 2.0 authorization flow (search scopes). |
| `manage_search_connector` | Check and maintain the Slack Enterprise Search connector for SOPs. |

## 🏗 Architecture role

```
slack-agent  ──MCP client──▶  mcp-server  ◀──MCP client──  backend
 (interview agent,               (this repo)              (LLMDossierGenerator,
  Jira/Trello/Slack tools)                                  generate_dossier only)
                                     │
                                     ├─▶ Jira / Trello / Slack APIs
                                     ├─▶ Anthropic (Claude) — generate_dossier
                                     ├─▶ backend's REST API — get_dossier, SOP search
                                     ├─▶ Kafka producer — knowledge_graph.interaction_registered
                                     └─◀ Kafka consumer — sop.{created,updated,deleted}
```

Two independent MCP clients talk to this server for different reasons: **slack-agent** uses the collaboration-tool and search tools during the live interview; **backend** uses only `generate_dossier`, once per completed interview, from its Kafka consumer.

### Kafka

`mcp-server` is a lightweight Kafka citizen, matching backend's and slack-agent's transport
security (SASL_SSL + SCRAM-SHA-512 in the shared docker-compose broker):

- **Producer:** the `add_interaction` tool publishes `knowledge_graph.interaction_registered`
  to `slack-agent.knowledge_graph.interaction_registered` — consumed by backend's knowledge graph.
- **Consumer:** a background task subscribes to `{prefix}.sop.created/updated/deleted`
  (published by backend) and calls `refresh_cache()` on the SOP search connector whenever any
  of them fires. This is purely a latency optimization on top of the existing
  `MCP_SERVER_SOP_CACHE_TTL_SECONDS` poll, which stays in place as a backstop — if the broker is
  unreachable or misconfigured, the server still starts and the cache just refreshes on the TTL
  alone. See `backend/docs/asyncapi/asyncapi.yml` for the canonical event contract.

## 🚀 Local development

Run the server:

```powershell
uv run mcp-server
```

Open the MCP Inspector:

```powershell
uv run mcp-inspector
```

Open the Inspector already pointed to the local server:

```powershell
uv run mcp-inspector-local
```

Then connect it to:

```text
http://localhost:8000/mcp
```

## ⚙️ Configuration

All settings are environment variables prefixed `MCP_SERVER_` (see [`.env.example`](.env.example) for the full, documented list — OAuth setup steps included for Jira/Trello/Slack). Highlights:

- `MCP_SERVER_ANTHROPIC_API_KEY` / `MCP_SERVER_ANTHROPIC_MODEL` — required for `generate_dossier`.
- `MCP_SERVER_BACKEND_API_URL` / `MCP_SERVER_BACKEND_JWT_SECRET` — how this server calls back into backend (`get_dossier`, SOPs); the JWT secret must match `BACKEND_JWT_SECRET` shared across all three repos.
- `MCP_SERVER_JIRA_*` / `MCP_SERVER_TRELLO_*` / `MCP_SERVER_SLACK_*` — OAuth credentials for each collaboration tool.
- `MCP_SERVER_SOP_CACHE_TTL_SECONDS` — refresh interval for the in-memory SOP search cache.

## 🧪 Testing

```powershell
uv run pytest
```

---

<div align="center">

Part of **BrainTrust** — fighting knowledge loss from volunteer turnover in NGOs.

[backend](https://github.com/PaAmbTomaquetYOle/backend) &nbsp;·&nbsp; [slack-agent](https://github.com/PaAmbTomaquetYOle/slack-agent) &nbsp;·&nbsp; MIT © [Pa Amb Tomàquet Y Olé](LICENSE)

</div>

