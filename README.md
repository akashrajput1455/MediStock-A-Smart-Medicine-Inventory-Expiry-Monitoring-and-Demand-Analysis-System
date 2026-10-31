# MediStock: Smart Medicine Inventory, Expiry Monitoring and Demand Analysis System

**An Academic Mini Project for Master of Computer Applications (MCA) – Specialization in Artificial Intelligence & Machine Learning**

---

## 1. Project Title
**MediStock**: A Smart Medicine Inventory, Expiry Monitoring and Demand Analysis System for Hospital Pharmacies and Medical Stores.

---

## 2. Introduction
In community healthcare centers, small hospital dispensaries, and retail pharmacies, effective drug inventory management is essential for patient health, legal compliance, and economic sustainability. Inefficient management frequently causes critical drug stockouts or unnecessary financial losses from expired medications.

**MediStock** is a Python-based web application designed to track pharmaceutical batches, automate expiry date surveillance, enforce **First Expiring, First Out (FEFO)** dispensing, and project future stock requirements using transparent statistical demand modeling.

---

## 3. Problem Statement
Manual record-keeping in small pharmacies encounters three critical challenges:
1. **Unnoticed Drug Expiration**: Without proactive expiry detection, expired medicines may sit on shelves or inadvertently be dispensed to patients.
2. **Improper Batch Rotation**: Dispensing newer consignments while older batches remain on the shelf causes preventable product spoilage.
3. **Unplanned Stockouts & Overstocking**: Inaccurate estimation of reorder levels leads to either sudden drug shortages during health emergencies or excess inventory tied up on shelves.

---

## 4. Project Objectives
- Maintain complete, structured batch records for medicines.
- Dynamically detect expired medicines and quarantine them from available stock.
- Identify medicines approaching their expiry dates within customizable threshold windows (e.g., 7 days, 30 days).
- Detect low-stock items based on configurable safety levels.
- Track historical dispensing transactions without allowing negative inventory.
- Implement **FEFO (First Expiring, First Out)** dispensing to prioritize earliest expiring batches.
- Calculate Average Daily Consumption (ADC) and project required stock for planned coverage horizons.
- Provide interactive visual dashboards and clean tabular summaries with CSV export capabilities.

---

## 5. Scope of the Application
### Within Scope:
- Single-store / small clinic pharmacy inventory tracking.
- Batch-level tracking (lot number, manufacturing date, expiry date, unit price).
- Automated expiry classification relative to the current calendar date (`date.today()`).
- Statistical demand calculations using NumPy and Pandas.
- Visual charts using Matplotlib.
- Reliable local data persistence using structured CSV files with atomic writes.
- Deterministic sample dataset for academic demonstrations and vivas.

### Out of Scope (Future Work):
- Multi-branch distributed networking and multi-tenant authentication.
- Direct Electronic Health Record (EHR) or clinical diagnosis support.
- Automated creation of purchase vendor orders or financial billing.
- Cloud SQL or blockchain ledger persistence.

---

## 6. Technologies Used
| Component | Technology | Version / Specification |
| :--- | :--- | :--- |
| **Language** | Python | 3.10+ / 3.11 |
| **Web Framework** | Streamlit | Clean, reactive UI |
| **Data Analytics** | Pandas | DataFrames, rolling windows, aggregations |
| **Numerical Calculations** | NumPy | Precision floating point & array metrics |
| **Data Visualization** | Matplotlib | Bar charts, line trends, status donut plots |
| **Data Storage** | CSV Files | Python's standard `csv` module with atomic file swapping |
| **Date & Time** | `datetime` standard library | Relative calendar comparisons |
| **Testing** | `unittest` standard library | 14 automated unit tests |

---

## 7. Key Features
1. **Executive Dashboard**:
   - 5 KPI summary cards: Total Batches, Available Units, Low-Stock Medicines, Expired Batches, Expiring Soon.
   - Actionable banners highlighting urgent safety actions.
   - Dynamic charts: Top 5 Consumed Medicines, Monthly Dispensing Trends, Inventory Status Breakdown.
   - High-priority attention table for rapid review.

2. **Medicine Inventory Management**:
   - Add, view, search, filter, edit, and delete individual medicine batches.
   - Real-time search across Medicine Name, Batch Number, Batch ID, and Manufacturer.
   - Multi-parameter filtering by Category, Expiry Status, and Stock Level.
   - CSV export for reporting.

3. **Automated Expiry Surveillance**:
   - Dynamic evaluation against system clock (`date.today()`).
   - Categorization:
     - **Expired**: Expiry date strictly before today (quarantined from available stock).
     - **Expiring Soon**: Expiry date within next 30 days (configurable slider from 7 to 90 days).
     - **Valid**: Long shelf life remaining.
   - Segregated tabs for urgent review.

4. **FEFO Dispensing & Consumption Audit**:
   - Enforces **First Expiring, First Out (FEFO)**: earliest expiring batch is always consumed first.
   - Prevents negative inventory: rejects requests exceeding total non-expired stock.
   - Audit trail of all dispensing events with clinical notes.

5. **Demand Analysis & Reorder Forecasting**:
   - Calculates Average Daily Consumption (ADC).
   - Projects days of stock coverage remaining.
   - Calculates suggested reorder quantities for planned coverage horizons (e.g., 30 days).

6. **Demonstration & Data Tools**:
   - Pre-loaded with 20 realistic pharmaceutical batches and 48 consumption transactions.
   - One-click restore button to reset demonstration data anytime during an academic presentation.

---

## 8. System Architecture
MediStock follows a clean, modular 3-tier architecture:

```
┌────────────────────────────────────────────────────────┐
│             Presentation Layer (Streamlit)             │
│   (Dashboard, Inventory, Expiry, Dispensing, Demand)   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  Business Logic Layer                  │
│  ├── InventoryManager (Validation, Search, FEFO logic) │
│  ├── DemandAnalyzer (Pandas/NumPy ADC & forecasting)   │
│  └── Domain Models (BaseEntity, MedicineBatch, etc.)   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                    Persistence Layer                   │
│      DataManager (Atomic CSV reads, writes, backups)   │
│     ├── data/medicine_inventory.csv                    │
│     └── data/consumption_records.csv                   │
└────────────────────────────────────────────────────────┘
```

---

## 9. Explanation of Main Classes (OOP Syllabus Concepts)

### `BaseEntity` (Abstract Base Class)
- Located in `modules/models.py`.
- Demonstrates abstract methods (`validate()`, `to_dict()`) and common attributes (`entity_id`, `created_at`).

### `MedicineBatch` (Inherits from `BaseEntity`)
- Represents an individual pharmaceutical consignment.
- **Attributes**: `batch_id`, `medicine_name`, `category`, `batch_number`, `manufacturer`, `quantity`, `min_stock_level`, `unit_price`, `mfg_date`, `expiry_date`.
- **Key Methods**:
  - `is_expired(ref_date)`: Boolean test (`expiry_date < ref_date`).
  - `is_expiring_soon(threshold, ref_date)`: Boolean test (`0 <= days <= threshold`).
  - `days_until_expiry(ref_date)`: Returns signed integer days remaining.
  - `validate()`: Enforces non-negative values and checks that `mfg_date <= expiry_date`.

### `ConsumptionRecord` (Inherits from `BaseEntity`)
- Represents an audit entry for a dispensing event.
- **Attributes**: `record_id`, `medicine_name`, `batch_id`, `consumption_date`, `quantity_consumed`, `notes`.
- **Validation**: Ensures `quantity_consumed > 0`.

### `InventoryManager`
- Handles inventory operations, search queries, multi-criteria filtering, and stock persistence.
- Implements `deduct_stock_fefo()`: sorts candidate batches by expiration date and allocates deductions across batches.

### `DemandAnalyzer`
- Bridges inventory batches with historical consumption transactions.
- Uses Pandas DataFrames for grouping and filtering.
- Implements visualization generators returning Matplotlib figure objects.

### `DataManager`
- Provides thread-safe, atomic file I/O using temporary files (`.tmp`) and atomic replacement (`Path.replace()`) to prevent file corruption.

---

## 10. Explanation of Inventory Calculations

### 1. Available Stock Calculation
$$\text{Available Stock} = \sum_{\text{batch} \in \text{Non-Expired Batches}} \text{batch.quantity}$$
*Expired batches are explicitly excluded ($\text{quantity} = 0$ for routine dispensing).*

### 2. Expiry Days Calculation
$$\text{Days Remaining} = \text{expiry\_date} - \text{today}$$
- If $\text{Days Remaining} < 0$: Status is **Expired**.
- If $0 \le \text{Days Remaining} \le \text{Threshold}$ (default 30): Status is **Expiring Soon**.
- If $\text{Days Remaining} > \text{Threshold}$: Status is **Valid**.

### 3. Low-Stock Condition
A medicine is flagged as **Low Stock** when:
$$\text{Available Stock} < \text{Minimum Stock Level}$$
$$\text{Shortage} = \max(0, \, \text{Minimum Stock Level} - \text{Available Stock})$$

---

## 11. Explanation of the Demand-Estimation Algorithm
Rather than an unexplainable machine learning black box, MediStock employs an explainable, deterministic statistical algorithm:

1. **Analysis Window Selection**:
   Select historical window of $D_{\text{hist}}$ days (default: 30 days).

2. **Total Quantity Consumed**:
   $$Q_{\text{consumed}} = \sum_{t = \text{today} - D_{\text{hist}}}^{\text{today}} \text{quantity\_consumed}_t$$

3. **Average Daily Consumption (ADC)**:
   $$\text{ADC} = \frac{Q_{\text{consumed}}}{D_{\text{hist}}}$$

4. **Estimated Monthly Demand**:
   $$\text{Monthly Demand} = \text{ADC} \times 30$$

5. **Stock Coverage (Estimated Days Remaining)**:
   $$\text{Coverage Days} = \begin{cases} 
   \frac{\text{Available Stock}}{\text{ADC}} & \text{if } \text{ADC} > 0 \\
   999 \text{ (Adequate)} & \text{if } \text{ADC} = 0 \text{ and } \text{Available Stock} > 0 \\
   0 & \text{if } \text{ADC} = 0 \text{ and } \text{Available Stock} = 0
   \end{cases}$$

6. **Suggested Reorder Quantity**:
   Given a target coverage buffer of $D_{\text{cov}}$ days (default: 30 days):
   $$\text{Required Stock} = \lceil \text{ADC} \times D_{\text{cov}} \rceil$$
   $$\text{Suggested Reorder} = \max\left(0, \, \text{Required Stock} - \text{Available Stock}\right)$$

---

## 12. Project Folder Structure
```
MediStock/
│
├── app.py                      # Main Streamlit web application entry point
├── requirements.txt            # Python package dependencies
├── README.md                   # Complete academic documentation & viva guide
│
├── modules/
│   ├── __init__.py             # Package initializer
│   ├── models.py               # Domain classes (BaseEntity, MedicineBatch, ConsumptionRecord)
│   ├── inventory_manager.py    # Inventory operations, validation, FEFO dispensing
│   └── demand_analyzer.py      # Pandas & NumPy demand calculations & Matplotlib charts
│
├── utils/
│   ├── __init__.py             # Package initializer
│   ├── data_manager.py         # Atomic CSV storage & export handlers
│   └── sample_data.py          # Deterministic demonstration dataset generator
│
├── data/
│   ├── medicine_inventory.csv  # Persistent batch inventory records
│   └── consumption_records.csv # Persistent dispensing audit records
│
└── tests/
    ├── __init__.py             # Package initializer
    └── test_medi_stock.py      # Automated unittest suite (14 test cases)
```

---

## 13. Installation Instructions

### Prerequisites
- Python 3.10 or 3.11 installed on your computer.
- Ensure `pip` is available.

### Setup Steps
1. Open your terminal or Command Prompt (cmd/PowerShell).
2. Clone or extract the project directory:
   ```bash
   cd MediStock
   ```
3. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 14. Instructions to Run the Application
To start the Streamlit web dashboard:
```bash
streamlit run app.py
```
Streamlit will automatically launch your default browser and navigate to:
```
http://localhost:8501
```

---

## 15. Instructions to Run the Tests
Run the unit test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover tests -v
```
All 14 tests will run in temporary directories without modifying your live database:
```
test_01_add_valid_batch ... ok
test_02_reject_duplicate_batch_id ... ok
test_03_reject_negative_quantity ... ok
test_04_reject_invalid_date_order ... ok
test_05_detect_expired_batch ... ok
test_06_detect_expiring_soon_batch ... ok
test_07_detect_low_stock ... ok
test_08_exclude_expired_from_available_stock ... ok
test_09_calculate_average_daily_consumption ... ok
test_10_calculate_stock_coverage_and_reorder ... ok
test_11_handle_empty_consumption ... ok
test_12_prevent_negative_stock ... ok
test_13_fefo_dispensing_order ... ok
test_14_preserve_records_on_invalid_input ... ok

Ran 14 tests in 0.05s
OK
```

---

## 16. Sample Data Information
MediStock includes a deterministic demonstration dataset:
- **20 Batches**: Representing antibiotics, analgesics, antidiabetics, cardiovascular, respiratory, and emergency fluids.
- Includes expired batches (for safety quarantine testing), batches expiring within 7 days and 30 days, low-stock batches, and multi-batch drugs (e.g., Paracetamol).
- **48 Consumption Records**: Spread across the preceding 55 days to enable trend lines and monthly grouping.
- Can be restored at any time via the **Data Management** tab.

---

## 17. Limitations
- Single-store focus; does not support concurrent multi-user distributed locking.
- CSV storage is optimal for demonstration but not suitable for high-frequency concurrent hospital enterprise workloads.
- Assumes historical consumption is a reasonable indicator of near-term demand (does not account for seasonal epidemics or sudden pandemics without manual window adjustments).

---

## 18. Future Integrations (Academic Roadmap)
MediStock is architected for seamless integration with complementary MCA projects:

1. **MedChain (Medical Supply Monitoring & Multi-Tier Database)**:
   - Replace the CSV layer with a secure relational database (PostgreSQL/MySQL) or distributed ledger.
   - The modular `DataManager` allows replacing file read/write methods with SQL queries or ORM calls without modifying the UI or business logic.

2. **MedRoute (Medical Delivery Route Optimization)**:
   - MediStock's `DemandAnalyzer` calculates `Suggested Reorder` quantities for each dispensary.
   - These reorder requirements can be sent as demand nodes to MedRoute's Dijkstra or Vehicle Routing Problem (VRP) algorithms to calculate optimal restocking delivery routes.

---

## 19. Author & Academic Viva Notes
- **Program**: Master of Computer Applications (MCA)
- **Specialization**: Artificial Intelligence & Machine Learning
- **Project Type**: Python & Data Analytics Mini Project
- **License**: Educational / Academic Project Use
