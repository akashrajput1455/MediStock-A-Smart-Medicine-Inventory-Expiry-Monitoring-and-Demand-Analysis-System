"""
MediStock Data Storage Manager.

Handles safe CSV file operations for medicine batches and consumption records.
Demonstrates practical file I/O, error handling, defensive programming, and
data persistence in Python without requiring external database engines.
"""

import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataManager:
    """
    Manages persistence of inventory batches and consumption records using CSV files.
    """

    INVENTORY_COLUMNS = [
        "batch_id",
        "medicine_name",
        "category",
        "batch_number",
        "manufacturer",
        "quantity",
        "min_stock_level",
        "unit_price",
        "mfg_date",
        "expiry_date",
        "created_at",
    ]

    CONSUMPTION_COLUMNS = [
        "record_id",
        "medicine_name",
        "batch_id",
        "consumption_date",
        "quantity_consumed",
        "notes",
        "created_at",
    ]

    def __init__(
        self,
        data_dir: str = "data",
        inventory_file: str = "medicine_inventory.csv",
        consumption_file: str = "consumption_records.csv",
    ):
        self.data_dir = Path(data_dir)
        self.inventory_path = self.data_dir / inventory_file
        self.consumption_path = self.data_dir / consumption_file
        self.ensure_storage_initialized()

    def ensure_storage_initialized(self) -> None:
        """
        Creates the data directory and initializes CSV files with headers
        if they do not already exist.
        """
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.inventory_path.exists():
            self._write_csv_headers(self.inventory_path, self.INVENTORY_COLUMNS)

        if not self.consumption_path.exists():
            self._write_csv_headers(self.consumption_path, self.CONSUMPTION_COLUMNS)

    def _write_csv_headers(self, file_path: Path, columns: List[str]) -> None:
        """Helper to write CSV column headers."""
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

    def load_inventory_records(self) -> List[Dict[str, Any]]:
        """
        Reads all medicine inventory records from CSV.
        Returns a list of dictionaries. Returns an empty list if file is missing or empty.
        """
        if not self.inventory_path.exists():
            return []

        records: List[Dict[str, Any]] = []
        try:
            with open(self.inventory_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and any(row.values()):
                        records.append(row)
        except Exception as e:
            print(f"[DataManager Warning] Error reading inventory CSV: {e}")
            return []

        return records

    def save_inventory_records(self, records: List[Dict[str, Any]]) -> bool:
        """
        Saves a list of inventory records to CSV atomically.
        Uses a temporary file to prevent corruption if interrupted.
        """
        temp_file = self.inventory_path.with_suffix(".tmp")
        try:
            with open(temp_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.INVENTORY_COLUMNS, extrasaction="ignore"
                )
                writer.writeheader()
                for rec in records:
                    writer.writerow(rec)
            # Atomic rename
            temp_file.replace(self.inventory_path)
            return True
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            print(f"[DataManager Error] Failed to save inventory: {e}")
            return False

    def load_consumption_records(self) -> List[Dict[str, Any]]:
        """
        Reads all consumption records from CSV.
        Returns a list of dictionaries.
        """
        if not self.consumption_path.exists():
            return []

        records: List[Dict[str, Any]] = []
        try:
            with open(self.consumption_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and any(row.values()):
                        records.append(row)
        except Exception as e:
            print(f"[DataManager Warning] Error reading consumption CSV: {e}")
            return []

        return records

    def save_consumption_records(self, records: List[Dict[str, Any]]) -> bool:
        """
        Saves consumption records to CSV atomically.
        """
        temp_file = self.consumption_path.with_suffix(".tmp")
        try:
            with open(temp_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=self.CONSUMPTION_COLUMNS, extrasaction="ignore"
                )
                writer.writeheader()
                for rec in records:
                    writer.writerow(rec)
            temp_file.replace(self.consumption_path)
            return True
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            print(f"[DataManager Error] Failed to save consumption: {e}")
            return False

    def append_consumption_record(self, record: Dict[str, Any]) -> bool:
        """
        Appends a single consumption record directly to the CSV.
        """
        try:
            records = self.load_consumption_records()
            records.append(record)
            return self.save_consumption_records(records)
        except Exception as e:
            print(f"[DataManager Error] Failed to append consumption: {e}")
            return False

    def get_inventory_csv_string(self) -> str:
        """Returns the complete raw CSV content of the inventory file for export."""
        if not self.inventory_path.exists():
            return ",".join(self.INVENTORY_COLUMNS) + "\n"
        with open(self.inventory_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_consumption_csv_string(self) -> str:
        """Returns the complete raw CSV content of the consumption file for export."""
        if not self.consumption_path.exists():
            return ",".join(self.CONSUMPTION_COLUMNS) + "\n"
        with open(self.consumption_path, "r", encoding="utf-8") as f:
            return f.read()

    def backup_data(self, backup_dir: str = "data/backups") -> Optional[str]:
        """Creates a timestamped backup of both CSV files."""
        try:
            b_dir = Path(backup_dir)
            b_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            inv_backup = b_dir / f"inventory_backup_{timestamp}.csv"
            con_backup = b_dir / f"consumption_backup_{timestamp}.csv"

            if self.inventory_path.exists():
                shutil.copy2(self.inventory_path, inv_backup)
            if self.consumption_path.exists():
                shutil.copy2(self.consumption_path, con_backup)
            return timestamp
        except Exception as e:
            print(f"[DataManager Error] Backup failed: {e}")
            return None
