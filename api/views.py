from rest_framework import viewsets, filters, generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import math
from django.db.models import F, ExpressionWrapper, FloatField, Q, Max, Prefetch, Count
from django.contrib.auth import logout
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from .filters import BuildingFilter

# Add this missing view for profile redirect
class ProfileRedirectView(View):
    """
    Redirects users from the default Django login url to the API root
    """
    def get(self, request):
        return redirect(reverse('api-root'))

from .models import Company, Building, Floor, Flat, AppUser, BuildingImage
from .serializers import (
    CompanySerializer, BuildingSerializer, FloorSerializer, FlatSerializer,
    UserRegisterSerializer, UserDetailSerializer, BuildingImageSerializer,
    AdminUserListSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .company_owner_permissions import IsCompanyOwnerForCompanyBuildings
from .company_owner_utils import is_company_owner, get_company_owner_stats


# Custom permission class (legacy - use classes from permissions.py instead)
class AdminWritePermission(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Read-only access for all authenticated users
    - Full access for admin users
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff


# Authentication Views
class RegisterView(generics.CreateAPIView):
    queryset = AppUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "success": True,
                    "message": "User registered successfully",
                    "user": UserDetailSerializer(user, context=self.get_serializer_context()).data
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"Registration validation errors: {serializer.errors}")
                return Response({
                    "success": False,
                    "message": "Registration failed",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log any exceptions
            print(f"Exception in registration: {str(e)}")
            return Response({
                "success": False,
                "message": "Registration failed due to server error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllUsersListView(generics.ListAPIView):
    """
    API endpoint that allows admins to view all users.
    """
    queryset = AppUser.objects.all().order_by('-date_joined')
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username', 'email', 'is_verified', 'last_login']


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = AppUser.objects.all()
    serializer_class = UserDetailSerializer
    
    def get_object(self):
        return self.request.user
        
    def get_permissions(self):
        """
        For GET requests, user can access their own profile
        For PUT/PATCH, only admin users can make changes
        """
        if self.request.method in permissions.SAFE_METHODS:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({
                "success": False,
                "message": "Refresh token is required",
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Blacklist the token
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as token_error:
            # Already blacklisted or other token error - still return success
            # as the end result is the token can't be used
            return Response({
                "success": True,
                "message": "Token already invalidated or logout already completed",
                "info": str(token_error)
            }, status=status.HTTP_200_OK)
            
        # Also handle Django's logout for session-based auth if it's being used
        logout(request)
        
        return Response({
            "success": True,
            "message": "Successfully logged out"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "success": False,
            "message": "Logout failed",
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_example_view(request):
    """
    Example view protected by JWT authentication
    """
    response_data = {
        "success": True,
        "message": "You have accessed a protected endpoint",
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "name": request.user.get_full_name(),
            "is_staff": request.user.is_staff,
        },
        "timestamp": "UTC timestamp: " + str(request.user.last_login) if request.user.last_login else None
    }
    
    # Add company information if the user is a company owner
    if is_company_owner(request.user):
        response_data["company"] = {
            "id": request.user.company.id,
            "name": request.user.company.name,
            "is_company_owner": True
        }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_panel_view(request):
    """
    Admin panel view - only accessible to admin users authenticated with JWT
    """
    # Get some statistics for the admin
    user_count = AppUser.objects.count()
    companies_count = Company.objects.count()
    buildings_count = Building.objects.count()
    floors_count = Floor.objects.count()
    flats_count = Flat.objects.count()
    
    # Count company owners
    company_owner_count = AppUser.objects.filter(company__isnull=False).count()
    
    # Count buildings by company
    buildings_by_company = list(Company.objects.annotate(
        building_count=Count('buildings')
    ).values('name', 'building_count'))
    
    # Count representatives by company
    representatives_by_company = list(Company.objects.annotate(
        representative_count=Count('representatives')
    ).values('name', 'representative_count'))
    
    # Return admin info
    return Response({
        "success": True,
        "message": "Welcome to the admin panel",
        "admin_user": {
            "id": request.user.id,
            "email": request.user.email,
            "name": request.user.get_full_name(),
            "is_staff": request.user.is_staff,
            "is_superuser": request.user.is_superuser,
        },
        "statistics": {
            "users": user_count,
            "company_owners": company_owner_count,
            "companies": companies_count,
            "buildings": buildings_count,
            "floors": floors_count,
            "flats": flats_count,
        },
        "buildings_by_company": buildings_by_company,
        "representatives_by_company": representatives_by_company
    }, status=status.HTTP_200_OK)


# ViewSets
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
    
    @action(detail=True, methods=['get'])
    def buildings(self, request, pk=None):
        company = self.get_object()
        buildings = company.buildings.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data)


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'address', 'description']  # Expanded search fields
    filterset_class = BuildingFilter  # Use our custom filter class
    ordering_fields = ['name', 'company__name', 'floors_count', 'flats_count']
    permission_classes = [IsCompanyOwnerForCompanyBuildings]  # Custom permission for company owners
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """
        Filter buildings based on user role:
        - Admin: Can see all buildings
        - Company owner: Can only see buildings for their company
        - Others: Can see all buildings (read-only)
        """
        queryset = Building.objects.all()

        # If user is a company owner, only show buildings from their company
        if self.request.user.is_authenticated and not self.request.user.is_staff and self.request.user.company:
            queryset = queryset.filter(company=self.request.user.company)

        return queryset
    
    @action(detail=True, methods=['post'], url_path='add-images')
    def add_images(self, request, pk=None):
        """Add multiple images to a building."""
        building = self.get_object()
        
        # Get data from request
        images = request.FILES.getlist('images', [])
        captions = request.POST.getlist('captions', [])
        orders = request.POST.getlist('orders', [])
        
        # Handle case where no images are provided
        if not images and not request.POST.get('caption'):
            # If neither images nor caption are provided, create a placeholder record
            building_image = BuildingImage.objects.create(
                building=building,
                image=None,
                caption="",
                order=0
            )
            serializer = BuildingImageSerializer(building_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Create image objects
        created_images = []
        
        # If there are no images but there's caption/order data, create records without images
        if not images and (captions or orders):
            max_items = max(len(captions), len(orders))
            for i in range(max_items):
                caption = captions[i] if i < len(captions) else ""
                order = int(orders[i]) if i < len(orders) and orders[i].isdigit() else i
                
                building_image = BuildingImage.objects.create(
                    building=building,
                    image=None,
                    caption=caption,
                    order=order
                )
                created_images.append(building_image)
        else:
            # Process each uploaded image
            for i, image in enumerate(images):
                caption = captions[i] if i < len(captions) else ""
                order = int(orders[i]) if i < len(orders) and orders[i].isdigit() else i
                
                building_image = BuildingImage.objects.create(
                    building=building,
                    image=image,
                    caption=caption,
                    order=order
                )
                created_images.append(building_image)
        
        serializer = BuildingImageSerializer(created_images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BuildingImageViewSet(viewsets.ModelViewSet):
    queryset = BuildingImage.objects.all()
    serializer_class = BuildingImageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['caption', 'building__name']
    ordering_fields = ['order', 'building__name']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
    parser_classes = [MultiPartParser, FormParser]


class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['building__name']
    ordering_fields = ['floor_number', 'building__name']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class


class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number', 'floor__building__name']
    ordering_fields = ['number', 'area', 'floor__floor_number']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
