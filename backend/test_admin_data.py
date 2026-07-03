#!/usr/bin/env python3
"""Test to verify admin panel is reading from SQLite Cloud."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from app.core.database import engine, SessionLocal
from sqlalchemy.orm import Session
from app.models.hardware import HardwareAsset
from app.models.user import User
from app.admin import get_dashboard_metrics

print("=" * 60)
print("Testing Admin Panel Data Source")
print("=" * 60)

try:
    print("\n1. Checking database configuration...")
    from app.core.config import settings
    print(f"   DATABASE_URL: {settings.database_url}")
    print(f"   Using SQLite Cloud: {settings.database_url.startswith('sqlitecloud://')}")
    
    print("\n2. Querying hardware data directly...")
    with Session(engine) as db:
        hardware_count = db.query(HardwareAsset).count()
        print(f"   Total hardware devices: {hardware_count}")
        
        devices = db.query(HardwareAsset).limit(5).all()
        print(f"   Sample devices:")
        for device in devices:
            print(f"     - {device.id}: {device.name} ({device.brand}) - {device.status}")
    
    print("\n3. Querying user data directly...")
    with Session(engine) as db:
        user_count = db.query(User).count()
        print(f"   Total users: {user_count}")
        
        users = db.query(User).all()
        print(f"   Users:")
        for user in users:
            print(f"     - {user.username} (admin: {user.is_admin}, active: {user.is_active})")
    
    print("\n4. Testing admin dashboard metrics function...")
    metrics = get_dashboard_metrics()
    print(f"   Dashboard metrics from SQLite Cloud:")
    print(f"     - Users: {metrics['users_count']}")
    print(f"     - Hardware: {metrics['hardware_count']}")
    print(f"     - Available: {metrics['available_hardware_count']}")
    print(f"     - Repair: {metrics['repair_hardware_count']}")
    
    print("\n5. Checking for local SQLite database...")
    import os.path
    local_db = "rental_shop.db"
    if os.path.exists(local_db):
        print(f"   ⚠ WARNING: Local SQLite database found: {local_db}")
        print(f"   This could cause confusion if admin panel is using it")
        
        # Try to connect to local DB and compare
        from sqlalchemy import create_engine
        from sqlalchemy.pool import StaticPool
        
        local_engine = create_engine(
            f"sqlite:///{local_db}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        with Session(local_engine) as local_db_session:
            local_hardware = local_db_session.query(HardwareAsset).count()
            local_users = local_db_session.query(User).count()
            
            print(f"   Local DB hardware count: {local_hardware}")
            print(f"   Local DB user count: {local_users}")
            print(f"   SQLite Cloud hardware count: {hardware_count}")
            print(f"   SQLite Cloud user count: {user_count}")
            
            if local_hardware != hardware_count or local_users != user_count:
                print(f"   ⚠ DATA MISMATCH DETECTED!")
                print(f"   Admin panel might be using local DB instead of SQLite Cloud")
        
        local_engine.dispose()
    else:
        print(f"   ✓ No local SQLite database found")
    
    print("\n6. Verifying admin panel uses correct engine...")
    from app.admin import engine as admin_engine
    print(f"   Admin engine is same as main engine: {admin_engine is engine}")
    
    print("\n" + "=" * 60)
    print("✓ Admin panel data verification completed!")
    print("=" * 60)
    
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