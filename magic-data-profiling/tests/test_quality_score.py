#!/usr/bin/env python3
"""
Unit tests for quality_score.py script.

Tests quality scoring with clean data, low quality data, and error cases.
"""

import pytest


class TestQualityScore:
    """Test cases for quality score script."""

    def test_high_quality_data(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that clean data scores > 80 with grade A or B."""
        output_path = tmp_workspace / "quality_result.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Scoring failed: {result.get('error')}"
        assert "overall_score" in result, "overall_score not in output"

        score = result["overall_score"]

        assert score >= 80, f"Clean data should score >= 80, got {score}"

        # Check for grade
        assert "grade" in result, "grade not in output"
        assert result["grade"] in ["A", "B"], f"Clean data should get grade A or B, got {result['grade']}"

    def test_low_quality_data(self, sample_missing_csv, tmp_workspace, run_script):
        """Test that data with missing values scores lower."""
        output_path = tmp_workspace / "quality_missing.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(sample_missing_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Scoring failed: {result.get('error')}"
        assert "overall_score" in result, "overall_score not in output"

        score = result["overall_score"]

        # Data with missing values should score lower than clean data
        assert score < 100, f"Data with missing values should score < 100, got {score}"

        # Check that dimensions are reported
        assert "dimensions" in result, "dimensions not in output"
        assert "completeness" in result["dimensions"], "completeness dimension not found"

    def test_empty_input_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "quality_empty.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file should fail
        assert result["success"] is False, "Empty file should fail"
        assert "error" in result, "Error message should be present"

    def test_quality_components(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that quality score includes component scores."""
        output_path = tmp_workspace / "quality_components.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/quality_score.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Scoring failed: {result.get('error')}"

        # Check for quality score components (completeness, consistency, etc.)
        assert "dimensions" in result, "dimensions not in output"
        assert "completeness" in result["dimensions"], "completeness not in dimensions"
        assert "consistency" in result["dimensions"], "consistency not in dimensions"
        assert "uniqueness" in result["dimensions"], "uniqueness not in dimensions"
        assert "validity" in result["dimensions"], "validity not in dimensions"
