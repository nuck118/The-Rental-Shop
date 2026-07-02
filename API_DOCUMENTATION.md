# API Documentation

Complete API documentation is available via **Swagger UI** at `http://localhost:8000/docs` when the backend is running.

## Overview

The Rental Shop API provides endpoints for:
- **Hardware Management** — CRUD operations on hardware assets
- **AI Chatbot** — Device recommendations using natural language
- **System Health** — Service status and diagnostics

## Base URL

```
http://localhost:8000
```

## Authentication

### Public Endpoints
No authentication required:
- `GET /health`
- `GET /docs`
- `GET /openapi.json`
- `GET /redoc`

### Protected Endpoints
All other endpoints require Bearer token authentication:

```
Authorization: Bearer <token>
```

**Note:** For development, you can disable JWT in `.env`:
```
JWT_ENABLED=false
```

## Rate Limiting

All endpoints are rate-limited:
- **Default**: 100 requests per 60 seconds
- **Tracking**: Per Bearer token or per IP address
- **Response**: 429 Too Many Requests when exceeded

Configure in `.env`:
```
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
```

## CORS

Cross-Origin Resource Sharing is enabled for configured origins:

```
CORS_ORIGINS=["http://localhost:5173", "https://app.example.com"]
```

**Allowed Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS

## Hardware Management API

### List Hardware Assets

**Endpoint:** `GET /api/hardware`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip |
| `limit` | integer | 10 | Maximum records to return (max: 100) |
| `status` | string | null | Filter by status (Available, In Use, Repair, Unknown) |

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "name": "Apple iPhone 13 Pro Max",
    "brand": "Apple",
    "purchase_date": "2021-11-23",
    "status": "Available",
    "assigned_to": null,
    "notes": null
  },
  {
    "id": 2,
    "name": "Apple MacBook Pro 13",
    "brand": "Apple",
    "purchase_date": "2021-12-20",
    "status": "In Use",
    "assigned_to": "john.doe@example.com",
    "notes": null
  }
]
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/hardware?skip=0&limit=10&status=Available" \
  -H "Authorization: Bearer <token>"
```

---

### Get Hardware Asset by ID

**Endpoint:** `GET /api/hardware/{hardware_id}`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hardware_id` | integer | The ID of the hardware asset |

**Response:** 200 OK
```json
{
  "id": 1,
  "name": "Apple iPhone 13 Pro Max",
  "brand": "Apple",
  "purchase_date": "2021-11-23",
  "status": "Available",
  "assigned_to": null,
  "notes": null
}
```

**Error Responses:**
- `404 Not Found` — Hardware asset not found

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>"
```

---

### Create Hardware Asset

**Endpoint:** `POST /api/hardware`

**Request Body:**
| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `name` | string | Yes | 255 | Device name/model |
| `brand` | string | Yes | 100 | Manufacturer brand |
| `status` | string | Yes | 50 | Current status |
| `purchase_date` | string | No | - | Purchase date (YYYY-MM-DD) |
| `assigned_to` | string | No | 255 | Assigned user |
| `notes` | string | No | - | Additional notes |

**Response:** 201 Created
```json
{
  "id": 12,
  "name": "Dell XPS 15",
  "brand": "Dell",
  "purchase_date": "2023-01-15",
  "status": "Available",
  "assigned_to": null,
  "notes": "High-performance laptop"
}
```

**Error Responses:**
- `400 Bad Request` — Invalid request data or date format

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dell XPS 15",
    "brand": "Dell",
    "status": "Available",
    "purchase_date": "2023-01-15",
    "notes": "High-performance laptop"
  }'
```

---

### Update Hardware Asset

**Endpoint:** `PUT /api/hardware/{hardware_id}`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hardware_id` | integer | The ID of the hardware asset |

**Request Body:**
All fields are optional. Only provided fields will be updated.

| Field | Type | Max Length | Description |
|-------|------|-----------|-------------|
| `name` | string | 255 | Device name/model |
| `brand` | string | 100 | Manufacturer brand |
| `status` | string | 50 | Current status |
| `purchase_date` | string | - | Purchase date (YYYY-MM-DD) |
| `assigned_to` | string | 255 | Assigned user |
| `notes` | string | - | Additional notes |

**Response:** 200 OK
```json
{
  "id": 1,
  "name": "Apple iPhone 13 Pro Max",
  "brand": "Apple",
  "purchase_date": "2021-11-23",
  "status": "In Use",
  "assigned_to": "john.doe@example.com",
  "notes": "Assigned to John Doe"
}
```

**Error Responses:**
- `404 Not Found` — Hardware asset not found
- `400 Bad Request` — Invalid request data

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "In Use",
    "assigned_to": "john.doe@example.com"
  }'
```

---

### Delete Hardware Asset

**Endpoint:** `DELETE /api/hardware/{hardware_id}`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `hardware_id` | integer | The ID of the hardware asset |

**Response:** 200 OK
```json
{
  "message": "Hardware asset with ID 1 deleted successfully"
}
```

**Error Responses:**
- `404 Not Found` — Hardware asset not found

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>"
```

---

## AI Chatbot API

### Chat with Assistant

**Endpoint:** `POST /api/ai/chat`

**Request Body:**
| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `message` | string | Yes | 2000 | Natural language request |
| `conversation_history` | array | No | - | Previous messages for context |

**Conversation History Format:**
```json
[
  {
    "role": "user",
    "content": "I need a laptop"
  },
  {
    "role": "assistant",
    "content": "I can help you find a laptop..."
  }
]
```

**Response:** 200 OK
```json
{
  "message": "Great! For software development, I'd recommend the MacBook Pro 13. It has excellent performance for coding tasks...",
  "recommendations": [
    {
      "id": 2,
      "name": "Apple MacBook Pro 13",
      "brand": "Apple",
      "status": "Available",
      "reason": "Powerful performance for development and productivity"
    }
  ],
  "conversation_context": "I need a laptop for software development"
}
```

**Error Responses:**
- `401 Unauthorized` — API credentials not configured
- `429 Too Many Requests` — API rate limit exceeded
- `504 Gateway Timeout` — API request timed out
- `500 Internal Server Error` — Other API errors

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a laptop for software development",
    "conversation_history": []
  }'
```

---

### Check AI Service Health

**Endpoint:** `GET /api/ai/health`

**Response:** 200 OK
```json
{
  "status": "healthy",
  "model": "gemini-2.5-flash",
  "message": "AI chatbot service is ready"
}
```

**Error Responses:**
- `401 Unauthorized` — API credentials not configured

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/ai/health"
```

---

## System Health API

### Health Check

**Endpoint:** `GET /health`

**Response:** 200 OK
```json
{
  "status": "healthy"
}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

---

## Error Handling

All endpoints return standard HTTP status codes and error messages:

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | CSRF token invalid |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 504 | Gateway Timeout | AI service timeout |

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Security Headers

All responses include security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | nosniff | Prevent MIME type sniffing |
| `X-Frame-Options` | DENY | Prevent clickjacking |
| `X-XSS-Protection` | 1; mode=block | Enable XSS filter |
| `Strict-Transport-Security` | max-age=31536000 | Enforce HTTPS |
| `Content-Security-Policy` | default-src 'self' | Restrict resource loading |

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `skip` — Number of records to skip (default: 0)
- `limit` — Maximum records to return (default: 10, max: 100)

**Example:**
```bash
# Get records 20-30
curl -X GET "http://localhost:8000/api/hardware?skip=20&limit=10"
```

---

## Filtering

List endpoints support filtering:

**Query Parameters:**
- `status` — Filter by status (Available, In Use, Repair, Unknown)

**Example:**
```bash
# Get only available devices
curl -X GET "http://localhost:8000/api/hardware?status=Available"
```

---

## Date Format

All dates use ISO 8601 format: `YYYY-MM-DD`

**Examples:**
- `2023-01-15` — January 15, 2023
- `2021-11-23` — November 23, 2021

---

## Testing with cURL

### List all hardware
```bash
curl -X GET "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>"
```

### Get specific hardware
```bash
curl -X GET "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>"
```

### Create hardware
```bash
curl -X POST "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dell XPS 15",
    "brand": "Dell",
    "status": "Available",
    "purchase_date": "2023-01-15"
  }'
```

### Update hardware
```bash
curl -X PUT "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "In Use"}'
```

### Delete hardware
```bash
curl -X DELETE "http://localhost:8000/api/hardware/1" \
  -H "Authorization: Bearer <token>"
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a laptop for software development",
    "conversation_history": []
  }'
```

---

## Interactive Documentation

### Swagger UI
Access the interactive API documentation at:
```
http://localhost:8000/docs
```

Features:
- Try out endpoints directly
- View request/response schemas
- See example values
- Test with different parameters

### ReDoc
Alternative documentation view at:
```
http://localhost:8000/redoc
```

### OpenAPI Schema
Machine-readable API specification at:
```
http://localhost:8000/openapi.json
```

---

## Rate Limit Headers

Responses include rate limit information:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

---

## Changelog

### Version 1.0.0
- Initial API release
- Hardware management endpoints
- AI chatbot integration
- Rate limiting and security middleware
- Comprehensive documentation
