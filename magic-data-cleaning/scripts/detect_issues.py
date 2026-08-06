#!/usr/bin/env python3
"""
Data quality issue detection script.
Scans data for missing values, duplicates, type errors, text issues, and outliers.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import re
import time
import pandas as pd
import numpy as np

def load_dataframe(path, **kwargs):
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def load_data(input_path, input_format="auto"):
    """Load data using io_utils, supporting CSV, JSONL, JSON, Parquet, TSV, Excel."""
    return load_dataframe(input_path, format=input_format)


def detect_jsonl_issues(df, input_path):
    """Detect JSONL-specific issues like malformed lines and schema drift."""
    issues = []
    ext = os.path.splitext(input_path)[1].lower()
    if ext != '.jsonl':
        return issues

    # Check for schema drift (different field sets across records)
    field_sets = set()
    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                obj = json.loads(line.strip())
                field_sets.add(frozenset(obj.keys()))
            except json.JSONDecodeError:
                issues.append({
                    "type": "malformed_json_line",
                    "severity": "high",
                    "line": i + 1,
                    "description": f"Line {i+1} is not valid JSON"
                })

    if len(field_sets) > 1:
        issues.append({
            "type": "schema_drift",
            "severity": "medium",
            "unique_schemas": len(field_sets),
            "description": f"Found {len(field_sets)} different field sets across records"
        })

    return issues


def detect_missing_values(df):
    """Detect missing values and categorize by severity."""
    missing_info = {}
    total_missing = 0

    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            missing_pct = (missing_count / len(df)) * 100

            # Severity based on percentage
            if missing_pct < 5:
                severity = "low"
            elif missing_pct < 20:
                severity = "medium"
            else:
                severity = "high"

            missing_info[col] = {
                "count": int(missing_count),
                "pct": round(missing_pct, 2),
                "severity": severity
            }
            total_missing += missing_count

    return {
        "affected_columns": missing_info,
        "total_missing": int(total_missing)
    }


def detect_duplicates(df):
    """Detect duplicate rows."""
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0

    if duplicate_pct < 5:
        severity = "low"
    elif duplicate_pct < 20:
        severity = "medium"
    else:
        severity = "high"

    return {
        "count": int(duplicate_count),
        "pct": round(duplicate_pct, 2),
        "severity": severity
    }


def detect_type_errors(df):
    """Detect type inconsistencies in numeric columns."""
    type_errors = {}

    # Common null-like strings to check
    null_strings = ["n/a", "null", "none", "unknown", "na", "nan", "n.a.", "nil"]

    for col in df.columns:
        # Try to infer if column should be numeric
        non_null_values = df[col].dropna()
        if len(non_null_values) == 0:
            continue

        # Check if column looks numeric but has string values
        string_values = non_null_values.astype(str)

        # Check for null-like strings
        null_like_found = []
        for null_str in null_strings:
            matches = string_values.str.lower().str.strip() == null_str
            if matches.any():
                null_like_found.append(null_str)

        if null_like_found:
            # Try to convert remaining values to numeric
            non_null_mask = ~string_values.str.lower().str.strip().isin(null_strings)
            test_values = string_values[non_null_mask]

            if len(test_values) > 0:
                # Try numeric conversion
                try:
                    pd.to_numeric(test_values, errors='raise')
                    expected_type = "numeric"

                    type_errors[col] = {
                        "expected": expected_type,
                        "found": null_like_found,
                        "count": int(string_values.str.lower().str.strip().isin(null_strings).sum())
                    }
                except (ValueError, TypeError):
                    pass  # Not a numeric column, skip

    return {"affected_columns": type_errors}


def detect_text_issues(df):
    """Detect text-related issues: whitespace, empty strings, encoding problems."""
    text_issues = {}

    for col in df.columns:
        # Only check string columns
        if df[col].dtype != object:
            continue

        non_null_values = df[col].dropna()
        if len(non_null_values) == 0:
            continue

        string_values = non_null_values.astype(str)

        # Check for whitespace issues
        whitespace_count = 0
        for val in string_values:
            if val != val.strip() or '  ' in val:
                whitespace_count += 1

        # Check for empty strings
        empty_count = (string_values.str.strip() == '').sum()

        # Check for encoding issues (mojibake patterns)
        encoding_count = 0
        mojibake_patterns = [
            r'Ã©',  # é encoded as Latin-1
            r'Ã¨',  # è
            r'Ã ',  # à
            r'â€™',  # '
            r'â€"',  # –
            r'Â',   # non-breaking space
        ]

        for val in string_values:
            for pattern in mojibake_patterns:
                if re.search(pattern, val):
                    encoding_count += 1
                    break

        if whitespace_count > 0 or empty_count > 0 or encoding_count > 0:
            text_issues[col] = {
                "whitespace": int(whitespace_count),
                "empty_strings": int(empty_count),
                "encoding_issues": int(encoding_count)
            }

    return {"affected_columns": text_issues}


def detect_outliers(df):
    """Detect outliers using IQR method for numeric columns."""
    outliers = {}

    for col in df.columns:
        # Only check numeric columns, excluding boolean
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        # Skip boolean columns (numpy doesn't support arithmetic on bools)
        if df[col].dtype == bool:
            continue

        non_null_values = df[col].dropna()
        if len(non_null_values) < 4:  # Need at least 4 values for quartiles
            continue

        # IQR method
        Q1 = non_null_values.quantile(0.25)
        Q3 = non_null_values.quantile(0.75)
        IQR = Q3 - Q1

        if IQR == 0:  # All values are the same
            continue

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        outlier_count = outlier_mask.sum()

        if outlier_count > 0:
            outlier_pct = (outlier_count / len(df)) * 100
            outliers[col] = {
                "count": int(outlier_count),
                "pct": round(outlier_pct, 2)
            }

    return {"affected_columns": outliers}


def main(input_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Main function to detect data quality issues.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output JSON file with issue report
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Dictionary with success status and issue details
    """
    try:
        # Read input data
        df = load_data(input_path, input_format)

        # Quality gate: check for empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        rows_in = len(df)

        # Detect various issues
        missing_values = detect_missing_values(df)
        duplicates = detect_duplicates(df)
        type_errors = detect_type_errors(df)
        text_issues = detect_text_issues(df)
        outliers = detect_outliers(df)
        jsonl_issues = detect_jsonl_issues(df, input_path)

        # Calculate total issues
        total_issues = (
            missing_values["total_missing"] +
            duplicates["count"] +
            sum(info["count"] for info in type_errors["affected_columns"].values()) +
            sum(
                info["whitespace"] + info["empty_strings"] + info["encoding_issues"]
                for info in text_issues["affected_columns"].values()
            ) +
            sum(info["count"] for info in outliers["affected_columns"].values()) +
            len(jsonl_issues)
        )

        # Build result
        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_in,  # No rows removed in detection
            "total_issues": int(total_issues),
            "issues": {
                "missing_values": missing_values,
                "duplicates": duplicates,
                "type_errors": type_errors,
                "text_issues": text_issues,
                "outliers": outliers,
                "jsonl_issues": jsonl_issues
            }
        }

        # Write output
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check that the file path is correct"
        }
    except pd.errors.EmptyDataError:
        return {
            "success": False,
            "error": "Input file is empty or invalid",
            "suggestion": "Provide a valid CSV file with data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and try again"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect data quality issues")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(args.input_path, args.output_path, input_format=args.input_format)

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            meta = {
                "script": os.path.relpath(__file__),
                "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
                "rows_in": result.get("rows_in", 0),
                "rows_out": result.get("rows_out", 0),
                "duration_seconds": round(time.time() - _start_time, 3),
            }
            ckpt_path = maybe_checkpoint(output_path, "detect_issues", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
