# Setup Instructions

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your `GEMINI_API_KEY`:
```
GEMINI_API_KEY=your-api-key-here
```

### 4. Create and Run Database Migrations

```bash
# Create initial migration for HardwareAsset table
piccolo migrations new app --auto

# Apply the migration to create the database schema
piccolo migrations run
```

This will:
- Generate a migration file in `backend/migrations/`
- Create `rental_shop.db` SQLite database
- Create the `hardware_asset` table

### 5. Seed the Database (Optional)

```bash
# Populate the database with sample hardware data
python scripts/seed_hardware.py
```

Expected output:
```
Inserted: [1] Apple iPhone 13 Pro Max
Inserted: [2] Apple MacBook Pro 13
...
```

### 6. Start the Backend Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Verify Everything Works

### 1. Check Backend Health

```bash
curl http://localhost:8000/docs
```

You should see the FastAPI Swagger UI with all endpoints listed.

### 2. Check AI Service

```bash
curl http://localhost:8000/api/ai/health
```

Expected response:
```json
{
  "status": "healthy",
  "model": "gemini-2.5-flash",
  "message": "AI chatbot service is ready"
}
```

### 3. Access Admin Panel

Open http://localhost:8000/admin in your browser. You should see:
- **HardwareAsset** table listed
- All seeded devices visible in the table

### 4. Test Chatbot Endpoint

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a laptop for software development",
    "conversation_history": []
  }'
```

## Troubleshooting

### Database Not Showing Data in Admin

1. Verify migrations were created:
   ```bash
   piccolo migrations check
   ```

2. Verify database file exists:
   ```bash
   ls -la rental_shop.db
   ```

3. Verify data was seeded:
   ```bash
   python -c "from app.models.hardware import HardwareAsset; import asyncio; print(asyncio.run(HardwareAsset.select().run()))"
   ```

### AI Service Returns 401

Ensure `GEMINI_API_KEY` is set in `.env`:
```bash
echo $GEMINI_API_KEY
```

### Port Already in Use

Change the port:
```bash
# Backend (default 8000)
uvicorn app.main:app --reload --port 8001

# Frontend (default 5173)
npm run dev -- --port 5174
```

## Production Deployment

Before deploying to production:

1. Generate a strong SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Update `.env` with production values:
   ```
   SECRET_KEY=<generated-key>
   CORS_ORIGINS=["https://yourdomain.com"]
   JWT_ENABLED=true
   CSRF_ENABLED=true
   ```

3. Use a production ASGI server:
   ```bash
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

4. Enable HTTPS with a reverse proxy (nginx, Caddy, etc.)
