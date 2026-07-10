from abc import ABC, abstractmethod


class IKnowledgeGraphPort(ABC):
    """
    Interface for the Knowledge Graph Port (REST reads).
    """

    @abstractmethod
    async def search_experts(self, topic: str, limit: int = 10) -> list[dict]:
        """
        Search for experts on a given topic in the knowledge graph.

        Returns the raw list of ExpertResponse dicts: [{"person": {...}, "topic": str, "score": float}].
        """

    @abstractmethod
    async def get_person_knowledge(self, person_id: str) -> dict:
        """
        Retrieve the knowledge profile of a person from the knowledge graph.

        Returns the raw PersonKnowledgeProfileResponse dict:
        {"person": {...}, "topics": [...], "documents": [...]}.

        Raises PersonNotFoundException if the person does not exist in the graph.
        """
