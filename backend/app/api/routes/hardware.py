from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_active_admin
from app.core.validation import import_hardware_batch
from app.models.hardware import HardwareAsset

router = APIRouter(prefix="/api/hardware", tags=["Hardware Management"])


class HardwareAssetResponse(BaseModel):
    """Response schema for hardware asset."""
    id: int
    name: str
    brand: str
    purchase_date: Optional[date] = None
    status: str
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get(
    "",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="List all hardware assets",
    description="Retrieve a paginated list of all hardware assets with optional filtering by status",
)
def list_hardware(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    status: str = Query(None, description="Filter by status (Available, In Use, Repair, Unknown)"),
    db: Session = Depends(get_db),
):
    """
    List all hardware assets with pagination and optional filtering.

    **Query Parameters:**
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Maximum records to return (default: 10, max: 100)
    - `status`: Filter by status (optional)

    **Response:**
    Returns a list of hardware assets with the following fields:
    - `id`: Unique identifier
    - `name`: Device name/model
    - `brand`: Manufacturer brand
    - `purchase_date`: Purchase date (YYYY-MM-DD)
    - `status`: Current status
    - `assigned_to`: Assigned user (if applicable)
    - `notes`: Additional notes

    **Example Response:**
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
    """
    query = db.query(HardwareAsset)

    if status:
        query = query.filter(HardwareAsset.status == status)

    total = query.count()
    devices = query.offset(skip).limit(limit).all()

    return [
        {
            "id": device.id,
            "name": device.name,
            "brand": device.brand,
            "purchase_date": device.purchase_date.isoformat() if device.purchase_date else None,
            "status": device.status,
            "assigned_to": device.assigned_to,
            "notes": device.notes,
        }
        for device in devices
    ]


@router.get(
    "/{hardware_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get hardware asset by ID",
    description="Retrieve a specific hardware asset by its ID",
)
def get_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific hardware asset by ID.

    **Path Parameters:**
    - `hardware_id`: The ID of the hardware asset

    **Response:**
    Returns the hardware asset with all details.

    **Error Responses:**
    - `404 Not Found`: Hardware asset with given ID does not exist

    **Example Response:**
    ```json
    {
      "id": 1,
      "name": "Apple iPhone 13 Pro Max",
      "brand": "Apple",
      "purchase_date": "2021-11-23",
      "status": "Available",
      "assigned_to": null,
      "notes": null
    }
    ```
    """
    device = db.query(HardwareAsset).filter(HardwareAsset.id == hardware_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hardware asset with ID {hardware_id} not found",
        )

    return {
        "id": device.id,
        "name": device.name,
        "brand": device.brand,
        "purchase_date": device.purchase_date.isoformat() if device.purchase_date else None,
        "status": device.status,
        "assigned_to": device.assigned_to,
        "notes": device.notes,
    }


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create new hardware asset",
    description="Create a new hardware asset in the inventory",
)
def create_hardware(
    name: str,
    brand: str,
    status: str,
    purchase_date: str = None,
    assigned_to: str = None,
    notes: str = None,
    db: Session = Depends(get_db),
):
    """
    Create a new hardware asset.

    **Request Body:**
    - `name` (required): Device name/model (max 255 characters)
    - `brand` (required): Manufacturer brand (max 100 characters)
    - `status` (required): Current status (max 50 characters)
    - `purchase_date` (optional): Purchase date in YYYY-MM-DD format
    - `assigned_to` (optional): Assigned user (max 255 characters)
    - `notes` (optional): Additional notes

    **Response:**
    Returns the created hardware asset with assigned ID.

    **Error Responses:**
    - `400 Bad Request`: Invalid request data

    **Example Request:**
    ```json
    {
      "name": "Dell XPS 15",
      "brand": "Dell",
      "status": "Available",
      "purchase_date": "2023-01-15",
      "notes": "High-performance laptop"
    }
    ```

    **Example Response:**
    ```json
    {
      "id": 12,
      "name": "Dell XPS 15",
      "brand": "Dell",
      "purchase_date": "2023-01-15",
      "status": "Available",
      "assigned_to": null,
      "notes": "High-performance laptop"
    }
    ```
    """
    # Validate and sanitize input using Pydantic schema
    raw_data = {
        "name": name,
        "brand": brand,
        "status": status,
        "purchase_date": purchase_date,
        "assigned_to": assigned_to,
        "notes": notes,
    }
    
    from app.core.validation import validate_hardware_record, quarantine_record
    result = validate_hardware_record(raw_data)
    
    if not result.is_valid:
        # Quarantine the bad record
        severity = "critical" if result.is_critical else "warning"
        quarantine_record(db, raw_data, result.errors, severity, "api_create")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {', '.join(result.errors)}",
        )

    # Valid record — create HardwareAsset
    device = HardwareAsset(
        name=result.schema.name,
        brand=result.schema.brand,
        purchase_date=date.fromisoformat(result.schema.purchase_date) if result.schema.purchase_date else None,
        status=result.schema.status,
        assigned_to=result.schema.assigned_to,
        notes=result.schema.notes,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return {
        "id": device.id,
        "name": device.name,
        "brand": device.brand,
        "purchase_date": device.purchase_date.isoformat() if device.purchase_date else None,
        "status": device.status,
        "assigned_to": device.assigned_to,
        "notes": device.notes,
    }


@router.put(
    "/{hardware_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update hardware asset",
    description="Update an existing hardware asset",
)
def update_hardware(
    hardware_id: int,
    name: str = None,
    brand: str = None,
    status: str = None,
    purchase_date: str = None,
    assigned_to: str = None,
    notes: str = None,
    db: Session = Depends(get_db),
):
    """
    Update a hardware asset.

    **Path Parameters:**
    - `hardware_id`: The ID of the hardware asset to update

    **Request Body:**
    All fields are optional. Only provided fields will be updated.
    - `name`: Device name/model
    - `brand`: Manufacturer brand
    - `status`: Current status
    - `purchase_date`: Purchase date in YYYY-MM-DD format
    - `assigned_to`: Assigned user
    - `notes`: Additional notes

    **Response:**
    Returns the updated hardware asset.

    **Error Responses:**
    - `404 Not Found`: Hardware asset not found
    - `400 Bad Request`: Invalid request data

    **Example Request:**
    ```json
    {
      "status": "In Use",
      "assigned_to": "john.doe@example.com"
    }
    ```

    **Example Response:**
    ```json
    {
      "id": 1,
      "name": "Apple iPhone 13 Pro Max",
      "brand": "Apple",
      "purchase_date": "2021-11-23",
      "status": "In Use",
      "assigned_to": "john.doe@example.com",
      "notes": null
    }
    ```
    """
    from datetime import datetime
    from app.core.validation import validate_hardware_record, quarantine_record

    device = db.query(HardwareAsset).filter(HardwareAsset.id == hardware_id).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hardware asset with ID {hardware_id} not found",
        )

    # Build raw_data dict with only provided fields for validation
    raw_data = {}
    if name is not None:
        raw_data["name"] = name
    if brand is not None:
        raw_data["brand"] = brand
    if status is not None:
        raw_data["status"] = status
    if purchase_date is not None:
        raw_data["purchase_date"] = purchase_date
    if assigned_to is not None:
        raw_data["assigned_to"] = assigned_to
    if notes is not None:
        raw_data["notes"] = notes

    # Validate the update payload
    result = validate_hardware_record(raw_data)
    
    if not result.is_valid:
        severity = "critical" if result.is_critical else "warning"
        quarantine_record(db, raw_data, result.errors, severity, "api_update")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {', '.join(result.errors)}",
        )

    # Apply validated data
    if result.schema.name is not None:
        device.name = result.schema.name
    if result.schema.brand is not None:
        device.brand = result.schema.brand
    if result.schema.status is not None:
        device.status = result.schema.status
    if result.schema.purchase_date is not None:
        device.purchase_date = date.fromisoformat(result.schema.purchase_date)
    if result.schema.assigned_to is not None:
        device.assigned_to = result.schema.assigned_to
    if result.schema.notes is not None:
        device.notes = result.schema.notes

    db.commit()
    db.refresh(device)

    return {
        "id": device.id,
        "name": device.name,
        "brand": device.brand,
        "purchase_date": device.purchase_date.isoformat() if device.purchase_date else None,
        "status": device.status,
        "assigned_to": device.assigned_to,
        "notes": device.notes,
    }


@router.delete(
    "/{hardware_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hardware asset",
    description="Delete a hardware asset by its ID",
)
def delete_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_admin),
):
    """
    Delete a hardware asset.
    Requires administrator privileges.
    """
    device = db.query(HardwareAsset).filter(HardwareAsset.id == hardware_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hardware asset not found",
        )

    db.delete(device)
    db.commit()


@router.post(
    "/{hardware_id}/rent",
    response_model=HardwareAssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Rent a hardware asset",
    description="Rents an available hardware asset to the currently authenticated user.",
)
def rent_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Rent a device."""
    device = db.query(HardwareAsset).filter(HardwareAsset.id == hardware_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hardware asset not found")
        
    if device.status != "Available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device cannot be rented. Current status is '{device.status}'."
        )
        
    device.status = "In Use"
    device.assigned_to = current_user.username
    db.commit()
    db.refresh(device)
    return device


@router.post(
    "/{hardware_id}/return",
    response_model=HardwareAssetResponse,
    status_code=status.HTTP_200_OK,
    summary="Return a hardware asset",
    description="Returns a hardware asset that is currently rented by the user.",
)
def return_hardware(
    hardware_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Return a device."""
    device = db.query(HardwareAsset).filter(HardwareAsset.id == hardware_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hardware asset not found")
        
    if device.status != "In Use":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device cannot be returned. Current status is '{device.status}'."
        )
        
    if device.assigned_to != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot return a device you did not rent."
        )
        
    device.status = "Available"
    device.assigned_to = None
    db.commit()
    db.refresh(device)
    return device
