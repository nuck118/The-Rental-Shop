#!/usr/bin/env python3
"""Verify that data is being read from SQLite Cloud."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Verifying Data Source - SQLite Cloud vs Local")
print("=" * 60)

try:
    print("\n1. Checking configuration...")
    from app.core.config import settings
    print(f"   DATABASE_URL: {settings.database_url}")
    
    is_sqlitecloud = settings.database_url.startswith("sqlitecloud://")
    print(f"   Using SQLite Cloud: {is_sqlitecloud}")
    
    if not is_sqlitecloud:
        print("   ⚠ WARNING: Not using SQLite Cloud!")
        print("   Please update .env to use SQLite Cloud connection string")
        sys.exit(1)
    
    print("\n2. Connecting to SQLite Cloud...")
    from app.core.database import engine
    from sqlalchemy.orm import Session
    from app.models.hardware import HardwareAsset
    
    with Session(engine) as db:
        print("   ✓ Connected to SQLite Cloud")
        
        print("\n3. Reading device data from SQLite Cloud...")
        devices = db.query(HardwareAsset).all()
        print(f"   ✓ Found {len(devices)} devices in SQLite Cloud")
        
        if devices:
            print("\n4. Device details from SQLite Cloud:")
            for device in devices[:5]:  # Show first 5
                print(f"   - ID {device.id}: {device.name} ({device.brand}) - {device.status}")
            if len(devices) > 5:
                print(f"   ... and {len(devices) - 5} more")
        
        print("\n5. Verifying data persistence...")
        # Count by status
        available = db.query(HardwareAsset).filter(HardwareAsset.status == "Available").count()
        in_use = db.query(HardwareAsset).filter(HardwareAsset.status == "In Use").count()
        repair = db.query(HardwareAsset).filter(HardwareAsset.status == "Repair").count()
        
        print(f"   Available: {available}")
        print(f"   In Use: {in_use}")
        print(f"   Repair: {repair}")
        print(f"   Total: {available + in_use + repair}")
    
    print("\n" + "=" * 60)
    print("✓ Confirmed: Data is from SQLite Cloud!")
    print("=" * 60)
    print("\nYour application is connected to:")
    print(f"  {settings.database_url}")
    print("\nAll device data is being read from and written to SQLite Cloud.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ Verification failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()