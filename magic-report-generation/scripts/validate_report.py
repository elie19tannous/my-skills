#!/usr/bin/env python3
"""
SCRIPTABLE TOOL — validate_report.py
Validate report markdown completeness.

Checks mandatory sections, word count range, and section header formatting.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Mandatory sections and their accepted alternative names
MANDATORY_SECTIONS = [
    {
        "canonical": "Summary",
        "aliases": ["summary"]
    },
    {
        "canonical": "Data Provenance",
        "aliases": ["data provenance", "provenance"]
    },
    {
        "canonical": "Methodology",
        "aliases": ["methodology"]
    },
    {
        "canonical": "Key Findings",
        "aliases": ["key findings", "findings"]
    },
    {
        "canonical": "Caveats",
        "aliases": ["caveats", "caveats and limitations"]
    },
    {
        "canonical": "Next Steps",
        "aliases": ["next steps"]
    },
]

# Word count range per template
WORD_COUNT_RANGES = {
    "standard": (300, 600),
    "executive": (200, 400),
    "technical": (400, 800),
}

DEFAULT_WORD_COUNT_RANGE = (400, 800)


def extract_section_headers(content):
    """Extract all section headers (## or ### prefix) from markdown content."""
    pattern = re.compile(r'^#{2,3}\s+(.+)$', re.MULTILINE)
    return [m.group(1).strip() for m in pattern.finditer(content)]


def check_section_present(headers, section_spec):
    """Check if a section is present in the headers list (case-insensitive)."""
    headers_lower = [h.lower() for h in headers]
    for alias in section_spec["aliases"]:
        if alias.lower() in headers_lower:
            return True
    return False


def count_words(content):
    """Count words in markdown content (excluding header markers and code blocks)."""
    # Strip code blocks
    content_no_code = re.sub(r'```[\s\S]*?```', '', content)
    # Strip inline code
    content_no_code = re.sub(r'`[^`]*`', '', content_no_code)
    # Strip markdown formatting characters but keep words
    content_clean = re.sub(r'[#*_~>\-]', ' ', content_no_code)
    words = content_clean.split()
    return len(words)


def main(report_path: str, output_path: str, template: str = "technical") -> dict:
    """
    Validate report markdown completeness.

    Args:
        report_path: Path to the markdown report file
        output_path: Path to save validation report JSON
        template: Template name to determine acceptable word count range

    Returns:
        Result dictionary with validation results
    """
    try:
        # Check report file exists
        report_file = Path(report_path)
        if not report_file.exists():
            return {
                "success": False,
                "error": f"Report file not found: {report_path}",
                "suggestion": "Verify the report markdown file path exists"
            }

        # Load report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return {
                "success": False,
                "error": "Report file is empty",
                "suggestion": "Provide a non-empty markdown report for validation"
            }

        checks_passed = 0
        checks_failed = 0
        failures = []

        # --- Check: section headers present ---
        headers = extract_section_headers(content)
        sections_found = []
        sections_missing = []

        for section_spec in MANDATORY_SECTIONS:
            if check_section_present(headers, section_spec):
                sections_found.append(section_spec["canonical"])
                checks_passed += 1
            else:
                sections_missing.append(section_spec["canonical"])
                checks_failed += 1
                failures.append({
                    "check": f"section_present_{section_spec['canonical'].lower().replace(' ', '_')}",
                    "message": (
                        f"Missing mandatory section: '{section_spec['canonical']}' "
                        f"(also accepted: {', '.join(repr(a) for a in section_spec['aliases'])})"
                    )
                })

        # --- Check: word count within acceptable range ---
        word_count = count_words(content)
        word_range = WORD_COUNT_RANGES.get(template, DEFAULT_WORD_COUNT_RANGE)
        min_words, max_words = word_range

        if min_words <= word_count <= max_words:
            checks_passed += 1
        else:
            checks_failed += 1
            if word_count < min_words:
                failures.append({
                    "check": "word_count_minimum",
                    "message": (
                        f"Report word count ({word_count}) is below the minimum "
                        f"({min_words}) for template '{template}'"
                    )
                })
            else:
                failures.append({
                    "check": "word_count_maximum",
                    "message": (
                        f"Report word count ({word_count}) exceeds the maximum "
                        f"({max_words}) for template '{template}'"
                    )
                })

        # Overall validity
        is_valid = checks_failed == 0

        result = {
            "success": True,
            "output_path": str(output_path),
            "valid": is_valid,
            "template": template,
            "word_count": word_count,
            "word_count_range": {"min": min_words, "max": max_words},
            "sections_found": sections_found,
            "sections_missing": sections_missing,
            "all_headers_found": headers,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "failures": failures
        }

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check that the report file path is correct"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and report structure"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate report markdown completeness")
    parser.add_argument("report_path", help="Path to the markdown report file")
    parser.add_argument("output_path", help="Path to output validation report JSON")
    parser.add_argument("--template", default="technical",
                        choices=["standard", "executive", "technical"],
                        help="Report template to validate against (default: technical)")

    args = parser.parse_args()

    result = main(args.report_path, args.output_path, args.template)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
