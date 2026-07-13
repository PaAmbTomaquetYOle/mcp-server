import asyncio
import contextlib
import logging

from aiokafka import AIOKafkaConsumer

from mcp_server.application.ports import IEventConsumerPort
from mcp_server.application.service_interfaces import ISearchConnectorService

logger = logging.getLogger(__name__)


class KafkaSopCacheConsumerAdapter(IEventConsumerPort):
    """Reactively refreshes the SOP cache when backend publishes a SOP change.

    Subscribes only to the ``sop.created``/``sop.updated``/``sop.deleted``
    topics — any message on any of them means the SOP set changed, so the
    reaction is always the same full ``refresh_cache()`` re-fetch regardless
    of which event type or payload arrived. This makes the handler trivially
    idempotent under at-least-once redelivery and immune to malformed
    envelopes: the payload is never parsed, only the fact that a message
    arrived matters.

    This is a *reactive* addition on top of the existing TTL poll
    (``main.py``'s periodic refresh loop), not a replacement for it — if the
    broker is unreachable or misconfigured, the TTL poll keeps the cache from
    going permanently stale.
    """

    __consumer: AIOKafkaConsumer
    __search_connector: ISearchConnectorService
    __task: asyncio.Task | None

    def __init__(self, consumer: AIOKafkaConsumer, search_connector: ISearchConnectorService) -> None:
        self.__consumer = consumer
        self.__search_connector = search_connector
        self.__task = None

    async def start(self) -> None:
        await self.__consumer.start()
        self.__task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self.__task is not None:
            self.__task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.__task
            self.__task = None
        await self.__consumer.stop()

    async def _run(self) -> None:
        async for _message in self.__consumer:
            try:
                await self.__search_connector.refresh_cache()
            except Exception:
                logger.exception("Reactive SOP cache refresh failed; TTL poll will retry")
