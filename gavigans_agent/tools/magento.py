"""
Magento Product Catalog Tools
=============================

Search products, browse categories, get brands/colors, and product details.
"""

import os
import json
import httpx
from typing import Dict, Any, Optional, List

# Configuration
DEFAULT_MAGENTO_BASE = os.getenv('MAGENTO_API_BASE', 'https://www.woodstockoutlet.com')
DEFAULT_MAGENTO_BASE = DEFAULT_MAGENTO_BASE.rstrip('/') if DEFAULT_MAGENTO_BASE else 'https://www.woodstockoutlet.com'
DEFAULT_MAGENTO_TOKEN_PATH = os.getenv('MAGENTO_ADMIN_TOKEN_PATH', '/rest/all/V1/integration/admin/token')
MAGENTO_TIMEOUT = float(os.getenv('MAGENTO_HTTP_TIMEOUT_SECONDS', '15'))


def _build_magento_url(path: str) -> str:
    """Return a sanitized Magento API URL using configured base + path."""
    base_url = os.getenv('MAGENTO_API_BASE', DEFAULT_MAGENTO_BASE).strip()
    base_url = base_url.rstrip('/') or DEFAULT_MAGENTO_BASE
    if not path.startswith('/'):
        path = '/' + path
    return f'{base_url}{path}'


# Load attribute options from local JSON file
try:
    with open('docs/product_attributes_options.json', 'r') as f:
        ATTRIBUTE_OPTIONS = json.load(f)
except Exception:
    ATTRIBUTE_OPTIONS = {}


# ============================================================================
# VERIFIED BRAND & COLOR DATA
# ============================================================================

VERIFIED_BRANDS = [
    {"name": "Signature Design by Ashley®", "id": "1229", "products": 1922},
    {"name": "homestyles", "id": "1200", "products": 651},
    {"name": "Liberty Furniture", "id": "1212", "products": 518},
    {"name": "Elements International", "id": "1191", "products": 487},
    {"name": "Vaughan-Bassett", "id": "2164", "products": 337},
    {"name": "Hooker Furnishings", "id": "2004", "products": 317},
    {"name": "aspenhome", "id": "1174", "products": 309},
    {"name": "Simpli-Home", "id": "16186", "products": 248},
    {"name": "Homelegance", "id": "1198", "products": 246},
    {"name": "England Furniture", "id": "1968", "products": 244},
    {"name": "Benchcraft® by Ashley", "id": "1176", "products": 221},
    {"name": "Ashley Furniture", "id": "1911", "products": 212},
    {"name": "HomeStretch", "id": "1199", "products": 189},
    {"name": "Tempur-Pedic", "id": "1233", "products": 187},
    {"name": "International Furniture Direct", "id": "1203", "products": 186},
    {"name": "New Classic Furniture", "id": "1220", "products": 180},
    {"name": "Sealy", "id": "1228", "products": 180},
    {"name": "Coaster", "id": "1185", "products": 179},
    {"name": "Millennium® by Ashley", "id": "9923", "products": 163},
    {"name": "Progressive Furniture", "id": "1223", "products": 152},
    {"name": "Lane Furniture", "id": "2024", "products": 143},
    {"name": "Lexington", "id": "1209", "products": 137},
    {"name": "Southern Motion", "id": "1232", "products": 123},
    {"name": "A-America", "id": "1895", "products": 121},
    {"name": "Serta", "id": "2113", "products": 116},
    {"name": "Sunny Designs", "id": "2139", "products": 113},
    {"name": "Hillsdale Furniture", "id": "1197", "products": 112},
    {"name": "Beautyrest", "id": "1177", "products": 99},
    {"name": "Stearns & Foster", "id": "2131", "products": 95},
    {"name": "Steve Silver", "id": "2133", "products": 90},
]

VERIFIED_COLORS = [
    {"name": "Brown", "id": "1720", "products": 2809},
    {"name": "Grey", "id": "1889", "products": 1554},
    {"name": "White", "id": "1888", "products": 853},
    {"name": "Beige", "id": "1719", "products": 610},
    {"name": "Black", "id": "1717", "products": 491},
    {"name": "Blue", "id": "1723", "products": 281},
    {"name": "Cream", "id": "1890", "products": 167},
    {"name": "Green", "id": "1722", "products": 61},
    {"name": "Silver/Chrome", "id": "1727", "products": 60},
    {"name": "Gold", "id": "1724", "products": 24},
    {"name": "Orange", "id": "2491", "products": 9},
    {"name": "Red", "id": "1725", "products": 8},
    {"name": "Pink", "id": "1728", "products": 8},
    {"name": "Multicolored/Patterned", "id": "1730", "products": 6},
    {"name": "Yellow", "id": "1721", "products": 5},
    {"name": "Purple", "id": "1726", "products": 1},
]

# Maps for human-friendly responses
BRAND_NAMES = {b["id"]: b["name"] for b in VERIFIED_BRANDS}
COLOR_NAMES = {c["id"]: c["name"] for c in VERIFIED_COLORS}

# ============================================================================
# SEATING CAPACITY MAPPING (for dining tables/sets)
# ============================================================================
# Attribute: seating_capacity - applies to Indoor & Outdoor dining
SEATING_CAPACITY = {
    2: "1149",
    3: "17573", 
    4: "1150",
    5: "1148",
    6: "1147",
    8: "1151",
    10: "1152",  # "10+"
    12: "2446",
    14: "17574",
}

def get_seating_capacity_ids(min_seats: int) -> str:
    """Get comma-separated IDs for seating capacity >= min_seats.
    
    Example: min_seats=8 returns "1151,1152,2446,17574" (8, 10+, 12, 14)
    """
    matching_ids = [
        seat_id for seats, seat_id in SEATING_CAPACITY.items() 
        if seats >= min_seats
    ]
    return ",".join(matching_ids) if matching_ids else None


# ============================================================================
# STYLE OPTIONS (for furniture style filtering)
# ============================================================================
STYLE_OPTIONS = {
    "modern": "1790",           # Modern & Contemporary
    "contemporary": "1790",     # Modern & Contemporary
    "farmhouse": "1793",
    "rustic": "1795",
    "casual": "1791",
    "coastal": "1796",
    "industrial": "1801",
    "mid-century": "1799",      # Mid-Century Modern
    "glam": "1798",
    "traditional": "1791",      # Maps to Casual as closest
    "lodge": "1800",
}

def get_style_id(style_name: str) -> str:
    """Get Magento style ID from common style name.
    
    Example: "farmhouse" returns "1793"
    """
    if not style_name:
        return None
    return STYLE_OPTIONS.get(style_name.lower().strip())


# ============================================================================
# MAGENTO TOOLS
# ============================================================================

async def get_magento_token_tool(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get Magento admin authentication token.
    Required for all Magento API calls.
    """
    try:
        username = os.getenv('MAGENTO_USERNAME')
        password = os.getenv('MAGENTO_PASSWORD')
        
        if not username or not password:
            return {"status": "error", "message": "Magento credentials not configured"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                _build_magento_url(DEFAULT_MAGENTO_TOKEN_PATH),
                headers={'Content-Type': 'application/json'},
                json={'username': username, 'password': password},
                timeout=MAGENTO_TIMEOUT
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": f"Magento auth failed: {response.status_code}"}
            
            token = response.text.strip('"')
            return {"status": "success", "token": token}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_magento_categories_tool(
    level: int = 0,
    include_subcategories: bool = True,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get furniture categories with clickable links to browse on the website.
    
    Use this tool when users want to see furniture categories, browse the catalog,
    or explore what types of furniture are available.
    
    Args:
        level: Filter by category level (0=all, 2=main categories, 3=subcategories)
        include_subcategories: If True, also include levels below the specified level
        page: Page number for pagination (default: 1)
        page_size: Number of categories per page (default: 10, use 0 for all)
    
    Returns:
        Dictionary with categories organized by level, each with clickable URLs.
    """
    try:
        token_result = await get_magento_token_tool()
        if token_result.get("status") != "success":
            return token_result
        
        token = token_result["token"]
        all_items = []
        api_page = 1
        api_page_size = 100
        
        async with httpx.AsyncClient() as client:
            while True:
                url = _build_magento_url('/rest/V1/categories/list')
                params = {
                    'searchCriteria[pageSize]': api_page_size,
                    'searchCriteria[currentPage]': api_page,
                    'searchCriteria[filterGroups][0][filters][0][field]': 'is_active',
                    'searchCriteria[filterGroups][0][filters][0][value]': '1',
                    'searchCriteria[filterGroups][0][filters][0][conditionType]': 'eq'
                }
                
                response = await client.get(
                    url, headers={'Authorization': f'Bearer {token}'},
                    params=params, timeout=MAGENTO_TIMEOUT
                )
                
                if response.status_code != 200:
                    return {"status": "error", "message": f"Failed to get categories: {response.status_code}"}
                
                data = response.json()
                items = data.get('items', [])
                total_count = data.get('total_count', 0)
                all_items.extend(items)
                
                if len(all_items) >= total_count or len(items) == 0:
                    break
                api_page += 1
        
        # Process categories
        categories_by_level: Dict[int, List] = {2: [], 3: [], 4: [], 5: [], 6: []}
        
        for item in all_items:
            url_path = None
            for attr in item.get('custom_attributes', []):
                if attr['attribute_code'] == 'url_path':
                    url_path = attr['value']
                    break
            
            if url_path and item.get('level', 0) >= 2:
                cat_level = item.get('level', 0)
                if cat_level in categories_by_level:
                    categories_by_level[cat_level].append({
                        'id': item['id'],
                        'name': item['name'],
                        'level': cat_level,
                        'url': f"https://www.woodstockoutlet.com/{url_path}",
                        'url_path': url_path
                    })
        
        def paginate_list(items: list, pg: int, pg_size: int):
            if pg_size == 0:
                return items, len(items), 1
            start = (pg - 1) * pg_size
            end = start + pg_size
            total = len(items)
            total_pages = (total + pg_size - 1) // pg_size if total > 0 else 0
            return items[start:end], total, total_pages
        
        if level == 0:
            return {
                "status": "success",
                "total_categories": sum(len(v) for v in categories_by_level.values()),
                "main_categories": categories_by_level[2],
                "subcategories": categories_by_level[3],
                "detailed_categories": categories_by_level[4],
                "message": "Use the 'url' field to link customers directly to each category."
            }
        elif level == 2:
            cats, total, total_pages = paginate_list(categories_by_level[2], page, page_size)
            result = {
                "status": "success",
                "main_categories": cats,
                "pagination": {"current_page": page, "page_size": page_size or total, "total_count": total, "total_pages": total_pages}
            }
            if include_subcategories:
                result["subcategories"] = categories_by_level[3]
            return result
        elif level == 3:
            cats, total, total_pages = paginate_list(categories_by_level[3], page, page_size)
            result = {
                "status": "success",
                "subcategories": cats,
                "pagination": {"current_page": page, "page_size": page_size or total, "total_count": total, "total_pages": total_pages}
            }
            if include_subcategories:
                result["detailed_categories"] = categories_by_level[4]
            return result
        else:
            all_cats = categories_by_level.get(level, [])
            cats, total, total_pages = paginate_list(all_cats, page, page_size)
            return {
                "status": "success",
                "categories": cats,
                "pagination": {"current_page": page, "page_size": page_size or total, "total_count": total, "total_pages": total_pages}
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def search_magento_products_tool(
    query: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    color_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    style: Optional[str] = None,
    min_seating: Optional[int] = None,
    custom_filters: Optional[List[Dict[str, str]]] = None,
    page_size: int = 5,
    current_page: int = 1
) -> Dict[str, Any]:
    """
    Search for products with filters and return clickable links and images.
    
    Args:
        query: Search term - product type (e.g., "sectional", "sofa", "recliner", "dining set")
        min_price: Minimum price filter
        max_price: Maximum price filter
        color_id: Color family ID (use get_magento_colors_tool for IDs)
        brand_id: Brand ID (use get_magento_brands_tool for IDs)
        style: Furniture style filter. Valid values:
               "modern", "contemporary", "farmhouse", "rustic", "casual",
               "coastal", "industrial", "mid-century", "glam", "lodge"
               Example: style="farmhouse" finds farmhouse-style furniture
        min_seating: Minimum seating capacity for DINING TABLES/SETS ONLY.
                     Use when customer asks for dining that "seats X or more".
                     Valid values: 2, 3, 4, 5, 6, 8, 10, 12, 14
                     Example: min_seating=8 finds dining for 8+ people
        custom_filters: List of custom attribute filters [{field, value}]
        page_size: Results per page (default: 5, max: 20)
        current_page: Page number (default: 1)
    
    Returns:
        Products with name, price, sku, url, image_url and pagination info.
    """
    try:
        token_result = await get_magento_token_tool()
        if token_result.get("status") != "success":
            return token_result
        
        token = token_result["token"]
        
        async with httpx.AsyncClient() as client:
            url = _build_magento_url('/rest/V1/products')
            params = {
                'searchCriteria[pageSize]': page_size,
                'searchCriteria[currentPage]': current_page
            }
            
            filter_idx = 0
            
            if query:
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'name'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = f'%{query}%'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'like'
                filter_idx += 1
            
            if min_price is not None:
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'price'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = str(min_price)
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'gteq'
                filter_idx += 1
            
            if max_price is not None:
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'price'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = str(max_price)
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'lteq'
                filter_idx += 1
            
            if color_id:
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'color_family'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = color_id
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'eq'
                filter_idx += 1
            
            if brand_id:
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'brand'
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = brand_id
                params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'eq'
                filter_idx += 1
            
            # Style filter (farmhouse, modern, rustic, etc.)
            if style:
                style_id = get_style_id(style)
                if style_id:
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'style'
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = style_id
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'eq'
                    filter_idx += 1
            
            # Seating capacity filter (for dining tables/sets)
            if min_seating is not None:
                seating_ids = get_seating_capacity_ids(min_seating)
                if seating_ids:
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'seating_capacity'
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = seating_ids
                    params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'in'
                    filter_idx += 1
            
            if custom_filters:
                for filter_item in custom_filters:
                    field = filter_item.get('field')
                    value = filter_item.get('value')
                    condition = filter_item.get('condition_type', 'eq')
                    if field and value:
                        params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = field
                        params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = value
                        params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = condition
                        filter_idx += 1
            
            # Only enabled products
            params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][field]'] = 'status'
            params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][value]'] = '1'
            params[f'searchCriteria[filterGroups][{filter_idx}][filters][0][conditionType]'] = 'eq'
            
            response = await client.get(
                url, headers={'Authorization': f'Bearer {token}'},
                params=params, timeout=MAGENTO_TIMEOUT
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": f"Failed to search products: {response.status_code}"}
            
            data = response.json()
            items = data.get('items', [])
            total_count = data.get('total_count', 0)
            
            products = []
            for item in items:
                url_key = None
                image_path = None
                
                for attr in item.get('custom_attributes', []):
                    attr_code = attr.get('attribute_code')
                    if attr_code == 'url_key':
                        url_key = attr.get('value')
                    elif attr_code in ('thumbnail', 'small_image') and not image_path:
                        image_path = attr.get('value')
                
                product_url = f"https://www.woodstockoutlet.com/{url_key}" if url_key else None
                image_url = None
                if image_path and image_path != 'no_selection':
                    image_url = f"https://www.woodstockoutlet.com/media/catalog/product{image_path}"
                
                products.append({
                    'name': item.get('name'),
                    'sku': item.get('sku'),
                    'price': item.get('price'),
                    'url': product_url,
                    'image_url': image_url,
                    'type': item.get('type_id')
                })
            
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
            
            return {
                "status": "success",
                "total_count": total_count,
                "products": products,
                "brand_name": BRAND_NAMES.get(brand_id),
                "color_name": COLOR_NAMES.get(color_id),
                "pagination": {
                    "current_page": current_page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_count": total_count,
                    "has_next": current_page < total_pages,
                    "has_prev": current_page > 1
                },
                "filters_applied": {
                    "query": query, "min_price": min_price, "max_price": max_price,
                    "color_id": color_id, "brand_id": brand_id, "style": style,
                    "min_seating": min_seating, "custom_filters": custom_filters
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_magento_product_by_sku_tool(sku: str) -> Dict[str, Any]:
    """
    Get detailed product information by SKU including all images.
    
    Args:
        sku: The product SKU (e.g., "124985831")
    
    Returns:
        Product details: name, price, url, description, dimensions, all_images
    """
    try:
        token_result = await get_magento_token_tool()
        if token_result.get("status") != "success":
            return token_result
        
        token = token_result["token"]
        
        async with httpx.AsyncClient() as client:
            url = _build_magento_url(f'/rest/V1/products/{sku}')
            response = await client.get(
                url, headers={'Authorization': f'Bearer {token}'}, timeout=MAGENTO_TIMEOUT
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": f"Product not found: {response.status_code}"}
            
            data = response.json()
            
            url_key = thumbnail = description = width = height = depth = None
            
            for attr in data.get('custom_attributes', []):
                code = attr.get('attribute_code')
                value = attr.get('value')
                if code == 'url_key': url_key = value
                elif code == 'thumbnail': thumbnail = value
                elif code == 'small_image' and not thumbnail: thumbnail = value
                elif code == 'description': description = value
                elif code == 'width': width = value
                elif code == 'height': height = value
                elif code == 'depth': depth = value
            
            product_url = f"https://www.woodstockoutlet.com/{url_key}" if url_key else None
            image_url = None
            if thumbnail and thumbnail != 'no_selection':
                image_url = f"https://www.woodstockoutlet.com/media/catalog/product{thumbnail}"
            
            all_images = []
            for entry in data.get('media_gallery_entries', []):
                file_path = entry.get('file')
                if file_path:
                    all_images.append({
                        'url': f"https://www.woodstockoutlet.com/media/catalog/product{file_path}",
                        'position': entry.get('position', 0),
                        'types': entry.get('types', [])
                    })
            
            return {
                "status": "success",
                "product": {
                    "name": data.get('name'),
                    "sku": data.get('sku'),
                    "price": data.get('price'),
                    "url": product_url,
                    "image_url": image_url,
                    "description": description,
                    "dimensions": {"width": width, "height": height, "depth": depth} if any([width, height, depth]) else None,
                    "all_images": all_images,
                    "type": data.get('type_id'),
                    "weight": data.get('weight')
                }
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_magento_brands_tool(search: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """
    Get available furniture brands with product counts.
    
    Args:
        search: Optional search term to filter brands
        limit: Maximum brands to return (default 20, use 0 for all)
    
    Returns:
        List of brands with ID and product count.
    """
    results = VERIFIED_BRANDS
    
    if search:
        search_lower = search.lower()
        results = [b for b in results if search_lower in b['name'].lower()]
    
    if limit > 0:
        results = results[:limit]
    
    return {
        "status": "success",
        "total_brands_available": 135,
        "brands": results,
        "usage_hint": "Use the 'id' value as brand_id in search_magento_products_tool"
    }


async def get_magento_colors_tool() -> Dict[str, Any]:
    """
    Get available color options with product counts.
    
    Returns:
        All 16 colors with ID and product count.
    """
    return {
        "status": "success",
        "total_colors_available": 16,
        "colors": VERIFIED_COLORS,
        "usage_hint": "Use the 'id' value as color_id in search_magento_products_tool"
    }


async def get_magento_attribute_options_tool(attribute_code: str) -> Dict[str, Any]:
    """
    Get valid options/values for a specific product attribute.
    
    REQUIRED: Call this BEFORE filtering by 'material', 'style', 'comfort', etc.
    
    Args:
        attribute_code: The attribute code (e.g., 'material', 'comfort', 'style')
    
    Returns:
        List of options with 'label' and 'value' (ID).
    """
    try:
        # Check local cache first
        if attribute_code in ATTRIBUTE_OPTIONS:
            return {
                "status": "success",
                "attribute_code": attribute_code,
                "options": ATTRIBUTE_OPTIONS[attribute_code],
                "source": "local_cache",
                "usage_hint": f"Use field='{attribute_code}' and value='[ID]' in search_magento_products_tool"
            }
        
        # Fallback to API
        token_result = await get_magento_token_tool()
        if token_result.get("status") != "success":
            return token_result
        
        token = token_result["token"]
        
        async with httpx.AsyncClient() as client:
            url = _build_magento_url(f'/rest/V1/products/attributes/{attribute_code}/options')
            response = await client.get(
                url, headers={'Authorization': f'Bearer {token}'}, timeout=MAGENTO_TIMEOUT
            )
            
            if response.status_code != 200:
                return {"status": "error", "message": f"Could not fetch options for {attribute_code}"}
            
            options = response.json()
            valid_options = [
                {"label": opt["label"], "value": opt["value"]} 
                for opt in options if opt.get("value") and opt.get("label")
            ]
            
            return {
                "status": "success",
                "attribute_code": attribute_code,
                "options": valid_options,
                "source": "magento_api",
                "usage_hint": f"Use field='{attribute_code}' and value='[ID]' in search_magento_products_tool"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

