# Frontend Setup Guide

## Overview

The frontend is a Vue 3 + Vite application with a modern dashboard for managing hardware rentals. It includes:

- **Signin Page** — User authentication with JWT tokens
- **Dashboard** — Three-tab interface for managing devices:
  - Available Devices — Browse and rent available hardware
  - Rented Devices — View and return currently rented devices
  - History — View complete device inventory history

## Installation

```bash
cd frontend
npm install
```

## Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`.

All `/api` and `/admin` requests are automatically proxied to the backend at `http://localhost:8000`.

## Build for Production

```bash
npm run build
```

Output is in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── assets/
│   │   └── main.css          # Tailwind CSS directives
│   ├── components/
│   │   └── DeviceCard.vue    # Reusable device card component
│   ├── router/
│   │   └── index.js          # Vue Router with auth guards
│   ├── stores/
│   │   ├── auth.js           # Pinia auth store (login/logout)
│   │   └── device.js         # Pinia device store (fetch devices)
│   ├── views/
│   │   ├── SigninView.vue    # Login page
│   │   └── DashboardView.vue # Main dashboard with tabs
│   ├── App.vue               # Root component
│   └── main.js               # App entry point
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Authentication Flow

1. User navigates to `/signin`
2. Enters username and password
3. Frontend calls `POST /api/auth/login`
4. Backend validates credentials and returns JWT token
5. Token is stored in `localStorage`
6. User is redirected to `/dashboard`
7. All subsequent API requests include `Authorization: Bearer <token>` header

## Demo Credentials

```
Username: admin
Password: admin123
```

These are created by the backend seed script (`scripts/seed_admin.py`).

## Key Features

### Signin Page
- Clean, modern UI with gradient background
- Form validation
- Error messages for invalid credentials
- Demo credentials displayed for convenience
- Enter key support for quick login

### Dashboard
- **Header** — User profile with logout button
- **Tab Navigation** — Switch between three views
- **Available Devices Tab**
  - Grid layout of available devices
  - Device cards show name, brand, status, purchase date
  - "Rent" button for each device (feature ready for implementation)
  - Status badge with color coding

- **Rented Devices Tab**
  - Grid layout of currently rented devices
  - "Return" button for each device (feature ready for implementation)
  - Same device card layout as available devices

- **History Tab**
  - Table view of all devices in inventory
  - Sortable columns: Name, Brand, Status, Purchase Date, Assigned To
  - Color-coded status badges
  - Responsive table with horizontal scroll on mobile

### Device Card Component
- Displays device information (name, brand, status)
- Color-coded status badges:
  - Green: Available
  - Blue: In Use
  - Yellow: Repair
  - Gray: Unknown
- Optional action buttons (Rent/Return)
- Hover effects for better UX

## Stores (Pinia)

### Auth Store (`stores/auth.js`)
```javascript
// State
user              // Current user object
token             // JWT token
isAuthenticated   // Boolean flag

// Methods
login(username, password)  // Authenticate user
logout()                   // Clear auth state
```

### Device Store (`stores/device.js`)
```javascript
// State
availableDevices  // Array of available devices
rentedDevices     // Array of rented devices
deviceHistory     // Array of all devices
loading           // Loading state
error             // Error message

// Methods
fetchAvailableDevices(token)  // Fetch available devices
fetchRentedDevices(token)     // Fetch rented devices
fetchDeviceHistory(token)     // Fetch all devices
```

## API Integration

The frontend communicates with the backend via these endpoints:

### Authentication
- `POST /api/auth/login` — User login

### Hardware
- `GET /api/hardware?status=Available` — List available devices
- `GET /api/hardware?status=In Use` — List rented devices
- `GET /api/hardware` — List all devices (history)

All requests include the JWT token in the `Authorization` header:
```
Authorization: Bearer <token>
```

## Styling

The project uses:
- **Tailwind CSS** — Utility-first CSS framework
- **Preline** — Tailwind component library
- **PostCSS** — CSS processing

### Tailwind Configuration
- Configured for Vue files in `src/`
- Preline plugin enabled for pre-built components
- Custom colors and spacing available

## Router Guards

The router includes authentication guards:
- Routes with `meta: { requiresAuth: true }` require valid JWT token
- Unauthenticated users are redirected to `/signin`
- Authenticated users accessing `/signin` are redirected to `/dashboard`

## Environment Variables

No environment variables are required for the frontend. The Vite config automatically proxies API requests to `http://localhost:8000`.

To change the backend URL, edit `vite.config.js`:
```javascript
proxy: {
  '/api': 'http://your-backend-url:8000',
  '/admin': 'http://your-backend-url:8000',
}
```

## Troubleshooting

### "Invalid credentials" error
- Verify backend is running at `http://localhost:8000`
- Check that admin user was created: `python scripts/seed_admin.py`
- Verify credentials: admin / admin123

### API requests failing
- Check browser console for CORS errors
- Verify backend CORS configuration in `.env`
- Ensure `CORS_ORIGINS` includes `http://localhost:5173`

### Token not persisting
- Check browser localStorage is enabled
- Verify token is being stored: `localStorage.getItem('token')`
- Check token expiration (24 hours from login)

### Devices not loading
- Verify backend is running
- Check that hardware was seeded: `python scripts/seed_hardware.py`
- Verify token is valid and not expired
- Check browser console for API errors

## Next Steps

To implement the rent/return functionality:

1. Create endpoints in backend:
   - `POST /api/hardware/{id}/rent` — Rent a device
   - `POST /api/hardware/{id}/return` — Return a device

2. Update device store with rent/return methods

3. Update DashboardView to call rent/return methods

4. Add confirmation dialogs for user actions

5. Refresh device lists after successful rent/return
