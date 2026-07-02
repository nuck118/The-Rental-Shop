# Quick Start Guide — Dashboard & Signin

This guide walks you through setting up and running the complete application with the new dashboard and signin page.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google AI Studio API key (for AI chatbot)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Google AI API key:
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 4. Seed Data

```bash
# Create admin user (admin / admin123)
python scripts/seed_admin.py

# Seed hardware devices
python scripts/seed_hardware.py
```

### 5. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend is now running at `http://localhost:8000`

**Available URLs:**
- API: `http://localhost:8000/api`
- Swagger Docs: `http://localhost:8000/docs`
- Admin Panel: `http://localhost:8000/admin`

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

Frontend is now running at `http://localhost:5173`

## Using the Dashboard

### 1. Sign In

Navigate to `http://localhost:5173` and you'll be redirected to the signin page.

**Demo Credentials:**
```
Username: admin
Password: admin123
```

### 2. Dashboard Overview

After signing in, you'll see the dashboard with three tabs:

#### Available Devices
- Browse all available hardware
- Click "Rent" to rent a device (feature ready for implementation)
- Devices shown in grid layout with status badges

#### Rented Devices
- View devices you've rented
- Click "Return" to return a device (feature ready for implementation)
- Shows assignment and rental status

#### History
- View complete inventory history
- Table view of all devices
- Sortable by name, brand, status, purchase date, assigned user

### 3. User Profile

Click your profile icon in the top-right corner to:
- View your username
- Sign out

## API Endpoints

### Authentication
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
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

### Hardware
```
GET /api/hardware?status=Available
Authorization: Bearer <token>

GET /api/hardware?status=In Use
Authorization: Bearer <token>

GET /api/hardware
Authorization: Bearer <token>
```

## Project Structure

```
The-Rental-Shop/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py          # NEW: Login endpoint
│   │   │   └── hardware.py      # Device management
│   │   ├── models/
│   │   │   ├── user.py          # User model
│   │   │   ├── hardware.py      # Hardware model
│   │   │   └── audit_log.py     # Audit logging
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   ├── database.py      # SQLAlchemy setup
│   │   │   └── user.py          # User utilities
│   │   ├── security/
│   │   │   └── middleware.py    # Security middleware
│   │   ├── ai/
│   │   │   ├── router.py        # AI endpoints
│   │   │   └── services.py      # Gemini integration
│   │   └── main.py              # FastAPI app
│   ├── scripts/
│   │   ├── seed_admin.py        # Create admin user
│   │   └── seed_hardware.py     # Seed devices
│   ├── alembic/                 # Database migrations
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── DeviceCard.vue   # NEW: Device card component
│   │   ├── stores/
│   │   │   ├── auth.js          # NEW: Auth store
│   │   │   └── device.js        # NEW: Device store
│   │   ├── views/
│   │   │   ├── SigninView.vue   # NEW: Login page
│   │   │   └── DashboardView.vue # NEW: Main dashboard
│   │   ├── router/
│   │   │   └── index.js         # UPDATED: Auth guards
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── README.md
├── FRONTEND_SETUP.md            # NEW: Frontend guide
└── QUICKSTART_DASHBOARD.md      # NEW: This file
```

## Key Features

### Signin Page
✅ Clean, modern UI  
✅ Form validation  
✅ Error handling  
✅ Demo credentials display  
✅ Enter key support  

### Dashboard
✅ Three-tab interface  
✅ Available devices grid  
✅ Rented devices grid  
✅ Device history table  
✅ User profile menu  
✅ Logout functionality  

### Device Management
✅ Device cards with status badges  
✅ Color-coded status (Available, In Use, Repair, Unknown)  
✅ Device details (name, brand, purchase date, notes)  
✅ Rent/Return buttons (ready for implementation)  

### Authentication
✅ JWT token-based auth  
✅ Token persistence in localStorage  
✅ Route guards for protected pages  
✅ Automatic redirect to signin  

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Can't login
```bash
# Verify admin user exists
python scripts/seed_admin.py

# Check backend is running
curl http://localhost:8000/health

# Verify CORS is configured
# Check .env: CORS_ORIGINS should include http://localhost:5173
```

### Devices not loading
```bash
# Seed hardware
python scripts/seed_hardware.py

# Check database
# Verify rental_shop.db exists in backend/

# Check API directly
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/hardware
```

### Token expired
- Tokens expire after 24 hours
- Sign out and sign back in to get a new token
- Check browser console for 401 errors

## Next Steps

1. **Implement Rent/Return**
   - Create backend endpoints for rent/return operations
   - Update device store with rent/return methods
   - Add confirmation dialogs

2. **Add Device Search**
   - Add search input to dashboard
   - Filter devices by name/brand

3. **Add Device Details Modal**
   - Click device card to view full details
   - Show maintenance history
   - Show rental history

4. **Implement Notifications**
   - Toast notifications for actions
   - Success/error messages

5. **Add User Management**
   - User profile page
   - Change password
   - View rental history

## Documentation

- **Backend**: See [README.md](README.md) and [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Frontend**: See [FRONTEND_SETUP.md](FRONTEND_SETUP.md)
- **Admin Panel**: See [SQLADMIN_GUIDE.md](SQLADMIN_GUIDE.md)
- **Database**: See [ALEMBIC_GUIDE.md](ALEMBIC_GUIDE.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation files
3. Check browser console for errors
4. Check backend logs for API errors
5. Verify all prerequisites are installed
