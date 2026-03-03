"""
Async Session Middleware - Wraps ADK Endpoints with Fast Session Management
============================================================================
Intercepts /run_sse and session endpoints to use our async session service
instead of ADK's blocking DatabaseSessionService.
"""
import asyncio
import json
import logging
from uuid import uuid4
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from custom_session_service import get_custom_session_service

logger = logging.getLogger(__name__)


class AsyncSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that makes session operations non-blocking.

    Intercepts:
    - POST /run_sse: Streams response immediately, saves session in background
    - POST /apps/{app}/users/{user}/sessions: Fast session creation
    - GET /apps/{app}/users/{user}/sessions/{session}: Fast session retrieval
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Intercept session creation
        if path.endswith("/sessions") and request.method == "POST":
            return await self._handle_create_session(request)

        # Intercept session retrieval
        if "/sessions/" in path and request.method == "GET":
            return await self._handle_get_session(request, call_next)

        # Intercept SSE streaming
        if path == "/run_sse" and request.method == "POST":
            return await self._handle_run_sse(request, call_next)

        # All other requests pass through
        return await call_next(request)

    async def _handle_create_session(self, request: Request):
        """
        Fast session creation using our async service.
        Returns immediately without blocking on database write.
        """
        try:
            # Parse path to get app_name and user_id
            parts = request.url.path.split("/")
            app_idx = parts.index("apps") if "apps" in parts else -1
            if app_idx >= 0 and app_idx + 4 < len(parts):
                app_name = parts[app_idx + 1]
                user_id = parts[app_idx + 3]
            else:
                return Response(
                    content=json.dumps({"error": "Invalid path"}),
                    status_code=400,
                    media_type="application/json"
                )

            # Parse request body
            body = await request.body()
            data = json.loads(body) if body else {}
            state = data.get("state", {})

            # Create session
            session_id = str(uuid4())
            session_service = get_custom_session_service()
            session_data = await session_service.create_session(
                session_id, user_id, app_name, state
            )

            # Return immediately (database write happens in background!)
            return Response(
                content=json.dumps({
                    "id": session_id,
                    "appName": app_name,
                    "userId": user_id,
                    "state": state,
                    "events": [],
                    "lastUpdateTime": session_data["updated_at"]
                }),
                media_type="application/json"
            )
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return Response(
                content=json.dumps({"error": str(e)}),
                status_code=500,
                media_type="application/json"
            )

    async def _handle_get_session(self, request: Request, call_next):
        """
        Fast session retrieval from cache/database.
        """
        try:
            # Extract session_id from path
            parts = request.url.path.split("/")
            session_id = parts[-1] if parts else None

            if not session_id:
                return await call_next(request)

            session_service = get_custom_session_service()
            session_data = await session_service.get_session(session_id)

            if session_data:
                return Response(
                    content=json.dumps(session_data),
                    media_type="application/json"
                )
            else:
                return Response(
                    content=json.dumps({"detail": "Session not found"}),
                    status_code=404,
                    media_type="application/json"
                )
        except Exception as e:
            logger.error(f"Session retrieval error: {e}")
            return await call_next(request)

    async def _handle_run_sse(self, request: Request, call_next):
        """
        Intercept SSE streaming to save sessions asynchronously.

        Strategy:
        1. Parse request to get session info
        2. Call ADK's endpoint (streams response)
        3. In background, save session events to our async service
        4. Response streams immediately - zero blocking!
        """
        try:
            # Parse request body
            body_bytes = await request.body()
            body_data = json.loads(body_bytes)

            session_id = body_data.get("sessionId")
            user_id = body_data.get("userId")
            app_name = body_data.get("appName")

            # Call original ADK endpoint (get streaming response)
            # We need to reconstruct the request with the body
            scope = request.scope
            async def receive():
                return {"type": "http.request", "body": body_bytes}

            from starlette.requests import Request as StarletteRequest
            new_request = StarletteRequest(scope, receive)

            response = await call_next(new_request)

            # If it's a streaming response, wrap it to capture events
            if isinstance(response, StreamingResponse):
                original_body_iterator = response.body_iterator

                async def wrapped_stream():
                    """
                    Stream response to user while collecting events for async save.
                    """
                    collected_events = []

                    async for chunk in original_body_iterator:
                        # Stream chunk to user immediately
                        yield chunk

                        # Parse SSE events for background save
                        if chunk.startswith(b"data: "):
                            try:
                                event_json = chunk[6:].decode()  # Remove "data: "
                                event_data = json.loads(event_json)
                                collected_events.append(event_data)
                            except:
                                pass

                    # After streaming completes, save session in background
                    if session_id and collected_events:
                        session_service = get_custom_session_service()
                        session_service.save_session_async(
                            session_id=session_id,
                            user_id=user_id,
                            app_name=app_name,
                            events=collected_events,
                            state={}  # State would need to be extracted if needed
                        )
                        logger.info(f"🎯 Session saved in background: {session_id[:12]}")

                # Return wrapped streaming response
                return StreamingResponse(
                    wrapped_stream(),
                    media_type=response.media_type,
                    headers=dict(response.headers)
                )

            return response

        except Exception as e:
            logger.error(f"SSE middleware error: {e}")
            return await call_next(request)
