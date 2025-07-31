"""
Script to create a building as a company owner for testing.
To use this script, you need a company owner account already set up.

Usage:
python create_building.py [company_owner_email] [password] [building_name] [latitude] [longitude]

Example:
python create_building.py company_owner@example.com password123 "New Apartment Building" 51.5074 0.1278
"""

import os
import sys
import json
import requests
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.models import Company, AppUser, Building

def create_building(owner_email, password, building_name, latitude, longitude, address=None):
    # Get company owner token
    try:
        login_url = "http://localhost:8000/api/auth/login/"
        login_data = {
            "email": owner_email,
            "password": password
        }
        
        login_response = requests.post(login_url, json=login_data)
        login_response.raise_for_status()
        
        token_data = login_response.json()
        access_token = token_data.get("access")
        
        # Check if user is a company owner
        if not token_data.get("is_company_owner", False):
            print("Error: This user is not a company owner.")
            return False
        
        company_id = token_data.get("company_id")
        company_name = token_data.get("company_name")
        print(f"Logged in as company owner for: {company_name}")
    except Exception as e:
        print(f"Error logging in as company owner: {e}")
        return False
    
    # Create building
    try:
        create_url = "http://localhost:8000/api/buildings/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Basic required building data
        building_data = {
            "name": building_name,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "company": company_id,
            "floors_count": 1,  # Default value
            "flats_count": 1    # Default value
        }
        
        # Add optional address if provided
        if address:
            building_data["address"] = address
        
        create_response = requests.post(create_url, headers=headers, json=building_data)
        create_response.raise_for_status()
        
        print(f"Building created successfully:")
        print(json.dumps(create_response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error creating building: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False


if __name__ == "__main__":
    # Get arguments from command line
    if len(sys.argv) < 6:
        print("Usage: python create_building.py [company_owner_email] [password] [building_name] [latitude] [longitude]")
        sys.exit(1)
    
    owner_email = sys.argv[1]
    password = sys.argv[2]
    building_name = sys.argv[3]
    latitude = float(sys.argv[4])
    longitude = float(sys.argv[5])
    
    # Optional address parameter
    address = None
    if len(sys.argv) > 6:
        address = sys.argv[6]
    
    create_building(owner_email, password, building_name, latitude, longitude, address)
