# SQLite Cloud Integration Setup

This document describes the SQLite Cloud integration for The Rental Shop application.

## Overview

The application has been successfully configured to use SQLite Cloud as the database backend. SQLite Cloud provides a managed SQLite database service that allows you to access your database from anywhere.

## Configuration

### Environment Variables

The database connection is configured via the `DATABASE_URL` environment variable in `.env`:

```env
# SQLite Cloud connection
DATABASE_URL=sqlitecloud://host:port/database?apikey=your-sqlitecloud-api-key
```

### Connection String Format

```
sqlitecloud://host:port/database?apikey=your-api-key
```

- **host**: SQLite Cloud server hostname
- **port**: SQLite Cloud server port (default: 8860)
- **database**: Database name
- **apikey**: Your SQLite Cloud API key

## Files Modified

1. **backend/.env** - Updated with SQLite Cloud connection URL
2. **backend/.env.example** - Added SQLite Cloud configuration example
3. **backend/app/core/database.py** - Updated to support SQLite Cloud connections
4. **backend/alembic/env.py** - Updated to use the application's database engine
5. **backend/requirements.txt** - Added sqlitecloud package

## Database Connection Implementation

The database connection uses a custom wrapper class (`SQLiteCloudConnection`) that:

1. Creates connections using the `sqlitecloud` library
2. Wraps the connection to make it compatible with SQLAlchemy
3. Handles unsupported features (like `create_function`) gracefully
4. Supports both SQLite Cloud and local SQLite databases

### Fallback to Local SQLite

The application automatically falls back to local SQLite if the `DATABASE_URL` doesn't start with `sqlitecloud://`:

```python
# Local SQLite connection (fallback)
engine = create_engine(
    f"sqlite:///{settings.database_url}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

## Testing

Two test scripts were created to verify the integration:

### 1. Test SQLite Cloud Connection

```bash
cd backend
.venv/bin/python test_sqlitecloud.py
```

This script tests:
- Basic connection to SQLite Cloud
- Simple query execution
- Listing existing tables

### 2. Test Application Startup

```bash
cd backend
.venv/bin/python test_app_startup.py
```

This script tests:
- Loading application configuration
- Creating database engine
- Importing models
- Database connection
- Session creation
- Table creation/verification

## Current Database State

The SQLite Cloud database currently contains the following tables:
- `_sqliteai_vector` - SQLite AI vector extension table
- `migrations` - Alembic migration tracking
- `access_tokens` - Access token storage
- `hardware_asset` - Hardware asset data
- `data_quarantine` - Quarantined data
- `user` - User accounts
- `audit_log` - Audit logging

## Usage

### Starting the Application

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Migrations

```bash
cd backend
.venv/bin/python -m alembic upgrade head
```

### Switching Back to Local SQLite

To switch back to local SQLite, update `.env`:

```env
DATABASE_URL=rental_shop.db
```

## Benefits of SQLite Cloud

1. **Remote Access**: Access your database from anywhere
2. **Managed Service**: No need to manage database servers
3. **Automatic Backups**: SQLite Cloud handles backups
4. **Scalability**: Easy to scale as your application grows
5. **Collaboration**: Multiple developers can access the same database

## Security Notes

- The API key in `.env` provides full access to your SQLite Cloud database
- Never commit `.env` to version control
- Use environment variables in production
- Consider using different databases for development and production

## Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Verify the API key is correct
2. Check that the host and port are correct
3. Ensure your network allows outbound connections to SQLite Cloud
4. Check SQLite Cloud status at https://sqlitecloud.io/

### Feature Limitations

SQLite Cloud doesn't support all SQLite features:
- `create_function()` is not supported
- Some custom functions may not work
- Check SQLite Cloud documentation for limitations

## References

- SQLite Cloud Documentation: https://docs.sqlitecloud.io/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Project README: ../README.md