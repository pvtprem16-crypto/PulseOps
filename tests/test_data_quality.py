import unittest

import pandas as pd

from src.data_quality import (
    check_duplicate_ids,
    check_reporting_cutoff,
    calculate_quality_score,
)


class DataQualityTests(unittest.TestCase):
    def test_duplicate_ticket_ids_detected(self):
        df = pd.DataFrame({"ticket_id": ["TKT-1", "TKT-1", "TKT-2"]})
        self.assertEqual(check_duplicate_ids(df), 1)

    def test_future_timestamps_detected(self):
        df = pd.DataFrame({
            "first_response_at": ["2026-11-26", None],
            "resolved_at": [None, "2026-11-27"],
            "closed_at": [None, None],
        })
        checks = check_reporting_cutoff(df)
        self.assertEqual(checks["Future timestamps in first_response_at"], 1)
        self.assertEqual(checks["Future timestamps in resolved_at"], 1)
        self.assertEqual(checks["Future timestamps in closed_at"], 0)

    def test_quality_score_handles_empty_results(self):
        self.assertEqual(calculate_quality_score({})["quality_score"], 0)

    def test_quality_score_counts_pass_and_fail(self):
        score = calculate_quality_score({"check_a": 0, "check_b": 2})
        self.assertEqual(score["passed_checks"], 1)
        self.assertEqual(score["failed_checks"], 1)
        self.assertEqual(score["quality_score"], 50.0)


if __name__ == "__main__":
    unittest.main()
