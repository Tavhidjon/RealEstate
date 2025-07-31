from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class ReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow read access.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Admin users (is_staff=True) can perform all actions: GET, POST, PUT, DELETE
    - Regular users (is_staff=False) can only perform safe methods: GET, HEAD, OPTIONS
    """
    message = "Admin rights required to modify resources."
    
    def has_permission(self, request, view):
        # Allow safe methods for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin users can perform all actions
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Owners of an object to view and edit it
    - Admins can view and edit all objects
    """
    message = "You must be the owner of this object or an admin."
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
            
        # Check if the object has a user field and if it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If object doesn't have user field, deny access
        return False


class IsCompanyOwner(permissions.BasePermission):
    """
    Custom permission to only allow company owners access.
    Users must have company field set to a valid company to have access.
    """
    message = "You must be a company owner to access this resource."
    
    def has_permission(self, request, view):
        # Check if the user is authenticated and has a company
        return request.user and request.user.is_authenticated and request.user.company is not None


class IsCompanyOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Company owners to access their own company data
    - Admins can access all data
    """
    message = "You must be a company owner or admin."
    
    def has_permission(self, request, view):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
            
        # Company owners have access
        return request.user and request.user.is_authenticated and request.user.company is not None
