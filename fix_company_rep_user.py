#!/usr/bin/env python
"""
Test script to create a company representative user and verify it works correctly.
"""

import os
import sys
import django
from datetime import timedelta

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from api.models import Company
from django.utils import timezone

User = get_user_model()

def create_company_rep():
    """Create a company representative user for testing"""
    
    # Create or get test company
    company_name = "Test Company"
    try:
        company = Company.objects.get(name=company_name)
        print(f"Using existing company: {company_name}")
    except Company.DoesNotExist:
        company = Company.objects.create(
            name=company_name,
            email="company@example.com",
            phone="1234567890",
            website="https://example.com"
        )
        print(f"Created new company: {company_name}")
    
    # Create or update company rep user
    email = "company_rep@example.com"
    password = "NewPassword123!"
    
    try:
        user = User.objects.get(email=email)
        print(f"User already exists: {email}")
        
        # Reset password and verify active status
        user.set_password(password)
        user.is_active = True
        user.company = company
        user.is_staff = False
        user.save()
        print(f"Password reset for user: {email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name="Company",
            last_name="Representative",
            is_staff=False,
            is_active=True,
        )
        user.company = company
        user.save()
        print(f"Created new company rep user: {email}")
    
    # Verify the user is set up correctly
    verify_user = User.objects.get(email=email)
    print(f"User exists: {verify_user is not None}, Has usable password: {verify_user.has_usable_password()}")
    print(f"User is associated with company: {verify_user.company.name}")
    print(f"User is active: {verify_user.is_active}")
    
    # Print login instructions
    print("\nLogin Instructions:")
    print(f"URL: http://127.0.0.1:8000/auth/login/")
    print(f"Email: {email}")
    print(f"Password: {password}")

if __name__ == "__main__":
    create_company_rep()
