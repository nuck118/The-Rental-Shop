# Migration: Piccolo → SQLAlchemy + Alembic

## What Changed

### Removed
- ❌ Piccolo ORM (`piccolo`, `piccolo_admin`, `piccolo_api`)
- ❌ Piccolo migrations system
- ❌ `piccolo_conf.py` and `app/piccolo_app.py`
- ❌ Piccolo admin panel at `/admin`

### Added
- ✅ SQLAlchemy ORM (`sqlalchemy`)
- ✅ Alembic migrations (`alembic`)
- ✅ `app/core/database.py` — SQLAlchemy engine & session management
- ✅ `alembic/` directory — migration files and configuration
- ✅ `alembic.ini` — Alembic configuration

## Key Improvements

### 1. Auto-Migration Support
**Before (Piccolo)**:
```bash
piccolo migrations new app --auto
piccolo migrations run
```

**After (Alembic)**:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

Alembic automatically detects model changes and generates migration files.

### 2. Better Version Control
- All migrations tracked in `alembic/versions/`
- Each migration has `upgrade()` and `downgrade()` functions
- Easy to review what changed in each migration

### 3. Production-Ready
- Industry-standard migration tool (used by Django, Flask, etc.)
- Robust rollback support
- Better error handling and validation

### 4. Cleaner ORM
- SQLAlchemy is more flexible and powerful
- Better async support (though we use sync for simplicity)
- Larger ecosystem and community

## File Changes

### Models
**Before**:
```python
from piccolo.columns import Date, Integer, Text, Varchar
from piccolo.table import Table

class HardwareAsset(Table):
    id = Integer(primary_key=True)
    name = Varchar(length=255)
```

**After**:
```python
from sqlalchemy import Column, Integer, String, Text, Date
from app.core.database import Base

class HardwareAsset(Base):
    __tablename__ = "hardware_asset"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

### Database Configuration
**Before** (`piccolo_conf.py`):
```python
from piccolo.engine.sqlite import SQLiteEngine
DB = SQLiteEngine(path="rental_shop.db")
```

**After** (`app/core/database.py`):
```python
from sqlalchemy import create_engine
engine = create_engine("sqlite:///rental_shop.db")
SessionLocal = sessionmaker(bind=engine)
```

### Seed Script
**Before** (async with Piccolo):
```python
async def seed():
    await HardwareAsset.insert(...).run()
```

**After** (sync with SQLAlchemy):
```python
def seed():
    db = SessionLocal()
    db.add(HardwareAsset(...))
    db.commit()
```

## Setup Instructions

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

### 2. Apply Initial Migration
```bash
alembic upgrade head
```

Creates `rental_shop.db` with the schema.

### 3. Seed Data
```bash
python scripts/seed_hardware.py
```

### 4. Start Backend
```bash
uvicorn app.main:app --reload
```

## Migration Commands Reference

| Task | Command |
|------|---------|
| Create migration | `alembic revision --autogenerate -m "Description"` |
| Apply migrations | `alembic upgrade head` |
| Downgrade one | `alembic downgrade -1` |
| View history | `alembic history` |
| Check current | `alembic current` |

## Adding New Models

### 1. Create Model
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    name = Column(String(255))
```

### 2. Generate Migration
```bash
alembic revision --autogenerate -m "Add User table"
```

### 3. Apply Migration
```bash
alembic upgrade head
```

## Troubleshooting

### Database Already Exists
If you have an old Piccolo database:

```bash
# Backup old database
mv rental_shop.db rental_shop.db.old

# Create new database with SQLAlchemy schema
alembic upgrade head

# Seed data
python scripts/seed_hardware.py
```

### Migration Won't Apply
```bash
# Check current version
alembic current

# Check history
alembic history

# Apply with verbose output
alembic upgrade head --verbose
```

### Model Changes Not Detected
Ensure model is imported in `alembic/env.py`:

```python
from app.core.database import Base
target_metadata = Base.metadata
```

## Benefits Summary

| Feature | Piccolo | SQLAlchemy + Alembic |
|---------|---------|----------------------|
| Auto-migration | ❌ Manual | ✅ Automatic |
| Rollback support | ⚠️ Limited | ✅ Full |
| Version control | ⚠️ Basic | ✅ Detailed |
| Community | ⚠️ Small | ✅ Large |
| Production-ready | ⚠️ Emerging | ✅ Mature |
| Async support | ✅ Native | ⚠️ Limited |
| Admin panel | ✅ Built-in | ❌ Separate |

## Next Steps

1. **Read ALEMBIC_GUIDE.md** — Comprehensive migration guide
2. **Create new models** — Add User, Rental, MaintenanceLog tables
3. **Generate migrations** — `alembic revision --autogenerate -m "..."`
4. **Build API endpoints** — Create routes for new models
5. **Deploy** — Follow production deployment guidelines

## Documentation

- **README.md** — Updated with SQLAlchemy + Alembic info
- **ALEMBIC_GUIDE.md** — Comprehensive migration guide
- **QUICKSTART.md** — Quick reference for common tasks
- **TROUBLESHOOTING.md** — Debugging guide
