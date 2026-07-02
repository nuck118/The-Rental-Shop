# Project Summary: The Rental Shop

## Overview

The Rental Shop is an **async-native, AI-driven Hardware Rental Hub** built with modern web technologies. It orchestrates corporate equipment workflows with an advanced asynchronous backend and an optimistic user interface.

## Key Achievements

### ✅ Backend Architecture
- **FastAPI** — Async ASGI framework for high-performance APIs
- **SQLAlchemy** — Powerful ORM with full async support
- **Alembic** — Auto-migration system for database schema management
- **SQLite** — Lightweight, file-based relational database

### ✅ AI Integration
- **Google GenAI SDK** — Modern SDK for Gemini 2.5 Flash
- **Device Recommendation Chatbot** — Natural language device discovery
- **Multi-turn Conversations** — Context-aware recommendations
- **Real-time Inventory** — Always recommends available devices

### ✅ Security Layer
- **Rate Limiting** — 100 requests/60 seconds per client
- **JWT Authentication** — Bearer token verification
- **CSRF Protection** — HMAC-SHA256 token validation
- **CORS Validation** — Strict origin allowlist
- **Security Headers** — Hardened response headers

### ✅ API Documentation
- **Swagger UI** — Interactive endpoint testing at `/docs`
- **ReDoc** — Alternative documentation view at `/redoc`
- **OpenAPI Schema** — Machine-readable specification at `/openapi.json`
- **Comprehensive Guides** — Complete API reference with examples

### ✅ Frontend
- **Vue 3** — Modern reactive framework
- **Vite** — Lightning-fast build tool
- **Tailwind CSS** — Utility-first styling
- **Preline** — Pre-built UI components
- **Pinia** — State management
- **Vue Router** — Client-side routing

## Documentation

### Quick Reference
| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview and setup |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference |
| [API_GUIDE.md](API_GUIDE.md) | How to test and use APIs |
| [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) | Database migrations |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Piccolo to SQLAlchemy migration |
| [SETUP.md](SETUP.md) | Detailed setup instructions |
| [QUICKSTART.md](QUICKSTART.md) | Quick reference |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues |
| [DOCUMENTATION.md](DOCUMENTATION.md) | Documentation index |

### Access Points
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

## API Endpoints

### Hardware Management
```
GET    /api/hardware              List all hardware
GET    /api/hardware/{id}         Get specific hardware
POST   /api/hardware              Create hardware
PUT    /api/hardware/{id}         Update hardware
DELETE /api/hardware/{id}         Delete hardware
```

### AI Chatbot
```
POST   /api/ai/chat               Get device recommendations
GET    /api/ai/health             Check AI service health
```

### System
```
GET    /health                    System health check
GET    /docs                      Swagger UI
GET    /redoc                     ReDoc
GET    /openapi.json              OpenAPI schema
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.115.5
- **ORM**: SQLAlchemy 2.0.25
- **Migrations**: Alembic 1.13.1
- **Database**: SQLite
- **AI**: Google GenAI 1.16.0
- **Validation**: Pydantic 2.10.3
- **Server**: Uvicorn 0.32.1

### Frontend
- **Framework**: Vue 3.5.13
- **Build**: Vite 6.0.5
- **Routing**: Vue Router 4.5.0
- **State**: Pinia 2.3.0
- **Styling**: Tailwind CSS 3.4.17
- **Components**: Preline 2.7.0

## Security Features

### Authentication
- Bearer token authentication
- Public endpoints: `/health`, `/docs`, `/openapi.json`, `/redoc`
- Protected endpoints: All `/api/*` routes

### Rate Limiting
- **100 requests per 60 seconds**
- Per Bearer token or IP address
- Configurable via `.env`

### CSRF Protection
- HMAC-SHA256 tokens
- Timing-attack resistant
- Configurable via `.env`

### CORS
- Strict origin allowlist
- Configurable via `.env`
- Credentials enabled

### Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Content-Security-Policy

## Database Schema

### HardwareAsset Table
```sql
CREATE TABLE hardware_asset (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    purchase_date DATE,
    status VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(255),
    notes TEXT
);
```

**Indexes:**
- `name` — For quick device lookup
- `status` — For filtering by availability

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python scripts/seed_hardware.py
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Access Points
- **Backend API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

## Key Features

### Hardware Management
- ✅ CRUD operations on hardware assets
- ✅ Pagination and filtering
- ✅ Status tracking (Available, In Use, Repair, Unknown)
- ✅ Assignment tracking
- ✅ Notes and metadata

### AI Chatbot
- ✅ Natural language device discovery
- ✅ Context-aware recommendations
- ✅ Multi-turn conversations
- ✅ Real-time inventory integration
- ✅ Personalized explanations

### Security
- ✅ Rate limiting
- ✅ JWT authentication
- ✅ CSRF protection
- ✅ CORS validation
- ✅ Security headers

### Database
- ✅ SQLAlchemy ORM
- ✅ Alembic auto-migrations
- ✅ SQLite storage
- ✅ Automatic table creation

## Migration from Piccolo

### Why SQLAlchemy + Alembic?
- ✅ **Auto-migration support** — Alembic detects model changes automatically
- ✅ **Version control** — All schema changes tracked and reversible
- ✅ **Production-ready** — Industry-standard tool
- ✅ **Better ecosystem** — Larger community and more extensions

### What Changed
- Replaced Piccolo ORM with SQLAlchemy
- Replaced Piccolo migrations with Alembic
- Removed Piccolo admin panel
- Updated all models and queries
- Updated seed script

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

## Error Handling

### HTTP Status Codes
- `200 OK` — Successful request
- `201 Created` — Resource created
- `400 Bad Request` — Invalid request data
- `401 Unauthorized` — Missing/invalid authentication
- `403 Forbidden` — CSRF token invalid
- `404 Not Found` — Resource not found
- `429 Too Many Requests` — Rate limit exceeded
- `500 Internal Server Error` — Server error
- `504 Gateway Timeout` — AI service timeout

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Configuration

### Required Environment Variables
```
GEMINI_API_KEY=your-api-key
```

### Optional Environment Variables
```
DATABASE_URL=rental_shop.db
CORS_ORIGINS=["http://localhost:5173"]
SECRET_KEY=your-secret-key
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
CSRF_ENABLED=true
JWT_ENABLED=true
```

## Testing

### Using Swagger UI
1. Open http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using cURL
```bash
# List hardware
curl -X GET "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>"

# Create hardware
curl -X POST "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Dell XPS", "brand": "Dell", "status": "Available"}'

# Chat with AI
curl -X POST "http://localhost:8000/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a laptop", "conversation_history": []}'
```

## Project Structure

```
The-Rental-Shop/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI chatbot service
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Config & database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── security/        # Security middleware
│   │   └── main.py          # FastAPI app
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Utility scripts
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page components
│   │   ├── router/          # Vue Router
│   │   └── stores/          # Pinia stores
│   └── package.json
└── Documentation files
```

## Performance Considerations

### Backend
- **Async ASGI** — Non-blocking I/O for high concurrency
- **Connection pooling** — Efficient database connections
- **Rate limiting** — Prevents abuse and ensures fair usage
- **Caching** — In-memory rate limit tracking

### Frontend
- **Vite** — Fast development server and build
- **Code splitting** — Lazy-loaded routes
- **Tree shaking** — Unused code removal
- **Minification** — Production-optimized bundles

## Scalability

### Current Limitations
- SQLite is single-writer (suitable for MVP)
- In-memory rate limiting (suitable for single instance)
- No distributed caching

### Future Improvements
- PostgreSQL for multi-instance deployment
- Redis for distributed rate limiting
- Kubernetes for container orchestration
- CDN for static assets

## Production Deployment

### Before Deploying
1. Generate strong SECRET_KEY
2. Set HTTPS/TLS certificates
3. Configure production database
4. Set appropriate rate limits
5. Enable all security features

### Deployment Steps
1. Install dependencies
2. Run database migrations
3. Seed initial data
4. Start backend with production server
5. Deploy frontend to CDN
6. Configure reverse proxy (nginx, Caddy)

## Support & Documentation

### Getting Help
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
3. Check backend logs
4. Review error messages

### Documentation Files
- [README.md](README.md) — Project overview
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — API reference
- [API_GUIDE.md](API_GUIDE.md) — Testing guide
- [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) — Database guide
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) — Migration details
- [SETUP.md](SETUP.md) — Setup instructions
- [QUICKSTART.md](QUICKSTART.md) — Quick reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues
- [DOCUMENTATION.md](DOCUMENTATION.md) — Documentation index

## Next Steps

1. **Read [README.md](README.md)** — Understand the project
2. **Follow [SETUP.md](SETUP.md)** — Set up the environment
3. **Access [API_DOCUMENTATION.md](API_DOCUMENTATION.md)** — Learn the API
4. **Test with Swagger UI** — http://localhost:8000/docs
5. **Build frontend** — Integrate with Vue.js
6. **Deploy** — Follow production guidelines

## License

See [LICENSE](LICENSE) file for details.

## Summary

The Rental Shop is a **production-ready, AI-native hardware rental platform** with:

✅ Modern async backend (FastAPI + SQLAlchemy + Alembic)  
✅ Intelligent AI chatbot (Google Gemini)  
✅ Comprehensive security (rate limiting, JWT, CSRF, CORS)  
✅ Complete API documentation (Swagger UI + ReDoc)  
✅ Modern frontend (Vue 3 + Vite + Tailwind)  
✅ Extensive documentation (8+ guides)  

**Ready for development and deployment!**
