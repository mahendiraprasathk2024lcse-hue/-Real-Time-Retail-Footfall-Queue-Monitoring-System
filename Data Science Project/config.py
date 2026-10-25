"""
config.py
Configuration parameters for Retail Footfall & Queue Monitoring System (RTRFQM)
"""

import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Database
DB_PATH = os.path.join(DATA_DIR, "retail_monitoring.db")

# Datasets
FOOTFALL_DATASET_CSV = os.path.join(DATA_DIR, "retail_footfall_queue_data.csv")
TRANSACTIONS_DATASET_CSV = os.path.join(DATA_DIR, "retail_transactions.csv")

# Models
FOOTFALL_MODEL_PATH = os.path.join(MODELS_DIR, "footfall_forecast_rf.joblib")
QUEUE_MODEL_PATH = os.path.join(MODELS_DIR, "queue_forecast_rf.joblib")

# Store Metadata
STORE_ID = "STORE-104"
STORE_NAME = "HyperMart Superstore #104 (Flagship Branch)"
STORE_OPEN_HOUR = 8   # 08:00
STORE_CLOSE_HOUR = 22 # 22:00
MAX_STORE_CAPACITY = 350 # safe fire occupancy limit

# Cashier Lanes Configuration
LANES_CONFIG = {
    1: {"name": "Lane 1 (Express <10 items)", "type": "Express", "base_mu": 0.90, "max_capacity": 10},
    2: {"name": "Lane 2 (Standard A)", "type": "Standard", "base_mu": 0.60, "max_capacity": 12},
    3: {"name": "Lane 3 (Standard B)", "type": "Standard", "base_mu": 0.58, "max_capacity": 12},
    4: {"name": "Lane 4 (Bulk Groceries)", "type": "Bulk", "base_mu": 0.45, "max_capacity": 15},
    5: {"name": "Lane 5 (Backup Flex)", "type": "Flex", "base_mu": 0.62, "max_capacity": 12},
    6: {"name": "Lane 6 (Priority / Senior)", "type": "Priority", "base_mu": 0.55, "max_capacity": 10},
}
TOTAL_COUNTERS = len(LANES_CONFIG)
DEFAULT_ACTIVE_COUNTERS = 4

# Little's Law and Queue Dynamics Default Parameters
DEFAULT_SERVICE_RATE_MU = 0.606  # customers served per minute per lane (~1.65 min/cust)
TARGET_WAIT_TIME_MIN = 3.0       # Target maximum acceptable queue wait time

# Congestion Alert Thresholds
CONGESTION_THRESHOLDS = {
    "NORMAL": {"max_queue": 3, "max_wait_time": 2.5},
    "BUSY": {"max_queue": 5, "max_wait_time": 4.0},
    "CRITICAL": {"min_queue": 6, "min_wait_time": 4.0}
}
DEFAULT_WARN_QUEUE_LEN = 4
DEFAULT_CRITICAL_QUEUE_LEN = 6
DEFAULT_WARN_WAIT_MINUTES = 3.5
DEFAULT_CRITICAL_WAIT_MINUTES = 5.0

# Alert Deduplication Window (seconds)
ALERT_DEDUP_WINDOW_SECONDS = 300  # 5 minutes
