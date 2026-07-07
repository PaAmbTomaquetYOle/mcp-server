"""Generates offboarding dossier content from an interview transcript using an LLM.

This is where the "model" actually lives — backend's ``LLMDossierGenerator``
is a thin MCP client that just calls the ``generate_dossier`` tool backed by
this service. Keeping the model here lets it use mcp-server's own read-only
data sources (prior dossiers, the SOP index) as native tools during
generation, without a headless service in another repo needing an LLM SDK,
API key, or MCP-client-of-itself hop.
"""

import json
import logging
import re
from typing import Any

from anthropic import AsyncAnthropic

from mcp_server.application.ports import IBackendApiPort
from mcp_server.application.service_interfaces.dossier_generation_service_interface import (
    IDossierGenerationService,
)
from mcp_server.application.service_interfaces.search_connector_service_interface import (
    ISearchConnectorService,
)
from mcp_server.infrastructure.dto.tools.dossier_schemas import GenerateDossierResponse

logger = logging.getLogger(__name__)

DEFAULT_MAX_TOOL_ITERATIONS = 4

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_prior_dossiers",
        "description": (
            "Search prior offboarding dossiers by employee name and/or process id, to see "
            "how the same employee's earlier processes or similar roles were documented."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string"},
                "process_id": {"type": "string"},
            },
        },
    },
    {
        "name": "search_sops",
        "description": (
            "Search the organization's SOP index for knowledge related to a topic raised "
            "in the interview."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = """You write offboarding handover dossiers for departing employees.

You receive an interview transcript (questions and answers, plus any free-form
notes) with a departing employee. Optionally, use the available tools to pull
extra context: `search_prior_dossiers` to look up prior dossiers, and
`search_sops` to search the organization's SOP index for knowledge that
relates to topics mentioned in the interview. Use tools only when they would
materially improve the dossier; it's fine to answer without using any.

When you are done, respond with ONLY a single JSON object (no prose, no
markdown fences) with this exact shape:

{
  "summary": "<one paragraph summarizing the handover, or null>",
  "sections": [
    {"section_type": "responsibilities", "title": "<title>", "responsibilities": ["<string>", ...]},
    {"section_type": "contacts", "title": "<title>", "contacts": [
        {"name": "<string>", "role": "<string>", "email": "<string>", "relationship": "<string>"}
    ]},
    {"section_type": "pending_tasks", "title": "<title>", "tasks": [
        {"description": "<string>", "priority": "<low|medium|high>", "deadline": "<string or null>"}
    ]},
    {"section_type": "knowledge_areas", "title": "<title>", "areas": [
        {"topic": "<string>", "description": "<string>", "expertise_level": "<string>"}
    ]}
  ]
}

Omit section types that don't apply given the interview content. Only include
information actually grounded in the transcript or tool results — never
invent contacts, tasks, or knowledge areas."""


class DossierGenerationService(IDossierGenerationService):
    """Drives an LLM, with mcp-server's own data sources as tools, to write a dossier."""

    def __init__(
        self,
        anthropic_client: AsyncAnthropic,
        model: str,
        backend_api: IBackendApiPort,
        search_connector: ISearchConnectorService,
        max_tool_iterations: int = DEFAULT_MAX_TOOL_ITERATIONS,
        max_tokens: int = 4096,
    ) -> None:
        self.__client = anthropic_client
        self.__model = model
        self.__backend_api = backend_api
        self.__search_connector = search_connector
        self.__max_tool_iterations = max_tool_iterations
        self.__max_tokens = max_tokens

    async def generate(self, interview_transcript: str) -> GenerateDossierResponse:
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": f"Interview transcript:\n\n{interview_transcript}"}
        ]

        for _ in range(self.__max_tool_iterations):
            response = await self.__client.messages.create(
                model=self.__model,
                max_tokens=self.__max_tokens,
                system=SYSTEM_PROMPT,
                tools=_TOOLS,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                return _parse_response(_extract_text(response))

            messages.append(
                {"role": "assistant", "content": [block.model_dump() for block in response.content]}
            )
            messages.append({"role": "user", "content": await self.__execute_tool_calls(response)})

        raise RuntimeError(
            "LLM did not produce a final dossier within "
            f"{self.__max_tool_iterations} tool-call round trips"
        )

    async def __execute_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = await self.__call_tool(block.name, block.input)
                content = json.dumps(output)
                is_error = False
            except Exception as exc:
                logger.warning("Tool '%s' failed during dossier generation: %s", block.name, exc)
                content = f"Error: {exc}"
                is_error = True
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                    "is_error": is_error,
                }
            )
        return results

    async def __call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if name == "search_prior_dossiers":
            return await self.__backend_api.search_dossiers(
                employee_name=arguments.get("employee_name"),
                process_id=arguments.get("process_id"),
            )
        if name == "search_sops":
            documents = await self.__search_connector.test_search(arguments["query"])
            return [doc.model_dump() for doc in documents]
        raise ValueError(f"unknown tool: {name}")


def _extract_text(response: Any) -> str:
    parts = [block.text for block in response.content if block.type == "text"]
    if not parts:
        raise ValueError("LLM response contained no text content")
    return "\n".join(parts)


def _parse_response(text: str) -> GenerateDossierResponse:
    match = _JSON_FENCE.search(text)
    payload = json.loads(match.group(1) if match else text.strip())
    return GenerateDossierResponse.model_validate(payload)
