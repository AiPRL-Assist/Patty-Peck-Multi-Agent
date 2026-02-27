"""
Fast Non-Blocking Session Service for Production
=================================================
Custom session service that makes database writes async and non-blocking.
Chat responses stream immediately without waiting for database writes.
"""
import asyncio
import logging
from typing import Any, Dict, Optional, List
from google.adk.sessions import DatabaseSessionService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class FastSessionService(DatabaseSessionService):
    """
    Production-ready session service with non-blocking writes.

    - Session reads are synchronous (needed for recovery)
    - Session writes are fire-and-forget (async background tasks)
    - Zero blocking database latency for chat responses
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._write_queue = []
        logger.info("🚀 FastSessionService initialized - async writes enabled")

    async def update_session_events(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        events: List[Any]
    ) -> None:
        """
        Override: Make event updates non-blocking.

        The parent method blocks on database writes. We fire a background
        task instead so the response streams immediately.
        """
        # Create background task for database write
        task = asyncio.create_task(
            self._async_update_events(app_name, user_id, session_id, events)
        )

        # Track task to prevent memory leaks
        self._write_queue.append(task)
        self._write_queue = [t for t in self._write_queue if not t.done()]

        logger.debug(f"✅ Session update queued (non-blocking): {session_id[:12]}...")
        # Return immediately without awaiting

    async def _async_update_events(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        events: List[Any]
    ) -> None:
        """Background task that actually writes to database"""
        try:
            await super().update_session_events(app_name, user_id, session_id, events)
            logger.debug(f"✅ DB write completed: {session_id[:12]}...")
        except Exception as e:
            logger.error(f"❌ Async session write failed: {e}")

    async def update_session_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Override: Make state updates non-blocking"""
        task = asyncio.create_task(
            self._async_update_state(app_name, user_id, session_id, state)
        )
        self._write_queue.append(task)
        self._write_queue = [t for t in self._write_queue if not t.done()]
        logger.debug(f"✅ State update queued: {session_id[:12]}...")

    async def _async_update_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Background task for state writes"""
        try:
            await super().update_session_state(app_name, user_id, session_id, state)
            logger.debug(f"✅ State write completed: {session_id[:12]}...")
        except Exception as e:
            logger.error(f"❌ Async state write failed: {e}")
