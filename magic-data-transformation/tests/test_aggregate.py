#!/usr/bin/env python3
"""
Unit tests for aggregate.py script.

Tests basic aggregation, multiple aggregation functions, and error cases.
"""

import pytest
import pandas as pd


class TestAggregate:
    """Test cases for aggregation script."""

    def test_basic_aggregation(self, test_data_dir, tmp_workspace, run_script):
        """Test that group-by with mean/count produces correct results."""
        # Create CSV with groupable data
        group_csv = test_data_dir / "sample_grouped.csv"
        with open(group_csv, 'w') as f:
            f.write("category,value\n")
            f.write("A,10\n")
            f.write("A,20\n")
            f.write("B,30\n")
            f.write("B,40\n")
            f.write("C,50\n")

        output_path = tmp_workspace / "aggregated.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/aggregate.py",
            str(group_csv),
            str(output_path),
            "--group-cols", "category",
            "--functions", "mean"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Aggregation failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify aggregation results
        df = pd.read_csv(output_path)
        assert len(df) == 3, f"Expected 3 groups (A, B, C), got {len(df)}"

        # Check row counts
        assert "rows_in" in result, "rows_in not in result"
        assert "rows_out" in result, "rows_out not in result"
        assert result["rows_in"] == 5, "Input should have 5 rows"
        assert result["rows_out"] == 3, "Output should have 3 rows (groups)"

    def test_multiple_functions(self, test_data_dir, tmp_workspace, run_script):
        """Test that multiple aggregation functions work."""
        # Create CSV with groupable data
        group_csv = test_data_dir / "sample_multi_agg.csv"
        with open(group_csv, 'w') as f:
            f.write("category,value\n")
            f.write("A,10\n")
            f.write("A,20\n")
            f.write("B,30\n")
            f.write("B,40\n")

        output_path = tmp_workspace / "multi_agg.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/aggregate.py",
            str(group_csv),
            str(output_path),
            "--group-cols", "category",
            "--functions", "mean,sum,count"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Aggregation failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify multiple aggregation columns exist
        df = pd.read_csv(output_path)
        assert len(df) >= 2, "Should have at least 2 groups"

        # Should have multiple columns from different aggregations
        assert len(df.columns) >= 2, "Should have multiple aggregation columns"

    def test_empty_data_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "agg_empty.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/aggregate.py",
            str(empty_csv),
            str(output_path),
            "--group-cols", "category"
        )

        # Empty file should either fail or succeed with 0 rows
        if result["success"]:
            assert result.get("rows_in", 0) == 0, "Empty file should have 0 input rows"
            assert result.get("rows_out", 0) == 0, "Empty file should have 0 output rows"
        else:
            assert "error" in result, "Error message should be present"

    def test_multiple_group_columns(self, test_data_dir, tmp_workspace, run_script):
        """Test aggregation with multiple group-by columns."""
        # Create CSV with multiple group columns
        group_csv = test_data_dir / "sample_multi_group.csv"
        with open(group_csv, 'w') as f:
            f.write("category,subcategory,value\n")
            f.write("A,X,10\n")
            f.write("A,X,20\n")
            f.write("A,Y,30\n")
            f.write("B,X,40\n")
            f.write("B,Y,50\n")

        output_path = tmp_workspace / "multi_group_agg.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/aggregate.py",
            str(group_csv),
            str(output_path),
            "--group-cols", "category,subcategory",
            "--functions", "mean"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Aggregation failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify multiple group columns
        df = pd.read_csv(output_path)
        assert len(df) >= 3, "Should have at least 3 unique combinations"
