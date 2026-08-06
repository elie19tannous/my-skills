#!/usr/bin/env python3
"""
Unit tests for detect_format.py script.

Tests format detection, encoding detection, and delimiter detection.
"""

import pytest


class TestDetectFormat:
    """Test cases for format detection script."""

    def test_csv_detection(self, tmp_workspace, run_script):
        """Test that normal CSV file is detected correctly."""
        # Create a test CSV directly in the test to control column count
        csv_path = tmp_workspace / "test_detect.csv"
        with open(csv_path, 'w') as f:
            f.write("id,name,age,score\n")
            f.write("1,Alice,25,85.5\n")
            f.write("2,Bob,30,92.0\n")
            f.write("3,Charlie,35,78.3\n")
            f.write("4,Diana,28,88.7\n")
            f.write("5,Eve,32,95.2\n")

        output_path = tmp_workspace / "detect_result.json"

        result, exit_code = run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(csv_path),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert result["format"] == "csv", "CSV format not detected"
        assert result["encoding"] in ["utf-8", "ascii"], f"Unexpected encoding: {result['encoding']}"
        assert result["delimiter"] == ",", "CSV delimiter not detected as comma"
        assert result["has_header"] is True, "Header not detected"
        assert result["estimated_rows"] >= 5, "Row count estimation incorrect"
        assert result["columns_detected"] == 4, "Column count incorrect"

    def test_encoding_detection(self, sample_latin1_csv, tmp_workspace, run_script):
        """Test that Latin-1 encoded file is detected correctly."""
        output_path = tmp_workspace / "detect_latin1.json"

        result, exit_code = run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(sample_latin1_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        # chardet may return several Latin-1 / ISO-8859 family names depending
        # on its version and confidence. Accept any non-UTF-8 single-byte encoding.
        detected = result["encoding"].lower().replace("-", "").replace("_", "")
        latin1_family = {
            "latin1", "iso88591", "iso885915", "windows1252", "cp1252",
            "iso88591", "iso8859", "cp819", "csisolatin1",
        }
        assert any(name in detected or detected.startswith(name[:6])
                   for name in latin1_family), \
            f"Latin-1 family encoding not detected, got: {result['encoding']}"

    def test_delimiter_detection(self, test_data_dir, tmp_workspace, run_script):
        """Test that TSV/semicolon-delimited file is detected correctly."""
        # Create a TSV file
        tsv_path = test_data_dir / "sample.tsv"
        with open(tsv_path, 'w') as f:
            f.write("id\tname\tvalue\n")
            f.write("1\tAlice\t100\n")
            f.write("2\tBob\t200\n")

        output_path = tmp_workspace / "detect_tsv.json"

        result, exit_code = run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(tsv_path),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert result["format"] == "tsv", "TSV format not detected"
        assert result["delimiter"] == "\t", "Tab delimiter not detected"

    def test_empty_file_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty file produces appropriate result."""
        output_path = tmp_workspace / "detect_empty.json"

        result, exit_code = run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file should still succeed but with limited detection
        assert result["success"] is True, "Empty file should not fail detection"
        assert result["estimated_rows"] == 0, "Empty file should have 0 rows"
        assert result["file_size_mb"] == 0, "Empty file should have 0 MB size"

    def test_nonexistent_file_error(self, tmp_workspace, run_script):
        """Test that nonexistent file produces error."""
        output_path = tmp_workspace / "detect_nonexistent.json"
        fake_path = tmp_workspace / "nonexistent.csv"

        result, exit_code = run_script(
            "magic-data-loading/scripts/detect_format.py",
            str(fake_path),
            str(output_path)
        )

        assert exit_code == 1, "Nonexistent file should return error exit code"
        assert result["success"] is False, "Nonexistent file should fail"
        assert "error" in result, "Error message should be present"
        assert "not found" in result["error"].lower(), "Error should mention file not found"
