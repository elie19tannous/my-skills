#!/usr/bin/env python3
"""
Unit tests for detect_issues.py script.

Tests missing value detection, duplicate detection, and clean data handling.
"""

import pytest


class TestDetectIssues:
    """Test cases for issue detection script."""

    def test_missing_values_detected(self, sample_missing_csv, tmp_workspace, run_script):
        """Test that data with missing values reports correct counts."""
        output_path = tmp_workspace / "issues_missing.json"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(sample_missing_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "issues" in result, "issues not in output"

        # Check for missing value counts
        issues = result["issues"]
        assert "missing_values" in issues, "missing_values not in issues"
        missing_info = issues["missing_values"]
        assert missing_info["total_missing"] > 0, "Missing values should be detected"

    def test_duplicates_detected(self, test_data_dir, tmp_workspace, run_script):
        """Test that data with duplicates reports correct count."""
        # Create a CSV with duplicates
        dup_csv = test_data_dir / "sample_duplicates.csv"
        with open(dup_csv, 'w') as f:
            f.write("id,name,value\n")
            f.write("1,Alice,100\n")
            f.write("2,Bob,200\n")
            f.write("1,Alice,100\n")  # Duplicate
            f.write("3,Charlie,300\n")
            f.write("2,Bob,200\n")  # Duplicate

        output_path = tmp_workspace / "issues_duplicates.json"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(dup_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "issues" in result, "issues not in output"

        # Check for duplicate detection
        issues = result["issues"]
        assert "duplicates" in issues, "duplicates not in issues"
        dup_info = issues["duplicates"]
        assert dup_info["count"] > 0, "Duplicates should be detected"

    def test_clean_data_no_issues(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that clean data reports 0 issues."""
        output_path = tmp_workspace / "issues_clean.json"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "issues" in result, "issues not in output"

        # Check that no major issues are found
        issues = result["issues"]
        assert "missing_values" in issues, "missing_values not in issues"
        missing_info = issues["missing_values"]
        assert missing_info["total_missing"] == 0, "Clean data should have no missing values"

        assert "duplicates" in issues, "duplicates not in issues"
        dup_info = issues["duplicates"]
        assert dup_info["count"] == 0, "Clean data should have no duplicates"

    def test_comprehensive_issue_check(self, sample_outliers_csv, tmp_workspace, run_script):
        """Test that outliers are detected as potential issues."""
        output_path = tmp_workspace / "issues_outliers.json"

        result, exit_code = run_script(
            "magic-data-cleaning/scripts/detect_issues.py",
            str(sample_outliers_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Detection failed: {result.get('error')}"
        assert "issues" in result, "issues not in output"

        # Outliers should be detected as issues
        issues = result["issues"]
        assert "outliers" in issues, "outliers not in issues"
        outlier_info = issues["outliers"]
        assert "affected_columns" in outlier_info, "affected_columns not in outliers"
        # Should detect outliers in the value column
        assert len(outlier_info["affected_columns"]) > 0, "Outliers should be detected"
