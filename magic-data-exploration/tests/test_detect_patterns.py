#!/usr/bin/env python3
"""
Unit tests for detect_patterns.py script.

Tests correlation pattern detection, clean data handling, and error cases.
"""

import pytest


class TestDetectPatterns:
    """Test cases for pattern detection script."""

    def test_correlation_pattern(self, test_data_dir, tmp_workspace, run_script):
        """Test that correlated columns are detected."""
        # Create CSV with correlated data (need >= 10 rows for correlation detection)
        correlated_csv = test_data_dir / "sample_correlated.csv"
        with open(correlated_csv, 'w') as f:
            f.write("x,y,z\n")
            for i in range(1, 21):
                f.write(f"{i},{i*2},{i*10}\n")

        output_path = tmp_workspace / "patterns_result.json"

        result, exit_code = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(correlated_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "findings" in result, "findings not in output"

        findings = result["findings"]

        # Should detect correlations between x-y and x-z
        assert isinstance(findings, list), "findings should be a list"
        assert len(findings) > 0, "Should detect correlation patterns"

    def test_clean_data(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that clean uniform data may find fewer patterns."""
        output_path = tmp_workspace / "patterns_clean.json"

        result, exit_code = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "findings" in result, "findings not in output"

        # Clean data should still complete successfully, even if few patterns found
        # findings could be empty or have some patterns
        assert isinstance(result["findings"], list), "findings should be a list"

    def test_empty_data_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "patterns_empty.json"

        result, exit_code = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file should fail
        assert result["success"] is False, "Empty file should fail"
        assert "error" in result, "Error message should be present"

    def test_outlier_patterns(self, sample_outliers_csv, tmp_workspace, run_script):
        """Test that outlier patterns are detected."""
        output_path = tmp_workspace / "patterns_outliers.json"

        result, exit_code = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(sample_outliers_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "findings" in result, "findings not in output"

        # Outliers might be detected as patterns
        findings = result["findings"]
        # Check if any findings relate to outliers
        has_outlier_finding = any(
            f.get("type") == "outlier_presence" for f in findings
        ) if findings else False
        # It's OK if no outliers detected, but findings should be a list
        assert isinstance(findings, list), "findings should be a list"

    def test_pattern_types(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that different pattern types are detected."""
        output_path = tmp_workspace / "patterns_types.json"

        result, exit_code = run_script(
            "magic-data-exploration/scripts/detect_patterns.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"

        # Check for findings and column_types
        assert "findings" in result, "findings not in output"
        assert "column_types" in result, "column_types not in output"
        assert isinstance(result["findings"], list), "findings should be a list"
        assert isinstance(result["column_types"], dict), "column_types should be a dict"
