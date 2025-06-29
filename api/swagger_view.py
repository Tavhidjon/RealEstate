from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.generic import TemplateView
from django.conf import settings

class SwaggerUIWithAuth(TemplateView):
    """
    Custom Swagger UI view that includes a form to input JWT tokens
    """
    template_name = 'swagger_with_auth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['swagger_url'] = '/swagger/?format=openapi'
        return context
