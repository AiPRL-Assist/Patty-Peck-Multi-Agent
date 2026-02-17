"""
Store Locations Tool
====================

Provides store locations with Google Maps links.
NO hardcoded ZIP codes - Gemini knows geography and can determine proximity.
"""

from typing import Dict, Any, Optional

# ============================================================================
# STORE LOCATIONS DATA
# ============================================================================
# Google Maps URLs are FREE - no API key required!
# - maps_url: View location on map
# - directions_url: Get driving directions  
# - embed_url: For iframe embedding on webchat

STORE_LOCATIONS = [
    {
        "name": "Woodstock/Acworth (Flagship Showroom)",
        "type": "Full-Service Furniture & Mattress",
        "address": "100 Robin Road Ext, Acworth, GA 30102",
        "city": "Acworth",
        "phone": "(770) 592-2363",
        "hours": "Mon-Sat: 9AM-6PM, Wed: OPEN, Sun: CLOSED",
        "special_note": "100,000 sq ft showroom - Only location open on Wednesdays",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=100+Robin+Road+Ext,+Acworth,+GA+30102",
        "directions_url": "https://www.google.com/maps/dir//100+Robin+Road+Ext,+Acworth,+GA+30102",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3310.5!2d-84.6775!3d34.0669!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s100+Robin+Road+Ext%2C+Acworth%2C+GA+30102!5e0!3m2!1sen!2sus",
        "is_flagship": True
    },
    {
        "name": "Dallas/Hiram",
        "type": "Full-Service Furniture & Mattress",
        "address": "52 Village Blvd, Dallas, GA 30157",
        "city": "Dallas",
        "phone": "(770) 505-8575",
        "hours": "Mon-Sat: 9AM-6PM, Wed: CLOSED, Sun: CLOSED",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=52+Village+Blvd,+Dallas,+GA+30157",
        "directions_url": "https://www.google.com/maps/dir//52+Village+Blvd,+Dallas,+GA+30157",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3314.8!2d-84.8406!3d33.9541!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s52+Village+Blvd%2C+Dallas%2C+GA+30157!5e0!3m2!1sen!2sus",
        "is_flagship": False
    },
    {
        "name": "Rome",
        "type": "Full-Service Furniture & Mattress",
        "address": "10 Central Plaza, Rome, GA 30161",
        "city": "Rome",
        "phone": "(706) 291-8772",
        "hours": "Mon-Sat: 9AM-6PM, Wed: CLOSED, Sun: CLOSED",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=10+Central+Plaza,+Rome,+GA+30161",
        "directions_url": "https://www.google.com/maps/dir//10+Central+Plaza,+Rome,+GA+30161",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3279.12!2d-85.1693!3d34.2463!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x888aa4b7ff4d54fd%3A0xb6158ec11841571f!2s10+Central+Plaza%2C+Rome%2C+GA+30161!5e0!3m2!1sen!2sus",
        "is_flagship": False
    },
    {
        "name": "Covington",
        "type": "Full-Service Furniture & Mattress",
        "address": "9218 US-278, Covington, GA 30014",
        "city": "Covington",
        "phone": "(770) 787-5200",
        "hours": "Mon-Sat: 9AM-6PM, Wed: CLOSED, Sun: CLOSED",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=9218+US-278,+Covington,+GA+30014",
        "directions_url": "https://www.google.com/maps/dir//9218+US-278,+Covington,+GA+30014",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3319.5!2d-83.8!3d33.6!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s9218+US-278%2C+Covington%2C+GA+30014!5e0!3m2!1sen!2sus",
        "is_flagship": False
    },
    {
        "name": "Canton (Sleep Center)",
        "type": "Mattress-Only",
        "address": "2249 Cumming Hwy, Canton, GA 30115",
        "city": "Canton",
        "phone": "(770) 720-9055",
        "hours": "Mon-Sat: 9AM-6PM, Wed: CLOSED, Sun: CLOSED",
        "special_note": "Mattresses and sleep products only",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=2249+Cumming+Hwy,+Canton,+GA+30115",
        "directions_url": "https://www.google.com/maps/dir//2249+Cumming+Hwy,+Canton,+GA+30115",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3299.5!2d-84.4875!3d34.2361!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s2249+Cumming+Hwy%2C+Canton%2C+GA+30115!5e0!3m2!1sen!2sus",
        "is_flagship": False
    },
    {
        "name": "Douglasville (Sleep Center)",
        "type": "Mattress-Only",
        "address": "7100 Douglas Blvd, Douglasville, GA 30135",
        "city": "Douglasville",
        "phone": "(770) 577-9544",
        "hours": "Mon-Sat: 9AM-6PM, Wed: CLOSED, Sun: CLOSED",
        "special_note": "Mattresses and sleep products only",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=7100+Douglas+Blvd,+Douglasville,+GA+30135",
        "directions_url": "https://www.google.com/maps/dir//7100+Douglas+Blvd,+Douglasville,+GA+30135",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3315.9!2d-84.7472!3d33.7519!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s7100+Douglas+Blvd%2C+Douglasville%2C+GA+30135!5e0!3m2!1sen!2sus",
        "is_flagship": False
    },
    {
        "name": "Customer Pickup Location (Distribution Center)",
        "type": "Pickup Only - NOT a retail showroom",
        "address": "6050 Old Alabama Rd, Acworth, GA 30102",
        "city": "Acworth",
        "phone": "(770) 592-2363",
        "hours": "By appointment only",
        "special_note": "Customer pickup ONLY - not a retail store. Items are NOT assembled.",
        "maps_url": "https://www.google.com/maps/search/?api=1&query=6050+Old+Alabama+Rd,+Acworth,+GA+30102",
        "directions_url": "https://www.google.com/maps/dir//6050+Old+Alabama+Rd,+Acworth,+GA+30102",
        "embed_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3308.5!2d-84.6547!3d34.0836!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2s6050+Old+Alabama+Rd%2C+Acworth%2C+GA+30102!5e0!3m2!1sen!2sus",
        "is_flagship": False
    }
]


# ============================================================================
# LOCATION TOOL
# ============================================================================

async def get_store_locations_tool(
    store_type: Optional[str] = None,
    customer_location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get Woodstock Furniture & Mattress Outlet store locations with Google Maps links.
    
    Use this tool when customers ask about:
    - Store locations and addresses
    - "Where are you located?"
    - "How do I get to your store?"
    - "What stores are near me?" / "I'm in [city/ZIP]"
    - Store hours and phone numbers
    
    Each location includes Google Maps links:
    - 'maps_url': View location on map (for "View on Maps")
    - 'directions_url': Get driving directions (for "Get Directions")
    - 'embed_url': For iframe embedding (webchat rich content)
    
    Args:
        store_type: Optional filter:
            - "furniture" for full-service stores
            - "mattress" for sleep centers only
            - "pickup" for distribution center
            - None for all locations
        customer_location: Optional customer city, ZIP code, or area.
            Gemini will use its geographic knowledge to suggest the nearest store.
            Examples: "30102", "Marietta", "near Atlanta", "Kennesaw area"
    
    Returns:
        All store locations with maps links. Gemini should use its geographic
        knowledge to recommend the closest store if customer_location is provided.
        
    RESPONSE FORMAT FOR EACH PLATFORM:
    
    **WEBCHAT (rich content):**
    Use embed_url in iframe:
    <iframe src="[embed_url]" width="100%" height="300"></iframe>
    
    **FACEBOOK/INSTAGRAM (text links):**
    📍 **[Store Name]** - [Address]
    📞 [phone] | ⏰ [hours]
    🗺️ View on Maps: [maps_url]
    🚗 Get Directions: [directions_url]
    """
    locations = STORE_LOCATIONS.copy()
    
    # Filter by store type if specified
    if store_type:
        store_type_lower = store_type.lower()
        if "furniture" in store_type_lower or "full" in store_type_lower:
            locations = [loc for loc in locations if "Full-Service" in loc.get("type", "")]
        elif "mattress" in store_type_lower or "sleep" in store_type_lower:
            locations = [loc for loc in locations if "Mattress-Only" in loc.get("type", "")]
        elif "pickup" in store_type_lower or "distribution" in store_type_lower:
            locations = [loc for loc in locations if "Pickup" in loc.get("type", "")]
    
    return {
        "status": "success",
        "total_locations": len(locations),
        "locations": locations,
        "customer_location": customer_location,
        "proximity_instruction": (
            f"Customer is at/near: {customer_location}. "
            "Use your geographic knowledge to recommend the CLOSEST store. "
            "Consider that all stores are in the Atlanta metro area of Georgia."
        ) if customer_location else None,
        "formatting": {
            "webchat": "Use embed_url in <iframe> for rich map display",
            "social": "Use maps_url (View) and directions_url (Directions) as clickable links"
        }
    }

