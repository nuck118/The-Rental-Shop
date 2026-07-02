# Dashboard Architecture & Flow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                         │
│                    http://localhost:5173                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Router (Vue Router)                   │  │
│  │  /signin → SigninView                                   │  │
│  │  /dashboard → DashboardView (protected)                 │  │
│  │  / → redirect to /dashboard                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              State Management (Pinia)                    │  │
│  │  ┌────────────────┐  ┌────────────────┐                │  │
│  │  │  Auth Store    │  │ Device Store   │                │  │
│  │  │ - user         │  │ - available    │                │  │
│  │  │ - token        │  │ - rented       │                │  │
│  │  │ - login()      │  │ - history      │                │  │
│  │  │ - logout()     │  │ - fetch*()     │                │  │
│  │  └────────────────┘  └────────────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Components & Views                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ SigninView   │  │ DashboardView│  │ DeviceCard   │  │  │
│  │  │ - form       │  │ - tabs       │  │ - display    │  │  │
│  │  │ - validation │  │ - grids      │  │ - buttons    │  │  │
│  │  │ - error msg  │  │ - table      │  │ - status     │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              HTTP Client (fetch API)                     │  │
│  │  Authorization: Bearer <token>                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                       Backend (FastAPI)                         │
│                    http://localhost:8000                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Security Middleware                         │  │
│  │  - Rate Limiting (100 req/60s)                          │  │
│  │  - JWT Verification                                     │  │
│  │  - CSRF Protection                                      │  │
│  │  - CORS Validation                                      │  │
│  │  - Security Headers                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Routers                                 │  │
│  │  ┌────────────────┐  ┌────────────────┐                │  │
│  │  │  Auth Router   │  │ Hardware Router│                │  │
│  │  │ POST /login    │  │ GET /hardware  │                │  │
│  │  └────────────────┘  └────────────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Database Layer                              │  │
│  │  ┌────────────────┐  ┌────────────────┐                │  │
│  │  │  User Model    │  │ HardwareAsset  │                │  │
│  │  │ - id           │  │ - id           │                │  │
│  │  │ - username     │  │ - name         │                │  │
│  │  │ - password_hash│  │ - brand        │                │  │
│  │  │ - email        │  │ - status       │                │  │
│  │  │ - is_admin     │  │ - assigned_to  │                │  │
│  │  └────────────────┘  └────────────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLite Database                             │  │
│  │              rental_shop.db                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Signin Flow                             │
└─────────────────────────────────────────────────────────────────┘

1. User navigates to http://localhost:5173
   ↓
2. Router checks authentication
   ├─ Not authenticated → redirect to /signin
   └─ Authenticated → redirect to /dashboard
   ↓
3. SigninView displays login form
   ├─ Username input
   ├─ Password input
   └─ Sign In button
   ↓
4. User enters credentials and clicks Sign In
   ↓
5. SigninView.handleSignin() called
   ├─ Validates form (both fields required)
   └─ Calls authStore.login(username, password)
   ↓
6. authStore.login() sends POST request
   ├─ URL: /api/auth/login
   ├─ Body: { username, password }
   └─ Headers: Content-Type: application/json
   ↓
7. Backend validates credentials
   ├─ Query User table for username
   ├─ Verify password hash
   ├─ Check user is active
   └─ Generate JWT token (24-hour expiration)
   ↓
8. Backend returns response
   ├─ Status: 200 OK
   └─ Body: { token, user: { id, username, email, is_admin } }
   ↓
9. authStore stores token
   ├─ localStorage.setItem('token', token)
   ├─ authStore.token = token
   ├─ authStore.user = user
   └─ authStore.isAuthenticated = true
   ↓
10. Router redirects to /dashboard
    ↓
11. DashboardView mounts
    ├─ Checks authentication (✓ authenticated)
    ├─ Fetches available devices
    ├─ Fetches rented devices
    └─ Fetches device history
    ↓
12. Dashboard displays with three tabs
    ├─ Available Devices (grid)
    ├─ Rented Devices (grid)
    └─ History (table)
    ↓
13. User can interact with dashboard
    ├─ Switch between tabs
    ├─ View device details
    ├─ Click Rent/Return buttons
    └─ Click profile menu
    ↓
14. User clicks Sign Out
    ↓
15. authStore.logout() called
    ├─ localStorage.removeItem('token')
    ├─ authStore.token = null
    ├─ authStore.user = null
    └─ authStore.isAuthenticated = false
    ↓
16. Router redirects to /signin
    ↓
17. User is back at login page
```

## Device Fetch Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Device Fetch Flow                              │
└─────────────────────────────────────────────────────────────────┘

DashboardView mounts
    ↓
Check authentication
    ├─ Not authenticated → redirect to /signin
    └─ Authenticated → continue
    ↓
Parallel requests (all three tabs):
    ├─ fetchAvailableDevices(token)
    ├─ fetchRentedDevices(token)
    └─ fetchDeviceHistory(token)
    ↓
For each request:
    ├─ Set loading = true
    ├─ Set error = null
    ├─ Send GET request with Authorization header
    │  ├─ URL: /api/hardware?status=Available (or In Use, or all)
    │  └─ Headers: Authorization: Bearer <token>
    ├─ Backend validates token
    ├─ Backend queries database
    ├─ Backend returns device list
    ├─ Store devices in appropriate array
    ├─ Set loading = false
    └─ Template re-renders
    ↓
Dashboard displays:
    ├─ Available Devices tab (grid of available devices)
    ├─ Rented Devices tab (grid of rented devices)
    └─ History tab (table of all devices)
    ↓
User can:
    ├─ Switch between tabs
    ├─ View device details
    ├─ Click Rent button (available devices)
    └─ Click Return button (rented devices)
```

## Token Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Token Lifecycle                              │
└─────────────────────────────────────────────────────────────────┘

1. User logs in
   ├─ Backend generates JWT token
   ├─ Token expires in 24 hours
   └─ Token returned to frontend
   ↓
2. Frontend stores token
   ├─ localStorage.setItem('token', token)
   └─ authStore.token = token
   ↓
3. Token used in API requests
   ├─ All requests include: Authorization: Bearer <token>
   ├─ Backend validates token signature
   ├─ Backend checks token expiration
   └─ Backend processes request if valid
   ↓
4. Page reload
   ├─ App initializes
   ├─ authStore reads token from localStorage
   ├─ authStore.isAuthenticated = true
   └─ User remains logged in
   ↓
5. Token expires (24 hours)
   ├─ Backend rejects request with 401 Unauthorized
   ├─ Frontend could redirect to /signin
   └─ User must log in again
   ↓
6. User logs out
   ├─ localStorage.removeItem('token')
   ├─ authStore.token = null
   ├─ authStore.isAuthenticated = false
   └─ Router redirects to /signin
```

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    App.vue (Root)                               │
└─────────────────────────────────────────────────────────────────┘
                           ↓
                    RouterView
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                     ↓
   SigninView                          DashboardView
   ├─ Form                             ├─ Header
   │  ├─ Username input                │  ├─ Logo
   │  ├─ Password input                │  ├─ User profile
   │  └─ Sign In button                │  └─ Logout button
   ├─ Error message                    ├─ Tab navigation
   └─ Demo credentials                 ├─ Tab content
                                       │  ├─ Available Devices
                                       │  │  └─ DeviceCard (grid)
                                       │  ├─ Rented Devices
                                       │  │  └─ DeviceCard (grid)
                                       │  └─ History
                                       │     └─ Device table
                                       └─ Loading/Error states
```

## State Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pinia State Flow                              │
└─────────────────────────────────────────────────────────────────┘

Auth Store:
    ├─ user: null → { id, username, email, is_admin }
    ├─ token: null → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ├─ isAuthenticated: false → true
    └─ Methods:
       ├─ login(username, password) → updates user, token, isAuthenticated
       └─ logout() → resets all to null/false

Device Store:
    ├─ availableDevices: [] → [{ id, name, brand, status, ... }]
    ├─ rentedDevices: [] → [{ id, name, brand, status, ... }]
    ├─ deviceHistory: [] → [{ id, name, brand, status, ... }]
    ├─ loading: false → true → false
    ├─ error: null → "error message" → null
    └─ Methods:
       ├─ fetchAvailableDevices(token) → updates availableDevices
       ├─ fetchRentedDevices(token) → updates rentedDevices
       └─ fetchDeviceHistory(token) → updates deviceHistory

Component State:
    ├─ SigninView
    │  ├─ username: ""
    │  ├─ password: ""
    │  ├─ error: ""
    │  └─ loading: false
    └─ DashboardView
       ├─ activeTab: "available"
       └─ showProfileMenu: false
```

## API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Login Request/Response                         │
└─────────────────────────────────────────────────────────────────┘

Frontend Request:
    POST /api/auth/login
    Content-Type: application/json
    
    {
      "username": "admin",
      "password": "admin123"
    }

Backend Processing:
    1. Parse request body
    2. Query User table for username
    3. Verify password hash
    4. Check user is active
    5. Generate JWT token
    6. Return response

Backend Response:
    HTTP 200 OK
    Content-Type: application/json
    
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": true
      }
    }

Frontend Processing:
    1. Store token in localStorage
    2. Update authStore
    3. Redirect to /dashboard

┌─────────────────────────────────────────────────────────────────┐
│              Device List Request/Response                       │
└─────────────────────────────────────────────────────────────────┘

Frontend Request:
    GET /api/hardware?status=Available
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Backend Processing:
    1. Validate JWT token
    2. Query HardwareAsset table
    3. Filter by status
    4. Return device list

Backend Response:
    HTTP 200 OK
    Content-Type: application/json
    
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
      ...
    ]

Frontend Processing:
    1. Store devices in deviceStore
    2. Update component state
    3. Re-render template
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Error Handling Flow                            │
└─────────────────────────────────────────────────────────────────┘

Login Error:
    User enters invalid credentials
        ↓
    Backend returns 401 Unauthorized
        ↓
    Frontend catches error
        ↓
    authStore.login() returns false
        ↓
    SigninView displays error message
        ↓
    User can retry

Device Fetch Error:
    Network error or backend error
        ↓
    Fetch fails
        ↓
    deviceStore catches error
        ↓
    Sets error property
        ↓
    Sets loading = false
        ↓
    DashboardView displays error box
        ↓
    User can retry by switching tabs

Token Expired:
    User makes API request
        ↓
    Backend returns 401 Unauthorized
        ↓
    Frontend could:
        ├─ Redirect to /signin
        ├─ Show error message
        └─ Prompt user to log in again
```

## Responsive Design Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              Responsive Breakpoints                             │
└─────────────────────────────────────────────────────────────────┘

Mobile (< 768px):
    ├─ SigninView
    │  └─ Full width form
    └─ DashboardView
       ├─ Single column grid
       ├─ Stacked layout
       └─ Table scrolls horizontally

Tablet (768px - 1024px):
    ├─ SigninView
    │  └─ Centered form (max-width: 28rem)
    └─ DashboardView
       ├─ Two column grid
       ├─ Responsive spacing
       └─ Table scrolls horizontally

Desktop (> 1024px):
    ├─ SigninView
    │  └─ Centered form (max-width: 28rem)
    └─ DashboardView
       ├─ Three column grid
       ├─ Full width layout
       └─ Table fully visible
```

## Performance Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│              Performance Optimizations                          │
└─────────────────────────────────────────────────────────────────┘

Frontend:
    ├─ Lazy loading views (dynamic imports)
    ├─ Pinia stores for state management
    ├─ Computed properties for derived state
    ├─ Tailwind CSS for minimal CSS
    └─ Vite for fast development

Backend:
    ├─ SQLAlchemy ORM with indexes
    ├─ Database queries optimized
    ├─ JWT tokens (no session storage)
    ├─ In-memory rate limiting
    └─ Async ASGI server

Caching:
    ├─ Token stored in localStorage
    ├─ Devices fetched on dashboard mount
    ├─ No automatic refresh
    └─ Manual refresh by tab switching

Network:
    ├─ Parallel device fetches
    ├─ Minimal payload size
    ├─ Gzip compression
    └─ HTTP/2 support
```

## Security Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Security Flow                                  │
└─────────────────────────────────────────────────────────────────┘

1. User enters credentials
   ↓
2. Frontend sends HTTPS request
   ├─ Credentials sent in request body (not URL)
   └─ HTTPS encrypts transmission
   ↓
3. Backend receives request
   ├─ Validates input
   ├─ Queries database
   └─ Verifies password hash
   ↓
4. Backend generates JWT token
   ├─ Signed with SECRET_KEY
   ├─ Includes expiration (24 hours)
   └─ Returned to frontend
   ↓
5. Frontend stores token
   ├─ localStorage (persistent)
   └─ Included in all API requests
   ↓
6. Backend validates token
   ├─ Verifies signature
   ├─ Checks expiration
   └─ Processes request if valid
   ↓
7. Rate limiting
   ├─ 100 requests per 60 seconds
   ├─ Per IP or per token
   └─ Returns 429 if exceeded
   ↓
8. CORS validation
   ├─ Only allows localhost:5173
   └─ Blocks cross-origin requests
   ↓
9. Security headers
   ├─ X-Content-Type-Options: nosniff
   ├─ X-Frame-Options: DENY
   ├─ X-XSS-Protection: 1; mode=block
   └─ Strict-Transport-Security
```
