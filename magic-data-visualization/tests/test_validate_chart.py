#!/usr/bin/env python3
"""Unit tests for skills/magic-data-visualization/scripts/validate_chart.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd
import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "validate_chart.py"
)


class TestValidateChart:
    """Tests for validate_chart.py script."""

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

    def test_valid_chart_metadata_passes(self):
        """Valid chart metadata with existing columns should pass all checks."""
        df = pd.DataFrame({
            "category": ["A", "B", "C", "D"],
            "value": [10, 20, 30, 40],
        })
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "chart_type": "bar",
            "x_col": "category",
            "y_col": "value",
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["valid"] is True
        assert result["checks_failed"] == 0
        assert result["checks_passed"] >= 3  # chart_type present, x_col/columns present, chart_type valid, x_col exists, y_col exists

    def test_missing_chart_type_fails(self):
        """Missing chart_type field should be flagged as a failure."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "x_col": "x",
            "y_col": "y",
            # chart_type deliberately omitted
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0  # script succeeds even with validation failures
        assert result["success"] is True
        assert result["valid"] is False
        assert result["checks_failed"] >= 1
        # Find the specific failure
        type_failures = [
            f for f in result["failures"]
            if f["check"] == "required_field_chart_type"
        ]
        assert len(type_failures) == 1

    def test_nonexistent_column_fails(self):
        """Referencing a column not in the CSV should cause a failure."""
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "chart_type": "scatter",
            "x_col": "nonexistent_col",
            "y_col": "y",
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["valid"] is False
        col_failures = [
            f for f in result["failures"]
            if f["check"] == "x_col_exists"
        ]
        assert len(col_failures) == 1
        assert "nonexistent_col" in col_failures[0]["message"]

    def test_appropriateness_score_returned(self):
        """A valid chart type should produce a non-zero appropriateness score."""
        df = pd.DataFrame({
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [10.0, 20.0, 15.0, 25.0, 30.0],
        })
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "chart_type": "scatter",
            "x_col": "x",
            "y_col": "y",
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert "appropriateness_score" in result
        # Scatter with two numeric columns should get a high score
        assert result["appropriateness_score"] >= 80
        assert isinstance(result["appropriateness_notes"], list)
        assert len(result["appropriateness_notes"]) >= 1

    def test_invalid_chart_type_fails(self):
        """An unrecognized chart_type should be flagged."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "chart_type": "radar_3d_exploded",
            "x_col": "x",
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["valid"] is False
        chart_type_failures = [
            f for f in result["failures"]
            if f["check"] == "chart_type_valid"
        ]
        assert len(chart_type_failures) == 1
        assert "radar_3d_exploded" in chart_type_failures[0]["message"]

    def test_columns_list_with_missing_columns(self):
        """The 'columns' list referencing non-existent columns should fail."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        csv_path = self._make_csv("data.csv", df)

        metadata = {
            "chart_type": "heatmap",
            "columns": ["a", "b", "c_missing"],
        }
        meta_path = self._make_json("chart_meta.json", metadata)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(csv_path, meta_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["valid"] is False
        col_failures = [
            f for f in result["failures"]
            if f["check"] == "columns_exist"
        ]
        assert len(col_failures) == 1
        assert "c_missing" in col_failures[0]["message"]
