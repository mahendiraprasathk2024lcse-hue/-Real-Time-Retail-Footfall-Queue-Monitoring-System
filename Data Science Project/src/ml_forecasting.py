"""
src/ml_forecasting.py
Module E: Machine Learning Engine for Short-Term Queue Forecasting and Staffing Optimization
"""

import os
from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import plotly.graph_objects as go

from config import (
    QUEUE_MODEL_PATH,
    FOOTFALL_MODEL_PATH,
    MODELS_DIR,
    DEFAULT_SERVICE_RATE_MU,
    TARGET_WAIT_TIME_MIN
)


def extract_features(df: pd.DataFrame, target_col: str = "queue_length") -> Tuple[pd.DataFrame, pd.Series]:
    """
    Builds temporal lag features and rolling statistics without data leakage.
    Features:
    - Auto-regressive lags: target(t-1), target(t-2), target(t-4)
    - Rolling window statistics: rolling mean (4 periods = 1 hour), rolling std
    - Upstream footfall indicators: entries, arrival_rate, net_occupancy
    - Temporal calendar attributes: hour, day_of_week, is_weekend
    - Operational attributes: active_counters
    """
    df_feat = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_feat["timestamp"]):
        df_feat["timestamp"] = pd.to_datetime(df_feat["timestamp"])

    df_feat = df_feat.sort_values("timestamp").reset_index(drop=True)

    # Lags
    df_feat["target_lag_1"] = df_feat[target_col].shift(1)
    df_feat["target_lag_2"] = df_feat[target_col].shift(2)
    df_feat["target_lag_4"] = df_feat[target_col].shift(4)

    # Rolling stats
    df_feat["target_roll_mean_4"] = df_feat[target_col].shift(1).rolling(window=4).mean()
    df_feat["target_roll_std_4"] = df_feat[target_col].shift(1).rolling(window=4).std().fillna(0)
    df_feat["target_rate_of_change"] = df_feat["target_lag_1"] - df_feat["target_lag_4"]

    # Upstream footfall indicators
    if "entries" in df_feat.columns:
        df_feat["entries_lag_1"] = df_feat["entries"].shift(1)
    if "arrival_rate" in df_feat.columns:
        df_feat["arrival_rate_lag_1"] = df_feat["arrival_rate"].shift(1)
    if "net_occupancy" in df_feat.columns:
        df_feat["net_occupancy_lag_1"] = df_feat["net_occupancy"].shift(1)

    # Calendar features
    df_feat["hour"] = df_feat["timestamp"].dt.hour
    df_feat["day_of_week"] = df_feat["timestamp"].dt.dayofweek
    df_feat["is_weekend"] = df_feat["day_of_week"].apply(lambda d: 1 if d >= 5 else 0)

    # Target forward horizon (e.g., target at t+1 = 15 mins ahead)
    df_feat["y_target"] = df_feat[target_col].shift(-1)

    # Drop NA rows resulting from shifts
    df_clean = df_feat.dropna().reset_index(drop=True)

    feature_cols = [
        "target_lag_1", "target_lag_2", "target_lag_4",
        "target_roll_mean_4", "target_roll_std_4", "target_rate_of_change",
        "hour", "day_of_week", "is_weekend"
    ]
    for opt in ["entries_lag_1", "arrival_rate_lag_1", "net_occupancy_lag_1", "active_counters"]:
        if opt in df_clean.columns:
            feature_cols.append(opt)

    X = df_clean[feature_cols]
    y = df_clean["y_target"]
    return X, y, df_clean["timestamp"]


def train_eval_forecasting_model(
    df: pd.DataFrame,
    target_col: str = "queue_length",
    model_save_path: str = QUEUE_MODEL_PATH
) -> Dict[str, Any]:
    """
    Trains a Random Forest Regressor and baseline model using chronological split (80/20).
    Evaluates MAE, RMSE, MAPE, R2 score and persists the trained artifact.
    """
    if len(df) < 50:
        return {"error": "Insufficient data records for robust supervised machine learning (need >= 50)."}

    X, y, timestamps = extract_features(df, target_col=target_col)

    # Chronological Split (No shuffle to prevent time leakage)
    split_idx = int(len(X) * 0.80)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    ts_test = timestamps.iloc[split_idx:]

    # Train Random Forest
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_split=4, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    # Train Baseline Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    # Predict
    y_pred_rf = rf.predict(X_test)
    y_pred_lr = lr.predict(X_test)

    # Metrics RF
    mae_rf = float(mean_absolute_error(y_test, y_pred_rf))
    rmse_rf = float(np.sqrt(mean_squared_error(y_test, y_pred_rf)))
    r2_rf = float(r2_score(y_test, y_pred_rf))
    non_zero = y_test != 0
    mape_rf = float(np.mean(np.abs((y_test[non_zero] - y_pred_rf[non_zero]) / y_test[non_zero])) * 100) if np.any(non_zero) else 0.0

    # Metrics Baseline
    mae_lr = float(mean_absolute_error(y_test, y_pred_lr))
    rmse_lr = float(np.sqrt(mean_squared_error(y_test, y_pred_lr)))
    r2_lr = float(r2_score(y_test, y_pred_lr))

    # Feature Importance
    feature_importance = dict(zip(X.columns, [round(float(v) * 100, 2) for v in rf.feature_importances_]))
    feature_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True))

    # Persist model
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump({"model": rf, "feature_names": list(X.columns), "target_col": target_col}, model_save_path)

    # Sample comparison dataframe for plotting
    test_eval_df = pd.DataFrame({
        "timestamp": ts_test.values,
        "actual": y_test.values,
        "predicted_rf": np.round(y_pred_rf, 1),
        "predicted_baseline": np.round(y_pred_lr, 1)
    })

    return {
        "status": "SUCCESS",
        "model_type": "Random Forest Regressor (100 Trees)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "mae": round(mae_rf, 2),
        "rmse": round(rmse_rf, 2),
        "mape": round(mape_rf, 1),
        "r2_score": round(r2_rf, 3),
        "baseline_mae": round(mae_lr, 2),
        "baseline_rmse": round(rmse_lr, 2),
        "baseline_r2": round(r2_lr, 3),
        "feature_importance": feature_importance,
        "model_path": model_save_path,
        "eval_dataframe": test_eval_df
    }


def predict_next_horizon(
    recent_records: pd.DataFrame,
    target_col: str = "queue_length",
    model_save_path: str = QUEUE_MODEL_PATH
) -> Dict[str, Any]:
    """
    Loads saved model and predicts queue / footfall for next 15-minute horizon,
    providing dynamic staff recommendation.
    """
    if not os.path.exists(model_save_path):
        return {"status": "UNAVAILABLE", "message": "Model not trained yet."}

    try:
        saved_obj = joblib.load(model_save_path)
        model = saved_obj["model"]
        feature_names = saved_obj["feature_names"]

        X, _, _ = extract_features(recent_records, target_col=target_col)
        if X.empty:
            return {"status": "ERROR", "message": "Insufficient recent rows to form lag features."}

        latest_x = X[feature_names].iloc[-1:]
        predicted_val = float(model.predict(latest_x)[0])
        predicted_val = max(0.0, round(predicted_val, 1))

        # Dynamic staffing recommendation
        # If predicted queue is Q_pred, arrival rate lam, we want wait time <= target_wait
        # Little's Law: Wq = Q_pred / (c * mu) <= 3.0 => c >= Q_pred / (3.0 * mu)
        mu = DEFAULT_SERVICE_RATE_MU
        needed_counters = int(np.clip(np.ceil(predicted_val / (TARGET_WAIT_TIME_MIN * mu)), 2, 6))

        return {
            "status": "SUCCESS",
            "forecast_horizon": "Next 15 Minutes",
            "predicted_queue_length": predicted_val,
            "recommended_active_counters": needed_counters,
            "forecast_congestion_risk": "HIGH" if predicted_val >= 6 else ("MEDIUM" if predicted_val >= 4 else "LOW")
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def create_actual_vs_predicted_chart(eval_df: pd.DataFrame) -> go.Figure:
    """Generates time-series line chart comparing Actual vs Predicted values on test set."""
    if eval_df.empty:
        return go.Figure()

    sample_eval = eval_df.tail(150).copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sample_eval["timestamp"],
        y=sample_eval["actual"],
        mode="lines",
        line=dict(color="#1e293b", width=2.5),
        name="Ground-Truth Actual"
    ))
    fig.add_trace(go.Scatter(
        x=sample_eval["timestamp"],
        y=sample_eval["predicted_rf"],
        mode="lines+markers",
        line=dict(color="#0284c7", width=2, dash="dash"),
        marker=dict(size=4),
        name="Random Forest Forecast (Proposed)"
    ))
    fig.add_trace(go.Scatter(
        x=sample_eval["timestamp"],
        y=sample_eval["predicted_baseline"],
        mode="lines",
        line=dict(color="#94a3b8", width=1.5, dash="dot"),
        name="Linear Regression Baseline"
    ))

    fig.update_layout(
        title="Predictive Model Evaluation: Ground-Truth Actual vs. Short-Term Forecast",
        xaxis=dict(title="Chronological Test Timestamp"),
        yaxis=dict(title="Queue Length (Customers)"),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def create_feature_importance_chart(feature_importance: Dict[str, float]) -> go.Figure:
    """Generates horizontal bar chart of Gini feature importances."""
    if not feature_importance:
        return go.Figure()

    feats = list(feature_importance.keys())[::-1]
    vals = list(feature_importance.values())[::-1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=vals,
        y=feats,
        orientation="h",
        marker_color="#2563eb",
        text=[f"{v:.1f}%" for v in vals],
        textposition="outside"
    ))

    fig.update_layout(
        title="Random Forest Gini Feature Importance Breakdown",
        xaxis=dict(title="Relative Importance Contribution (%)"),
        yaxis=dict(title="Feature Variable"),
        template="plotly_white",
        margin=dict(l=150, r=40, t=50, b=40)
    )
    return fig
