"""Data validation, normalization, and quarantine system for hardware imports."""

from __future__ import annotations

import json
import re
from datetime import datetime, date
from typing import Any, Optional
from sqlalchemy.orm import Session

from pydantic import BaseModel, Field, field_validator, ValidationError
from app.models.hardware import HardwareAsset, DataQuarantine


class HardwareImportSchema(BaseModel):
    """Pydantic schema for validating incoming hardware data."""
    name: str = Field(..., min_length=1, max_length=255)
    brand: str = Field(..., min_length=1, max_length=100)
    purchase_date: Optional[str] = Field(None, description="ISO date string YYYY-MM-DD")
    status: str = Field(default="Available", max_length=50)
    assigned_to: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=None)

    @field_validator("name", "brand", mode="before")
    @classmethod
    def sanitize_string(cls, v: Any) -> str:
        """Strip whitespace, normalize internal spaces."""
        if not isinstance(v, str):
            raise ValueError("Must be a string")
        v = v.strip()
        v = re.sub(r"\s+", " ", v)  # collapse multiple spaces
        if not v:
            raise ValueError("Cannot be empty after sanitization")
        return v

    @field_validator("purchase_date", mode="before")
    @classmethod
    def normalize_date(cls, v: Any) -> Optional[str]:
        """Accept various date formats and normalize to ISO YYYY-MM-DD."""
        if v is None or v == "":
            return None
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, datetime):
            return v.date().isoformat()
        if not isinstance(v, str):
            raise ValueError("Date must be a string or date object")
        v = v.strip()
        # Try common formats
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(v, fmt).date().isoformat()
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD")

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> str:
        """Normalize status to title case, default to Available."""
        if v is None or v == "":
            return "Available"
        if not isinstance(v, str):
            raise ValueError("Status must be a string")
        v = v.strip().title()
        valid_statuses = {"Available", "In Use", "Repair", "Unknown"}
        if v not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {', '.join(sorted(valid_statuses))}")
        return v

    @field_validator("assigned_to", mode="before")
    @classmethod
    def sanitize_assigned_to(cls, v: Any) -> Optional[str]:
        """Sanitize assigned_to field."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            raise ValueError("assigned_to must be a string")
        v = v.strip()
        v = re.sub(r"\s+", " ", v)
        return v if v else None

    @field_validator("notes", mode="before")
    @classmethod
    def sanitize_notes(cls, v: Any) -> Optional[str]:
        """Sanitize notes field."""
        if v is None or v == "":
            return None
        if not isinstance(v, str):
            raise ValueError("notes must be a string")
        v = v.strip()
        v = re.sub(r"\s+", " ", v)
        return v if v else None


class ValidationResult:
    """Result of validating a single hardware record."""

    def __init__(self, raw_data: dict, schema: Optional[HardwareImportSchema] = None, errors: Optional[list[str]] = None):
        self.raw_data = raw_data
        self.schema = schema
        self.errors = errors or []
        self.is_valid = len(self.errors) == 0
        self.is_critical = self._check_critical()

    def _check_critical(self) -> bool:
        """Check if this is a critical failure (missing required fields or invalid status with assigned_to)."""
        if not self.is_valid:
            for error in self.errors:
                if any(critical in error for critical in ["name", "brand", "status"]):
                    return True
        # Critical: status is "In Use" but assigned_to is missing
        if self.schema and self.schema.status == "In Use" and not self.schema.assigned_to:
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "raw_data": self.raw_data,
            "errors": self.errors,
            "is_valid": self.is_valid,
            "severity": "critical" if self.is_critical else "warning",
        }


def validate_hardware_record(raw_data: dict) -> ValidationResult:
    """Validate a single hardware record against the schema."""
    try:
        schema = HardwareImportSchema(**raw_data)
        return ValidationResult(raw_data=raw_data, schema=schema, errors=[])
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return ValidationResult(raw_data=raw_data, schema=None, errors=errors)


def quarantine_record(db: Session, raw_data: dict, errors: list[str], severity: str, source: str) -> DataQuarantine:
    """Save a failed record to the quarantine table."""
    quarantine = DataQuarantine(
        raw_data=json.dumps(raw_data, default=str),
        errors=json.dumps(errors),
        severity=severity,
        source=source,
    )
    db.add(quarantine)
    db.commit()
    db.refresh(quarantine)
    return quarantine


def import_hardware_batch(db: Session, records: list[dict], source: str = "api_import") -> tuple[list[HardwareAsset], list[DataQuarantine]]:
    """
    Import a batch of hardware records with validation and quarantine.
    
    Returns:
        (successfully_imported_devices, quarantine_entries)
    """
    imported = []
    quarantined = []

    for raw in records:
        result = validate_hardware_record(raw)
        
        # Quarantine if validation failed OR if critical business rule violated
        if not result.is_valid or result.is_critical:
            if result.is_critical and result.is_valid:
                result.errors = ["Critical: device is 'In Use' but missing assigned_to"]
            quarantine_record(db, raw, result.errors, result.is_critical, source)
            quarantined.append(result)
            continue

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
        imported.append(device)

    db.commit()
    return imported, quarantined
