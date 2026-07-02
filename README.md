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

## Database Migrations

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
