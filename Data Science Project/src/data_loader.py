"""
src/data_loader.py
Dataset Management: Ingestion, Validation, Synthetic Generation, and Cleaning for RTRFQM
"""

import os
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd

from config import (
    FOOTFALL_DATASET_CSV,
    TRANSACTIONS_DATASET_CSV,
    LANES_CONFIG,
    STORE_OPEN_HOUR,
    STORE_CLOSE_HOUR,
    STORE_ID
)


# Expected schemas for validation
REQUIRED_FOOTFALL_COLUMNS = [
    "timestamp",
    "entries",
    "exits",
    "net_occupancy",
    "arrival_rate",
    "queue_length",
    "active_counters",
    "avg_waiting_time"
]

REQUIRED_TRANSACTION_COLUMNS = [
    "transaction_id",
    "timestamp",
    "lane_id",
    "items_count",
    "basket_value",
    "service_duration_sec",
    "payment_mode"
]


def generate_synthetic_telemetry(days: int = 90, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates a realistic 90-day longitudinal retail store footfall, queue,
    and register transaction dataset matching retail supermarket physics.
    Clearly labelled as synthetic simulation dataset.
    """
    np.random.seed(seed)
    
    # 90 days ending today
    end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days)
    
    records = []
    transactions = []
    trans_id_counter = 10001
    
    curr = start_date
    while curr <= end_date:
        hour = curr.hour
        day_of_week = curr.weekday() # 0=Mon, 6=Sun
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Only simulate during store operating hours
        if STORE_OPEN_HOUR <= hour < STORE_CLOSE_HOUR:
            # Diurnal entry profile (customers per hour)
            # 8: 40, 9: 75, 10: 130, 11: 185, 12: 175, 13: 140, 14: 110, 15: 125, 16: 150, 17: 210, 18: 300, 19: 290, 20: 220, 21: 80
            base_hourly = {
                8: 42, 9: 78, 10: 135, 11: 182, 12: 172, 13: 138,
                14: 112, 15: 128, 16: 155, 17: 218, 18: 305, 19: 295,
                20: 225, 21: 85
            }
            mean_entries = base_hourly.get(hour, 60)
            
            # Weekend surge factor
            if is_weekend:
                mean_entries = int(mean_entries * 1.38)
            
            # 15-minute slice entries
            slice_entries = int(np.maximum(2, np.random.poisson(lam=mean_entries / 4.0)))
            
            # Exits lag entries by average dwell time (~30 mins)
            slice_exits = int(np.maximum(1, np.random.poisson(lam=slice_entries * 0.96)))
            
            # Net Occupancy
            net_occ = int(np.clip(slice_entries * 2.8 + np.random.normal(0, 5), 5, 320))
            
            # Instantaneous arrival rate at checkout (customers/min)
            arrival_rate = round(slice_entries / 15.0, 2)
            
            # Number of active counters adjusts with traffic
            if net_occ > 220 or arrival_rate > 3.8:
                active_c = 5
            elif net_occ > 140 or arrival_rate > 2.5:
                active_c = 4
            elif net_occ > 70 or arrival_rate > 1.2:
                active_c = 3
            else:
                active_c = 2
            
            # Total storewide queue length
            # Effective service capacity = active_c * mu * 15 min
            service_capacity = active_c * 0.606 * 15.0
            excess = slice_entries - service_capacity
            mean_q = max(1.2, 1.5 + (excess / active_c if excess > 0 else 0) + np.random.normal(0, 0.6))
            total_queue = int(np.clip(np.random.poisson(lam=mean_q * active_c), 1, 35))
            
            # Little's law waiting time: Wq = Lq / (c * mu)
            avg_wait_min = round(max(0.4, total_queue / (active_c * 0.606) + np.random.normal(0, 0.2)), 2)
            
            peak_status = "PEAK" if (hour in [11, 12, 18, 19, 20] or total_queue >= 18) else "NORMAL"
            
            records.append({
                "timestamp": curr.strftime("%Y-%m-%d %H:%M:%S"),
                "store_id": STORE_ID,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "entries": slice_entries,
                "exits": slice_exits,
                "net_occupancy": net_occ,
                "arrival_rate": arrival_rate,
                "queue_length": total_queue,
                "active_counters": active_c,
                "avg_waiting_time": avg_wait_min,
                "peak_status": peak_status
            })
            
            # Sample granular transactions
            num_tx = min(slice_entries, np.random.randint(2, 6))
            for _ in range(num_tx):
                lane = int(np.random.choice(list(LANES_CONFIG.keys())[:active_c]))
                items = int(np.clip(np.random.geometric(p=0.08), 1, 45))
                # Service duration ~ items * 4 sec + payment (30 sec)
                duration_sec = int(np.clip(items * 3.8 + np.random.normal(32, 10), 18, 280))
                basket_val = round(float(items * np.random.uniform(80, 220) + np.random.normal(50, 20)), 2)
                pay_mode = np.random.choice(["UPI / QR", "Credit Card", "Debit Card", "Cash"], p=[0.52, 0.24, 0.14, 0.10])
                
                transactions.append({
                    "transaction_id": f"TXN-{trans_id_counter}",
                    "timestamp": curr.strftime("%Y-%m-%d %H:%M:%S"),
                    "lane_id": lane,
                    "items_count": items,
                    "basket_value": basket_val,
                    "service_duration_sec": duration_sec,
                    "payment_mode": pay_mode
                })
                trans_id_counter += 1
                
        curr += timedelta(minutes=15)
        
    df_footfall = pd.DataFrame(records)
    df_trans = pd.DataFrame(transactions)
    return df_footfall, df_trans


def ensure_datasets_exist() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Checks if primary datasets exist on disk; generates and persists them if not."""
    if os.path.exists(FOOTFALL_DATASET_CSV) and os.path.exists(TRANSACTIONS_DATASET_CSV):
        try:
            df_ff = pd.read_csv(FOOTFALL_DATASET_CSV)
            df_tx = pd.read_csv(TRANSACTIONS_DATASET_CSV)
            df_ff["timestamp"] = pd.to_datetime(df_ff["timestamp"])
            df_tx["timestamp"] = pd.to_datetime(df_tx["timestamp"])
            return df_ff, df_tx
        except Exception:
            pass

    # Generate fresh realistic synthetic dataset
    df_ff, df_tx = generate_synthetic_telemetry(days=90)
    os.makedirs(os.path.dirname(FOOTFALL_DATASET_CSV), exist_ok=True)
    df_ff.to_csv(FOOTFALL_DATASET_CSV, index=False)
    df_tx.to_csv(TRANSACTIONS_DATASET_CSV, index=False)
    df_ff["timestamp"] = pd.to_datetime(df_ff["timestamp"])
    df_tx["timestamp"] = pd.to_datetime(df_tx["timestamp"])
    return df_ff, df_tx


def validate_dataframe(df: pd.DataFrame, schema_type: str = "footfall") -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates user-uploaded or disk DataFrame against expected schema.
    Returns (is_valid, error_or_success_message, stats_dict).
    """
    if df is None or df.empty:
        return False, "Error: The uploaded dataset is empty.", {}

    required = REQUIRED_FOOTFALL_COLUMNS if schema_type == "footfall" else REQUIRED_TRANSACTION_COLUMNS
    missing_cols = [col for col in required if col not in df.columns]

    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}", {}

    # Check for nulls and clean
    null_counts = df[required].isnull().sum().to_dict()
    total_nulls = sum(null_counts.values())

    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "missing_values_count": total_nulls,
        "null_details": null_counts,
        "date_range": (
            str(df["timestamp"].min()) if "timestamp" in df.columns else "N/A",
            str(df["timestamp"].max()) if "timestamp" in df.columns else "N/A"
        )
    }

    return True, "Dataset structure successfully verified.", stats


def clean_telemetry_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans telemetry DataFrame:
    - Parses timestamps
    - Drops duplicates on timestamp
    - Imputes missing numerical values with median/forward fill
    - Clips negative values
    """
    df = df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp")

    # Numeric columns cleaning
    num_cols = df.select_dtypes(include=[np.number]).columns
    for c in num_cols:
        df[c] = df[c].ffill().bfill().fillna(0)
        if c in ["entries", "exits", "net_occupancy", "queue_length", "active_counters"]:
            df[c] = np.maximum(0, df[c]).astype(int)
        elif c in ["arrival_rate", "avg_waiting_time"]:
            df[c] = np.maximum(0.0, df[c])

    return df
