"""
test_app.py
Comprehensive Test Suite for RTRFQM: Functional Tests, Edge Cases, and Integration Checks
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd
from PIL import Image

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH, LANES_CONFIG
from src.database import (
    init_db,
    get_connection,
    save_footfall_record,
    save_queue_observation,
    log_congestion_alert,
    get_active_alerts,
    resolve_alert
)
from src.data_loader import (
    generate_synthetic_telemetry,
    validate_dataframe,
    clean_telemetry_dataframe
)
from src.footfall_analytics import compute_footfall_kpis, filter_footfall_by_date
from src.queue_dynamics import compute_counter_metrics, evaluate_lane_status
from src.waiting_time import (
    estimate_waiting_time_littles_law,
    estimate_multiserver_mmc_queue,
    compute_lane_wait_times
)
from src.ml_forecasting import (
    extract_features,
    train_eval_forecasting_model,
    predict_next_horizon
)
from src.simulation_engine import SimulationEngine
from src.alert_system import AlertManager
from src.visual_stream import generate_overhead_surveillance_frame


class TestRTRFQM(unittest.TestCase):
    """Test suite covering all functional, edge case, and integration requirements."""

    @classmethod
    def setUpClass(cls):
        """Initializes database and generates sample datasets for testing."""
        cls.test_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "test_retail.db")
        init_db(cls.test_db)
        cls.df_ff, cls.df_tx = generate_synthetic_telemetry(days=7, seed=123)

    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            try:
                os.remove(cls.test_db)
            except Exception:
                pass

    # 1. DATABASE & PERSISTENCE TESTS
    def test_database_initialization(self):
        conn = get_connection(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        for expected in ["footfall_records", "queue_observations", "checkout_counters", "congestion_alerts", "simulation_events"]:
            self.assertIn(expected, tables)

    def test_footfall_record_insertion(self):
        row_id = save_footfall_record(
            timestamp="2026-10-24 12:00:00",
            store_id="STORE-104",
            entries=45,
            exits=40,
            net_occupancy=150,
            arrival_rate=3.0,
            peak_status="PEAK",
            db_path=self.test_db
        )
        self.assertGreater(row_id, 0)

    # 2. FOOTFALL ANALYTICS TESTS
    def test_footfall_kpi_computation(self):
        kpis = compute_footfall_kpis(self.df_ff)
        self.assertGreater(kpis["total_entries"], 0)
        self.assertGreater(kpis["total_exits"], 0)
        self.assertIsNotNone(kpis["peak_hour"])
        self.assertIn(kpis["busiest_day"], ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

    def test_footfall_empty_dataframe(self):
        empty_kpi = compute_footfall_kpis(pd.DataFrame())
        self.assertEqual(empty_kpi["total_entries"], 0)
        self.assertEqual(empty_kpi["current_occupancy"], 0)

    # 3. QUEUE DYNAMICS & LITTLE'S LAW TESTS
    def test_littles_law_calculation(self):
        # 6 customers at mu = 0.6 cust/min => Wq = 10.0 min
        wait = estimate_waiting_time_littles_law(queue_length=6, service_rate_mu=0.6)
        self.assertEqual(wait, 10.0)

    def test_littles_law_edge_cases(self):
        # Empty queue
        self.assertEqual(estimate_waiting_time_littles_law(0, 0.6), 0.0)
        # Negative queue (safely handled as 0)
        self.assertEqual(estimate_waiting_time_littles_law(-5, 0.6), 0.0)
        # Zero service rate (handles division by zero safely)
        wait_zero_mu = estimate_waiting_time_littles_law(5, 0.0)
        self.assertGreater(wait_zero_mu, 0.0)

    def test_mmc_queue_theory(self):
        # Stable system: lambda = 2.0, mu = 0.606, c = 4 => c*mu = 2.424 > 2.0
        res = estimate_multiserver_mmc_queue(arrival_rate_lambda=2.0, service_rate_mu=0.606, active_servers_c=4)
        self.assertTrue(res["is_stable"])
        self.assertLess(res["rho"], 1.0)
        self.assertGreater(res["W_q"], 0.0)

        # Unstable system: lambda = 5.0, mu = 0.606, c = 2 => c*mu = 1.212 < 5.0
        res_unstable = estimate_multiserver_mmc_queue(arrival_rate_lambda=5.0, service_rate_mu=0.606, active_servers_c=2)
        self.assertFalse(res_unstable["is_stable"])

        # Edge case: zero servers
        res_zero = estimate_multiserver_mmc_queue(arrival_rate_lambda=2.0, service_rate_mu=0.606, active_servers_c=0)
        self.assertFalse(res_zero["is_stable"])

    # 4. MACHINE LEARNING ENGINE TESTS
    def test_ml_feature_extraction(self):
        X, y, ts = extract_features(self.df_ff, target_col="queue_length")
        self.assertGreater(len(X), 0)
        self.assertEqual(len(X), len(y))
        # Ensure no NaN values in features
        self.assertEqual(X.isnull().sum().sum(), 0)

    def test_ml_training_evaluation(self):
        model_test_path = os.path.join(os.path.dirname(self.test_db), "test_model_rf.joblib")
        eval_res = train_eval_forecasting_model(self.df_ff, target_col="queue_length", model_save_path=model_test_path)
        self.assertEqual(eval_res["status"], "SUCCESS")
        self.assertIn("mae", eval_res)
        self.assertIn("rmse", eval_res)
        self.assertIn("r2_score", eval_res)
        self.assertGreater(eval_res["r2_score"], -1.0)

        # Test inference
        pred = predict_next_horizon(self.df_ff.tail(20), target_col="queue_length", model_save_path=model_test_path)
        self.assertEqual(pred["status"], "SUCCESS")
        self.assertGreaterEqual(pred["predicted_queue_length"], 0.0)
        self.assertIn(pred["recommended_active_counters"], [2, 3, 4, 5, 6])

        # Cleanup model
        if os.path.exists(model_test_path):
            os.remove(model_test_path)

    # 5. REAL-TIME SIMULATION ENGINE TESTS
    def test_simulation_engine_step(self):
        sim = SimulationEngine(seed=99)
        initial_time = sim.sim_time
        state = sim.step()
        self.assertEqual(sim.sim_time - initial_time, pd.Timedelta(minutes=1))
        self.assertGreaterEqual(state["net_occupancy"], 0)
        self.assertGreater(state["active_counters"], 0)

        # Test counter toggle
        sim.set_counter_active(5, True)
        self.assertTrue(sim.lane_states[5]["is_active"])
        sim.set_counter_active(5, False)
        self.assertFalse(sim.lane_states[5]["is_active"])

    # 6. CONGESTION ALERTS & DEDUPLICATION TESTS
    def test_alert_generation_and_deduplication(self):
        mgr = AlertManager(warn_queue_len=4, crit_queue_len=6)
        mock_lanes = {
            1: {"name": "Lane 1", "is_active": True, "queue_length": 7, "estimated_wait_min": 6.0},
            2: {"name": "Lane 2", "is_active": True, "queue_length": 2, "estimated_wait_min": 1.5}
        }
        # First trigger
        alerts = mgr.evaluate_and_dispatch(mock_lanes, {})
        # Should detect Critical for Lane 1
        active = mgr.get_live_alerts()
        self.assertGreaterEqual(len(active), 1)

        # Deduplication: running again immediately shouldn't create duplicate active alert
        alerts_dup = mgr.evaluate_and_dispatch(mock_lanes, {})
        active_after = mgr.get_live_alerts()
        self.assertEqual(len(active), len(active_after))

        # Resolve alert
        alert_id = active[0]["id"]
        success = mgr.dismiss_alert(alert_id)
        self.assertTrue(success)

    # 7. CCTV VISUAL STREAM SIMULATOR TESTS
    def test_visual_surveillance_frame_rendering(self):
        sim = SimulationEngine(seed=42)
        frame = generate_overhead_surveillance_frame(sim.lane_states, current_occupancy=150)
        self.assertIsInstance(frame, Image.Image)
        self.assertEqual(frame.size, (800, 450))

    # 8. DATASET VALIDATION & CLEANING TESTS
    def test_dataset_validation(self):
        valid, msg, stats = validate_dataframe(self.df_ff, schema_type="footfall")
        self.assertTrue(valid)

        # Invalid missing columns
        invalid_df = pd.DataFrame({"random_col": [1, 2, 3]})
        valid_bad, msg_bad, _ = validate_dataframe(invalid_df, schema_type="footfall")
        self.assertFalse(valid_bad)
        self.assertIn("Missing required columns", msg_bad)

        # Empty df
        valid_empty, _, _ = validate_dataframe(pd.DataFrame())
        self.assertFalse(valid_empty)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRTRFQM)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
