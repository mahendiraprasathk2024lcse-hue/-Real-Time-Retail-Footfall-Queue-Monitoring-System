# report_builder/chapter2.py
"""
Chapter 2: Literature Survey
Comprehensive academic literature review covering:
2.1 Sensor-Based and Traditional Footfall Counting
2.2 Evolution of Vision-Based Object Detection
2.3 Multi-Object Tracking and Identity Association
2.4 Classical Queue Modeling and Waiting Time Estimation
2.5 Predictive Analytics and Retail Demand Forecasting
2.6 Comparative Literature Review Summary Table
2.7 Research Gaps Addressed by Proposed System
"""

from docx.shared import Pt
from report_builder.styles import (
    add_chapter_heading,
    add_section_heading,
    add_body_paragraph,
    add_bullet_point,
    add_styled_table,
    add_callout_box
)


def build_chapter2(doc):
    """Builds Chapter 2: Literature Survey."""
    add_chapter_heading(doc, 2, "Literature Survey")

    add_section_heading(doc, "2.1", "Sensor-Based and Traditional Footfall Counting", level=2)
    add_body_paragraph(
        doc,
        "The quantification of human footfall in commercial and public infrastructure has been investigated for "
        "several decades. Early retail counting architectures relied predominantly on physical, hardware-based "
        "sensing modalities. Prominent among these were horizontal infrared (IR) break-beam sensors mounted at store "
        "entrances. While mechanically simple and inexpensive, break-beam sensors register an entry count each time an "
        "invisible optical beam is occluded. Consequently, these systems suffer from severe counting inaccuracies when "
        "multiple individuals enter abreast, when children enter accompanied by adults, or when shoppers pause at the "
        "threshold, frequently resulting in counting errors exceeding 25% to 35% in high-density retail environments."
    )
    add_body_paragraph(
        doc,
        "To mitigate optical occlusion, subsequent research investigated pressure-sensitive floor mats and overhead "
        "thermal sensors. Pressure mats utilize piezoelectric or resistive arrays to detect downward foot pressure. "
        "However, they suffer from high mechanical wear, complex flooring installation logistics, and an inability to "
        "discern directional crossing vectoring. Overhead thermal sensors detect human body heat radiation against "
        "ambient floor temperatures. While thermal sensors resolve optical lighting variations and preserve visual "
        "privacy, their coarse spatial resolution prevents accurate identity tracking in crowded queues, and their "
        "accuracy degrades significantly during warm summer seasons when ambient store temperatures approach human body heat."
    )
    add_body_paragraph(
        doc,
        "With the proliferation of personal mobile computing devices, radio-frequency (RF) sensing techniques gained "
        "temporary industrial traction. In particular, Wi-Fi and Bluetooth Low Energy (BLE) probe-request sniffing "
        "systems capture Media Access Control (MAC) addresses broadcast by smartphones searching for local networks. "
        "Although RF sensing facilitates broad spatial tracking across an entire retail store, modern smartphone operating "
        "systems (iOS and Android) have implemented randomized MAC rotation protocols to protect user privacy. "
        "Furthermore, shoppers without enabled Wi-Fi or smartphones remain completely invisible to RF sensors, introducing "
        "unpredictable sampling biases that invalidate rigorous queue counting."
    )

    add_section_heading(doc, "2.2", "Evolution of Vision-Based Object Detection", level=2)
    add_body_paragraph(
        doc,
        "The limitations of dedicated physical sensors catalyzed the rapid adoption of computer vision techniques for "
        "retail traffic monitoring. Early vision systems relied on handcrafted visual features, notably Haar cascades, "
        "Histogram of Oriented Gradients (HOG) combined with Support Vector Machines (SVM), and background subtraction "
        "algorithms (such as Gaussian Mixture Models). These classical techniques exhibited extreme vulnerability to "
        "environmental noise, camera jitter, dynamic shadows, clothing color variations, and sudden changes in ambient store lighting."
    )
    add_body_paragraph(
        doc,
        "The paradigm shifted fundamentally with the emergence of deep convolutional neural networks (CNNs). Deep learning "
        "object detection architectures bifurcated into two primary paradigms: two-stage detectors and one-stage detectors. "
        "Two-stage architectures, exemplified by Faster R-CNN (Ren et al., 2015), utilize a Region Proposal Network (RPN) "
        "to generate candidate object regions, followed by dedicated classification and bounding box regression subnetworks. "
        "While two-stage detectors achieve high localization precision, their multi-step computational pipeline limits "
        "inference throughput to 8–14 frames per second (FPS) on mid-tier graphics hardware, rendering them impractical for "
        "real-time multi-camera retail surveillance."
    )
    add_body_paragraph(
        doc,
        "To overcome latency bottlenecks, one-stage detectors revolutionized real-time computer vision by framing object "
        "detection as a unified regression problem. The You Only Look Once (YOLO) framework, pioneered by Redmon et al. "
        "(2016) and subsequently refined through architectures such as YOLOv4 (Bochkovskiy et al., 2020), YOLOv5, and "
        "YOLOv7, directly predicts bounding box coordinates and class probabilities across a dense spatial grid in a single "
        "forward pass. The latest iteration, YOLOv8 developed by Ultralytics (2023), introduces an anchor-free split-head "
        "architecture that decouples objectness, classification, and regression tasks. By replacing traditional anchor box "
        "matching with Task-Aligned Assignment and employing Distribution Focal Loss (DFL) combined with Complete "
        "Intersection over Union (CIoU) loss, YOLOv8 achieves state-of-the-art mean Average Precision (mAP) while sustaining "
        "inference rates exceeding 45 FPS on edge GPU hardware. This makes YOLOv8 the optimal candidate for retail "
        "surveillance ingestion."
    )

    add_section_heading(doc, "2.3", "Multi-Object Tracking and Identity Association", level=2)
    add_body_paragraph(
        doc,
        "While object detection localizes human targets within individual video frames, operational retail monitoring "
        "mandates temporal continuity—the ability to recognize that a bounding box in frame t represents the identical "
        "individual observed in frame t-1. The prevailing academic paradigm for multi-camera video analytics is "
        "Tracking-by-Detection (TbD), which decomposes the problem into per-frame detection followed by inter-frame data association."
    )
    add_body_paragraph(
        doc,
        "The foundational Simple Online and Realtime Tracking (SORT) algorithm (Bewley et al., 2016) utilizes a linear "
        "constant-velocity Kalman filter to project target bounding boxes into future frames and solves the bipartite "
        "matching problem using the Hungarian algorithm based solely on spatial Intersection over Union (IoU) overlap. "
        "Although SORT operates at over 60 FPS, its reliance purely on spatial overlap causes frequent identity switches "
        "(ID switches) whenever people cross paths or undergo brief visual occlusions."
    )
    add_body_paragraph(
        doc,
        "To address SORT's vulnerability to occlusions, Wojke et al. (2017) introduced DeepSORT, integrating a deep CNN "
        "trained on person re-identification (Re-ID) to extract 128-dimensional appearance feature vectors for each target. "
        "Association is then performed using a cost matrix combining Mahalanobis spatial distance and cosine appearance distance. "
        "However, extracting deep visual embeddings for dozens of people in every frame introduces substantial computational "
        "latency, dropping tracking throughput to 18–22 FPS on edge devices. Furthermore, storing visual feature embeddings "
        "approaches biometric profiling boundaries, raising sensitive data governance concerns in consumer retail environments."
    )
    add_body_paragraph(
        doc,
        "A breakthrough resolution was achieved with ByteTrack (Zhang et al., 2022). ByteTrack challenges the standard "
        "convention of discarding low-confidence detection boxes (e.g., detections with confidence scores below 0.5). "
        "Recognizing that true occluded persons frequently exhibit lower confidence scores rather than complete absence, "
        "ByteTrack implements a two-stage association pipeline. First, high-confidence detections are matched with existing "
        "tracks. Second, remaining unmatched tracks are associated with low-confidence detections using spatial IoU. By "
        "eliminating deep appearance feature extractors and relying on enhanced motion modeling, ByteTrack establishes "
        "superior Multi-Object Tracking Accuracy (MOTA) and Identification F1-scores (IDF1) while executing at over 38 FPS, "
        "providing the ideal foundation for real-time retail queue tracking."
    )

    add_section_heading(doc, "2.4", "Classical Queue Modeling and Waiting Time Estimation", level=2)
    add_body_paragraph(
        doc,
        "Independently of computer vision, queueing theory has provided the mathematical foundation for analyzing retail "
        "service bottlenecks since the seminal contributions of A.K. Erlang in telephony. In classical Kendall notation, "
        "retail checkout lanes are commonly modeled as multi-server queueing systems denoted as M/M/c or M/G/c, where "
        "customer arrivals follow a Poisson process with mean rate λ, service times follow an exponential or general distribution "
        "with mean rate μ, and c represents the number of active parallel checkout counters."
    )
    add_body_paragraph(
        doc,
        "The cornerstone equation linking queue volume to customer experience is Little's Law (Little, 1961), which proves "
        "that under stationary operating conditions, the long-term average number of customers waiting in a queue (Lq) is "
        "strictly equal to the product of the average customer arrival rate (λ) and the average waiting time spent in queue (Wq):"
    )
    add_body_paragraph(
        doc,
        "Lq = λ * Wq    or equivalently,    Wq = Lq / λ = Lq / (c * μ)",
        italic_prefix="Mathematical Expression:"
    )
    add_body_paragraph(
        doc,
        "While classical queueing models provide elegant theoretical formulations, their practical application in real-world "
        "retail stores has historically been hindered by the absence of continuous, accurate parameter estimation. Store "
        "supervisors rarely knew the instantaneous arrival rate (λ) or real-time queue length (Lq), rendering Little's Law a "
        "retrospective auditing formula rather than an active operational control mechanism. Integrating real-time computer "
        "vision with Little's Law operationalizes these equations into live telemetry streams."
    )

    add_section_heading(doc, "2.5", "Predictive Analytics and Retail Demand Forecasting", level=2)
    add_body_paragraph(
        doc,
        "Real-time monitoring informs managers of current store conditions; however, optimal checkout staffing requires "
        "proactive anticipation. In retail operations, cashier re-allocation incurs a physical transition latency of 5 to "
        "15 minutes (as staff conclude stock-shelving duties and sign into register terminals). Consequently, alerting "
        "managers only after a queue has formed results in unavoidable customer delays."
    )
    add_body_paragraph(
        doc,
        "Prior academic research has explored diverse predictive methodologies for retail demand forecasting. Classical "
        "univariate statistical models, such as Autoregressive Integrated Moving Average (ARIMA) and Seasonal ARIMA (SARIMA), "
        "capture linear temporal trends and diurnal periodicities but struggle to adapt to non-linear surges driven by "
        "abrupt weather shifts or promotional campaigns. Deep learning architectures, such as Long Short-Term Memory (LSTM) "
        "networks and Temporal Convolutional Networks (TCN), model complex temporal dependencies effectively but require "
        "enormous training corpora, demand high computational overhead, and behave as opaque black-box systems lacking "
        "operational interpretability."
    )
    add_body_paragraph(
        doc,
        "Supervised ensemble tree models—specifically Random Forest Regressors and Gradient Boosted Trees (XGBoost)—have "
        "emerged as the most effective predictive paradigm for operational tabular telemetry. By engineering lag features "
        "(e.g., footfall counts over preceding 15, 30, and 60 minutes), rolling rate-of-change indicators, day-of-week "
        "dummies, and active cashier ratios, Random Forest models deliver high prediction accuracy, rapid retraining cycles, "
        "robustness against overfitting, and transparent feature importance metrics vital for managerial trust."
    )

    add_section_heading(doc, "2.6", "Comparative Literature Review Summary", level=2)
    add_body_paragraph(
        doc,
        "To provide a systematic comparative synthesis of the existing body of knowledge, Table 2.1 analyzes landmark "
        "contributions across sensor-based systems, vision-based detection, multi-object tracking, queueing formulations, "
        "and retail analytics frameworks, identifying the core methodology, performance metrics, and inherent limitations of each."
    )

    lit_headers = [
        "Author / Reference",
        "Primary Domain / Scope",
        "Methodology & Tools",
        "Key Performance Metrics",
        "Identified Limitations & Gaps"
    ]

    lit_data = [
        [
            "Redmon et al. (2016)\n[YOLO Foundation]",
            "Real-Time Object Detection",
            "Single-stage CNN regression on full image grid",
            "45 FPS inference, 63.4% mAP on Pascal VOC",
            "Lower localization accuracy for dense, small occluded objects in crowds."
        ],
        [
            "Ren et al. (2015)\n[Faster R-CNN]",
            "Two-Stage Object Detection",
            "Region Proposal Network (RPN) + Fast R-CNN subnets",
            "73.2% mAP on VOC 2007, high spatial localization",
            "High computational latency (8-12 FPS), unsuitable for multi-camera edge deployment."
        ],
        [
            "Bewley et al. (2016)\n[SORT]",
            "Multi-Object Tracking",
            "Kalman filter state estimation + Hungarian IoU matching",
            "60+ FPS throughput, 59.8% MOTA benchmark",
            "High frequency of ID switches during occlusions; no appearance or confidence handling."
        ],
        [
            "Wojke et al. (2017)\n[DeepSORT]",
            "Multi-Object Tracking with Re-ID",
            "Kalman filter + 128-dim deep CNN appearance embedding",
            "61.4% MOTA, significant ID switch suppression",
            "Computational bottleneck (~20 FPS); stores visual appearance embeddings, raising privacy issues."
        ],
        [
            "Zhang et al. (2022)\n[ByteTrack]",
            "Two-Stage Detection Association",
            "Associating high & low score detection boxes via IoU",
            "80.3% MOTA, 77.3% IDF1, 38+ FPS on MOT17",
            "Focuses purely on tracking; does not integrate spatial ROI queue analysis or predictive engines."
        ],
        [
            "Little (1961) /\nGross et al. (2008)",
            "Classical Queueing Theory",
            "Mathematical formulation: Lq = λ * Wq (M/M/c systems)",
            "Exact steady-state mathematical queue proofs",
            "Formulations assume stationary arrival rates; lack integration with real-time video telemetry."
        ],
        [
            "Box & Jenkins (2015)\n[ARIMA Modeling]",
            "Time-Series Forecasting",
            "Linear autoregressive integrated moving average",
            "Established statistical baseline for linear patterns",
            "Fails to capture sudden non-linear footfall surges, external promotions, or multi-queue interactions."
        ],
        [
            "Brebels et al. (2021)\n[Retail Queue Psych]",
            "Customer Behavior & Waiting",
            "Empirical consumer surveys & POS checkout audits",
            "Quantified cart abandonment correlation with wait time",
            "Manual auditing methodology; provides no automated vision or real-time alert system."
        ]
    ]

    add_styled_table(
        doc,
        headers=lit_headers,
        data=lit_data,
        col_widths=[1.3, 1.2, 1.5, 1.3, 1.5],
        caption="Comprehensive Literature Review and Methodological Comparison of Retail Analytics Technologies",
        table_num="2.1"
    )

    add_section_heading(doc, "2.7", "Research Gaps Addressed by Proposed System", level=2)
    add_body_paragraph(
        doc,
        "A critical synthesis of the reviewed literature reveals four prominent research and architectural gaps that "
        "severely limit the operational efficacy of existing commercial and academic retail monitoring systems:"
    )

    add_callout_box(
        doc,
        "1. The Architectural Fragmentation Gap: Computer vision tracking and queueing theory have evolved in academic "
        "silos. Prior works either propose vision models without queueing models, or analyze queue equations using simulated "
        "random arrival variables without real-world camera inputs.\n\n"
        "2. The Edge Inference Latency Gap: Existing tracking frameworks with re-identification features (e.g., DeepSORT) "
        "incur substantial deep feature extraction overhead, preventing real-time execution across multiple checkout cameras "
        "without expensive enterprise server infrastructure.\n\n"
        "3. The Proactive Predictive Gap: Commercial retail video analytics tools focus almost exclusively on descriptive, "
        "retrospective heatmaps and historical charts. None integrate real-time queue forecasting to alert staff before "
        "congestion thresholds are breached.\n\n"
        "4. The Consumer Privacy and Biometrics Gap: Emerging commercial systems frequently employ facial recognition or "
        "demographic profiling, sparking intense regulatory penalties under GDPR and consumer pushback. An enterprise solution "
        "must guarantee non-biometric, fully anonymized tracking.",
        title="Summary of Core Research Gaps Addressed by RTRFQM"
    )

    add_body_paragraph(
        doc,
        "The RTRFQM framework developed in this project directly eliminates these gaps by unifying lightweight, high-precision "
        "YOLOv8 detection with ByteTrack tracking, operationalizing Little's Law with real-time spatial ROI telemetry, and "
        "coupling live observations with an interpretable Random Forest forecasting engine—all while maintaining strict "
        "biometric anonymization by design."
    )
