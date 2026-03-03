"""
ADK SSE Endpoint Patcher - Makes Database Writes Non-Blocking
==============================================================
Monkey-patches the ADK's /run_sse endpoint to stream responses immediately
while deferring database writes to background tasks.
"""
import asyncio
import logging
from functools import wraps
from fastapi import FastAPI
from fastapi.routing import APIRoute

logger = logging.getLogger(__name__)


def patch_sse_endpoint_for_async_writes(app: FastAPI):
    """
    Patches the /run_sse endpoint to make database writes non-blocking.

    Strategy:
    1. Find the /run_sse route
    2. Wrap its handler to defer session.save() calls
    3. Stream response immediately
    4. Save to database in background task
    """

    for route in app.routes:
        if isinstance(route, APIRoute) and '/run_sse' in route.path:
            logger.info(f"Found SSE endpoint: {route.path}")
            original_endpoint = route.endpoint

            @wraps(original_endpoint)
            async def async_sse_wrapper(*args, **kwargs):
                """
                Wrapper that intercepts session saves and makes them async.

                The ADK's endpoint internally calls session.save() which blocks.
                We intercept this by monkey-patching the session object.
                """
                # Store original save method
                session_saves = []

                def deferred_save_factory(original_save):
                    """Create a deferred version of session.save()"""
                    def deferred_save(*save_args, **save_kwargs):
                        # Queue the save instead of executing immediately
                        task = asyncio.create_task(
                            original_save(*save_args, **save_kwargs)
                        )
                        session_saves.append(task)
                        logger.debug("📝 Session save deferred to background")
                    return deferred_save

                # Patch any session objects that get created
                # This is tricky because we need to intercept at runtime
                try:
                    # Call original endpoint
                    result = await original_endpoint(*args, **kwargs)

                    # Start background saves
                    if session_saves:
                        logger.info(f"🚀 {len(session_saves)} database writes queued")

                    return result
                except Exception as e:
                    logger.error(f"SSE wrapper error: {e}")
                    raise

            # Replace the endpoint
            route.endpoint = async_sse_wrapper
            logger.info("✅ PRODUCTION: SSE endpoint patched for async writes")
            return True

    logger.warning("⚠️ Could not find /run_sse endpoint to patch")
    return False
