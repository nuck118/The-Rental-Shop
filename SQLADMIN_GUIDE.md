# SQLAdmin Documentation

## Overview

SQLAdmin is an integrated admin panel for The Rental Shop that provides:

- **User Management** — Create, edit, and manage user accounts
- **Hardware Management** — CRUD operations on hardware assets
- **Audit History** — Track all changes made by each user

## Access

**URL:** http://localhost:8000/admin

The admin panel is accessible to all users. In production, implement authentication to restrict access to admin users only.

## Features

### 1. User Management Tab

The User Management tab allows admins to create and manage user accounts.

#### Creating a New User

1. Navigate to http://localhost:8000/admin
2. Click on **Users** in the left sidebar
3. Click **Create** button
4. Fill in the following fields:
   - **Username** — Unique username (required)
   - **Email** — Unique email address (required)
   - **Full Name** — User's full name (optional)
   - **Password Hash** — Hashed password (required)
   - **Is Active** — Whether user can access the system (default: true)
   - **Is Admin** — Whether user has admin privileges (default: false)
5. Click **Save**

#### User Fields

| Field | Type | Description |
|-------|------|-------------|
| ID | Integer | Auto-generated user ID |
| Username | String | Unique username for login |
| Email | String | Unique email address |
| Full Name | String | User's full name |
| Password Hash | String | Hashed password (SHA-256 with salt) |
| Is Active | Boolean | Whether user is active |
| Is Admin | Boolean | Whether user has admin privileges |
| Created At | DateTime | Account creation timestamp |
| Updated At | DateTime | Last update timestamp |

#### User List View

The user list shows:
- **ID** — User ID
- **Username** — Username
- **Email** — Email address
- **Full Name** — Full name
- **Is Active** — ✓ Active or ✗ Inactive
- **Is Admin** — ✓ Admin or ✗ User
- **Created At** — Account creation date

#### Searching Users

Use the search box to find users by:
- Username
- Email
- Full Name

#### Sorting Users

Click column headers to sort by:
- ID
- Username
- Email
- Created At

#### Editing Users

1. Click on a user in the list
2. Modify the fields
3. Click **Save**

#### Deactivating Users

1. Click on a user
2. Set **Is Active** to false
3. Click **Save**

The user will no longer be able to access the system.

### 2. Hardware Management Tab

The Hardware Management tab allows admins to manage hardware assets.

#### Creating Hardware

1. Navigate to http://localhost:8000/admin
2. Click on **Hardware Assets** in the left sidebar
3. Click **Create** button
4. Fill in the following fields:
   - **Name** — Device name/model (required)
   - **Brand** — Manufacturer brand (required)
   - **Purchase Date** — Date of purchase (optional)
   - **Status** — Current status (required)
   - **Assigned To** — User assigned to device (optional)
   - **Notes** — Additional notes (optional)
5. Click **Save**

#### Hardware Fields

| Field | Type | Description |
|-------|------|-------------|
| ID | Integer | Auto-generated hardware ID |
| Name | String | Device name/model |
| Brand | String | Manufacturer brand |
| Purchase Date | Date | Date of purchase |
| Status | String | Current status (Available, In Use, Repair, Unknown) |
| Assigned To | String | User assigned to device |
| Notes | Text | Additional notes |

#### Hardware List View

The hardware list shows:
- **ID** — Hardware ID
- **Name** — Device name
- **Brand** — Manufacturer
- **Status** — Current status (color-coded)
- **Assigned To** — Assigned user

#### Searching Hardware

Use the search box to find hardware by:
- Name
- Brand
- Assigned To

#### Sorting Hardware

Click column headers to sort by:
- ID
- Name
- Brand
- Status

#### Editing Hardware

1. Click on a hardware item
2. Modify the fields
3. Click **Save**

Changes are automatically logged in the Audit Log.

#### Deleting Hardware

1. Click on a hardware item
2. Click **Delete** button
3. Confirm deletion

The deletion is logged in the Audit Log.

#### Status Management

Update hardware status:
- **Available** — Device is available for use
- **In Use** — Device is currently assigned
- **Repair** — Device is in repair
- **Unknown** — Status is unknown

### 3. Audit History Tab

The Audit History tab shows all changes made by users.

#### Audit Log Fields

| Field | Type | Description |
|-------|------|-------------|
| ID | Integer | Audit log entry ID |
| User ID | Integer | ID of user who made the change |
| Action | String | Type of action (CREATE, UPDATE, DELETE) |
| Table Name | String | Name of affected table |
| Record ID | Integer | ID of affected record |
| Old Values | JSON | Previous values (for UPDATE/DELETE) |
| New Values | JSON | New values (for CREATE/UPDATE) |
| Description | Text | Human-readable description |
| IP Address | String | User's IP address |
| User Agent | String | Browser/client information |
| Created At | DateTime | Timestamp of action |

#### Audit Log List View

The audit log shows:
- **ID** — Log entry ID
- **User ID** — User who made the change
- **Action** — Type of action (color-coded)
- **Table Name** — Affected table
- **Record ID** — Affected record
- **Created At** — Timestamp

#### Searching Audit Logs

Use the search box to find logs by:
- Action (CREATE, UPDATE, DELETE)
- Table Name
- Description

#### Sorting Audit Logs

Click column headers to sort by:
- ID
- User ID
- Action
- Created At

#### Viewing Audit Details

Click on an audit log entry to see:
- **Old Values** — Previous values (JSON)
- **New Values** — New values (JSON)
- **Description** — Human-readable description
- **IP Address** — User's IP address
- **User Agent** — Browser information

#### Audit Log Features

- **Read-Only** — Audit logs cannot be edited or deleted
- **Exportable** — Export audit logs to CSV
- **Searchable** — Search by action, table, or description
- **Sortable** — Sort by any column

#### Tracking User Actions

View all actions by a specific user:
1. Search for the user ID in the audit log
2. All actions by that user are displayed
3. Click on each entry to see details

#### Tracking Table Changes

View all changes to a specific table:
1. Search for the table name (e.g., "hardware_asset", "user")
2. All changes to that table are displayed
3. Click on each entry to see details

#### Tracking Record Changes

View all changes to a specific record:
1. Search for the table name and record ID
2. All changes to that record are displayed
3. Click on each entry to see details

## User Workflow

### Admin Creates User

1. Admin logs into SQLAdmin
2. Navigates to Users tab
3. Clicks Create
4. Fills in user details
5. Clicks Save
6. User is created and logged in audit log

### User Accesses System

1. User receives credentials from admin
2. User logs in with username/password
3. User can access API endpoints
4. All user actions are logged in audit log

### Admin Reviews Audit History

1. Admin navigates to Audit History tab
2. Searches for specific user or action
3. Reviews changes made
4. Exports audit log if needed

## Security Considerations

### Password Security

- Passwords are hashed using SHA-256 with salt
- Never store plain text passwords
- Use strong passwords (12+ characters recommended)

### Audit Logging

- All changes are logged with:
  - User ID
  - Timestamp
  - IP address
  - User agent
  - Old and new values

### Access Control

- Implement authentication to restrict admin access
- Only admins should be able to create users
- Regular users cannot access SQLAdmin

## API Integration

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
```

### Logging Audit Entries

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
    ip_address="192.168.1.1"
)
```

### Retrieving Audit History

```python
from app.core.audit import get_user_audit_history

logs, total = get_user_audit_history(db, user_id=1, limit=10)
for log in logs:
    print(f"{log.action} on {log.table_name} at {log.created_at}")
```

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
```

## Troubleshooting

### Admin Panel Not Loading

1. Ensure backend is running: `uvicorn app.main:app --reload`
2. Check that SQLAdmin is installed: `pip install sqladmin`
3. Verify database migrations are applied: `alembic upgrade head`

### Cannot Create Users

1. Check that User table exists: `alembic upgrade head`
2. Verify username is unique
3. Verify email is unique
4. Check backend logs for errors

### Audit Logs Not Appearing

1. Ensure AuditLog table exists: `alembic upgrade head`
2. Verify user_id is valid
3. Check that actions are being logged in code
4. Review backend logs

### Password Issues

1. Passwords are hashed with SHA-256 + salt
2. Never store plain text passwords
3. Use strong passwords
4. Reset password by updating password_hash field

## Best Practices

### User Management

- ✅ Create users with strong passwords
- ✅ Deactivate unused accounts
- ✅ Regularly review user list
- ✅ Promote only trusted users to admin
- ❌ Don't share admin credentials
- ❌ Don't store passwords in plain text

### Hardware Management

- ✅ Keep hardware status updated
- ✅ Assign hardware to users
- ✅ Add notes for maintenance issues
- ✅ Regularly review hardware list
- ❌ Don't delete hardware without backup
- ❌ Don't modify purchase dates without reason

### Audit Logging

- ✅ Review audit logs regularly
- ✅ Export logs for backup
- ✅ Monitor for suspicious activity
- ✅ Track all user actions
- ❌ Don't delete audit logs
- ❌ Don't modify audit logs

## Next Steps

1. **Create Admin User** — Create first admin account
2. **Create Regular Users** — Add users for the system
3. **Manage Hardware** — Add and manage hardware assets
4. **Monitor Audit Logs** — Review user actions
5. **Implement Authentication** — Restrict admin access in production

## Support

For issues or questions:
1. Check backend logs
2. Verify database migrations
3. Review SQLAdmin documentation
4. Check user and audit log tables
