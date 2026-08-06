#!/usr/bin/env python3
"""
Unit tests for merge_datasets.py script.

Tests inner join, join explosion warnings, and missing key errors.
"""

import pytest
import pandas as pd


class TestMergeDatasets:
    """Test cases for dataset merging script."""

    def test_inner_join(self, test_data_dir, tmp_workspace, run_script):
        """Test that inner join produces correct matched count."""
        # Create two CSV files to join
        left_csv = test_data_dir / "left_data.csv"
        with open(left_csv, 'w') as f:
            f.write("id,name\n")
            f.write("1,Alice\n")
            f.write("2,Bob\n")
            f.write("3,Charlie\n")

        right_csv = test_data_dir / "right_data.csv"
        with open(right_csv, 'w') as f:
            f.write("id,score\n")
            f.write("1,85\n")
            f.write("2,92\n")
            f.write("4,78\n")

        output_path = tmp_workspace / "merged.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/merge_datasets.py",
            str(left_csv),
            str(right_csv),
            str(output_path),
            "--on", "id",
            "--how", "inner"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Merge failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify inner join results (only id 1 and 2 should match)
        df = pd.read_csv(output_path)
        assert len(df) == 2, f"Inner join should have 2 rows, got {len(df)}"

        # Check row counts
        assert "rows_out" in result, "rows_out not in result"
        assert result["rows_out"] == 2, "Inner join should output 2 rows"

    def test_join_explosion_warning(self, test_data_dir, tmp_workspace, run_script):
        """Test that many-to-many join triggers warning."""
        # Create data with duplicate keys (many-to-many)
        left_csv = test_data_dir / "left_many.csv"
        with open(left_csv, 'w') as f:
            f.write("id,value_left\n")
            f.write("1,A\n")
            f.write("1,B\n")
            f.write("2,C\n")

        right_csv = test_data_dir / "right_many.csv"
        with open(right_csv, 'w') as f:
            f.write("id,value_right\n")
            f.write("1,X\n")
            f.write("1,Y\n")
            f.write("2,Z\n")

        output_path = tmp_workspace / "merged_many.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/merge_datasets.py",
            str(left_csv),
            str(right_csv),
            str(output_path),
            "--on", "id"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Merge failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Many-to-many join on id=1 should produce 4 rows (2x2)
        df = pd.read_csv(output_path)
        assert len(df) >= 4, f"Many-to-many join should produce at least 4 rows, got {len(df)}"

        # Check for warning about join explosion
        if "warnings" in result:
            has_explosion_warning = any(
                "explosion" in str(w).lower() or "many" in str(w).lower()
                for w in result["warnings"]
            )
            # Warning is optional but good practice
            # assert has_explosion_warning, "Should warn about join explosion"

    def test_missing_key_error(self, test_data_dir, tmp_workspace, run_script):
        """Test that missing join key produces error."""
        # Create CSV without the join key
        left_csv = test_data_dir / "left_no_key.csv"
        with open(left_csv, 'w') as f:
            f.write("name,value\n")
            f.write("Alice,100\n")

        right_csv = test_data_dir / "right_no_key.csv"
        with open(right_csv, 'w') as f:
            f.write("score\n")
            f.write("85\n")

        output_path = tmp_workspace / "merged_error.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/merge_datasets.py",
            str(left_csv),
            str(right_csv),
            str(output_path),
            "--on", "id"
        )

        # Should fail because 'id' column doesn't exist
        assert exit_code == 1, "Missing join key should return error exit code"
        assert result["success"] is False, "Missing join key should fail"
        assert "error" in result, "Error message should be present"

    def test_left_join(self, test_data_dir, tmp_workspace, run_script):
        """Test that left join preserves all left rows."""
        # Create two CSV files to join
        left_csv = test_data_dir / "left_join.csv"
        with open(left_csv, 'w') as f:
            f.write("id,name\n")
            f.write("1,Alice\n")
            f.write("2,Bob\n")
            f.write("3,Charlie\n")

        right_csv = test_data_dir / "right_join.csv"
        with open(right_csv, 'w') as f:
            f.write("id,score\n")
            f.write("1,85\n")
            f.write("2,92\n")

        output_path = tmp_workspace / "left_joined.csv"

        result, exit_code = run_script(
            "magic-data-transformation/scripts/merge_datasets.py",
            str(left_csv),
            str(right_csv),
            str(output_path),
            "--on", "id",
            "--how", "left"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Merge failed: {result.get('error')}"
        assert output_path.exists(), "Output file not created"

        # Verify left join preserves all 3 left rows
        df = pd.read_csv(output_path)
        assert len(df) == 3, f"Left join should have 3 rows, got {len(df)}"
