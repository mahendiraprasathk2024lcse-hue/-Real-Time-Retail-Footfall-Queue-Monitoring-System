"""
src/queue_dynamics.py
Module C: Checkout Queue Monitoring, Counter Dynamics, and Queue State Evaluation
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from config import (
    LANES_CONFIG,
    DEFAULT_WARN_QUEUE_LEN,
    DEFAULT_CRITICAL_QUEUE_LEN,
    DEFAULT_SERVICE_RATE_MU
)


def evaluate_lane_status(queue_length: int, warn_thresh: int = DEFAULT_WARN_QUEUE_LEN, crit_thresh: int = DEFAULT_CRITICAL_QUEUE_LEN) -> Tuple[str, str]:
    """
    Evaluates queue congestion status and returns (status_label, hex_color).
    """
    if queue_length >= crit_thresh:
        return "CRITICAL", "#dc2626" # Red
    elif queue_length >= warn_thresh:
        return "BUSY", "#f59e0b"     # Amber / Warning
    else:
        return "NORMAL", "#10b981"   # Emerald Green


def compute_counter_metrics(
    lane_states: Dict[int, Dict[str, Any]],
    arrival_rate: float
) -> Dict[str, Any]:
    """
    Calculates multi-counter queue metrics:
    - Active counters
    - Overall queue length
    - Average queue length per active lane
    - Average waiting time across lanes
    - Utilization percentage rho = lambda / (c * mu)
    """
    active_lanes = [l for l, d in lane_states.items() if d.get("is_active", True)]
    c = max(1, len(active_lanes))
    total_q = sum(d.get("queue_length", 0) for d in lane_states.values())
    avg_q = round(total_q / c, 2)

    # Effective storewide service rate = sum(mu_i for active lanes)
    total_mu = sum(lane_states[l].get("service_rate_mu", DEFAULT_SERVICE_RATE_MU) for l in active_lanes)
    total_mu = max(0.01, total_mu)

    # Utilization rho
    rho = min(1.0, max(0.0, (arrival_rate / total_mu) if total_mu > 0 else 0.0))
    utilization_pct = round(rho * 100.0, 1)

    # Average wait time Little's Law: Wq = Lq / (c * mu)
    overall_wait_min = round(total_q / total_mu, 2)

    # Critical lanes count
    crit_count = sum(1 for d in lane_states.values() if d.get("status") == "CRITICAL")
    busy_count = sum(1 for d in lane_states.values() if d.get("status") == "BUSY")

    return {
        "active_counters_count": c,
        "total_counters_count": len(lane_states),
        "total_queue_length": total_q,
        "avg_queue_per_lane": avg_q,
        "effective_service_rate": round(total_mu, 2),
        "storewide_utilization_pct": utilization_pct,
        "overall_wait_time_min": overall_wait_min,
        "critical_lanes_count": crit_count,
        "busy_lanes_count": busy_count
    }


def create_lanes_overview_chart(lane_states: Dict[int, Dict[str, Any]]) -> go.Figure:
    """Generates horizontal / vertical bar chart showing queue lengths and status per checkout counter."""
    lanes = []
    names = []
    queues = []
    colors = []
    statuses = []
    wait_times = []

    for l_id in sorted(lane_states.keys()):
        d = lane_states[l_id]
        lanes.append(f"Lane {l_id}")
        names.append(d.get("name", f"Lane {l_id}"))
        q = d.get("queue_length", 0)
        queues.append(q)
        status, color = evaluate_lane_status(q)
        if not d.get("is_active", True):
            status = "CLOSED"
            color = "#94a3b8" # gray
        statuses.append(status)
        colors.append(color)
        wait_times.append(d.get("estimated_wait_min", 0.0))

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=lanes,
        y=queues,
        marker_color=colors,
        text=[f"<b>{q} cust</b><br>({st})<br>~{wt:.1f}m" for q, st, wt in zip(queues, statuses, wait_times)],
        textposition="outside",
        name="Queue Length (Observed)"
    ))

    # Add warning and critical threshold horizontal lines
    fig.add_hline(
        y=DEFAULT_WARN_QUEUE_LEN,
        line_dash="dot",
        line_color="#f59e0b",
        annotation_text=f"Warning Threshold ({DEFAULT_WARN_QUEUE_LEN})",
        annotation_position="bottom left"
    )
    fig.add_hline(
        y=DEFAULT_CRITICAL_QUEUE_LEN,
        line_dash="dash",
        line_color="#dc2626",
        annotation_text=f"Critical Threshold ({DEFAULT_CRITICAL_QUEUE_LEN})",
        annotation_position="top left"
    )

    fig.update_layout(
        title="Real-Time Checkout Lane Queue Lengths & Congestion Classification",
        xaxis=dict(title="Checkout Counter"),
        yaxis=dict(title="Queue Length (Number of Waiting Customers)", range=[0, max(8, max(queues, default=0) + 3)]),
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def create_queue_history_chart(df_queue: pd.DataFrame) -> go.Figure:
    """Generates queue length over time trend line chart."""
    if df_queue.empty or "timestamp" not in df_queue.columns:
        return go.Figure()

    df_recent = df_queue.tail(200).copy()

    fig = go.Figure()
    if "lane_id" in df_recent.columns:
        for lane_id, grp in df_recent.groupby("lane_id"):
            fig.add_trace(go.Scatter(
                x=grp["timestamp"],
                y=grp["queue_length"],
                mode="lines",
                name=f"Lane {lane_id}"
            ))
    elif "queue_length" in df_recent.columns:
        fig.add_trace(go.Scatter(
            x=df_recent["timestamp"],
            y=df_recent["queue_length"],
            mode="lines",
            line=dict(color="#d62728", width=2.5),
            name="Total Store Queue"
        ))

    fig.update_layout(
        title="Checkout Queue Dynamics Over Elapsed Monitoring Time",
        xaxis=dict(title="Timestamp"),
        yaxis=dict(title="Queue Length (Customers)"),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
