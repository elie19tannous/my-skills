#!/usr/bin/env python3
"""
Unit tests for distribution_analysis.py script.

Tests numeric distribution analysis, text distribution analysis, and error cases.
"""

import pytest


class TestDistributionAnalysis:
    """Test cases for distribution analysis script."""

    def test_numeric_distribution(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that numeric columns return skewness, kurtosis, shapiro test."""
        output_path = tmp_workspace / "distribution_result.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(sample_clean_csv),
            str(output_path),
            "--columns=age,score"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "distributions" in result, "distributions not in output"

        # Check for distribution statistics
        distributions = result["distributions"]

        # Should have numeric and/or text distributions
        assert "numeric" in distributions or "text" in distributions, "No distributions found"

        # Check that numeric statistics are present
        if "numeric" in distributions and len(distributions["numeric"]) > 0:
            for col_name, dist_data in distributions["numeric"].items():
                # Check for numeric distribution metrics
                assert "skewness" in dist_data, f"skewness not in {col_name}"
                assert "kurtosis" in dist_data, f"kurtosis not in {col_name}"
                assert "shapiro_test" in dist_data, f"shapiro_test not in {col_name}"
                break

    def test_text_distribution(self, sample_text_csv, tmp_workspace, run_script):
        """Test that text columns return length_distribution, word_count_distribution, vocabulary_size."""
        output_path = tmp_workspace / "text_distribution.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(sample_text_csv),
            str(output_path),
            "--columns=description"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "distributions" in result, "distributions not in output"

        distributions = result["distributions"]

        # Check for text-specific statistics
        assert "text" in distributions, "text distributions not found"
        assert len(distributions["text"]) > 0, "No text distributions found"

        # Check first text column
        for col_name, dist_data in distributions["text"].items():
            assert "length_distribution" in dist_data, "length_distribution not found"
            assert "word_count_distribution" in dist_data, "word_count_distribution not found"
            assert "vocabulary_size" in dist_data, "vocabulary_size not found"
            break

    def test_empty_input_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "empty_distribution.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(empty_csv),
            str(output_path)
        )

        # Empty file should fail
        assert result["success"] is False, "Empty file should fail"
        assert "error" in result, "Error message should be present"

    def test_all_columns_analysis(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that analysis works without specifying columns (analyzes all)."""
        output_path = tmp_workspace / "all_columns_dist.json"

        result, exit_code = run_script(
            "magic-data-profiling/scripts/distribution_analysis.py",
            str(sample_clean_csv),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "distributions" in result, "distributions not in output"

        distributions = result["distributions"]

        # Should analyze multiple columns (numeric and/or text)
        total_cols = len(distributions.get("numeric", {})) + len(distributions.get("text", {}))
        assert total_cols >= 1, "Expected at least one column analyzed"
