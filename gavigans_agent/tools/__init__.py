"""
Woodstock Outlet Agent Tools
=============================

Modular tool organization for maintainability.
"""

from .locations import get_store_locations_tool, STORE_LOCATIONS
from .delivery import get_delivery_options_by_zip_tool
from .rag import get_rag_auth_token_tool, query_rag_knowledge_tool
from .magento import (
    get_magento_token_tool,
    get_magento_categories_tool,
    search_magento_products_tool,
    get_magento_product_by_sku_tool,
    get_magento_brands_tool,
    get_magento_colors_tool,
    get_magento_attribute_options_tool,
)
from .loft import (
    get_customer_by_phone_tool,
    get_customer_by_email_tool,
    get_orders_by_customer_tool,
    get_order_details_tool,
    escalate_to_support_tool,
)

__all__ = [
    # Locations
    "get_store_locations_tool",
    "STORE_LOCATIONS",
    # Delivery
    "get_delivery_options_by_zip_tool",
    # RAG
    "get_rag_auth_token_tool",
    "query_rag_knowledge_tool",
    # Magento
    "get_magento_token_tool",
    "get_magento_categories_tool",
    "search_magento_products_tool",
    "get_magento_product_by_sku_tool",
    "get_magento_brands_tool",
    "get_magento_colors_tool",
    "get_magento_attribute_options_tool",
    # Loft
    "get_customer_by_phone_tool",
    "get_customer_by_email_tool",
    "get_orders_by_customer_tool",
    "get_order_details_tool",
    "escalate_to_support_tool",
]

