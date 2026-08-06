#!/usr/bin/env python3
"""Unit tests for skills/magic-data-validation/scripts/validate_statistics.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "magic-data-validation", "scripts", "validate_statistics.py"
)


class TestValidateStatistics:
    """Tests for validate_statistics.py script."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_csv(self, filename, df):
        path = os.path.join(self.tmpdir, filename)
        df.to_csv(path, index=False)
        return path

    def _make_json(self, filename, data):
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return path

    def run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True, text=True, timeout=30
        )
        return result

    def test_all_passing_within_tolerance(self):
        """Statistics that exactly match the source data should pass all checks."""
        df = pd.DataFrame({
            "revenue": [100.0, 200.0, 300.0, 400.0, 500.0],
            "cost": [50.0, 60.0, 70.0, 80.0, 90.0],
        })
        csv_path = self._make_csv("data.csv", df)

        # Compute correct stats
        stats = {
            "revenue": {
                "mean": float(df["revenue"].mean()),
                "std": float(df["revenue"].std(ddof=1)),
                "min": float(df["revenue"].min()),
                "max": float(df["revenue"].max()),
                "count": int(len(df["revenue"])),
            },
            "cost": {
                "mean": float(df["cost"].mean()),
                "std": float(df["cost"].std(ddof=1)),
                "min": float(df["cost"].min()),
                "max": float(df["cost"].max()),
                "count": int(len(df["cost"])),
            },
        }
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, stats_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["checks_failed"] == 0
        assert result["checks_passed"] == 10  # 5 stats * 2 columns

    def test_failing_mean_off_by_more_than_tolerance(self):
        """If the reported mean is off by more than tolerance, it should fail."""
        df = pd.DataFrame({"revenue": [100.0, 200.0, 300.0]})
        csv_path = self._make_csv("data.csv", df)

        # Report an incorrect mean (off by 10)
        stats = {
            "revenue": {
                "mean": float(df["revenue"].mean()) + 10.0,
                "count": 3,
            },
        }
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, stats_path, output_path, "--tolerance", "1e-6")
        result = json.loads(proc.stdout)

        assert proc.returncode == 1
        assert result["success"] is False
        assert result["checks_failed"] >= 1
        # The mean check should specifically fail
        mean_result = result["results"]["revenue"]["mean"]
        assert mean_result["passed"] is False
        assert mean_result["diff"] > 1e-6

    def test_missing_column_in_source(self):
        """If the stats reference a column not in the CSV, checks should fail."""
        df = pd.DataFrame({"revenue": [100.0, 200.0, 300.0]})
        csv_path = self._make_csv("data.csv", df)

        # Stats reference 'profit' which is not in the CSV
        stats = {
            "profit": {
                "mean": 50.0,
                "count": 3,
            },
        }
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, stats_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 1
        assert result["success"] is False
        assert result["checks_failed"] >= 1
        # Should report the missing column
        profit_results = result["results"]["profit"]
        for stat_name, stat_result in profit_results.items():
            assert stat_result["passed"] is False
            assert "not found" in stat_result.get("error", "").lower()

    def test_count_exact_integer_comparison(self):
        """Count comparison should be exact (no floating tolerance)."""
        df = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0]})
        csv_path = self._make_csv("data.csv", df)

        # Report count as 5 (wrong: actual count is 4)
        stats = {"value": {"count": 5}}
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, stats_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 1
        assert result["success"] is False
        count_result = result["results"]["value"]["count"]
        assert count_result["passed"] is False
        assert count_result["expected"] == 5
        assert count_result["actual"] == 4

    def test_nested_columns_key_in_stats_json(self):
        """Stats JSON with a 'columns' wrapper should be parsed correctly."""
        df = pd.DataFrame({"x": [10.0, 20.0, 30.0]})
        csv_path = self._make_csv("data.csv", df)

        stats = {
            "columns": {
                "x": {
                    "mean": float(df["x"].mean()),
                    "min": float(df["x"].min()),
                    "max": float(df["x"].max()),
                    "count": 3,
                }
            }
        }
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, stats_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["checks_failed"] == 0

    def test_column_filter(self):
        """The --columns flag should limit validation to specified columns."""
        df = pd.DataFrame({
            "a": [1.0, 2.0, 3.0],
            "b": [10.0, 20.0, 30.0],
        })
        csv_path = self._make_csv("data.csv", df)

        stats = {
            "a": {"mean": float(df["a"].mean()), "count": 3},
            "b": {"mean": 999.0, "count": 3},  # intentionally wrong
        }
        stats_path = self._make_json("stats.json", stats)
        output_path = os.path.join(self.tmpdir, "validation.json")

        # Only validate column 'a' -- 'b' wrong mean should not be checked
        proc = self.run_script(csv_path, stats_path, output_path, "--columns", "a")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        # Only column 'a' should appear in results
        assert "a" in result["results"]
        assert "b" not in result["results"]
