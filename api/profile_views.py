from django.views import View
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response

class ProfileRedirectView(View):
    """
    Redirect view for Django's default profile page after login
    This is used to redirect users after authenticating through Django admin or browsable API
    """
    def get(self, request):
        # You can customize this redirect to point to any page you want
        return redirect('/')
