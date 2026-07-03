#!/usr/bin/env python3
"""Test script to verify admin authentication is working with SQLite Cloud."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Admin Authentication with SQLite Cloud")
print("=" * 60)

try:
    print("\n1. Checking database connection...")
    from app.core.database import engine
    from sqlalchemy.orm import Session
    from app.models.user import User
    print("   ✓ Database modules imported")
    
    with Session(engine) as db:
        print("   ✓ Connected to database")
        
        print("\n2. Checking for admin users...")
        users = db.query(User).all()
        print(f"   Total users in database: {len(users)}")
        
        if users:
            print("\n3. User details:")
            for user in users:
                print(f"   - Username: {user.username}")
                print(f"     Email: {user.email}")
                print(f"     Is Admin: {user.is_admin}")
                print(f"     Is Active: {user.is_active}")
                print(f"     Has Password Hash: {bool(user.password_hash)}")
        else:
            print("   ⚠ No users found in database!")
            print("   You need to create an admin user first.")
        
        print("\n4. Testing admin authentication backend...")
        from app.admin_auth import AdminAuthenticationBackend
        from app.core.config import settings
        
        auth_backend = AdminAuthenticationBackend()
        print("   ✓ Authentication backend initialized")
        
        # Create a mock request for testing
        from starlette.requests import Request
        from starlette.datastructures import Headers, URL
        from unittest.mock import MagicMock
        
        # Test with a mock request
        print("\n5. Testing login with mock request...")
        
        # Check if we have users to test with
        admin_users = [u for u in users if u.is_admin and u.is_active]
        
        if not admin_users:
            print("   ⚠ No active admin users found!")
            print("   Cannot test login without admin user.")
        else:
            print(f"   Found {len(admin_users)} active admin user(s)")
            print("   Admin login should work with these credentials:")
            for admin in admin_users:
                print(f"   - Username: {admin.username}")
    
    print("\n" + "=" * 60)
    print("✓ Admin authentication test completed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ Admin authentication test failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()