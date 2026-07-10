from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.domain import EventPublishException
from mcp_server.infrastructure.adapters.kafka_event_publisher import KafkaEventPublisherAdapter


@pytest.fixture
def mock_producer():
    producer = AsyncMock()
    producer.start = AsyncMock()
    producer.stop = AsyncMock()
    producer.send_and_wait = AsyncMock()
    return producer


@pytest.fixture
def adapter():
    return KafkaEventPublisherAdapter(bootstrap_servers="localhost:9092")


class TestPublish:
    @pytest.mark.anyio
    async def test_starts_producer_on_first_publish(self, adapter, mock_producer):
        with patch(
            "mcp_server.infrastructure.adapters.kafka_event_publisher.AIOKafkaProducer",
            return_value=mock_producer,
        ):
            await adapter.publish("topic-a", {"event_id": "1"})

        mock_producer.start.assert_awaited_once()
        mock_producer.send_and_wait.assert_awaited_once_with("topic-a", {"event_id": "1"})

    @pytest.mark.anyio
    async def test_does_not_recreate_producer_on_subsequent_publish(self, adapter, mock_producer):
        with patch(
            "mcp_server.infrastructure.adapters.kafka_event_publisher.AIOKafkaProducer",
            return_value=mock_producer,
        ) as producer_cls:
            await adapter.publish("topic-a", {"event_id": "1"})
            await adapter.publish("topic-a", {"event_id": "2"})

        producer_cls.assert_called_once()
        mock_producer.start.assert_awaited_once()
        assert mock_producer.send_and_wait.await_count == 2

    @pytest.mark.anyio
    async def test_wraps_errors_in_event_publish_exception(self, adapter, mock_producer):
        mock_producer.send_and_wait.side_effect = RuntimeError("broker unreachable")

        with patch(
            "mcp_server.infrastructure.adapters.kafka_event_publisher.AIOKafkaProducer",
            return_value=mock_producer,
        ):
            with pytest.raises(EventPublishException):
                await adapter.publish("topic-a", {"event_id": "1"})


class TestClose:
    @pytest.mark.anyio
    async def test_stops_started_producer(self, adapter, mock_producer):
        with patch(
            "mcp_server.infrastructure.adapters.kafka_event_publisher.AIOKafkaProducer",
            return_value=mock_producer,
        ):
            await adapter.publish("topic-a", {"event_id": "1"})

        await adapter.close()

        mock_producer.stop.assert_awaited_once()

    @pytest.mark.anyio
    async def test_does_not_stop_unstarted_producer(self, adapter, mock_producer):
        await adapter.close()

        mock_producer.stop.assert_not_awaited()
