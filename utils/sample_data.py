"""
MediStock Sample Demonstration Data Generator.

Provides a realistic, deterministic demonstration dataset of:
- 20 medicine batches across diverse therapeutic categories
- 45+ historical consumption records spanning the last 60 days
- Includes expired, expiring soon, low-stock, and multi-batch scenarios
- Dates are computed dynamically relative to today's date so the demo remains
  perpetually fresh for vivas and presentations.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple


def generate_sample_batches(base_date: date = None) -> List[Dict]:
    """
    Generates 20 realistic pharmaceutical batches.
    Dates are calculated relative to `base_date` (defaults to today).
    """
    today = base_date or date.today()

    batches = [
        # 1. Paracetamol 500mg - Multiple batches (Batch 1: Expiring very soon in 6 days)
        {
            "batch_id": "BAT-1001",
            "medicine_name": "Paracetamol 500mg",
            "category": "Analgesic & Antipyretic",
            "batch_number": "PCM-2024-A1",
            "manufacturer": "Cipla Pharmaceuticals",
            "quantity": 180,
            "min_stock_level": 100,
            "unit_price": 1.50,
            "mfg_date": (today - timedelta(days=700)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=6)).strftime("%Y-%m-%d"),  # Expiring soon (<7d)
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 2. Paracetamol 500mg - Batch 2: Fresh batch (Valid for 18 months)
        {
            "batch_id": "BAT-1002",
            "medicine_name": "Paracetamol 500mg",
            "category": "Analgesic & Antipyretic",
            "batch_number": "PCM-2024-B2",
            "manufacturer": "Cipla Pharmaceuticals",
            "quantity": 600,
            "min_stock_level": 150,
            "unit_price": 1.65,
            "mfg_date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=540)).strftime("%Y-%m-%d"),  # Valid
            "created_at": (today - timedelta(days=40)).strftime("%Y-%m-%d"),
        },
        # 3. Amoxicillin 500mg - Low Stock batch
        {
            "batch_id": "BAT-1003",
            "medicine_name": "Amoxicillin 500mg",
            "category": "Antibiotic",
            "batch_number": "AMX-8901",
            "manufacturer": "Sun Pharma Ltd",
            "quantity": 25,  # Below min_stock_level 80
            "min_stock_level": 80,
            "unit_price": 6.80,
            "mfg_date": (today - timedelta(days=300)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=220)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 4. Azithromycin 500mg - Expired batch (action required!)
        {
            "batch_id": "BAT-1004",
            "medicine_name": "Azithromycin 500mg",
            "category": "Antibiotic",
            "batch_number": "AZM-7712",
            "manufacturer": "Dr. Reddy's Laboratories",
            "quantity": 40,
            "min_stock_level": 50,
            "unit_price": 14.50,
            "mfg_date": (today - timedelta(days=750)).strftime("%Y-%m-%d"),
            "expiry_date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),  # EXPIRED 20 days ago
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 5. Metformin 500mg - High volume, healthy stock
        {
            "batch_id": "BAT-1005",
            "medicine_name": "Metformin 500mg",
            "category": "Antidiabetic",
            "batch_number": "MET-4430",
            "manufacturer": "USV Pvt Ltd",
            "quantity": 450,
            "min_stock_level": 120,
            "unit_price": 2.20,
            "mfg_date": (today - timedelta(days=120)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=400)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 6. Amlodipine 5mg - Expiring in 21 days (< 30 days)
        {
            "batch_id": "BAT-1006",
            "medicine_name": "Amlodipine 5mg",
            "category": "Cardiovascular",
            "batch_number": "AML-3319",
            "manufacturer": "Torrent Pharma",
            "quantity": 90,
            "min_stock_level": 100,  # Also low stock
            "unit_price": 2.90,
            "mfg_date": (today - timedelta(days=680)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=21)).strftime("%Y-%m-%d"),  # Expiring soon
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 7. Pantoprazole 40mg - Stable stock
        {
            "batch_id": "BAT-1007",
            "medicine_name": "Pantoprazole 40mg",
            "category": "Gastrointestinal",
            "batch_number": "PAN-9021",
            "manufacturer": "Alkem Laboratories",
            "quantity": 320,
            "min_stock_level": 80,
            "unit_price": 4.50,
            "mfg_date": (today - timedelta(days=100)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=480)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 8. Montelukast 10mg - Low Stock
        {
            "batch_id": "BAT-1008",
            "medicine_name": "Montelukast 10mg",
            "category": "Respiratory",
            "batch_number": "MON-6102",
            "manufacturer": "Mankind Pharma",
            "quantity": 18,  # Below min 60
            "min_stock_level": 60,
            "unit_price": 8.00,
            "mfg_date": (today - timedelta(days=180)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=320)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 9. Cetirizine 10mg - Healthy stock
        {
            "batch_id": "BAT-1009",
            "medicine_name": "Cetirizine 10mg",
            "category": "Antihistamine",
            "batch_number": "CET-1120",
            "manufacturer": "Dr. Reddy's Laboratories",
            "quantity": 280,
            "min_stock_level": 70,
            "unit_price": 1.80,
            "mfg_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=420)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 10. Atorvastatin 20mg - Expired batch
        {
            "batch_id": "BAT-1010",
            "medicine_name": "Atorvastatin 20mg",
            "category": "Cardiovascular",
            "batch_number": "ATV-5541",
            "manufacturer": "Zydus Cadila",
            "quantity": 30,
            "min_stock_level": 50,
            "unit_price": 9.20,
            "mfg_date": (today - timedelta(days=780)).strftime("%Y-%m-%d"),
            "expiry_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),  # EXPIRED 5 days ago
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 11. Atorvastatin 20mg - Valid Batch
        {
            "batch_id": "BAT-1011",
            "medicine_name": "Atorvastatin 20mg",
            "category": "Cardiovascular",
            "batch_number": "ATV-9902",
            "manufacturer": "Zydus Cadila",
            "quantity": 210,
            "min_stock_level": 60,
            "unit_price": 9.50,
            "mfg_date": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=500)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=50)).strftime("%Y-%m-%d"),
        },
        # 12. Ibuprofen 400mg - Expiring in 14 days
        {
            "batch_id": "BAT-1012",
            "medicine_name": "Ibuprofen 400mg",
            "category": "Analgesic & Antipyretic",
            "batch_number": "IBU-3401",
            "manufacturer": "Abbott India",
            "quantity": 75,
            "min_stock_level": 80,
            "unit_price": 2.40,
            "mfg_date": (today - timedelta(days=690)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),  # Expiring soon (<15d)
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 13. Ciprofloxacin 500mg - Valid stock
        {
            "batch_id": "BAT-1013",
            "medicine_name": "Ciprofloxacin 500mg",
            "category": "Antibiotic",
            "batch_number": "CIP-4210",
            "manufacturer": "Ranbaxy / Sun Pharma",
            "quantity": 160,
            "min_stock_level": 50,
            "unit_price": 7.10,
            "mfg_date": (today - timedelta(days=110)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=390)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 14. Vitamin C 500mg (Chewable) - Good stock
        {
            "batch_id": "BAT-1014",
            "medicine_name": "Vitamin C 500mg Chewable",
            "category": "Vitamins & Supplements",
            "batch_number": "VTC-8822",
            "manufacturer": "GlaxoSmithKline (GSK)",
            "quantity": 520,
            "min_stock_level": 150,
            "unit_price": 1.20,
            "mfg_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=450)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 15. Omeprazole 20mg - Low Stock
        {
            "batch_id": "BAT-1015",
            "medicine_name": "Omeprazole 20mg",
            "category": "Gastrointestinal",
            "batch_number": "OMP-1190",
            "manufacturer": "Dr. Reddy's Laboratories",
            "quantity": 15,  # Below min 50
            "min_stock_level": 50,
            "unit_price": 3.40,
            "mfg_date": (today - timedelta(days=250)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=190)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 16. Salbutamol Inhaler 100mcg - Valid
        {
            "batch_id": "BAT-1016",
            "medicine_name": "Salbutamol Inhaler 100mcg",
            "category": "Respiratory",
            "batch_number": "SLB-7004",
            "manufacturer": "Cipla Pharmaceuticals",
            "quantity": 42,
            "min_stock_level": 25,
            "unit_price": 115.00,
            "mfg_date": (today - timedelta(days=140)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=360)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 17. Glimepiride 2mg - Expiring in 28 days
        {
            "batch_id": "BAT-1017",
            "medicine_name": "Glimepiride 2mg",
            "category": "Antidiabetic",
            "batch_number": "GLM-4011",
            "manufacturer": "Sanofi India",
            "quantity": 65,
            "min_stock_level": 60,
            "unit_price": 4.10,
            "mfg_date": (today - timedelta(days=660)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=28)).strftime("%Y-%m-%d"),  # Expiring soon
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 18. ORS Powder Sachet - High volume
        {
            "batch_id": "BAT-1018",
            "medicine_name": "Oral Rehydration Salts (ORS)",
            "category": "Emergency & Fluids",
            "batch_number": "ORS-2918",
            "manufacturer": "FDC Limited",
            "quantity": 380,
            "min_stock_level": 100,
            "unit_price": 18.00,
            "mfg_date": (today - timedelta(days=100)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=580)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 19. Ondansetron 4mg - Critical Low Stock
        {
            "batch_id": "BAT-1019",
            "medicine_name": "Ondansetron 4mg",
            "category": "Gastrointestinal",
            "batch_number": "OND-8820",
            "manufacturer": "GlaxoSmithKline (GSK)",
            "quantity": 8,  # Below min 40
            "min_stock_level": 40,
            "unit_price": 5.20,
            "mfg_date": (today - timedelta(days=150)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=320)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
        # 20. Calcium + Vitamin D3 Tablets - Good stock
        {
            "batch_id": "BAT-1020",
            "medicine_name": "Calcium + Vitamin D3 Tablets",
            "category": "Vitamins & Supplements",
            "batch_number": "CAL-9912",
            "manufacturer": "Pfizer Limited",
            "quantity": 230,
            "min_stock_level": 80,
            "unit_price": 6.50,
            "mfg_date": (today - timedelta(days=110)).strftime("%Y-%m-%d"),
            "expiry_date": (today + timedelta(days=440)).strftime("%Y-%m-%d"),
            "created_at": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
        },
    ]
    return batches


def generate_sample_consumption(base_date: date = None) -> List[Dict]:
    """
    Generates 48 realistic dispensing / consumption records
    spread over the last 55 days.
    """
    today = base_date or date.today()

    records = [
        # Days 50 to 41 ago
        {"record_id": "CON-1001", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 52, "qty": 18, "notes": "OPD Fever Clinic"},
        {"record_id": "CON-1002", "medicine_name": "Amoxicillin 500mg", "batch_id": "BAT-1003", "days_ago": 50, "qty": 12, "notes": "Dental OPD"},
        {"record_id": "CON-1003", "medicine_name": "Metformin 500mg", "batch_id": "BAT-1005", "days_ago": 48, "qty": 30, "notes": "Diabetic Clinic Monthly Refills"},
        {"record_id": "CON-1004", "medicine_name": "Pantoprazole 40mg", "batch_id": "BAT-1007", "days_ago": 47, "qty": 15, "notes": "Gastroenterology OPD"},
        {"record_id": "CON-1005", "medicine_name": "Cetirizine 10mg", "batch_id": "BAT-1009", "days_ago": 45, "qty": 20, "notes": "Allergy Consultations"},
        {"record_id": "CON-1006", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 44, "qty": 25, "notes": "Emergency Triage Dispensing"},
        {"record_id": "CON-1007", "medicine_name": "Oral Rehydration Salts (ORS)", "batch_id": "BAT-1018", "days_ago": 43, "qty": 10, "notes": "Pediatric Dehydration Cases"},
        {"record_id": "CON-1008", "medicine_name": "Atorvastatin 20mg", "batch_id": "BAT-1011", "days_ago": 41, "qty": 15, "notes": "Cardiology Routine Refills"},

        # Days 40 to 31 ago
        {"record_id": "CON-1009", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 39, "qty": 22, "notes": "General Medicine OPD"},
        {"record_id": "CON-1010", "medicine_name": "Amoxicillin 500mg", "batch_id": "BAT-1003", "days_ago": 38, "qty": 15, "notes": "ENT Clinic Prescriptions"},
        {"record_id": "CON-1011", "medicine_name": "Metformin 500mg", "batch_id": "BAT-1005", "days_ago": 37, "qty": 35, "notes": "Endocrinology Follow-ups"},
        {"record_id": "CON-1012", "medicine_name": "Amlodipine 5mg", "batch_id": "BAT-1006", "days_ago": 36, "qty": 20, "notes": "Hypertension Management"},
        {"record_id": "CON-1013", "medicine_name": "Vitamin C 500mg Chewable", "batch_id": "BAT-1014", "days_ago": 35, "qty": 40, "notes": "Preventive Care Wellness Camp"},
        {"record_id": "CON-1014", "medicine_name": "Ibuprofen 400mg", "batch_id": "BAT-1012", "days_ago": 34, "qty": 18, "notes": "Orthopedic OPD Joint Pain"},
        {"record_id": "CON-1015", "medicine_name": "Salbutamol Inhaler 100mcg", "batch_id": "BAT-1016", "days_ago": 32, "qty": 4, "notes": "Pulmonology Asthma Clinic"},
        {"record_id": "CON-1016", "medicine_name": "Pantoprazole 40mg", "batch_id": "BAT-1007", "days_ago": 31, "qty": 22, "notes": "Inpatient Ward Supply"},

        # Days 30 to 21 ago
        {"record_id": "CON-1017", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 29, "qty": 30, "notes": "OPD Fever Season Peak"},
        {"record_id": "CON-1018", "medicine_name": "Montelukast 10mg", "batch_id": "BAT-1008", "days_ago": 28, "qty": 14, "notes": "Pediatric Asthma & Allergies"},
        {"record_id": "CON-1019", "medicine_name": "Metformin 500mg", "batch_id": "BAT-1005", "days_ago": 27, "qty": 40, "notes": "Community Diabetic Camp"},
        {"record_id": "CON-1020", "medicine_name": "Oral Rehydration Salts (ORS)", "batch_id": "BAT-1018", "days_ago": 26, "qty": 25, "notes": "Acute Diarrhea Inpatients"},
        {"record_id": "CON-1021", "medicine_name": "Ciprofloxacin 500mg", "batch_id": "BAT-1013", "days_ago": 25, "qty": 16, "notes": "UTI Clinic Dispensing"},
        {"record_id": "CON-1022", "medicine_name": "Calcium + Vitamin D3 Tablets", "batch_id": "BAT-1020", "days_ago": 24, "qty": 20, "notes": "Geriatric Care Clinic"},
        {"record_id": "CON-1023", "medicine_name": "Ondansetron 4mg", "batch_id": "BAT-1019", "days_ago": 23, "qty": 12, "notes": "Post-Op Nausea Protocol"},
        {"record_id": "CON-1024", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 21, "qty": 28, "notes": "Emergency Room Supply"},

        # Days 20 to 11 ago
        {"record_id": "CON-1025", "medicine_name": "Amoxicillin 500mg", "batch_id": "BAT-1003", "days_ago": 20, "qty": 18, "notes": "Bacterial Respiratory Infection"},
        {"record_id": "CON-1026", "medicine_name": "Atorvastatin 20mg", "batch_id": "BAT-1011", "days_ago": 19, "qty": 25, "notes": "Cardiology Long-term Dispensary"},
        {"record_id": "CON-1027", "medicine_name": "Cetirizine 10mg", "batch_id": "BAT-1009", "days_ago": 18, "qty": 30, "notes": "Seasonal Rhinitis Clinic"},
        {"record_id": "CON-1028", "medicine_name": "Pantoprazole 40mg", "batch_id": "BAT-1007", "days_ago": 17, "qty": 28, "notes": "General Ward Stock"},
        {"record_id": "CON-1029", "medicine_name": "Metformin 500mg", "batch_id": "BAT-1005", "days_ago": 16, "qty": 45, "notes": "Endocrine Clinic Dispensing"},
        {"record_id": "CON-1030", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 15, "qty": 32, "notes": "Viral Outbreak Screening"},
        {"record_id": "CON-1031", "medicine_name": "Glimepiride 2mg", "batch_id": "BAT-1017", "days_ago": 14, "qty": 18, "notes": "Diabetic Glycemic Control"},
        {"record_id": "CON-1032", "medicine_name": "Vitamin C 500mg Chewable", "batch_id": "BAT-1014", "days_ago": 13, "qty": 50, "notes": "Wellness Immunity Drive"},
        {"record_id": "CON-1033", "medicine_name": "Ibuprofen 400mg", "batch_id": "BAT-1012", "days_ago": 12, "qty": 22, "notes": "Sports Injury Day Clinic"},
        {"record_id": "CON-1034", "medicine_name": "Amlodipine 5mg", "batch_id": "BAT-1006", "days_ago": 11, "qty": 24, "notes": "Cardiac Care OPD"},

        # Days 10 to 1 ago (Recent 10 days)
        {"record_id": "CON-1035", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 9, "qty": 35, "notes": "OPD Primary Care"},
        {"record_id": "CON-1036", "medicine_name": "Amoxicillin 500mg", "batch_id": "BAT-1003", "days_ago": 8, "qty": 14, "notes": "Pediatric Clinic"},
        {"record_id": "CON-1037", "medicine_name": "Omeprazole 20mg", "batch_id": "BAT-1015", "days_ago": 7, "qty": 15, "notes": "Gastroenterology Consultation"},
        {"record_id": "CON-1038", "medicine_name": "Oral Rehydration Salts (ORS)", "batch_id": "BAT-1018", "days_ago": 6, "qty": 30, "notes": "Gastroenteritis Emergency Care"},
        {"record_id": "CON-1039", "medicine_name": "Metformin 500mg", "batch_id": "BAT-1005", "days_ago": 5, "qty": 50, "notes": "Monthly Diabetes Prescription Refills"},
        {"record_id": "CON-1040", "medicine_name": "Pantoprazole 40mg", "batch_id": "BAT-1007", "days_ago": 5, "qty": 30, "notes": "Surgical Pre-op Prophylaxis"},
        {"record_id": "CON-1041", "medicine_name": "Montelukast 10mg", "batch_id": "BAT-1008", "days_ago": 4, "qty": 16, "notes": "Respiratory Care Center"},
        {"record_id": "CON-1042", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 3, "qty": 40, "notes": "Emergency Department Walk-ins"},
        {"record_id": "CON-1043", "medicine_name": "Calcium + Vitamin D3 Tablets", "batch_id": "BAT-1020", "days_ago": 3, "qty": 25, "notes": "Antenatal & Postnatal OPD"},
        {"record_id": "CON-1044", "medicine_name": "Salbutamol Inhaler 100mcg", "batch_id": "BAT-1016", "days_ago": 2, "qty": 6, "notes": "Emergency Bronchospasm Relief"},
        {"record_id": "CON-1045", "medicine_name": "Atorvastatin 20mg", "batch_id": "BAT-1011", "days_ago": 2, "qty": 30, "notes": "Cardiac Wellness Registry"},
        {"record_id": "CON-1046", "medicine_name": "Ondansetron 4mg", "batch_id": "BAT-1019", "days_ago": 1, "qty": 10, "notes": "Daycare Chemotherapy Antiemetic"},
        {"record_id": "CON-1047", "medicine_name": "Cetirizine 10mg", "batch_id": "BAT-1009", "days_ago": 1, "qty": 25, "notes": "OPD Allergy Clinic"},
        {"record_id": "CON-1048", "medicine_name": "Paracetamol 500mg", "batch_id": "BAT-1001", "days_ago": 0, "qty": 25, "notes": "Today OPD Fever Triage"},
    ]

    formatted_records = []
    for r in records:
        cons_date = today - timedelta(days=r["days_ago"])
        formatted_records.append({
            "record_id": r["record_id"],
            "medicine_name": r["medicine_name"],
            "batch_id": r["batch_id"],
            "consumption_date": cons_date.strftime("%Y-%m-%d"),
            "quantity_consumed": r["qty"],
            "notes": r["notes"],
            "created_at": cons_date.strftime("%Y-%m-%d"),
        })

    return formatted_records


def seed_sample_data(data_manager) -> Tuple[int, int]:
    """
    Populates data files with demonstration dataset.
    Returns (num_batches, num_consumption_records).
    """
    batches = generate_sample_batches()
    consumption = generate_sample_consumption()

    data_manager.save_inventory_records(batches)
    data_manager.save_consumption_records(consumption)

    return len(batches), len(consumption)
