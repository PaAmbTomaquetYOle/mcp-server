from abc import ABC, abstractmethod


class IEventConsumerPort(ABC):
    """
    Interface for the Event Consumer Port (async message broker reads).

    Lifecycle-only: a consumer subscribes to whatever topics it needs at
    construction time and reacts to messages by calling into the application
    layer directly (e.g. triggering a cache refresh) — there is no generic
    "handle this message" method here because each consumer's reaction is
    specific to what it's driving.
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Start consuming messages in the background.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Gracefully stop the background consumer task and close the connection.
        """
