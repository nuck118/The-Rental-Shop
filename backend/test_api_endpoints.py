#!/usr/bin/env python3
"""Test script to verify API endpoints are working."""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing API Endpoints")
print("=" * 60)

try:
    print("\n1. Importing application...")
    from app.main import app
    from fastapi.testclient import TestClient
    print("   ✓ Application imported")
    
    # Create test client
    client = TestClient(app)
    
    print("\n2. Testing hardware API endpoint...")
    
    # Test the hardware endpoint without auth (should fail or return empty)
    response = client.get("/api/hardware?skip=0&limit=100")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        devices = response.json()
        print(f"   ✓ Success! Found {len(devices)} devices")
        if devices:
            print(f"   Sample device: {devices[0]}")
        else:
            print("   ⚠ No devices found in database")
    else:
        print(f"   Response: {response.text}")
        print(f"   ✗ Failed with status {response.status_code}")
    
    print("\n3. Checking database directly...")
    from app.core.database import engine
    from sqlalchemy import text
    from app.models.hardware import HardwareAsset
    from sqlalchemy.orm import Session
    
    with Session(engine) as db:
        count = db.query(HardwareAsset).count()
        print(f"   ✓ Total devices in database: {count}")
        
        if count > 0:
            devices = db.query(HardwareAsset).limit(5).all()
            print(f"   Sample devices:")
            for device in devices:
                print(f"     - {device.id}: {device.name} ({device.brand}) - {device.status}")
    
    print("\n" + "=" * 60)
    print("✓ API test completed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("✗ API test failed!")
    print("=" * 60)
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()