# Permission Structure in this API

This document outlines the permission structure used in this API application.

## User Types

1. **Anonymous Users**:
   - Can browse and view data (GET requests)
   - Cannot modify any data
   - Can register new accounts

2. **Authenticated Regular Users**:
   - Can browse and view all data
   - Can access their own user profile
   - Cannot modify any data in the system
   - Read-only access to all resources

3. **Admin Users** (`is_staff=True`):
   - Full CRUD permissions on all resources
   - Can create, view, update, and delete all data
   - Can manage user accounts

## Permission Classes

### IsAdminOrReadOnly

This custom permission class allows:
- Admin users (`is_staff=True`) to perform all actions: GET, POST, PUT, DELETE
- Regular users (`is_staff=False`) to perform only safe methods: GET, HEAD, OPTIONS

```python
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow safe methods for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin users can perform all actions
        return request.user and request.user.is_staff
```

### IsOwnerOrAdmin

This permission class allows:
- Admin users to access and modify all objects
- Regular users to access and modify only their own objects

```python
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user and request.user.is_staff:
            return True
            
        # Check if the object has a user field and if it matches the request user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False
```

## Permission Implementation

### ViewSets (Company, Building, Floor, Flat)

All model ViewSets use the `IsAdminOrReadOnly` permission:
- GET/LIST/RETRIEVE: Available to all users (including anonymous)
- POST/PUT/PATCH/DELETE: Available only to admin users

### Authentication

- Registration: Available to anonymous users
- Login: Available to all users
- User profile viewing: Available to authenticated users
- User profile editing: Available only to admin users

## Testing Permissions

### As Anonymous User:
```
# This will work
GET /api/buildings/

# This will fail
POST /api/buildings/
```

### As Regular User:
```
# Get token first
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123"
}

# This will work
GET /api/buildings/
Authorization: Bearer <your_token>

# This will fail
POST /api/buildings/
Authorization: Bearer <your_token>
```

### As Admin User:
```
# Get token first
POST /api/auth/login/
Content-Type: application/json

{
    "email": "admin@example.com",
    "password": "admin123"
}

# All operations will work with admin token
GET /api/buildings/
POST /api/buildings/
PUT /api/buildings/1/
DELETE /api/buildings/1/
Authorization: Bearer <your_admin_token>
```
