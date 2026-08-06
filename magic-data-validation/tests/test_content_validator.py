#!/usr/bin/env python3
"""Unit tests for skills/magic-data-validation/scripts/content_validator.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd
import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "content_validator.py"
)


class TestContentValidator:
    """Tests for content_validator.py script."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_csv(self, filename, df):
        path = os.path.join(self.tmpdir, filename)
        df.to_csv(path, index=False)
        return path

    def run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True, text=True, timeout=30
        )
        return result

    def test_sentinel_detection_finds_known_values(self):
        """CSV with known sentinel values should be detected with correct counts."""
        # Write CSV manually to avoid pandas converting sentinel strings like N/A to NaN
        csv_path = os.path.join(self.tmpdir, "sentinels.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("word,definition\n")
            f.write("hello,meaning1\n")
            f.write("X,???\n")
            f.write("world,meaning3\n")
            f.write("TODO,meaning4\n")
            f.write("test_value,placeholder\n")
        output_path = os.path.join(self.tmpdir, "report.json")

        proc = self.run_script(csv_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        sentinel = result["sentinel_findings"]
        assert sentinel["total_sentinels"] > 0
        # 'X' and 'TODO' should be found in 'word'; '???' and 'placeholder' in 'definition'
        assert "word" in sentinel["by_column"]
        assert "definition" in sentinel["by_column"]

        # Check specific value counts
        word_vals = sentinel["by_column"]["word"]["values"]
        assert "X" in word_vals
        assert "TODO" in word_vals

        definition_vals = sentinel["by_column"]["definition"]["values"]
        assert "???" in definition_vals
        assert "placeholder" in definition_vals

    def test_min_content_length_flag(self):
        """The --min-content-length flag should flag short strings below the threshold."""
        df = pd.DataFrame({
            "name": ["AB", "A longer name here", "CD", "Another good name", "EF"],
        })
        csv_path = self._make_csv("short.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        # Set min content length to 5 -- "AB", "CD", "EF" (length 2) should be flagged
        proc = self.run_script(csv_path, output_path, "--min-content-length", "5")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        sentinel = result["sentinel_findings"]
        assert sentinel["total_sentinels"] >= 3  # AB, CD, EF are all < 5 chars
        assert "name" in sentinel["by_column"]
        assert sentinel["by_column"]["name"]["count"] >= 3

    def test_custom_sentinel_values(self):
        """The --sentinel-values flag should replace the built-in sentinel list."""
        df = pd.DataFrame({
            "status": ["active", "REVIEW", "active", "PENDING", "active"],
        })
        csv_path = self._make_csv("custom.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        # Only flag REVIEW and PENDING as sentinels
        proc = self.run_script(
            csv_path, output_path,
            "--sentinel-values", "REVIEW,PENDING",
            "--min-content-length", "1",  # disable short-string detection
        )
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        sentinel = result["sentinel_findings"]

        # REVIEW and PENDING should be found
        assert sentinel["total_sentinels"] == 2
        vals = sentinel["by_column"]["status"]["values"]
        assert "REVIEW" in vals
        assert "PENDING" in vals
        # 'active' should NOT be flagged
        assert "active" not in vals

    def test_distribution_check_flag(self):
        """The --distribution-check flag should enable anomaly detection layer."""
        # Create data with a mix of long and short values to trigger anomalies
        long_text = "This is a fairly long text with many words and characters inside"
        df = pd.DataFrame({
            "description": [long_text] * 20 + ["X"] * 2,
        })
        csv_path = self._make_csv("distribution.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        # Without --distribution-check
        proc_no_dist = self.run_script(csv_path, output_path)
        result_no_dist = json.loads(proc_no_dist.stdout)
        assert result_no_dist["success"] is True
        # Should have a note about distribution check being disabled
        dist_no = result_no_dist["distribution_findings"]
        assert dist_no["anomalies_detected"] == 0

        # With --distribution-check
        output_path2 = os.path.join(self.tmpdir, "report2.json")
        proc_dist = self.run_script(csv_path, output_path2, "--distribution-check")
        result_dist = json.loads(proc_dist.stdout)
        assert result_dist["success"] is True
        dist_yes = result_dist["distribution_findings"]
        # The short "X" values should be flagged as anomalies
        assert dist_yes["anomalies_detected"] >= 1

    def test_clean_data_no_sentinels(self):
        """Data with no sentinel values and adequate length should report zero issues."""
        df = pd.DataFrame({
            "word": ["apple", "banana", "cherry", "dragonfruit", "elderberry"],
            "meaning": [
                "A round fruit",
                "A yellow fruit",
                "A small red fruit",
                "A tropical fruit",
                "A dark berry",
            ],
        })
        csv_path = self._make_csv("clean.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        proc = self.run_script(csv_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["sentinel_findings"]["total_sentinels"] == 0
        assert result["sentinel_findings"]["severity"] == "NONE"

    def test_columns_flag_limits_analysis(self):
        """The --columns flag should restrict analysis to specified columns."""
        df = pd.DataFrame({
            "clean_col": ["normal text here", "another normal text", "yet another"],
            "dirty_col": ["X", "TODO", "N/A"],
        })
        csv_path = self._make_csv("partial.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        # Only analyze clean_col
        proc = self.run_script(csv_path, output_path, "--columns", "clean_col")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        sentinel = result["sentinel_findings"]
        # dirty_col should not be analyzed
        assert "dirty_col" not in sentinel["by_column"]
        assert sentinel["total_sentinels"] == 0

    def test_severity_levels(self):
        """Severity should escalate based on percentage of sentinels found."""
        # Create data where 50% of values are sentinels -> HIGH severity
        df = pd.DataFrame({
            "col": ["X", "N/A", "TODO", "???", "real_value_one",
                     "real_value_two", "real_value_three", "real_value_four",
                     "real_value_five", "real_value_six"],
        })
        csv_path = self._make_csv("severity.csv", df)
        output_path = os.path.join(self.tmpdir, "report.json")

        proc = self.run_script(csv_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        # 4 sentinels out of 10 = 40% -> should be HIGH
        severity = result["sentinel_findings"]["severity"]
        assert severity in ("HIGH", "MEDIUM")
