#!/usr/bin/env python3
"""
Unit tests for descriptive_stats.py script.

Tests numeric statistics, text statistics, and error cases.
"""

import pytest


class TestDescriptiveStats:
    """Test cases for descriptive statistics script."""

    def test_numeric_stats(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that numeric columns return mean, median, std, etc."""
        output_path = tmp_workspace / "stats_result.json"

        result, exit_code = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(sample_clean_csv),
            "--output", str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "statistics" in result, "Statistics not in output"

        stats = result["statistics"]

        # Statistics are organized by type: numeric, text, categorical
        assert "numeric" in stats or "text" in stats or "categorical" in stats, \
            "Statistics should have type categories"

        # Check for numeric statistics (age and score should be numeric)
        if "numeric" in stats:
            numeric_stats = stats["numeric"]
            assert len(numeric_stats) > 0, "Should have numeric column statistics"

            # Check one numeric column has required fields
            for col_name, col_stats in numeric_stats.items():
                assert "mean" in col_stats, f"Column '{col_name}' should have mean"
                assert "median" in col_stats, f"Column '{col_name}' should have median"
                assert "std" in col_stats, f"Column '{col_name}' should have std"
                assert "min" in col_stats, f"Column '{col_name}' should have min"
                assert "max" in col_stats, f"Column '{col_name}' should have max"
                assert "count" in col_stats, f"Column '{col_name}' should have count"
                assert "narrative" in col_stats, f"Column '{col_name}' should have narrative"
                break  # Check at least one column

    def test_text_stats(self, sample_text_csv, tmp_workspace, run_script):
        """Test that text columns return word count, vocabulary, top terms."""
        output_path = tmp_workspace / "stats_text.json"

        result, exit_code = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(sample_text_csv),
            "--output", str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "statistics" in result, "Statistics not in output"

        stats = result["statistics"]

        # Text columns should appear in text or categorical section
        has_text_or_categorical = "text" in stats or "categorical" in stats
        assert has_text_or_categorical, "Should have text or categorical statistics"

        # Check for text-specific statistics
        if "text" in stats:
            text_stats = stats["text"]
            assert len(text_stats) > 0, "Should have text column statistics"

            # Check one text column has required fields
            for col_name, col_stats in text_stats.items():
                assert "count" in col_stats, f"Column '{col_name}' should have count"
                assert "avg_word_count" in col_stats, f"Column '{col_name}' should have avg_word_count"
                assert "vocabulary_size" in col_stats, f"Column '{col_name}' should have vocabulary_size"
                assert "top_10_terms" in col_stats, f"Column '{col_name}' should have top_10_terms"
                assert "narrative" in col_stats, f"Column '{col_name}' should have narrative"
                break  # Check at least one column

    def test_empty_data_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "stats_empty.json"

        result, exit_code = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(empty_csv),
            "--output", str(output_path)
        )

        # Empty file should fail with an error
        assert result["success"] is False, "Empty file should fail"
        assert "error" in result, "Error message should be present"

    def test_comprehensive_stats(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that comprehensive statistics are generated."""
        output_path = tmp_workspace / "stats_comprehensive.json"

        result, exit_code = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(sample_clean_csv),
            "--output", str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "statistics" in result, "Statistics not in output"

        stats = result["statistics"]

        # Count total columns analyzed across all types
        total_columns = sum(len(stats.get(type_key, {})) for type_key in ["numeric", "text", "categorical"])

        # Should have stats for multiple columns (sample_clean.csv has 4 columns: id, name, age, score)
        assert total_columns >= 2, f"Expected stats for multiple columns, got {total_columns}"

        # Should have caveats
        assert "caveats" in result, "Result should include caveats"
        assert len(result["caveats"]) > 0, "Should have at least one caveat"

    def test_column_specific_stats(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that statistics can be generated for specific columns."""
        output_path = tmp_workspace / "stats_specific.json"

        result, exit_code = run_script(
            "magic-statistical-analysis/scripts/descriptive_stats.py",
            "--input", str(sample_clean_csv),
            "--output", str(output_path),
            "--columns", "age,score"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Analysis failed: {result.get('error')}"
        assert "statistics" in result, "Statistics not in output"

        stats = result["statistics"]

        # Count total columns analyzed
        total_columns = sum(len(stats.get(type_key, {})) for type_key in ["numeric", "text", "categorical"])

        # Should have stats only for requested columns (age and score, both numeric)
        assert total_columns == 2, f"Expected stats for 2 columns, got {total_columns}"

        # age and score should be in numeric section
        if "numeric" in stats:
            numeric_cols = set(stats["numeric"].keys())
            assert "age" in numeric_cols or "score" in numeric_cols, \
                "Should have statistics for requested numeric columns"
