"""
Loft Customer Service Tools
===========================

Customer lookup, order history, and support escalation via Loft API.
"""

import os
import httpx
from typing import Dict, Any

# Configuration
LOFT_TIMEOUT = float(os.getenv('LOFT_HTTP_TIMEOUT_SECONDS', '10'))


def _get_loft_base_url() -> str:
    """Return sanitized Loft API base URL."""
    base_url = os.getenv(
        'WOODSTOCK_API_BASE',
        'https://api.woodstockoutlet.com/public/index.php/april'
    )
    return base_url.strip().rstrip('/') or 'https://api.woodstockoutlet.com/public/index.php/april'


async def get_customer_by_phone_tool(phone: str) -> Dict[str, Any]:
    """
    Look up customer information using their phone number.
    
    Use this tool when a user provides a phone number to identify themselves
    or when you need to retrieve customer profile information. This is the
    primary customer lookup method.
    
    Args:
        phone: Customer's phone number in any format (e.g., "770-653-7383", "7706537383")
    
    Returns:
        Customer data on success, error message on failure.
    """
    try:
        api_base = _get_loft_base_url()
        
        async with httpx.AsyncClient() as client:
            url = f'{api_base}/GetCustomerByPhone'
            params = {'phone': phone.strip()}
            
            response = await client.get(url, params=params, timeout=LOFT_TIMEOUT)
            response.raise_for_status()
            
            return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_customer_by_email_tool(email: str) -> Dict[str, Any]:
    """
    Get customer information by email address.
    
    Args:
        email: Customer's email address
    
    Returns:
        Customer data on success, error message on failure.
    """
    try:
        api_base = _get_loft_base_url()
        
        async with httpx.AsyncClient() as client:
            url = f'{api_base}/GetCustomerByEmail'
            params = {'email': email.strip()}
            
            response = await client.get(url, params=params, timeout=LOFT_TIMEOUT)
            response.raise_for_status()
            
            return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_orders_by_customer_tool(customer_id: str) -> Dict[str, Any]:
    """
    Get orders for a customer by customer ID.
    
    First use get_customer_by_phone_tool or get_customer_by_email_tool
    to get the customer_id, then use this to get their order history.
    
    Args:
        customer_id: Customer ID from customer lookup
    
    Returns:
        List of customer orders on success.
    """
    try:
        api_base = _get_loft_base_url()
        
        async with httpx.AsyncClient() as client:
            url = f'{api_base}/GetOrdersByCustomer'
            params = {'custid': customer_id}
            
            response = await client.get(url, params=params, timeout=LOFT_TIMEOUT)
            response.raise_for_status()
            
            return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_order_details_tool(order_id: str) -> Dict[str, Any]:
    """
    Get detailed order information by order ID.
    
    Args:
        order_id: Order ID to look up
    
    Returns:
        Detailed order information including items, status, delivery info.
    """
    try:
        api_base = _get_loft_base_url()
        
        async with httpx.AsyncClient() as client:
            url = f'{api_base}/GetDetailsByOrder'
            params = {'orderid': order_id}
            
            response = await client.get(url, params=params, timeout=LOFT_TIMEOUT)
            response.raise_for_status()
            
            return {"status": "success", "data": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def escalate_to_support_tool(
    ticket_id: str,
    priority: str,
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    customer_identifier: str,
    issue_description: str
) -> Dict[str, Any]:
    """
    Escalate issue to human support via webhook.
    
    Use this when the AI cannot resolve an issue and human intervention is needed.
    
    Args:
        ticket_id: Unique ticket identifier
        priority: Priority level ("low", "medium", "high", "urgent")
        customer_name: Customer's full name
        customer_phone: Customer's phone number
        customer_email: Customer's email address
        customer_identifier: Customer ID from Loft
        issue_description: Detailed description of the issue
    
    Returns:
        Confirmation of ticket creation.
    """
    try:
        webhook_url = os.getenv(
            'SUPPORT_WEBHOOK_URL',
            'https://drivedevelopment.app.n8n.cloud/webhook/3b5f2c20-af67-427e-896e-bf79fe2426c5'
        )
        
        payload = {
            "ticket_id": ticket_id,
            "priority": priority,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "customer_identifier": customer_identifier,
            "issue_description": issue_description,
            "source": "ai_chatbot",
            "timestamp": str(os.getenv('TIMESTAMP', '')),
            "status": "open"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=LOFT_TIMEOUT
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Support ticket created successfully",
                    "data": response.json()
                }
            else:
                return {"status": "error", "message": f"Webhook failed: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

