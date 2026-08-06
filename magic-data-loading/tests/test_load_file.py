#!/usr/bin/env python3
"""
Unit tests for load_file.py script.

Tests CSV loading, encoding handling, and error cases.
"""

import pytest


class TestLoadFile:
    """Test cases for file loading script."""

    def test_load_csv(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that normal CSV loads correctly with row counts."""
        output_path = tmp_workspace / "loaded_data.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Load failed: {result.get('error')}"
        assert "rows_in" in result, "rows_in not in result"
        assert result["rows_in"] >= 5, f"Expected at least 5 rows, got {result['rows_in']}"
        assert "rows_out" in result, "rows_out not in result"
        assert result["rows_out"] == result["rows_in"], "rows_out should equal rows_in for clean data"
        assert output_path.exists(), "Output file not created"

    def test_load_with_encoding(self, sample_latin1_csv, tmp_workspace, run_script):
        """Test that Latin-1 file loads with --encoding latin-1."""
        output_path = tmp_workspace / "loaded_latin1.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(sample_latin1_csv),
            str(output_path),
            "--encoding", "latin-1"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Load failed: {result.get('error')}"
        assert result["rows_in"] >= 3, f"Expected at least 3 rows, got {result['rows_in']}"
        assert output_path.exists(), "Output file not created"

    def test_empty_file_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty file produces error result."""
        output_path = tmp_workspace / "loaded_empty.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file might succeed with 0 rows or fail - both acceptable
        if result["success"]:
            assert result["rows_in"] == 0, "Empty file should have 0 rows"
        else:
            assert "error" in result, "Error message should be present"

    def test_nonexistent_file_error(self, tmp_workspace, run_script):
        """Test that nonexistent file produces error."""
        fake_path = tmp_workspace / "nonexistent.csv"
        output_path = tmp_workspace / "loaded_fake.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(fake_path),
            str(output_path)
        )

        assert exit_code == 1, "Nonexistent file should return error exit code"
        assert result["success"] is False, "Nonexistent file should fail"
        assert "error" in result, "Error message should be present"

    def test_jsonl_loading(self, sample_jsonl, tmp_workspace, run_script):
        """Test that JSONL file loads correctly."""
        output_path = tmp_workspace / "loaded_jsonl.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/load_file.py",
            str(sample_jsonl),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Load failed: {result.get('error')}"
        assert result["rows_in"] >= 3, f"Expected at least 3 rows, got {result['rows_in']}"
        assert output_path.exists(), "Output file not created"
