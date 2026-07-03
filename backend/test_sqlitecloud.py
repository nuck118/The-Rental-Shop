#!/usr/bin/env python3
"""Test script to verify SQLite Cloud connection."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import engine
from sqlalchemy import text

print("=" * 60)
print("Testing SQLite Cloud Connection")
print("=" * 60)
print(f"Database URL: {settings.database_url}")
print()

try:
    # Test connection
    print("Connecting to database...")
    with engine.connect() as connection:
        print("✓ Connection successful!")
        
        # Test a simple query
        print("\nExecuting test query...")
        result = connection.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"✓ Query result: {row[0]}")
        
        # List tables
        print("\nListing tables in database...")
        if "sqlitecloud://" in settings.database_url:
            # SQLite Cloud specific query
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        else:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        
        tables = result.fetchall()
        if tables:
            print("✓ Tables found:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  (No tables found - database is empty)")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\n" + "=" * 60)
    print("✗ Connection test failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    engine.dispose()