# Company Owner Usage Guide

## For Admin Users:

### 1. Register a Company Owner

As an admin, you can create a new company owner account by making a POST request to:

```
/api/auth/register-company-owner/
```

Required fields:
- `username`: Username for the new company owner
- `email`: Email address (must be unique)
- `password`: Password for the account
- `company`: ID of the company this user will represent (must already exist)

Optional fields:
- `first_name`: First name of the company owner
- `last_name`: Last name of the company owner
- `phone_number`: Contact phone number
- `profile_picture`: Profile image

Example request:

```json
POST /api/auth/register-company-owner/
{
    "username": "company_rep1",
    "email": "representative@company.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "company": 1
}
```

### 2. View All Company Owners

Admins can list all company owners with a GET request to:

```
/api/auth/company-owners/
```

You can filter by company ID:

```
/api/auth/company-owners/?company=1
```

## For Company Owners:

### 1. Login

Company owners can log in using the standard login endpoint:

```
POST /api/auth/login/
{
    "email": "representative@company.com", 
    "password": "secure_password"
}
```

The JWT token returned will include company information.

### 2. View Profile

Company owners can view their profile (including company information):

```
GET /api/auth/profile/
```

### 3. Manage Buildings

Company owners can create, view, update, and delete buildings for their company:

**View company buildings:**
```
GET /api/buildings/
```

**Create a new building:**
```
POST /api/buildings/
{
    "name": "New Apartment Complex",
    "latitude": 51.5074,
    "longitude": 0.1278,
    "floors_count": 5,
    "flats_count": 20,
    "address": "123 Main Street, City",
    "description": "Modern apartment complex in the heart of the city"
}
```

Note: Company owners don't need to specify the `company` field - it will be automatically set to their company.

**Update a building:**
```
PUT /api/buildings/{id}/
{
    "name": "Updated Building Name",
    ...
}
```

**Delete a building:**
```
DELETE /api/buildings/{id}/
```

## JWT Token Claims

The JWT token for company owners will include:
- `company_id`: ID of the associated company
- `company_name`: Name of the company
- `is_company_owner`: Boolean flag indicating company owner status
