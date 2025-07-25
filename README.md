# Building Management API

A Django REST Framework API for managing buildings, floors, and flats with integrated chat functionality.

## Features

- User registration and authentication with JWT tokens
- Building management with geospatial features
- Floor and flat management
- 3D model support
- API documentation with Swagger/ReDoc
- Robust chat system between users and companies
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

## Chat System

The application includes a robust chat system that allows users to communicate with companies. Full documentation for the chat system is available in [README-CHAT.md](README-CHAT.md).

### Chat API Endpoints

- `GET /api/chat/companies-list/`: List all companies available for chat
- `POST /api/chats/`: Create a new chat with a company
- `GET /api/chats/{id}/messages/`: View all messages in a specific chat
- `POST /api/chats/{id}/send_message/`: Send a message in a chat
- `GET /api/chats/unread_count/`: Check unread messages count
- `GET /api/company-chats/`: View all chats for a company (company representatives)
- `POST /api/company-chats/{id}/reply/`: Reply to a user message (company representatives)

### Implementation Details

The chat system code is organized in dedicated files:
- `api/chat_views.py`: Contains all chat-related views
- `api/chat_serializers.py`: Contains serializers for chat models
- `api/CHAT_IMPLEMENTATION.md`: Detailed implementation guide

## Running Tests

```bash
python manage.py test
```

### Testing the Chat System

You can test the chat functionality using the provided test script:

```bash
python manage.py shell < test_chat.py
```
