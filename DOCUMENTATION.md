# Documentation Index

## Quick Links

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview, stack, setup instructions |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete API reference with examples |
| [API_GUIDE.md](API_GUIDE.md) | How to access and test API documentation |
| [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) | Database migrations with Alembic |
| [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) | Piccolo to SQLAlchemy migration details |
| [SETUP.md](SETUP.md) | Detailed setup instructions |
| [QUICKSTART.md](QUICKSTART.md) | Quick reference for common tasks |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Debugging and common issues |

## Getting Started

### 1. First Time Setup
Start here: [SETUP.md](SETUP.md)
- Environment setup
- Dependency installation
- Database initialization
- Data seeding

### 2. Quick Start
For experienced developers: [QUICKSTART.md](QUICKSTART.md)
- Minimal setup steps
- Common commands
- Quick reference

### 3. API Documentation
Access the API: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- All endpoints documented
- Request/response examples
- Error handling
- Authentication details

### 4. Testing APIs
Learn how to test: [API_GUIDE.md](API_GUIDE.md)
- Swagger UI access
- cURL examples
- Python/JavaScript examples
- Common issues

## Documentation by Topic

### Backend Setup
- [README.md](README.md) — Overview and stack
- [SETUP.md](SETUP.md) — Detailed setup
- [QUICKSTART.md](QUICKSTART.md) — Quick reference

### Database
- [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) — Migrations
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) — ORM migration

### API
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — Complete reference
- [API_GUIDE.md](API_GUIDE.md) — Testing guide

### Troubleshooting
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues
- [README.md](README.md) — Security and features

## Key Features

### Hardware Management API
**Endpoints:**
- `GET /api/hardware` — List all hardware
- `GET /api/hardware/{id}` — Get specific hardware
- `POST /api/hardware` — Create hardware
- `PUT /api/hardware/{id}` — Update hardware
- `DELETE /api/hardware/{id}` — Delete hardware

**Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md#hardware-management-api)

### AI Chatbot API
**Endpoints:**
- `POST /api/ai/chat` — Get device recommendations
- `GET /api/ai/health` — Check AI service health

**Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md#ai-chatbot-api)

### Security Features
- Rate limiting (100 requests/60 seconds)
- JWT authentication
- CSRF protection
- CORS validation
- Security headers

**Documentation:** [README.md](README.md#security)

### Database
- SQLAlchemy ORM
- Alembic migrations
- Auto-migration support
- SQLite storage

**Documentation:** [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

## Interactive Documentation

### Swagger UI
**URL:** http://localhost:8000/docs

**Features:**
- Interactive endpoint testing
- Request/response examples
- Parameter validation
- Try-it-out functionality

### ReDoc
**URL:** http://localhost:8000/redoc

**Features:**
- Clean documentation view
- Search functionality
- Responsive design

### OpenAPI Schema
**URL:** http://localhost:8000/openapi.json

**Use Cases:**
- API client generation
- Documentation automation
- Third-party integrations

## Common Tasks

### Setup Backend
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

See: [SETUP.md](SETUP.md)

### Create Database Migration
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

See: [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

### Test API Endpoint
```bash
curl -X GET "http://localhost:8000/api/hardware" \
  -H "Authorization: Bearer <token>"
```

See: [API_GUIDE.md](API_GUIDE.md)

### Add New Model
1. Create model in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "..."`
3. Apply migration: `alembic upgrade head`

See: [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

## Architecture Overview

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

## Stack Information

### Backend
- **Framework:** FastAPI (async ASGI)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Database:** SQLite
- **AI:** Google GenAI SDK (gemini-2.5-flash)
- **Security:** Native middleware (rate limiting, JWT, CSRF)

### Frontend
- **Framework:** Vue 3
- **Build Tool:** Vite
- **State Management:** Pinia
- **Routing:** Vue Router
- **Styling:** Tailwind CSS + Preline

## API Endpoints Summary

### Hardware Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hardware` | List all hardware |
| GET | `/api/hardware/{id}` | Get specific hardware |
| POST | `/api/hardware` | Create hardware |
| PUT | `/api/hardware/{id}` | Update hardware |
| DELETE | `/api/hardware/{id}` | Delete hardware |

### AI Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Get recommendations |
| GET | `/api/ai/health` | Check AI health |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| GET | `/openapi.json` | OpenAPI schema |

## Security

### Authentication
- Bearer token authentication
- Public endpoints: `/health`, `/docs`, `/openapi.json`, `/redoc`
- Protected endpoints: All `/api/*` routes

### Rate Limiting
- 100 requests per 60 seconds
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

See: [README.md](README.md#security)

## Environment Configuration

### Required Variables
```
GEMINI_API_KEY=your-api-key
```

### Optional Variables
```
DATABASE_URL=rental_shop.db
CORS_ORIGINS=["http://localhost:5173"]
SECRET_KEY=your-secret-key
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX_REQUESTS=100
CSRF_ENABLED=true
JWT_ENABLED=true
```

See: [README.md](README.md#backend)

## Troubleshooting

### Common Issues
- Database not showing data → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Migration errors → [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md#troubleshooting)
- API errors → [API_GUIDE.md](API_GUIDE.md#common-issues)
- Setup issues → [SETUP.md](SETUP.md)

## Support Resources

### Documentation
- [README.md](README.md) — Project overview
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — API reference
- [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md) — Database guide

### Tools
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI: http://localhost:8000/openapi.json

### Debugging
- Check backend logs
- Review error messages
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Next Steps

1. **Read [README.md](README.md)** — Understand the project
2. **Follow [SETUP.md](SETUP.md)** — Set up the environment
3. **Access [API_DOCUMENTATION.md](API_DOCUMENTATION.md)** — Learn the API
4. **Test with Swagger UI** — http://localhost:8000/docs
5. **Build frontend** — Integrate with Vue.js
6. **Deploy** — Follow production guidelines

## Document Versions

| Document | Last Updated | Version |
|----------|--------------|---------|
| README.md | 2024-01-15 | 1.0 |
| API_DOCUMENTATION.md | 2024-01-15 | 1.0 |
| API_GUIDE.md | 2024-01-15 | 1.0 |
| ALEMBIC_GUIDE.md | 2024-01-15 | 1.0 |
| MIGRATION_GUIDE.md | 2024-01-15 | 1.0 |
| SETUP.md | 2024-01-15 | 1.0 |
| QUICKSTART.md | 2024-01-15 | 1.0 |
| TROUBLESHOOTING.md | 2024-01-15 | 1.0 |

## Contributing

When adding new features:
1. Update relevant documentation
2. Add API endpoint documentation
3. Update [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. Add migration guide if schema changes
5. Update [README.md](README.md) if needed

## License

See [LICENSE](LICENSE) file for details.
