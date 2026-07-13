from mcp.server import FastMCP

from mcp_server.application.ports import IKnowledgeGraphPort
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import resource_error_handler
from mcp_server.infrastructure.dto import (
    DocumentInfo,
    ExpertResult,
    KnowledgeMapResponse,
    PersonInfo,
    QueryExpertsResponse,
    TopicInfo,
)


class KnowledgeGraphResourceController(BaseController):
    """Controller exposing Knowledge Graph reads as MCP resources: topic experts and person profiles.

    Reuses ``IKnowledgeGraphPort`` directly — the same port
    ``KnowledgeGraphService.query_experts``/``get_knowledge_map`` delegate to for the
    ``query_experts``/``get_knowledge_map`` tools — since these reads need no event
    publishing.
    """

    __kg_port: IKnowledgeGraphPort

    def __init__(self, server: FastMCP, kg_port: IKnowledgeGraphPort) -> None:
        super().__init__(server)
        self.__kg_port = kg_port

    def register(self) -> None:
        self._server.resource(
            "kg://offboardme/experts/{topic}",
            name="kg_experts",
            title="Topic experts",
            description="People who are experts on a given topic, ranked by expertise score.",
            mime_type="application/json",
        )(self.get_experts)

        self._server.resource(
            "kg://offboardme/persons/{person_id}/profile",
            name="kg_person_profile",
            title="Person knowledge profile",
            description="A person's knowledge map: the topics they are known for and their related documents.",
            mime_type="application/json",
        )(self.get_person_profile)

    @resource_error_handler
    async def get_experts(self, topic: str) -> str:
        """Retrieve experts for a given topic.

        Args:
            topic (str): The topic to search experts for.
        Returns:
            A JSON-encoded QueryExpertsResponse.
        """
        raw_results = await self.__kg_port.search_experts(topic)
        experts = [
            ExpertResult(person=PersonInfo(**r["person"]), topic=r["topic"], score=r["score"])
            for r in raw_results
        ]
        return QueryExpertsResponse(topic=topic, experts=experts, count=len(experts)).model_dump_json()

    @resource_error_handler
    async def get_person_profile(self, person_id: str) -> str:
        """Retrieve a person's knowledge profile.

        Args:
            person_id (str): The person's ID (e.g. Slack user ID).
        Returns:
            A JSON-encoded KnowledgeMapResponse.
        """
        data = await self.__kg_port.get_person_knowledge(person_id)
        profile = KnowledgeMapResponse(
            person=PersonInfo(**data["person"]),
            topics=[TopicInfo(**t) for t in data.get("topics", [])],
            documents=[DocumentInfo(**d) for d in data.get("documents", [])],
        )
        return profile.model_dump_json()
