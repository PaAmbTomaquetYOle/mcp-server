import aiosqlite
from pathlib import Path

from mcp_server.application.ports.token_storage import ITokenStoragePort


class SqliteTokenStorage(ITokenStoragePort):
    """SQLite-backed token storage, one row per user."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._initialized = False

    async def _ensure_db(self) -> None:
        if self._initialized:
            return
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS user_tokens (
                    user_id TEXT PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                )
                """
            )
            await db.commit()
        self._initialized = True

    async def get_tokens(self, user_id: str) -> dict | None:
        await self._ensure_db()
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT access_token, refresh_token, expires_at FROM user_tokens WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            return {
                "access_token": row["access_token"],
                "refresh_token": row["refresh_token"],
                "expires_at": row["expires_at"],
            }

    async def save_tokens(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expires_at: int,
    ) -> None:
        await self._ensure_db()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO user_tokens (user_id, access_token, refresh_token, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    expires_at = excluded.expires_at
                """,
                (user_id, access_token, refresh_token, expires_at),
            )
            await db.commit()

    async def delete_tokens(self, user_id: str) -> None:
        await self._ensure_db()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM user_tokens WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()
