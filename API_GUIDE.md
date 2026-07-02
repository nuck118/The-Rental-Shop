# API Documentation Guide

## Quick Access

Once the backend is running at `http://localhost:8000`, access the API documentation through:

### 1. Swagger UI (Interactive)
**URL:** http://localhost:8000/docs

**Features:**
- Interactive endpoint testing
- Request/response examples
- Parameter validation
- Try-it-out functionality
- Schema visualization

### 2. ReDoc (Alternative View)
**URL:** http://localhost:8000/redoc

**Features:**
- Clean, organized documentation
- Search functionality
- Responsive design
- Better for reading

### 3. OpenAPI Schema (Machine-Readable)
**URL:** http://localhost:8000/openapi.json

**Use Cases:**
- API client generation
- Documentation automation
- Integration with third-party tools

## Documentation Files

### API_DOCUMENTATION.md
Comprehensive API reference with:
- All endpoints documented
- Request/response examples
- Error handling
- Authentication details
- Rate limiting information
- cURL examples
- Security headers

### README.md
Quick reference with:
- Stack information
- Setup instructions
- Migration notes
- API overview
- Security features

## Endpoints Overview

### Hardware Management
- `GET /api/hardware` — List all hardware
- `GET /api/hardware/{id}` — Get specific hardware
- `POST /api/hardware` — Create hardware
- `PUT /api/hardware/{id}` — Update hardware
- `DELETE /api/hardware/{id}` — Delete hardware

### AI Chatbot
- `POST /api/ai/chat` — Get device recommendations
- `GET /api/ai/health` — Check AI service health

### System
- `GET /health` — System health check
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc
- `GET /openapi.json` — OpenAPI schema

## Testing Endpoints

### Using Swagger UI
1. Open http://localhost:8000/docs
2. Click on an endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"
6. View response

### Using cURL

**List hardware:**
```bash
curl -X GET "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>"
```

**Get specific hardware:**
```bash
curl -X GET "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>"
```

**Create hardware:**
```bash
curl -X POST "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dell XPS 15",
    "brand": "Dell",
    "status": "Available"
  }'
```

**Chat with AI:**
```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a laptop for development",
    "conversation_history": []
  }'
```

### Using Python Requests

```python
import requests

# List hardware
response = requests.get(
    "http://localhost:8000/api/hardware",
    headers={"Authorization": "Bearer <token>"}
)
print(response.json())

# Create hardware
response = requests.post(
    "http://localhost:8000/api/hardware",
    headers={"Authorization": "Bearer <token>"},
    json={
        "name": "Dell XPS 15",
        "brand": "Dell",
        "status": "Available"
    }
)
print(response.json())

# Chat with AI
response = requests.post(
    "http://localhost:8000/api/ai/chat",
    json={
        "message": "I need a laptop for development",
        "conversation_history": []
    }
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// List hardware
fetch('http://localhost:8000/api/hardware', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <token>'
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Create hardware
fetch('http://localhost:8000/api/hardware', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Dell XPS 15',
    brand: 'Dell',
    status: 'Available'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Chat with AI
fetch('http://localhost:8000/api/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'I need a laptop for development',
    conversation_history: []
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Authentication

### Development (JWT Disabled)
If `JWT_ENABLED=false` in `.env`, no authentication is required:

```bash
curl -X GET "http://localhost:8000/api/hardware"
```

### Production (JWT Enabled)
All protected endpoints require Bearer token:

```bash
curl -X GET "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <your-token>"
```

## Rate Limiting

Default limits:
- **100 requests per 60 seconds**
- Tracked per Bearer token or IP address
- Returns `429 Too Many Requests` when exceeded

Check rate limit status in response headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

## Error Handling

All errors follow standard HTTP status codes:

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid data |
| 401 | Unauthorized | Missing auth |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Common Issues

### 401 Unauthorized
**Problem:** Missing or invalid authentication token

**Solution:**
- Check if JWT is enabled: `JWT_ENABLED=true` in `.env`
- If enabled, provide valid Bearer token
- If disabled, remove Authorization header

### 429 Too Many Requests
**Problem:** Rate limit exceeded

**Solution:**
- Wait for the rate limit window to reset
- Check `X-RateLimit-Reset` header for reset time
- Increase `RATE_LIMIT_MAX_REQUESTS` in `.env` if needed

### 404 Not Found
**Problem:** Resource doesn't exist

**Solution:**
- Verify the resource ID is correct
- Check if the resource was deleted
- List all resources to find the correct ID

### 500 Internal Server Error
**Problem:** Server error

**Solution:**
- Check backend logs for error details
- Verify database is running
- Restart the backend server

## API Client Generation

### Using OpenAPI Generator

Generate client libraries from the OpenAPI schema:

```bash
# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./python-client

# Generate JavaScript client
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g javascript \
  -o ./js-client
```

## Security Notes

### No Secrets in Documentation
- API documentation does not include any secrets
- Bearer tokens are placeholders (`<token>`)
- API keys are not exposed in responses
- All sensitive data is server-side only

### HTTPS in Production
- Use HTTPS in production
- HSTS header enforces secure transport
- CSP header restricts resource loading
- X-Frame-Options prevents clickjacking

## Support

For issues or questions:
1. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed reference
2. Review error messages in response
3. Check backend logs for debugging
4. Verify `.env` configuration

## Next Steps

1. **Explore Swagger UI** — http://localhost:8000/docs
2. **Test endpoints** — Use "Try it out" feature
3. **Read API_DOCUMENTATION.md** — Detailed reference
4. **Build frontend** — Integrate with Vue.js app
5. **Deploy** — Follow production guidelines
