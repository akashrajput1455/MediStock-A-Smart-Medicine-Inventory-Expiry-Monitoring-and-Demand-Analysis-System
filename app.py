"""
MediStock: Smart Medicine Inventory, Expiry Monitoring and Demand Analysis System
A Python Web Application for MCA Mini Project (AI & Machine Learning Specialization).

Built with:
- Streamlit (Web Interface)
- Pandas & NumPy (Data Processing & Demand Analysis)
- Matplotlib (Healthcare Analytics Visualizations)
- CSV Persistence (Structured File Storage)
- Python OOP (Modular domain models and business logic)
"""

import math
from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from modules.demand_analyzer import DemandAnalyzer
from modules.inventory_manager import InventoryManager
from modules.models import MedicineBatch
from utils.data_manager import DataManager
from utils.sample_data import generate_sample_batches, generate_sample_consumption, seed_sample_data

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MediStock - Medicine Inventory & Expiry Monitoring",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Healthcare Clean Aesthetic
st.markdown(
    """
    <style>
    /* Global Typography & Palette */
    .main-title {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #475569;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.2rem 0;
    }
    .badge-in-stock {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-low-stock {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-expiring {
        background-color: #ffedd5;
        color: #9a3412;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-expired {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .callout-box {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .callout-warn {
        background-color: #fefce8;
        border-left: 4px solid #eab308;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .callout-danger {
        background-color: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    /* Streamlit widget fine-tuning */
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Dependency Initialization
# -----------------------------------------------------------------------------
@st.cache_resource
def get_services():
    """Initializes and returns shared DataManager, InventoryManager, and DemandAnalyzer."""
    dm = DataManager()
    # Check if storage is empty, initialize with demonstration data if needed
    if not dm.inventory_path.exists() or len(dm.load_inventory_records()) == 0:
        seed_sample_data(dm)
    im = InventoryManager(dm)
    da = DemandAnalyzer(im, dm)
    return dm, im, da


data_mgr, inv_mgr, demand_an = get_services()
# Keep inventory state synced with latest CSV data on each page run
inv_mgr.refresh_from_storage()


# -----------------------------------------------------------------------------
# Sidebar Navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <span style="font-size:2rem;">💊</span>
            <div>
                <h3 style="margin:0; color:#0284c7; font-size:1.3rem;">MediStock</h3>
                <p style="margin:0; font-size:0.75rem; color:#64748b;">Pharmacy Inventory & Demand System</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "📦 Medicine Inventory",
            "➕ Add Medicine",
            "⏳ Expiry Monitoring",
            "📉 Dispensing & Consumption",
            "📈 Demand Analysis",
            "ℹ️ About Project & Viva",
            "⚙️ Data Management",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:0.8rem; color:#64748b; line-height:1.4;">
            <strong>System Status</strong><br>
            • System Date: <code>{date.today().strftime('%d %b %Y')}</code><br>
            • Storage: Local CSV Storage<br>
            • MCA Mini Project Demo
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# 1. DASHBOARD PAGE
# =============================================================================
if page == "📊 Dashboard":
    st.markdown('<div class="main-title">Pharmacy Inventory Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Real-time overview of current medicine stock, impending expirations, and dispensing activities.</div>',
        unsafe_allow_html=True,
    )

    batches = inv_mgr.get_all_batches()
    expired_batches = inv_mgr.get_expired_batches()
    expiring_soon = inv_mgr.get_expiring_soon_batches(30)
    low_stock_items = inv_mgr.get_low_stock_summary()
    total_safe_units = inv_mgr.get_total_available_units()

    # KPI Summary Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Total Batches", value=len(batches))
    with col2:
        st.metric(label="Available Units", value=f"{total_safe_units:,}")
    with col3:
        st.metric(
            label="Low-Stock Medicines",
            value=len(low_stock_items),
            delta="-Action Needed" if low_stock_items else "Stock Healthy",
            delta_color="inverse" if low_stock_items else "normal",
        )
    with col4:
        st.metric(
            label="Expiring Soon (<30d)",
            value=len(expiring_soon),
            delta="-Review" if expiring_soon else "Safe",
            delta_color="inverse" if expiring_soon else "normal",
        )
    with col5:
        st.metric(
            label="Expired Batches",
            value=len(expired_batches),
            delta="-Quarantine" if expired_batches else "None",
            delta_color="inverse" if expired_batches else "normal",
        )

    # Actionable Alert Banners
    if expired_batches:
        st.markdown(
            f"""
            <div class="callout-danger">
                <strong>⚠️ Safety Alert:</strong> {len(expired_batches)} batch(es) have passed their expiry date!
                These have been automatically quarantined and are excluded from available dispensing stock.
                Navigate to <strong>Expiry Monitoring</strong> to review or mark for disposal.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif low_stock_items:
        st.markdown(
            f"""
            <div class="callout-warn">
                <strong>📦 Reorder Notice:</strong> {len(low_stock_items)} medicine(s) have fallen below their minimum stock threshold.
                Review the <strong>Demand Analysis</strong> tab for estimated reorder quantities.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Visual Analytics Section
    st.markdown("### Inventory & Consumption Visualizations")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_top = demand_an.plot_top_consumed_medicines(top_n=5, days=30)
        if fig_top:
            st.pyplot(fig_top, use_container_width=True)
            plt.close(fig_top)
        else:
            st.info("ℹ️ No historical consumption data recorded in the last 30 days to generate top consumed chart.")

    with chart_col2:
        fig_trend = demand_an.plot_monthly_consumption_trend()
        if fig_trend:
            st.pyplot(fig_trend, use_container_width=True)
            plt.close(fig_trend)
        else:
            st.info("ℹ️ Monthly consumption trend will appear as more dispensing records are logged.")

    # Lower Grid: Status Breakdown & Immediate Attention List
    st.markdown("---")
    bot_col1, bot_col2 = st.columns([1, 1.4])

    with bot_col1:
        st.markdown("#### Inventory Status Distribution")
        fig_dist = demand_an.plot_inventory_status_distribution()
        if fig_dist:
            st.pyplot(fig_dist, use_container_width=True)
            plt.close(fig_dist)
        else:
            st.info("No batches present to chart status distribution.")

    with bot_col2:
        st.markdown("#### Medicines Requiring Immediate Attention")
        attention_rows = []

        # Collect expired
        for b in expired_batches[:4]:
            attention_rows.append({
                "Medicine Name": b.medicine_name,
                "Batch ID": b.batch_id,
                "Current Qty": b.quantity,
                "Expiry Date": b.expiry_date.strftime("%Y-%m-%d"),
                "Attention Reason": f"🔴 Expired ({abs(b.days_until_expiry())}d ago)",
            })

        # Collect expiring soon
        for b in expiring_soon[:4]:
            attention_rows.append({
                "Medicine Name": b.medicine_name,
                "Batch ID": b.batch_id,
                "Current Qty": b.quantity,
                "Expiry Date": b.expiry_date.strftime("%Y-%m-%d"),
                "Attention Reason": f"🟠 Expiring in {b.days_until_expiry()}d",
            })

        # Collect low stock
        for ls in low_stock_items[:4]:
            attention_rows.append({
                "Medicine Name": ls["medicine_name"],
                "Batch ID": "-",
                "Current Qty": ls["available_stock"],
                "Expiry Date": "-",
                "Attention Reason": f"🟡 Low Stock (Shortage: {ls['shortage']} units)",
            })

        if attention_rows:
            att_df = pd.DataFrame(attention_rows)
            st.dataframe(att_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ All medicine stocks and batches are currently within safe limits!")


# =============================================================================
# 2. MEDICINE INVENTORY PAGE
# =============================================================================
elif page == "📦 Medicine Inventory":
    st.markdown('<div class="main-title">Medicine Batch Inventory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">View, search, filter, edit, and audit individual pharmaceutical batches.</div>',
        unsafe_allow_html=True,
    )

    all_batches = inv_mgr.get_all_batches()

    if not all_batches:
        st.info("No medicine batches found in inventory. Use the **Add Medicine** page or load sample data.")
    else:
        # Search & Filtering Controls
        fcol1, fcol2, fcol3, fcol4 = st.columns([2, 1.2, 1.2, 1.2])
        with fcol1:
            search_query = st.text_input("🔍 Search Batch", placeholder="Search by name, batch number, ID, manufacturer...")
        with fcol2:
            categories = ["All"] + inv_mgr.get_categories()
            selected_cat = st.selectbox("Category Filter", categories)
        with fcol3:
            expiry_options = ["All", "Expired", "Expiring Soon (<7 Days)", "Expiring Soon (<30 Days)", "Valid"]
            selected_expiry = st.selectbox("Expiry Filter", expiry_options)
        with fcol4:
            stock_options = ["All", "In Stock", "Low Stock", "Out of Stock"]
            selected_stock = st.selectbox("Stock Filter", stock_options)

        # Apply filtering
        filtered_batches = inv_mgr.search_and_filter(
            query=search_query,
            category=selected_cat,
            expiry_filter=selected_expiry,
            stock_filter=selected_stock,
        )

        st.caption(f"Showing **{len(filtered_batches)}** of **{len(all_batches)}** batches.")

        # Display Table
        if filtered_batches:
            table_data = []
            for b in filtered_batches:
                exp_stat = b.expiry_status(30)
                stk_stat = b.stock_status()

                table_data.append({
                    "Batch ID": b.batch_id,
                    "Medicine Name": b.medicine_name,
                    "Category": b.category,
                    "Batch No": b.batch_number,
                    "Manufacturer": b.manufacturer,
                    "Quantity": b.quantity,
                    "Min Stock": b.min_stock_level,
                    "Unit Price (₹)": f"₹{b.unit_price:.2f}",
                    "Mfg Date": b.mfg_date.strftime("%Y-%m-%d"),
                    "Expiry Date": b.expiry_date.strftime("%Y-%m-%d"),
                    "Days Left": b.days_until_expiry(),
                    "Status": f"🔴 {exp_stat}" if exp_stat == "Expired" else (f"🟠 {exp_stat}" if exp_stat == "Expiring Soon" else (f"🟡 {stk_stat}" if "Low" in stk_stat else "🟢 Safe")),
                })

            df_display = pd.DataFrame(table_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Export to CSV Button
            csv_str = data_mgr.get_inventory_csv_string()
            st.download_button(
                label="📥 Export Inventory as CSV",
                data=csv_str,
                file_name=f"medistock_inventory_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.warning("No batches matched the chosen filter criteria.")

        st.markdown("---")

        # Edit / Delete Section
        st.markdown("### Manage Existing Batch (Edit / Delete)")
        selected_batch_id = st.selectbox(
            "Select a Batch to Modify or Remove",
            options=["-- Select Batch --"] + [f"{b.batch_id} - {b.medicine_name} ({b.batch_number})" for b in all_batches],
        )

        if selected_batch_id != "-- Select Batch --":
            actual_id = selected_batch_id.split(" - ")[0]
            batch_to_edit = inv_mgr.get_batch(actual_id)

            if batch_to_edit:
                tab_edit, tab_delete = st.tabs(["✏️ Edit Batch Details", "🗑️ Delete Batch"])

                with tab_edit:
                    with st.form(f"edit_form_{actual_id}"):
                        e_col1, e_col2 = st.columns(2)
                        with e_col1:
                            e_name = st.text_input("Medicine Name", value=batch_to_edit.medicine_name)
                            e_cat = st.text_input("Category", value=batch_to_edit.category)
                            e_batch_no = st.text_input("Batch Number", value=batch_to_edit.batch_number)
                            e_mfg = st.date_input("Manufacturing Date", value=batch_to_edit.mfg_date)
                            e_qty = st.number_input("Quantity", min_value=0, value=batch_to_edit.quantity, step=1)
                        with e_col2:
                            e_mfr = st.text_input("Manufacturer", value=batch_to_edit.manufacturer)
                            e_price = st.number_input("Unit Price", min_value=0.0, value=batch_to_edit.unit_price, step=0.5, format="%.2f")
                            e_min = st.number_input("Minimum Stock Level", min_value=0, value=batch_to_edit.min_stock_level, step=5)
                            e_exp = st.date_input("Expiry Date", value=batch_to_edit.expiry_date)

                        submit_edit = st.form_submit_button("💾 Save Changes", type="primary")
                        if submit_edit:
                            try:
                                updated_batch = MedicineBatch(
                                    batch_id=actual_id,
                                    medicine_name=e_name,
                                    category=e_cat,
                                    batch_number=e_batch_no,
                                    manufacturer=e_mfr,
                                    quantity=e_qty,
                                    min_stock_level=e_min,
                                    unit_price=e_price,
                                    mfg_date=e_mfg,
                                    expiry_date=e_exp,
                                )
                                ok, msg = inv_mgr.update_batch(actual_id, updated_batch)
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            except Exception as ex:
                                st.error(f"Error updating batch: {ex}")

                with tab_delete:
                    st.warning(f"Are you sure you want to delete batch **{actual_id}** ({batch_to_edit.medicine_name})? This action cannot be undone.")
                    confirm_delete = st.checkbox(f"Confirm permanent deletion of {actual_id}")
                    if st.button("🗑️ Delete Batch Permanently", type="secondary", disabled=not confirm_delete):
                        ok, msg = inv_mgr.delete_batch(actual_id)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)


# =============================================================================
# 3. ADD MEDICINE PAGE
# =============================================================================
elif page == "➕ Add Medicine":
    st.markdown('<div class="main-title">Add New Medicine Batch</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Register an incoming medicine consignment with batch verification and expiry checking.</div>',
        unsafe_allow_html=True,
    )

    # Helper for Batch ID generation
    all_batches = inv_mgr.get_all_batches()
    suggested_id = f"BAT-{len(all_batches) + 1001}"

    with st.form("add_medicine_form"):
        col1, col2 = st.columns(2)

        with col1:
            batch_id = st.text_input("Batch ID (Unique Identifier)*", value=suggested_id, help="e.g. BAT-1021")
            medicine_name = st.text_input("Medicine Name*", placeholder="e.g. Amoxicillin 500mg, Paracetamol 650mg")
            category_choice = st.selectbox(
                "Therapeutic Category",
                options=[
                    "Analgesic & Antipyretic",
                    "Antibiotic",
                    "Antihistamine",
                    "Antidiabetic",
                    "Cardiovascular",
                    "Gastrointestinal",
                    "Respiratory",
                    "Vitamins & Supplements",
                    "Emergency & Fluids",
                    "Other",
                ],
            )
            if category_choice == "Other":
                category = st.text_input("Specify Other Category", value="General")
            else:
                category = category_choice

            batch_number = st.text_input("Manufacturer's Batch / Lot Number*", placeholder="e.g. BN-2025-09")
            manufacturer = st.text_input("Manufacturer*", placeholder="e.g. Cipla Ltd, Sun Pharma, Abbott")

        with col2:
            quantity = st.number_input("Consignment Quantity (Units)*", min_value=1, value=100, step=10)
            min_stock = st.number_input("Minimum Stock Alert Level*", min_value=0, value=30, step=5)
            unit_price = st.number_input("Unit Purchase Price (₹)*", min_value=0.0, value=5.50, step=0.5, format="%.2f")

            mfg_date = st.date_input(
                "Manufacturing Date*",
                value=date.today() - timedelta(days=30),
                help="Date when batch was manufactured",
            )
            expiry_date = st.date_input(
                "Expiry Date*",
                value=date.today() + timedelta(days=365),
                help="Expiry date must be after manufacturing date",
            )

        submit_btn = st.form_submit_button("➕ Register Medicine Batch", type="primary")

        if submit_btn:
            # Client-side and domain validation
            if not medicine_name.strip():
                st.error("Validation Error: Medicine Name is required.")
            elif not batch_number.strip():
                st.error("Validation Error: Batch Number is required.")
            elif not manufacturer.strip():
                st.error("Validation Error: Manufacturer is required.")
            elif mfg_date > expiry_date:
                st.error(f"Validation Error: Manufacturing date ({mfg_date}) cannot be later than Expiry date ({expiry_date}).")
            else:
                try:
                    new_batch = MedicineBatch(
                        batch_id=batch_id,
                        medicine_name=medicine_name,
                        category=category,
                        batch_number=batch_number,
                        manufacturer=manufacturer,
                        quantity=quantity,
                        min_stock_level=min_stock,
                        unit_price=unit_price,
                        mfg_date=mfg_date,
                        expiry_date=expiry_date,
                    )
                    success, message = inv_mgr.add_batch(new_batch)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
                except Exception as ex:
                    st.error(f"Validation Error: {ex}")


# =============================================================================
# 4. EXPIRY MONITORING PAGE
# =============================================================================
elif page == "⏳ Expiry Monitoring":
    st.markdown('<div class="main-title">Expiry Date Monitoring & Safety Review</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Automated detection of expired and near-expiry medicine batches based on current calendar date.</div>',
        unsafe_allow_html=True,
    )

    # Configurable threshold
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        threshold = st.slider("Select 'Expiring Soon' Threshold Window (Days)", min_value=7, max_value=90, value=30, step=1)
    with col_t2:
        st.markdown(
            f"""
            <div style="background:#f1f5f9; padding:8px 12px; border-radius:6px; font-size:0.85rem; color:#334155;">
                <strong>Current Reference Date:</strong> <code>{date.today().strftime('%Y-%m-%d')}</code><br>
                Batches expiring on or before <code>{(date.today() + timedelta(days=threshold)).strftime('%Y-%m-%d')}</code> are flagged.
            </div>
            """,
            unsafe_allow_html=True,
        )

    expired_list = inv_mgr.get_expired_batches()
    soon_list = inv_mgr.get_expiring_soon_batches(threshold)
    urgent_7d_list = inv_mgr.get_expiring_soon_batches(7)
    all_batches = inv_mgr.get_all_batches()
    valid_batches = [b for b in all_batches if not b.is_expired() and not b.is_expiring_soon(threshold)]

    tab_exp, tab_soon, tab_urgent, tab_valid, tab_all = st.tabs([
        f"🚨 Expired ({len(expired_list)})",
        f"⚠️ Expiring Soon (<{threshold}d) ({len(soon_list)})",
        f"⚡ Critical (<7d) ({len(urgent_7d_list)})",
        f"✅ Valid Batches ({len(valid_batches)})",
        f"📋 All Batches ({len(all_batches)})",
    ])

    def render_expiry_table(batch_list, is_expired_view=False):
        if not batch_list:
            st.info("No batches found in this category.")
            return

        table_data = []
        for b in batch_list:
            days_left = b.days_until_expiry()
            status_text = f"Overdue by {abs(days_left)} days" if days_left < 0 else f"{days_left} days remaining"

            table_data.append({
                "Batch ID": b.batch_id,
                "Medicine Name": b.medicine_name,
                "Batch No": b.batch_number,
                "Manufacturer": b.manufacturer,
                "Quantity": b.quantity,
                "Expiry Date": b.expiry_date.strftime("%Y-%m-%d"),
                "Days Until Expiry": status_text,
                "Stock Value (₹)": f"₹{(b.quantity * b.unit_price):.2f}",
            })

        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    with tab_exp:
        st.markdown(
            """
            <div class="callout-danger">
                <strong>Safety Policy Notice:</strong> Expired medicines are hazardous and strictly barred from being dispensed.
                They must be moved to designated pharmaceutical quarantine bins and disposed of in accordance with healthcare bio-waste standards.
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_expiry_table(expired_list, is_expired_view=True)

    with tab_soon:
        st.markdown(f"Medicines expiring within the selected window of **{threshold} days**.")
        render_expiry_table(soon_list)

    with tab_urgent:
        st.markdown("Medicines expiring within **7 days** (immediate FEFO priority dispensing needed).")
        render_expiry_table(urgent_7d_list)

    with tab_valid:
        st.markdown("Safely stored medicines with long shelf life remaining.")
        render_expiry_table(valid_batches)

    with tab_all:
        st.markdown("All registered batches sorted by expiry date.")
        sorted_all = sorted(all_batches, key=lambda x: x.expiry_date)
        render_expiry_table(sorted_all)


# =============================================================================
# 5. DISPENSING & CONSUMPTION PAGE
# =============================================================================
elif page == "📉 Dispensing & Consumption":
    st.markdown('<div class="main-title">Medicine Dispensing & Consumption Audit</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Record patient or ward dispensing transactions using First Expiring, First Out (FEFO) batch deduction.</div>',
        unsafe_allow_html=True,
    )

    tab_dispense, tab_history = st.tabs(["💊 Record New Dispensing", "📜 Historical Consumption Records"])

    with tab_dispense:
        st.markdown("### Dispense Medicine (FEFO Rule)")
        st.caption(
            "Under the First Expiring, First Out (FEFO) principle, stock is deducted first from the batch closest to expiration "
            "to minimize pharmacy wastage."
        )

        all_meds = inv_mgr.get_medicine_names()
        stock_map = inv_mgr.get_available_stock_by_medicine()

        if not all_meds:
            st.warning("No medicines available in inventory.")
        else:
            with st.form("dispense_form"):
                d_col1, d_col2 = st.columns(2)

                with d_col1:
                    selected_med = st.selectbox("Select Medicine to Dispense*", options=all_meds)
                    avail_stock = stock_map.get(selected_med, 0)

                    st.markdown(
                        f"""
                        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:10px 14px; margin-top:10px;">
                            <span style="font-size:0.8rem; color:#64748b; font-weight:600;">ACTIVE NON-EXPIRED STOCK</span>
                            <div style="font-size:1.6rem; font-weight:700; color:{'#16a34a' if avail_stock > 20 else ('#d97706' if avail_stock > 0 else '#dc2626')};">
                                {avail_stock} Units
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with d_col2:
                    dispense_qty = st.number_input(
                        "Quantity to Dispense (Units)*",
                        min_value=1,
                        max_value=max(1, avail_stock),
                        value=min(10, max(1, avail_stock)),
                        step=1,
                    )
                    dispense_date = st.date_input("Dispensing Date*", value=date.today())
                    dispense_notes = st.text_input(
                        "Clinical / Department Remarks",
                        placeholder="e.g. OPD Prescription #8942, Emergency Ward 3, Fever Clinic",
                    )

                submit_dispense = st.form_submit_button("✅ Authorize & Deduct Stock", type="primary")

                if submit_dispense:
                    if avail_stock <= 0:
                        st.error(f"Cannot dispense '{selected_med}': No non-expired stock available.")
                    elif dispense_qty > avail_stock:
                        st.error(f"Cannot dispense {dispense_qty} units: Only {avail_stock} non-expired units available.")
                    else:
                        success, message, deductions = inv_mgr.deduct_stock_fefo(
                            medicine_name=selected_med,
                            quantity=dispense_qty,
                            consumption_date=dispense_date,
                            notes=dispense_notes,
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

    with tab_history:
        st.markdown("### Consumption Records Audit Trail")
        cons_df = demand_an.get_consumption_dataframe()

        if cons_df.empty:
            st.info("No consumption records recorded yet.")
        else:
            h_col1, h_col2 = st.columns([2, 1])
            with h_col1:
                filter_med = st.selectbox("Filter History by Medicine", options=["All Medicines"] + sorted(list(cons_df["medicine_name"].unique())))
            with h_col2:
                st.caption(f"Total Transactions Logged: **{len(cons_df)}** | Total Units Dispensed: **{cons_df['quantity_consumed'].sum():,}**")

            display_df = cons_df.copy()
            if filter_med != "All Medicines":
                display_df = display_df[display_df["medicine_name"] == filter_med]

            # Format date for display
            display_df["consumption_date"] = display_df["consumption_date"].dt.strftime("%Y-%m-%d")
            display_df = display_df.sort_values(by="consumption_date", ascending=False).reset_index(drop=True)

            st.dataframe(
                display_df[["record_id", "consumption_date", "medicine_name", "batch_id", "quantity_consumed", "notes"]],
                use_container_width=True,
                hide_index=True,
            )

            # Download CSV
            csv_con = data_mgr.get_consumption_csv_string()
            st.download_button(
                label="📥 Export Consumption History as CSV",
                data=csv_con,
                file_name=f"medistock_consumption_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )


# =============================================================================
# 6. DEMAND ANALYSIS PAGE
# =============================================================================
elif page == "📈 Demand Analysis":
    st.markdown('<div class="main-title">Medicine Demand Analysis & Reorder Forecasting</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Statistical consumption rate analysis and transparent stock requirement modeling using Pandas & NumPy.</div>',
        unsafe_allow_html=True,
    )

    # Explanation Card for MCA Syllabus / Viva
    with st.expander("📚 Statistical Demand Modeling Methodology (MCA Syllabus Concept)", expanded=False):
        st.markdown(
            r"""
            This module applies **descriptive analytics and statistical forecasting** to historical consumption data:
            
            1. **Average Daily Consumption (ADC)**:
               $$\text{ADC} = \frac{\text{Total Quantity Consumed in Historical Window}}{\text{Analysis Period (Days)}}$$
            
            2. **Estimated Monthly Demand**:
               $$\text{Monthly Demand} = \text{ADC} \times 30$$
            
            3. **Stock Coverage (Days Remaining)**:
               $$\text{Coverage Days} = \frac{\text{Current Non-Expired Available Stock}}{\text{ADC}}$$
               *(Safely handled with zero-division protection when ADC = 0)*
            
            4. **Planned Stock Requirement**:
               $$\text{Estimated Requirement} = \lceil \text{ADC} \times \text{Planned Coverage Days} \rceil$$
            
            5. **Suggested Reorder Quantity**:
               $$\text{Suggested Reorder} = \max\left(0, \, \text{Estimated Requirement} - \text{Available Stock}\right)$$
            
            *Note: Transparent mathematical modeling is chosen over black-box machine learning to guarantee explainability in academic project vivas.*
            """
        )

    # Forecasting Configuration Controls
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        analysis_window = st.slider("Historical Consumption Window (Days)", min_value=7, max_value=90, value=30, step=1)
    with c_col2:
        coverage_period = st.slider("Target Future Stock Coverage (Days)", min_value=7, max_value=90, value=30, step=1)

    # Calculate metrics via Pandas & NumPy
    metrics_df = demand_an.calculate_demand_metrics(
        analysis_days=analysis_window,
        coverage_days=coverage_period,
    )

    if metrics_df.empty:
        st.info("No medicine or consumption data found. Please add medicines or seed sample data.")
    else:
        # Reorder Alert Summary
        reorder_needed = metrics_df[metrics_df["Suggested Reorder"] > 0]
        if not reorder_needed.empty:
            st.markdown(
                f"""
                <div class="callout-warn">
                    <strong>⚠️ Procurement Recommendation:</strong> Based on the past {analysis_window} days of consumption,
                    <strong>{len(reorder_needed)} medicine(s)</strong> require replenishment to maintain a {coverage_period}-day safety buffer.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Style table columns
        def highlight_urgency(val):
            if "Critical" in str(val):
                return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
            elif "High" in str(val):
                return "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
            elif "Moderate" in str(val):
                return "background-color: #fef9c3; color: #854d0e;"
            elif "Adequate" in str(val):
                return "background-color: #dcfce7; color: #166534;"
            return ""

        styled_df = metrics_df.style.applymap(highlight_urgency, subset=["Status"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Download Demand Report
        csv_metrics = metrics_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Demand Analysis Report (CSV)",
            data=csv_metrics,
            file_name=f"medistock_demand_forecast_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

        # Demand Visualizations
        st.markdown("### Stock vs Suggested Reorder Comparison")
        reorder_plot_df = metrics_df.head(8)
        if not reorder_plot_df.empty and reorder_plot_df[f"Req for {coverage_period}d"].sum() > 0:
            fig, ax = plt.subplots(figsize=(9, 4), dpi=100)
            fig.patch.set_facecolor("#ffffff")
            ax.set_facecolor("#f8fafc")

            x = np.arange(len(reorder_plot_df))
            width = 0.35

            ax.bar(x - width/2, reorder_plot_df["Available Stock"], width, label="Current Stock", color="#0284c7")
            ax.bar(x + width/2, reorder_plot_df[f"Req for {coverage_period}d"], width, label=f"Required ({coverage_period}d)", color="#f59e0b")

            ax.set_xticks(x)
            ax.set_xticklabels(reorder_plot_df["Medicine Name"], rotation=25, ha="right", fontsize=8.5, color="#1e293b")
            ax.set_ylabel("Quantity (Units)", fontsize=9, color="#475569")
            ax.set_title(f"Available Stock vs Projected Requirement ({coverage_period}-Day Coverage)", fontsize=11, fontweight="bold", pad=12)
            ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cbd5e1", fontsize=8.5)
            ax.grid(axis="y", linestyle="--", alpha=0.35, color="#94a3b8")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#cbd5e1")
            ax.spines["bottom"].set_color("#cbd5e1")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


# =============================================================================
# 7. ABOUT PROJECT & VIVA GUIDE PAGE
# =============================================================================
elif page == "ℹ️ About Project & Viva":
    st.markdown('<div class="main-title">About MediStock & MCA Viva Presentation Guide</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Project architecture, syllabus mapping, technical documentation, and presentation viva answers.</div>',
        unsafe_allow_html=True,
    )

    tab_doc, tab_viva, tab_future = st.tabs(["📖 Project Documentation", "🎓 Viva Voce Q&A Guide", "🚀 Future Integrations"])

    with tab_doc:
        st.markdown(
            """
            ### 1. Project Overview & Objectives
            **MediStock** is an intelligent pharmaceutical inventory, expiry monitoring, and demand analysis system engineered
            specifically for small hospital pharmacies, primary health centers (PHCs), and retail medical stores.
            
            #### Key Objectives:
            - **Batch-Level Inventory Tracking**: Maintain detailed lot numbers, manufacturing dates, expiry dates, and unit prices.
            - **Automated Expiry Safeguards**: Dynamically detect expired medicines and near-expiry stocks relative to current calendar dates.
            - **FEFO Dispensing**: Enforce First-Expiring, First-Out stock deduction to eliminate preventable medicine expiration wastage.
            - **Data-Driven Demand Forecasting**: Calculate average daily consumption rates (ADC) and project safety buffer reorder requirements using Pandas & NumPy.
            - **Visual Analytics**: Real-time charts rendered with Matplotlib illustrating monthly trends and inventory status distributions.
            
            ---
            
            ### 2. MCA Syllabus Concepts Demonstrated
            | Syllabus Topic | MediStock Implementation |
            | :--- | :--- |
            | **Object-Oriented Programming (OOP)** | Abstract base class `BaseEntity`, domain classes `MedicineBatch` & `ConsumptionRecord` with encapsulation, validation methods, and serialization. |
            | **File I/O & Data Persistence** | CSV storage with atomic temporary file swapping (`replace`) to guarantee zero corruption during unexpected power loss. |
            | **Defensive Programming & Exceptions** | Domain constraints check negative quantities, inverted manufacturing/expiry dates, duplicate batch IDs, and division-by-zero protection. |
            | **Data Analytics with Pandas** | Vectorized grouping, multi-table joins, date filtering, rolling windows, and aggregation over consumption histories. |
            | **Numerical Computing with NumPy** | Fast numeric array manipulation, precision rounding, and array mathematical ceiling operations. |
            | **Data Visualization with Matplotlib** | Bar charts, area-fill line trends, donut charts, and multi-series bar plots. |
            | **Unit Testing (Automated Verification)** | Comprehensive test suite using Python's standard `unittest` framework with isolated temporary directories. |
            """
        )

    with tab_viva:
        st.markdown(
            """
            ### Frequently Asked Viva Questions & Model Answers

            #### Q1: What problem does MediStock solve?
            **Answer**: Small pharmacies often suffer financial losses and safety hazards due to unmonitored medicine expiry and stockouts of critical drugs. MediStock provides automated expiry tracking, safety quarantine, and FEFO dispensing so older batches are used first, alongside data-driven reorder estimations based on actual consumption.

            #### Q2: Why is FEFO preferred over FIFO in pharmaceutical inventory?
            **Answer**: In general warehouses, FIFO (First In, First Out) uses the receipt date. In healthcare, however, a newly arrived batch might have a shorter shelf-life than existing stock due to manufacturer supply delays. **FEFO (First Expiring, First Out)** checks the actual expiration date and dispenses the batch closest to expiry, minimizing drug expiration waste.

            #### Q3: How is demand forecasting implemented without black-box ML?
            **Answer**: We compute the **Average Daily Consumption (ADC)** over a user-selected historical period (e.g., 30 days) using Pandas:
            $$\text{ADC} = \frac{\sum \text{Quantity Consumed}}{\text{Analysis Days}}$$
            Projected stock requirement for planned coverage (e.g., 30 days) is $\lceil \text{ADC} \times 30 \rceil$. Suggested reorder is the positive difference between requirement and current non-expired stock. This is transparent, verifiable, and explainable in academic vivas.

            #### Q4: Why are expired medicines excluded from available stock?
            **Answer**: Dispensing expired medication violates drug safety regulations and endangers patient health. Even if physical boxes exist on shelves, our system quarantines them with status `Expired` and assigns their effective available stock to 0 so they can never be dispensed.

            #### Q5: How do you prevent CSV file corruption during application crashes?
            **Answer**: In `DataManager.save_inventory_records()`, we use **atomic writes**: records are first written to a temporary file (`.tmp`). Once writing completes cleanly, we use `Path.replace()` to atomically swap the file. If an interruption occurs mid-write, the original CSV remains intact.
            """
        )

    with tab_future:
        st.markdown(
            """
            ### Future Roadmap & Academic Integration Points
            
            MediStock is engineered with clean modular boundaries to allow future integration with complementary MCA student projects:
            
            1. **MedChain (Medical Supply Monitoring & Multi-Tier Database)**:
               - Can replace the CSV persistence layer with an external relational database (PostgreSQL/MySQL) or distributed ledger.
               - MediStock's `DataManager` interface can be swapped without touching UI or domain models.
            
            2. **MedRoute (Medical Delivery Route Optimization)**:
               - The reorder quantities generated by MediStock's `DemandAnalyzer` can be fed directly as delivery order inputs into MedRoute's Dijkstra or Vehicle Routing Problem (VRP) algorithms.
               - This will enable automated restocking routes from central warehouses to distributed dispensaries.
            """
        )


# =============================================================================
# 8. DATA MANAGEMENT PAGE
# =============================================================================
elif page == "⚙️ Data Management":
    st.markdown('<div class="main-title">Data Storage & Demonstration Data Management</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Inspect raw CSV files, download backups, or reset demonstration records.</div>',
        unsafe_allow_html=True,
    )

    batches = inv_mgr.get_all_batches()
    cons_records = data_mgr.load_consumption_records()

    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.info(f"📁 **Medicine Inventory Storage:** `{data_mgr.inventory_path}` ({len(batches)} batches stored)")
    with col_stat2:
        st.info(f"📁 **Consumption Records Storage:** `{data_mgr.consumption_path}` ({len(cons_records)} records stored)")

    st.markdown("### Export Full Dataset")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        inv_csv = data_mgr.get_inventory_csv_string()
        st.download_button(
            "📥 Download Inventory CSV",
            data=inv_csv,
            file_name=f"medicine_inventory_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    with col_d2:
        con_csv = data_mgr.get_consumption_csv_string()
        st.download_button(
            "📥 Download Consumption CSV",
            data=con_csv,
            file_name=f"consumption_records_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("### Reset / Restore Demonstration Data")
    st.markdown(
        "For viva demonstrations or test presentations, you can restore the complete realistic demonstration dataset "
        "(20 diverse medicine batches and 48 consumption transactions)."
    )

    confirm_reset = st.checkbox("⚠️ Yes, I confirm I want to reset and restore sample demonstration data")
    if st.button("🔄 Reset to Demonstration Dataset", type="primary", disabled=not confirm_reset):
        num_b, num_c = seed_sample_data(data_mgr)
        inv_mgr.refresh_from_storage()
        st.success(f"✅ Successfully loaded {num_b} medicine batches and {num_c} historical consumption records!")
        st.rerun()

    st.markdown("---")
    st.markdown("### Inspect Raw CSV Files")
    with st.expander("📄 View Raw `medicine_inventory.csv`"):
        st.code(data_mgr.get_inventory_csv_string(), language="csv")
    with st.expander("📄 View Raw `consumption_records.csv`"):
        st.code(data_mgr.get_consumption_csv_string(), language="csv")
