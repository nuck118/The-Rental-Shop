# AI Development Log — The Rental Shop

## Project Overview

**Timeline:** 2026-07-01 → 2026-07-04 (4 days)
**Repository:** github.com/nuck118/The-Rental-Shop
**Initial Commit:** `5ca63e6` (2026-07-01 17:08)

### AI Tooling
- **Amazon Q CLI** — Initial scaffolding and boilerplate generation
- **Cline CLI** — Primary development agent for backend logic, middleware, and API routes
- **Claude Code Sonnet** — Frontend component generation and UI design
- **Gemini (google-genai SDK)** — Used at runtime via the AI chatbot service (not for code generation)

### Development Strategy
The initial dataset was intentionally left in a raw, imperfect state to accelerate the initial build phase. AI models correctly identified data quality issues (malformed JSON, inconsistent naming, missing fields, duplicate IDs, invalid dates), but the decision was made to proceed with minimal fixes to prioritize rapid prototyping and architecture validation. Data sanitization was deferred to a later phase.

---

## Phase A — Repository Scaffolding
**Commits:** `5ca63e6` → `9cd4b79`
**Date:** 2026-07-01 17:08 → 2026-07-02 13:47
**Tools:** Amazon Q CLI, Cline CLI

### Prompt
Initialize a repository for an AI-Native Web Application MVP with:
- Backend: FastAPI (Async ASGI native)
- ORM/Database: Piccolo ORM with SQLite, integrated with piccolo_admin
- Security: piccolo_api for auth/session management
- AI Layer: Google GenAI SDK with gemini-2.5-flash
- Frontend: Vue.js 3 (Vite, Composition API, Preline CSS / Tailwind CSS)

### Output
- Project directory structure for `/backend`, `/frontend`, and root configs
- `backend/requirements.txt` with FastAPI, Piccolo ORM, piccolo_admin, piccolo_api, google-genai
- `frontend/package.json` with Vue 3, Vue Router, Pinia, Tailwind CSS, Preline
- `frontend/tailwind.config.js` and `frontend/postcss.config.js`
- Root `.gitignore` blocking Python artifacts, SQLite files, and Node artifacts
- `backend/.env.example` with placeholder configuration

### Result
- Repository scaffolded and pushed as initial commit
- Piccolo ORM chosen as the initial ORM despite known auto-migration limitations — trade-off accepted for rapid setup
- Both backend and frontend build pipelines verified working independently

---

## Phase B — Database Schema & Data Ingestion (Piccolo ORM)
**Commits:** `27893a7` → `1c081a1`
**Date:** 2026-07-02 13:52 → 2026-07-02 13:47 (same window)
**Tools:** Cline CLI

### Prompt
Define Piccolo ORM table `HardwareAsset` with fields: id, name, brand, purchase_date, status, assigned_to, notes. Create async seed script to parse and ingest malformed legacy JSON data. Mount piccolo_admin at `/admin/`.

### Output
- `HardwareAsset` table defined in Piccolo ORM
- Seed script that parsed malformed JSON (syntax errors, duplicate IDs, inconsistent naming)
- piccolo_admin mounted at `/admin/` endpoint
- Initial migration created and applied

### Result
- Schema created and data ingested successfully
- Piccolo's lack of auto-migration support identified as a growing pain point
- Decision made to continue with Piccolo for initial prototyping despite concerns

---

## Phase C — Security Middleware Layer
**Commits:** `e3da340`
**Date:** 2026-07-02 14:13
**Tools:** Cline CLI

### Prompt
Implement security middleware for FastAPI ASGI pipelines: CORS validation, native IP/token-based rate limiter (in-memory sliding window, no Redis), CSRF verification for mutable operations, JWT & session state verification via piccolo_api.

### Output
- `backend/app/security/middleware.py` — Complete ASGI middleware with rate limiting, JWT verification, CSRF protection, CORS enforcement, and security headers
- Integrated into FastAPI app factory in `backend/main.py`
- In-memory `RateLimitStore` using Python `defaultdict` with timestamps

### Result
- Security middleware operational with zero external dependencies
- CSRF and JWT both defaulted to `disabled` for local development (`settings.csrf_enabled = False`, `settings.jwt_enabled = False`)
- Hardware CRUD endpoints intentionally left public for faster iteration, with only `DELETE` requiring admin auth
- Known shortcuts documented: in-memory rate limiting (not Redis), JWT in localStorage (not httpOnly cookies)

---

## Phase D — AI Service Layer & ORM Migration (Piccolo → SQLAlchemy)
**Commits:** `5aaa339`
**Date:** 2026-07-02 19:21
**Tools:** Cline CLI, Claude Code Sonnet

### Prompt
Build AI-native service layer using modern `google-genai` SDK with `gemini-2.5-flash`. Create decoupled architecture with Pydantic schemas, async service layer, and API router. Also: migrate from Piccolo ORM to SQLAlchemy + Alembic.

### Output
**AI Service:**
- `backend/app/ai/services.py` — `DeviceRecommendationService` with async Gemini client
- `backend/app/ai/schemas.py` — Pydantic models: `ChatMessage`, `DeviceRecommendation`, `ChatbotResponse`
- `backend/app/ai/router.py` — `POST /api/ai/chat`, `GET /api/ai/health`
- Uses modern `from google import genai` SDK (not legacy `google-generativeai`)
- Async non-blocking calls via `client.aio.models.generate_content()`

**ORM Migration:**
- Piccolo ORM replaced with SQLAlchemy + Alembic
- `HardwareAsset`, `User`, `AuditLog` models migrated
- `backend/alembic/` — full migration infrastructure with versioned migration files
- `piccolo_admin` replaced with SQLAdmin panel at `/admin`
- `backend/app/core/database.py` — SQLAlchemy engine and session factory
- `backend/app/core/deps.py` — FastAPI dependency injection for JWT auth

### Result
- **Major architectural decision**: Piccolo ORM abandoned due to lack of auto-migration support — this is the single biggest pivot in the project
- SQLAdmin provides a more maintainable admin interface with proper audit logging
- AI service fully functional: users can describe needs in natural language and get device recommendations
- Migration documented in `MIGRATION_GUIDE.md`
- Alembic migrations versioned: `001_initial`, `002_add_user_audit`

---

## Phase E — Frontend Integration & Dashboard
**Commits:** `f3bf10f`
**Date:** 2026-07-03 00:17
**Tools:** Claude Code Sonnet, Cline CLI

### Prompt
Wire backend API to frontend dashboard. Implement sign-in page with JWT token storage, dashboard with three tabs (Available, My Rentals, All Devices), device cards with rent/return actions, search/filter/sort/pagination, and AI chat assistant panel.

### Output
- `frontend/src/views/SigninView.vue` — Login page with JWT token storage in localStorage
- `frontend/src/views/DashboardView.vue` — Main dashboard with tab navigation
- `frontend/src/components/DeviceCard.vue` — Device card component with rent/return buttons
- `frontend/src/components/ChatAssistant.vue` — Floating AI chatbot panel
- `frontend/src/stores/auth.js` — Pinia store for authentication state
- `frontend/src/stores/device.js` — Pinia store for device list, search, filter, sort, pagination
- `frontend/src/stores/chat.js` — Pinia store for chat messages and API communication
- `frontend/src/router/index.js` — Vue Router with auth guard and catch-all redirect

### Result
- Full-stack integration verified: frontend communicates with backend API
- Auth flow working: login → JWT → localStorage → Bearer header on API calls
- Device list with search, filter (by status/brand), sort (by name/brand/date), and pagination
- Rent/return buttons trigger API calls with toast notifications for success/error
- Chat assistant panel toggleable via floating button

---

## Phase F — Production Deployment & Build Debugging
**Commits:** `7082b7c` → `2e8ec53`
**Date:** 2026-07-03 10:26 → 2026-07-03 10:43
**Tools:** Cline CLI

### Prompt
Prepare backend for production deployment. Fix build issues on FastAPI Cloud / Render.

### Debugging Sequence

| Commit | Issue | Resolution |
|--------|-------|------------|
| `7082b7c` | SQLite Cloud integration | Production-ready backend with SQLite Cloud, JWT/CSRF/CORS security, secrets audit |
| `d3a0982` | Login broken by unconditional CSRF validation | Made CSRF validation conditional on `settings.csrf_enabled` |
| `abd2645` | sqladmin version conflict blocking build | Pinned compatible sqladmin version |
| `a9aca18` | Python 3.14 missing pydantic wheels | Downgraded to Python 3.12 |
| `923bce9` | Python 3.12 build issue | Downgraded to Python 3.11.9 |
| `793b35f` → `a8717a1` | Multiple pyproject.toml alignment issues | Fixed entrypoint path, package config, build deps |
| `e29e258` | Render deployment config | Aligned config files and dependencies |
| `9baca1e` | Synced dependency manifest | Final build verification |

### Result
- Backend successfully deployed to Render at `https://the-rental-shop.onrender.com`
- Frontend deployed to Vercel at `https://therentalshop.vercel.app`
- Multiple Python version compatibility issues resolved
- sqladmin version pinned to avoid breaking changes
- Build pipeline documented for repeatability

---

## Phase G — CORS & Cross-Domain Debugging Marathon
**Commits:** `af204a0` → `37af8a3` (14 commits)
**Date:** 2026-07-03 13:56 → 2026-07-03 17:42
**Tools:** Cline CLI

### Prompt
Fix CORS issues between Vercel frontend and Render backend. Ensure login, API calls, admin panel, and AI chatbot work across domains.

### Debugging Sequence

| # | Commit | Fix | Result |
|---|--------|-----|--------|
| 1 | `af204a0` | Added `/health` endpoint, added production domains to CORS origins | Health check now accessible |
| 2 | `e0edb7f` | Configured frontend stores to use full production backend URL | API calls now reach Render |
| 3 | `890c583` | Configured CSRF for cross-domain cookies (`SameSite=None`, `Secure`) | Cross-domain CSRF operational |
| 4 | `77860da` | Fixed syntax errors in device.js fetch calls | Frontend API calls no longer crash |
| 5 | `7dcdc2d` | Added `/api/auth/csrf-token` to public paths | CSRF token retrievable without auth |
| 6 | `71998e9` | Reordered middleware: CORSMiddleware before SecurityMiddleware | Preflight requests still blocked |
| 7 | `784e049` | Allowed OPTIONS requests to bypass security middleware | Preflight now passes through |
| 8 | `64fb0ec` | Added wildcard CORS for debugging, improved OPTIONS bypass | Root cause identified: CSP blocking cross-origin |
| 9 | `c132a44` | Reversed middleware order again | Back to working state |
| 10 | `8bfab69` | Temporarily disabled CSRF to isolate CORS issue | Confirmed CSRF not the blocker |
| 11 | `c067a8c` | Handled OPTIONS preflight directly in SecurityMiddleware | Clean OPTIONS bypass without side effects |
| 12 | `a569e7c` | CORS first, Security last in middleware chain | Final middleware order established |
| 13 | `d7b6b7f` | Updated admin session cookies for cross-domain | Admin login works across domains |
| 14 | `efb7728` | Disabled all security for demo (CORS, CSRF, JWT) | Demo mode: all features accessible without auth |
| 15 | `8b986bb` | Fixed CORS wildcard — disabled credentials flag | Production CORS without wildcard |
| 16 | `e97a2f9` | Final CORS config for Vercel frontend | Stable cross-domain configuration |
| 17 | `37af8a3` | Fixed Pydantic validation error for `cors_origins` field | Config no longer crashes on startup |
| 18 | `8506c03` | CORS credentials, timeout handling, Vercel preview URL support | Production-ready CORS with preview deployment support |

### Key Outcomes

**Middleware Order (final):**
```
CORSMiddleware (runs last, outermost)
    ↓
SecurityMiddleware (rate limit → JWT → CSRF → headers)
    ↓
Route Handler
```

**Lessons Learned:**
1. In FastAPI, middleware runs in **reverse order** of registration — CORSMiddleware must be added first to run outermost
2. OPTIONS preflight must bypass ALL security checks, not just CORS
3. `SameSite=None` requires `Secure=True` (HTTPS only)
4. Content-Security-Policy headers can silently block cross-origin API calls even when CORS is correctly configured
5. Vercel preview deployments need dynamic CORS origin support (solved via `VERCEL_URL` env var)

---

## Phase H — Data Validation, Quarantine & Admin Features
**Commits:** `d676e2e` → `04a8528`
**Date:** 2026-07-03 18:11 → 2026-07-03 19:12
**Tools:** Cline CLI

### Prompt
Add data validation and quarantine system for hardware imports. Implement Pydantic-based validation pipeline that quarantines invalid records instead of silently dropping them.

### Output
- `backend/app/core/validation.py`:
  - `HardwareImportSchema` (Pydantic) — field validators for name, brand, date, status normalization
  - `ValidationResult` — validation outcome with error collection and severity classification
  - `validate_hardware_record()` — single-record validation
  - `quarantine_record()` — persists failed records to `data_quarantine` table
  - `import_hardware_batch()` — bulk import with per-record quarantine
- `DataQuarantine` model — stores raw input, errors, severity, source, resolved status
- `ReturnRecord` model — tracks device returns with condition (perfect/damaged/other) and descriptions
- `backend/app/core/user.py` — User CRUD utilities (create, update, activate/deactivate, promote/demote admin)
- `backend/app/core/audit.py` — Audit logging helpers (`log_audit()`, `get_user_audit_history()`, etc.)
- SQLAdmin views for `DataQuarantine` and `ReturnRecord`
- Admin dashboard metrics (user count, hardware counts by status)
- Alembic migrations: `003_add_quarantine_and_repair_flag`, `004_add_return_records`

### Result
- API endpoints (`POST/PUT /api/hardware`) now validate input through the validation pipeline
- Invalid records are quarantined with full context (raw input, errors, severity, source)
- Admin can review quarantined records in the SQLAdmin panel and mark them resolved
- Device returns now create permanent `ReturnRecord` entries with condition tracking
- Previous shortcuts ("form-parameter endpoints", "no rental history tracking") documented in README

---

## Phase I — Frontend UI Refinements & Overhaul
**Commits:** `2fdbb4b` → `80f9783`
**Date:** 2026-07-03 18:11 → 2026-07-04 14:11
**Tools:** Claude Code Sonnet, Cline CLI

### Prompt
Polish the frontend UI: mobile-friendly dashboard, search/sort/filter improvements, skeleton loaders, inactivity auto-logout, modern industrial aesthetic, return modal with condition selection, and AI chatbot UX.

### Changes (Chronological)

| Date | Commit | Change |
|------|--------|--------|
| Jul 3 18:11 | `2fdbb4b` | Mobile-friendly dashboard layout |
| Jul 3 19:12 | `04a8528` | "Modern Industrial Workshop" aesthetic — refined color palette, typography, spacing |
| Jul 4 12:03 | `27054a0` | UI overhaul: editorial minimalism, skeleton loaders, inactivity auto-logout (30 min), catch-all 404 redirect |
| Jul 4 12:30 | `5535b75` | Configuration optimizations for staging deployment |
| Jul 4 12:35 | `2da4057` | Favicon updated to laptop emoji |
| Jul 4 12:55 | `a6024a2` | Fixed dashboard search, sort, and filter interactions |
| Jul 4 13:09 | `b4f26ca` | Fixed CORS and CSP for AI chatbot cross-origin API calls |
| Jul 4 13:18 | `9265711` | Modernized dashboard header and mobile experience (hamburger menu, responsive tabs) |
| Jul 4 13:26 | `3169301` | Redesigned search box styling to match modern UI |
| Jul 4 13:28 | `370f0ef` | Added sort controls to mobile filter panel, moved profile icon to top-right on mobile |
| Jul 4 13:38 | `9f64f3a` | Chatbot button changed to circular, themed with primary red |
| Jul 4 14:11 | `80f9783` | **Device return logic with condition selection** — `ReturnModal.vue` with three options (perfect → Available, damaged → Repair, other → Repair with description) |

### Key Features Delivered
- `ReturnModal.vue` — Condition selection modal that determines device disposition
- Inactivity auto-logout (30 min timeout) with session clear
- Skeleton loaders during data fetching (replaced simple spinner)
- Mobile-responsive navigation with hamburger menu
- Catch-all route redirects based on auth state
- Toast notifications for rent/return success/failure

---

## Phase J — SQLite Cloud & Final Production Stabilization
**Commits:** `bc95925`
**Date:** 2026-07-03 18:47
**Tools:** Cline CLI

### Prompt
Fix SQLite Cloud session cleanup errors causing 500 responses. Suppress rollback/commit/close errors when session is already closed.

### Fix
- `bc95925` — Suppressed sqlitecloud rollback/commit/close errors to prevent 500 on session cleanup
- Error occurs when SQLAlchemy session tries to close a SQLite Cloud connection that was already terminated by the server

### Result
- Production server no longer returns sporadic 500 errors during session cleanup
- SQLite Cloud documented as a known limitation (not ideal for production — PostgreSQL recommended)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total commits** | 68 |
| **Timeline** | 2026-07-01 → 2026-07-04 (4 days) |
| **Backend** | FastAPI, SQLAlchemy + Alembic, SQLite/SQLite Cloud |
| **Frontend** | Vue 3, Pinia, Vue Router, Tailwind CSS, Preline |
| **AI** | Google GenAI (gemini-2.5-flash) |
| **Admin** | SQLAdmin with session auth, 5 model views |
| **Deployment** | Frontend: Vercel · Backend: Render |
| **Known shortcuts** | 7 documented in README with rationale and future paths |

### Architecture Pivots
1. **Piccolo ORM → SQLAlchemy + Alembic** (Phase D) — Lack of auto-migration support drove the migration
2. **Security: all-off → all-on → selectively on** (Phase G) — CORS/CORS debugging revealed middleware ordering complexity
3. **Flat form params → Pydantic validation** (Phase H) — Data quality issues drove validation pipeline creation

### Key Files Referenced
- `backend/app/main.py` — FastAPI app factory
- `backend/app/security/middleware.py` — ASGI security middleware
- `backend/app/core/validation.py` — Data validation & quarantine
- `backend/app/admin.py` — SQLAdmin model views (5 registered)
- `backend/app/admin_auth.py` — Admin authentication backend
- `backend/app/ai/services.py` — AI recommendation engine
- `frontend/src/views/DashboardView.vue` — Main dashboard
- `frontend/src/components/ReturnModal.vue` — Return condition modal

---

## Corrections: AI Bugs & Fixes

This section documents specific moments where the AI produced suboptimal, buggy, or insecure code, and how each was identified and corrected.

---

### 1. CORS Middleware Order (Phase G — 14 commits to fix)

**The Bug:** The AI initially placed `CORSMiddleware` after `SecurityMiddleware` in the FastAPI middleware chain. In FastAPI, middleware runs in **reverse order** of registration — the first middleware added runs outermost (last). This meant `SecurityMiddleware` was intercepting all CORS preflight `OPTIONS` requests before `CORSMiddleware` could handle them, returning 401/403 instead of 200 with CORS headers.

**How It Was Identified:** The frontend console showed `CORS Missing Allow Origin` errors on every API call. The browser's preflight `OPTIONS` requests were returning non-2xx responses. Network tab inspection confirmed the preflight was being blocked by the security layer, not by CORS configuration.

**The Fix (14 attempts, commits `71998e9` → `a569e7c`):**
1. First attempt: Reordered middleware so `CORSMiddleware` was added first → still blocked
2. Added OPTIONS bypass in `SecurityMiddleware` → preflight passed but CSP still blocked
3. Added wildcard CORS for debugging → root cause identified (CSP headers, not CORS)
4. Reversed middleware order again → back to working state
5. Temporarily disabled CSRF to isolate → confirmed CSRF not the blocker
6. Final fix: `SecurityMiddleware` handles OPTIONS directly at the top of `dispatch()` (lines 123-132), returning 200 with CORS headers before any rate limit or auth checks. Middleware order finalized as CORSMiddleware first, SecurityMiddleware second.

**Lesson:** Never trust middleware order assumptions. Test preflight requests explicitly. OPTIONS must bypass ALL security, not just CORS.

---

### 2. Unconditional CSRF Validation Breaking Login (Commit `d3a0982`)

**The Bug:** The AI implemented CSRF validation in the login endpoint that ran **unconditionally**, regardless of the `settings.csrf_enabled` flag. When CSRF was disabled in `.env` (the default for local development), the login endpoint still tried to validate a CSRF token that didn't exist, returning 403 Forbidden on every login attempt.

**How It Was Identified:** Local development login flow was completely broken. The frontend received 403 responses on `POST /api/auth/login` even though the credentials were correct. The error message pointed to CSRF validation failure.

**The Code (before fix, in `backend/app/api/routes/auth.py`):**
```python
# Bug: CSRF validation ran unconditionally
await csrf_protect.validate_csrf(request)
```

**The Fix:**
```python
# Fix: Only validate CSRF if CSRF protection is enabled
if settings.csrf_enabled:
    await csrf_protect.validate_csrf(request)
```

**Lesson:** Feature flags in settings must be checked at every enforcement point, not just at middleware registration. A single missed conditional can break the entire auth flow.

---

### 3. Pydantic `cors_origins` Type Mismatch (Commit `37af8a3`)

**The Bug:** The AI defined `cors_origins` in `Settings` as `list[str] | None = None`, then tried to assign a dynamically generated list in `__init__`. Pydantic's validation ran **after** `__init__` completed, and the field's setter expected a `list[str]` but received a value that didn't match the type annotation after Pydantic's internal processing. This caused a `ValidationError` on every startup.

**How It Was Identified:** The backend crashed immediately on `uvicorn` startup with a Pydantic validation error for the `cors_origins` field. The traceback pointed to the `__init__` method where `self.cors_origins = self._get_cors_origins()` was called.

**The Fix:**
```python
# Bug: Pydantic re-validated after __init__ assignment
def __init__(self, **data):
    super().__init__(**data)
    if self.cors_origins is None:
        self.cors_origins = self._get_cors_origins()  # Pydantic rejected this

# Fix: Use model_config with extra="ignore" and handle defaults differently
model_config = SettingsConfigDict(env_file=".env", extra="ignore")
# The cors_origins default is computed in _get_cors_origins() and assigned
# before Pydantic validation by setting it in __init__ before super().__init__
```

**Lesson:** Pydantic v2's `__init__` behavior differs from v1. Mutating fields after `super().__init__()` can trigger re-validation. The safer pattern is to compute defaults before calling `super().__init__()` or use `field_validator` with `mode="before"`.

---

### 4. Redundant `fetchWithTimeout` — Double Timeout Race (Frontend)

**The Bug:** The AI generated a `fetchWithTimeout` utility in `frontend/src/stores/device.js` and `frontend/src/stores/auth.js` that used **two competing timeout mechanisms** simultaneously:

```javascript
const fetchWithTimeout = (url, options = {}) => {
  return Promise.race([
    fetch(url, { ...options, signal: AbortSignal.timeout(API_TIMEOUT) }),
    // BUG: This setTimeout never resolves — it only rejects
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timeout...")), API_TIMEOUT)
    ),
  ]);
};
```

**The Problem:**
1. `AbortSignal.timeout(API_TIMEOUT)` already aborts the fetch after 120s — the manual `setTimeout` is redundant
2. The `Promise.race` with a timer that **only rejects** creates an unhandled promise rejection if the fetch succeeds before the timeout: the `setTimeout` callback fires later and rejects a promise that `Promise.race` has already discarded
3. Node.js (and some browsers) log unhandled promise rejections as warnings, which can mask real errors

**How It Was Identified:** Browser console showed intermittent `Unhandled Promise Rejection` warnings on successful API calls. The warning message referenced the timeout error string, but the API call had actually succeeded.

**The Fix:**
```javascript
// Fix: Use AbortSignal.timeout() alone — it handles both abort and cleanup
const fetchWithTimeout = (url, options = {}) => {
  return fetch(url, { ...options, signal: AbortSignal.timeout(API_TIMEOUT) });
};
```

**Lesson:** Never race a fetch against a timer that only rejects. Either use `AbortSignal.timeout()` (modern browsers) or implement a proper `AbortController` that cleans up the timer on success. Unhandled rejections from discarded promises are a subtle bug that can mask real failures.

---

### 5. Security Headers Blocking Cross-Origin AI Chat (Phase G, Commit `b4f26ca`)

**The Bug:** The AI's `Content-Security-Policy` header was set to `default-src 'self'` for all non-admin responses. This blocked the frontend's AI chatbot from making API calls to `https://generativelanguage.googleapis.com` (the Gemini API), because `connect-src` fell back to `default-src 'self'` which only allows the origin itself.

**How It Was Identified:** The AI chatbot worked in local development (where the frontend proxy handled the request) but failed in production. The browser console showed `Refused to connect to 'https://generativelanguage.googleapis.com/...' because it violates the document's Content Security Policy.`

**The Fix:**
```python
# Before: CSP blocked all external API calls
response.headers["Content-Security-Policy"] = "default-src 'self'"

# After: Explicitly allow Gemini API in connect-src
response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' https://generativelanguage.googleapis.com;"
```

**Lesson:** CSP headers are silent blockers — they don't return HTTP errors, they just prevent the browser from making the request. Always check CSP when debugging cross-origin API failures. The `connect-src` directive must explicitly include any external APIs the frontend calls directly.
