"""
Delivery Options Tool
=====================

Fetches delivery options and pricing by ZIP code from the Woodstock API.
"""

from typing import Dict, Any, Optional
import httpx

DELIVERY_API_BASE = "https://api.woodstockoutlet.com/public/index.php/aiprl/GetDeliveryOptionsByZip"


async def get_delivery_options_by_zip_tool(zipcode: str) -> Dict[str, Any]:
    """
    Get delivery options and pricing for a given ZIP code.
    
    Use this tool when customers ask about:
    - Delivery cost to their area
    - "How much is delivery to [ZIP]?"
    - "Do you deliver to [ZIP code]?"
    - Delivery options (curbside, white glove, same day, etc.)
    - Delivery schedule or availability
    
    Args:
        zipcode: 5-digit US ZIP code (e.g., "30102", "30157")
    
    Returns:
        Delivery options with zone, description, and charge for each option.
        Options may include: Curbside, Haul Away, Express, Mattress/Recliner Only,
        Premium, Same Day, Service, etc.
    """
    zipcode = str(zipcode).strip()
    if not zipcode or len(zipcode) < 5:
        return {
            "status": "error",
            "message": "Please provide a valid 5-digit ZIP code.",
            "zipcode": zipcode,
        }
    
    # Use first 5 digits if they passed a ZIP+4
    zipcode = zipcode[:5]
    
    url = f"{DELIVERY_API_BASE}?zipcode={zipcode}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "message": f"API returned error: {e.response.status_code}",
            "zipcode": zipcode,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "zipcode": zipcode,
        }
    
    entry = data.get("entry", [])
    total_results = data.get("totalResults", len(entry))
    
    if not entry:
        return {
            "status": "success",
            "zipcode": zipcode,
            "total_results": 0,
            "delivery_options": [],
            "message": f"No delivery options found for ZIP {zipcode}. We may not deliver to this area yet - suggest they call the store for availability.",
        }
    
    # Normalize options for easier consumption
    options = []
    for item in entry:
        zone = item.get("zoneid", "Unknown")
        desc = item.get("description", "")
        charge = item.get("charge")
        charge_str = f"${charge}" if charge else "Contact store for pricing"
        options.append({
            "option": zone,
            "description": desc,
            "charge": charge,
            "charge_display": charge_str,
        })
    
    return {
        "status": "success",
        "zipcode": zipcode,
        "total_results": total_results,
        "delivery_options": options,
        "formatting_hint": "List each option with its description and price. Use charge_display for customer-facing text.",
    }
