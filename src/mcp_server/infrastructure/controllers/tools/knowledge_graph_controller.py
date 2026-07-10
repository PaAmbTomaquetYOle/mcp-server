from mcp.server import FastMCP

from mcp_server.application.service_interfaces import IKnowledgeGraphService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import (
    AddInteractionResponse,
    DocumentInfo,
    ExpertResult,
    KnowledgeMapResponse,
    PersonInfo,
    QueryExpertsResponse,
    TopicInfo,
)


class KnowledgeGraphToolController(BaseController):
    """Controller for tools that query and feed the organization's Knowledge Graph."""

    __service: IKnowledgeGraphService

    def __init__(self, server: FastMCP, service: IKnowledgeGraphService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.add_tool(
            self.query_experts,
            name="query_experts",
            title="Query topic experts",
            description=(
                "Search for people who are experts on a given topic, ranked by expertise "
                "score. Use this to find who to ask about a specific subject."
            ),
        )
        self._server.add_tool(
            self.add_interaction,
            name="add_interaction",
            title="Register knowledge interaction",
            description=(
                "Register that a person demonstrated knowledge on a topic, feeding the "
                "knowledge graph. Use interaction_type='knows' for general expertise, or "
                "'answered' when the interaction came from answering a question."
            ),
        )
        self._server.add_tool(
            self.get_knowledge_map,
            name="get_knowledge_map",
            title="Get person knowledge map",
            description=(
                "Retrieve the knowledge map of a person: the topics they are known for and "
                "the documents they authored or are associated with."
            ),
        )

    @tool_error_handler
    async def query_experts(self, topic: str, limit: int = 10) -> QueryExpertsResponse:
        """Search for experts on a given topic.

        Args:
            topic (str): The topic to search experts for.
            limit (int): Maximum number of experts to return.
        Returns:
            QueryExpertsResponse containing the matching experts, ranked by score.
        """
        raw_results = await self.__service.query_experts(topic, limit=limit)
        experts = [
            ExpertResult(person=PersonInfo(**r["person"]), topic=r["topic"], score=r["score"])
            for r in raw_results
        ]
        return QueryExpertsResponse(topic=topic, experts=experts, count=len(experts))

    @tool_error_handler
    async def add_interaction(
        self,
        person_id: str,
        person_name: str,
        topic_name: str,
        interaction_type: str = "knows",
        department: str | None = None,
        topic_description: str | None = None,
    ) -> AddInteractionResponse:
        """Register a knowledge interaction between a person and a topic.

        Args:
            person_id (str): The person's ID (e.g. Slack user ID).
            person_name (str): The person's display name.
            topic_name (str): The topic they demonstrated knowledge on.
            interaction_type (str): Either "knows" (general expertise) or "answered"
                (demonstrated by answering a question).
            department (str | None): The person's department, if known.
            topic_description (str | None): A short description of the topic, if known.
        Returns:
            AddInteractionResponse confirming the event was published.
        """
        result = await self.__service.add_interaction(
            person_id=person_id,
            person_name=person_name,
            topic_name=topic_name,
            interaction_type=interaction_type,
            department=department,
            topic_description=topic_description,
        )
        return AddInteractionResponse(event_id=result["event_id"], status=result["status"])

    @tool_error_handler
    async def get_knowledge_map(self, person_id: str) -> KnowledgeMapResponse:
        """Retrieve the knowledge map of a person.

        Args:
            person_id (str): The person's ID (e.g. Slack user ID).
        Returns:
            KnowledgeMapResponse containing the person's known topics and related documents.
        """
        data = await self.__service.get_knowledge_map(person_id)
        return KnowledgeMapResponse(
            person=PersonInfo(**data["person"]),
            topics=[TopicInfo(**t) for t in data.get("topics", [])],
            documents=[DocumentInfo(**d) for d in data.get("documents", [])],
        )
