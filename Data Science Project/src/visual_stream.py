"""
src/visual_stream.py
Synthetic Computer Vision & CCTV Overhead Surveillance Stream Simulator for RTRFQM
Generates annotated camera frames with Spatial ROI Polygons, Bounding Boxes, and Track IDs.
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def generate_overhead_surveillance_frame(
    lane_states: Dict[int, Dict[str, Any]],
    current_occupancy: int = 184,
    frame_width: int = 800,
    frame_height: int = 450
) -> Image.Image:
    """
    Renders a realistic CCTV surveillance frame simulating an overhead wide-angle camera
    mounted at 3.8m above the checkout counter zone.
    Overlays:
    - Polygonal Queue ROI Zones
    - Cashier Counter Baseline
    - Tracked customer bounding boxes with confidence scores & ByteTrack IDs
    - Camera telemetry OSD (On-Screen Display) with timestamp and FPS
    """
    # Create dark surveillance floor background
    img = Image.new("RGB", (frame_width, frame_height), color=(22, 27, 34))
    draw = ImageDraw.Draw(img)

    # Store floor tiling grid lines (subtle perspective grid)
    for y in range(80, frame_height, 45):
        draw.line([(0, y), (frame_width, y)], fill=(32, 38, 46), width=1)
    for x in range(0, frame_width, 60):
        draw.line([(x, 80), (x, frame_height)], fill=(32, 38, 46), width=1)

    # 1. Cashier Desk Baseline (Front of lanes)
    cashier_desk_y = 130
    draw.rectangle([40, cashier_desk_y - 25, frame_width - 40, cashier_desk_y], fill=(45, 55, 72), outline=(100, 116, 139), width=2)
    draw.text((50, cashier_desk_y - 20), "POS TERMINAL CONSOLES & CASHIER COUNTERS [LANES 1 - 6]", fill=(226, 232, 240))

    # Cashier Counter baseline (amber tripwire)
    draw.line([(40, cashier_desk_y + 4), (frame_width - 40, cashier_desk_y + 4)], fill=(234, 179, 8), width=3)
    draw.text((frame_width - 240, cashier_desk_y + 8), "--- TRANSACTION SERVICE BASELINE ---", fill=(234, 179, 8))

    # 2. Draw Queue ROI Zones and Tracked Shoppers for each lane
    num_lanes = len(lane_states)
    lane_w = (frame_width - 80) / max(1, num_lanes)

    track_id_counter = 101

    for idx, (l_id, state) in enumerate(sorted(lane_states.items())):
        lx_start = int(40 + idx * lane_w)
        lx_end = int(lx_start + lane_w - 12)
        ly_top = cashier_desk_y + 15
        ly_bottom = frame_height - 35

        is_active = state.get("is_active", True)
        q_len = state.get("queue_length", 0)
        status = state.get("status", "NORMAL")

        # Color based on status
        if not is_active:
            roi_color = (100, 116, 139) # gray
            lane_title = f"Lane #{l_id} [CLOSED]"
        elif status == "CRITICAL":
            roi_color = (239, 68, 68)   # red
            lane_title = f"Lane #{l_id} [CRITICAL: {q_len}]"
        elif status == "BUSY":
            roi_color = (245, 158, 11)  # amber
            lane_title = f"Lane #{l_id} [BUSY: {q_len}]"
        else:
            roi_color = (16, 185, 129)  # green
            lane_title = f"Lane #{l_id} [OK: {q_len}]"

        # Draw ROI polygon outline
        draw.rectangle([lx_start, ly_top, lx_end, ly_bottom], outline=roi_color, width=2)
        draw.text((lx_start + 6, ly_top + 6), lane_title, fill=roi_color)

        if is_active and q_len > 0:
            # Draw customer bounding boxes queued in this lane
            box_spacing = min(42, int((ly_bottom - ly_top - 50) / max(1, q_len)))
            for q_idx in range(min(q_len, 7)):
                cy = ly_top + 38 + q_idx * box_spacing
                cx = int((lx_start + lx_end) / 2)
                bw, bh = 34, 30

                bx1, by1 = cx - bw // 2, cy - bh // 2
                bx2, by2 = cx + bw // 2, cy + bh // 2

                # Person bounding box
                box_color = (239, 68, 68) if q_idx == 0 else (56, 189, 248) # head of queue highlighted
                draw.rectangle([bx1, by1, bx2, by2], outline=box_color, fill=(box_color[0]//4, box_color[1]//4, box_color[2]//4), width=2)

                # Head circle
                draw.ellipse([cx - 7, by1 + 4, cx + 7, by1 + 18], fill=(226, 232, 240), outline=box_color)

                # Track ID tag
                tag_text = f"ID:{track_id_counter}" if q_idx > 0 else f"ID:{track_id_counter} [Serving]"
                draw.rectangle([bx1, by1 - 12, bx1 + 48, by1], fill=(15, 23, 42))
                draw.text((bx1 + 2, by1 - 12), tag_text, fill=(255, 255, 255))
                track_id_counter += 1

    # 3. Top OSD Camera Banner
    draw.rectangle([0, 0, frame_width, 42], fill=(15, 23, 42))
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((15, 8), f"CCTV CAM-03 [Overhead Checkout Array] | RES: 1080p | FPS: 30.1", fill=(74, 222, 128))
    draw.text((15, 24), f"SYSTEM TIME: {timestamp_str} | NET STORE OCCUPANCY: {current_occupancy} PERSONS", fill=(203, 213, 225))
    draw.text((frame_width - 180, 12), "● REC [LIVE FEED]", fill=(239, 68, 68))

    # Bottom status bar
    draw.rectangle([0, frame_height - 24, frame_width, frame_height], fill=(15, 23, 42))
    draw.text((15, frame_height - 18), "ByteTrack Kalman Filter Active | YOLOv8 Spatial ROI In-Zone Raycasting Engine", fill=(148, 163, 184))

    return img
