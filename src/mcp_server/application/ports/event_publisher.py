from abc import ABC, abstractmethod


class IEventPublisherPort(ABC):
    """
    Interface for the Event Publisher Port (async message broker writes).
    """

    @abstractmethod
    async def publish(self, topic: str, event: dict) -> None:
        """
        Publish an event to the given topic.
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Gracefully shut down the underlying producer.
        """
