#!/usr/bin/env python3
"""
Validate statistical outputs against source data.

Recomputes descriptive statistics (mean, std, min, max, count) from the source
CSV and compares them against reported values within a configurable tolerance.
Reports mismatches with expected vs actual values.
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.


import argparse
import json
import os
import sys
from pathlib import Path
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


STAT_KEYS = ["mean", "std", "min", "max", "count"]


def compute_stats(series: pd.Series) -> dict:
    """Compute descriptive statistics for a numeric series."""
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) == 0:
        return {}
    return {
        "mean": float(numeric.mean()),
        "std": float(numeric.std(ddof=1)) if len(numeric) > 1 else 0.0,
        "min": float(numeric.min()),
        "max": float(numeric.max()),
        "count": int(len(numeric)),
    }


def compare_stat(
    stat_name: str,
    expected: float,
    actual: float,
    tolerance: float,
) -> dict:
    """Compare a single statistic value against the expected value."""
    # For count, use integer-exact comparison (no floating tolerance)
    if stat_name == "count":
        diff = abs(int(expected) - int(actual))
        passed = diff == 0
        return {
            "expected": int(expected),
            "actual": int(actual),
            "diff": diff,
            "passed": passed,
        }

    diff = abs(float(expected) - float(actual))
    passed = diff <= tolerance
    return {
        "expected": float(expected),
        "actual": float(actual),
        "diff": float(diff),
        "passed": passed,
    }


def validate_column_stats(
    df: pd.DataFrame,
    col_name: str,
    reported_stats: dict,
    tolerance: float,
) -> tuple[dict, int, int]:
    """
    Validate statistics for a single column.

    Returns:
        (per_stat_results, checks_passed, checks_failed)
    """
    col_results = {}
    checks_passed = 0
    checks_failed = 0

    if col_name not in df.columns:
        # Column missing from source — flag every reported stat as failed
        for stat_name in STAT_KEYS:
            if stat_name in reported_stats:
                col_results[stat_name] = {
                    "expected": reported_stats[stat_name],
                    "actual": None,
                    "diff": None,
                    "passed": False,
                    "error": f"Column '{col_name}' not found in source data",
                }
                checks_failed += 1
        return col_results, checks_passed, checks_failed

    actual_stats = compute_stats(df[col_name])

    for stat_name in STAT_KEYS:
        if stat_name not in reported_stats:
            continue

        expected_val = reported_stats[stat_name]

        if stat_name not in actual_stats:
            col_results[stat_name] = {
                "expected": expected_val,
                "actual": None,
                "diff": None,
                "passed": False,
                "error": "Could not compute statistic from source data (no valid numeric values)",
            }
            checks_failed += 1
            continue

        result = compare_stat(stat_name, expected_val, actual_stats[stat_name], tolerance)
        col_results[stat_name] = result
        if result["passed"]:
            checks_passed += 1
        else:
            checks_failed += 1

    return col_results, checks_passed, checks_failed


def main(
    source_path: str,
    stats_path: str,
    output_path: str,
    tolerance: float = 1e-6,
    columns: list = None,
    input_format: str = "auto",
) -> dict:
    """
    Validate statistical outputs against source data.

    Args:
        source_path: Path to source CSV file
        stats_path:  Path to statistics JSON (output of descriptive_stats.py)
        output_path: Path to save validation report
        tolerance:   Absolute tolerance for floating-point comparisons
        columns:     Optional list of column names to validate (all if None)
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Result dictionary with validation results
    """
    try:
        source_file = Path(source_path)
        if not source_file.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_path}",
                "suggestion": "Verify the source CSV file path exists",
            }

        stats_file = Path(stats_path)
        if not stats_file.exists():
            return {
                "success": False,
                "error": f"Statistics file not found: {stats_path}",
                "suggestion": "Verify the statistics JSON file path exists",
            }

        # Load source data
        df = load_dataframe(source_path, format=input_format)

        # Quality gate: empty source
        if df.empty:
            return {
                "success": False,
                "error": "Source data is empty",
                "suggestion": "Provide a non-empty dataset for validation",
            }

        # Load statistics JSON
        with open(stats_path, "r") as f:
            stats_data = json.load(f)

        # Support both a flat dict of columns and a nested structure
        # (e.g. {"columns": {...}} or {"statistics": {...}} or directly {col: {...}})
        if "columns" in stats_data and isinstance(stats_data["columns"], dict):
            column_stats = stats_data["columns"]
        elif "statistics" in stats_data and isinstance(stats_data["statistics"], dict):
            column_stats = stats_data["statistics"]
        else:
            # Assume top-level keys are column names whose values are stat dicts
            column_stats = {
                k: v
                for k, v in stats_data.items()
                if isinstance(v, dict) and any(s in v for s in STAT_KEYS)
            }

        if not column_stats:
            return {
                "success": False,
                "error": "No column statistics found in the statistics JSON",
                "suggestion": (
                    "Ensure the statistics file contains per-column stat dicts "
                    "with keys like 'mean', 'std', 'min', 'max', 'count'"
                ),
            }

        # Apply column filter
        if columns:
            column_stats = {c: column_stats[c] for c in columns if c in column_stats}
            missing_requested = [c for c in columns if c not in column_stats]
            if missing_requested:
                return {
                    "success": False,
                    "error": (
                        f"Requested columns not found in statistics JSON: "
                        f"{missing_requested}"
                    ),
                    "suggestion": "Check column names match the statistics file",
                }

        # Validate each column
        all_results = {}
        total_passed = 0
        total_failed = 0

        for col_name, reported_stats in column_stats.items():
            col_results, col_passed, col_failed = validate_column_stats(
                df, col_name, reported_stats, tolerance
            )
            if col_results:
                all_results[col_name] = col_results
            total_passed += col_passed
            total_failed += col_failed

        checks_total = total_passed + total_failed
        success = total_failed == 0

        if success:
            summary = (
                f"All {checks_total} checks passed within tolerance {tolerance}"
            )
        else:
            summary = (
                f"{total_failed} of {checks_total} checks failed "
                f"(tolerance {tolerance})"
            )

        result = {
            "success": success,
            "output_path": str(output_path),
            "rows_in": len(df),
            "checks_total": checks_total,
            "checks_passed": total_passed,
            "checks_failed": total_failed,
            "tolerance": tolerance,
            "results": all_results,
            "summary": summary,
        }

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check source file format and statistics JSON structure",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate statistical outputs against source data"
    )
    parser.add_argument("source_path", help="Source CSV file")
    parser.add_argument("stats_path", help="Statistics JSON file (output of descriptive_stats.py)")
    parser.add_argument("output_path", help="Output validation report JSON")
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="Absolute tolerance for floating-point comparisons (default: 1e-6)",
    )
    parser.add_argument(
        "--columns",
        type=str,
        default=None,
        help="Comma-separated list of column names to validate (default: all)",
    )
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Input file format (default: auto)",
    )

    args = parser.parse_args()

    columns = [c.strip() for c in args.columns.split(",")] if args.columns else None

    result = main(
        args.source_path,
        args.stats_path,
        args.output_path,
        tolerance=args.tolerance,
        columns=columns,
        input_format=args.input_format,
    )
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
