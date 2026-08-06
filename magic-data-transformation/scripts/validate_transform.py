#!/usr/bin/env python3
"""
Validate transformation outputs.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Shared utilities
def load_dataframe(path, **kwargs):
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def parse_expected_shape(shape_str):
    """Parse expected shape string like '100,10' into tuple."""
    if not shape_str:
        return None

    parts = shape_str.split(",")
    if len(parts) != 2:
        raise ValueError("Expected shape format: 'rows,cols'")

    rows = int(parts[0].strip()) if parts[0].strip() != '*' else None
    cols = int(parts[1].strip()) if parts[1].strip() != '*' else None

    return (rows, cols)


def validate_shape(df, expected_shape):
    """Validate dataframe shape."""
    if not expected_shape:
        return True, None

    expected_rows, expected_cols = expected_shape
    actual_rows, actual_cols = df.shape

    issues = []

    if expected_rows is not None and actual_rows != expected_rows:
        issues.append(f"Expected {expected_rows} rows, got {actual_rows}")

    if expected_cols is not None and actual_cols != expected_cols:
        issues.append(f"Expected {expected_cols} columns, got {actual_cols}")

    return len(issues) == 0, issues


def validate_no_unexpected_nulls(original_df, transformed_df):
    """Check for unexpected null values introduced by transformation."""
    issues = []

    for col in transformed_df.columns:
        if col in original_df.columns:
            original_nulls = original_df[col].isna().sum()
            transformed_nulls = transformed_df[col].isna().sum()

            if transformed_nulls > original_nulls:
                new_nulls = transformed_nulls - original_nulls
                issues.append(
                    f"Column '{col}' has {new_nulls} new null values "
                    f"({original_nulls} -> {transformed_nulls})"
                )

    return len(issues) == 0, issues


def validate_key_columns_preserved(original_df, transformed_df, key_columns):
    """Check that key columns are preserved."""
    if not key_columns:
        return True, None

    key_cols_list = [c.strip() for c in key_columns.split(",")]
    issues = []

    for col in key_cols_list:
        if col not in original_df.columns:
            issues.append(f"Key column '{col}' not found in original data")
            continue

        if col not in transformed_df.columns:
            issues.append(f"Key column '{col}' missing in transformed data")
            continue

        # Check if values match
        if len(original_df) == len(transformed_df):
            if not original_df[col].equals(transformed_df[col]):
                # Check if values are the same but potentially reordered
                orig_set = set(original_df[col].dropna().unique())
                trans_set = set(transformed_df[col].dropna().unique())

                if orig_set != trans_set:
                    issues.append(f"Key column '{col}' values changed")

    return len(issues) == 0, issues


def validate_types_consistent(original_df, transformed_df):
    """Check that column types remain consistent where columns overlap."""
    issues = []

    common_cols = set(original_df.columns) & set(transformed_df.columns)

    for col in common_cols:
        orig_type = original_df[col].dtype
        trans_type = transformed_df[col].dtype

        # Check for type compatibility
        if orig_type != trans_type:
            # Allow numeric type changes (int -> float, etc.)
            if pd.api.types.is_numeric_dtype(orig_type) and pd.api.types.is_numeric_dtype(trans_type):
                continue

            # Allow object -> string
            if orig_type == 'object' and trans_type == 'string':
                continue

            issues.append(
                f"Column '{col}' type changed from {orig_type} to {trans_type}"
            )

    return len(issues) == 0, issues


def main(input_path: str, transformed_path: str, output_path: str,
         expected_shape: str = None, key_columns: str = None,
         input_format: str = "auto") -> dict:
    """
    Validate transformation outputs.

    Args:
        input_path: Path to original file
        transformed_path: Path to transformed file
        output_path: Path to validation report (JSON)
        expected_shape: Expected shape as 'rows,cols' (use * for any)
        key_columns: Comma-separated key columns to preserve
        input_format: File format for input files (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Validation results
    """
    try:
        # Load data
        df_original = load_dataframe(input_path, format=input_format)
        df_transformed = load_dataframe(transformed_path, format=input_format)

        if df_transformed.empty:
            return {
                "success": False,
                "error": "Transformed file is empty",
                "suggestion": "Check transformation script"
            }

        # Parse expected shape
        expected_shape_tuple = parse_expected_shape(expected_shape)

        # Run validation checks
        checks = {}
        warnings = []

        # Shape validation
        shape_valid, shape_issues = validate_shape(df_transformed, expected_shape_tuple)
        checks["shape_valid"] = shape_valid
        if shape_issues:
            warnings.extend(shape_issues)

        # Null validation
        no_unexpected_nulls, null_issues = validate_no_unexpected_nulls(df_original, df_transformed)
        checks["no_unexpected_nulls"] = no_unexpected_nulls
        if null_issues:
            warnings.extend(null_issues)

        # Key columns validation
        key_cols_preserved, key_issues = validate_key_columns_preserved(
            df_original, df_transformed, key_columns
        )
        checks["key_columns_preserved"] = key_cols_preserved
        if key_issues:
            warnings.extend(key_issues)

        # Type consistency validation
        types_consistent, type_issues = validate_types_consistent(df_original, df_transformed)
        checks["types_consistent"] = types_consistent
        if type_issues:
            warnings.extend(type_issues)

        # Overall validity
        valid = all(checks.values())

        # Create validation report
        report_rows = []

        report_rows.append({
            "check": "shape_validation",
            "passed": shape_valid,
            "details": "; ".join(shape_issues) if shape_issues else "OK"
        })

        report_rows.append({
            "check": "null_validation",
            "passed": no_unexpected_nulls,
            "details": "; ".join(null_issues) if null_issues else "OK"
        })

        report_rows.append({
            "check": "key_columns_validation",
            "passed": key_cols_preserved,
            "details": "; ".join(key_issues) if key_issues else "OK"
        })

        report_rows.append({
            "check": "type_consistency_validation",
            "passed": types_consistent,
            "details": "; ".join(type_issues) if type_issues else "OK"
        })

        report_df = pd.DataFrame(report_rows)
        report_df.to_csv(output_path, index=False)

        result = {
            "success": True,
            "output_path": output_path,
            "valid": valid,
            "checks": checks,
            "warnings": warnings
        }

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check file paths and try again"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check expected_shape format (rows,cols)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate transformation outputs")
    parser.add_argument("input_path", help="Path to original CSV file")
    parser.add_argument("transformed_path", help="Path to transformed CSV file")
    parser.add_argument("output_path", help="Path to validation report CSV file")
    parser.add_argument("--expected-shape", help="Expected shape as 'rows,cols' (use * for any)")
    parser.add_argument("--key-columns", help="Comma-separated key columns to preserve")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format for both original and transformed files (default: auto-detect)")

    args = parser.parse_args()

    result = main(args.input_path, args.transformed_path, args.output_path,
                  args.expected_shape, args.key_columns, args.input_format)

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
