"""
Custom pagination classes for API responses.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for list endpoints.
    
    Query parameters:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
    
    Response format:
    {
        "count": total_items,
        "next": next_page_url,
        "previous": previous_page_url,
        "results": [...]
    }
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
