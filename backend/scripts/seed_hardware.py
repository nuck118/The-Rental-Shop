import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from piccolo.engine import engine_finder
from app.models.hardware import HardwareAsset

RAW_DATA = [
    {"id": 1, "name": "Apple iPhone 13 Pro Max", "purchaseDate": "2021-11-23", "status": "Available", "brand": "Apple"},
    {"id": 2, "name": "Apple MacBook Pro 13", "purchaseDate": "2021-12-20", "status": "In Use", "brand": "Apple"},
    {"id": 3, "name": "Razer Basilisk V2", "purchaseDate": "2021-06-05", "brand": "Razer", "status": "Repair"},
    {"id": 4, "name": "SAMSUNG Galaxy S21", "brand": "Samsung", "purchaseDate": "2021-11-23", "status": "Available"},
    {"id": 5, "name": "Dell XPS 15 9510", "brand": "Dell", "purchaseDate": "2022-03-15", "status": "Available", "notes": "Battery swelling, do not issue without service."},
    {"id": 6, "name": "Logitech MX Master 3", "brand": "Logitech", "purchaseDate": "2027-10-10", "status": "Available"},
    {"id": 7, "name": "Sony WH-1000XM4", "purchaseDate": "2022-01-12", "brand": "Sony", "status": "In Use", "assignedTo": "j.doe@booksy.com"},
    {"id": 8, "name": "Duplicate ID Test Laptop", "purchaseDate": "2023-01-01", "status": "Repair", "brand": "Lenovo"},
    {"id": 9, "name": "iPad Pro 12.9", "purchaseDate": "22-05-2023", "brand": "Appel", "status": "Available"},
    {"id": 10, "purchaseDate": None, "name": "Unknown Device", "brand": "", "status": "Unknown"},
    {"id": 11, "name": "MacBook Air M2", "purchaseDate": "2023-08-01", "brand": "Apple", "status": "Available", "notes": "Returned by user with liquid damage. Keyboard sticky."},
]


async def seed():
    engine = engine_finder()
    await engine.start_connection_pool()

    for row in RAW_DATA:
        await HardwareAsset.insert(
            HardwareAsset(
                id=row["id"],
                name=row["name"],
                brand=row["brand"],
                purchase_date=row["purchaseDate"],
                status=row["status"],
                assigned_to=row.get("assignedTo"),
                notes=row.get("notes"),
            )
        ).run()
        print(f"Inserted: [{row['id']}] {row['name']}")

    await engine.close_connection_pool()


if __name__ == "__main__":
    asyncio.run(seed())
