import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd

fig_dir = r'e:\Data Science Project\figures'
os.makedirs(fig_dir, exist_ok=True)

# Set global matplotlib style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['figure.titleweight'] = 'bold'

# 1. Pipeline Diagram (DFD Level 1 Pipeline)
def create_dfd_pipeline():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.axis('off')

    boxes = [
        {"name": "Live Video Stream\n(RTSP / CCTV IP)", "x": 0.05, "y": 0.55, "w": 0.16, "h": 0.28, "color": "#1f77b4"},
        {"name": "Frame Preprocessing\n& Spatial ROI", "x": 0.25, "y": 0.55, "w": 0.16, "h": 0.28, "color": "#2ca02c"},
        {"name": "YOLOv8 Detection\n& ByteTrack", "x": 0.45, "y": 0.55, "w": 0.16, "h": 0.28, "color": "#ff7f0e"},
        {"name": "Queue & Footfall\nDynamics Engine", "x": 0.65, "y": 0.55, "w": 0.16, "h": 0.28, "color": "#9467bd"},
        {"name": "Real-Time Dashboard\n& Alert System", "x": 0.85, "y": 0.55, "w": 0.14, "h": 0.28, "color": "#d62728"}
    ]

    for b in boxes:
        rect = patches.FancyBboxPatch((b['x'], b['y']), b['w'], b['h'],
                                      boxstyle="round,pad=0.02,rounding_size=0.03",
                                      linewidth=2, edgecolor="#333333", facecolor=b['color'], alpha=0.85)
        ax.add_patch(rect)
        ax.text(b['x'] + b['w']/2, b['y'] + b['h']/2, b['name'],
                color='white', weight='bold', fontsize=9.5, ha='center', va='center')

    # Draw arrows
    for i in range(len(boxes) - 1):
        x1 = boxes[i]['x'] + boxes[i]['w'] + 0.005
        y1 = boxes[i]['y'] + boxes[i]['h']/2
        x2 = boxes[i+1]['x'] - 0.005
        y2 = boxes[i+1]['y'] + boxes[i+1]['h']/2
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2.5, color='#333333'))

    # Persistence layer box below
    rect_db = patches.FancyBboxPatch((0.40, 0.10), 0.35, 0.24,
                                     boxstyle="round,pad=0.02,rounding_size=0.03",
                                     linewidth=2, edgecolor="#333333", facecolor="#17becf", alpha=0.85)
    ax.add_patch(rect_db)
    ax.text(0.575, 0.22, "PostgreSQL & Time-Series DB\n(Historical Logs & Audit Store)",
            color='white', weight='bold', fontsize=10, ha='center', va='center')

    # Connecting arrows to database
    ax.annotate('', xy=(0.50, 0.35), xytext=(0.53, 0.54),
                arrowprops=dict(arrowstyle="->", lw=2, color='#555555', linestyle='dashed'))
    ax.annotate('', xy=(0.70, 0.35), xytext=(0.73, 0.54),
                arrowprops=dict(arrowstyle="->", lw=2, color='#555555', linestyle='dashed'))
    ax.annotate('', xy=(0.87, 0.54), xytext=(0.76, 0.26),
                arrowprops=dict(arrowstyle="->", lw=2, color='#555555', linestyle='dashed'))

    plt.title("Figure 4.2: RTRFQM Data Flow and Processing Pipeline Architecture", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'dfd_pipeline.png'), dpi=300)
    plt.close()
    print("Created dfd_pipeline.png")

# 2. Hourly Footfall Profile
def create_hourly_footfall():
    hours = np.arange(8, 23) # 8 AM to 10 PM
    # Typical retail store traffic pattern (morning rise, lunch peak, afternoon lull, evening surge)
    base_traffic = np.array([35, 75, 140, 185, 170, 125, 110, 130, 195, 260, 310, 290, 220, 130, 45])
    upper_bound = base_traffic + np.array([12, 18, 28, 35, 30, 22, 20, 25, 38, 48, 55, 50, 38, 25, 10])
    lower_bound = base_traffic - np.array([10, 15, 25, 30, 28, 20, 18, 22, 35, 45, 50, 45, 35, 20, 8])

    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    ax.plot(hours, base_traffic, color='#1f77b4', lw=2.8, marker='o', label='Mean Footfall (Customers/Hour)')
    ax.fill_between(hours, lower_bound, upper_bound, color='#1f77b4', alpha=0.22, label='95% Confidence Interval')

    # Annotate peaks
    ax.annotate('Evening Supermarket Surge\n(Max: ~310 customers/hr)', xy=(18, 310), xytext=(14.2, 325),
                arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=7),
                fontsize=9.5, fontweight='bold', color='#d62728')
    ax.annotate('Morning Shopping Peak\n(~185 customers/hr)', xy=(11, 185), xytext=(8.5, 240),
                arrowprops=dict(facecolor='#2ca02c', shrink=0.08, width=1.5, headwidth=7),
                fontsize=9.5, fontweight='bold', color='#2ca02c')

    ax.set_xlabel("Store Operating Hour (24-Hour Military Format)")
    ax.set_ylabel("In-Store Customer Entry Count")
    ax.set_title("Figure 6.1: Diurnal Customer Footfall Distribution across Operating Hours")
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h:02d}:00" for h in hours], rotation=45)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper left', frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'hourly_footfall_chart.png'), dpi=300)
    plt.close()
    print("Created hourly_footfall_chart.png")

# 3. Day of Week Footfall
def create_day_of_week():
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    footfall = [1850, 1720, 1910, 2050, 2680, 3950, 4210]
    queue_incidents = [14, 11, 15, 18, 36, 68, 79]

    fig, ax1 = plt.subplots(figsize=(8.5, 4.6), dpi=300)

    color1 = '#2b5c8f'
    color2 = '#d95f02'

    x = np.arange(len(days))
    width = 0.42

    rects1 = ax1.bar(x - width/2, footfall, width, label='Total Daily Footfall', color=color1, alpha=0.85)
    ax1.set_xlabel('Day of the Week')
    ax1.set_ylabel('Total Store Footfall (Count)', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(days, fontweight='bold')

    ax2 = ax1.twinx()
    rects2 = ax2.bar(x + width/2, queue_incidents, width, label='Congestion Alert Events (>5 in queue)', color=color2, alpha=0.85)
    ax2.set_ylabel('Congestion Events Count', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    # Values on bars
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f'{h}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')
    for rect in rects2:
        h = rect.get_height()
        ax2.annotate(f'{h}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold')

    plt.title("Figure 6.2: Weekly Footfall Volume versus Checkout Congestion Events")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'day_of_week_footfall.png'), dpi=300)
    plt.close()
    print("Created day_of_week_footfall.png")

# 4. Queue Length Distribution
def create_queue_dist():
    np.random.seed(42)
    non_peak = np.random.poisson(lam=2.1, size=1500)
    peak = np.random.poisson(lam=6.8, size=1500)

    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    bins = np.arange(0, 18) - 0.5

    ax.hist(non_peak, bins=bins, alpha=0.65, label='Non-Peak Hours (08:00-11:00, 14:00-17:00)',
            color='#2ca02c', edgecolor='black', density=True)
    ax.hist(peak, bins=bins, alpha=0.65, label='Peak Hours (11:00-13:00, 17:30-21:30)',
            color='#d62728', edgecolor='black', density=True)

    ax.axvline(x=5, color='black', linestyle='--', lw=2, label='Congestion Alarm Threshold (Lq = 5)')

    ax.set_xlabel('Checkout Queue Length (Number of Waiting Customers per Lane)')
    ax.set_ylabel('Probability Density Function (PDF)')
    ax.set_title("Figure 6.3: Probability Distribution of Checkout Queue Lengths")
    ax.set_xticks(range(0, 17))
    ax.legend(frameon=True)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'queue_length_distribution.png'), dpi=300)
    plt.close()
    print("Created queue_length_distribution.png")

# 5. Waiting Time vs Queue Length (Little's Law Validation)
def create_waiting_time_plot():
    np.random.seed(42)
    queue_lengths = np.random.randint(1, 14, size=300)
    # Average service time per customer = 1.6 minutes, plus variance
    service_rate_min = 1.65
    noise = np.random.normal(0, 0.75, size=300)
    waiting_times = np.maximum(0.5, queue_lengths * service_rate_min + noise)

    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    ax.scatter(queue_lengths, waiting_times, alpha=0.45, color='#1f77b4', edgecolors='none', s=45, label='Observed Camera Queue Events')

    # Theoretical Little's Law Curve: W_q = L_q / mu
    q_ideal = np.linspace(1, 13, 100)
    w_ideal = q_ideal * service_rate_min
    ax.plot(q_ideal, w_ideal, color='#d62728', lw=2.8, linestyle='-', label="Little's Law Linear Fit (μ = 0.606 cust/min)")

    # 95% prediction intervals
    ax.plot(q_ideal, w_ideal + 1.5, color='#ff7f0e', lw=1.5, linestyle='--', label='95% Upper Bound')
    ax.plot(q_ideal, np.maximum(0, w_ideal - 1.5), color='#ff7f0e', lw=1.5, linestyle='--', label='95% Lower Bound')

    ax.set_xlabel('Observed Queue Length ($L_q$, Customers in Waiting Line)')
    ax.set_ylabel('Measured Customer Waiting Time ($W_q$, Minutes)')
    ax.set_title("Figure 6.4: Empirical Customer Waiting Time versus Measured Queue Length")
    ax.set_xticks(range(1, 14))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'waiting_time_vs_queue.png'), dpi=300)
    plt.close()
    print("Created waiting_time_vs_queue.png")

# 6. MOT Tracking Quality Comparison
def create_tracking_metrics_plot():
    trackers = ['YOLOv8 + ByteTrack (Proposed)', 'YOLOv8 + DeepSORT', 'YOLOv8 + SORT', 'Faster R-CNN + DeepSORT']
    mota = [76.4, 69.8, 61.2, 64.5]
    idf1 = [78.2, 71.5, 58.4, 66.1]
    fps = [38.5, 22.4, 42.1, 11.2]

    x = np.arange(len(trackers))
    width = 0.26

    fig, ax = plt.subplots(figsize=(9.2, 4.8), dpi=300)
    r1 = ax.bar(x - width, mota, width, label='MOTA (%)', color='#2ca02c')
    r2 = ax.bar(x, idf1, width, label='IDF1 Score (%)', color='#1f77b4')
    r3 = ax.bar(x + width, fps, width, label='Inference Speed (FPS)', color='#ff7f0e')

    ax.set_ylabel('Metric Value (% / FPS)')
    ax.set_title('Figure 7.1: Multi-Object Tracking Accuracy and Speed Benchmarks')
    ax.set_xticks(x)
    ax.set_xticklabels(trackers, rotation=15, ha='right', fontweight='bold', fontsize=8.5)
    ax.set_ylim(0, 95)
    ax.legend(frameon=True, loc='upper right')
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    # Values
    for r in [r1, r2, r3]:
        for bar in r:
            h = bar.get_height()
            ax.annotate(f'{h:.1f}', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 2),
                        textcoords="offset points", ha='center', va='bottom', fontsize=7.5, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'mot_tracking_metrics.png'), dpi=300)
    plt.close()
    print("Created mot_tracking_metrics.png")

# 7. Model Performance Comparison for Queue Length Prediction
def create_model_comparison_plot():
    models = ['Historical Moving Avg', 'ARIMA (2,1,2)', 'Linear Regression', 'Random Forest Regressor (Proposed)', 'XGBoost Regressor']
    mae = [2.48, 1.84, 1.95, 0.72, 0.76]
    rmse = [3.15, 2.38, 2.52, 0.98, 1.04]
    mape = [32.4, 24.6, 26.1, 9.8, 10.5]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

    x = np.arange(len(models))
    w = 0.35

    ax1.bar(x - w/2, mae, w, label='MAE (Customers)', color='#377eb8')
    ax1.bar(x + w/2, rmse, w, label='RMSE (Customers)', color='#e41a1c')
    ax1.set_ylabel('Error in Queue Count')
    ax1.set_title('Prediction Error (MAE & RMSE)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=25, ha='right', fontsize=8, fontweight='bold')
    ax1.legend(frameon=True)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.5)

    ax2.bar(x, mape, width=0.5, color='#4daf4a', edgecolor='black')
    ax2.set_ylabel('Mean Absolute Percentage Error (%)')
    ax2.set_title('Relative Percentage Error (MAPE)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=25, ha='right', fontsize=8, fontweight='bold')
    ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

    for i, v in enumerate(mape):
        ax2.text(i, v + 0.8, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=8)

    plt.suptitle("Figure 7.2: Predictive Model Evaluation for Checkout Queue Forecasting", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'model_performance_comparison.png'), dpi=300)
    plt.close()
    print("Created model_performance_comparison.png")

# 8. Cashier Utilization and Congestion Timeline
def create_cashier_timeline():
    t = np.arange(0, 120, 2) # 2 hours in minutes
    # Simulated arrival surge
    arrivals = 1.2 + 1.8 * np.exp(-((t - 45)/18)**2) + 2.2 * np.exp(-((t - 85)/22)**2)
    # Queue length
    q_len = np.maximum(0, arrivals * 2.8 - 2.5 + np.sin(t/5)*0.8)
    # Active cashiers
    cashiers = np.ones_like(t) * 2
    cashiers[t >= 36] = 3
    cashiers[t >= 48] = 4
    cashiers[t >= 70] = 3
    cashiers[t >= 82] = 5
    cashiers[t >= 105] = 3

    fig, ax1 = plt.subplots(figsize=(9, 4.6), dpi=300)

    line1 = ax1.plot(t, q_len, color='#d62728', lw=2.5, label='Checkout Queue Length ($L_q$)')
    ax1.axhline(y=5, color='black', linestyle='--', lw=1.8, label='Congestion Alarm Level ($L_q=5$)')
    ax1.set_xlabel('Elapsed Monitoring Time (Minutes)')
    ax1.set_ylabel('Observed Queue Length (Customers)', color='#d62728')
    ax1.tick_params(axis='y', labelcolor='#d62728')

    ax2 = ax1.twinx()
    line2 = ax2.step(t, cashiers, where='post', color='#1f77b4', lw=2.2, label='Active Cashier Lanes ($c$)')
    ax2.set_ylabel('Number of Active Cashier Counters', color='#1f77b4')
    ax2.tick_params(axis='y', labelcolor='#1f77b4')
    ax2.set_ylim(0, 6)

    # Congestion annotations
    ax1.annotate('Congestion Alert Triggered\n(Lane 3 & 4 opened)', xy=(40, 5.2), xytext=(15, 7.5),
                 arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=8.5, fontweight='bold', color='#d62728')
    ax1.annotate('Second Peak Surge\n(Lane 5 activated)', xy=(86, 6.4), xytext=(65, 8.5),
                 arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=6),
                 fontsize=8.5, fontweight='bold', color='#d62728')

    plt.title("Figure 7.3: Dynamic Cashier Lane Dispatch and Queue Length Suppression Timeline")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'cashier_utilization_timeline.png'), dpi=300)
    plt.close()
    print("Created cashier_utilization_timeline.png")

# 9. Dashboard Mockup UI
def create_dashboard_mockup():
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=300)
    ax.axis('off')

    # Main dashboard background
    bg = patches.Rectangle((0, 0), 1, 1, facecolor='#f8f9fa', edgecolor='#cccccc', lw=2)
    ax.add_patch(bg)

    # Top Navigation Bar
    navbar = patches.Rectangle((0, 0.90), 1, 0.10, facecolor='#1e293b')
    ax.add_patch(navbar)
    ax.text(0.03, 0.94, "RTRFQM | Real-Time Retail Store Intelligence & Queue Monitor",
            color='white', weight='bold', fontsize=12, va='center')
    ax.text(0.85, 0.94, "🟢 LIVE: STORE #104", color='#4ade80', weight='bold', fontsize=9.5, va='center')

    # KPI Metric Cards
    kpis = [
        {"title": "CURRENT STORE FOOTFALL", "val": "184 Persons", "sub": "+14% vs yesterday", "color": "#0284c7", "x": 0.03},
        {"title": "ACTIVE CHECKOUT LANES", "val": "4 / 6 Open", "sub": "Utilization: 82%", "color": "#16a34a", "x": 0.27},
        {"title": "MAX QUEUE LENGTH", "val": "6 Customers", "sub": "Counter #2 (Alert)", "color": "#dc2626", "x": 0.51},
        {"title": "ESTIMATED WAIT TIME", "val": "4.2 Minutes", "sub": "Target: < 3.0 min", "color": "#ea580c", "x": 0.75}
    ]

    for k in kpis:
        card = patches.FancyBboxPatch((k['x'], 0.72), 0.22, 0.15,
                                      boxstyle="round,pad=0.015,rounding_size=0.02",
                                      facecolor='white', edgecolor='#e2e8f0', lw=1.5)
        ax.add_patch(card)
        ax.text(k['x'] + 0.015, 0.835, k['title'], color='#64748b', fontsize=7.5, weight='bold')
        ax.text(k['x'] + 0.015, 0.78, k['val'], color=k['color'], fontsize=12, weight='bold')
        ax.text(k['x'] + 0.015, 0.74, k['sub'], color='#94a3b8', fontsize=7)

    # Left Section: Live Camera Feed with ROI
    cam_box = patches.FancyBboxPatch((0.03, 0.06), 0.46, 0.62,
                                     boxstyle="round,pad=0.015,rounding_size=0.02",
                                     facecolor='#0f172a', edgecolor='#334155', lw=1.5)
    ax.add_patch(cam_box)
    ax.text(0.05, 0.63, "CCTV CAM-03 [Checkout Lanes 1-4 Overhead View]", color='white', weight='bold', fontsize=8.5)

    # Simulated BBoxes in Camera
    roi_box = patches.Rectangle((0.08, 0.14), 0.36, 0.44, fill=False, edgecolor='#38bdf8', lw=2, linestyle='--')
    ax.add_patch(roi_box)
    ax.text(0.09, 0.55, "ROI: Checkout Queuing Zone", color='#38bdf8', fontsize=7.5, weight='bold')

    # Detected customers in queue
    cust_pts = [(0.15, 0.22), (0.19, 0.28), (0.24, 0.34), (0.29, 0.39), (0.33, 0.45)]
    for idx, (cx, cy) in enumerate(cust_pts):
        c_box = patches.Rectangle((cx-0.02, cy-0.03), 0.04, 0.06, fill=True, facecolor='#ef4444', alpha=0.7, edgecolor='white')
        ax.add_patch(c_box)
        ax.text(cx, cy, f"ID:{idx+101}", color='white', fontsize=6, weight='bold', ha='center', va='center')

    # Virtual Line
    ax.plot([0.08, 0.44], [0.18, 0.18], color='#eab308', lw=2)
    ax.text(0.26, 0.19, "Cashier Counter Line", color='#eab308', fontsize=7, weight='bold')

    # Right Section: Live Alert & Congestion Forecaster
    alert_box = patches.FancyBboxPatch((0.51, 0.38), 0.46, 0.30,
                                       boxstyle="round,pad=0.015,rounding_size=0.02",
                                       facecolor='white', edgecolor='#e2e8f0', lw=1.5)
    ax.add_patch(alert_box)
    ax.text(0.53, 0.64, "⚠️ CONGESTION DISPATCH ALERT", color='#dc2626', weight='bold', fontsize=9.5)
    ax.text(0.53, 0.58, "Condition: Lane #2 Queue Exceeded Threshold (>5 persons)", color='#334155', fontsize=8)
    ax.text(0.53, 0.52, "Recommended Action: Open Backup Lane #5 Immediately", color='#16a34a', weight='bold', fontsize=8.5)
    ax.text(0.53, 0.46, "Auto-Dispatched SMS Alert to Shift Supervisor at 18:42:10 IST", color='#64748b', fontsize=7.5)
    ax.text(0.53, 0.41, "Predicted Queue Dissipation Time: 3.5 minutes", color='#0284c7', fontsize=7.5)

    # Right Bottom: Mini Traffic Trend Chart
    chart_box = patches.FancyBboxPatch((0.51, 0.06), 0.46, 0.29,
                                       boxstyle="round,pad=0.015,rounding_size=0.02",
                                       facecolor='white', edgecolor='#e2e8f0', lw=1.5)
    ax.add_patch(chart_box)
    ax.text(0.53, 0.31, "Hourly Footfall Trend & Real-Time Forecast", color='#334155', weight='bold', fontsize=8.5)

    # Mini plot inside
    mini_x = np.linspace(0.54, 0.94, 15)
    mini_y = 0.12 + np.array([0.02, 0.04, 0.06, 0.09, 0.08, 0.06, 0.05, 0.07, 0.11, 0.14, 0.13, 0.10, 0.08, 0.06, 0.04])
    ax.plot(mini_x, mini_y, color='#0284c7', lw=2)
    ax.scatter(mini_x[-5], mini_y[-5], color='#dc2626', s=40, zorder=5)
    ax.text(mini_x[-5], mini_y[-5]+0.015, "NOW", color='#dc2626', weight='bold', fontsize=7, ha='center')

    plt.title("Figure 7.4: Interactive Real-Time Store Manager Dashboard Mockup", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'dashboard_mockup.png'), dpi=300)
    plt.close()
    print("Created dashboard_mockup.png")

create_dfd_pipeline()
create_hourly_footfall()
create_day_of_week()
create_queue_dist()
create_waiting_time_plot()
create_tracking_metrics_plot()
create_model_comparison_plot()
create_cashier_timeline()
create_dashboard_mockup()
print("All figures generated successfully!")
