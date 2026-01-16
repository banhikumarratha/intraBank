"""
Create default test users for the application.
Run this script once to populate the database with test users.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import AuthService

def create_default_users():
    """Create 5 default users for testing."""
    auth_service = AuthService()
    
    test_users = [
        {"name": "Alice Johnson", "email": "alice@test.com", "password": "alice"},
        {"name": "Bob Smith", "email": "bob@test.com", "password": "bob"},
        {"name": "Charlie Davis", "email": "charlie@test.com", "password": "charlie"},
        {"name": "Diana Chen", "email": "diana@test.com", "password": "diana"},
        {"name": "Eve Martinez", "email": "eve@test.com", "password": "eve"}
    ]
    
    print("Creating default test users...")
    print("=" * 60)
    
    for user_data in test_users:
        result = auth_service.register(
            name=user_data["name"],
            email=user_data["email"],
            password=user_data["password"]
        )
        
        if result['success']:
            print(f"✓ Created: {user_data['name']} ({user_data['email']})")
            print(f"  Password: {user_data['password']}")
            print(f"  User ID: {result['user']['id']}")
        else:
            print(f"✗ Failed: {user_data['name']} - {result['message']}")
        print()
    
    print("=" * 60)
    print("Default users created successfully!")
    print("\nYou can now login with any of these credentials:")
    print("Email: alice@test.com, Password: alice")
    print("Email: bob@test.com, Password: bob")
    print("Email: charlie@test.com, Password: charlie")
    print("Email: diana@test.com, Password: diana")
    print("Email: eve@test.com, Password: eve")

if __name__ == "__main__":
    create_default_users()
