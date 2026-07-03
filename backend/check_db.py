from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.hardware import HardwareAsset, DataQuarantine
from app.models.audit_log import AuditLog
from sqlalchemy import inspect
import app.models  # noqa

# Check what tables exist
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Tables in database: {tables}')
print()

db = SessionLocal()
try:
    user_count = db.query(User).count()
    print(f'Users: {user_count}')
    for u in db.query(User).all():
        print(f'  ID={u.id} username={u.username} email={u.email} is_active={u.is_active} is_admin={u.is_admin}')
    
    hw_count = db.query(HardwareAsset).count()
    print(f'Hardware Assets: {hw_count}')
    for h in db.query(HardwareAsset).all():
        print(f'  ID={h.id} name={h.name} brand={h.brand} status={h.status} repair_flagged={h.repair_flagged}')
    
    audit_count = db.query(AuditLog).count()
    print(f'Audit Logs: {audit_count}')
    
    quarantine_count = db.query(DataQuarantine).count()
    print(f'Data Quarantine: {quarantine_count}')
finally:
    db.close()