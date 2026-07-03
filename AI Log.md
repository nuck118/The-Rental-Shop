# AI Development Log - The Rental Shop

## Project Overview

### Tooling Stack
The following AI tools and models were used concurrently during development:
- **Amazon Q CLI** (in WordPress environment)
- **Cline CLI**
- **Antigravity**
- **Claude Code Sonnet**
- **Gemini 3.1 Pro**
- **DeepSeek V4 Flash**

### Development Strategy
**Data Approach:** The initial dataset was intentionally left in a raw, imperfect state to accelerate the initial build phase. AI models correctly identified data quality issues (malformed JSON, inconsistent naming, missing fields, duplicate IDs, invalid dates), but the decision was made to proceed with minimal fixes to prioritize rapid prototyping and architecture validation. Data sanitization was deferred to a later phase.

**Code Integrity Challenges:** AI tools frequently produced duplicate code segments, incomplete implementations, and vulnerable code patterns. To address this, comprehensive audit prompts were integrated between each development phase to validate code integrity and security.

---

## Development Process (A-Z)

### A. Repository Scaffolding

**Prompt:**
Act as an expert Senior Python Backend Engineer and Enterprise Solutions Architect. Initialize a repository for an AI-Native Web Application MVP with the following stack:
- Backend: FastAPI (Async ASGI native)
- ORM/Database: Piccolo ORM with SQLite, integrated with piccolo_admin
- Security: piccolo_api for auth/session management
- AI Layer: Google GenAI SDK (google-genai) with 'gemini-2.5-flash'
- Frontend: Vue.js 3 (Vite, Composition API, Preline CSS / Tailwind CSS)

Generate:
1. Project directory structure for /backend, /frontend, and root configs
2. `backend/requirements.txt` with fastapi, uvicorn[standard], piccolo, piccolo_admin, piccolo_api, google-genai, pydantic, pydantic-settings
3. `frontend/package.json` with vue, vue-router, pinia, tailwindcss, postcss, autoprefixer, preline
4. `frontend/tailwind.config.js` and `frontend/postcss.config.js` for Tailwind + Preline
5. Root `.gitignore` blocking Python artifacts, SQLite files, and Node artifacts

Constraints: No business logic, complete configurations (no placeholders), modular design for decoupling.

**Audit:**
1. Check for duplicate code segments across configuration files
2. Verify all imports and dependencies are correctly specified
3. Ensure no placeholder or incomplete implementations exist
4. Validate file structure matches specified architecture
5. Check for security vulnerabilities in initial configuration
6. Verify all configuration files are complete and functional

### B. Database Schema and Data Ingestion

**Prompt:**
Set up the core relational schema for asset tracking and ingest a legacy data dump.

**Tasks:**
1. Define Piccolo ORM table `HardwareAsset` in `backend/apps/hardware/tables.py` with fields: id (auto-increment), name (varchar 255), brand (varchar 100), purchase_date (date, nullable), status (varchar 50), assigned_to (varchar 255, nullable), notes (text, nullable). Ensure piccolo_admin compatibility.

2. Create async seed script `backend/scripts/seed_hardware.py` to parse and insert legacy data. Fix JSON syntax anomalies and map fields directly (e.g., purchaseDate → purchase_date). No defensive validation—baseline ingestion only.

3. Show routing hook in `backend/main.py` to mount piccolo_admin at `/admin/` endpoint.

**Raw Data:** Malformed JSON with syntax errors, duplicate IDs, inconsistent naming, missing fields.

**Audit:**
1. Verify Piccolo ORM table definitions match specified schema exactly
2. Check for SQL injection vulnerabilities in seed script
3. Ensure seed script handles edge cases in malformed data
4. Validate admin mounting configuration is secure
5. Check for duplicate or redundant database operations
6. Verify database connections are properly closed and managed
7. Ensure seed script doesn't introduce data integrity issues

### C. Database Initialization and Migration

**Prompt:**
Provide terminal commands to:
1. Create and run initial Piccolo migrations to generate SQLite database and HardwareAsset table
2. Execute `backend/scripts/seed_hardware.py` in async environment context
3. Provide Python snippet or execution pattern for async script triggering

**Audit:**
1. Verify migration commands are correct and safe to execute
2. Check for potential data loss scenarios in migration process
3. Ensure async execution pattern is properly implemented
4. Validate seed script execution won't cause race conditions
5. Check for proper error handling in initialization process
6. Verify database file permissions and security settings

### D. Security Middleware Layer

**Prompt:**
Implement robust security middleware for FastAPI ASGI pipelines. Provide complete implementation for `backend/apps/security/middleware.py` and integration in `backend/main.py`.

**Requirements:**
1. Strict CORS validation with origin allowances for Vue 3 dev/production domains
2. Native IP/token-based rate limiter using in-memory sliding window cache (no Redis)
3. CSRF verification for mutable operations (POST, PUT, DELETE)
4. JWT & session state verification via piccolo_api, blocking unauthenticated traffic with 401

**Audit:**
1. Check for CORS misconfigurations allowing unauthorized access
2. Verify rate limiting logic cannot be bypassed
3. Ensure CSRF validation for all mutable operations
4. Check for authentication bypass vulnerabilities
5. Validate session management security against session fixation
6. Verify JWT token validation is properly implemented
7. Check for timing attack vulnerabilities in token comparison
8. Ensure middleware order doesn't create security gaps
9. Verify error messages don't leak sensitive information

### E. AI Service Layer

**Prompt:**
Build AI-native service layer using modern `google-genai` SDK with `gemini-2.5-flash` model. Create decoupled architecture in `backend/apps/ai/services.py` and API router in `backend/apps/ai/router.py`.

**Requirements:**
1. Schema enforcement: Pydantic model `HardwareDiagnosticReport` with health_score (int), detected_issues (list), maintenance_urgency (enum: LOW, MEDIUM, HIGH)
2. Modern SDK: Use `from google import genai` pattern with `client.aio` for async calls
3. Structured outputs: Pass Pydantic model to SDK's `response_schema` for forced JSON conformance
4. Error handling: Robust try/except for rate limits, timeouts, credential issues, mapping to FastAPI HTTP exceptions

**Audit:**
1. Check for API key exposure or hardcoding
2. Verify structured output validation is enforced
3. Ensure error handling doesn't leak sensitive AI responses
4. Check for prompt injection vulnerabilities
5. Validate async calls don't create resource exhaustion
6. Verify rate limiting applied to AI API calls
7. Check for proper user input sanitization before AI
8. Ensure Pydantic models validate all AI responses
9. Verify service handles API quota limits gracefully

### F. Final Codebase Audit

**Audit:**
Perform comprehensive end-to-end audit of entire codebase:
1. Scan for duplicate code patterns across all modules
2. Check for incomplete implementations or TODO comments
3. Verify all imports are used and necessary
4. Check for hardcoded secrets or configuration values
5. Validate error handling is consistent across modules
6. Ensure logging is properly implemented for debugging
7. Check for potential memory leaks in async operations
8. Verify database connection pooling is properly configured
9. Validate all endpoints have proper authentication requirements
10. Check for dependency injection opportunities to improve testability

### G. Production Deployment and CORS Debugging

**Prompt 1 - Health Check Endpoint:**
The deployment platform is returning 404 for /health endpoint. Add a health check endpoint to backend/app/main.py that returns a simple JSON response with status "healthy". This endpoint should be accessible without authentication.

**Audit:**
1. Verify health endpoint returns 200 OK without authentication
2. Check endpoint is not blocked by security middleware
3. Ensure endpoint is in public paths list
4. Validate response format is simple JSON
5. Check endpoint doesn't leak sensitive information

**Prompt 2 - CSRF Token Endpoint Access:**
The /api/auth/csrf-token endpoint is returning 401 Unauthorized. Add this endpoint to the public paths list in backend/app/security/middleware.py so it can be accessed without authentication for initial CSRF token retrieval.

**Audit:**
1. Verify CSRF token endpoint is accessible without auth
2. Check endpoint is in public paths list
3. Ensure endpoint doesn't expose sensitive data
4. Validate CSRF token generation is secure
5. Check endpoint is not rate-limited too aggressively

**Prompt 3 - CORS Configuration:**
Update backend/app/core/config.py to allow CORS from production domains. Add https://therentalshop.vercel.app and https://the-rental-shop.onrender.com to the cors_origins list. Ensure the frontend can make requests to the backend.

**Audit:**
1. Verify all production domains are in allowed origins list
2. Check for security implications of wildcard CORS
3. Ensure credentials are allowed if needed
4. Validate CORS headers are properly configured
5. Check for origin spoofing vulnerabilities

**Prompt 4 - Cross-Domain Cookie Configuration:**
Update backend/app/core/csrf.py to configure cookies for cross-domain requests. Set cookie_samesite to "none" and cookie_secure to True when ENVIRONMENT=production is set. This allows cookies to work between vercel.app and onrender.com domains.

**Audit:**
1. Ensure cross-domain cookies have correct SameSite and Secure attributes
2. Check Secure flag is only set in production
3. Validate cookies are HttpOnly where appropriate
4. Check for cookie-based security vulnerabilities
5. Ensure cookie configuration works with HTTPS

**Prompt 5 - Frontend API URL Configuration:**
Update frontend stores (auth.js, device.js, chat.js) to use full backend URL instead of relative paths. Add API_URL constant using import.meta.env.VITE_API_URL with fallback to https://the-rental-shop.onrender.com. Update all fetch calls to use the full URL.

**Audit:**
1. Verify frontend uses correct backend URL in production
2. Check environment variable is properly configured
3. Ensure fallback URL is correct
4. Validate all fetch calls use the API_URL constant
5. Check for hardcoded URLs in frontend code

**Prompt 6 - Middleware Order:**
Reorder middleware in backend/app/main.py so CORSMiddleware is added BEFORE SecurityMiddleware. In FastAPI, middleware runs in reverse order, so CORSMiddleware needs to be added first to run before SecurityMiddleware and handle CORS preflight requests properly.

**Audit:**
1. Check middleware order doesn't block CORS preflight
2. Verify CORSMiddleware runs before SecurityMiddleware
3. Ensure middleware chain is properly configured
4. Check for middleware conflicts
5. Validate all middleware is necessary

**Prompt 7 - OPTIONS Request Bypass:**
Add OPTIONS request bypass in backend/app/security/middleware.py. Allow CORS preflight requests (OPTIONS method) to pass through immediately without rate limiting or authentication checks. This ensures preflight requests are not blocked by security middleware.

**Audit:**
1. Validate OPTIONS requests bypass security checks
2. Ensure bypass is early in middleware chain
3. Check bypass doesn't create security vulnerabilities
4. Verify preflight requests return proper headers
5. Ensure bypass only applies to OPTIONS method

**Prompt 8 - Wildcard CORS Debugging:**
Temporarily add "*" to cors_origins in backend/app/core/config.py for debugging CORS issues. This allows all origins to bypass CORS checks temporarily. Remember to remove wildcard after debugging is complete and restore to specific domain list.

**Audit:**
1. Ensure wildcard CORS is removed after debugging
2. Check for security implications of wildcard CORS
3. Validate wildcard is only temporary
4. Document why wildcard was needed
5. Ensure specific domains are restored

---

## Summary

This development log documents the iterative AI-assisted development process for The Rental Shop. Each phase (A-F) was followed by comprehensive audit prompts to ensure code integrity, security, and completeness. The concurrent use of multiple AI tools (Amazon Q CLI, Cline CLI, Antigravity, Claude Code Sonnet, Gemini 3.1 Pro, DeepSeek V4 Flash) required regular validation to prevent duplicate code, incomplete implementations, and security vulnerabilities.
