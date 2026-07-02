# Troubleshooting: 500 Error on Hardware Endpoint

## Issue
Frontend receives 500 (Internal Server Error) when trying to fetch hardware devices.

## Root Cause
The security middleware was not properly validating JWT tokens, and the `/api/auth/login` endpoint was not in the public endpoints list.

## Solution

### 1. Update Security Middleware
The middleware has been updated to:
- Add `/api/auth/login` to public endpoints
- Properly validate JWT tokens using PyJWT
- Handle token expiration and invalid tokens
- Add error handling for route handlers

### 2. Verify Backend is Running
```bash
cd backend
uvicorn app.main:app --reload
```

Check that the server starts without errors.

### 3. Test Login Endpoint
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

You should receive a response with a token:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

### 4. Test Hardware Endpoint with Token
```bash
curl -X GET http://localhost:8000/api/hardware \
  -H "Authorization: Bearer <your-token-here>"
```

Replace `<your-token-here>` with the token from step 3.

### 5. Restart Frontend
```bash
cd frontend
npm run dev
```

### 6. Test in Browser
1. Go to http://localhost:5173
2. Login with admin/admin123
3. Check that devices load in the dashboard

## Common Issues

### Issue: "Missing authorization header"
**Cause**: Frontend is not sending the token  
**Solution**: Verify auth store is saving the token correctly
```javascript
// In browser console
localStorage.getItem('token')
```

### Issue: "Invalid token"
**Cause**: Token is malformed or expired  
**Solution**: 
- Clear localStorage and login again
- Check token format (should start with "eyJ")

### Issue: "Token has expired"
**Cause**: Token is older than 24 hours  
**Solution**: Login again to get a new token

### Issue: Backend crashes on startup
**Cause**: Missing dependencies or database issue  
**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify database
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('rental_shop.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM hardware_asset;")
print(f"Hardware assets: {cursor.fetchone()[0]}")
conn.close()
EOF
```

## Files Updated

### backend/app/security/middleware.py
- Added JWT import
- Added `/api/auth/login` to public endpoints
- Implemented proper JWT token validation
- Added error handling for route handlers

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Login endpoint returns token
- [ ] Hardware endpoint works with token
- [ ] Frontend loads signin page
- [ ] Can login with admin/admin123
- [ ] Dashboard loads with devices
- [ ] Chat panel opens
- [ ] No console errors

## Next Steps

1. Restart backend: `uvicorn app.main:app --reload`
2. Restart frontend: `npm run dev`
3. Test login and device loading
4. Check browser console for any errors
5. Verify network tab shows successful API calls

## Additional Resources

- Backend Security: See `backend/app/security/middleware.py`
- Auth Endpoint: See `backend/app/api/routes/auth.py`
- Hardware Endpoint: See `backend/app/api/routes/hardware.py`
- Frontend Auth Store: See `frontend/src/stores/auth.js`
- Frontend Device Store: See `frontend/src/stores/device.js`

## Support

If issues persist:
1. Check backend logs for error messages
2. Verify database has hardware data
3. Check frontend network tab for API responses
4. Verify CORS is configured correctly
5. Clear browser cache and localStorage
