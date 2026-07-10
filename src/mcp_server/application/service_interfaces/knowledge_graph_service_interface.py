from abc import ABC, abstractmethod


class IKnowledgeGraphService(ABC):
    """
    Inbound service interface for Knowledge Graph use cases.
    """

    @abstractmethod
    async def query_experts(self, topic: str, limit: int = 10) -> list[dict]:
        """
        Search for experts on a given topic.
        """

    @abstractmethod
    async def add_interaction(
        self,
        person_id: str,
        person_name: str,
        topic_name: str,
        interaction_type: str,
        department: str | None = None,
        topic_description: str | None = None,
    ) -> dict:
        """
        Register a knowledge interaction between a person and a topic.

        Returns a confirmation dict: {"event_id": str, "status": str}.
        """

    @abstractmethod
    async def get_knowledge_map(self, person_id: str) -> dict:
        """
        Retrieve the full knowledge map of a person.

        Raises PersonNotFoundException if the person does not exist in the graph.
        """
