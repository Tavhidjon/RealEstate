from rest_framework import viewsets, filters, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import math
from django.db.models import F, ExpressionWrapper, FloatField
from django.contrib.auth import logout
from .models import Company, Building, Floor, Flat, AppUser
from .serializers import (
    CompanySerializer, BuildingSerializer, FloorSerializer, FlatSerializer,
    UserRegisterSerializer, UserDetailSerializer
)
from django.db.models import Count
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin


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
    return Response({
        "success": True,
        "message": "You have accessed a protected endpoint",
        "user": {
            "id": request.user.id,
            "email": request.user.email,
            "name": request.user.get_full_name(),
            "is_staff": request.user.is_staff,
        },
        "timestamp": "UTC timestamp: " + str(request.user.last_login) if request.user.last_login else None
    }, status=status.HTTP_200_OK)


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
    
    # Count buildings by company
    buildings_by_company = list(Company.objects.annotate(
        building_count=Count('buildings')
    ).values('name', 'building_count'))
    
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
            "companies": companies_count,
            "buildings": buildings_count,
            "floors": floors_count,
            "flats": flats_count,
        },
        "buildings_by_company": buildings_by_company
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
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find buildings near a specified location using the Haversine formula."""
        latitude = request.query_params.get('lat')
        longitude = request.query_params.get('lon')
        radius = float(request.query_params.get('radius', 5))  # Default 5km radius
        
        if latitude and longitude:
            lat = float(latitude)
            lng = float(longitude)
            
            buildings = Building.objects.all()
            
            nearby_buildings = []
            for building in buildings:
                lat1, lng1 = lat, lng
                lat2, lng2 = building.latitude, building.longitude
                
                lat1_rad = math.radians(lat1)
                lng1_rad = math.radians(lng1)
                lat2_rad = math.radians(lat2)
                lng2_rad = math.radians(lng2)
                
                dlng = lng2_rad - lng1_rad
                dlat = lat2_rad - lat1_rad
                a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = 6371 * c  # Earth radius in km
                
                if distance <= radius:
                    building.distance = distance  # Add distance property
                    nearby_buildings.append(building)
            
            nearby_buildings.sort(key=lambda b: b.distance)
            
            serializer = self.get_serializer(nearby_buildings, many=True)
            return Response(serializer.data)
        return Response({"error": "Latitude and longitude parameters are required"}, status=400)
    
    @action(detail=True, methods=['get'])
    def floors(self, request, pk=None):
        building = self.get_object()
        floors = building.floors.all()
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data)


class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['floor_number']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
    
    def get_queryset(self):
        queryset = Floor.objects.all()
        building_id = self.request.query_params.get('building', None)
        
        if building_id:
            queryset = queryset.filter(building_id=building_id)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def flats(self, request, pk=None):
        floor = self.get_object()
        flats = floor.flats.all()
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data)


class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['number']
    ordering_fields = ['number']
    permission_classes = [IsAdminOrReadOnly]  # Using our custom permission class
    
    def get_queryset(self):
        queryset = Flat.objects.all()
        floor_id = self.request.query_params.get('floor', None)
        
        if floor_id:
            queryset = queryset.filter(floor_id=floor_id)
        
        return queryset
