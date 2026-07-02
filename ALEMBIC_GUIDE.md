# SQLAlchemy + Alembic Migration Guide

## Overview

The project now uses **SQLAlchemy** as the ORM and **Alembic** for database migrations. This provides:

- **Auto-migration**: Alembic automatically detects model changes and generates migration files
- **Version control**: All schema changes are tracked in migration files
- **Rollback support**: Easily downgrade to previous schema versions
- **Production-ready**: Industry-standard migration tool used by major projects

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Apply Initial Migration

The initial migration (`001_initial.py`) creates the `hardware_asset` table:

```bash
alembic upgrade head
```

This creates `rental_shop.db` with the schema.

### 3. Seed Sample Data

```bash
python scripts/seed_hardware.py
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

## Creating New Migrations

### When You Change a Model

After modifying a model in `app/models/`, create a migration:

```bash
alembic revision --autogenerate -m "Add new column to HardwareAsset"
```

This generates a new migration file in `alembic/versions/` with:
- `upgrade()` function — applies the change
- `downgrade()` function — reverts the change

### Example: Add a Column

1. **Update the model** (`app/models/hardware.py`):
```python
class HardwareAsset(Base):
    __tablename__ = "hardware_asset"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # ... existing columns ...
    warranty_expiry = Column(Date, nullable=True)  # NEW
```

2. **Generate migration**:
```bash
alembic revision --autogenerate -m "Add warranty_expiry to HardwareAsset"
```

3. **Review the generated migration** in `alembic/versions/`:
```python
def upgrade() -> None:
    op.add_column('hardware_asset', 
        sa.Column('warranty_expiry', sa.Date(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('hardware_asset', 'warranty_expiry')
```

4. **Apply the migration**:
```bash
alembic upgrade head
```

## Common Alembic Commands

### View Migration History

```bash
alembic history
```

Output:
```
<base> -> 001_initial (head), Create hardware_asset table
```

### Check Current Database Version

```bash
alembic current
```

### Upgrade to Latest Migration

```bash
alembic upgrade head
```

### Downgrade One Migration

```bash
alembic downgrade -1
```

### Downgrade to Specific Migration

```bash
alembic downgrade 001_initial
```

### Generate Migration Without Auto-Detection

```bash
alembic revision -m "Manual migration"
```

Then edit the generated file in `alembic/versions/` to add your SQL operations.

## Migration File Structure

Each migration file has this structure:

```python
"""Description of changes

Revision ID: 002_add_warranty
Revises: 001_initial
Create Date: 2024-01-15 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_warranty"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Apply changes
    op.add_column('hardware_asset', 
        sa.Column('warranty_expiry', sa.Date(), nullable=True)
    )

def downgrade() -> None:
    # Revert changes
    op.drop_column('hardware_asset', 'warranty_expiry')
```

## Best Practices

### 1. Always Review Generated Migrations

```bash
alembic revision --autogenerate -m "Description"
# Review alembic/versions/XXX_description.py
# Make adjustments if needed
alembic upgrade head
```

### 2. Test Migrations Locally

```bash
# Apply migration
alembic upgrade head

# Test your code
python -c "from app.models import HardwareAsset; print(HardwareAsset.__table__.columns.keys())"

# Rollback if needed
alembic downgrade -1
```

### 3. Use Descriptive Migration Names

```bash
# Good
alembic revision --autogenerate -m "Add warranty_expiry and maintenance_notes"

# Avoid
alembic revision --autogenerate -m "Update schema"
```

### 4. Keep Migrations Small

One logical change per migration makes rollbacks easier:

```bash
# Good: separate migrations
alembic revision --autogenerate -m "Add warranty_expiry column"
alembic revision --autogenerate -m "Add maintenance_notes column"

# Avoid: multiple unrelated changes in one migration
```

### 5. Never Edit Applied Migrations

If you need to change an applied migration:

```bash
# Downgrade
alembic downgrade -1

# Edit the migration file
# Re-apply
alembic upgrade head
```

## Troubleshooting

### Migration Won't Apply

```bash
# Check current version
alembic current

# Check migration history
alembic history

# Try upgrading with verbose output
alembic upgrade head --verbose
```

### Model Changes Not Detected

Ensure the model is imported in `alembic/env.py`:

```python
from app.core.database import Base
target_metadata = Base.metadata
```

### Database Locked Error

SQLite can have locking issues. Try:

```bash
# Stop the backend server
# Delete the database
rm rental_shop.db

# Re-apply migrations
alembic upgrade head

# Reseed data
python scripts/seed_hardware.py
```

### Revision ID Conflicts

If you have conflicting revision IDs:

```bash
# Check history
alembic history

# Merge branches (if using branches)
alembic merge -m "Merge branches"
```

## Production Deployment

### Before Deploying

1. **Test migrations locally**:
```bash
alembic upgrade head
# Test application
alembic downgrade -1
alembic upgrade head
```

2. **Backup production database**:
```bash
cp rental_shop.db rental_shop.db.backup
```

3. **Apply migrations**:
```bash
alembic upgrade head
```

4. **Verify schema**:
```bash
python -c "from app.models import HardwareAsset; print(HardwareAsset.__table__.columns.keys())"
```

### Rollback in Production

```bash
# Downgrade to previous version
alembic downgrade -1

# Or downgrade to specific version
alembic downgrade 001_initial
```

## File Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial.py          # Initial schema
│   │   ├── 002_add_warranty.py     # Example: add column
│   │   └── __init__.py
│   ├── env.py                      # Alembic environment config
│   ├── script.py.mako              # Migration template
│   └── __init__.py
├── alembic.ini                     # Alembic configuration
├── app/
│   ├── core/
│   │   ├── config.py               # Settings
│   │   └── database.py             # SQLAlchemy engine
│   ├── models/
│   │   ├── hardware.py             # HardwareAsset model
│   │   └── __init__.py
│   └── main.py
└── scripts/
    └── seed_hardware.py            # Data seeding script
```

## Next Steps

1. **Add more models**: Create new models in `app/models/`
2. **Generate migrations**: `alembic revision --autogenerate -m "description"`
3. **Apply migrations**: `alembic upgrade head`
4. **Build API endpoints**: Create routes in `app/api/routes/`
5. **Deploy**: Follow production deployment guidelines
