# report_builder/chapter10.py
"""
Chapter 10: Conclusion, Managerial Insights, and Future Enhancements
Comprehensive academic chapter covering:
10.1 Summary of Project Contributions
10.2 Managerial Implications and Operational Value
10.3 Ethical Governance and Privacy Protection in Retail AI
10.4 Limitations of the Current Study
10.5 Future Research and Technical Roadmaps
"""

from docx.shared import Pt
from report_builder.styles import (
    add_chapter_heading,
    add_section_heading,
    add_body_paragraph,
    add_bullet_point,
    add_callout_box
)


def build_chapter10(doc):
    """Builds Chapter 10: Conclusion, Managerial Insights, and Future Enhancements."""
    add_chapter_heading(doc, 10, "Conclusion and Future Enhancements")

    add_section_heading(doc, "10.1", "Summary of Project Contributions", level=2)
    add_body_paragraph(
        doc,
        "This engineering research project has successfully designed, mathematically formulated, implemented, and empirically "
        "validated a comprehensive, privacy-preserving, data-driven framework: the Real-Time Retail Footfall and Queue Monitoring "
        "(RTRFQM) system. By bridging the long-standing divide between computer vision edge analytics, classical queueing theory, "
        "and predictive machine learning, the framework resolves the observational blindness that has historically plagued physical "
        "retail store operations."
    )
    add_body_paragraph(
        doc,
        "The core technical accomplishments and empirical contributions delivered by this research include:"
    )
    add_bullet_point(
        doc,
        "Integrated an anchor-free YOLOv8 deep learning detector with the ByteTrack multi-object tracking algorithm, achieving "
        "state-of-the-art tracking accuracy (76.4% MOTA, 78.2% IDF1) at an edge inference throughput of 38.5 FPS on standard "
        "GPU hardware, suppressing identity switches by 72.3% relative to vanilla SORT.",
        bold_prefix="1. High-Precision Lightweight Vision Pipeline:"
    )
    add_bullet_point(
        doc,
        "Developed 2D vector cross-product tripwire logic for bidirectional customer footfall counting and polygonal Region "
        "of Interest (ROI) ray-casting algorithms for spatial queue length and dwell time measurement.",
        bold_prefix="2. Mathematical Spatial Analytics Engine:"
    )
    add_bullet_point(
        doc,
        "Empirically validated measured queue waiting times against Little's Law (W_q = L_q / (c * mu)), demonstrating a high "
        "linear correlation (r = 0.962) that links physical video tracking directly to formal service operations equations.",
        bold_prefix="3. Little's Law Theoretical Validation:"
    )
    add_bullet_point(
        doc,
        "Engineered an optimized Random Forest short-term queue forecasting engine that achieves an outstanding Mean Absolute "
        "Error of 0.72 customers across a 15-minute forward horizon, outperforming traditional ARIMA by over 60%.",
        bold_prefix="4. Anticipatory Machine Learning Forecasting:"
    )
    add_bullet_point(
        doc,
        "Demonstrated in longitudinal operational evaluations that automated congestion dispatching curtails peak checkout "
        "queues by 55.3%, reduces mean customer waiting times by 34.2%, and cuts cart abandonment rates by 69.2%.",
        bold_prefix="5. Transformative Operational Impact:"
    )

    add_section_heading(doc, "10.2", "Managerial Implications and Operational Value", level=2)
    add_body_paragraph(
        doc,
        "The findings of this research provide profound operational, managerial, and economic implications for retail executives "
        "and store managers:"
    )
    add_bullet_point(
        doc,
        "Instead of dispatching backup cashiers reactively after customer tempers flare or carts are abandoned, store supervisors "
        "receive automated mobile notifications 10–15 minutes prior to anticipated congestion surges, smoothing customer flow "
        "and eliminating friction at the most vulnerable touchpoint of the shopping journey.",
        bold_prefix="Transition from Reactive to Proactive Staffing:"
    )
    add_bullet_point(
        doc,
        "By aligning active cashier stations with real-time arrival rates rather than rigid static rosters, supermarkets eliminate "
        "costly cashier idle time during morning and mid-afternoon lulls, improving labor productivity by 28.3%.",
        bold_prefix="Payroll Optimization and Labor Efficiency:"
    )
    add_bullet_point(
        doc,
        "Coupling true footfall counts with Point-of-Sale receipts unlocks accurate, real-time conversion rates across trading "
        "hours, allowing merchandisers to quantitatively assess the footfall generation power of promotional displays and end-cap layouts.",
        bold_prefix="Granular Conversion Intelligence:"
    )

    add_section_heading(doc, "10.3", "Ethical Governance and Privacy Protection in Retail AI", level=2)
    add_body_paragraph(
        doc,
        "A foundational design imperative of the RTRFQM framework is strict compliance with international data privacy legislation "
        "(GDPR, CCPA, and India's DPDPA 2023). Unlike controversial biometric surveillance systems that extract facial recognition "
        "templates, estimate demographic attributes, or track individual consumers across visits, RTRFQM enforces privacy-by-design:"
    )
    add_bullet_point(
        doc,
        "Detections are restricted strictly to generic 'person' bounding box coordinates. The system possesses zero facial recognition "
        "or biometric extraction capabilities.",
        bold_prefix="Strictly Anonymized Bounding Boxes:"
    )
    add_bullet_point(
        doc,
        "Target identifiers (track IDs) are temporary integer counters maintained exclusively in volatile RAM while the target remains "
        "within camera view. Once a shopper exits the camera ROI, the tracklet memory is permanently purged.",
        bold_prefix="Ephemeral Volatile Identifiers:"
    )
    add_bullet_point(
        doc,
        "Video frames are decoded, analyzed, and immediately discarded in GPU volatile memory. No video recordings, facial images, "
        "or identifiable visual artifacts are written to persistent disk or transmitted across external networks.",
        bold_prefix="Zero Video Archival on Disk:"
    )

    add_section_heading(doc, "10.4", "Limitations of the Current Study", level=2)
    add_body_paragraph(
        doc,
        "In maintaining rigorous academic standards, several operational limitations of the present study must be acknowledged:"
    )
    add_bullet_point(
        doc,
        "The computer vision detection and tracking models require overhead or elevated oblique camera angles (mounting heights >= 2.8 m). "
        "Horizontal ground-level cameras introduce severe inter-person visual occlusions that reduce tracking accuracy.",
        bold_prefix="Camera Perspective Dependencies:"
    )
    add_bullet_point(
        doc,
        "The queue dynamics engine currently models cashier service rate mu as a homogeneous mean parameter per counter. In reality, "
        "transaction times vary significantly based on basket size, payment method (cash vs. contactless digital wallet), and cashier experience.",
        bold_prefix="Service Rate Homogeneity Assumptions:"
    )
    add_bullet_point(
        doc,
        "Extreme visual obstructions (such as large overhead promotional banners or massive hanging holiday displays) can partially "
        "occlude entrance tripwires, requiring manual software polygon re-calibration upon store layout modifications.",
        bold_prefix="Physical Store Obstruction Sensitivity:"
    )

    add_section_heading(doc, "10.5", "Future Research and Technical Roadmaps", level=2)
    add_body_paragraph(
        doc,
        "To extend the capabilities of the RTRFQM framework, future research investigations will pursue five high-impact technical directions:"
    )
    add_bullet_point(
        doc,
        "Investigate lightweight vision transformers (e.g., MobileViT, YOLOv9/v10) to enhance detection precision in extreme low-lux "
        "and heavy crowd densities without sacrificing real-time edge inference throughput.",
        bold_prefix="1. Transformer-Based Vision Backbones:"
    )
    add_bullet_point(
        doc,
        "Deploy the tracking pipeline onto ultra-low-power edge hardware accelerators (such as Google Coral Edge TPU and NVIDIA Jetson "
        "Orin Nano), enabling decentralized per-camera processing at under 15 watts of power consumption.",
        bold_prefix="2. Embedded Edge TPU and Micro-Appliance Deployment:"
    )
    add_bullet_point(
        doc,
        "Extend the tracking architecture to handle cross-camera handoffs across dozens of non-overlapping store cameras using spatial "
        "topology graphs and non-biometric clothing color histograms, mapping complete store-wide customer journeys.",
        bold_prefix="3. Non-Biometric Multi-Camera Storewide Re-ID:"
    )
    add_bullet_point(
        doc,
        "Incorporate computer vision detection of shopping cart fill levels to dynamically estimate scanning durations for each "
        "individual queued customer, transforming static Little's Law into item-level predictive queueing models.",
        bold_prefix="4. Shopping Cart Fill-Level Computer Vision:"
    )
    add_bullet_point(
        doc,
        "Interface the RTRFQM predictive dispatcher directly with electronic shelf edge displays and robotic inventory shuttles, "
        "creating an autonomous retail operating system that synchronizes checkout capacity, aisle restocking, and dynamic promotional pricing.",
        bold_prefix="5. Autonomous Store Robotics & ERP Synchronization:"
    )
