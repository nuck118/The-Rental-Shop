# The-Rental-Shop
An async-native, AI-driven Hardware Rental Hub built to orchestrate corporate equipment workflows. The platform leverages an advanced asynchronous backend architecture paired with an immediate, optimistic user interface to manage asset life cycles, enforce atomic concurrency guardrails, and execute semantic inventory discovery.

## Stack
- **Backend** — FastAPI (async ASGI), Piccolo ORM + SQLite, piccolo_admin, piccolo_api
- **AI** — Google GenAI SDK (`gemini-2.5-flash`)
- **Frontend** — Vue 3 (Vite, Composition API), Pinia, Vue Router, Tailwind CSS, Preline

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
| `CORS_ORIGINS` | Allowed frontend origins | `["http://localhost:5173"]` |
| `SECRET_KEY` | HMAC secret for CSRF/JWT | `your-secret-key-change-in-production` |
| `RATE_LIMIT_WINDOW` | Rate limit window in seconds | `60` |
| `RATE_LIMIT_MAX_REQUESTS` | Max requests per window | `100` |
| `CSRF_ENABLED` | Enable CSRF protection | `true` |
| `JWT_ENABLED` | Enable JWT/session verification | `true` |

Run database migrations:

```bash
piccolo migrations run
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

Run these from the `backend/` directory with the virtual environment active.

```bash
# Create a new migration after changing models
piccolo migrations new app --auto

# Apply all pending migrations
piccolo migrations run

# Check migration status
piccolo migrations check
```

---

## Project Structure

```
The-Rental-Shop/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API route modules
│   │   ├── core/config.py     # Settings (pydantic-settings)
│   │   ├── models/            # Piccolo Table definitions
│   │   ├── main.py            # FastAPI app factory
│   │   └── piccolo_app.py     # Piccolo app config for migrations
│   ├── migrations/            # Auto-generated migration files
│   ├── piccolo_conf.py        # DB engine + app registry
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── assets/            # Global CSS (Tailwind directives)
│   │   ├── components/        # Reusable Vue components
│   │   ├── router/            # Vue Router config
│   │   ├── stores/            # Pinia stores
│   │   ├── views/             # Page-level Vue components
│   │   ├── App.vue
│   │   └── main.js
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
└── .gitignore
```
