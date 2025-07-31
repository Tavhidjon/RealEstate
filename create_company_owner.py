"""
Script to create a company owner for testing.
To use this script, first make sure you have:
1. At least one Company in the database
2. A superuser account (admin)

Usage:
python create_company_owner.py [admin_email] [admin_password] [company_id]

Example:
python create_company_owner.py admin@example.com adminpassword 1
"""

import os
import sys
import json
import requests
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Company, AppUser

def create_company_owner(admin_email, admin_password, company_id, 
                         owner_username="company_owner", 
                         owner_email="company_owner@example.com",
                         owner_password="password123"):
    
    # Verify company exists
    try:
        company = Company.objects.get(id=company_id)
        print(f"Using company: {company.name} (ID: {company_id})")
    except Company.DoesNotExist:
        print(f"Error: Company with ID {company_id} does not exist")
        return False
    
    # Get admin token
    try:
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "email": admin_email,
            "password": admin_password
        }
        
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()
        
        token_data = login_response.json()
        access_token = token_data.get("access")
        
        print(f"Admin login successful")
    except Exception as e:
        print(f"Error logging in as admin: {e}")
        return False
    
    # Create company owner
    try:
        register_url = "http://localhost:8000/api/auth/register-company-owner/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        owner_data = {
            "username": owner_username,
            "email": owner_email,
            "password": owner_password,
            "first_name": "Company",
            "last_name": "Owner",
            "company": company_id
        }
        
        register_response = requests.post(register_url, headers=headers, json=owner_data)
        register_response.raise_for_status()
        
        print(f"Company owner created successfully:")
        print(json.dumps(register_response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error creating company owner: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    # Get arguments from command line
    if len(sys.argv) < 4:
        print("Usage: python create_company_owner.py [admin_email] [admin_password] [company_id]")
        sys.exit(1)
    
    admin_email = sys.argv[1]
    admin_password = sys.argv[2]
    company_id = int(sys.argv[3])
    
    create_company_owner(admin_email, admin_password, company_id)
