"""
init_data_and_models.py
Bootstrapping Script: Initializes database, generates 90-day retail dataset,
and trains initial Random Forest predictive models.
"""

import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH, FOOTFALL_DATASET_CSV, TRANSACTIONS_DATASET_CSV, QUEUE_MODEL_PATH
from src.database import init_db, bulk_insert_footfall, bulk_insert_queue
from src.data_loader import ensure_datasets_exist
from src.ml_forecasting import train_eval_forecasting_model


def bootstrap():
    print("=" * 65)
    print("RTRFQM INITIALIZATION & DATA BOOTSTRAP PIPELINE")
    print("=" * 65)

    print("[1/4] Initializing SQLite Database schema & tables...")
    init_db(DB_PATH)
    print(f" Database successfully initialized at: {DB_PATH}")

    print("\n[2/4] Generating / Verifying 90-Day Longitudinal Retail Telemetry...")
    df_ff, df_tx = ensure_datasets_exist()
    print(f" Footfall Dataset: {len(df_ff):,} records saved at {FOOTFALL_DATASET_CSV}")
    print(f" Transactions Dataset: {len(df_tx):,} records saved at {TRANSACTIONS_DATASET_CSV}")

    print("\n[3/4] Populating database tables with historical baseline telemetry...")
    # Insert recent sample to DB for fast queries
    df_ff_recent = df_ff.tail(1500).copy()
    bulk_insert_footfall(df_ff_recent[["timestamp", "store_id", "entries", "exits", "net_occupancy", "arrival_rate", "peak_status"]])
    print(f" Bulk inserted {len(df_ff_recent)} records into footfall_records table.")

    print("\n[4/4] Training and serializing Supervised Random Forest Forecasting Engine...")
    eval_res = train_eval_forecasting_model(df_ff, target_col="queue_length", model_save_path=QUEUE_MODEL_PATH)
    print(f" Model Trained: {eval_res.get('model_type')}")
    print(f" Train Samples: {eval_res.get('train_samples')} | Test Samples: {eval_res.get('test_samples')}")
    print(f" Evaluation Metrics -> MAE: {eval_res.get('mae')} | RMSE: {eval_res.get('rmse')} | MAPE: {eval_res.get('mape')}% | R2: {eval_res.get('r2_score')}")
    print(f" Model successfully persisted at: {eval_res.get('model_path')}")

    print("=" * 65)
    print("BOOTSTRAP COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    bootstrap()
