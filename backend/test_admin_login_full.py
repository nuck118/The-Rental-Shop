#!/usr/bin/env python3
"""Full test of admin login functionality with SQLite Cloud."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from app.core.database import engine
from sqlalchemy.orm import Session
from app.models.user import User
from app.admin_auth import AdminAuthenticationBackend
from app.core.user import verify_password
from starlette.requests import Request
from starlette.datastructures import URL
from unittest.mock import MagicMock

print("=" * 60)
print("Testing Admin Login Functionality")
print("=" * 60)

try:
    # Test 1: Verify admin user exists in SQLite Cloud
    print("\n1. Verifying admin user in SQLite Cloud...")
    with Session(engine) as db:
        admin = db.query(User).filter(User.username == "admin").first()
        
        if not admin:
            print("   ✗ Admin user not found!")
            sys.exit(1)
        
        print(f"   ✓ Admin user found in SQLite Cloud")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
    
    # Test 2: Verify password verification works
    print("\n2. Testing password verification...")
    with Session(engine) as db:
        admin = db.query(User).filter(User.username == "admin").first()
        
        # Test with correct password
        is_valid = verify_password("admin123", admin.password_hash)
        print(f"   Password 'admin123' valid: {is_valid}")
        
        if not is_valid:
            print("   ✗ Password verification failed!")
            sys.exit(1)
        
        print("   ✓ Password verification working")
    
    # Test 3: Test the authentication backend login method
    print("\n3. Testing authentication backend login...")
    
    # Create authentication backend
    auth_backend = AdminAuthenticationBackend()
    print("   ✓ Authentication backend created")
    
    # Create a mock request
    mock_request = MagicMock()
    mock_request.url = URL("http://localhost:8000/admin/login")
    
    # Mock the form data
    async def mock_form():
        return {
            "username": "admin",
            "password": "admin123"
        }
    
    mock_request.form = mock_form
    
    # Test login
    import asyncio
    login_result = asyncio.run(auth_backend.login(mock_request))
    
    print(f"   Login result: {login_result}")
    
    if login_result:
        print("   ✓ Login successful!")
        
        # Check if session was set
        if hasattr(mock_request, 'session'):
            print(f"   Session admin_token set: {'admin_token' in mock_request.session}")
            print(f"   Session admin_user set: {'admin_user' in mock_request.session}")
    else:
        print("   ✗ Login failed!")
        sys.exit(1)
    
    # Test 4: Verify data is from SQLite Cloud
    print("\n4. Confirming data source...")
    from app.core.config import settings
    
    if "sqlitecloud://" in settings.database_url:
        print(f"   ✓ Using SQLite Cloud: {settings.database_url}")
        print("   ✓ Admin credentials are verified against SQLite Cloud")
    else:
        print(f"   ✗ Not using SQLite Cloud: {settings.database_url}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All admin login tests passed!")
    print("=" * 60)
    print("\nAdmin panel login is working correctly with SQLite Cloud")
    print("\nLogin credentials:")
    print("  URL: http://localhost:8000/admin")
    print("  Username: admin")
    print("  Password: admin123")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ Admin login test failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()