# Development Prompts for The Rental Shop

This document outlines the likely prompts used to develop The Rental Shop application step by step, reconstructed from git commit history and the AI Log.md file.

---

## Phase 1: Initial Repository Setup

### Prompt 1: Repository Scaffolding
Act as an expert Senior Python Backend Engineer and Enterprise Solutions Architect. I am initializing a repository for an AI-Native Web Application MVP. I need you to generate the foundational repository scaffolding and environment setup configuration files.

Our stack consists of:
- Backend: FastAPI (Async ASGI native)
- ORM/Database: Piccolo ORM using SQLite as the relational storage engine, integrated with piccolo_admin (the Vue.js-based administration engine running directly on top of Piccolo tables)
- Security Auth/Session Management: piccolo_api
- AI Layer: Modern Google GenAI SDK (google-genai) utilizing 'gemini-2.5-flash'
- Frontend: Vue.js 3 (Vite, Composition API using <script setup>, and Preline CSS / Tailwind CSS)

Please generate the file content and structure matching the architecture below. Ensure everything is clean, production-ready, and follows modern async standards.

### 1. Project Directory Architecture Structure
Provide a visual ASCII text tree or directory mapping for:
- /backend (App code, routing, models, security middleware, migrations config)
- /frontend (Vite + Vue 3 source structure, components, styles configuration)
- Root configurations (.gitignore, documentation stubs)

### 2. Dependency Configurations
Please output the exact contents for the following files:

A) `backend/requirements.txt`:
Include fastapi, uvicorn[standard], piccolo, piccolo_admin, piccolo_api, google-genai, pydantic, pydantic-settings, and any necessary async drivers for SQLite/ASGI functionality. Use specific, stable modern version constraints.

B) `frontend/package.json`:
A standard Vite + Vue 3 initialization configuration. Explicitly include dependencies for `vue`, `vue-router`, `pinia` (or simple state), `tailwindcss`, `postcss`, `autoprefixer`, and `preline`.

### 3. Build & Tooling Configurations
Please output the code for:

C) `frontend/tailwind.config.js` & `frontend/postcss.config.js`:
Configure Tailwind CSS to properly parse Vue files, and crucially, include the configuration/plugin setup required for Preline CSS components to function correctly.

D) Root level `.gitignore`:
A combined, clean .gitignore that blocks common Python artifacts (`.venv`, `__pycache__`, `.pytest_cache`, `.piccolo`), SQLite local files (`*.db`, `*.sqlite3`), and Node/Frontend artifacts (`node_modules`, `dist`, `.env.local`).

Constraints:
- Do not write business logic or API routes yet.
- Ensure all configuration files are complete—do not use placeholders like "# add remaining settings here".
- Keep the design highly modular so the backend and frontend can be decoupled or containerized easily later.

---

## Phase 2: Database Schema and Data Ingestion

### Prompt 2: Database Schema Definition
Moving on to the database layer. I need to set up the core relational schema for our asset tracking and technical maintenance logging platform, and ingest a messy legacy data dump.

Task 1: Define Piccolo ORM Tables
In backend/apps/hardware/tables.py, create the following model:
- HardwareAsset:
    - id (Auto-incrementing primary key Integer)
    - name (Varchar, max length 255)
    - brand (Varchar, max length 100)
    - purchase_date (Date field, nullable)
    - status (Varchar, max length 50)
    - assigned_to (Varchar, max length 255, nullable)
    - notes (Text field, nullable)

Ensure this is compatible with piccolo_admin so it mounts clean list and form views out of the box.

Task 2: Ingestion Seed Script
I extracted a raw data dump from an old unvalidated system. Write an async seed script in backend/scripts/seed_hardware.py to parse this and insert it into the HardwareAsset table.

Two rules for the script:
1. Fix the broken JSON syntax anomalies (missing/misplaced brackets, dangling comma strings) directly so it can actually load as a valid Python list of dicts.
2. For the main loop logic, map the fields directly using standard dictionary key lookups (e.g., pulling purchaseDate and pushing it straight into purchase_date). Let's avoid writing defensive validation or data-scrubbing layers in the script for now—I want to establish a straightforward ingestion pipeline baseline first.

[Raw data dump with malformed JSON was provided here]

Task 3: Admin Mounting
Show me the routing hook needed in backend/main.py to mount the ASGI piccolo_admin app directly onto our FastAPI instance under the /admin/ endpoint.

Give me the complete file implementations with zero placeholders.

### Prompt 3: Database Initialization and Migration
Now that our tables are defined and the seed script is ready, I need to initialize the database and run the ingestion pipeline.

Can you walk me through the exact terminal commands to:
1. Create and run the initial Piccolo migrations to generate our SQLite database file and the HardwareAsset table.
2. Execute the backend/scripts/seed_hardware.py script within our async environment context to populate the database with that legacy dump.

Also, if we need a quick way to run the script asynchronously via a simple CLI task or a temporary custom command wrapper (since it uses async loops), provide the cleanest Python snippet or execution pattern to trigger it.

---

## Phase 3: Security Middleware Implementation

### Prompt 4: Security Middleware Layer
Next up is securing our FastAPI ASGI pipelines. I need to implement a robust, native security middleware layer to wrap our API routes before we build out the AI-native service modules.

Please provide the complete implementation for `backend/apps/security/middleware.py` and the integration hook inside `backend/main.py`.

Requirements:
1. Strict CORS Validation: Configure FastAPI's built-in CORSMiddleware with strict origin allowances (prepared for our Vue 3 dev and production domains).
2. Native IP/Token-Based Rate Limiter: Implement a lightweight, high-performance async rate-limiting middleware layer. For this MVP layer, let's keep it clean using an in-memory sliding window cache tracking client IPs/Auth tokens to avoid adding system dependencies like Redis just yet.
3. CSRF Verification Blocks: Add a middleware state checker to validate incoming mutable states (POST, PUT, DELETE) against secure client headers.
4. JWT & Session State Verification: Integrate `piccolo_api`'s session/token verification mechanics to safely authenticate incoming client requests, ensuring unauthenticated traffic hits a clean 401 Unauthorized block early in the ASGI life cycle.

Give me the raw, complete file implementations with no omitted blocks or shorthand notation so I can wire this straight into our core backend app.

---

## Phase 4: AI Features Integration

### Prompt 5: AI Service Layer
Time to build out the AI-native service layer. We are integrating the modern `google-genai` SDK to run diagnostics and summarize data using the `gemini-2.5-flash` model.

I need a clean, decoupled service architecture in `backend/apps/ai/services.py` along with an API router endpoint in `backend/apps/ai/router.py`.

Requirements:
1. Schema Enforcement: Define a strict Pydantic model (`HardwareDiagnosticReport`) to handle the structured output from Gemini. It needs to include fields for `health_score` (int), `detected_issues` (list of strings), and `maintenance_urgency` (string enum: LOW, MEDIUM, HIGH).
2. Modern SDK Implementation: Use the new `from google import genai` initialization pattern rather than the legacy `google-generativeai` package. Utilize `client.aio` for native asynchronous calls so we don't block the ASGI main loop.
3. Strict Structured Outputs: Configure the generation request to pass our Pydantic model directly into the SDK's native structured output configuration (`response_schema`) so the model is forced to return valid JSON that conforms exactly to our data validation layer.
4. Error Handling: Wrap the async API call in a robust try/except block to handle API rate limits, timeouts, or credential missing states gracefully, mapping failures back to clean FastAPI HTTP exceptions.

Provide the complete file implementations with full import statements and zero placeholder logic.

---

## Phase 5: Frontend Integration

### Prompt 6: Frontend Dashboard and API Integration
I need to wire the backend API to the frontend dashboard logic. Create a Vue 3 dashboard that displays hardware assets from the backend API with the following features:

1. Create a device store using Pinia to manage hardware asset state
2. Implement API calls to fetch hardware data from the backend endpoints
3. Build a dashboard component that displays the assets in a clean, modern UI using Tailwind CSS and Preline components
4. Add filtering and search capabilities for the asset list
5. Implement proper error handling and loading states
6. Ensure the frontend properly handles CSRF tokens for API requests

### Prompt 7: Chatbot Interface
Implement a chatbot interface that connects to the AI diagnostic service. The chatbot should:

1. Provide a clean chat UI using Vue 3 and Tailwind CSS
2. Allow users to ask questions about hardware assets
3. Send requests to the AI service endpoint
4. Display structured diagnostic reports in a user-friendly format
5. Handle conversation state and history

---

## Phase 6: Production Deployment

### Prompt 8: Production-Ready Backend Configuration
I need to make the backend production-ready with the following enhancements:

1. Migrate from Piccolo ORM to SQLAlchemy with Alembic for migrations
2. Replace piccolo_admin with SQLAdmin for the admin interface
3. Integrate SQLite Cloud for production database hosting
4. Implement comprehensive security layer:
   - JWT authentication for API endpoints
   - CSRF protection for all mutable operations
   - CORS configuration for production domains
   - Session management and validation
5. Add Swagger/OpenAPI documentation
6. Implement health check endpoint for monitoring
7. Audit and secure all environment variables and secrets
8. Configure proper logging and error handling for production

### Prompt 9: Deployment Configuration
Configure the application for deployment on Render/FastAPI Cloud:

1. Set up proper pyproject.toml configuration with canonical package structure
2. Configure Python version requirements (Python 3.11.9)
3. Set up proper entrypoint configuration
4. Align all configuration files for deployment
5. Implement proper dependency management
6. Add Procfile for process management
7. Configure environment-specific settings for staging and production

---

## Phase 7: Bug Fixes and Refinements

### Prompt 10: CSRF and CORS Fixes
Fix the login flow that was broken by unconditional CSRF validation. The middleware should:

1. Allow CSRF token endpoint to be publicly accessible
2. Properly handle CORS preflight requests
3. Only enforce CSRF validation on mutable operations (POST, PUT, DELETE)
4. Reorder middleware to ensure CORS preflight is handled before CSRF validation

### Prompt 11: Frontend API Integration Fixes
Fix syntax errors in the frontend device.js fetch calls to ensure:

1. Proper error handling for API responses
2. Correct CSRF token inclusion in headers
3. Proper JSON parsing and error handling
4. Clean integration with the production backend URL

### Prompt 12: Cross-Domain Cookie Configuration
Configure CSRF for cross-domain cookies in production:

1. Set proper cookie attributes (SameSite, Secure, HttpOnly)
2. Configure CORS to allow credentials
3. Ensure frontend can properly authenticate with backend across domains
4. Update frontend to use production backend URL

---

## Phase 8: Documentation

### Prompt 13: Documentation Updates
Create comprehensive documentation for the project including:

1. API documentation (API_DOCUMENTATION.md)
2. Migration guide (MIGRATION_GUIDE.md)
3. SQLAdmin setup guide (SQLADMIN_GUIDE.md)
4. SQLite Cloud setup instructions (SQLITE_CLOUD_SETUP.md)
5. AI Log documentation to track AI-assisted development

---

## Summary

The development of The Rental Shop followed a systematic progression from initial setup through production deployment:

1. **Foundation**: Repository scaffolding with FastAPI, Vue 3, and Piccolo ORM
2. **Data Layer**: Database schema definition and legacy data ingestion
3. **Security**: Comprehensive middleware for CORS, rate limiting, CSRF, and JWT authentication
4. **AI Integration**: Google GenAI SDK integration for hardware diagnostics
5. **Frontend**: Vue 3 dashboard with Pinia state management and chatbot interface
6. **Production**: Migration to SQLAlchemy/Alembic, SQLite Cloud integration, and deployment configuration
7. **Refinement**: Bug fixes for CSRF/CORS handling and frontend API integration
8. **Documentation**: Comprehensive guides for API, migrations, and setup

Each phase built upon the previous one, with careful attention to security, scalability, and production readiness.
