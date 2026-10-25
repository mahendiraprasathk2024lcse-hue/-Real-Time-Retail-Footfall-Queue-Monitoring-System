"""
src/simulation_engine.py
Module F: Real-Time Discrete-Event Queue Simulation Engine for Retail Checkout
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

from config import (
    LANES_CONFIG,
    DEFAULT_SERVICE_RATE_MU,
    DEFAULT_WARN_QUEUE_LEN,
    DEFAULT_CRITICAL_QUEUE_LEN
)
from src.database import save_footfall_record, save_queue_observation
from src.waiting_time import estimate_waiting_time_littles_law
from src.queue_dynamics import evaluate_lane_status


class SimulationEngine:
    """
    Simulates retail store customer footfall arrivals and multi-counter checkout dynamics.
    Produces realistic stochastic queues and Little's Law waiting times.
    """

    def __init__(self, seed: Optional[int] = 42):
        if seed:
            np.random.seed(seed)
        self.reset()

    def reset(self) -> None:
        """Resets the simulation to baseline morning state."""
        self.is_running = False
        self.sim_time = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)
        self.step_counter = 0

        # In-store state
        self.net_occupancy = 120
        self.total_entries_today = 840
        self.total_exits_today = 720

        # Multi-counter queues
        self.lane_states = {}
        for l_id, cfg in LANES_CONFIG.items():
            is_active = (l_id <= 4) # Lanes 1-4 open initially, 5-6 backup
            q_len = int(np.random.randint(1, 4)) if is_active else 0
            mu = cfg["base_mu"]
            wait_min = estimate_waiting_time_littles_law(q_len, mu)
            status, _ = evaluate_lane_status(q_len)

            self.lane_states[l_id] = {
                "lane_id": l_id,
                "name": cfg["name"],
                "type": cfg["type"],
                "is_active": is_active,
                "queue_length": q_len,
                "service_rate_mu": mu,
                "estimated_wait_min": wait_min,
                "status": status,
                "total_served": int(np.random.randint(40, 80)) if is_active else 0
            }

        self.recent_events_log: List[Dict[str, Any]] = []
        self._add_event("SYSTEM_INIT", "Simulation initialized. Baseline counters 1 to 4 active.")

    def _add_event(self, event_type: str, details: str) -> None:
        """Records an event in the simulation log."""
        ts = self.sim_time.strftime("%H:%M:%S")
        self.recent_events_log.insert(0, {
            "timestamp": ts,
            "type": event_type,
            "details": details
        })
        if len(self.recent_events_log) > 50:
            self.recent_events_log.pop()

    def set_counter_active(self, lane_id: int, is_active: bool) -> None:
        """Dynamically opens or closes a checkout lane."""
        if lane_id in self.lane_states:
            self.lane_states[lane_id]["is_active"] = is_active
            action_str = "Opened" if is_active else "Closed"
            if not is_active:
                # If closing, redistribute queue
                excess = self.lane_states[lane_id]["queue_length"]
                self.lane_states[lane_id]["queue_length"] = 0
                self.lane_states[lane_id]["status"] = "CLOSED"
                self.lane_states[lane_id]["estimated_wait_min"] = 0.0
                active_lanes = [l for l, d in self.lane_states.items() if d["is_active"]]
                if active_lanes and excess > 0:
                    for _ in range(excess):
                        target = min(active_lanes, key=lambda l: self.lane_states[l]["queue_length"])
                        self.lane_states[target]["queue_length"] += 1
            self._add_event("COUNTER_STATUS_CHANGE", f"Lane #{lane_id} ({self.lane_states[lane_id]['name']}) was {action_str}.")

    def step(self, surge_multiplier: float = 1.0) -> Dict[str, Any]:
        """
        Advances the simulation by 1 discrete minute time step:
        - Stochastic customer entries generated (Poisson process)
        - Exits simulated
        - Arriving shoppers at checkout join shortest active queue
        - Cashiers process transactions based on their service rate mu
        """
        self.step_counter += 1
        self.sim_time += timedelta(minutes=1)
        now_ts_str = self.sim_time.strftime("%Y-%m-%d %H:%M:%S")

        # Arrival rate depends on hour of day
        hour = self.sim_time.hour
        # Peak hours: 11-13 (lunch) and 18-20 (evening)
        is_peak = (11 <= hour <= 13) or (17 <= hour <= 20)
        base_arrival_rate = 3.5 if is_peak else 2.1
        current_arrival_rate = round(base_arrival_rate * surge_multiplier + np.random.normal(0, 0.4), 2)
        current_arrival_rate = max(0.2, current_arrival_rate)

        # Entering store
        entries_this_min = int(np.random.poisson(lam=current_arrival_rate))
        exits_this_min = int(np.random.poisson(lam=max(0.5, current_arrival_rate * 0.92)))

        self.net_occupancy = int(np.clip(self.net_occupancy + entries_this_min - exits_this_min, 10, 340))
        self.total_entries_today += entries_this_min
        self.total_exits_today += exits_this_min

        # Shoppers completing browsing and proceeding to checkout
        checkout_arrivals = int(np.random.poisson(lam=current_arrival_rate))
        active_lanes = [l for l, d in self.lane_states.items() if d["is_active"]]

        # Distribute arrivals into shortest active lane
        if active_lanes:
            for _ in range(checkout_arrivals):
                # Express lane 1 gets small arrivals
                if 1 in active_lanes and np.random.random() < 0.35 and self.lane_states[1]["queue_length"] < 6:
                    target_lane = 1
                else:
                    # Choose shortest active standard/flex lane
                    target_lane = min(active_lanes, key=lambda l: self.lane_states[l]["queue_length"])
                self.lane_states[target_lane]["queue_length"] += 1

        # Service completion at each active cashier counter
        total_q_now = 0
        for l_id, state in self.lane_states.items():
            if not state["is_active"]:
                state["queue_length"] = 0
                state["status"] = "CLOSED"
                state["estimated_wait_min"] = 0.0
                continue

            q = state["queue_length"]
            mu = state["service_rate_mu"]

            # Probability of completing service in this minute: mu
            # e.g. mu = 0.60 => 60% chance 1 served, plus random Poisson
            completed = int(np.random.binomial(n=max(1, min(q, 2)), p=min(0.85, mu))) if q > 0 else 0
            completed = min(completed, q)

            state["queue_length"] = max(0, q - completed)
            state["total_served"] += completed
            total_q_now += state["queue_length"]

            # Update wait time and status
            wait_min = estimate_waiting_time_littles_law(state["queue_length"], mu)
            state["estimated_wait_min"] = wait_min
            status, _ = evaluate_lane_status(state["queue_length"])
            state["status"] = status

        # Persist observation to database
        try:
            save_footfall_record(
                timestamp=now_ts_str,
                store_id="STORE-104",
                entries=entries_this_min * 15, # scaled
                exits=exits_this_min * 15,
                net_occupancy=self.net_occupancy,
                arrival_rate=current_arrival_rate,
                peak_status="PEAK" if is_peak else "NORMAL"
            )
            for l_id, state in self.lane_states.items():
                if state["is_active"]:
                    save_queue_observation(
                        timestamp=now_ts_str,
                        lane_id=l_id,
                        queue_length=state["queue_length"],
                        waiting_time_min=state["estimated_wait_min"],
                        service_rate_mu=state["service_rate_mu"],
                        utilization_pct=min(100.0, (current_arrival_rate / (len(active_lanes) * 0.606)) * 100),
                        status=state["status"]
                    )
        except Exception:
            pass

        return {
            "timestamp": now_ts_str,
            "net_occupancy": self.net_occupancy,
            "total_entries": self.total_entries_today,
            "total_exits": self.total_exits_today,
            "arrival_rate": current_arrival_rate,
            "active_counters": len(active_lanes),
            "total_queue": total_q_now,
            "lane_states": self.lane_states
        }
