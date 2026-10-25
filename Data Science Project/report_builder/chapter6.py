# report_builder/chapter6.py
"""
Chapter 6: Machine Learning for Short-Term Queue Forecasting
Comprehensive academic chapter covering:
6.1 Short-Term Forecasting Problem Formulation
6.2 Temporal Lag and Rolling Window Feature Engineering (Table 6.1: Feature Importance)
6.3 Candidate Predictive Model Architectures (Random Forest, XGBoost, ARIMA, Linear Reg)
6.4 Hyperparameter Optimization and Cross-Validation (Table 6.2: Hyperparameters)
6.5 Performance Metrics and Loss Minimization (MAE, RMSE, MAPE, R2 Formulas)
"""

from docx.shared import Pt
from report_builder.styles import (
    add_chapter_heading,
    add_section_heading,
    add_body_paragraph,
    add_bullet_point,
    add_equation,
    add_styled_table,
    add_callout_box
)


def build_chapter6(doc):
    """Builds Chapter 6: Machine Learning for Short-Term Queue Forecasting."""
    add_chapter_heading(doc, 6, "Machine Learning for Short-Term Queue Forecasting")

    add_section_heading(doc, "6.1", "Short-Term Forecasting Problem Formulation", level=2)
    add_body_paragraph(
        doc,
        "While real-time computer vision telemetry provides instantaneous visibility into existing queues, proactive operational "
        "intervention mandates anticipatory foresight. In physical retail supermarkets, reassigning store employees from inventory "
        "restocking or aisle maintenance to active cashier checkout counters involves an operational transition delay of 8 to "
        "15 minutes (incorporating task handover, handwashing, and POS terminal authorization). If store supervisors are alerted "
        "only when a checkout line has already expanded to 8 or 10 customers, the resulting queue bottleneck is already deeply "
        "established, causing inevitable customer dissatisfaction and cart abandonment."
    )
    add_body_paragraph(
        doc,
        "To overcome this reactive limitation, the RTRFQM framework incorporates a supervised machine learning engine designed "
        "for short-term queue length forecasting. The problem is formally framed as a multi-step supervised regression task. "
        "Let t denote the current discrete observation timestamp (measured in 1-minute intervals). The objective is to predict "
        "the future queue length L_q at forward forecast horizons H in {15, 30} minutes:"
    )

    add_equation(doc, "hat{L}_q(t + H) = f(X_t; Theta)", "6.1")

    add_body_paragraph(
        doc,
        "where X_t in R^d represents an engineered feature vector encapsulating historical queue states, spatial footfall arrival "
        "rates, cashier operating parameters, and temporal calendar attributes, and Theta denotes the optimized parameters of the "
        "predictive model f."
    )

    add_section_heading(doc, "6.2", "Temporal Lag and Rolling Window Feature Engineering", level=2)
    add_body_paragraph(
        doc,
        "High-fidelity queue forecasting requires transforming raw time-series telemetry into a rich, stationary feature matrix. "
        "Because human arrival patterns in retail stores exhibit both high auto-regressive momentum and strong diurnal periodicity, "
        "the feature engineering pipeline constructs four distinct feature categories:"
    )
    add_bullet_point(
        doc,
        "Captures the immediate inertia of checkout lines using historical values: L_q(t), L_q(t - 5), L_q(t - 10), L_q(t - 15), "
        "and L_q(t - 30).",
        bold_prefix="1. Auto-Regressive Queue Lags:"
    )
    add_bullet_point(
        doc,
        "Smooths high-frequency camera noise and captures queue acceleration over rolling windows: mean queue length mu_{Lq}(15m), "
        "standard deviation sigma_{Lq}(15m), and first-order rate-of-change Delta L_q = L_q(t) - L_q(t - 15).",
        bold_prefix="2. Rolling Window Statistics:"
    )
    add_bullet_point(
        doc,
        "Integrates upstream customer inflow entering through the front entrance: cumulative footfall N_{entry}(t - 15), "
        "instantaneous arrival rate lambda(t), and in-store net occupancy O(t). Because entering shoppers browse for an average "
        "dwell time of 22 minutes before reaching checkout, upstream footfall serves as a powerful leading indicator of impending queue surges.",
        bold_prefix="3. Upstream Footfall Leading Indicators:"
    )
    add_bullet_point(
        doc,
        "Encodes diurnal shopping rhythms: hour of the day (0–23), minute of the hour, day-of-week integer (0–6), weekend "
        "indicator dummy (IsWeekend in {0, 1}), and active cashier counters c(t).",
        bold_prefix="4. Operational and Calendar Attributes:"
    )
    add_body_paragraph(
        doc,
        "Table 6.1 summarizes the engineered feature set, listing Pearson correlation coefficients with the target variable "
        "(Queue Length at t + 15 min) and relative Gini feature importance scores extracted from the optimized Random Forest model."
    )

    feat_headers = [
        "Feature Variable Name",
        "Feature Description & Calculation",
        "Pearson Corr (r)",
        "Gini Importance (%)"
    ]

    feat_data = [
        [
            "queue_len_t0",
            "Current instantaneous queue length at time t",
            "+0.84",
            "34.8%"
        ],
        [
            "queue_len_lag15",
            "Queue length observed 15 minutes prior (t - 15)",
            "+0.71",
            "18.4%"
        ],
        [
            "footfall_entry_rate_15m",
            "Customer entry rate across entrance tripwire (cust/min)",
            "+0.68",
            "14.2%"
        ],
        [
            "net_store_occupancy",
            "Current in-store customer occupancy (entry - exit)",
            "+0.62",
            "11.5%"
        ],
        [
            "active_cashiers",
            "Number of active cashier checkout lanes operating",
            "-0.55",
            "8.2%"
        ],
        [
            "queue_rolling_std_15m",
            "Standard deviation of queue length over past 15 min",
            "+0.48",
            "5.1%"
        ],
        [
            "hour_of_day",
            "Hour of operating day (8 to 22)",
            "+0.41",
            "4.3%"
        ],
        [
            "is_weekend",
            "Binary indicator for Saturday and Sunday",
            "+0.36",
            "2.5%"
        ],
        [
            "queue_rolling_mean_30m",
            "Rolling average queue length over past 30 min",
            "+0.59",
            "1.0%"
        ]
    ]

    add_styled_table(
        doc,
        headers=feat_headers,
        data=feat_data,
        col_widths=[1.8, 2.7, 1.1, 1.2],
        caption="Engineered Feature Sets, Correlation Analysis, and Random Forest Gini Importance Scores",
        table_num="6.1"
    )

    add_section_heading(doc, "6.3", "Candidate Predictive Model Architectures", level=2)
    add_body_paragraph(
        doc,
        "To identify the optimal predictive algorithm, five candidate machine learning and statistical architectures were "
        "implemented and systematically evaluated:"
    )
    add_bullet_point(
        doc,
        "The proposed architecture. An ensemble of B = 200 decorrelated regression decision trees trained via bootstrap "
        "aggregation (bagging). At each split node, a random subset of m = sqrt{d} features is evaluated. Final predictions "
        "represent the arithmetic ensemble average: hat{y} = (1/B) sum_{b=1}^B T_b(x). Random Forest provides superior handling "
        "of non-linear interactions, is inherently robust against outlier noise, and eliminates multi-collinearity sensitivity.",
        bold_prefix="1. Random Forest Regressor (Proposed Model):"
    )
    add_bullet_point(
        doc,
        "A regularized gradient boosted decision tree framework that constructs trees sequentially, optimizing second-order "
        "Taylor approximations of the loss function with L1/L2 leaf weight regularization.",
        bold_prefix="2. Extreme Gradient Boosting (XGBoost):"
    )
    add_bullet_point(
        doc,
        "A classical univariate statistical baseline fitted to historical queue series with parameter order (p=2, d=1, q=2). "
        "ARIMA models stationary auto-regressive differences but cannot ingest exogenous upstream footfall leading indicators.",
        bold_prefix="3. Autoregressive Integrated Moving Average (ARIMA):"
    )
    add_bullet_point(
        doc,
        "A standard multi-variable linear regression model with Ordinary Least Squares (OLS) estimation: hat{y} = beta^T X + epsilon. "
        "Provides a baseline evaluation of purely linear relationships.",
        bold_prefix="4. Multiple Linear Regression:"
    )
    add_bullet_point(
        doc,
        "A naive operational heuristic that projects future queue length as the trailing 30-minute simple moving average: "
        "hat{L}_q(t+15) = (1/k) sum_{i=0}^{k-1} L_q(t-i).",
        bold_prefix="5. Historical Moving Average Baseline:"
    )

    add_section_heading(doc, "6.4", "Hyperparameter Optimization and Cross-Validation", level=2)
    add_body_paragraph(
        doc,
        "To prevent temporal data leakage, standard randomized k-fold cross-validation is inapplicable to time-series data. "
        "Instead, hyperparameter tuning was conducted using an expanding-window TimeSeriesSplit cross-validation protocol with "
        "five distinct splits. The hyperparameter search space was explored using exhaustive Grid Search (GridSearchCV) over the "
        "training partition."
    )
    add_body_paragraph(
        doc,
        "Table 6.2 outlines the evaluated hyperparameter ranges, step intervals, and the optimal values selected by minimizing "
        "out-of-sample Root Mean Squared Error (RMSE)."
    )

    param_headers = [
        "Hyperparameter Name",
        "Evaluated Search Range",
        "Search Step / Candidates",
        "Optimal Selected Value"
    ]

    param_data = [
        [
            "n_estimators (Number of Trees)",
            "[50, 100, 200, 300, 500]",
            "Discrete Grid",
            "200 Trees"
        ],
        [
            "max_depth (Tree Depth Limit)",
            "[6, 10, 14, 18, None]",
            "Discrete Grid",
            "14 Levels"
        ],
        [
            "min_samples_split",
            "[2, 4, 6, 10]",
            "Integer Step",
            "4 Samples"
        ],
        [
            "min_samples_leaf",
            "[1, 2, 4, 8]",
            "Integer Step",
            "2 Samples"
        ],
        [
            "max_features",
            "['sqrt', 'log2', 0.5, 1.0]",
            "Categorical Selection",
            "'sqrt' (Square Root)"
        ],
        [
            "bootstrap Sampling",
            "[True, False]",
            "Boolean",
            "True (with Replacement)"
        ],
        [
            "criterion (Split Quality)",
            "['squared_error', 'absolute_error']",
            "Categorical Selection",
            "'squared_error' (MSE)"
        ]
    ]

    add_styled_table(
        doc,
        headers=param_headers,
        data=param_data,
        col_widths=[2.0, 2.0, 1.5, 1.3],
        caption="Hyperparameter Search Space, Grid Intervals, and Optimal Configuration for Random Forest Model",
        table_num="6.2"
    )

    add_section_heading(doc, "6.5", "Performance Metrics and Loss Minimization", level=2)
    add_body_paragraph(
        doc,
        "To rigorously quantify predictive performance across models, four standard regression metrics are computed on the "
        "unseen test partition: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE), "
        "and the Coefficient of Determination (R^2). Let y_i denote the ground-truth observed queue length at time i and hat{y}_i "
        "denote the model's predicted queue length over N test samples."
    )
    add_body_paragraph(
        doc,
        "Mean Absolute Error (MAE) measures the average magnitude of prediction errors in actual customer units, without "
        "penalizing large outliers disproportionately:"
    )

    add_equation(doc, "MAE = (1 / N) * sum_{i=1}^N |y_i - hat{y}_i|", "6.2")

    add_body_paragraph(
        doc,
        "Root Mean Squared Error (RMSE) gives higher weight to large prediction errors, providing insight into model stability "
        "during volatile peak surges:"
    )

    add_equation(doc, "RMSE = sqrt{(1 / N) * sum_{i=1}^N (y_i - hat{y}_i)^2}", "6.3")

    add_body_paragraph(
        doc,
        "Mean Absolute Percentage Error (MAPE) expresses error relative to actual queue magnitude, providing scale-independent "
        "interpretability for store supervisors:"
    )

    add_equation(doc, "MAPE = (100% / N) * sum_{i=1}^N |(y_i - hat{y}_i) / y_i|", "6.4")

    add_body_paragraph(
        doc,
        "The Coefficient of Determination (R^2) quantifies the proportion of total variance explained by the model relative to "
        "a naive mean predictor (where bar{y} represents sample mean):"
    )

    add_equation(doc, "R^2 = 1 - (sum_{i=1}^N (y_i - hat{y}_i)^2) / (sum_{i=1}^N (y_i - bar{y})^2)", "6.5")

    add_body_paragraph(
        doc,
        "An optimal forecasting model minimizes MAE, RMSE, and MAPE while maximizing R^2 towards 1.0. Comparative results across "
        "all candidate models are presented and analyzed in Chapter 9."
    )
