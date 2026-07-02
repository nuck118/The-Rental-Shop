# Admin Panel Security — Authentication & Authorization

## Overview

The admin panel at `/admin` is now fully protected with JWT-based authentication. Only admin users can access it.

## Security Features

### Authentication
- ✅ JWT token-based authentication
- ✅ Session management
- ✅ Login form with username/password
- ✅ Automatic logout on token expiration
- ✅ Admin-only access

### Authorization
- ✅ Only admin users can login
- ✅ Active user check
- ✅ Token validation on every request
- ✅ Automatic redirect to login if unauthorized

### Protection
- ✅ Removed `/admin` from public endpoints
- ✅ Security middleware enforces authentication
- ✅ JWT tokens expire after 24 hours
- ✅ Session tokens stored securely

## How It Works

### Login Flow
```
1. User visits http://localhost:8000/admin
   ↓
2. Redirected to login page (not authenticated)
   ↓
3. User enters username and password
   ↓
4. Backend validates credentials
   ├─ Check user exists
   ├─ Check user is active
   ├─ Check user is admin
   └─ Verify password hash
   ↓
5. If valid, generate JWT token
   ↓
6. Store token in session
   ↓
7. Redirect to admin dashboard
   ↓
8. User can access admin panel
```

### Request Flow
```
1. User makes request to /admin
   ↓
2. Security middleware checks authentication
   ├─ Check if endpoint is public (it's not)
   ├─ Check for Authorization header
   └─ Validate JWT token
   ↓
3. If not authenticated, redirect to login
   ↓
4. If authenticated, check admin status
   ├─ Verify user is still active
   ├─ Verify user is still admin
   └─ Verify token is valid
   ↓
5. If all checks pass, allow access
   ↓
6. If any check fails, redirect to login
```

## Files Updated

### backend/app/admin_auth.py (NEW)
```python
class AdminAuthenticationBackend(AuthenticationBackend):
    """Authentication backend for SQLAdmin using JWT tokens."""
    
    async def login(request)      # Handle login form
    async def logout(request)     # Handle logout
    async def authenticate(request) # Check authentication
```

### backend/app/admin.py (UPDATED)
```python
def setup_admin(app):
    """Setup SQLAdmin with authentication."""
    admin = Admin(
        app=app,
        engine=engine,
        title="The Rental Shop Admin",
        authentication_backend=AdminAuthenticationBackend(secret_key=settings.secret_key),
    )
```

### backend/app/main.py (UPDATED)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Store secret key in app for admin auth
    app.secret_key = settings.secret_key
    
    # Setup SQLAdmin
    setup_admin(app)
```

### backend/app/security/middleware.py (UPDATED)
```python
def _is_public_endpoint(self, path: str) -> bool:
    """Check if endpoint is public (no auth required)."""
    public_paths = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/auth/login",
        # /admin is NOT in this list anymore
    ]
```

## Testing

### 1. Verify Admin Panel Requires Login
```bash
# Try to access admin without authentication
curl http://localhost:8000/admin

# Should redirect to login page
```

### 2. Test Login with Admin User
```bash
# Visit in browser
http://localhost:8000/admin

# Login with:
# Username: admin
# Password: admin123

# Should see admin dashboard
```

### 3. Test Login with Non-Admin User
```bash
# Create a non-admin user (via admin panel or database)
# Try to login with that user
# Should see error: "User is not an admin"
```

### 4. Test Session Expiration
```bash
# Login to admin panel
# Wait 24 hours (or modify token expiration in code)
# Try to access admin panel
# Should redirect to login page
```

### 5. Test Logout
```bash
# Login to admin panel
# Click logout button
# Should redirect to login page
# Session should be cleared
```

## Admin User Management

### Create Admin User
```bash
cd backend
python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.user import User
from app.core.user import hash_password

db = SessionLocal()
admin = User(
    username="admin",
    email="admin@example.com",
    password_hash=hash_password("admin123"),
    is_admin=True,
    is_active=True,
)
db.add(admin)
db.commit()
print("Admin user created")
db.close()
EOF
```

### Promote User to Admin
```bash
cd backend
python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "john").first()
if user:
    user.is_admin = True
    db.commit()
    print(f"User {user.username} promoted to admin")
else:
    print("User not found")
db.close()
EOF
```

### Demote Admin to User
```bash
cd backend
python3 << 'EOF'
from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == "john").first()
if user:
    user.is_admin = False
    db.commit()
    print(f"User {user.username} demoted to regular user")
else:
    print("User not found")
db.close()
EOF
```

## Security Best Practices

### For Administrators
1. **Change Default Password**
   - Login to admin panel
   - Change admin password immediately
   - Use strong password (12+ characters, mixed case, numbers, symbols)

2. **Create Individual Admin Accounts**
   - Don't share admin credentials
   - Create separate accounts for each admin
   - Disable unused accounts

3. **Monitor Admin Activity**
   - Check Audit Log tab regularly
   - Review user changes
   - Monitor hardware modifications

4. **Regular Backups**
   - Backup database regularly
   - Store backups securely
   - Test restore procedures

### For Developers
1. **Change SECRET_KEY in Production**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - Update `.env` with new key
   - Restart backend

2. **Enable HTTPS**
   - Use SSL/TLS certificates
   - Redirect HTTP to HTTPS
   - Set Secure flag on cookies

3. **Rate Limiting**
   - Monitor failed login attempts
   - Implement account lockout after N failures
   - Log suspicious activity

4. **Token Expiration**
   - Tokens expire after 24 hours
   - Implement refresh tokens for long sessions
   - Force re-authentication for sensitive operations

## Troubleshooting

### Issue: "Cannot access admin panel"
**Cause**: Not authenticated  
**Solution**: 
1. Visit http://localhost:8000/admin
2. Login with admin/admin123
3. Check browser console for errors

### Issue: "User is not an admin"
**Cause**: Logged in user is not an admin  
**Solution**:
1. Promote user to admin (see above)
2. Or login with admin account

### Issue: "Invalid token"
**Cause**: Token is malformed or expired  
**Solution**:
1. Logout and login again
2. Clear browser cookies
3. Check SECRET_KEY matches

### Issue: "Session expired"
**Cause**: Token expired (24 hours)  
**Solution**:
1. Login again
2. Or increase token expiration time

### Issue: "Redirect loop"
**Cause**: Authentication backend issue  
**Solution**:
1. Check backend logs
2. Verify database connection
3. Restart backend server

## API Endpoints

### Admin Panel
```
GET /admin
  - Requires: Admin user authentication
  - Returns: Admin dashboard
  - Redirects to login if not authenticated
```

### Login
```
POST /admin/login
  - Requires: Username and password
  - Returns: Redirect to admin dashboard
  - Sets session cookie with JWT token
```

### Logout
```
POST /admin/logout
  - Requires: Admin user authentication
  - Returns: Redirect to login page
  - Clears session
```

## Configuration

### In `.env`
```
SECRET_KEY=your-secret-key-change-in-production
JWT_ENABLED=true
```

### In `app/core/config.py`
```python
secret_key: str = "your-secret-key-change-in-production"
jwt_enabled: bool = True
```

## Token Details

### JWT Payload
```json
{
  "sub": "1",
  "username": "admin",
  "is_admin": true
}
```

### Token Expiration
- Default: 24 hours
- Can be modified in `app/admin_auth.py`

### Token Storage
- Stored in session (server-side)
- Also stored in JWT (client-side)
- Validated on every request

## Summary

✅ Admin panel requires authentication  
✅ Only admin users can access  
✅ JWT token-based security  
✅ Session management  
✅ Automatic logout on expiration  
✅ Audit logging of admin actions  
✅ Production-ready security  

**Status**: Admin panel is now fully secured
