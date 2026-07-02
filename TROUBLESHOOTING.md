# Piccolo Admin Data Visibility Guide

## Why Data Isn't Showing in Piccolo Admin

The most common reasons hardware data doesn't appear in Piccolo Admin:

### 1. Migrations Not Created or Run

**Problem**: Database schema doesn't exist yet.

**Solution**:
```bash
cd backend
source .venv/bin/activate

# Create migration from model definitions
piccolo migrations new app --auto

# Apply migration to create tables
piccolo migrations run

# Verify
piccolo migrations check
```

### 2. Data Not Seeded

**Problem**: Tables exist but are empty.

**Solution**:
```bash
python scripts/seed_hardware.py
```

### 3. Admin Not Registered with Tables

**Problem**: Piccolo Admin is mounted but doesn't know about HardwareAsset table.

**Solution**: Verify `app/main.py` has:
```python
from app.models.hardware import HardwareAsset

app.mount("/admin", create_admin(tables=[
    HardwareAsset,
]))
```

### 4. Server Not Restarted After Changes

**Problem**: Changes to code aren't reflected.

**Solution**:
```bash
# Stop server (Ctrl+C)
# Restart
uvicorn app.main:app --reload
```

## Complete Setup Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with `GEMINI_API_KEY`
- [ ] Migration created: `piccolo migrations new app --auto`
- [ ] Migration applied: `piccolo migrations run`
- [ ] Data seeded: `python scripts/seed_hardware.py`
- [ ] Backend server running: `uvicorn app.main:app --reload`
- [ ] Admin accessible: http://localhost:8000/admin
- [ ] HardwareAsset table visible in admin sidebar
- [ ] 11 devices visible in table

## Verification Commands

### Check Migrations Exist
```bash
ls -la backend/migrations/
```
Should show at least one `.py` file (not `__init__.py`)

### Check Migrations Applied
```bash
cd backend
piccolo migrations check
```
Should show all migrations with ✓

### Check Database File
```bash
ls -la backend/rental_shop.db
```
Should exist and have recent timestamp

### Check Data in Database
```bash
cd backend
python -c "
from app.models.hardware import HardwareAsset
import asyncio

async def check():
    count = await HardwareAsset.count().run()
    print(f'Total devices in database: {count}')

asyncio.run(check())
"
```
Should print: `Total devices in database: 11`

### Check Admin Endpoint
```bash
curl http://localhost:8000/admin
```
Should return HTML (not 404 or 500)

### Check API Health
```bash
curl http://localhost:8000/docs
```
Should show Swagger UI with all endpoints

## File Structure Verification

Ensure these files exist:

```
backend/
├── app/
│   ├── models/
│   │   ├── __init__.py          (exports HardwareAsset)
│   │   └── hardware.py          (defines HardwareAsset table)
│   ├── main.py                  (mounts admin with HardwareAsset)
│   └── piccolo_app.py           (AppConfig for migrations)
├── scripts/
│   └── seed_hardware.py         (populates database)
├── migrations/                  (should have migration files after running)
├── piccolo_conf.py              (database engine config)
└── requirements.txt
```

## Step-by-Step Recovery

If data still isn't showing:

### 1. Clean Start
```bash
cd backend
rm -f rental_shop.db
rm -f migrations/*.py  # Keep __init__.py
```

### 2. Recreate Everything
```bash
piccolo migrations new app --auto
piccolo migrations run
python scripts/seed_hardware.py
```

### 3. Restart Server
```bash
# Stop current server (Ctrl+C)
uvicorn app.main:app --reload
```

### 4. Access Admin
Open http://localhost:8000/admin

### 5. Verify Data
- Click "HardwareAsset" in sidebar
- Should see 11 devices listed

## Common Error Messages

### "No tables found"
- Migrations not run
- Solution: `piccolo migrations run`

### "Table 'hardware_asset' does not exist"
- Database schema not created
- Solution: `piccolo migrations new app --auto && piccolo migrations run`

### "404 Not Found" on /admin
- Admin not mounted in main.py
- Solution: Verify `create_admin(tables=[HardwareAsset])` in main.py

### "Empty table" in admin
- Data not seeded
- Solution: `python scripts/seed_hardware.py`

### "Connection refused" to database
- Database file corrupted or locked
- Solution: Delete `rental_shop.db` and restart from step 1

## Advanced Debugging

### View Raw Database
```bash
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('rental_shop.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print(f'  - {table[0]}')
    cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
    count = cursor.fetchone()[0]
    print(f'    Records: {count}')
conn.close()
"
```

### Check Migration History
```bash
cd backend
piccolo migrations check --verbose
```

### View Migration Files
```bash
ls -la backend/migrations/
cat backend/migrations/001_*.py  # View the migration content
```

## Success Indicators

You'll know everything is working when:

1. ✓ `piccolo migrations check` shows all migrations applied
2. ✓ `rental_shop.db` file exists and is recent
3. ✓ Backend server starts without errors
4. ✓ http://localhost:8000/admin loads
5. ✓ "HardwareAsset" appears in admin sidebar
6. ✓ Clicking HardwareAsset shows 11 devices
7. ✓ Each device has name, brand, status, etc.
8. ✓ Can click a device to view/edit details

## Next Steps

Once data is visible:

1. **Test Chatbot**: 
   ```bash
   curl -X POST http://localhost:8000/api/ai/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "I need a laptop", "conversation_history": []}'
   ```

2. **Build Frontend**: Create Vue components to display devices

3. **Add More Tables**: Create User, Rental, MaintenanceLog models

4. **Deploy**: Follow production guidelines in README.md
