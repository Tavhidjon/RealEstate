# JWT Authentication Guide

This Django REST Framework application uses JWT (JSON Web Token) authentication via the `djangorestframework-simplejwt` library.

## Authentication Endpoints

### Register a new user
```
POST /auth/register/
```
Body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Login (Get JWT tokens)
```
POST /auth/login/
```
Body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Access Token
```
POST /auth/login/refresh/
```
Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Verify Token
```
POST /auth/verify/
```
Body:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Logout (Blacklist Token)
```
POST /auth/logout/
```
Body:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Using JWT Tokens

### In HTTP Headers

For authenticated requests, include the access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## JWT Configuration

The current JWT configuration:

- Access token lifetime: 15 minutes
- Refresh token lifetime: 7 days

## Example Protected Endpoint

To test JWT authentication, use the example protected endpoint:

```
GET /example/protected/
```

This endpoint requires a valid JWT token and returns information about the authenticated user.
