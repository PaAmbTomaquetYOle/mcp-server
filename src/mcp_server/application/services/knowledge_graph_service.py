import uuid
from datetime import UTC, datetime

from mcp_server.application.ports import IEventPublisherPort, IKnowledgeGraphPort
from mcp_server.application.service_interfaces import IKnowledgeGraphService

_INTERACTION_TOPIC = "slack-agent.knowledge_graph.interaction_registered"
_INTERACTION_EVENT_TYPE = "knowledge_graph.interaction_registered"


class KnowledgeGraphService(IKnowledgeGraphService):
    """Orchestrates Knowledge Graph reads (REST) and writes (Kafka)."""

    __kg_port: IKnowledgeGraphPort
    __event_publisher: IEventPublisherPort

    def __init__(self, kg_port: IKnowledgeGraphPort, event_publisher: IEventPublisherPort) -> None:
        self.__kg_port = kg_port
        self.__event_publisher = event_publisher

    async def query_experts(self, topic: str, limit: int = 10) -> list[dict]:
        return await self.__kg_port.search_experts(topic, limit=limit)

    async def add_interaction(
        self,
        person_id: str,
        person_name: str,
        topic_name: str,
        interaction_type: str,
        department: str | None = None,
        topic_description: str | None = None,
    ) -> dict:
        event_id = str(uuid.uuid4())
        event = {
            "event_id": event_id,
            "event_type": _INTERACTION_EVENT_TYPE,
            "occurred_at": datetime.now(UTC).isoformat(),
            "payload": {
                "person_id": person_id,
                "person_name": person_name,
                "topic_name": topic_name,
                "interaction_type": interaction_type,
                "department": department,
                "topic_description": topic_description,
            },
        }
        await self.__event_publisher.publish(_INTERACTION_TOPIC, event)
        return {"event_id": event_id, "status": "published"}

    async def get_knowledge_map(self, person_id: str) -> dict:
        return await self.__kg_port.get_person_knowledge(person_id)
