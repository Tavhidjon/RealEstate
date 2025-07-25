"""
Script to fix the company representative login issue.
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

# Import models
from api.models import AppUser, Company
from django.contrib.auth.models import Group

# Constants
USERNAME = "company_rep"
EMAIL = "company_rep@example.com"
PASSWORD = "password123"  # Simple password for testing

try:
    # Get company representative
    user = AppUser.objects.get(email=EMAIL)
    print(f"Found user: {user.email}")
    
    # Reset password
    user.set_password(PASSWORD)
    user.save()
    print(f"Password reset for user: {user.email}")
    
    # Verify company association
    if user.company:
        print(f"User is associated with company: {user.company.name}")
    else:
        # Find the company and associate
        company = Company.objects.first()
        if company:
            user.company = company
            user.save()
            print(f"Associated user with company: {company.name}")
        else:
            print("No companies found in the database")
    
    # Make sure user is active
    if not user.is_active:
        user.is_active = True
        user.save()
        print("Activated user account")
    
    print("\nLOGIN CREDENTIALS:")
    print("==================")
    print(f"Email: {EMAIL}")
    print(f"Password: {PASSWORD}")
    print("\nUse these credentials in the Swagger UI to login")
    
except AppUser.DoesNotExist:
    print(f"User with email {EMAIL} not found")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")
