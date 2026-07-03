#!/usr/bin/env python3
"""Test script to verify the application can start with SQLite Cloud."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing Application Startup with SQLite Cloud")
print("=" * 60)

try:
    print("\n1. Importing application modules...")
    from app.core.config import settings
    print(f"   ✓ Settings loaded")
    print(f"   - Database URL: {settings.database_url}")
    
    from app.core.database import engine, Base, get_db
    print(f"   ✓ Database engine created")
    
    from app.models import hardware, user  # noqa: F401
    print(f"   ✓ Models imported")
    
    print("\n2. Testing database connection...")
    with engine.connect() as connection:
        print(f"   ✓ Connection successful")
        
        # Check if tables exist
        from sqlalchemy import text
        result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"   ✓ Found {len(tables)} tables: {', '.join(tables)}")
    
    print("\n3. Testing session creation...")
    db = next(get_db())
    print(f"   ✓ Database session created")
    db.close()
    
    print("\n4. Testing table creation (if needed)...")
    # This will create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print(f"   ✓ Tables verified/created")
    
    print("\n" + "=" * 60)
    print("✓ Application startup test passed!")
    print("=" * 60)
    print("\nYour application is ready to use with SQLite Cloud!")
    print(f"Database: {settings.database_url}")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ Application startup test failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()