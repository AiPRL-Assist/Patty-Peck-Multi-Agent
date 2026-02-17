"""
RAG Knowledge Base Tools
========================

Query company policies, FAQs, and documents via AiPRL RAG service.
"""

import os
import httpx
from typing import Dict, Any, Optional

# Configuration
RAG_AUTH_URL = os.getenv('RAG_AUTH_URL', 'https://aiprlauth-production.up.railway.app/auth/signin')
RAG_API_URL = os.getenv('RAG_API_URL', 'https://aiprlrag-production.up.railway.app/prompt')
RAG_AUTH_EMAIL = os.getenv('RAG_AUTH_EMAIL', 'admin@woodstock.com')
RAG_AUTH_PASSWORD = os.getenv('RAG_AUTH_PASSWORD', 'Admin123')
RAG_TIMEOUT = float(os.getenv('RAG_HTTP_TIMEOUT_SECONDS', '30'))

# Module-level cache for RAG auth token
_rag_token_cache: Optional[str] = None


async def get_rag_auth_token_tool(
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Get authentication token for RAG knowledge base service.
    
    This tool caches the token to avoid repeated authentication calls.
    The token is required for all RAG knowledge base queries.
    
    Args:
        force_refresh: If True, force token refresh even if cached
    
    Returns:
        Dictionary with status and token.
        On success: {'status': 'success', 'token': '...', 'cached': True/False}
        On error: {'status': 'error', 'message': '...'}
    """
    global _rag_token_cache
    
    # Return cached token if available and not forcing refresh
    if _rag_token_cache and not force_refresh:
        return {
            "status": "success",
            "token": _rag_token_cache,
            "cached": True
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RAG_AUTH_URL,
                headers={'Content-Type': 'application/json'},
                json={
                    "email": RAG_AUTH_EMAIL,
                    "password": RAG_AUTH_PASSWORD
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"RAG auth failed: {response.status_code}"
                }
            
            data = response.json()
            token = data.get("token") or data.get("access_token")
            
            if not token:
                return {
                    "status": "error",
                    "message": "No token in RAG auth response"
                }
            
            # Cache the token
            _rag_token_cache = token
            
            return {
                "status": "success",
                "token": token,
                "cached": False
            }
            
    except httpx.TimeoutException:
        return {
            "status": "error",
            "message": "RAG auth service timeout"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


async def query_rag_knowledge_tool(
    prompt: str
) -> Dict[str, Any]:
    """
    Query the RAG knowledge base for store policies, FAQs, and general information.
    
    Use this tool when customers ask about:
    - Return and exchange policies (5 days, exchange/store credit only)
    - Delivery services and costs (Premium Delivery $169.99, pickup policy)
    - Payment methods and financing (Wells Fargo, Kornerstone, Acima Credit)
    - Design Center services (custom furniture, in-home design, Room Planner)
    - Store hours, locations, and contact information
    - Order cancellation policies (50% non-refundable deposit for custom)
    - Warranty information and product care
    
    This searches through all uploaded company documents and returns
    AI-generated responses based on actual Woodstock Outlet policies.
    
    Args:
        prompt: Natural language question about policies, store info, or FAQs
    
    Returns:
        Dictionary with status and response.
        On success: {'status': 'success', 'response': '...', 'query': '...'}
        On error: {'status': 'error', 'message': '...', 'query': '...'}
    """
    try:
        # Get token (handles caching automatically)
        token_result = await get_rag_auth_token_tool()
        
        if token_result.get("status") != "success":
            return {
                "status": "error",
                "message": f"Failed to authenticate with RAG service: {token_result.get('message', 'Unknown error')}",
                "query": prompt
            }
        
        token = token_result["token"]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                RAG_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                json={"prompt": prompt},
                timeout=RAG_TIMEOUT
            )
            
            # Handle token expiration - auto-refresh and retry once
            if response.status_code == 401:
                token_result = await get_rag_auth_token_tool(force_refresh=True)
                if token_result.get("status") == "success":
                    token = token_result["token"]
                    response = await client.post(
                        RAG_API_URL,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {token}"
                        },
                        json={"prompt": prompt},
                        timeout=RAG_TIMEOUT
                    )
                else:
                    return {
                        "status": "error",
                        "message": "RAG authentication failed after token refresh",
                        "query": prompt
                    }
            
            # Process response
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "response": data.get("response", ""),
                    "query": prompt
                }
            elif response.status_code == 404:
                return {
                    "status": "error",
                    "message": "No documents found in knowledge base. Please contact support.",
                    "query": prompt
                }
            else:
                return {
                    "status": "error",
                    "message": f"RAG query failed: {response.status_code}",
                    "query": prompt
                }
                
    except httpx.TimeoutException:
        return {
            "status": "error",
            "message": "Knowledge base query timed out. Please try again.",
            "query": prompt
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "query": prompt
        }

