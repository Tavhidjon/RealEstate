from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import AppUser, Company
from .company_owner_serializers import CompanyOwnerRegisterSerializer
from .serializers import UserDetailSerializer


class CompanyOwnerRegisterView(generics.CreateAPIView):
    """
    API endpoint to register company owners.
    Only accessible to admin users.
    """
    queryset = AppUser.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = CompanyOwnerRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "success": True,
                    "message": "Company owner registered successfully",
                    "user": UserDetailSerializer(user, context=self.get_serializer_context()).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "success": False,
                    "message": "Registration failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log any exceptions
            print(f"Exception in company owner registration: {str(e)}")
            return Response({
                "success": False,
                "message": "Registration failed due to server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompanyOwnerListView(generics.ListAPIView):
    """
    API endpoint to list all company owners.
    Only accessible to admin users.
    """
    queryset = AppUser.objects.filter(company__isnull=False).order_by('-date_joined')
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username', 'email']

    def get_queryset(self):
        """
        Filter to only include users who are associated with a company
        """
        queryset = super().get_queryset()
        company_id = self.request.query_params.get('company', None)
        
        if company_id:
            queryset = queryset.filter(company__id=company_id)
            
        return queryset
