from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class AuthInstructionsView(APIView):
    """
    View providing instructions on how to authenticate with JWT tokens
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "message": "This API uses JWT Authentication",
            "instructions": [
                "1. First, log in to get tokens: POST /auth/login/ with email and password",
                "2. Then include the access token in all API requests: Authorization: Bearer <access_token>",
                "3. When the access token expires, get a new one: POST /auth/login/refresh/ with the refresh token"
            ],
            "note": "Session authentication is not supported. Please use JWT tokens for all authenticated requests.",
            "endpoints": {
                "login": "/auth/login/",
                "refresh": "/auth/login/refresh/",
                "register": "/auth/register/",
                "logout": "/auth/logout/"
            }
        })
