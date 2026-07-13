import json

from aiokafka import AIOKafkaProducer

from mcp_server.application.ports import IEventPublisherPort
from mcp_server.domain import EventPublishException


class KafkaEventPublisherAdapter(IEventPublisherPort):
    """Publishes domain events to Kafka topics, connecting lazily on first use.

    AIOKafkaProducer requires a running event loop to be constructed, so the
    producer itself is created on first publish rather than in __init__.

    Unlike backend's/slack-agent's fire-and-forget forwarders, ``publish`` here
    backs a synchronous MCP tool call (``add_interaction``) — the caller is
    waiting for a real answer, so failures are raised as EventPublishException
    (mapped to a friendly message by infrastructure/controllers/error_handler.py)
    rather than swallowed, to avoid silently reporting success on a message
    that never reached Kafka.
    """

    __bootstrap_servers: str
    __client_id: str | None
    __connection_kwargs: dict
    __producer: AIOKafkaProducer | None

    def __init__(
        self,
        bootstrap_servers: str,
        *,
        client_id: str | None = None,
        connection_kwargs: dict | None = None,
    ) -> None:
        self.__bootstrap_servers = bootstrap_servers
        self.__client_id = client_id
        self.__connection_kwargs = connection_kwargs or {}
        self.__producer = None

    async def _ensure_started(self) -> AIOKafkaProducer:
        if self.__producer is None:
            producer = AIOKafkaProducer(
                bootstrap_servers=self.__bootstrap_servers,
                client_id=self.__client_id,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
                **self.__connection_kwargs,
            )
            await producer.start()
            self.__producer = producer
        return self.__producer

    async def publish(self, topic: str, event: dict) -> None:
        try:
            producer = await self._ensure_started()
            await producer.send_and_wait(topic, event)
        except Exception as exc:
            raise EventPublishException(str(exc)) from exc

    async def close(self) -> None:
        if self.__producer is not None:
            await self.__producer.stop()
            self.__producer = None
