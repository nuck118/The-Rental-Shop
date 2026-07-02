# Frontend Components & Stores Documentation

## Overview

This document describes the new Vue 3 components and Pinia stores added for the dashboard and signin functionality.

## Stores (Pinia)

### Auth Store (`src/stores/auth.js`)

Manages user authentication state and JWT token persistence.

**State:**
```javascript
user: null              // Current user object { id, username, email, is_admin }
token: null            // JWT token from localStorage
isAuthenticated: bool  // Computed: true if token exists
```

**Methods:**

#### `login(username, password): Promise<boolean>`
Authenticates user with credentials.

```javascript
const authStore = useAuthStore();
const success = await authStore.login('admin', 'admin123');
if (success) {
  // User is authenticated, token is stored
  console.log(authStore.user);
}
```

**Request:**
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

**Error Handling:**
- Returns `false` on invalid credentials
- Logs error to console
- Does not throw exception

#### `logout(): void`
Clears authentication state and removes token from localStorage.

```javascript
const authStore = useAuthStore();
authStore.logout();
// Token is cleared, user is null
```

**Token Persistence:**
- Token is stored in `localStorage` under key `'token'`
- Token is automatically restored on page reload
- Token is cleared on logout

---

### Device Store (`src/stores/device.js`)

Manages hardware device data and API requests.

**State:**
```javascript
availableDevices: []   // Devices with status="Available"
rentedDevices: []      // Devices with status="In Use"
deviceHistory: []      // All devices
loading: bool          // Loading state for all requests
error: null            // Error message if request fails
```

**Methods:**

#### `fetchAvailableDevices(token): Promise<void>`
Fetches devices with status "Available".

```javascript
const deviceStore = useDeviceStore();
const authStore = useAuthStore();

await deviceStore.fetchAvailableDevices(authStore.token);
console.log(deviceStore.availableDevices);
```

**Request:**
```
GET /api/hardware?status=Available
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Apple iPhone 13 Pro Max",
    "brand": "Apple",
    "purchase_date": "2021-11-23",
    "status": "Available",
    "assigned_to": null,
    "notes": null
  }
]
```

#### `fetchRentedDevices(token): Promise<void>`
Fetches devices with status "In Use".

```javascript
const deviceStore = useDeviceStore();
await deviceStore.fetchRentedDevices(authStore.token);
console.log(deviceStore.rentedDevices);
```

**Request:**
```
GET /api/hardware?status=In Use
Authorization: Bearer <token>
```

#### `fetchDeviceHistory(token): Promise<void>`
Fetches all devices (complete history).

```javascript
const deviceStore = useDeviceStore();
await deviceStore.fetchDeviceHistory(authStore.token);
console.log(deviceStore.deviceHistory);
```

**Request:**
```
GET /api/hardware
Authorization: Bearer <token>
```

**Error Handling:**
- Sets `error` property on failure
- Sets `loading` to `false` after request completes
- Does not throw exception

---

## Views

### SigninView (`src/views/SigninView.vue`)

User authentication page with login form.

**Features:**
- Username and password input fields
- Form validation (both fields required)
- Error message display
- Loading state during authentication
- Enter key support for quick login
- Demo credentials display
- Gradient background with centered card layout

**Props:** None

**Emits:** None

**Usage:**
```vue
<template>
  <SigninView />
</template>
```

**Form Validation:**
- Both username and password are required
- Shows error: "Please enter both username and password"
- Shows error: "Invalid username or password" on auth failure

**Styling:**
- Gradient background: `from-blue-50 to-indigo-100`
- Card: White background with shadow
- Inputs: Tailwind form styling with focus states
- Button: Indigo color with hover effect
- Error message: Red background with border

**Keyboard Support:**
- Enter key in either input field triggers login
- Useful for quick authentication

---

### DashboardView (`src/views/DashboardView.vue`)

Main application dashboard with three tabs for device management.

**Features:**
- Header with user profile and logout
- Tab navigation (Available, Rented, History)
- Device grid for Available and Rented tabs
- Device table for History tab
- Loading and error states
- Responsive design

**Props:** None

**Emits:** None

**Usage:**
```vue
<template>
  <DashboardView />
</template>
```

**Tabs:**

#### Available Devices
- Grid layout (1 column on mobile, 2 on tablet, 3 on desktop)
- Shows all devices with status "Available"
- Each device card has "Rent" button
- Empty state message if no devices available

#### Rented Devices
- Grid layout (same as Available)
- Shows all devices with status "In Use"
- Each device card has "Return" button
- Empty state message if no rented devices

#### History
- Table layout with columns:
  - Device Name
  - Brand
  - Status (with color badge)
  - Purchase Date
  - Assigned To
- Responsive table with horizontal scroll on mobile
- Hover effects on rows
- Empty state message if no history

**Header:**
- Logo and title
- User profile button with dropdown menu
- Logout option in dropdown

**Loading State:**
- Spinner animation
- "Loading devices..." message

**Error State:**
- Red error box with error message
- Allows user to retry

**Responsive Design:**
- Mobile: Single column grid, stacked layout
- Tablet: Two column grid
- Desktop: Three column grid
- Table scrolls horizontally on small screens

---

## Components

### DeviceCard (`src/components/DeviceCard.vue`)

Reusable component for displaying device information.

**Props:**

```javascript
device: {
  type: Object,
  required: true,
  // Expected properties:
  // - id: number
  // - name: string
  // - brand: string
  // - status: string ("Available", "In Use", "Repair", "Unknown")
  // - purchase_date: string (ISO date)
  // - assigned_to: string (optional)
  // - notes: string (optional)
}

showRentButton: {
  type: Boolean,
  default: false
}

showReturnButton: {
  type: Boolean,
  default: false
}
```

**Emits:**

```javascript
// Emitted when Rent button is clicked
@rent="handleRent"
// Payload: device object

// Emitted when Return button is clicked
@return="handleReturn"
// Payload: device object
```

**Usage:**

```vue
<template>
  <DeviceCard
    :device="device"
    :show-rent-button="true"
    @rent="handleRent"
  />
</template>

<script setup>
const handleRent = (device) => {
  console.log('Renting:', device.name);
};
</script>
```

**Features:**
- Device name and brand
- Status badge with color coding
- Purchase date (formatted)
- Assigned user (if applicable)
- Notes (if available)
- Optional action buttons
- Hover effects

**Status Badge Colors:**
- Green: Available
- Blue: In Use
- Yellow: Repair
- Gray: Unknown

**Styling:**
- White background with shadow
- Rounded corners
- Hover shadow effect
- Responsive padding
- Tailwind CSS utilities

---

## Router Configuration

### Routes

```javascript
// Public routes
GET /signin          → SigninView
GET /                → Redirect to /dashboard

// Protected routes (require authentication)
GET /dashboard       → DashboardView (meta: { requiresAuth: true })
```

### Route Guards

**Before Each Route:**
1. Check if route requires authentication (`meta.requiresAuth`)
2. If required and user not authenticated → redirect to `/signin`
3. If user is authenticated and accessing `/signin` → redirect to `/dashboard`
4. Otherwise → proceed to route

**Usage:**
```javascript
// In router/index.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/signin");
  } else if (to.path === "/signin" && authStore.isAuthenticated) {
    next("/dashboard");
  } else {
    next();
  }
});
```

---

## API Integration

### Authentication Flow

```
User Input (username, password)
    ↓
SigninView.handleSignin()
    ↓
authStore.login(username, password)
    ↓
POST /api/auth/login
    ↓
Backend validates credentials
    ↓
Returns { token, user }
    ↓
Store token in localStorage
    ↓
Set authStore.user and authStore.token
    ↓
Router redirects to /dashboard
    ↓
DashboardView mounts
    ↓
Fetch devices with token
    ↓
Display dashboard
```

### Device Fetch Flow

```
DashboardView mounts
    ↓
Check authentication
    ↓
deviceStore.fetchAvailableDevices(token)
deviceStore.fetchRentedDevices(token)
deviceStore.fetchDeviceHistory(token)
    ↓
GET /api/hardware?status=...
    ↓
Include Authorization header
    ↓
Backend validates token
    ↓
Returns device list
    ↓
Store in deviceStore
    ↓
Render in template
```

### Token Usage

All API requests include the JWT token:

```javascript
// In device store
const response = await fetch("/api/hardware?status=Available", {
  headers: { Authorization: `Bearer ${token}` },
});
```

---

## State Management

### Auth Store Lifecycle

```
App loads
    ↓
useAuthStore() initializes
    ↓
Reads token from localStorage
    ↓
Sets isAuthenticated based on token
    ↓
User navigates to /signin
    ↓
Enters credentials
    ↓
login() called
    ↓
Token stored in localStorage
    ↓
User navigated to /dashboard
    ↓
User refreshes page
    ↓
Token restored from localStorage
    ↓
User remains authenticated
```

### Device Store Lifecycle

```
DashboardView mounts
    ↓
Check authentication
    ↓
Call fetchAvailableDevices()
    ↓
Set loading = true
    ↓
API request
    ↓
Set loading = false
    ↓
Store devices in availableDevices
    ↓
Template re-renders
    ↓
Devices displayed
```

---

## Error Handling

### Authentication Errors

| Error | Cause | User Message |
|-------|-------|--------------|
| Invalid credentials | Wrong username/password | "Invalid username or password" |
| User inactive | Account deactivated | "User account is inactive" |
| Network error | Backend unreachable | "Invalid username or password" |

### Device Fetch Errors

| Error | Cause | Display |
|-------|-------|---------|
| Network error | Backend unreachable | Error box with message |
| Invalid token | Token expired/invalid | Error box with message |
| Server error | Backend error | Error box with message |

---

## Performance Considerations

### Token Persistence
- Token stored in localStorage (persistent across sessions)
- No need to re-authenticate on page reload
- Token expires after 24 hours (backend setting)

### Device Caching
- Devices fetched on dashboard mount
- No automatic refresh
- Manual refresh by navigating between tabs

### Lazy Loading
- Views loaded on-demand via dynamic imports
- Reduces initial bundle size
- Faster initial page load

---

## Accessibility

### Signin Form
- Proper label associations
- Keyboard navigation support
- Error messages linked to inputs
- Focus management

### Dashboard
- Semantic HTML structure
- Color not sole indicator (status badges have text)
- Keyboard navigation for tabs
- ARIA labels for interactive elements

### Device Cards
- Semantic card structure
- Button labels are descriptive
- Color-coded badges have text labels

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Future Enhancements

1. **Search & Filter**
   - Search devices by name/brand
   - Filter by status
   - Sort by purchase date

2. **Device Details Modal**
   - Click device to view full details
   - Show maintenance history
   - Show rental history

3. **Notifications**
   - Toast notifications for actions
   - Success/error messages
   - Rental reminders

4. **User Profile**
   - View profile information
   - Change password
   - View rental history

5. **Advanced Filtering**
   - Date range filters
   - Multi-select status filters
   - Advanced search

6. **Export**
   - Export device list to CSV
   - Export rental history
   - Generate reports
