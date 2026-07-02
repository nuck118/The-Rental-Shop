# SQLAdmin Setup Guide

## Installation

### 1. Update Dependencies

SQLAdmin has been added to `requirements.txt`. Install it:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migrations

Create the User and AuditLog tables:

```bash
alembic upgrade head
```

This creates:
- `user` table — for user accounts
- `audit_log` table — for tracking changes

### 3. Create Initial Admin User

Seed the database with an initial admin account:

```bash
python scripts/seed_admin.py
```

Output:
```
✓ Created admin user: admin
  Email: admin@rentalshop.local
  ID: 1

⚠️  IMPORTANT: Change the default password in production!
   Username: admin
   Default Password: admin123
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload
```

### 5. Access Admin Panel

Open http://localhost:8000/admin in your browser.

## Initial Setup

### Step 1: Login (Optional)

The admin panel is currently accessible without authentication. In production, implement authentication.

### Step 2: Create Users

1. Click **Users** in the sidebar
2. Click **Create**
3. Fill in user details:
   - Username (required, unique)
   - Email (required, unique)
   - Full Name (optional)
   - Password Hash (required)
   - Is Active (default: true)
   - Is Admin (default: false)
4. Click **Save**

### Step 3: Manage Hardware

1. Click **Hardware Assets** in the sidebar
2. View existing hardware or create new
3. Update status, assignment, and notes
4. Changes are automatically logged

### Step 4: Review Audit History

1. Click **Audit Logs** in the sidebar
2. View all changes made by users
3. Search by user, action, or table
4. Export logs if needed

## Database Schema

### User Table

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX ix_user_username ON user(username);
CREATE INDEX ix_user_email ON user(email);
```

### Audit Log Table

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    old_values TEXT,
    new_values TEXT,
    description TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE INDEX ix_audit_log_user_id ON audit_log(user_id);
CREATE INDEX ix_audit_log_action ON audit_log(action);
CREATE INDEX ix_audit_log_table_name ON audit_log(table_name);
CREATE INDEX ix_audit_log_created_at ON audit_log(created_at);
```

## File Structure

```
backend/
├── app/
│   ├── admin.py                 # SQLAdmin configuration
│   ├── core/
│   │   ├── audit.py            # Audit logging utilities
│   │   └── user.py             # User management utilities
│   ├── models/
│   │   ├── user.py             # User model
│   │   ├── audit_log.py        # AuditLog model
│   │   └── hardware.py         # HardwareAsset model
│   └── main.py                 # FastAPI app with SQLAdmin
├── alembic/
│   └── versions/
│       ├── 001_initial.py      # Initial migration
│       └── 002_add_user_audit.py  # User and audit tables
└── scripts/
    ├── seed_hardware.py        # Seed hardware data
    └── seed_admin.py           # Seed admin user
```

## Configuration

### SQLAdmin Settings

SQLAdmin is configured in `app/admin.py`:

```python
from app.admin import setup_admin

# In main.py lifespan:
setup_admin(app)
```

### Model Views

Three model views are configured:

1. **UserAdmin** — User management
   - Searchable by: username, email, full_name
   - Sortable by: id, username, email, created_at
   - Editable fields: all

2. **HardwareAssetAdmin** — Hardware management
   - Searchable by: name, brand, assigned_to
   - Sortable by: id, name, brand, status
   - Editable fields: all

3. **AuditLogAdmin** — Audit history (read-only)
   - Searchable by: action, table_name, description
   - Sortable by: id, user_id, action, created_at
   - Read-only: cannot create, edit, or delete

## User Management

### Creating Users Programmatically

```python
from app.core.user import create_user
from app.core.database import SessionLocal

db = SessionLocal()
user = create_user(
    db=db,
    username="john.doe",
    email="john@example.com",
    password="secure_password",
    full_name="John Doe",
    is_admin=False
)
print(f"Created user: {user.username}")
```

### Password Hashing

Passwords are hashed using SHA-256 with salt:

```python
from app.core.user import hash_password, verify_password

# Hash a password
hashed = hash_password("my_password")

# Verify a password
is_valid = verify_password("my_password", hashed)
```

### User Utilities

```python
from app.core.user import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    update_user,
    deactivate_user,
    activate_user,
    promote_to_admin,
    demote_from_admin,
    list_users,
)

# Get user
user = get_user_by_username(db, "john.doe")

# Update user
updated = update_user(db, user.id, full_name="John Smith")

# Deactivate user
deactivate_user(db, user.id)

# Promote to admin
promote_to_admin(db, user.id)

# List users
users, total = list_users(db, skip=0, limit=10, is_admin=False)
```

## Audit Logging

### Logging Actions

```python
from app.core.audit import log_audit

log_audit(
    db=db,
    user_id=1,
    action="CREATE",
    table_name="hardware_asset",
    record_id=5,
    new_values={"name": "Dell XPS", "brand": "Dell"},
    description="Created new hardware asset",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)
```

### Retrieving Audit History

```python
from app.core.audit import (
    get_user_audit_history,
    get_table_audit_history,
    get_record_audit_history,
)

# Get all actions by a user
logs, total = get_user_audit_history(db, user_id=1, limit=10)

# Get all changes to a table
logs, total = get_table_audit_history(db, table_name="hardware_asset", limit=10)

# Get all changes to a specific record
logs, total = get_record_audit_history(
    db, 
    table_name="hardware_asset", 
    record_id=5, 
    limit=10
)

for log in logs:
    print(f"{log.action} on {log.table_name} by user {log.user_id}")
    print(f"  Old: {log.old_values}")
    print(f"  New: {log.new_values}")
```

## Security Considerations

### Password Security

- Passwords are hashed with SHA-256 + salt
- Never store plain text passwords
- Use strong passwords (12+ characters)
- Change default admin password immediately

### Audit Logging

- All changes are logged with:
  - User ID
  - Timestamp
  - IP address
  - User agent
  - Old and new values
- Audit logs are read-only in admin panel
- Cannot be edited or deleted

### Access Control

- Implement authentication in production
- Restrict admin panel to admin users only
- Use HTTPS in production
- Implement rate limiting

## Troubleshooting

### Admin Panel Not Loading

```bash
# Check backend is running
curl http://localhost:8000/health

# Check SQLAdmin is installed
pip list | grep sqladmin

# Check migrations are applied
alembic current
```

### Cannot Create Users

```bash
# Check User table exists
sqlite3 rental_shop.db ".tables"

# Check migrations
alembic history

# Apply migrations if needed
alembic upgrade head
```

### Audit Logs Not Appearing

```bash
# Check AuditLog table exists
sqlite3 rental_shop.db ".schema audit_log"

# Check audit logging is called in code
grep -r "log_audit" backend/app/
```

### Password Issues

```python
# Reset password
from app.core.user import hash_password, update_user

new_hash = hash_password("new_password")
update_user(db, user_id=1, password_hash=new_hash)
```

## Next Steps

1. **Create Users** — Use admin panel to create user accounts
2. **Manage Hardware** — Add and update hardware assets
3. **Review Audit Logs** — Monitor user actions
4. **Implement Authentication** — Restrict admin access in production
5. **Customize** — Modify admin panel views as needed

## Production Deployment

### Before Deploying

1. Change default admin password
2. Implement authentication
3. Restrict admin panel to admin users
4. Enable HTTPS
5. Set up regular backups
6. Monitor audit logs

### Security Checklist

- [ ] Change default admin password
- [ ] Implement authentication
- [ ] Restrict admin access
- [ ] Enable HTTPS
- [ ] Set up backups
- [ ] Monitor audit logs
- [ ] Review user list
- [ ] Deactivate unused accounts

## Support

For issues or questions:
1. Check [SQLADMIN_GUIDE.md](SQLADMIN_GUIDE.md)
2. Review backend logs
3. Verify database migrations
4. Check user and audit tables
