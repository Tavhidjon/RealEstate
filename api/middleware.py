import json
from django.conf import settings

class JWTDebugMiddleware:
    """
    Middleware to help with debugging JWT tokens in development
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and 'Authorization' in request.headers:
            # Just log that we found an Authorization header
            print(f"[JWT Debug] Authorization header found: {request.headers.get('Authorization')[:15]}...")
        
        response = self.get_response(request)
        
        # Debug JWT tokens in responses during development
        if settings.DEBUG and hasattr(response, 'data') and ('access' in response.data or 'refresh' in response.data):
            print("[JWT Debug] JWT token generated")
            if 'access' in response.data:
                print(f"[JWT Debug] Access token: {response.data['access'][:15]}...")
            if 'refresh' in response.data:
                print(f"[JWT Debug] Refresh token: {response.data['refresh'][:15]}...")
        
        return response
