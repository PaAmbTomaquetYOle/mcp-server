import os
import tempfile

import pytest

from mcp_server.infrastructure.adapters.sqlite_token_storage import SqliteTokenStorage


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def storage(temp_db_path):
    return SqliteTokenStorage(db_path=temp_db_path)


@pytest.mark.integration
class TestSqliteTokenStorage:
    @pytest.mark.anyio
    async def test_save_and_get_tokens(self, storage):
        await storage.save_tokens(
            user_id="user1@example.com",
            access_token="acc123",
            refresh_token="ref123",
            expires_at=1234567890
        )

        tokens = await storage.get_tokens("user1@example.com")
        
        assert tokens is not None
        assert tokens["access_token"] == "acc123"
        assert tokens["refresh_token"] == "ref123"
        assert tokens["expires_at"] == 1234567890

    @pytest.mark.anyio
    async def test_get_nonexistent_user_returns_none(self, storage):
        tokens = await storage.get_tokens("unknown@example.com")
        assert tokens is None

    @pytest.mark.anyio
    async def test_save_overwrites_existing_tokens(self, storage):
        await storage.save_tokens(
            user_id="user1@example.com",
            access_token="acc1",
            refresh_token="ref1",
            expires_at=100
        )
        
        await storage.save_tokens(
            user_id="user1@example.com",
            access_token="acc2",
            refresh_token="ref2",
            expires_at=200
        )

        tokens = await storage.get_tokens("user1@example.com")
        
        assert tokens is not None
        assert tokens["access_token"] == "acc2"
        assert tokens["refresh_token"] == "ref2"
        assert tokens["expires_at"] == 200

    @pytest.mark.anyio
    async def test_delete_tokens(self, storage):
        await storage.save_tokens(
            user_id="user2@example.com",
            access_token="acc1",
            refresh_token="ref1",
            expires_at=100
        )
        
        await storage.delete_tokens("user2@example.com")
        
        tokens = await storage.get_tokens("user2@example.com")
        assert tokens is None
