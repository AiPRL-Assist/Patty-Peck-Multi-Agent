"""
Custom Async Session Service - Bypasses ADK's Blocking Session Management
==========================================================================
Implements fast, non-blocking session persistence using background tasks.
Responses stream immediately while database writes happen asynchronously.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import os

logger = logging.getLogger(__name__)


class CustomAsyncSessionService:
    """
    Fast session service with async writes.

    - get_session: Fast read (cached in memory when possible)
    - save_session: Fire-and-forget async write
    - Zero blocking latency on chat responses
    """

    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=False,  # No ping for speed
            pool_recycle=-1,      # No recycle for dev
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self._write_tasks = []
        self._memory_cache = {}  # Quick in-memory cache
        logger.info("🚀 CustomAsyncSessionService initialized")

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session from cache or database.
        Fast read - uses memory cache when available.
        """
        # Check memory cache first
        if session_id in self._memory_cache:
            logger.debug(f"💨 Cache hit: {session_id[:12]}")
            return self._memory_cache[session_id]

        # Otherwise fetch from database
        try:
            async with self.async_session() as session:
                # Use ADK's existing sessions table
                result = await session.execute(
                    text("""
                        SELECT events, state FROM sessions
                        WHERE id = :session_id
                        LIMIT 1
                    """),
                    {"session_id": session_id}
                )
                row = result.first()

                if row:
                    data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    self._memory_cache[session_id] = data
                    logger.debug(f"📀 DB hit: {session_id[:12]}")
                    return data

                return None
        except Exception as e:
            logger.error(f"Session read error: {e}")
            return None

    def save_session_async(
        self,
        session_id: str,
        user_id: str,
        app_name: str,
        events: List[Any],
        state: Dict[str, Any]
    ):
        """
        Save session asynchronously (fire-and-forget).

        Returns immediately without waiting for database write.
        This is the key to zero-latency responses!
        """
        # Update memory cache immediately
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "events": events,
            "state": state,
            "updated_at": datetime.utcnow().isoformat()
        }
        self._memory_cache[session_id] = session_data

        # Create background task for database write
        task = asyncio.create_task(
            self._async_write_session(session_data)
        )
        self._write_tasks.append(task)

        # Clean up completed tasks
        self._write_tasks = [t for t in self._write_tasks if not t.done()]

        logger.debug(f"✅ Session save queued (non-blocking): {session_id[:12]}")
        # Returns immediately!

    async def _async_write_session(self, session_data: Dict[str, Any]):
        """
        Background task that actually writes to PostgreSQL.
        This happens AFTER the response has already streamed to the user.
        """
        try:
            async with self.async_session() as session:
                # Use ADK's existing sessions table structure
                await session.execute(
                    text("""
                        INSERT INTO sessions
                            (id, app_name, user_id, events, state, last_update_time)
                        VALUES
                            (:id, :app_name, :user_id, :events::jsonb, :state::jsonb, NOW())
                        ON CONFLICT (id)
                        DO UPDATE SET
                            events = EXCLUDED.events,
                            state = EXCLUDED.state,
                            last_update_time = NOW()
                    """),
                    {
                        "id": session_data["session_id"],
                        "app_name": session_data["app_name"],
                        "user_id": session_data["user_id"],
                        "events": json.dumps(session_data["events"]),
                        "state": json.dumps(session_data["state"])
                    }
                )
                await session.commit()
                logger.debug(f"💾 DB write completed: {session_data['session_id'][:12]}")
        except Exception as e:
            logger.error(f"❌ Async session write failed: {e}")

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        app_name: str,
        state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create new session (synchronous for immediate return of session_id).
        """
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "app_name": app_name,
            "events": [],
            "state": state or {},
            "updated_at": datetime.utcnow().isoformat()
        }

        # Cache immediately
        self._memory_cache[session_id] = session_data

        # Write to DB in background
        self.save_session_async(session_id, user_id, app_name, [], state or {})

        return session_data


# Global instance
_custom_session_service: Optional[CustomAsyncSessionService] = None


def get_custom_session_service() -> CustomAsyncSessionService:
    """Get or create the global custom session service"""
    global _custom_session_service

    if _custom_session_service is None:
        database_url = os.environ.get("DATABASE_URL", "")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable required")

        # Ensure it uses asyncpg and correct SSL parameter
        if "postgresql://" in database_url and "postgresql+asyncpg://" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        # asyncpg uses ssl=require, not sslmode=require
        database_url = database_url.replace("sslmode=require", "ssl=require")

        _custom_session_service = CustomAsyncSessionService(database_url)

    return _custom_session_service
