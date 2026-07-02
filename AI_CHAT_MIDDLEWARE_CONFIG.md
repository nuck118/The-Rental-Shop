# AI Chat Service — Middleware Configuration

## Overview

The AI chat service endpoints have been added to the allowed services group in the security middleware. This allows the chat functionality to work properly while maintaining security.

## Allowed Endpoints

### Public Endpoints (No Authentication Required)
```
/health                    - System health check
/docs                      - Swagger UI documentation
/openapi.json             - OpenAPI schema
/redoc                    - ReDoc documentation
/api/auth/login           - User login
/api/ai/health            - AI service health check
```

### Protected Endpoints (Authentication Required)
```
/api/hardware             - Hardware management
/api/ai/chat              - AI chat (requires Bearer token)
/admin                    - Admin panel (requires admin login)
```

## AI Chat Endpoints

### GET /api/ai/health
**Purpose**: Check if AI service is ready  
**Authentication**: Not required  
**Response**:
```json
{
  "status": "healthy",
  "model": "gemini-2.5-flash",
  "message": "AI chatbot service is ready"
}
```

### POST /api/ai/chat
**Purpose**: Send message to AI assistant  
**Authentication**: Required (Bearer token)  
**Request**:
```json
{
  "message": "I need a laptop for software development",
  "conversation_history": []
}
```

**Response**:
```json
{
  "message": "Great! For software development, I'd recommend...",
  "recommendations": [
    {
      "id": 2,
      "name": "Apple MacBook Pro 13",
      "brand": "Apple",
      "status": "Available",
      "reason": "Powerful performance for development"
    }
  ],
  "conversation_context": "I need a laptop for software development"
}
```

## Middleware Configuration

### File: `backend/app/security/middleware.py`

**Public Endpoints List**:
```python
def _is_public_endpoint(self, path: str) -> bool:
    """Check if endpoint is public (no auth required)."""
    public_paths = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/auth/login",
        "/api/ai/health",  # ← AI health check (public)
    ]
    return any(path.startswith(p) for p in public_paths)
```

**Protected Endpoints**:
- `/api/ai/chat` — Requires Bearer token
- `/api/hardware` — Requires Bearer token
- `/admin` — Requires admin login

## How It Works

### Chat Request Flow
```
1. Frontend sends POST /api/ai/chat
   ├─ Includes Authorization: Bearer <token>
   └─ Includes message and conversation history
   ↓
2. Security middleware checks:
   ├─ Rate limit (100 req/60s)
   ├─ JWT token validation
   └─ Token expiration
   ↓
3. If valid, route handler processes request
   ├─ Queries available devices
   ├─ Calls Gemini API
   └─ Returns recommendations
   ↓
4. Response sent to frontend
   ├─ Message from AI
   ├─ Device recommendations
   └─ Conversation context
```

### Health Check Flow
```
1. Frontend sends GET /api/ai/health
   ├─ No authentication required
   └─ No Bearer token needed
   ↓
2. Security middleware checks:
   ├─ Rate limit (100 req/60s)
   └─ Endpoint is public (no auth check)
   ↓
3. Route handler returns status
   ├─ Service status
   ├─ Model name
   └─ Ready message
   ↓
4. Response sent to frontend
```

## Testing

### 1. Test Health Check (No Auth Required)
```bash
curl http://localhost:8000/api/ai/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "model": "gemini-2.5-flash",
  "message": "AI chatbot service is ready"
}
```

### 2. Test Chat Without Token (Should Fail)
```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I need a laptop","conversation_history":[]}'
```

**Expected Response**:
```json
{
  "detail": "Missing authorization header"
}
```

### 3. Test Chat With Token (Should Work)
```bash
# First, get a token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# Then use it for chat
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message":"I need a laptop","conversation_history":[]}'
```

**Expected Response**:
```json
{
  "message": "Great! For software development, I'd recommend...",
  "recommendations": [...],
  "conversation_context": "I need a laptop"
}
```

## Frontend Integration

### Using Chat in Frontend
```javascript
// In ChatAssistant.vue or chat store
const response = await fetch("/api/ai/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,  // ← Token required
  },
  body: JSON.stringify({
    message: userMessage,
    conversation_history: conversationHistory,
  }),
});
```

### Using Health Check
```javascript
// Check if AI service is ready
const response = await fetch("/api/ai/health");
const data = await response.json();
console.log(data.status);  // "healthy"
```

## Security Considerations

### Why Health Check is Public
- Allows frontend to verify AI service is ready
- No sensitive data exposed
- Helps with debugging and monitoring
- Improves user experience

### Why Chat Requires Authentication
- Prevents unauthorized access
- Tracks usage per user
- Enables audit logging
- Protects API quota

### Rate Limiting
- All endpoints (public and protected) are rate limited
- 100 requests per 60 seconds per IP/token
- Prevents abuse and API quota exhaustion

## Configuration

### In `.env`
```
GEMINI_API_KEY=your-api-key
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
JWT_ENABLED=true
```

### In `app/core/config.py`
```python
rate_limit_window: int = 60
rate_limit_max_requests: int = 100
jwt_enabled: bool = True
```

## Troubleshooting

### Issue: "Missing authorization header" on chat
**Cause**: Token not being sent  
**Solution**:
1. Verify user is logged in
2. Check token is stored in localStorage
3. Verify Authorization header is included
4. Check token format: `Bearer <token>`

### Issue: "Invalid token" on chat
**Cause**: Token is invalid or expired  
**Solution**:
1. Login again to get new token
2. Check token hasn't expired (24 hours)
3. Verify SECRET_KEY matches

### Issue: Health check returns error
**Cause**: AI service not configured  
**Solution**:
1. Verify GEMINI_API_KEY is set in .env
2. Check API key is valid
3. Verify internet connection
4. Check Gemini API quota

### Issue: Chat returns 429 (Too Many Requests)
**Cause**: Rate limit exceeded  
**Solution**:
1. Wait 60 seconds
2. Reduce request frequency
3. Increase rate limit in .env (if needed)

## Monitoring

### Check AI Service Status
```bash
curl http://localhost:8000/api/ai/health
```

### Monitor Rate Limiting
- Check response headers for rate limit info
- Monitor 429 responses
- Track request frequency per user

### Monitor Chat Usage
- Check audit logs for chat requests
- Track conversation patterns
- Monitor API quota usage

## Production Deployment

### Before Deploying
1. Verify GEMINI_API_KEY is set
2. Test health check endpoint
3. Test chat with valid token
4. Monitor rate limiting
5. Set up error logging

### Monitoring in Production
1. Monitor health check responses
2. Track 401/403 errors
3. Monitor 429 rate limit errors
4. Track API quota usage
5. Set up alerts for failures

## Summary

✅ AI chat endpoints configured  
✅ Health check is public (no auth)  
✅ Chat requires authentication  
✅ Rate limiting applied to all endpoints  
✅ Security middleware properly configured  
✅ Frontend can access chat service  

**Status**: AI chat service is properly configured and accessible
