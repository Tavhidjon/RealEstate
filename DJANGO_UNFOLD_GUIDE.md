# Django Unfold Admin Setup Guide

This guide explains how to set up the Django Unfold admin panel in the Real Estate project.

## What is Django Unfold?

Django Unfold is a modern admin panel theme for Django that provides a clean, intuitive interface with enhanced components, charts, and design elements that make managing your application data more pleasant and efficient.

## Installation

1. Install the django-unfold package:

```bash
pip install django-unfold
```

2. Add it to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # Django Unfold admin
    'unfold',  
    'unfold.contrib.filters',  # Optional for custom filters
    'unfold.contrib.forms',    # Optional for custom forms
    
    # Default Django apps - must come after unfold
    'django.contrib.admin',
    # ... other apps
]
```

## Configuration

The Unfold admin panel is configured in `settings.py`:

```python
# Unfold Admin Configuration
UNFOLD = {
    "SITE_TITLE": "Real Estate Admin",
    "SITE_HEADER": "Real Estate Management",
    "SITE_ICON": None,  # or path to custom icon
    "COLORS": {
        "PRIMARY_50": "#faf5ff",
        "PRIMARY_100": "#f3e8ff",
        "PRIMARY_200": "#e9d5ff",
        "PRIMARY_300": "#d8b4fe",
        "PRIMARY_400": "#c084fc",
        "PRIMARY_500": "#a855f7",
        "PRIMARY_600": "#9333ea",
        "PRIMARY_700": "#7e22ce",
        "PRIMARY_800": "#6b21a8",
        "PRIMARY_900": "#581c87",
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Buildings",
                "icon": "heroicons.outline.home",
                "models": ["api.building", "api.floor", "api.flat", "api.buildingimage"]
            },
            {
                "title": "Companies",
                "icon": "heroicons.outline.office-building",
                "models": ["api.company"]
            },
            {
                "title": "Users",
                "icon": "heroicons.outline.user-group",
                "models": ["api.appuser"]
            },
            {
                "title": "Messaging",
                "icon": "heroicons.outline.chat",
                "models": ["api.chat", "api.message"]
            }
        ]
    }
}
```

## Admin Model Classes

For each model, you can use Unfold's enhanced ModelAdmin classes in `admin.py`:

```python
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from unfold.contrib.forms.widgets import DropdownSelectWidget
from unfold.decorators import display
```

## Enhanced UI Elements

### Pills for Status

```python
def get_building_count(self, obj):
    count = obj.buildings.count()
    return format_html(
        '<span class="pill pill-success">{}</span>', 
        count
    ) if count > 0 else format_html('<span class="pill pill-light">0</span>')
```

### Enhanced Image Display

```python
def get_image(self, obj):
    if obj.image:
        return format_html(
            '<img src="{}" width="80" height="50" style="object-fit: cover; border-radius: 4px;" />', 
            obj.image.url
        )
    return format_html('<span class="pill pill-light">No Image</span>')
```

## Additional Features

### Admin Dashboard

Unfold supports enhanced dashboards. You can create a custom dashboard by:

1. Creating a custom view in `admin.py`
2. Creating a template in `templates/admin/dashboard.html`
3. Registering the view in your admin URLs

### Customizing Lists and Forms

- Use `show_facets = True` to show statistics on list pages
- Add `search_help_text` to provide guidance for search fields
- Set `actions_position = "both"` to have action buttons at top and bottom
- Use `empty_value_display = "—"` for consistent empty value display

## Benefits of Django Unfold

- Modern, responsive design
- Dark mode support
- Enhanced UI components
- Better visualization of data
- Customizable sidebar and navigation
- Improved user experience for administrators
- Cleaner interface for managing content

## Next Steps

After installation and configuration:

1. Start your server with `python manage.py runserver`
2. Go to the admin interface (typically at http://localhost:8000/admin/)
3. Log in with your admin credentials
4. Explore the new interface and features provided by Django Unfold
