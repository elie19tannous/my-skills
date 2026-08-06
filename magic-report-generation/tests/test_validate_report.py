#!/usr/bin/env python3
"""Unit tests for skills/magic-report-generation/scripts/validate_report.py."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "validate_report.py"
)


class TestValidateReport:
    """Tests for validate_report.py script."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_report(self, filename, content):
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True, text=True, timeout=30
        )
        return result

    def _build_full_report(self, word_count_target=500):
        """Build a valid report markdown with all 6 mandatory sections.

        Generates enough words to fall within the technical template range (400-800).
        """
        # Generate filler paragraphs to reach the target word count
        filler = " ".join(["analysis"] * 50)  # 50 words per block
        blocks_needed = max(1, (word_count_target - 50) // 50)
        body = "\n\n".join([filler for _ in range(blocks_needed)])

        return f"""# Report Title

## Summary

{body}

## Data Provenance

The data was sourced from internal records covering the full fiscal year.

## Methodology

We applied standard descriptive statistics and regression analysis.

## Key Findings

Revenue grew by 15% year over year. Cost remained stable.

## Caveats

Sample size is limited to a single region. Results may not generalize.

## Next Steps

Expand analysis to cover all regions. Collect more data.
"""

    def test_valid_report_all_sections(self):
        """A report with all 6 mandatory sections and enough words should pass."""
        content = self._build_full_report(word_count_target=500)
        report_path = self._make_report("report.md", content)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(report_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["valid"] is True
        assert result["checks_failed"] == 0
        assert len(result["sections_found"]) == 6
        assert len(result["sections_missing"]) == 0

    def test_missing_sections_flagged(self):
        """A report missing some mandatory sections should fail."""
        content = """# Report

## Summary

""" + " ".join(["word"] * 500) + """

## Key Findings

Some findings here.
"""
        report_path = self._make_report("incomplete.md", content)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(report_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["valid"] is False
        assert result["checks_failed"] >= 1
        # Should be missing: Data Provenance, Methodology, Caveats, Next Steps
        assert len(result["sections_missing"]) >= 3
        # Check specific missing sections
        for expected_missing in ["Data Provenance", "Methodology", "Caveats", "Next Steps"]:
            assert expected_missing in result["sections_missing"], \
                f"Expected '{expected_missing}' to be in sections_missing"

    def test_word_count_too_few(self):
        """A report with too few words should fail the word count check."""
        content = """# Report

## Summary

Short.

## Data Provenance

Brief.

## Methodology

Quick.

## Key Findings

One finding.

## Caveats

None.

## Next Steps

Done.
"""
        report_path = self._make_report("short.md", content)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(report_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["valid"] is False
        # word_count should be well below the minimum of 400
        assert result["word_count"] < 400
        # There should be a word_count_minimum failure
        wc_failures = [
            f for f in result["failures"]
            if f["check"] == "word_count_minimum"
        ]
        assert len(wc_failures) == 1

    def test_empty_report_error(self):
        """An empty report file should produce an error."""
        report_path = self._make_report("empty.md", "")
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(report_path, output_path)
        result = json.loads(proc.stdout)

        # Empty content should fail
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_section_alias_accepted(self):
        """Aliases like 'Findings' instead of 'Key Findings' should be accepted."""
        filler = " ".join(["data"] * 80)
        content = f"""# Report

## Summary

{filler}

## Provenance

{filler}

## Methodology

{filler}

## Findings

{filler}

## Caveats and Limitations

{filler}

## Next Steps

{filler}
"""
        report_path = self._make_report("aliased.md", content)
        output_path = os.path.join(self.tmpdir, "validation.json")

        proc = self.run_script(report_path, output_path)
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        # 'Provenance' is an alias for 'Data Provenance'
        # 'Findings' is an alias for 'Key Findings'
        # 'Caveats and Limitations' is an alias for 'Caveats'
        assert "Data Provenance" in result["sections_found"]
        assert "Key Findings" in result["sections_found"]
        assert "Caveats" in result["sections_found"]
