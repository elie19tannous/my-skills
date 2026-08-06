#!/usr/bin/env python3
"""
Unit tests for generate_report.py script.

Tests standard report generation, missing findings handling, and template variations.
"""

import pytest
import json


class TestGenerateReport:
    """Test cases for report generation script."""

    def test_standard_report(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that standard template generates all 6 mandatory sections."""
        # Create findings file with correct structure expected by generate_report.py
        findings = {
            "summary": "Analysis of 5 records across 4 variables showing clean data with no missing values.",
            "data_source": {
                "file": str(sample_clean_csv),
                "rows": 5,
                "columns": 4,
                "processing_steps": ["Loaded CSV file", "Validated data types"]
            },
            "methodology": "Statistical analysis performed on cleaned dataset using standard methods.",
            "assumptions": [
                "Data is representative of population",
                "Missing values handled appropriately"
            ],
            "key_findings": [
                {
                    "title": "Clean Data Quality",
                    "description": "Data is clean with no missing values across all columns.",
                    "evidence": "0% missing values detected in profiling"
                },
                {
                    "title": "Normal Distributions",
                    "description": "All numeric columns show approximately normal distributions.",
                    "evidence": "Skewness < 0.5 for age and score columns"
                }
            ],
            "caveats": [
                "Results are based on the quality and completeness of the input data",
                "Sample size is small (n=5)"
            ],
            "next_steps": [
                "Data is ready for analysis",
                "No cleaning required",
                "Proceed with statistical modeling"
            ]
        }

        findings_path = tmp_workspace / "findings.json"
        with open(findings_path, 'w') as f:
            json.dump(findings, f, indent=2)

        output_path = tmp_workspace / "report.md"

        result, exit_code = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path),
            str(output_path),
            "--template", "standard"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Report generation failed: {result.get('error')}"
        assert output_path.exists(), "Output report file not created"

        # Check result structure
        assert "sections" in result, "Result should include sections list"
        assert "word_count" in result, "Result should include word_count"
        assert "charts_embedded" in result, "Result should include charts_embedded"

        # Read report content
        with open(output_path, 'r') as f:
            report_content = f.read()

        # Check for standard template sections (these are the actual sections in STANDARD_TEMPLATE)
        standard_sections = [
            "Summary",
            "Data Provenance",
            "Methodology",
            "Key Findings",
            "Caveats and Limitations",
            "Next Steps"
        ]

        for section in standard_sections:
            assert section in report_content, \
                f"Section '{section}' not found in report"

    def test_missing_findings(self, tmp_workspace, run_script):
        """Test that missing findings are handled gracefully."""
        # Create minimal findings (script will auto-generate missing sections)
        findings = {
            "data_source": {
                "file": "test.csv",
                "rows": 5,
                "columns": 4
            }
        }

        findings_path = tmp_workspace / "minimal_findings.json"
        with open(findings_path, 'w') as f:
            json.dump(findings, f, indent=2)

        output_path = tmp_workspace / "minimal_report.md"

        result, exit_code = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path),
            str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Report generation failed: {result.get('error')}"
        assert output_path.exists(), "Output report file not created"

        # Read report content
        with open(output_path, 'r') as f:
            report_content = f.read()

        # Report should still be generated even with minimal findings
        # Script auto-generates summary, methodology, findings, caveats, and next_steps
        assert len(report_content) > 0, "Report should have content even with minimal findings"
        assert "Data Provenance" in report_content, "Should have data provenance section"

    def test_executive_template(self, tmp_workspace, run_script):
        """Test that executive template generates concise report."""
        # Create findings with correct structure
        findings = {
            "summary": "Analysis of 100 records showing good data quality with minor cleaning needed.",
            "data_source": {
                "file": "test_data.csv",
                "rows": 100,
                "columns": 10
            },
            "key_findings": [
                {
                    "title": "Good Data Quality",
                    "description": "Overall data quality is good with 85% quality score."
                },
                {
                    "title": "Minor Cleaning Required",
                    "description": "Some minor cleaning needed to handle 2% missing values."
                },
                {
                    "title": "Ready for Analysis",
                    "description": "Data is suitable for proceeding with analysis after minor fixes."
                }
            ],
            "caveats": [
                "Missing values present in 2% of records",
                "Data quality assessment is preliminary"
            ],
            "next_steps": [
                "Handle 2% missing values",
                "Proceed with analysis",
                "Monitor data quality over time"
            ]
        }

        findings_path = tmp_workspace / "exec_findings.json"
        with open(findings_path, 'w') as f:
            json.dump(findings, f, indent=2)

        output_path = tmp_workspace / "exec_report.md"

        result, exit_code = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path),
            str(output_path),
            "--template", "executive"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Report generation failed: {result.get('error')}"
        assert output_path.exists(), "Output report file not created"

        # Read report content
        with open(output_path, 'r') as f:
            report_content = f.read()

        # Executive report should be concise
        assert len(report_content) > 0, "Executive report should have content"

        # Check for executive template sections (from EXECUTIVE_TEMPLATE)
        executive_sections = ["Executive Summary", "Key Findings", "Action Items", "Limitations", "Data Overview"]

        for section in executive_sections:
            assert section in report_content, f"Section '{section}' not found in executive report"

    def test_empty_findings_error(self, tmp_workspace, run_script):
        """Test that empty findings produce error or minimal report."""
        findings_path = tmp_workspace / "empty_findings.json"
        with open(findings_path, 'w') as f:
            json.dump({}, f)

        output_path = tmp_workspace / "empty_report.md"

        result, exit_code = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path),
            str(output_path)
        )

        # Empty findings should either fail or produce minimal report
        if result["success"]:
            assert output_path.exists(), "Output report file should be created"
        else:
            assert "error" in result, "Error message should be present"

    def test_custom_title(self, tmp_workspace, run_script):
        """Test that custom report title works."""
        findings = {
            "data_source": {
                "file": "test.csv",
                "rows": 50,
                "columns": 5
            },
            "key_findings": [
                {
                    "title": "Test Finding",
                    "description": "This is a test finding for the report."
                }
            ]
        }

        findings_path = tmp_workspace / "custom_findings.json"
        with open(findings_path, 'w') as f:
            json.dump(findings, f, indent=2)

        output_path = tmp_workspace / "custom_report.md"

        result, exit_code = run_script(
            "magic-report-generation/scripts/generate_report.py",
            str(findings_path),
            str(output_path),
            "--title", "Custom Data Analysis Report"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Report generation failed: {result.get('error')}"
        assert output_path.exists(), "Output report file not created"

        # Check for custom title
        with open(output_path, 'r') as f:
            report_content = f.read()

        # Custom title should appear in report (as markdown H1 header)
        assert "# Custom Data Analysis Report" in report_content, \
               "Custom title not found in report"
