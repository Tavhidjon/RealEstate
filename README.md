# Building Management API

A Django REST Framework API for managing buildings, floors, and flats.

## Features

- User registration and authentication with JWT tokens
- Building management with geospatial features
- Floor and flat management
- 3D model support
- API documentation with Swagger/ReDoc
- Strict permission structure:
  - Admin users have full CRUD access
  - Regular users have read-only access
  - Anonymous users can view data but not modify it

## Prerequisites

- Python 3.8+
- PostgreSQL with PostGIS extension
- GDAL library

## Installation

1. Clone the repository:
```bash
git clone https://your-repository-url.git
cd project-directory
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your database in server/settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (if you didn't use the provided migration):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/auth/register/`: Register a new user
- `POST /api/auth/login/`: Obtain JWT tokens
- `POST /api/auth/login/refresh/`: Refresh JWT token
- `POST /api/auth/logout/`: Logout (blacklist token)
- `GET /api/auth/profile/`: Get user profile

### Buildings

- `GET /api/buildings/`: List all buildings
- `POST /api/buildings/`: Create a building
- `GET /api/buildings/{id}/`: Get building details
- `PUT /api/buildings/{id}/`: Update a building
- `DELETE /api/buildings/{id}/`: Delete a building
- `GET /api/buildings/nearby/?lat=XX&lon=YY&radius=ZZ`: Find buildings near a location

### Companies, Floors, and Flats

Similar CRUD endpoints are available for companies, floors, and flats.

## Documentation

API documentation is available at:

- Swagger: `/swagger/`
- ReDoc: `/redoc/`

## Permission Structure

The API implements a strict permission structure:

| Action | Anonymous Users | Regular Users | Admin Users |
|--------|----------------|---------------|-------------|
| View data | ✓ | ✓ | ✓ |
| Create data | ✗ | ✗ | ✓ |
| Update data | ✗ | ✗ | ✓ |
| Delete data | ✗ | ✗ | ✓ |
| Register | ✓ | N/A | N/A |
| Edit profile | ✗ | ✗ | ✓ |

This ensures that only admin users can make changes to the system data, while regular users have read-only access. For more details, see [PERMISSIONS.md](PERMISSIONS.md).

## Running Tests

```bash
python manage.py test
```
