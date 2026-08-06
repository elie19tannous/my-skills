#!/usr/bin/env python3
"""Unit tests for skills/magic-data-exploration/scripts/prepare_for_exploration.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd
import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "prepare_for_exploration.py"
)



class TestPrepareForExploration:
    """Tests for prepare_for_exploration.py script."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_csv(self, filename, df):
        path = os.path.join(self.tmpdir, filename)
        df.to_csv(path, index=False)
        return path

    def run_script(self, *args):
        env = os.environ.copy()
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True, text=True, timeout=30,
            env=env,
        )
        return result

    def test_auto_derivation_produces_expected_columns(self):
        """Auto-derivation should produce {col}_length, {col}_word_count, {col}_is_present."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
            "description": [
                "A software engineer",
                "A data scientist with experience",
                "A product manager",
                "",
                "A designer and illustrator",
            ],
        })
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        proc = self.run_script(csv_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_in"] == 5
        assert result["columns_derived"] >= 6  # 3 per text column * 2 columns

        # Read the output CSV
        out_df = pd.read_csv(output_path)

        # Check derived columns for 'name'
        assert "name_length" in out_df.columns
        assert "name_word_count" in out_df.columns
        assert "name_is_present" in out_df.columns

        # Check derived columns for 'description'
        assert "description_length" in out_df.columns
        assert "description_word_count" in out_df.columns
        assert "description_is_present" in out_df.columns

        # Verify actual values
        assert out_df["name_length"].iloc[0] == len("Alice")  # 5
        assert out_df["name_word_count"].iloc[0] == 1  # single word
        assert out_df["name_is_present"].iloc[0] == 1
        # Empty description should have is_present = 0
        assert out_df["description_is_present"].iloc[3] == 0

    def test_columns_flag_selective_derivation(self):
        """The --columns flag should limit derivation to specified columns only."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob", "Charlie"],
            "city": ["London", "Paris", "Tokyo"],
            "score": [85, 92, 78],  # numeric -- should be skipped automatically
        })
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        proc = self.run_script(csv_path, output_path, "--columns", "name")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        out_df = pd.read_csv(output_path)

        # name should have derived columns
        assert "name_length" in out_df.columns
        assert "name_word_count" in out_df.columns
        assert "name_is_present" in out_df.columns

        # city should NOT have derived columns
        assert "city_length" not in out_df.columns
        assert "city_word_count" not in out_df.columns

    def test_derive_with_whitelisted_expression(self):
        """The --derive flag with a whitelisted expression should add a custom column."""
        df = pd.DataFrame({
            "name": ["Alice", "Bob123", "Charlie", "Diana99", "Eve"],
        })
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        derive_json = json.dumps({"name_len": "name:str.len()"})
        proc = self.run_script(csv_path, output_path, "--derive", derive_json)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert "name_len" in result["derived_features"]

        out_df = pd.read_csv(output_path)
        assert "name_len" in out_df.columns
        assert out_df["name_len"].iloc[0] == len("Alice")
        assert out_df["name_len"].iloc[1] == len("Bob123")

    def test_derive_digit_count_expression(self):
        """The str.count(digits) expression should count digit characters."""
        df = pd.DataFrame({
            "word": ["abc123", "def456789", "ghi", "j0k1l2"],
        })
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        derive_json = json.dumps({"word_digits": "word:str.count(digits)"})
        proc = self.run_script(csv_path, output_path, "--derive", derive_json)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        out_df = pd.read_csv(output_path)
        assert "word_digits" in out_df.columns
        assert out_df["word_digits"].iloc[0] == 3    # "abc123" has 3 digits
        assert out_df["word_digits"].iloc[1] == 6    # "def456789" has 6 digits
        assert out_df["word_digits"].iloc[2] == 0    # "ghi" has 0 digits
        assert out_df["word_digits"].iloc[3] == 3    # "j0k1l2" has 3 digits

    def test_derive_rejected_for_unknown_expression(self):
        """An expression not in the whitelist should be rejected."""
        df = pd.DataFrame({"name": ["Alice", "Bob"]})
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        derive_json = json.dumps({"bad_col": "name:eval(dangerous_code)"})
        proc = self.run_script(csv_path, output_path, "--derive", derive_json)
        result = json.loads(proc.stdout)

        assert proc.returncode == 1
        assert result["success"] is False
        assert "whitelist" in result["error"].lower()

    def test_numeric_columns_skipped(self):
        """Numeric columns should not get text-derived features even if passed explicitly."""
        df = pd.DataFrame({
            "score": [85, 92, 78, 88, 95],
            "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        })
        csv_path = self._make_csv("data.csv", df)
        output_path = os.path.join(self.tmpdir, "enriched.csv")

        proc = self.run_script(csv_path, output_path, "--columns", "score,name")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        out_df = pd.read_csv(output_path)
        # score is numeric, so no _length etc. derived
        assert "score_length" not in out_df.columns
        # name is text, so derived columns should exist
        assert "name_length" in out_df.columns
