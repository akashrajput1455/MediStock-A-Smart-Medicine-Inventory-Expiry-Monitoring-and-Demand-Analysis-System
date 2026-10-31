"""
MediStock Comprehensive Unit Test Suite.

Tests domain models, inventory operations, validation constraints,
FEFO stock deduction, statistical demand calculations, and persistence.
Uses Python's standard `unittest` framework with isolated temporary directories.
"""

import shutil
import tempfile
import unittest
from datetime import date, timedelta

from modules.demand_analyzer import DemandAnalyzer
from modules.inventory_manager import InventoryManager
from modules.models import ConsumptionRecord, MedicineBatch
from utils.data_manager import DataManager


class TestMediStock(unittest.TestCase):
    """Unit test cases covering all required academic project assertions."""

    def setUp(self):
        """Set up an isolated temporary storage directory for each test."""
        self.test_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(
            data_dir=self.test_dir,
            inventory_file="test_inventory.csv",
            consumption_file="test_consumption.csv",
        )
        self.inventory_manager = InventoryManager(self.data_manager)
        self.demand_analyzer = DemandAnalyzer(self.inventory_manager, self.data_manager)
        self.ref_date = date(2025, 6, 1)

    def tearDown(self):
        """Clean up temporary test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_sample_batch(
        self,
        batch_id="BAT-001",
        name="Paracetamol 500mg",
        qty=100,
        min_stock=50,
        price=2.5,
        mfg_date="2024-01-01",
        expiry_date="2025-12-31",
    ) -> MedicineBatch:
        return MedicineBatch(
            batch_id=batch_id,
            medicine_name=name,
            category="Analgesic",
            batch_number="BN-01",
            manufacturer="Cipla",
            quantity=qty,
            min_stock_level=min_stock,
            unit_price=price,
            mfg_date=mfg_date,
            expiry_date=expiry_date,
        )

    # 1. Adding a valid medicine batch
    def test_01_add_valid_batch(self):
        batch = self._create_sample_batch()
        success, msg = self.inventory_manager.add_batch(batch)
        self.assertTrue(success, f"Failed to add valid batch: {msg}")
        self.assertEqual(len(self.inventory_manager.get_all_batches()), 1)
        retrieved = self.inventory_manager.get_batch("BAT-001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.medicine_name, "Paracetamol 500mg")

    # 2. Rejecting duplicate batch identifiers
    def test_02_reject_duplicate_batch_id(self):
        batch1 = self._create_sample_batch(batch_id="BAT-DUP")
        success1, _ = self.inventory_manager.add_batch(batch1)
        self.assertTrue(success1)

        batch2 = self._create_sample_batch(batch_id="BAT-DUP", name="Different Med")
        success2, msg = self.inventory_manager.add_batch(batch2)
        self.assertFalse(success2)
        self.assertIn("already exists", msg.lower())
        self.assertEqual(len(self.inventory_manager.get_all_batches()), 1)

    # 3. Rejecting negative quantities
    def test_03_reject_negative_quantity(self):
        with self.assertRaises(ValueError):
            self._create_sample_batch(qty=-10)

    # 4. Rejecting manufacturing date after expiry date
    def test_04_reject_invalid_date_order(self):
        with self.assertRaises(ValueError):
            self._create_sample_batch(mfg_date="2025-12-31", expiry_date="2024-01-01")

    # 5. Detecting an expired batch
    def test_05_detect_expired_batch(self):
        # Expiry is 2025-05-15, which is before reference date 2025-06-01
        expired_batch = self._create_sample_batch(
            batch_id="BAT-EXP",
            mfg_date="2024-01-01",
            expiry_date="2025-05-15",
        )
        self.assertTrue(expired_batch.is_expired(self.ref_date))
        self.assertEqual(expired_batch.expiry_status(reference_date=self.ref_date), "Expired")

    # 6. Detecting a batch approaching expiry (expiring soon)
    def test_06_detect_expiring_soon_batch(self):
        # Expiry is 2025-06-15, which is 14 days after ref_date 2025-06-01 (<= 30 days)
        soon_batch = self._create_sample_batch(
            batch_id="BAT-SOON",
            mfg_date="2024-01-01",
            expiry_date="2025-06-15",
        )
        self.assertFalse(soon_batch.is_expired(self.ref_date))
        self.assertTrue(soon_batch.is_expiring_soon(30, self.ref_date))
        self.assertEqual(soon_batch.expiry_status(30, self.ref_date), "Expiring Soon")

    # 7. Detecting low stock
    def test_07_detect_low_stock(self):
        low_batch = self._create_sample_batch(qty=15, min_stock=40)
        self.assertTrue(low_batch.is_low_stock())

        adequate_batch = self._create_sample_batch(qty=50, min_stock=40)
        self.assertFalse(adequate_batch.is_low_stock())

    # 8. Excluding expired batches from available stock calculation
    def test_08_exclude_expired_from_available_stock(self):
        # Add 1 valid batch of 100 units
        valid_batch = self._create_sample_batch(
            batch_id="BAT-V1",
            name="Amoxicillin 500mg",
            qty=100,
            expiry_date="2026-01-01",
        )
        # Add 1 expired batch of 50 units
        expired_batch = self._create_sample_batch(
            batch_id="BAT-E1",
            name="Amoxicillin 500mg",
            qty=50,
            expiry_date="2025-05-01",
        )
        self.inventory_manager.add_batch(valid_batch)
        self.inventory_manager.add_batch(expired_batch)

        available_map = self.inventory_manager.get_available_stock_by_medicine(self.ref_date)
        # Available should only be 100 units, NOT 150 units!
        self.assertEqual(available_map.get("Amoxicillin 500mg"), 100)

    # 9. Calculating average daily consumption
    def test_09_calculate_average_daily_consumption(self):
        # 60 units consumed over a 30-day window => ADC = 2.0
        self.data_manager.append_consumption_record({
            "record_id": "CON-01",
            "medicine_name": "Paracetamol 500mg",
            "batch_id": "BAT-01",
            "consumption_date": "2025-05-20",
            "quantity_consumed": 40,
            "notes": "OPD",
            "created_at": "2025-05-20",
        })
        self.data_manager.append_consumption_record({
            "record_id": "CON-02",
            "medicine_name": "Paracetamol 500mg",
            "batch_id": "BAT-01",
            "consumption_date": "2025-05-25",
            "quantity_consumed": 20,
            "notes": "Emergency",
            "created_at": "2025-05-25",
        })

        metrics = self.demand_analyzer.calculate_demand_metrics(
            analysis_days=30, coverage_days=30, reference_date=self.ref_date
        )
        row = metrics[metrics["Medicine Name"] == "Paracetamol 500mg"].iloc[0]
        self.assertEqual(row["Consumed (30d)"], 60)
        self.assertAlmostEqual(row["Avg Daily (ADC)"], 2.0, places=2)

    # 10. Calculating estimated stock coverage and suggested reorder
    def test_10_calculate_stock_coverage_and_reorder(self):
        # Add 30 units of available stock
        batch = self._create_sample_batch(
            batch_id="BAT-REC",
            name="Metformin 500mg",
            qty=30,
            expiry_date="2026-01-01",
        )
        self.inventory_manager.add_batch(batch)

        # 90 units consumed over 30 days => ADC = 3.0 units/day
        self.data_manager.append_consumption_record({
            "record_id": "CON-10",
            "medicine_name": "Metformin 500mg",
            "batch_id": "BAT-REC",
            "consumption_date": "2025-05-15",
            "quantity_consumed": 90,
            "notes": "Diabetic OPD",
            "created_at": "2025-05-15",
        })

        # Coverage days = 30 days
        # ADC = 3.0
        # Available stock = 30
        # Stock Coverage Days = 30 / 3.0 = 10.0 days
        # Required for 30 days = 3.0 * 30 = 90 units
        # Suggested Reorder = 90 - 30 = 60 units
        metrics = self.demand_analyzer.calculate_demand_metrics(
            analysis_days=30, coverage_days=30, reference_date=self.ref_date
        )
        row = metrics[metrics["Medicine Name"] == "Metformin 500mg"].iloc[0]
        self.assertAlmostEqual(row["Stock Coverage (Days)"], 10.0, places=1)
        self.assertEqual(row["Suggested Reorder"], 60)

    # 11. Handling empty consumption dataset gracefully
    def test_11_handle_empty_consumption(self):
        batch = self._create_sample_batch(
            batch_id="BAT-EMPTY",
            name="Cetirizine 10mg",
            qty=80,
            expiry_date="2026-01-01",
        )
        self.inventory_manager.add_batch(batch)

        metrics = self.demand_analyzer.calculate_demand_metrics(
            analysis_days=30, coverage_days=30, reference_date=self.ref_date
        )
        self.assertFalse(metrics.empty)
        row = metrics[metrics["Medicine Name"] == "Cetirizine 10mg"].iloc[0]
        self.assertEqual(row["Consumed (30d)"], 0)
        self.assertEqual(row["Avg Daily (ADC)"], 0.0)
        self.assertEqual(row["Suggested Reorder"], 0)

    # 12. Preventing stock from becoming negative (insufficient stock validation)
    def test_12_prevent_negative_stock(self):
        batch = self._create_sample_batch(
            batch_id="BAT-LIM",
            name="Ibuprofen 400mg",
            qty=20,
            expiry_date="2026-01-01",
        )
        self.inventory_manager.add_batch(batch)

        # Attempt to dispense 50 units when only 20 are available
        success, msg, deductions = self.inventory_manager.deduct_stock_fefo(
            medicine_name="Ibuprofen 400mg",
            quantity=50,
            consumption_date=self.ref_date,
            reference_date=self.ref_date,
        )
        self.assertFalse(success)
        self.assertIn("Insufficient", msg)
        self.assertEqual(len(deductions), 0)
        # Verify batch quantity remained unchanged at 20
        self.assertEqual(self.inventory_manager.get_batch("BAT-LIM").quantity, 20)

    # 13. FEFO Dispensing: First Expiring batch is deducted first
    def test_13_fefo_dispensing_order(self):
        # Batch 1 expires in July 2025 (earlier) with 30 units
        batch_earlier = self._create_sample_batch(
            batch_id="BAT-FEFO-1",
            name="Azithromycin 250mg",
            qty=30,
            expiry_date="2025-07-01",
        )
        # Batch 2 expires in December 2025 (later) with 50 units
        batch_later = self._create_sample_batch(
            batch_id="BAT-FEFO-2",
            name="Azithromycin 250mg",
            qty=50,
            expiry_date="2025-12-01",
        )
        self.inventory_manager.add_batch(batch_earlier)
        self.inventory_manager.add_batch(batch_later)

        # Dispense 40 units: should take all 30 from BAT-FEFO-1 and 10 from BAT-FEFO-2
        success, msg, deductions = self.inventory_manager.deduct_stock_fefo(
            medicine_name="Azithromycin 250mg",
            quantity=40,
            consumption_date=self.ref_date,
            reference_date=self.ref_date,
        )
        self.assertTrue(success, msg)
        self.assertEqual(deductions, [("BAT-FEFO-1", 30), ("BAT-FEFO-2", 10)])

        # Check in-memory & persisted states
        b1 = self.inventory_manager.get_batch("BAT-FEFO-1")
        b2 = self.inventory_manager.get_batch("BAT-FEFO-2")
        self.assertEqual(b1.quantity, 0)
        self.assertEqual(b2.quantity, 40)

    # 14. Preserving existing records when invalid input is submitted
    def test_14_preserve_records_on_invalid_input(self):
        batch = self._create_sample_batch(batch_id="BAT-KEEP")
        self.inventory_manager.add_batch(batch)
        initial_count = len(self.inventory_manager.get_all_batches())

        # Attempt to add batch with empty name
        with self.assertRaises(ValueError):
            bad_batch = self._create_sample_batch(batch_id="BAT-BAD", name="")
            bad_batch.validate()

        # Ensure original record remains intact
        self.assertEqual(len(self.inventory_manager.get_all_batches()), initial_count)
        self.assertIsNotNone(self.inventory_manager.get_batch("BAT-KEEP"))


if __name__ == "__main__":
    unittest.main()
