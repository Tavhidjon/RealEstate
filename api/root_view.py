from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny


class ApiRootView(APIView):
    """
    Root view for the API that provides links to all main endpoints
    """
    permission_classes = [AllowAny]
    
    def get(self, request, format=None):
        response_data = {
            'auth': {
                'register': reverse('register', request=request, format=format),
                'login': reverse('token_obtain_pair', request=request, format=format),
                'refresh': reverse('token_refresh', request=request, format=format),
                'verify': reverse('token_verify', request=request, format=format),
                'logout': reverse('logout', request=request, format=format),
                'profile': reverse('user-detail', request=request, format=format),
                'help': reverse('auth-instructions', request=request, format=format),
            },
            'companies': reverse('company-list', request=request, format=format),
            'buildings': reverse('building-list', request=request, format=format),
            'floors': reverse('floor-list', request=request, format=format),
            'flats': reverse('flat-list', request=request, format=format),
            'protected_example': reverse('protected-example', request=request, format=format),
        }
        
        # Only show admin panel link if the user is authenticated with JWT and is an admin
        if request.user and request.user.is_authenticated and request.user.is_staff:
            response_data['admin_panel'] = reverse('admin-panel', request=request, format=format)
            
        return Response(response_data)
