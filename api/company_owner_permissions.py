from rest_framework import permissions

class IsCompanyOwnerForCompanyBuildings(permissions.BasePermission):
    """
    Custom permission to allow:
    - Company owners to create/edit buildings for their own company
    - Admins to have full access to all buildings
    - Everyone else to have read-only access
    """
    message = "You must be a company owner or admin to modify buildings."
    
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
        
        # For POST requests, check if user is a company owner
        if request.method == 'POST' and request.user and request.user.is_authenticated:
            return request.user.company is not None
            
        return False
    
    def has_object_permission(self, request, view, obj):
        # Allow safe methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
            
        # Company owners can only edit buildings for their company
        if request.user and request.user.company:
            return obj.company == request.user.company
            
        return False
