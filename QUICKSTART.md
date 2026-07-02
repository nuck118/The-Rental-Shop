# Quick Start Guide

## Get Hardware Data in Piccolo Admin

### Step 1: Create Migrations

```bash
cd backend
source .venv/bin/activate
piccolo migrations new app --auto
```

This creates a migration file in `backend/migrations/` that defines the `hardware_asset` table schema.

### Step 2: Run Migrations

```bash
piccolo migrations run
```

This creates the SQLite database (`rental_shop.db`) and the `hardware_asset` table.

### Step 3: Seed Sample Data

```bash
python scripts/seed_hardware.py
```

This populates the database with 11 sample hardware devices from the legacy data dump.

Expected output:
```
Inserted: [1] Apple iPhone 13 Pro Max
Inserted: [2] Apple MacBook Pro 13
Inserted: [3] Razer Basilisk V2
Inserted: [4] SAMSUNG Galaxy S21
Inserted: [5] Dell XPS 15 9510
Inserted: [6] Logitech MX Master 3
Inserted: [7] Sony WH-1000XM4
Inserted: [8] Duplicate ID Test Laptop
Inserted: [9] iPad Pro 12.9
Inserted: [10] Unknown Device
Inserted: [11] MacBook Air M2
```

### Step 4: Start Backend Server

```bash
uvicorn app.main:app --reload
```

### Step 5: Access Piccolo Admin

Open http://localhost:8000/admin in your browser.

You should see:
- **HardwareAsset** table in the left sidebar
- Click it to view all 11 devices
- Click any device to edit or view details

## Verify Data in Database

### Check Migration Status

```bash
piccolo migrations check
```

Should show all migrations as applied.

### Query Data Directly

```bash
python -c "
from app.models.hardware import HardwareAsset
import asyncio

async def check():
    devices = await HardwareAsset.select().run()
    print(f'Total devices: {len(devices)}')
    for device in devices:
        print(f'  - {device.name} ({device.brand})')

asyncio.run(check())
"
```

## Troubleshooting

### No Tables Showing in Admin

1. Verify migrations were created:
   ```bash
   ls -la migrations/
   ```
   Should show at least one `.py` file

2. Verify migrations were applied:
   ```bash
   piccolo migrations check
   ```
   Should show "✓" for all migrations

3. Verify database file exists:
   ```bash
   ls -la rental_shop.db
   ```

4. Restart the backend server:
   ```bash
   # Stop current server (Ctrl+C)
   # Then restart
   uvicorn app.main:app --reload
   ```

### Data Not Showing After Seeding

1. Check seed script output for errors
2. Verify database file was modified:
   ```bash
   ls -la rental_shop.db
   ```
   Should show recent timestamp

3. Query the database directly to confirm data exists:
   ```bash
   python scripts/seed_hardware.py  # Run again
   ```

### Admin Panel Not Loading

1. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check admin endpoint:
   ```bash
   curl http://localhost:8000/admin
   ```

3. Check browser console for errors (F12)

## Next Steps

Once data is visible in Piccolo Admin:

1. **Test the Chatbot**: Use the `/api/ai/chat` endpoint to get device recommendations
2. **Build Frontend**: Create Vue components to display devices
3. **Add More Tables**: Create additional models (Users, Rentals, etc.)
4. **Deploy**: Follow production deployment guidelines in README.md
