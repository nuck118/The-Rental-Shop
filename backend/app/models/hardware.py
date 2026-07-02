from datetime import date
from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import declarative_base

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

    def __repr__(self):
        return f"<HardwareAsset(id={self.id}, name={self.name}, brand={self.brand}, status={self.status})>"
