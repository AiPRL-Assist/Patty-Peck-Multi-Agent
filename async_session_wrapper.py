"""
Async Session Service Wrapper
===============================
Wraps the DatabaseSessionService to make writes non-blocking.
Database writes happen asynchronously without blocking the chat response.
"""
import asyncio
import logging
from typing import Any, Dict, Optional
from google.adk.sessions import DatabaseSessionService

logger = logging.getLogger(__name__)


class AsyncSessionServiceWrapper:
    """
    Wraps DatabaseSessionService to make writes async (non-blocking).

    - Reads are still synchronous (needed for session recovery)
    - Writes are fire-and-forget (async background tasks)
    - This eliminates ~800ms of blocking database latency per response
    """

    def __init__(self, session_service: DatabaseSessionService):
        self._service = session_service
        self._pending_writes = []
        logger.info("✅ AsyncSessionServiceWrapper initialized - database writes will be non-blocking")

    async def get_session(self, app_name: str, user_id: str, session_id: str):
        """Read operations remain synchronous (needed for correctness)"""
        return await self._service.get_session(app_name, user_id, session_id)

    async def create_session(self, app_name: str, user_id: str, state: Optional[Dict[str, Any]] = None):
        """Create session synchronously (needed to return session_id immediately)"""
        return await self._service.create_session(app_name, user_id, state)

    async def update_session(self, app_name: str, user_id: str, session_id: str, **kwargs):
        """
        Update session ASYNCHRONOUSLY - fire and forget.
        The chat response streams immediately without waiting for DB write.
        """
        # Create background task for the database write
        task = asyncio.create_task(
            self._async_update_session(app_name, user_id, session_id, **kwargs)
        )
        self._pending_writes.append(task)

        # Clean up completed tasks to prevent memory leak
        self._pending_writes = [t for t in self._pending_writes if not t.done()]

        # Return immediately without waiting
        logger.debug(f"🚀 Session update queued (non-blocking): {session_id[:8]}...")

    async def _async_update_session(self, app_name: str, user_id: str, session_id: str, **kwargs):
        """Background task that actually writes to database"""
        try:
            await self._service.update_session(app_name, user_id, session_id, **kwargs)
            logger.debug(f"✅ Session update completed: {session_id[:8]}...")
        except Exception as e:
            logger.error(f"❌ Async session update failed: {e}")

    async def delete_session(self, app_name: str, user_id: str, session_id: str):
        """Delete operations can be async too"""
        task = asyncio.create_task(
            self._service.delete_session(app_name, user_id, session_id)
        )
        self._pending_writes.append(task)
        logger.debug(f"🗑️ Session deletion queued: {session_id[:8]}...")

    async def list_sessions(self, app_name: str, user_id: str):
        """List operations remain synchronous"""
        return await self._service.list_sessions(app_name, user_id)

    def __getattr__(self, name):
        """Proxy all other methods to the underlying service"""
        return getattr(self._service, name)
