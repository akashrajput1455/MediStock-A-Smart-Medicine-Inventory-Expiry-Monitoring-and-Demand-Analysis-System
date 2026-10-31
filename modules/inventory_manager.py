"""
MediStock Inventory Manager Module.

Encapsulates all medicine inventory operations, batch management,
validation rules, stock status calculations, and FEFO (First Expiring, First Out)
stock dispensing logic.
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from modules.models import ConsumptionRecord, MedicineBatch
from utils.data_manager import DataManager


class InventoryManager:
    """
    Manages pharmaceutical batch inventory with domain validation,
    safety checks, and CSV persistence via DataManager.
    """

    def __init__(self, data_manager: Optional[DataManager] = None):
        self.data_manager = data_manager or DataManager()
        self._batches: List[MedicineBatch] = []
        self.refresh_from_storage()

    def refresh_from_storage(self) -> None:
        """Reloads batches from the underlying CSV data store."""
        raw_records = self.data_manager.load_inventory_records()
        self._batches = []
        for raw in raw_records:
            try:
                batch = MedicineBatch.from_dict(raw)
                self._batches.append(batch)
            except Exception as e:
                print(f"[InventoryManager Warning] Skipping corrupted record: {raw}. Error: {e}")

    def save_to_storage(self) -> bool:
        """Serializes current in-memory batches and persists them to CSV."""
        record_dicts = [batch.to_dict() for batch in self._batches]
        return self.data_manager.save_inventory_records(record_dicts)

    def get_all_batches(self) -> List[MedicineBatch]:
        """Returns a copy of all registered medicine batches."""
        return list(self._batches)

    def get_batch(self, batch_id: str) -> Optional[MedicineBatch]:
        """Finds a batch by unique batch_id."""
        b_id = str(batch_id).strip().upper()
        for batch in self._batches:
            if batch.batch_id.upper() == b_id:
                return batch
        return None

    def add_batch(self, batch: MedicineBatch) -> Tuple[bool, str]:
        """
        Validates and adds a new medicine batch to the inventory.
        Enforces unique batch_id and domain integrity constraints.
        """
        try:
            batch.validate()
        except ValueError as ve:
            return False, f"Validation Error: {str(ve)}"

        # Check for duplicate batch_id
        if self.get_batch(batch.batch_id) is not None:
            return False, f"Batch ID '{batch.batch_id}' already exists in inventory."

        self._batches.append(batch)
        if self.save_to_storage():
            return True, f"Batch '{batch.batch_id}' for '{batch.medicine_name}' added successfully."
        else:
            self._batches.pop()
            return False, "Failed to persist batch to CSV storage."

    def update_batch(self, batch_id: str, updated_batch: MedicineBatch) -> Tuple[bool, str]:
        """
        Updates an existing batch with new attributes after validation.
        """
        try:
            updated_batch.validate()
        except ValueError as ve:
            return False, f"Validation Error: {str(ve)}"

        index_to_update = -1
        b_id = str(batch_id).strip().upper()
        for i, b in enumerate(self._batches):
            if b.batch_id.upper() == b_id:
                index_to_update = i
                break

        if index_to_update == -1:
            return False, f"Batch '{batch_id}' not found."

        old_batch = self._batches[index_to_update]
        self._batches[index_to_update] = updated_batch

        if self.save_to_storage():
            return True, f"Batch '{batch_id}' updated successfully."
        else:
            self._batches[index_to_update] = old_batch
            return False, "Failed to persist updated batch to storage."

    def delete_batch(self, batch_id: str) -> Tuple[bool, str]:
        """
        Deletes a batch from inventory.
        """
        b_id = str(batch_id).strip().upper()
        initial_len = len(self._batches)
        self._batches = [b for b in self._batches if b.batch_id.upper() != b_id]

        if len(self._batches) == initial_len:
            return False, f"Batch '{batch_id}' not found."

        if self.save_to_storage():
            return True, f"Batch '{batch_id}' deleted successfully."
        else:
            self.refresh_from_storage()
            return False, "Failed to persist deletion to storage."

    def search_and_filter(
        self,
        query: str = "",
        category: str = "All",
        expiry_filter: str = "All",
        stock_filter: str = "All",
        reference_date: Optional[date] = None,
    ) -> List[MedicineBatch]:
        """
        Searches and filters batches based on query text, category, expiry state, and stock level.
        """
        ref = reference_date or date.today()
        filtered = self._batches

        # 1. Search text (matches name, batch_number, manufacturer, or batch_id)
        if query and query.strip():
            q = query.strip().lower()
            filtered = [
                b for b in filtered
                if q in b.medicine_name.lower()
                or q in b.batch_number.lower()
                or q in b.batch_id.lower()
                or q in b.manufacturer.lower()
            ]

        # 2. Filter by Category
        if category and category != "All":
            filtered = [b for b in filtered if b.category.lower() == category.lower()]

        # 3. Filter by Expiry Status
        if expiry_filter == "Expired":
            filtered = [b for b in filtered if b.is_expired(ref)]
        elif expiry_filter == "Expiring Soon (<7 Days)":
            filtered = [b for b in filtered if b.is_expiring_soon(7, ref)]
        elif expiry_filter == "Expiring Soon (<30 Days)":
            filtered = [b for b in filtered if b.is_expiring_soon(30, ref)]
        elif expiry_filter == "Valid":
            filtered = [b for b in filtered if not b.is_expired(ref) and not b.is_expiring_soon(30, ref)]

        # 4. Filter by Stock Status
        if stock_filter == "Low Stock":
            filtered = [b for b in filtered if b.is_low_stock() and not b.is_expired(ref)]
        elif stock_filter == "Out of Stock":
            filtered = [b for b in filtered if b.quantity == 0 and not b.is_expired(ref)]
        elif stock_filter == "In Stock":
            filtered = [b for b in filtered if b.quantity >= b.min_stock_level and not b.is_expired(ref)]

        return filtered

    def get_categories(self) -> List[str]:
        """Returns sorted unique category names present in inventory."""
        cats = sorted(list({b.category for b in self._batches if b.category}))
        return cats

    def get_medicine_names(self) -> List[str]:
        """Returns sorted unique medicine names."""
        names = sorted(list({b.medicine_name for b in self._batches if b.medicine_name}))
        return names

    def get_available_stock_by_medicine(self, reference_date: Optional[date] = None) -> Dict[str, int]:
        """
        Calculates non-expired available stock aggregated by medicine name.
        CRITICAL RULE: Expired batches MUST NOT contribute to routine available stock.
        """
        ref = reference_date or date.today()
        stock_map: Dict[str, int] = {}

        # Initialize all known medicines with 0 stock
        for b in self._batches:
            if b.medicine_name not in stock_map:
                stock_map[b.medicine_name] = 0

        # Sum quantities only from non-expired batches
        for b in self._batches:
            if not b.is_expired(ref):
                stock_map[b.medicine_name] = stock_map.get(b.medicine_name, 0) + b.quantity

        return stock_map

    def get_total_available_units(self, reference_date: Optional[date] = None) -> int:
        """Returns total units of all non-expired medicines in stock."""
        ref = reference_date or date.today()
        return sum(b.quantity for b in self._batches if not b.is_expired(ref))

    def get_expired_batches(self, reference_date: Optional[date] = None) -> List[MedicineBatch]:
        """Returns all batches where expiry date is strictly earlier than reference date."""
        ref = reference_date or date.today()
        expired = [b for b in self._batches if b.is_expired(ref)]
        # Sort by most overdue first
        expired.sort(key=lambda b: b.expiry_date)
        return expired

    def get_expiring_soon_batches(
        self, threshold_days: int = 30, reference_date: Optional[date] = None
    ) -> List[MedicineBatch]:
        """Returns non-expired batches expiring within the specified threshold."""
        ref = reference_date or date.today()
        soon = [b for b in self._batches if b.is_expiring_soon(threshold_days, ref)]
        # Sort by earliest expiry first (urgent batches on top)
        soon.sort(key=lambda b: b.expiry_date)
        return soon

    def get_low_stock_summary(self, reference_date: Optional[date] = None) -> List[Dict]:
        """
        Computes medicine-level low stock report with shortage and reorder calculations.
        Considers only non-expired available stock.
        """
        ref = reference_date or date.today()
        available_stocks = self.get_available_stock_by_medicine(ref)

        # Aggregate minimum stock thresholds and target levels per medicine
        min_thresholds: Dict[str, int] = {}
        for b in self._batches:
            # We use the maximum configured min_stock_level among batches as medicine baseline
            current_max = min_thresholds.get(b.medicine_name, 0)
            if b.min_stock_level > current_max:
                min_thresholds[b.medicine_name] = b.min_stock_level

        low_stock_list: List[Dict] = []
        for med_name, avail in available_stocks.items():
            threshold = min_thresholds.get(med_name, 10)
            if avail < threshold:
                shortage = max(0, threshold - avail)
                # Suggested reorder target = 2x threshold (buffer stock)
                target_stock = threshold * 2
                suggested_reorder = max(0, target_stock - avail)

                low_stock_list.append({
                    "medicine_name": med_name,
                    "available_stock": avail,
                    "min_stock_level": threshold,
                    "shortage": shortage,
                    "suggested_reorder": suggested_reorder,
                })

        # Sort by greatest shortage first
        low_stock_list.sort(key=lambda x: x["shortage"], reverse=True)
        return low_stock_list

    def deduct_stock_fefo(
        self,
        medicine_name: str,
        quantity: int,
        consumption_date: Optional[date] = None,
        notes: str = "",
        reference_date: Optional[date] = None,
    ) -> Tuple[bool, str, List[Tuple[str, int]]]:
        """
        Dispenses/deducts medicine stock using the standard healthcare FEFO rule
        (First Expiring, First Out).
        
        Steps:
        1. Validates that requested quantity is positive.
        2. Retrieves all valid non-expired batches for the medicine.
        3. Verifies total non-expired stock >= requested quantity.
        4. Sorts candidate batches by expiry_date ascending (earliest expiring first).
        5. Deducts sequentially from batches without allowing any batch to become negative.
        6. Creates and persists audit ConsumptionRecords for each deduction.
        7. Saves updated inventory.
        
        Returns:
            (success_bool, message, list_of_(batch_id, deducted_qty))
        """
        if quantity <= 0:
            return False, f"Quantity to dispense must be greater than zero (got {quantity}).", []

        ref = reference_date or date.today()
        cons_date = consumption_date or ref

        # Gather eligible non-expired batches with quantity > 0
        eligible_batches = [
            b for b in self._batches
            if b.medicine_name.lower() == medicine_name.strip().lower()
            and not b.is_expired(ref)
            and b.quantity > 0
        ]

        total_available = sum(b.quantity for b in eligible_batches)
        if total_available < quantity:
            return (
                False,
                f"Insufficient non-expired stock for '{medicine_name}'. "
                f"Available: {total_available} units, Requested: {quantity} units.",
                [],
            )

        # Sort eligible batches by expiry date (FEFO principle)
        eligible_batches.sort(key=lambda b: b.expiry_date)

        deductions: List[Tuple[str, int]] = []
        remaining_to_deduct = quantity
        new_consumption_records: List[Dict] = []

        # Generate unique starting ID for audit records
        existing_con = self.data_manager.load_consumption_records()
        next_con_num = len(existing_con) + 1

        for batch in eligible_batches:
            if remaining_to_deduct <= 0:
                break

            deduct_from_this_batch = min(batch.quantity, remaining_to_deduct)
            batch.quantity -= deduct_from_this_batch
            remaining_to_deduct -= deduct_from_this_batch

            deductions.append((batch.batch_id, deduct_from_this_batch))

            # Prepare consumption audit record
            rec_id = f"CON-{next_con_num:04d}"
            next_con_num += 1

            new_record = ConsumptionRecord(
                record_id=rec_id,
                medicine_name=batch.medicine_name,
                batch_id=batch.batch_id,
                consumption_date=cons_date,
                quantity_consumed=deduct_from_this_batch,
                notes=notes or f"Dispensed {deduct_from_this_batch} units from batch {batch.batch_id}",
            )
            new_consumption_records.append(new_record.to_dict())

        # Persist both inventory changes and consumption records atomically
        inv_saved = self.save_to_storage()
        if not inv_saved:
            self.refresh_from_storage()
            return False, "Failed to save updated inventory during deduction.", []

        # Append consumption records
        for con_rec in new_consumption_records:
            self.data_manager.append_consumption_record(con_rec)

        summary_details = ", ".join(f"{b_id}: {qty} units" for b_id, qty in deductions)
        return (
            True,
            f"Successfully dispensed {quantity} units of '{medicine_name}' via FEFO ({summary_details}).",
            deductions,
        )
