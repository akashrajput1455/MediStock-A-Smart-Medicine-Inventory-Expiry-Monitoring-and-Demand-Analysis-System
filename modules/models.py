"""
MediStock Domain Models.

This module defines the core data models for the MediStock application
using Object-Oriented Programming (OOP) principles. It includes:
1. BaseEntity: Base abstract class demonstrating inheritance and common attributes.
2. MedicineBatch: Represents a specific batch of medicine in inventory.
3. ConsumptionRecord: Represents a recorded dispensing/consumption event.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, Optional, Union


class BaseEntity(ABC):
    """
    Abstract base class for all persistent entities in MediStock.
    Demonstrates OOP inheritance, encapsulation, and interface consistency.
    """

    def __init__(self, entity_id: str, created_at: Optional[str] = None):
        self.entity_id = entity_id.strip() if entity_id else ""
        self.created_at = created_at or date.today().isoformat()

    @abstractmethod
    def validate(self) -> None:
        """Validate internal constraints and data integrity."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity attributes to a dictionary suitable for CSV serialization."""
        pass


class MedicineBatch(BaseEntity):
    """
    Represents an individual batch of medicine stored in inventory.
    
    Attributes:
        batch_id (str): Unique internal batch identifier (e.g. 'BAT-1001')
        medicine_name (str): Generic or trade name (e.g. 'Paracetamol 500mg')
        category (str): Therapeutic category (e.g. 'Analgesic')
        batch_number (str): Manufacturer's external lot number (e.g. 'BN-2024-08')
        manufacturer (str): Manufacturing pharmaceutical company
        quantity (int): Number of units currently on hand
        min_stock_level (int): Reorder threshold quantity
        unit_price (float): Purchase price per unit in currency
        mfg_date (date): Date of manufacture
        expiry_date (date): Date of expiration
    """

    def __init__(
        self,
        batch_id: str,
        medicine_name: str,
        category: str,
        batch_number: str,
        manufacturer: str,
        quantity: int,
        min_stock_level: int,
        unit_price: float,
        mfg_date: Union[date, str],
        expiry_date: Union[date, str],
        created_at: Optional[str] = None,
    ):
        super().__init__(batch_id, created_at)
        self.batch_id = self.entity_id
        self.medicine_name = medicine_name.strip() if medicine_name else ""
        self.category = category.strip() if category else "General"
        self.batch_number = batch_number.strip() if batch_number else ""
        self.manufacturer = manufacturer.strip() if manufacturer else ""
        self.quantity = int(quantity)
        self.min_stock_level = int(min_stock_level)
        self.unit_price = float(unit_price)

        # Parse manufacturing date
        if isinstance(mfg_date, str):
            self.mfg_date = datetime.strptime(mfg_date.strip(), "%Y-%m-%d").date()
        else:
            self.mfg_date = mfg_date

        # Parse expiry date
        if isinstance(expiry_date, str):
            self.expiry_date = datetime.strptime(expiry_date.strip(), "%Y-%m-%d").date()
        else:
            self.expiry_date = expiry_date

        self.validate()

    def validate(self) -> None:
        """
        Validates medicine batch details.
        Raises ValueError with an understandable message if constraints are violated.
        """
        if not self.batch_id:
            raise ValueError("Batch ID is required and cannot be empty.")
        if not self.medicine_name:
            raise ValueError("Medicine name is required.")
        if not self.batch_number:
            raise ValueError("Batch number is required.")
        if self.quantity < 0:
            raise ValueError(f"Quantity cannot be negative (got {self.quantity}).")
        if self.min_stock_level < 0:
            raise ValueError(f"Minimum stock level cannot be negative (got {self.min_stock_level}).")
        if self.unit_price < 0.0:
            raise ValueError(f"Unit price cannot be negative (got {self.unit_price}).")
        if self.mfg_date > self.expiry_date:
            raise ValueError(
                f"Manufacturing date ({self.mfg_date}) cannot be after Expiry date ({self.expiry_date})."
            )

    def is_expired(self, reference_date: Optional[date] = None) -> bool:
        """
        Returns True if the batch has expired relative to the reference date (defaults to today).
        Rule: Expiry date is strictly earlier than today.
        """
        ref = reference_date or date.today()
        return self.expiry_date < ref

    def is_expiring_soon(self, threshold_days: int = 30, reference_date: Optional[date] = None) -> bool:
        """
        Returns True if the medicine has not expired and expires within the next threshold_days.
        Rule: today <= expiry_date <= today + threshold_days.
        """
        ref = reference_date or date.today()
        if self.is_expired(ref):
            return False
        delta_days = (self.expiry_date - ref).days
        return 0 <= delta_days <= threshold_days

    def days_until_expiry(self, reference_date: Optional[date] = None) -> int:
        """
        Returns number of days remaining until expiry (positive),
        or days overdue if negative.
        """
        ref = reference_date or date.today()
        return (self.expiry_date - ref).days

    def expiry_status(self, threshold_days: int = 30, reference_date: Optional[date] = None) -> str:
        """
        Returns a human-readable expiry classification:
        - 'Expired'
        - 'Expiring Soon'
        - 'Valid'
        """
        ref = reference_date or date.today()
        if self.is_expired(ref):
            return "Expired"
        elif self.is_expiring_soon(threshold_days, ref):
            return "Expiring Soon"
        return "Valid"

    def is_low_stock(self) -> bool:
        """Returns True if the batch quantity falls below its minimum stock level."""
        return self.quantity < self.min_stock_level

    def stock_status(self, reference_date: Optional[date] = None) -> str:
        """
        Returns combined stock and safety status for display.
        Prioritizes safety: Expired items are flagged first.
        """
        ref = reference_date or date.today()
        if self.is_expired(ref):
            return "Expired"
        if self.quantity == 0:
            return "Out of Stock"
        if self.is_low_stock():
            return "Low Stock"
        if self.is_expiring_soon(30, ref):
            return "Expiring Soon"
        return "In Stock"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes batch to dictionary matching CSV column layout."""
        return {
            "batch_id": self.batch_id,
            "medicine_name": self.medicine_name,
            "category": self.category,
            "batch_number": self.batch_number,
            "manufacturer": self.manufacturer,
            "quantity": int(self.quantity),
            "min_stock_level": int(self.min_stock_level),
            "unit_price": round(float(self.unit_price), 2),
            "mfg_date": self.mfg_date.strftime("%Y-%m-%d"),
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d"),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MedicineBatch":
        """Instantiates a MedicineBatch from a dictionary or CSV row."""
        return cls(
            batch_id=str(data.get("batch_id", "")),
            medicine_name=str(data.get("medicine_name", "")),
            category=str(data.get("category", "General")),
            batch_number=str(data.get("batch_number", "")),
            manufacturer=str(data.get("manufacturer", "")),
            quantity=int(data.get("quantity", 0)),
            min_stock_level=int(data.get("min_stock_level", 10)),
            unit_price=float(data.get("unit_price", 0.0)),
            mfg_date=str(data.get("mfg_date", "")),
            expiry_date=str(data.get("expiry_date", "")),
            created_at=data.get("created_at"),
        )


class ConsumptionRecord(BaseEntity):
    """
    Represents an audit record of medicine consumption or dispensing.
    
    Attributes:
        record_id (str): Unique consumption record identifier (e.g. 'CON-1001')
        medicine_name (str): Name of the consumed medicine
        batch_id (str): ID of the inventory batch deducted from
        consumption_date (date): Date of dispensing/consumption
        quantity_consumed (int): Number of units consumed (positive integer)
        notes (str): Contextual remarks (e.g. 'OPD Prescription', 'Ward Transfer')
    """

    def __init__(
        self,
        record_id: str,
        medicine_name: str,
        batch_id: str,
        consumption_date: Union[date, str],
        quantity_consumed: int,
        notes: str = "",
        created_at: Optional[str] = None,
    ):
        super().__init__(record_id, created_at)
        self.record_id = self.entity_id
        self.medicine_name = medicine_name.strip() if medicine_name else ""
        self.batch_id = batch_id.strip() if batch_id else ""
        self.quantity_consumed = int(quantity_consumed)
        self.notes = notes.strip() if notes else ""

        if isinstance(consumption_date, str):
            self.consumption_date = datetime.strptime(
                consumption_date.strip(), "%Y-%m-%d"
            ).date()
        else:
            self.consumption_date = consumption_date

        self.validate()

    def validate(self) -> None:
        """Validates consumption record integrity."""
        if not self.record_id:
            raise ValueError("Record ID is required.")
        if not self.medicine_name:
            raise ValueError("Medicine name is required.")
        if self.quantity_consumed <= 0:
            raise ValueError(
                f"Quantity consumed must be greater than zero (got {self.quantity_consumed})."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes record to dictionary matching CSV format."""
        return {
            "record_id": self.record_id,
            "medicine_name": self.medicine_name,
            "batch_id": self.batch_id,
            "consumption_date": self.consumption_date.strftime("%Y-%m-%d"),
            "quantity_consumed": int(self.quantity_consumed),
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConsumptionRecord":
        """Instantiates a ConsumptionRecord from a dictionary or CSV row."""
        return cls(
            record_id=str(data.get("record_id", "")),
            medicine_name=str(data.get("medicine_name", "")),
            batch_id=str(data.get("batch_id", "")),
            consumption_date=str(data.get("consumption_date", "")),
            quantity_consumed=int(data.get("quantity_consumed", 0)),
            notes=str(data.get("notes", "")),
            created_at=data.get("created_at"),
        )
