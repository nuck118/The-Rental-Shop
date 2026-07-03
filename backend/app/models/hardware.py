from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime

from app.core.database import Base


class HardwareAsset(Base):
    """Hardware asset model for rental inventory."""

    __tablename__ = "hardware_asset"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(100), nullable=False)
    purchase_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Available", index=True)
    assigned_to = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    repair_flagged = Column(Boolean, default=False, nullable=True)

    def __repr__(self):
        return f"<HardwareAsset(id={self.id}, name={self.name}, brand={self.brand}, status={self.status})>"


class DataQuarantine(Base):
    """Quarantine table for invalid or incomplete hardware data that failed validation."""

    __tablename__ = "data_quarantine"

    id = Column(Integer, primary_key=True, index=True)
    raw_data = Column(Text, nullable=False)  # Original raw input as JSON
    errors = Column(Text, nullable=False)  # Validation errors as JSON
    severity = Column(String(20), nullable=False, default="warning")  # "critical" or "warning"
    source = Column(String(100), nullable=True)  # e.g., "seed_script", "api_import"
    resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DataQuarantine(id={self.id}, severity={self.severity}, resolved={self.resolved})>"