# The-Rental-Shop
An async-native, AI-driven Hardware Rental Hub built to orchestrate corporate equipment workflows. The platform leverages an advanced asynchronous backend architecture paired with an immediate, optimistic user interface to manage asset life cycles, enforce atomic concurrency guardrails, and execute semantic inventory discovery.

## Stack
- **Backend** — FastAPI (async ASGI), SQLAlchemy ORM + SQLite, Alembic migrations
- **AI** — Google GenAI SDK (`gemini-2.5-flash`)
- **Frontend** — Vue 3 (Vite, Composition API), Pinia, Vue Router, Tailwind CSS, Preline

## Migration Note

This project previously used **Piccolo ORM** but was migrated to **SQLAlchemy + Alembic** due to Piccolo's lack of auto-migration support. SQLAlchemy + Alembic provides:

- **Automatic migration generation** — Alembic detects model changes and generates migration files automatically
- **Version control** — All schema changes are tracked and reversible
- **Production-ready** — Industry-standard tool used by Django, Flask, and major projects
- **Better ecosystem** — Larger community and more extensions

For detailed migration information, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

---

## Prerequisites
- Python 3.11+
- Node.js 18+
- A [Google AI Studio](https://aistudio.google.com/) API key

---

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template and fill in your API key:

```bash
cp .env.example .env
```

`.env` values:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLite file path | `rental_shop.db` |
| `GEMINI_API_KEY` | Google AI Studio key | — |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `CORS_ORIGINS` | Allowed frontend origins (auto-includes Vercel preview URLs) | Dynamic (see config) |
| `SECRET_KEY` | HMAC secret for CSRF/JWT | Auto-generated random key per session |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per window | `100` |
| `CSRF_ENABLED` | Enable CSRF protection | `false` (disabled for demo) |
| `JWT_ENABLED` | Enable JWT/session verification | `false` (disabled for demo) |
| `ENVIRONMENT` | Runtime environment (`production` or `development`) | — |
| `VERCEL_URL` | Auto-set by Vercel for preview deployment CORS | — |

Run database migrations:

```bash
# Create initial migration for HardwareAsset table
alembic revision --autogenerate -m "Add HardwareAsset table"

# Apply the migration to create the database schema
alembic upgrade head
```

Seed the database with sample data:

```bash
python scripts/seed_hardware.py
```

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.  
The admin panel is available at `http://localhost:8000/admin`.

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The app is available at `http://localhost:5173`.  
All `/api` and `/admin` requests are proxied to the backend automatically.

---

## Admin Panel (SQLAdmin)

The admin panel at **http://localhost:8000/admin** provides five main sections:

### User Management
- Create new user accounts
- Edit user details
- Activate/deactivate users
- Promote users to admin
- Search and filter users

### Hardware Management
- Create, read, update, delete hardware assets
- Manage hardware status (Available, In Use, Repair, Unknown)
- Assign hardware to users
- Add maintenance notes
- Search and filter hardware
- Boolean filter for repair-flagged devices

### Return Records
- View all device return history
- See return condition (perfect, damaged, other) with color-coded badges
- View descriptions for non-perfect returns
- Filter by condition or returned-by user
- Export return records

### Audit History
- View all changes made by users
- Track user actions (CREATE, UPDATE, DELETE)
- See old and new values for changes
- Filter by user, action, or table
- Export audit logs

### Data Quarantine
- View records that failed validation during import
- Inspect raw input data and validation errors
- Filter by severity (critical/warning) or source
- Mark quarantined records as resolved
- Export quarantine entries

For detailed admin panel documentation, see [SQLADMIN_GUIDE.md](SQLADMIN_GUIDE.md).

---

Complete API documentation is available via Swagger UI at **http://localhost:8000/docs** when the backend is running.

For detailed API reference, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

### Available Endpoints

#### Authentication

**GET /api/auth/csrf-token** — Generate a CSRF token cookie for state-changing requests
- No authentication required
- Returns: CSRF token string in response body, signed cookie in response headers
- The client must send the token back in the `X-CSRF-Token` header on subsequent POST/PUT/PATCH/DELETE requests

**POST /api/auth/login** — Authenticate user and return JWT token
- Request body:
  ```json
  {
    "username": "admin",
    "password": "your_password"
  }
  ```
- Returns: JWT token and user object (id, username, email, is_admin)

#### Hardware Management

**GET /api/hardware** — List all hardware assets
- Query parameters: `skip`, `limit`, `status`
- Returns: List of HardwareAsset objects

**GET /api/hardware/{id}** — Get hardware asset by ID
- Path parameter: `id` (integer)
- Returns: Single HardwareAsset object

**POST /api/hardware** — Create new hardware asset
- Request body: HardwareAsset data
- Returns: Created HardwareAsset object

**PUT /api/hardware/{id}** — Update hardware asset
- Path parameter: `id` (integer)
- Request body: Updated HardwareAsset data
- Returns: Updated HardwareAsset object

**DELETE /api/hardware/{id}** — Delete hardware asset
- Path parameter: `id` (integer)
- Requires: Admin privileges
- Returns: 204 No Content

**POST /api/hardware/{id}/rent** — Rent a hardware asset
- Path parameter: `id` (integer)
- Requires: Authenticated user (Bearer token)
- The device must have status `Available`
- Assigns the device to the authenticated user and sets status to `In Use`
- Returns: Updated HardwareAsset object

**POST /api/hardware/{id}/return** — Return a rented hardware asset
- Path parameter: `id` (integer)
- Requires: Authenticated user (Bearer token)
- The device must be currently rented by the requesting user
- Request body:
  ```json
  {
    "return_condition": "perfect or damaged or other",
    "description": "Required if condition is 'other'"
  }
  ```
- If condition is `perfect`, device status becomes `Available` and `repair_flagged` is cleared
- If condition is `damaged` or `other`, device status becomes `Repair` and `repair_flagged = True`
- Returns: Updated HardwareAsset object

#### AI Chatbot

**POST /api/ai/chat** — Get device recommendations
- Request body:
  ```json
  {
    "message": "I need a laptop for software development",
    "conversation_history": []
  }
  ```
- Returns: ChatbotResponse with recommendations

**GET /api/ai/health** — Check AI service health
- Returns: Service status and model information

#### System Health

**GET /health** — System health check
- Returns: Service status

**GET /docs** — Swagger UI documentation
- Interactive API documentation

**GET /openapi.json** — OpenAPI schema
- Machine-readable API specification

### Authentication

Protected endpoints require Bearer token authentication:

```
Authorization: Bearer <token>
```

Public endpoints (no auth required):
- `/health`
- `/docs`
- `/openapi.json`
- `/redoc`

### Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` — Successful request
- `201 Created` — Resource created
- `400 Bad Request` — Invalid request data
- `401 Unauthorized` — Missing or invalid authentication
- `403 Forbidden` — CSRF token invalid or insufficient permissions
- `404 Not Found` — Resource not found
- `429 Too Many Requests` — Rate limit exceeded
- `500 Internal Server Error` — Server error
- `504 Gateway Timeout` — AI service timeout

### Rate Limiting

All endpoints are rate-limited:
- **Default**: 100 requests per 60 seconds
- **Per-client**: Tracked by Bearer token or IP address
- **Response**: 429 Too Many Requests when exceeded

Configure via `.env`:
```
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
```

### CORS

Cross-Origin Resource Sharing is enabled for configured origins:

```
CORS_ORIGINS=["http://localhost:5173", "https://app.example.com"]
```

Allowed methods: GET, POST, PUT, DELETE, PATCH, OPTIONS

---

## AI Chatbot Assistant

The platform includes an intelligent device recommendation chatbot powered by Gemini. Users can describe their needs in natural language, and the assistant recommends available devices from the inventory.

### How It Works

1. **Natural Language Input**: Users describe what they need (e.g., "I need a laptop for software development")
2. **Database Query**: The service queries all available devices from the inventory
3. **AI Analysis**: Gemini analyzes the user's request against available devices
4. **Smart Recommendations**: Returns matching devices with personalized reasons for each recommendation
5. **Multi-turn Conversations**: Maintains conversation history for context-aware follow-up questions

### API Endpoint

**POST /api/ai/chat** — Get device recommendations

**Request:**
```json
{
  "message": "I need a phone with a great camera for photography",
  "conversation_history": []
}
```

**Response:**
```json
{
  "message": "Great! For photography, I'd recommend the iPhone 13 Pro Max with its exceptional camera system...",
  "recommendations": [
    {
      "id": 1,
      "name": "Apple iPhone 13 Pro Max",
      "brand": "Apple",
      "status": "Available",
      "reason": "Great camera capabilities for photography and video"
    }
  ],
  "conversation_context": "I need a phone with a great camera for photography"
}
```

### Features

- **Context-Aware**: Understands user intent and device specifications
- **Multi-turn Support**: Maintains conversation history for follow-up questions
- **Real-time Inventory**: Always recommends from currently available devices
- **Personalized Reasons**: Explains why each device matches the user's needs
- **Graceful Fallbacks**: Suggests alternatives if exact matches aren't available

### Error Handling

- `401 Unauthorized` — API credentials not configured
- `429 Too Many Requests` — API rate limit exceeded
- `504 Gateway Timeout` — API request timed out
- `500 Internal Server Error` — Other API or processing errors

### Health Check

**GET /api/ai/health** — Verify the AI service is ready

```bash
curl http://localhost:8000/api/ai/health
```

### Architecture

The chatbot service is built with a clean, decoupled architecture:

**Schemas** (`app/ai/schemas.py`):
- `ChatMessage` — individual message with role (user/assistant) and content
- `DeviceRecommendation` — recommended device with ID, name, brand, status, and personalized reason
- `ChatbotResponse` — assistant response with message, recommendations, and conversation context

**Service** (`app/ai/services.py`):
- `DeviceRecommendationService` — core recommendation engine
  - `chat()` — main async method that processes user messages
  - `_fetch_available_devices()` — queries database for available devices
  - `_format_devices_for_context()` — formats device info for AI prompt
  - `_build_recommendation_prompt()` — constructs Gemini prompt with conversation history
  - `_parse_response()` — extracts device IDs and message from Gemini response
  - `_get_recommendation_reason()` — generates personalized recommendation reasons

**Router** (`app/ai/router.py`):
- `POST /api/ai/chat` — main chatbot endpoint with dependency injection
- `GET /api/ai/health` — service health check
- Comprehensive error handling mapping to HTTP status codes

### Request Flow

```
User Message (natural language)
    ↓
[POST /api/ai/chat]
    ↓
[Security Middleware] → Rate limit, JWT, CSRF checks
    ↓
[DeviceRecommendationService.chat()]
    ├─ Query database for available devices
    ├─ Format devices into context
    ├─ Build prompt with conversation history
    ├─ Call client.aio.models.generate_content() (async, non-blocking)
    ├─ Parse response for device IDs
    ├─ Build DeviceRecommendation objects
    └─ Return ChatbotResponse
    ↓
[ChatbotResponse] → JSON with message + recommendations
```

### Implementation Details

**Modern SDK Integration**:
- Uses `from google import genai` (modern SDK, not legacy `google-generativeai`)
- Initializes `genai.Client(api_key=...)` with credentials from `.env`
- Calls `client.aio.models.generate_content()` for async, non-blocking API calls
- Avoids blocking the ASGI event loop

**Database Integration**:
- Queries `HardwareAsset` table for devices with status="Available"
- Formats device metadata (ID, name, brand, notes) for AI context
- Ensures recommendations are always from current inventory

**Prompt Engineering**:
- Includes available devices list in prompt context
- Incorporates conversation history (last 3 messages) for multi-turn support
- Instructs Gemini to return device IDs in parseable format: "Recommended IDs: [1, 3, 5]"
- Requests personalized, conversational responses

**Error Handling**:
- `AIAuthenticationError` (401) — missing/invalid API key
- `AIRateLimitError` (429) — quota exceeded
- `AITimeoutError` (504) — request deadline exceeded
- `AIServiceError` — catch-all for other failures
- All exceptions mapped to appropriate HTTP status codes

---

## Security

The backend implements a comprehensive, native security middleware layer that wraps all ASGI pipelines with zero external dependencies (no Redis, no external auth services).

### Rate Limiting

In-memory sliding window rate limiter tracks requests per client identifier:
- **Per-token**: If a Bearer token is provided, rate limit is tracked by token
- **Per-IP**: If no token, rate limit is tracked by client IP address
- **Default**: 100 requests per 60-second window
- **Response**: 429 Too Many Requests when exceeded

Configurable via `.env`:
```
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
```

### JWT & Session Verification

All protected endpoints require Bearer token authentication:
```
Authorization: Bearer <token>
```

**Public endpoints** (no auth required):
- `/health`
- `/docs`
- `/openapi.json`
- `/redoc`
- `/admin`

**Protected endpoints** return:
- `401 Unauthorized` — missing or invalid token
- `401 Unauthorized` — invalid Bearer format

Enable/disable via `.env`:
```
JWT_ENABLED=true
```

### CSRF Protection

Cross-Site Request Forgery tokens protect mutable operations (POST, PUT, DELETE, PATCH).

**Token Generation**:
- HMAC-SHA256 derived from session ID + secret key
- Deterministic — same session always generates same token
- Timing-attack resistant using `hmac.compare_digest()`

**Client Usage** (for mutable operations with session):
```
X-Session-ID: <session_id>
X-CSRF-Token: <token>
```

**Response**:
- `403 Forbidden` — missing or invalid CSRF token

Enable/disable via `.env`:
```
CSRF_ENABLED=true
```

### CORS Validation

Strict origin allowlist prevents cross-origin requests from unauthorized domains.

**Allowed Methods**: GET, POST, PUT, DELETE, PATCH, OPTIONS  
**Allowed Headers**: All (configurable)  
**Credentials**: Enabled (cookies/auth headers sent with requests)

Configure origins via `.env`:
```
CORS_ORIGINS=["http://localhost:5173", "https://app.example.com"]
```

### Security Response Headers

All responses include hardened security headers:
- `X-Content-Type-Options: nosniff` — prevent MIME type sniffing
- `X-Frame-Options: DENY` — prevent clickjacking
- `X-XSS-Protection: 1; mode=block` — enable XSS filter
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` — enforce HTTPS
- `Content-Security-Policy: default-src 'self'` — restrict resource loading

### Request Flow

```
Incoming Request
    ↓
[Rate Limit Check] → 429 if exceeded
    ↓
[JWT Verification] → 401 if invalid/missing on protected routes
    ↓
[CSRF Validation] → 403 if invalid on mutable operations
    ↓
[CORS Check] → blocked if origin not allowed
    ↓
[Route Handler]
    ↓
[Response + Security Headers]
```

### Production Recommendations

1. **Change SECRET_KEY** — generate a strong random key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Enable HTTPS** — HSTS header requires secure transport

3. **Adjust Rate Limits** — tune `RATE_LIMIT_WINDOW` and `RATE_LIMIT_MAX_REQUESTS` based on expected traffic

4. **Monitor 429/401/403 Responses** — indicates potential attacks or misconfigured clients

---

## Database Migrations

Run these from the `backend/` directory with the virtual environment active.

```bash
# Create a new migration after changing models
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Downgrade to previous migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Project Status

### ✅ Implemented

**Backend:**
- FastAPI async ASGI app with SQLAlchemy ORM + SQLite
- JWT authentication (`/api/auth/login`) with Bearer tokens
- Hardware CRUD endpoints (`GET/POST/PUT/DELETE /api/hardware`)
- Rent/return workflow (`POST /api/hardware/{id}/rent`, `/return`)
- AI chatbot service using Google GenAI (`gemini-2.5-flash`) with async client
- AI-powered repair flagging — scans device notes for repair indicators and sets `repair_flagged = True` for admin review
- Security middleware: rate limiting, CSRF protection, JWT verification, CORS, security headers
- SQLAdmin panel at `/admin` with user management, hardware management, and audit logs
- Audit logging for all admin actions with change history diff
- Alembic migrations for schema versioning

**Frontend:**
- Vue 3 + Vite + Pinia + Tailwind CSS
- Sign-in page with JWT token storage
- Dashboard with three tabs: Available, My Rentals, All Devices
- Device cards with rent/return actions and toast notifications
- Search by name/brand, filter by status and brand
- Sort by name, brand, or purchase date (ascending/descending)
- Pagination with ellipsis for large datasets
- AI chat assistant panel with multi-turn conversation and device recommendations
- Floating chat button with expandable panel

**Admin Panel (SQLAdmin):**
- User CRUD with password hashing and validation
- Hardware CRUD with status badges and repair flag column
- Audit log viewer with username resolution and change history
- Dashboard metrics (user count, hardware counts)
- Boolean filter for repair-flagged devices

---

### ⚡ Shortcuts & "Hacks"

> *What did you build quickly just to make it work?*

- **In-memory rate limiting** — The `RateLimitStore` uses a Python `defaultdict` with timestamps instead of Redis or a database-backed store.

  **The "Why":** Zero external dependencies. No Redis setup needed for local dev. Acceptable for single-server MVP with low traffic.

  **The "Future":** Replace with Redis-backed rate limiter (e.g., `slowapi` or custom Redis sliding window) for horizontal scaling and persistence across restarts.

- **SQLite in production** — The default `DATABASE_URL` points to a local SQLite file.

  **The "Why":** Zero configuration. No PostgreSQL server to install. Perfect for local development and small-scale demos.

  **The "Future":** Swap to PostgreSQL via `asyncpg` + SQLAlchemy async session. Add connection pooling with `pgbouncer`.

- **JWT in localStorage** — The frontend stores the Bearer token in `localStorage` and reads it back on page load.

  **The "Why":** Simplest possible persistence. No cookie management, no CSRF dance for the SPA. Works immediately.

  **The "Future":** Use httpOnly secure cookies for the JWT, or at minimum `sessionStorage` + a refresh token flow. Add an Axios/fetch interceptor to attach the token automatically.

- **Hardware CRUD endpoints are public** — `GET/POST/PUT /api/hardware` have no auth dependency. Only `DELETE` requires admin.

  **The "Why":** Faster iteration during development. No need to log in to test device management.

  **The "Future":** Require authentication for all mutable operations (`POST`, `PUT`, `DELETE`). Add role-based access control (admin vs. regular user).

- **No user registration endpoint** — Users can only be created via the SQLAdmin panel or the `create_admin.py` script.

  **The "Why":** Admin panel was already built. Self-registration wasn't in scope for the initial demo.

  **The "Future":** Add `POST /api/auth/register` with email verification, password strength validation, and rate-limited signup.

- **Form-parameter endpoints** — `POST` and `PUT /api/hardware` accept flat form fields instead of a JSON body with a Pydantic schema.

  **The "Why":** Quick to implement. No extra schema class needed.

  **The "Future":** Use proper Pydantic request schemas (like `HardwareCreate`, `HardwareUpdate`) with field validation, defaults, and OpenAPI docs.

- **No rental history tracking** — Renting a device simply overwrites `assigned_to` and sets status to `"In Use"`. No record of who rented what and when.

  **The "Why":** The `HardwareAsset` model was designed before rental history was a requirement. The audit log in SQLAdmin captures changes but isn't exposed via the API.

  **The "Future":** Create a `Rental` model (user_id, device_id, start_date, end_date) and expose rental history endpoints.

---

### ⚠ Partial / Missing

> *What started but didn't make the cut?*

- **Test coverage** — Only one test file exists (`test_hardware_rent_return.py`) with basic rent/return tests. No tests for auth, AI chatbot, security middleware, or admin panel.

- **CI/CD pipeline** — No GitHub Actions, no automated test runner, no linting/formatting checks. No Dockerfile or docker-compose for reproducible deployments.

- **Frontend admin dashboard** — The admin panel is a separate SQLAdmin interface at `/admin`. There's no admin section in the Vue frontend for user management, device management, or analytics.

- **User profile & settings** — No way for users to change their password, update email, or manage account settings from the frontend.

- **Email notifications** — No email service integration for rental confirmations, return reminders, or account verification.

- **Dark mode** — The frontend uses Tailwind CSS (which has built-in dark mode support) but no dark mode toggle or theme persistence.

- **Loading skeletons** — The dashboard shows a simple spinner during loading. No skeleton placeholders for cards or tables.

- **Refresh token flow** — JWT tokens are stored in localStorage with no automatic refresh. When the token expires, the user must sign in again.

- **Request validation schemas** — Hardware create/update endpoints accept raw form fields instead of Pydantic schemas, so there's no automatic OpenAPI request body documentation.

---

### 🔮 Next Steps (The 24h Roadmap)

> *If you had one more day, what would be your top 3 priorities to fix or improve?*

1. **Add auth protection to hardware CRUD + user registration** — Lock down `POST/PUT /api/hardware` behind `get_current_active_user`, add `POST /api/auth/register` with a Pydantic schema, and add a registration page to the frontend. This closes the biggest security gap and enables self-service user onboarding.

2. **Add rental history tracking** — Create a `Rental` model with user/device/timestamps, expose `GET /api/hardware/{id}/history` and `GET /api/rentals/my` endpoints, and add a "Rental History" tab to the frontend dashboard. This turns the current "overwrite" approach into a proper audit trail.

3. **Add a fetch interceptor + token refresh** — Build a thin Axios/fetch wrapper that automatically attaches the Bearer token, handles 401 responses, and refreshes the token transparently. Add a refresh token endpoint to the backend. This fixes the most brittle part of the frontend auth flow.

---

## Database Models

The application uses SQLAlchemy ORM with four main tables:

### User (`user`)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, auto-increment | Unique user ID |
| `username` | String(255) | Unique, NOT NULL, indexed | Login username |
| `email` | String(255) | Unique, NOT NULL, indexed | Email address |
| `password_hash` | String(255) | NOT NULL | SHA-256 with salt |
| `full_name` | String(255) | Nullable | Display name |
| `is_active` | Boolean | Default: true | Account active status |
| `is_admin` | Boolean | Default: false | Admin privileges |
| `created_at` | DateTime | NOT NULL | Account creation timestamp |
| `updated_at` | DateTime | NOT NULL | Last update timestamp |

### HardwareAsset (`hardware_asset`)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, auto-increment | Unique device ID |
| `name` | String(255) | NOT NULL, indexed | Device name/model |
| `brand` | String(100) | NOT NULL | Manufacturer brand |
| `purchase_date` | Date | Nullable | Date of purchase |
| `status` | String(50) | NOT NULL, indexed, default: "Available" | Available, In Use, Repair, Unknown |
| `assigned_to` | String(255) | Nullable | Currently assigned user |
| `notes` | Text | Nullable | Additional notes / maintenance info |
| `repair_flagged` | Boolean | Default: false | Flagged for admin repair review |

### DataQuarantine (`data_quarantine`)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, auto-increment | Unique quarantine entry ID |
| `raw_data` | Text | NOT NULL | Original raw input as JSON |
| `errors` | Text | NOT NULL | Validation errors as JSON |
| `severity` | String(20) | NOT NULL, default: "warning" | "critical" or "warning" |
| `source` | String(100) | Nullable | e.g. "seed_script", "api_import" |
| `resolved` | Boolean | Default: false | Whether the issue has been addressed |
| `created_at` | DateTime | NOT NULL | Entry creation timestamp |

### ReturnRecord (`return_record`)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, auto-increment | Unique return record ID |
| `hardware_id` | Integer | FK → hardware_asset.id, NOT NULL, indexed | Returned device ID |
| `returned_by` | String(255) | NOT NULL, indexed | Username who returned the device |
| `return_condition` | String(50) | NOT NULL | "perfect", "damaged", or "other" |
| `description` | Text | Nullable | Required when condition is "other" |
| `returned_at` | DateTime | NOT NULL | Return timestamp |

### AuditLog (`audit_log`)
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | PK, auto-increment | Unique audit entry ID |
| `user_id` | Integer | FK → user.id, NOT NULL, indexed | User who performed the action |
| `action` | String(50) | NOT NULL, indexed | CREATE, UPDATE, DELETE |
| `table_name` | String(100) | NOT NULL, indexed | Affected table |
| `record_id` | Integer | NOT NULL | Affected record ID |
| `old_values` | Text | Nullable | JSON of old values |
| `new_values` | Text | Nullable | JSON of new values |
| `description` | Text | Nullable | Human-readable description |
| `ip_address` | String(45) | Nullable | Client IPv4 or IPv6 |
| `user_agent` | String(500) | Nullable | Browser/client info |
| `created_at` | DateTime | NOT NULL, indexed | Log entry timestamp |

---

## Data Validation & Quarantine System

The backend includes a data validation and quarantine system for hardware imports, ensuring data integrity even when bulk-importing records.

### How It Works

1. **Validation** — Incoming hardware records pass through `HardwareImportSchema` (Pydantic), which:
   - Strips and normalizes whitespace from all string fields
   - Normalizes purchase dates from multiple formats (ISO, US, EU) to YYYY-MM-DD
   - Normalizes status to title case and validates against allowed values
   - Enforces required fields: `name` (1-255 chars), `brand` (1-100 chars)
   - Rejects records with invalid status when `assigned_to` is provided

2. **Quarantine** — Records that fail validation are stored in the `data_quarantine` table with:
   - The original raw input preserved as JSON
   - All validation error messages stored as JSON
   - A severity flag (`critical` for missing required fields, `warning` for other issues)
   - Source tracking (e.g., `seed_script`, `api_import`, `api_create`)

3. **Import Batch API** — `import_hardware_batch(db, records, source)` processes multiple records at once, returning separate lists of successfully imported devices and quarantined entries.

### Key Components

- **`app/core/validation.py`** — `HardwareImportSchema` (Pydantic), `ValidationResult`, `validate_hardware_record()`, `quarantine_record()`, `import_hardware_batch()`
- **`app/models/hardware.py`** — `DataQuarantine` SQLAlchemy model

### Endpoints with Validation

Both `POST /api/hardware` and `PUT /api/hardware/{id}` use the validation pipeline, rejecting invalid data with `400 Bad Request` and automatically quarantining the failed record.

---

## Admin Authentication

The SQLAdmin panel uses session-based authentication separate from the API's JWT flow.

### How It Works

- **Session JWT** — On login, the admin credentials are verified against the `User` table, then a JWT token is stored in the session cookie
- **Inactivity Timeout** — Admin sessions expire after 30 minutes of inactivity (`admin_last_activity` timestamp tracked per request)
- **Session Duration** — Maximum session lifetime is 14 days
- **Cross-Domain** — Session cookie uses `SameSite=None` + `Secure` flag for cross-domain admin access

### Key Components

- **`app/admin_auth.py`** — `AdminAuthenticationBackend` class with `login()`, `logout()`, and `authenticate()` methods
- **Dependencies** — `app/core/user.py` provides `verify_password()` using SHA-256 with salt

---

## Frontend Architecture

### Router (`src/router/index.js`)

| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/` | — | — | Redirects to `/dashboard` |
| `/signin` | `SigninView.vue` | No (redirects to dashboard if authenticated) | Login page |
| `/dashboard` | `DashboardView.vue` | Yes (redirects to `/signin` if not authenticated) | Main dashboard with device management |
| `/:pathMatch(.*)*` | — | — | Catch-all: redirects based on auth state |

### Pinia Stores

| Store | File | Purpose |
|-------|------|---------|
| `useAuthStore` | `src/stores/auth.js` | JWT token management, login/logout, auth state |
| `useDeviceStore` | `src/stores/device.js` | Device list fetching, search, filter, sort, pagination |
| `useChatStore` | `src/stores/chat.js` | AI chat messages, conversation history, API communication |

### Components

| Component | File | Description |
|-----------|------|-------------|
| `DeviceCard` | `src/components/DeviceCard.vue` | Hardware asset card with rent/return actions |
| `ChatAssistant` | `src/components/ChatAssistant.vue` | Floating AI chatbot panel with conversation UI |
| `ReturnModal` | `src/components/ReturnModal.vue` | Return condition modal (perfect/damaged/other) |

### Features

- **Authentication Guard** — `beforeEach` navigation guard checks `authStore.isAuthenticated` against localStorage token
- **Dashboard Tabs** — Three views: Available, My Rentals, All Devices
- **Search & Filter** — Search by name/brand, filter by status and brand
- **Sorting** — By name, brand, or purchase date (ascending/descending)
- **Pagination** — With ellipsis for large datasets
- **Toast Notifications** — Success/error feedback for rent/return actions
- **Floating Chat** — Toggleable AI assistant panel
- **Catch-all Route** — Unknown paths redirect to `/dashboard` or `/signin` based on auth state

---

## Project Structure

```
The-Rental-Shop/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app factory, middleware registration
│   │   ├── admin.py               # SQLAdmin dashboard & model views
│   │   ├── admin_auth.py          # Admin session authentication backend
│   │   ├── admin_helpers.py       # Admin utility helpers
│   │   ├── ai/                    # AI chatbot service
│   │   │   ├── router.py          # Chat & health endpoints
│   │   │   ├── schemas.py         # Pydantic request/response models
│   │   │   └── services.py        # Device recommendation engine
│   │   ├── api/routes/            # API route modules
│   │   │   ├── auth.py            # Login & CSRF token endpoints
│   │   │   └── hardware.py        # Hardware CRUD + rent/return endpoints
│   │   ├── core/
│   │   │   ├── config.py          # Settings (pydantic-settings)
│   │   │   ├── database.py        # SQLAlchemy engine & session factory
│   │   │   ├── deps.py            # FastAPI dependency injection (JWT auth)
│   │   │   ├── user.py            # User CRUD & password hashing utilities
│   │   │   ├── audit.py           # Audit logging helpers
│   │   │   └── validation.py      # Hardware data validation & quarantine
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── hardware.py        # HardwareAsset, DataQuarantine, ReturnRecord
│   │   │   ├── user.py            # User model
│   │   │   └── audit_log.py       # AuditLog model
│   │   ├── security/
│   │   │   └── middleware.py      # ASGI middleware: rate limit, JWT, CSRF, CORS, headers
│   │   └── templates/sqladmin/    # Custom SQLAdmin Jinja2 templates
│   ├── alembic/                   # Alembic migrations
│   │   ├── versions/              # Migration files (001-004)
│   │   ├── env.py                 # Alembic environment config
│   │   └── script.py.mako         # Migration template
│   ├── scripts/                   # Utility scripts (seed, etc.)
│   ├── tests/
│   │   ├── conftest.py            # Test fixtures & configuration
│   │   └── test_hardware_rent_return.py  # Rent/return integration tests
│   ├── alembic.ini                # Alembic configuration
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Python dependencies
│   ├── pyproject.toml             # Project metadata
│   ├── Procfile                   # Heroku process definition
│   └── runtime.txt                # Heroku Python runtime
├── frontend/
│   ├── public/                    # Static assets
│   ├── src/
│   │   ├── assets/
│   │   │   └── main.css           # Global styles (Tailwind directives)
│   │   ├── components/
│   │   │   ├── DeviceCard.vue     # Device card with rent/return actions
│   │   │   ├── ChatAssistant.vue  # Floating AI chat panel
│   │   │   └── ReturnModal.vue    # Return condition modal
│   │   ├── router/
│   │   │   └── index.js           # Vue Router configuration
│   │   ├── stores/
│   │   │   ├── auth.js            # JWT auth state & login
│   │   │   ├── device.js          # Device list, search, filter, sort, pagination
│   │   │   └── chat.js            # AI chat messages & API communication
│   │   ├── views/
│   │   │   ├── HomeView.vue       # Landing page
│   │   │   ├── SigninView.vue     # Login page
│   │   │   └── DashboardView.vue  # Main dashboard with tabs
│   │   ├── App.vue                # Root Vue component
│   │   └── main.js                # Vue app entry point
│   ├── index.html                 # HTML entry point
│   ├── vite.config.js             # Vite configuration (proxy, build)
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── postcss.config.js          # PostCSS configuration
│   ├── .env.production            # Production environment variables
│   ├── package.json               # Node dependencies & scripts
│   └── vercel.json                # Vercel deployment configuration
├── .gitignore
├── LICENSE
├── README.md                      # This file
├── API_DOCUMENTATION.md           # Detailed API reference
├── MIGRATION_GUIDE.md             # Piccolo → SQLAlchemy migration notes
├── SQLADMIN_GUIDE.md              # Admin panel usage guide
├── DEVELOPMENT_PROMPTS.md         # Development prompts & notes
└── AI Log.md                      # AI assistant change log
```
