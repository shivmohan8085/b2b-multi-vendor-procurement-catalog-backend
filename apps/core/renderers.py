"""
Custom JSON renderer for consistent API response format.

All API responses will follow this structure:
{
    "success": true/false,
    "message": "...",
    "data": {...},
    "errors": {...}
}
"""

from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that wraps all responses in a consistent format.
    
    Response format:
    {
        "success": bool,
        "message": str,
        "data": dict/list/null,
        "errors": dict/null
    }
    """
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render the response data into a consistent format.
        
        Args:
            data: The response data from the view
            accepted_media_type: The media type accepted by the client
            renderer_context: Context dictionary with view, request, response info
        
        Returns:
            JSON bytes with consistent response structure
        """
        response = renderer_context.get('response') if renderer_context else None
        
        # Initialize response structure
        response_data = {
            'success': True,
            'message': 'Success',
            'data': data,
            'errors': None
        }
        
        # Handle errors (4xx and 5xx status codes)
        if response and response.status_code >= 400:
            response_data['success'] = False
            response_data['message'] = 'Error'
            response_data['data'] = None
            response_data['errors'] = data
        
        # Handle custom messages if provided in data
        if isinstance(data, dict):
            if 'message' in data:
                response_data['message'] = data.pop('message')
            if 'success' in data:
                response_data['success'] = data.pop('success')
        
        return super().render(response_data, accepted_media_type, renderer_context)
