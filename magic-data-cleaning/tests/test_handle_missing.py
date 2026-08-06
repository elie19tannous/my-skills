#!/usr/bin/env python3
"""
Unit tests for handle_missing.py script.

Tests median imputation, auto strategy, and error cases.
"""

import pytest
import pandas as pd


class TestHandleMissing:
    """Test cases for missing value handling script."""

    def test_median_imputation(self, sample_missing_csv, tmp_workspace, run_script):
        """Test that numeric nulls are filled with median."""
        output_path = tmp_workspace / "cleaned_median.csv"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(sample_missing_csv),
            str(output_path),
            "--strategy", "median"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Cleaning failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify that missing values were filled
        df = pd.read_csv(output_path)
        numeric_cols = df.select_dtypes(include=['number']).columns

        for col in numeric_cols:
            assert df[col].isna().sum() == 0, f"Column {col} still has missing values after median imputation"

        # Check row counts
        assert "rows_in" in result, "rows_in not in result"
        assert "rows_out" in result, "rows_out not in result"
        assert result["rows_out"] == result["rows_in"], "Imputation should not change row count"

    def test_auto_strategy(self, sample_missing_csv, tmp_workspace, run_script):
        """Test that auto strategy correctly chooses per column type."""
        output_path = tmp_workspace / "cleaned_auto.csv"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(sample_missing_csv),
            str(output_path),
            "--strategy", "auto"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Cleaning failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify output file exists and has content
        df = pd.read_csv(output_path)
        assert len(df) > 0, "Output file should have rows"

        # Check that some missing values were handled
        assert "summary" in result, "summary not in result"
        summary = result["summary"]
        # Auto strategy may impute columns or drop columns
        assert "columns_imputed" in summary or "columns_dropped" in summary, \
            "Auto strategy should report imputation or dropping"

    def test_empty_dataframe_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty input produces error."""
        output_path = tmp_workspace / "cleaned_empty.csv"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file should fail
        assert result["success"] is False, "Empty file should fail"
        assert "error" in result, "Error message should be present"

    def test_drop_strategy(self, sample_missing_csv, tmp_workspace, run_script):
        """Test that drop_rows strategy removes rows with missing values."""
        output_path = tmp_workspace / "cleaned_drop.csv"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/handle_missing.py",
            str(sample_missing_csv),
            str(output_path),
            "--strategy=drop_rows"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Cleaning failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify no missing values remain
        df = pd.read_csv(output_path)
        assert df.isna().sum().sum() == 0, "Drop strategy should remove all rows with missing values"

        # Row count should be less than input
        assert "rows_in" in result, "rows_in not in result"
        assert "rows_out" in result, "rows_out not in result"
        assert result["rows_out"] < result["rows_in"], "Drop strategy should reduce row count"
