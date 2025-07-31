import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Building, Company

class BuildingFilter(filters.FilterSet):
    """
    Custom filter for Buildings with enhanced filtering capabilities
    """
    # Filter by company name (not just ID)
    company_name = filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    
    # Range filters for floors and flats
    min_floors = filters.NumberFilter(field_name='floors_count', lookup_expr='gte')
    max_floors = filters.NumberFilter(field_name='floors_count', lookup_expr='lte')
    
    min_flats = filters.NumberFilter(field_name='flats_count', lookup_expr='gte')
    max_flats = filters.NumberFilter(field_name='flats_count', lookup_expr='lte')
    
    # Filter by location (address contains)
    location = filters.CharFilter(field_name='address', lookup_expr='icontains')
    
    # Filter by name with contains
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Building
        fields = {
            'company': ['exact'],
            'floors_count': ['exact'],
            'flats_count': ['exact'],
        }
