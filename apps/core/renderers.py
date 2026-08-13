"""Custom JSON renderer for consistent API response format."""

from rest_framework import status
from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    """Wraps all responses in a consistent envelope."""
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        
        # 204 No Content must not include a response body
        if response is not None and response.status_code == status.HTTP_204_NO_CONTENT:
            return b''
        
        response_data = {
            'success': True,
            'message': 'Success',
            'data': data,
            'errors': None
        }
        
        if response is not None and response.status_code >= 400:
            response_data['success'] = False
            response_data['message'] = 'Error'
            response_data['data'] = None
            response_data['errors'] = data
        
        if isinstance(data, dict):
            if 'message' in data:
                response_data['message'] = data.pop('message')
            if 'success' in data:
                response_data['success'] = data.pop('success')
        
        return super().render(response_data, accepted_media_type, renderer_context)