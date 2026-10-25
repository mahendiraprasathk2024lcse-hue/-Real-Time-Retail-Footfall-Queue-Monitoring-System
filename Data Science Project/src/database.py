"""
src/database.py
SQLite Database Layer for RTRFQM: Footfall, Queue Observations, Alerts, and Persistence
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from config import DB_PATH, LANES_CONFIG


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(db_path, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initializes the database schema and indexes."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Footfall Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS footfall_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        store_id TEXT NOT NULL,
        entries INTEGER NOT NULL,
        exits INTEGER NOT NULL,
        net_occupancy INTEGER NOT NULL,
        arrival_rate REAL NOT NULL,
        peak_status TEXT NOT NULL
    );
    """)

    # 2. Queue Observations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queue_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        lane_id INTEGER NOT NULL,
        queue_length INTEGER NOT NULL,
        waiting_time_min REAL NOT NULL,
        service_rate_mu REAL NOT NULL,
        utilization_pct REAL NOT NULL,
        status TEXT NOT NULL
    );
    """)

    # 3. Checkout Counters Master Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkout_counters (
        lane_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        cashier_name TEXT,
        total_served INTEGER NOT NULL DEFAULT 0,
        avg_service_time REAL NOT NULL DEFAULT 1.65,
        last_updated TEXT
    );
    """)

    # 4. Congestion Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS congestion_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        lane_id INTEGER NOT NULL,
        condition TEXT NOT NULL,
        severity TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        resolved_at TEXT
    );
    """)

    # 5. Simulation & System Events Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        details TEXT NOT NULL,
        store_footfall INTEGER NOT NULL,
        total_queue INTEGER NOT NULL
    );
    """)

    # Create Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_footfall_ts ON footfall_records(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_ts ON queue_observations(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_lane_ts ON queue_observations(lane_id, timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_status ON congestion_alerts(status);")

    # Seed default counters if not exists
    cursor.execute("SELECT COUNT(*) FROM checkout_counters;")
    count = cursor.fetchone()[0]
    if count == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for lane_id, cfg in LANES_CONFIG.items():
            is_act = 1 if lane_id <= 4 else 0
            cursor.execute("""
            INSERT INTO checkout_counters (lane_id, name, type, is_active, cashier_name, total_served, avg_service_time, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (lane_id, cfg["name"], cfg["type"], is_act, f"Cashier-{lane_id:02d}", 0, 1.65, now_str))

    conn.commit()
    conn.close()


def save_footfall_record(
    timestamp: str,
    store_id: str,
    entries: int,
    exits: int,
    net_occupancy: int,
    arrival_rate: float,
    peak_status: str,
    db_path: str = DB_PATH
) -> int:
    """Inserts a single footfall record."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO footfall_records (timestamp, store_id, entries, exits, net_occupancy, arrival_rate, peak_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, store_id, entries, exits, net_occupancy, arrival_rate, peak_status))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def save_queue_observation(
    timestamp: str,
    lane_id: int,
    queue_length: int,
    waiting_time_min: float,
    service_rate_mu: float,
    utilization_pct: float,
    status: str,
    db_path: str = DB_PATH
) -> int:
    """Inserts a single queue observation record."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO queue_observations (timestamp, lane_id, queue_length, waiting_time_min, service_rate_mu, utilization_pct, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, lane_id, queue_length, waiting_time_min, service_rate_mu, utilization_pct, status))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def log_congestion_alert(
    timestamp: str,
    lane_id: int,
    condition: str,
    severity: str,
    recommended_action: str,
    db_path: str = DB_PATH
) -> Optional[int]:
    """Logs an alert if no identical active alert exists within the deduplication window."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Check for recent active alert on same lane
    cursor.execute("""
    SELECT id, timestamp FROM congestion_alerts
    WHERE lane_id = ? AND status = 'ACTIVE'
    ORDER BY id DESC LIMIT 1
    """, (lane_id,))
    existing = cursor.fetchone()

    if existing:
        # Prevent spamming alerts if one is already active on this lane
        conn.close()
        return None

    cursor.execute("""
    INSERT INTO congestion_alerts (timestamp, lane_id, condition, severity, recommended_action, status)
    VALUES (?, ?, ?, ?, ?, 'ACTIVE')
    """, (timestamp, lane_id, condition, severity, recommended_action))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id


def resolve_alert(alert_id: int, db_path: str = DB_PATH) -> bool:
    """Marks an alert as resolved."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE congestion_alerts
    SET status = 'RESOLVED', resolved_at = ?
    WHERE id = ?
    """, (now_str, alert_id))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def get_active_alerts(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all active congestion alerts."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM congestion_alerts WHERE status = 'ACTIVE' ORDER BY id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_all_alerts(limit: int = 100, db_path: str = DB_PATH) -> pd.DataFrame:
    """Returns alerts dataframe."""
    conn = get_connection(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM congestion_alerts ORDER BY id DESC LIMIT ?",
        conn,
        params=(limit,)
    )
    conn.close()
    return df


def get_counters_state(db_path: str = DB_PATH) -> pd.DataFrame:
    """Returns all counters status."""
    conn = get_connection(db_path)
    df = pd.read_sql_query("SELECT * FROM checkout_counters ORDER BY lane_id ASC", conn)
    conn.close()
    return df


def update_counter_status(lane_id: int, is_active: bool, db_path: str = DB_PATH) -> None:
    """Updates counter active status."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE checkout_counters SET is_active = ?, last_updated = ? WHERE lane_id = ?
    """, (1 if is_active else 0, now_str, lane_id))
    conn.commit()
    conn.close()


def bulk_insert_footfall(df: pd.DataFrame, db_path: str = DB_PATH) -> None:
    """Bulk inserts a DataFrame of footfall records."""
    if df.empty:
        return
    conn = get_connection(db_path)
    df.to_sql("footfall_records", conn, if_exists="append", index=False)
    conn.close()


def bulk_insert_queue(df: pd.DataFrame, db_path: str = DB_PATH) -> None:
    """Bulk inserts a DataFrame of queue observations."""
    if df.empty:
        return
    conn = get_connection(db_path)
    df.to_sql("queue_observations", conn, if_exists="append", index=False)
    conn.close()


def get_footfall_dataframe(limit: Optional[int] = None, db_path: str = DB_PATH) -> pd.DataFrame:
    """Retrieves footfall records as a pandas DataFrame."""
    conn = get_connection(db_path)
    query = "SELECT * FROM footfall_records ORDER BY timestamp ASC"
    if limit:
        query += f" LIMIT {int(limit)}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def get_queue_dataframe(limit: Optional[int] = None, db_path: str = DB_PATH) -> pd.DataFrame:
    """Retrieves queue records as a pandas DataFrame."""
    conn = get_connection(db_path)
    query = "SELECT * FROM queue_observations ORDER BY timestamp ASC"
    if limit:
        query += f" LIMIT {int(limit)}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
