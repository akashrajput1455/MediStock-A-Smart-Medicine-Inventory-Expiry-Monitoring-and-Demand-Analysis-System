"""
MediStock Demand Analysis and Forecasting Module.

Performs historical consumption analysis, average daily consumption (ADC)
calculations, stock coverage estimations, and reorder projections using
NumPy and Pandas. Generates clean Matplotlib figures for reporting.

Note for MCA Syllabus & Viva:
This module demonstrates statistical data processing and trend forecasting
using standard analytical formulas (not opaque AI/ML black boxes), allowing
students to clearly explain every equation line-by-line.
"""

import math
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from modules.inventory_manager import InventoryManager
from utils.data_manager import DataManager


class DemandAnalyzer:
    """
    Analyzes historical medicine consumption and projects future stock requirements.
    """

    def __init__(
        self,
        inventory_manager: Optional[InventoryManager] = None,
        data_manager: Optional[DataManager] = None,
    ):
        self.data_manager = data_manager or DataManager()
        self.inventory_manager = inventory_manager or InventoryManager(self.data_manager)

    def get_consumption_dataframe(self) -> pd.DataFrame:
        """
        Loads consumption records into a typed Pandas DataFrame.
        Returns an empty DataFrame with required schema if no records exist.
        """
        records = self.data_manager.load_consumption_records()
        if not records:
            return pd.DataFrame(
                columns=[
                    "record_id",
                    "medicine_name",
                    "batch_id",
                    "consumption_date",
                    "quantity_consumed",
                    "notes",
                    "created_at",
                ]
            )

        df = pd.DataFrame(records)
        df["consumption_date"] = pd.to_datetime(df["consumption_date"], errors="coerce")
        df["quantity_consumed"] = pd.to_numeric(df["quantity_consumed"], errors="coerce").fillna(0).astype(int)
        df["medicine_name"] = df["medicine_name"].astype(str).str.strip()
        # Drop invalid rows
        df = df.dropna(subset=["consumption_date"])
        return df

    def get_inventory_dataframe(self) -> pd.DataFrame:
        """
        Loads all batches into a typed Pandas DataFrame.
        """
        batches = self.inventory_manager.get_all_batches()
        if not batches:
            return pd.DataFrame(columns=[
                "batch_id", "medicine_name", "category", "batch_number",
                "manufacturer", "quantity", "min_stock_level", "unit_price",
                "mfg_date", "expiry_date", "created_at"
            ])

        records = [b.to_dict() for b in batches]
        df = pd.DataFrame(records)
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        df["min_stock_level"] = pd.to_numeric(df["min_stock_level"], errors="coerce").fillna(0).astype(int)
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0).astype(float)
        df["mfg_date"] = pd.to_datetime(df["mfg_date"], errors="coerce")
        df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce")
        return df

    def calculate_demand_metrics(
        self,
        analysis_days: int = 30,
        coverage_days: int = 30,
        reference_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """
        Calculates demand estimation and reorder metrics for all known medicines.
        
        Mathematical Formulas Applied:
        1. Historical Window: [reference_date - analysis_days, reference_date]
        2. Total Consumed = sum(quantity_consumed in window)
        3. Average Daily Consumption (ADC) = Total Consumed / analysis_days
        4. Estimated Monthly Consumption = ADC * 30
        5. Available Stock = sum(quantity of non-expired batches for medicine)
        6. Stock Coverage (Days) = Available Stock / ADC  (handling ADC == 0)
        7. Required Stock for Coverage = ceil(ADC * coverage_days)
        8. Suggested Reorder Quantity = max(0, Required Stock - Available Stock)
        """
        ref = reference_date or date.today()
        start_date = pd.Timestamp(ref - timedelta(days=analysis_days))
        end_date = pd.Timestamp(ref)

        cons_df = self.get_consumption_dataframe()
        all_medicines = self.inventory_manager.get_medicine_names()
        available_stocks = self.inventory_manager.get_available_stock_by_medicine(ref)

        # Filter consumption within historical window
        if not cons_df.empty:
            mask = (cons_df["consumption_date"] >= start_date) & (cons_df["consumption_date"] <= end_date)
            window_df = cons_df[mask]
        else:
            window_df = pd.DataFrame()

        # Group consumption by medicine name
        if not window_df.empty:
            consumed_summary = window_df.groupby("medicine_name")["quantity_consumed"].sum().to_dict()
        else:
            consumed_summary = {}

        # Combine all medicine names from inventory and consumption
        all_unique_meds = sorted(list(set(all_medicines).union(set(consumed_summary.keys()))))

        rows = []
        for med in all_unique_meds:
            tot_consumed = consumed_summary.get(med, 0)
            avail_stock = available_stocks.get(med, 0)

            # Calculation: Average Daily Consumption (NumPy float precision)
            adc = float(np.round(tot_consumed / max(1, analysis_days), 2))
            est_monthly = float(np.round(adc * 30.0, 1))

            # Stock Coverage in Days calculation with defensive division
            if adc > 0:
                coverage = float(np.round(avail_stock / adc, 1))
            else:
                coverage = float(999.0 if avail_stock > 0 else 0.0)

            # Estimated Stock Requirement for planned coverage period
            est_requirement = int(math.ceil(adc * coverage_days))

            # Suggested Reorder Quantity
            suggested_reorder = max(0, est_requirement - avail_stock)

            # Classification of urgency
            if avail_stock == 0 and adc > 0:
                urgency = "Critical (Stockout)"
            elif coverage < 7 and adc > 0:
                urgency = "High Priority"
            elif coverage < 15 and adc > 0:
                urgency = "Moderate"
            elif adc == 0:
                urgency = "No Recent Demand"
            else:
                urgency = "Adequate Stock"

            rows.append({
                "Medicine Name": med,
                "Available Stock": avail_stock,
                f"Consumed ({analysis_days}d)": tot_consumed,
                "Avg Daily (ADC)": adc,
                "Est Monthly": est_monthly,
                "Stock Coverage (Days)": coverage,
                f"Req for {coverage_days}d": est_requirement,
                "Suggested Reorder": suggested_reorder,
                "Status": urgency,
            })

        result_df = pd.DataFrame(rows)
        if not result_df.empty:
            # Sort with most urgent reorders first
            result_df = result_df.sort_values(
                by=["Suggested Reorder", "Avg Daily (ADC)"], ascending=[False, False]
            ).reset_index(drop=True)

        return result_df

    # -------------------------------------------------------------
    # Visualizations using Matplotlib & Seaborn/Healthcare styling
    # -------------------------------------------------------------

    def plot_top_consumed_medicines(self, top_n: int = 6, days: int = 30) -> Optional[plt.Figure]:
        """
        Generates a clean horizontal bar chart of the highest-consumed medicines.
        """
        cons_df = self.get_consumption_dataframe()
        if cons_df.empty:
            return None

        # Filter recent
        cutoff = pd.Timestamp(date.today() - timedelta(days=days))
        recent_df = cons_df[cons_df["consumption_date"] >= cutoff]
        if recent_df.empty:
            recent_df = cons_df  # Fallback to all data if none in recent window

        grouped = recent_df.groupby("medicine_name")["quantity_consumed"].sum().reset_index()
        grouped = grouped.sort_values(by="quantity_consumed", ascending=True).tail(top_n)

        if grouped.empty or grouped["quantity_consumed"].sum() == 0:
            return None

        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        y_pos = np.arange(len(grouped))
        bars = ax.barh(
            y_pos,
            grouped["quantity_consumed"],
            color="#0284c7",
            edgecolor="#0369a1",
            height=0.6,
            alpha=0.9,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(grouped["medicine_name"], fontsize=9, fontweight="500", color="#1e293b")
        ax.set_xlabel(f"Units Consumed (Past {days} Days)", fontsize=9, color="#475569")
        ax.set_title(f"Top {top_n} Most Consumed Medicines", fontsize=11, fontweight="bold", color="#0f172a", pad=12)

        # Value annotations on bar tips
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(grouped["quantity_consumed"]) * 0.02),
                bar.get_y() + bar.get_height() / 2,
                f"{int(width)}",
                ha="left",
                va="center",
                fontsize=8.5,
                fontweight="600",
                color="#0f172a",
            )

        ax.grid(axis="x", linestyle="--", alpha=0.35, color="#94a3b8")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cbd5e1")
        ax.spines["bottom"].set_color("#cbd5e1")
        plt.tight_layout()
        return fig

    def plot_monthly_consumption_trend(self) -> Optional[plt.Figure]:
        """
        Generates a line chart showing medicine consumption aggregated by month.
        """
        cons_df = self.get_consumption_dataframe()
        if cons_df.empty:
            return None

        # Create Month-Year period column
        df = cons_df.copy()
        df["month_year"] = df["consumption_date"].dt.to_period("M")
        monthly = df.groupby("month_year")["quantity_consumed"].sum().reset_index()

        if len(monthly) < 1:
            return None

        # Convert period back to string for plotting
        monthly["month_str"] = monthly["month_year"].astype(str)

        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        x_coords = np.arange(len(monthly))
        ax.plot(
            x_coords,
            monthly["quantity_consumed"],
            marker="o",
            markersize=7,
            color="#0ea5e9",
            linewidth=2.5,
            label="Total Units Consumed",
        )
        ax.fill_between(x_coords, monthly["quantity_consumed"], color="#0ea5e9", alpha=0.12)

        ax.set_xticks(x_coords)
        ax.set_xticklabels(monthly["month_str"], fontsize=9, color="#1e293b")
        ax.set_ylabel("Total Units Dispensed", fontsize=9, color="#475569")
        ax.set_title("Monthly Medicine Consumption Trend", fontsize=11, fontweight="bold", color="#0f172a", pad=12)

        for x, y in zip(x_coords, monthly["quantity_consumed"]):
            ax.annotate(
                f"{int(y)}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=8.5,
                fontweight="600",
                color="#0f172a",
            )

        ax.grid(axis="y", linestyle="--", alpha=0.35, color="#94a3b8")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#cbd5e1")
        ax.spines["bottom"].set_color("#cbd5e1")
        plt.tight_layout()
        return fig

    def plot_inventory_status_distribution(self, reference_date: Optional[date] = None) -> Optional[plt.Figure]:
        """
        Generates a breakdown of batches by status:
        In Stock, Low Stock, Expiring Soon, Expired.
        """
        ref = reference_date or date.today()
        batches = self.inventory_manager.get_all_batches()
        if not batches:
            return None

        status_counts = {
            "In Stock (Safe)": 0,
            "Low Stock": 0,
            "Expiring Soon": 0,
            "Expired": 0,
        }

        for b in batches:
            if b.is_expired(ref):
                status_counts["Expired"] += 1
            elif b.is_expiring_soon(30, ref):
                status_counts["Expiring Soon"] += 1
            elif b.is_low_stock():
                status_counts["Low Stock"] += 1
            else:
                status_counts["In Stock (Safe)"] += 1

        labels = [k for k, v in status_counts.items() if v > 0]
        values = [status_counts[k] for k in labels]
        color_map = {
            "In Stock (Safe)": "#10b981",    # Emerald green
            "Low Stock": "#f59e0b",          # Amber
            "Expiring Soon": "#f97316",      # Orange
            "Expired": "#ef4444",            # Red
        }
        colors = [color_map[label] for label in labels]

        if not values:
            return None

        fig, ax = plt.subplots(figsize=(6, 3.8), dpi=100)
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            pctdistance=0.75,
            textprops={"fontsize": 8.5, "color": "#1e293b"},
            wedgeprops=dict(width=0.45, edgecolor="#ffffff", linewidth=2),
        )
        for at in autotexts:
            at.set_fontsize(8)
            at.set_fontweight("600")

        ax.set_title("Inventory Batches by Status", fontsize=11, fontweight="bold", color="#0f172a", pad=12)
        plt.tight_layout()
        return fig
