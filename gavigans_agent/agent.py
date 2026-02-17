"""
Gavigans Multi-Agent Platform - Root Agent
==========================================

Clean agent using Google ADK with Inbox integration callbacks.
This agent routes to sub-agents configured in the database.

Key Features:
- before_agent_callback: AI pause check (human takeover)
- after_agent_callback: Webhook to Inbox for real-time updates
- SSE broadcast for sidebar updates
"""

from dotenv import load_dotenv
import asyncio
import os
import httpx
from datetime import datetime

load_dotenv()

# Inbox webhook URL for real-time notifications
INBOX_WEBHOOK_URL = os.environ.get("INBOX_WEBHOOK_URL", "https://chatrace-inbox-production-561c.up.railway.app/webhook/message")

# Import broadcast_global for real-time sidebar updates
BROADCAST_AVAILABLE = False
broadcast_global = None

def _init_broadcast():
    global BROADCAST_AVAILABLE, broadcast_global
    try:
        import sys
        from pathlib import Path
        root_dir = Path(__file__).parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        
        from inbox_router import broadcast_global as bg
        broadcast_global = bg
        BROADCAST_AVAILABLE = True
        print("✅ broadcast_global imported successfully")
    except Exception as e:
        print(f"⚠️ broadcast_global not available: {e}")

_init_broadcast()

# Google ADK imports
try:
    from google.adk.agents import Agent
    from google.adk.agents.callback_context import CallbackContext
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️ Google ADK not installed. Install with: pip install google-adk")
    ADK_AVAILABLE = False
    Agent = None
    CallbackContext = None
    types = None


# ============================================================================
# AGENT INSTRUCTIONS
# ============================================================================

AGENT_INSTRUCTION = """
You are a helpful AI assistant for Gavigans multi-agent platform.

Your job is to understand the user's question and provide helpful responses.
You can assist with general inquiries and help route requests to the appropriate services.

## GUIDELINES
- Be friendly, helpful, and accurate
- If you're unsure about something, say so
- For complex issues, suggest escalating to human support

## MEMORY
You have full memory of the current conversation. Reference earlier parts naturally.
"""


# ============================================================================
# BEFORE AGENT CALLBACK - AI Pause Check
# ============================================================================

async def before_agent_callback(callback_context: CallbackContext) -> types.Content | None:
    """
    🔐 BEFORE AGENT CALLBACK
    
    1. Send webhook for USER message (so inbox sees it in realtime)
    2. Check if AI is paused (human agent takeover)
    """
    if not ADK_AVAILABLE:
        return None
    
    state = callback_context.state
    session = callback_context.session
    
    # ============================================
    # STEP 0: SEND WEBHOOK FOR USER MESSAGE
    # ============================================
    try:
        events = getattr(session, 'events', [])
        session_id = getattr(session, 'id', None)
        
        if events and session_id:
            for event in reversed(events):
                if event.author == "user" and event.content and event.content.parts:
                    text_parts = [p.text for p in event.content.parts if hasattr(p, 'text') and p.text]
                    if text_parts:
                        user_message = " ".join(text_parts).strip()
                        if user_message:
                            is_new = len(events) <= 1
                            asyncio.create_task(_send_webhook_to_inbox(
                                conversation_id=session_id,
                                message_id=f'user_{datetime.now().timestamp()}',
                                message=user_message[:500],
                                sender_name="user",
                                sender_type="user",
                                is_new_conversation=is_new,
                                user_id=session.user_id if hasattr(session, 'user_id') else "default"
                            ))
                            print(f"📤 User message webhook queued: {session_id[:8]}...")
                            break
    except Exception as e:
        print(f"⚠️ User webhook error (non-fatal): {e}")
    
    # ============================================
    # STEP 1: CHECK IF AI IS PAUSED
    # ============================================
    ai_paused = state.get('ai_paused', False)
    
    if ai_paused:
        print("🚫 AI PAUSED - Human agent handling this conversation")
        return types.Content(
            role="model",
            parts=[types.Part(text="__AI_PAUSED__")]
        )
    
    return None


# ============================================================================
# AFTER AGENT CALLBACK - Send Webhook to Inbox
# ============================================================================

async def after_agent_callback(callback_context: CallbackContext) -> types.Content | None:
    """
    📤 AFTER AGENT CALLBACK
    
    1. Persist last_message_preview and message_count in session.state
    2. Send webhook notification to Inbox for real-time SSE broadcast
    """
    if not ADK_AVAILABLE:
        return None
    
    try:
        session = callback_context.session
        state = callback_context.state
        
        if not session:
            return None
        
        session_id = getattr(session, 'id', None)
        if not session_id:
            return None
        
        events = getattr(session, 'events', [])
        if not events:
            return None
        
        is_new_conversation = len(events) <= 2
        
        # Persist state for list_sessions sidebar
        state["message_count"] = len(events)
        
        # Find last user message for preview
        for event in reversed(events):
            if event.author == "user" and event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if hasattr(p, 'text') and p.text]
                if text_parts:
                    user_message = " ".join(text_parts).strip()
                    if user_message and user_message != '__AI_PAUSED__':
                        state["last_message_preview"] = user_message[:100]
                        break
        
        # Send webhook for bot response
        last_event = events[-1]
        content = getattr(last_event, 'content', None)
        if not content:
            return None
        
        parts = getattr(content, 'parts', [])
        text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
        message_text = ' '.join(text_parts).strip()
        
        if message_text == '__AI_PAUSED__':
            return None
        
        if not message_text:
            return None
        
        asyncio.create_task(_send_webhook_to_inbox(
            conversation_id=session_id,
            message_id=getattr(last_event, 'id', f'evt_{datetime.now().timestamp()}'),
            message=message_text[:500],
            sender_name="gavigans_agent",
            sender_type="bot",
            is_new_conversation=is_new_conversation
        ))
        
        print(f"📤 Webhook queued for Inbox: {session_id[:8]}...")
        
    except Exception as e:
        print(f"⚠️ after_agent_callback error (non-fatal): {e}")
    
    return None


async def _send_webhook_to_inbox(conversation_id: str, message_id: str, message: str,
                                  sender_name: str, sender_type: str, is_new_conversation: bool = False,
                                  user_id: str = "default"):
    """Send webhook notification TO Inbox when new message arrives."""
    webhook_url = INBOX_WEBHOOK_URL
    
    payload = {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "message": message,
        "content": message,
        "author": sender_name,
        "sender": {
            "id": sender_name,
            "name": "Customer" if sender_type == "user" else "Gavigans Bot",
            "type": sender_type
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "is_new_conversation": is_new_conversation,
        "source": "gavigans_adk",
        "user_id": user_id
    }
    
    # Broadcast to global SSE listeners (for inbox sidebar)
    if BROADCAST_AVAILABLE and broadcast_global:
        try:
            event_type = "new_conversation" if is_new_conversation else "conversation_update"
            await broadcast_global(event_type, {
                "conversation_id": conversation_id,
                "user_id": "default",
                "last_message": message[:100],
                "author": sender_name,
                "is_new": is_new_conversation,
                "platform": "webchat",
                "source": "webchat"
            })
        except Exception as e:
            print(f"⚠️ broadcast_global error (non-fatal): {e}")
    
    # Also send webhook to inbox backend
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(webhook_url, json=payload, timeout=5.0)
            status = "✅" if resp.status_code == 200 else "⚠️"
            print(f"{status} Webhook to Inbox: {resp.status_code}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")


# ============================================================================
# AGENT DEFINITION
# ============================================================================

if ADK_AVAILABLE:
    root_agent = Agent(
        name="gavigans_agent",
        model="gemini-2.0-flash",
        description="Gavigans multi-agent platform AI assistant",
        instruction=AGENT_INSTRUCTION,
        tools=[],  # No default tools - agents are loaded from database
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback
    )
else:
    root_agent = None


def create_gavigans_agent(model: str = "gemini-2.0-flash", use_callbacks: bool = True):
    """Create a new instance of the Gavigans agent."""
    if not ADK_AVAILABLE:
        return None
    
    return Agent(
        name="gavigans_agent",
        model=model,
        description="Gavigans multi-agent platform AI assistant",
        instruction=AGENT_INSTRUCTION,
        tools=[],
        before_agent_callback=before_agent_callback if use_callbacks else None,
        after_agent_callback=after_agent_callback if use_callbacks else None
    )


if __name__ == "__main__":
    print("🚀 Gavigans Agent Platform")
    print(f"   ADK Available: {ADK_AVAILABLE}")
    if root_agent:
        print(f"   Agent Name: {root_agent.name}")
