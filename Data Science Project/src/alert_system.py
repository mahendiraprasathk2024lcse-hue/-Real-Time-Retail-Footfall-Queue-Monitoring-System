"""
src/alert_system.py
Module G: Congestion Detection, Hysteresis Alerting, and Staff Dispatch Directives
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from config import (
    DEFAULT_WARN_QUEUE_LEN,
    DEFAULT_CRITICAL_QUEUE_LEN,
    DEFAULT_WARN_WAIT_MINUTES,
    DEFAULT_CRITICAL_WAIT_MINUTES
)
from src.database import log_congestion_alert, get_active_alerts, resolve_alert, get_all_alerts


class AlertManager:
    """Manages real-time congestion evaluation, deduplication, and dispatch rules."""

    def __init__(
        self,
        warn_queue_len: int = DEFAULT_WARN_QUEUE_LEN,
        crit_queue_len: int = DEFAULT_CRITICAL_QUEUE_LEN,
        warn_wait_min: float = DEFAULT_WARN_WAIT_MINUTES,
        crit_wait_min: float = DEFAULT_CRITICAL_WAIT_MINUTES
    ):
        self.warn_queue_len = warn_queue_len
        self.crit_queue_len = crit_queue_len
        self.warn_wait_min = warn_wait_min
        self.crit_wait_min = crit_wait_min

    def evaluate_and_dispatch(
        self,
        lane_states: Dict[int, Dict[str, Any]],
        overall_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Scans all active checkout lanes for congestion threshold breaches.
        Generates actionable alerts with deduplication.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generated_alerts = []

        # Find backup lanes currently closed that could be opened
        closed_lanes = [l for l, d in lane_states.items() if not d.get("is_active", True)]
        recommended_lane_to_open = closed_lanes[0] if closed_lanes else None

        for lane_id, state in lane_states.items():
            if not state.get("is_active", True):
                continue

            q_len = state.get("queue_length", 0)
            w_min = state.get("estimated_wait_min", 0.0)
            lane_name = state.get("name", f"Lane {lane_id}")

            condition = None
            severity = None
            action = None

            if q_len >= self.crit_queue_len or w_min >= self.crit_wait_min:
                severity = "CRITICAL"
                condition = f"{lane_name} queue critical ({q_len} customers waiting, ~{w_min:.1f}m wait)"
                if recommended_lane_to_open:
                    action = f"URGENT: Open Backup Lane #{recommended_lane_to_open} immediately to relieve Lane #{lane_id}."
                else:
                    action = f"URGENT: All lanes active. Deploy floor assistant to assist cashier at Lane #{lane_id} with packing."
            elif q_len >= self.warn_queue_len or w_min >= self.warn_wait_min:
                severity = "WARNING"
                condition = f"{lane_name} approaching capacity ({q_len} customers, ~{w_min:.1f}m wait)"
                action = f"ADVISORY: Prepare backup cashier on standby for Lane #{lane_id}."

            if severity and condition and action:
                alert_id = log_congestion_alert(
                    timestamp=now_str,
                    lane_id=lane_id,
                    condition=condition,
                    severity=severity,
                    recommended_action=action
                )
                if alert_id:
                    generated_alerts.append({
                        "id": alert_id,
                        "timestamp": now_str,
                        "lane_id": lane_id,
                        "condition": condition,
                        "severity": severity,
                        "recommended_action": action,
                        "status": "ACTIVE"
                    })

        return generated_alerts

    @staticmethod
    def get_live_alerts() -> List[Dict[str, Any]]:
        """Returns all currently active unresolved alerts."""
        return get_active_alerts()

    @staticmethod
    def dismiss_alert(alert_id: int) -> bool:
        """Resolves an active alert."""
        return resolve_alert(alert_id)

    @staticmethod
    def get_alert_history(limit: int = 50) -> pd.DataFrame:
        """Returns historical alert audit trail."""
        return get_all_alerts(limit=limit)
