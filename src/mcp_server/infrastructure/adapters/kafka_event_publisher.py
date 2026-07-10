import json

from aiokafka import AIOKafkaProducer

from mcp_server.application.ports import IEventPublisherPort
from mcp_server.domain import EventPublishException


class KafkaEventPublisherAdapter(IEventPublisherPort):
    """Publishes domain events to Kafka topics, connecting lazily on first use.

    AIOKafkaProducer requires a running event loop to be constructed, so the
    producer itself is created on first publish rather than in __init__.
    """

    __bootstrap_servers: str
    __producer: AIOKafkaProducer | None

    def __init__(self, bootstrap_servers: str) -> None:
        self.__bootstrap_servers = bootstrap_servers
        self.__producer = None

    async def _ensure_started(self) -> AIOKafkaProducer:
        if self.__producer is None:
            producer = AIOKafkaProducer(
                bootstrap_servers=self.__bootstrap_servers,
                value_serializer=lambda value: json.dumps(value).encode("utf-8"),
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
