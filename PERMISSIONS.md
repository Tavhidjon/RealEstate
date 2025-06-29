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

## Permission Implementation

### ViewSets (Company, Building, Floor, Flat)

All model ViewSets follow this permission pattern:
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
