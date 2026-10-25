# report_builder/chapter4.py
"""
Chapter 4: System Architecture and Engineering Design
Comprehensive academic chapter covering:
4.1 High-Level Four-Tier Architectural Model (Figure 4.1)
4.2 Data Flow Modeling (DFD Levels 0, 1, and 2) (Figure 4.2)
4.3 UML Use Case Analysis and Actor Interaction
4.4 Dynamic Behavioral Modeling and Sequence Architecture
4.5 Relational Database Schema and Data Dictionary (Table 4.1)
"""

import os
from docx.shared import Pt
from report_builder.styles import (
    add_chapter_heading,
    add_section_heading,
    add_body_paragraph,
    add_bullet_point,
    add_figure,
    add_styled_table,
    add_callout_box
)

FIG_DIR = r"e:\Data Science Project\figures"


def build_chapter4(doc):
    """Builds Chapter 4: System Architecture and Engineering Design."""
    add_chapter_heading(doc, 4, "System Architecture and Engineering Design")

    add_section_heading(doc, "4.1", "High-Level Four-Tier Architectural Model", level=2)
    add_body_paragraph(
        doc,
        "The Real-Time Retail Footfall and Queue Monitoring (RTRFQM) framework is engineered as a robust, "
        "loosely-coupled, four-tier distributed software architecture designed for high-throughput edge deployment. "
        "The architecture decouples heavy computer vision inference, analytical queue dynamics processing, persistent "
        "time-series telemetry storage, and web-based executive presentation into isolated, highly scalable operational tiers. "
        "Figure 4.1 illustrates the comprehensive four-tier system architecture, depicting the flow of data from physical "
        "overhead surveillance hardware to interactive managerial decision-support interfaces."
    )

    # Embed Figure 4.1: Architecture Diagram
    arch_img = os.path.join(FIG_DIR, "architecture_diagram.png")
    add_figure(
        doc,
        img_path=arch_img,
        caption="Real-Time Retail Store Footfall and Queue Monitoring System Architecture (Four-Tier Edge-Cloud Decomposition)",
        fig_num="4.1",
        width_inches=5.8
    )

    add_body_paragraph(
        doc,
        "The four architectural tiers operate cooperatively as follows:"
    )
    add_bullet_point(
        doc,
        "Comprises the physical Closed-Circuit Television (CCTV) cameras, IP security cameras, and network video encoders "
        "positioned at store entrances and overhead checkout zones. Video frames are transmitted via Real-Time Streaming "
        "Protocol (RTSP) over the store's local gigabit Ethernet network (LAN).",
        bold_prefix="Tier 1: Video Ingestion & Hardware Acquisition Layer:"
    )
    add_bullet_point(
        doc,
        "Resides on the local on-premises edge computing workstation. It encapsulates an asynchronous multi-threaded OpenCV "
        "frame grabber, adaptive image contrast preprocessor, and spatial Region of Interest (ROI) mask generator. This tier "
        "ensures a steady 30 FPS ingestion rate while isolating network jitter.",
        bold_prefix="Tier 2: Computer Vision & Tracking Engine Layer:"
    )
    add_bullet_point(
        doc,
        "Contains the computational core of the system: the YOLOv8 object detector and the ByteTrack association engine. "
        "It maintains active tracklets, performs virtual tripwire crossing calculations to determine directional footfall, "
        "and evaluates spatial occupancy within checkout queue polygons. It also hosts the Random Forest short-term queue "
        "forecasting engine and automated threshold evaluation logic.",
        bold_prefix="Tier 3: Queue Analytics & Machine Learning Intelligence Layer:"
    )
    add_bullet_point(
        doc,
        "Consists of a high-performance PostgreSQL relational database optimized for time-series append-only logging, paired "
        "with an interactive Streamlit web dashboard. Store supervisors access live telemetry, alert feeds, and queue charts "
        "via lightweight browser clients, while dispatch alerts are pushed to SMS and webhook endpoints.",
        bold_prefix="Tier 4: Persistence, Alerting & Presentation Layer:"
    )

    add_section_heading(doc, "4.2", "Data Flow Modeling (DFD Levels 0, 1, and 2)", level=2)
    add_body_paragraph(
        doc,
        "To rigorously document the transformation and lifecycle of telemetry across the RTRFQM pipeline, data flow is "
        "modeled hierarchically using Structured Analysis and Design Technique (SADT) across three levels of abstraction: "
        "Context-Level DFD (Level 0), Pipeline Processing DFD (Level 1), and Queue Subsystem DFD (Level 2)."
    )

    add_section_heading(doc, "4.2.1", "DFD Level 0: System Context Diagram", level=3)
    add_body_paragraph(
        doc,
        "At Level 0 (the Context Diagram), the entire RTRFQM system is represented as a single centralized software process "
        "interacting with four external environmental entities:"
    )
    add_bullet_point(
        doc,
        "Streams continuous raw video frames (H.264/H.265 encoded) into the system over RTSP.",
        bold_prefix="1. CCTV / IP Surveillance Cameras:"
    )
    add_bullet_point(
        doc,
        "Receives real-time footfall statistics, queue length gauges, predicted wait times, and automated staffing alerts "
        "via the web dashboard; configures operational thresholds (e.g., maximum queue limit).",
        bold_prefix="2. Store Shift Manager:"
    )
    add_bullet_point(
        doc,
        "Receives mobile dispatch alerts recommending the opening or closing of specific backup cashier counters.",
        bold_prefix="3. Cashier Staff / Team Leads:"
    )
    add_bullet_point(
        doc,
        "Stores structured, anonymized time-series telemetry records and historical audit logs.",
        bold_prefix="4. Enterprise Database Storage:"
    )

    add_section_heading(doc, "4.2.2", "DFD Level 1: System Pipeline Processing Architecture", level=3)
    add_body_paragraph(
        doc,
        "Figure 4.2 presents the DFD Level 1 architecture, detailing the step-by-step transformations as video data flows "
        "through frame preprocessing, YOLOv8 detection, ByteTrack tracking, footfall line-crossing analysis, queue ROI dynamics, "
        "and persistent database logging."
    )

    # Embed Figure 4.2: DFD Pipeline Diagram
    dfd_img = os.path.join(FIG_DIR, "dfd_pipeline.png")
    add_figure(
        doc,
        img_path=dfd_img,
        caption="RTRFQM Data Flow Diagram (DFD Level 1) and Processing Pipeline Architecture",
        fig_num="4.2",
        width_inches=5.8
    )

    add_body_paragraph(
        doc,
        "As illustrated in Figure 4.2, raw video frames are decoded and preprocessed (Process 1.0) before being fed into "
        "the YOLOv8 neural network (Process 2.0). The resulting bounding box coordinates are transferred to the ByteTrack "
        "engine (Process 3.0), which produces persistent trajectory tracklets. Tracklets crossing defined line coordinates "
        "increment entry/exit accumulators (Process 4.0), while tracklets dwelling within checkout polygons are evaluated for "
        "queue length and waiting time (Process 5.0). All metrics are streamed to the database store and managerial dashboard."
    )

    add_section_heading(doc, "4.2.3", "DFD Level 2: Queue Dynamics & Predictive Subsystem", level=3)
    add_body_paragraph(
        doc,
        "At DFD Level 2, Process 5.0 (Queue Dynamics) is decomposed into three sub-processes: Tracklet Dwell Time Tracking "
        "(5.1), Point-in-Polygon Queue Length Aggregation (5.2), and Random Forest Congestion Prediction (5.3). Sub-process "
        "5.1 calculates the exact elapsed time between tracklet entry into the checkout zone and exit past the cashier point. "
        "Sub-process 5.2 computes instantaneous customer counts across individual lanes. Sub-process 5.3 ingests rolling "
        "15-minute lag queues and outputs predicted 15-minute forward congestion probabilities, triggering alerts when "
        "predicted queue length exceeds the threshold Lq > 5."
    )

    add_section_heading(doc, "4.3", "UML Use Case Analysis and Actor Interaction", level=2)
    add_body_paragraph(
        doc,
        "The functional capabilities of the RTRFQM system are formally defined through Unified Modeling Language (UML) "
        "Use Case analysis. The system interfaces with four distinct operational actors, each possessing specific access "
        "privileges and functional responsibilities:"
    )
    add_bullet_point(
        doc,
        "Monitors live store footfall and active queue lengths; inspects historical footfall trends; receives automated "
        "congestion SMS alerts; acknowledges dispatch recommendations; exports analytical PDF/Excel summary reports.",
        bold_prefix="Actor 1: Store Shift Manager:"
    )
    add_bullet_point(
        doc,
        "Receives counter dispatch notifications; opens or closes backup checkout counters in response to automated system "
        "alerts; verifies counter operational status.",
        bold_prefix="Actor 2: Cashier Team Lead / Floor Supervisor:"
    )
    add_bullet_point(
        doc,
        "Configures RTSP camera stream URLs; defines polygonal coordinates for virtual lines and queue ROIs; sets "
        "congestion alarm thresholds (e.g., Lq threshold = 5 persons); manages database backup and purge schedules.",
        bold_prefix="Actor 3: System Administrator / IT Specialist:"
    )
    add_bullet_point(
        doc,
        "The automated background engine executing scheduled model retraining, database persistence, and system health "
        "monitoring without human intervention.",
        bold_prefix="Actor 4: Automated System Engine (Daemon):"
    )

    add_section_heading(doc, "4.4", "Dynamic Behavioral Modeling and Sequence Architecture", level=2)
    add_body_paragraph(
        doc,
        "The temporal execution and inter-component message sequencing of the RTRFQM framework are governed by a strictly "
        "timed sequence loop operating on every incoming video frame. The complete sequence consists of eight discrete phases:"
    )
    add_bullet_point(
        doc,
        "The asynchronous camera ingestion thread captures an RTSP frame, assigns a high-resolution microsecond timestamp, "
        "and places the frame into a ring buffer queue.",
        bold_prefix="Phase 1 (Frame Ingestion):"
    )
    add_bullet_point(
        doc,
        "The inference worker pops the frame, resizes it to 640x640 resolution, and passes it through the YOLOv8 tensor engine, "
        "producing raw detection tensors [x1, y1, x2, y2, confidence, class].",
        bold_prefix="Phase 2 (Inference):"
    )
    add_bullet_point(
        doc,
        "ByteTrack compares current bounding boxes against active Kalman filter state predictions using two-stage Hungarian "
        "association, outputting verified tracklet identifiers.",
        bold_prefix="Phase 3 (Tracking & State Update):"
    )
    add_bullet_point(
        doc,
        "The analytics engine calculates displacement vectors between tracklet centroids in frame t and frame t-1 across "
        "virtual tripwires, incrementing entry or exit counters accordingly.",
        bold_prefix="Phase 4 (Tripwire Verification):"
    )
    add_bullet_point(
        doc,
        "Tracklet centroids are tested against polygonal checkout ROIs using the Jordan curve ray-casting algorithm. "
        "Matching tracklets are counted as active queue occupants.",
        bold_prefix="Phase 5 (Queue ROI Aggregation):"
    )
    add_bullet_point(
        doc,
        "The Random Forest regressor evaluates current queue length, temporal lags, and active cashiers, generating a predicted "
        "queue length for t + 15 minutes.",
        bold_prefix="Phase 6 (Predictive Forecasting):"
    )
    add_bullet_point(
        doc,
        "If predicted queue length exceeds the congestion threshold (Lq > 5), an automated dispatch alert event is logged "
        "and pushed to the notification queue.",
        bold_prefix="Phase 7 (Alert Triggering):"
    )
    add_bullet_point(
        doc,
        "Aggregated metrics are written asynchronously to the PostgreSQL database, and updated state tensors are pushed to "
        "the Streamlit web frontend via WebSocket.",
        bold_prefix="Phase 8 (Persistence & Presentation):"
    )

    add_section_heading(doc, "4.5", "Relational Database Schema and Data Dictionary", level=2)
    add_body_paragraph(
        doc,
        "To ensure high-throughput time-series logging without introducing disk I/O bottlenecks during live video analytics, "
        "the persistence tier employs PostgreSQL with relational indexing. Table 4.1 documents the comprehensive data "
        "dictionary for the core telemetry tables: store_footfall_log, checkout_queue_log, and dispatch_alert_log."
    )

    db_headers = [
        "Table Name",
        "Field Name",
        "Data Type",
        "Key / Constraint",
        "Field Description & Operational Semantics"
    ]

    db_data = [
        [
            "store_footfall_log",
            "log_id",
            "BIGSERIAL",
            "PRIMARY KEY",
            "Unique auto-incrementing record identifier."
        ],
        [
            "store_footfall_log",
            "timestamp",
            "TIMESTAMPTZ",
            "NOT NULL, INDEX",
            "UTC timestamp of the observation window."
        ],
        [
            "store_footfall_log",
            "camera_id",
            "VARCHAR(32)",
            "NOT NULL",
            "Identifier of the physical surveillance camera (e.g., CAM-01)."
        ],
        [
            "store_footfall_log",
            "entry_count",
            "INTEGER",
            "CHECK (entry_count >= 0)",
            "Cumulative customer entries across virtual tripwire."
        ],
        [
            "store_footfall_log",
            "exit_count",
            "INTEGER",
            "CHECK (exit_count >= 0)",
            "Cumulative customer exits across virtual tripwire."
        ],
        [
            "store_footfall_log",
            "net_occupancy",
            "INTEGER",
            "CHECK (net_occupancy >= 0)",
            "Instantaneous active shoppers present in store (entry - exit)."
        ],
        [
            "checkout_queue_log",
            "queue_log_id",
            "BIGSERIAL",
            "PRIMARY KEY",
            "Unique identifier for checkout queue observation."
        ],
        [
            "checkout_queue_log",
            "timestamp",
            "TIMESTAMPTZ",
            "NOT NULL, INDEX",
            "UTC timestamp of the queue measurement sample."
        ],
        [
            "checkout_queue_log",
            "counter_id",
            "VARCHAR(16)",
            "NOT NULL",
            "Identifier of specific checkout lane (e.g., LANE-02)."
        ],
        [
            "checkout_queue_log",
            "queue_length",
            "INTEGER",
            "NOT NULL",
            "Number of customers detected waiting in checkout ROI."
        ],
        [
            "checkout_queue_log",
            "avg_wait_min",
            "NUMERIC(5,2)",
            "NOT NULL",
            "Average measured customer waiting time in minutes."
        ],
        [
            "checkout_queue_log",
            "active_cashiers",
            "INTEGER",
            "NOT NULL",
            "Number of cashier stations actively processing transactions."
        ],
        [
            "checkout_queue_log",
            "predicted_queue_15m",
            "NUMERIC(5,2)",
            "DEFAULT NULL",
            "Random Forest forecasted queue length for t + 15 minutes."
        ],
        [
            "dispatch_alert_log",
            "alert_id",
            "BIGSERIAL",
            "PRIMARY KEY",
            "Unique identifier for automated congestion alert event."
        ],
        [
            "dispatch_alert_log",
            "timestamp",
            "TIMESTAMPTZ",
            "NOT NULL, INDEX",
            "Timestamp when congestion threshold was exceeded."
        ],
        [
            "dispatch_alert_log",
            "counter_id",
            "VARCHAR(16)",
            "NOT NULL",
            "Checkout lane experiencing bottleneck."
        ],
        [
            "dispatch_alert_log",
            "alert_severity",
            "VARCHAR(16)",
            "CHECK IN ('WARNING', 'CRITICAL')",
            "Severity level based on queue length (>5 or >8 customers)."
        ],
        [
            "dispatch_alert_log",
            "action_recommended",
            "VARCHAR(128)",
            "NOT NULL",
            "Specific dispatch directive (e.g., 'Open Backup Lane 5')."
        ],
        [
            "dispatch_alert_log",
            "resolved_at",
            "TIMESTAMPTZ",
            "DEFAULT NULL",
            "Timestamp when queue dissipated below threshold."
        ]
    ]

    add_styled_table(
        doc,
        headers=db_headers,
        data=db_data,
        col_widths=[1.2, 1.2, 1.0, 1.1, 1.9],
        caption="PostgreSQL Relational Schema & Data Dictionary for Retail Footfall & Queue Telemetry",
        table_num="4.1"
    )
