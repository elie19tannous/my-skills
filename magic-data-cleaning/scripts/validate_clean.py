#!/usr/bin/env python3
"""
Validation script for cleaned data.
Compares original and cleaned data to ensure quality.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
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


def count_nulls(df):
    """Count total null values in dataframe."""
    return int(df.isna().sum().sum())


def check_types_consistent(df_original, df_cleaned):
    """Check if data types are consistent between original and cleaned data."""
    # Get common columns
    common_cols = set(df_original.columns) & set(df_cleaned.columns)

    if not common_cols:
        return False

    inconsistent = []

    for col in common_cols:
        orig_type = df_original[col].dtype
        clean_type = df_cleaned[col].dtype

        # Check if types are compatible
        # Numeric types should stay numeric
        if pd.api.types.is_numeric_dtype(orig_type):
            if not pd.api.types.is_numeric_dtype(clean_type):
                inconsistent.append({
                    "column": col,
                    "original": str(orig_type),
                    "cleaned": str(clean_type)
                })

    return len(inconsistent) == 0


def check_columns_preserved(df_original, df_cleaned):
    """Check if columns are preserved (allowing for intentional drops)."""
    original_cols = set(df_original.columns)
    cleaned_cols = set(df_cleaned.columns)

    # Cleaned should be a subset of original (some columns may be dropped)
    extra_cols = cleaned_cols - original_cols

    # New columns appearing is suspicious
    return len(extra_cols) == 0


def detect_new_nulls(df_original, df_cleaned):
    """Detect if new nulls were introduced in any column."""
    common_cols = set(df_original.columns) & set(df_cleaned.columns)

    new_nulls = {}

    for col in common_cols:
        orig_nulls = df_original[col].isna().sum()
        clean_nulls = df_cleaned[col].isna().sum()

        # If cleaned has MORE nulls, that's a problem
        if clean_nulls > orig_nulls:
            new_nulls[col] = {
                "original_nulls": int(orig_nulls),
                "cleaned_nulls": int(clean_nulls),
                "new_nulls": int(clean_nulls - orig_nulls)
            }

    return new_nulls


def main(input_path: str, cleaned_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Validate cleaned data against original.

    Args:
        input_path: Path to original CSV file
        cleaned_path: Path to cleaned CSV file
        output_path: Path to output validation report JSON
        input_format: File format for both input files (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Dictionary with validation results
    """
    try:
        # Read both files
        df_original = load_dataframe(input_path, format=input_format)
        df_cleaned = load_dataframe(cleaned_path, format=input_format)

        # Quality gate: check for empty files
        if df_original.empty:
            return {
                "success": False,
                "error": "Original file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        if df_cleaned.empty:
            return {
                "success": False,
                "error": "Cleaned file is empty",
                "suggestion": "Cleaning process produced empty output"
            }

        # Gather metrics
        rows_original = len(df_original)
        rows_cleaned = len(df_cleaned)
        row_change_pct = ((rows_cleaned - rows_original) / rows_original * 100) if rows_original > 0 else 0

        nulls_before = count_nulls(df_original)
        nulls_after = count_nulls(df_cleaned)

        types_consistent = check_types_consistent(df_original, df_cleaned)
        columns_preserved = check_columns_preserved(df_original, df_cleaned)

        # Detect issues
        new_nulls = detect_new_nulls(df_original, df_cleaned)
        warnings = []

        # Check for new nulls (except when using drop strategies)
        if new_nulls:
            warnings.append({
                "type": "new_nulls_introduced",
                "details": new_nulls,
                "severity": "high"
            })

        # Check for excessive row removal
        if row_change_pct < -10:
            warnings.append({
                "type": "excessive_row_removal",
                "rows_removed": rows_original - rows_cleaned,
                "percentage": round(abs(row_change_pct), 2),
                "severity": "medium"
            })

        # Check for type inconsistencies
        if not types_consistent:
            warnings.append({
                "type": "type_inconsistencies",
                "severity": "high"
            })

        # Check for unexpected column changes
        if not columns_preserved:
            original_cols = set(df_original.columns)
            cleaned_cols = set(df_cleaned.columns)
            extra_cols = list(cleaned_cols - original_cols)
            warnings.append({
                "type": "unexpected_columns",
                "new_columns": extra_cols,
                "severity": "medium"
            })

        # Check if cleaning was effective
        if nulls_after > nulls_before:
            warnings.append({
                "type": "nulls_increased",
                "nulls_before": nulls_before,
                "nulls_after": nulls_after,
                "severity": "high"
            })

        # Determine overall validity
        high_severity_warnings = [w for w in warnings if w.get("severity") == "high"]
        valid = len(high_severity_warnings) == 0

        # Build comparison
        comparison = {
            "rows_original": rows_original,
            "rows_cleaned": rows_cleaned,
            "row_change_pct": round(row_change_pct, 2),
            "nulls_before": nulls_before,
            "nulls_after": nulls_after,
            "types_consistent": types_consistent,
            "columns_preserved": columns_preserved
        }

        # Build result
        result = {
            "success": True,
            "valid": valid,
            "output_path": output_path,
            "comparison": comparison,
            "warnings": warnings
        }

        # Write output
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check that both file paths are correct"
        }
    except pd.errors.EmptyDataError:
        return {
            "success": False,
            "error": "One or more files are empty or invalid",
            "suggestion": "Provide valid CSV files with data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file formats"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate cleaned data")
    parser.add_argument("input_path", help="Path to original CSV file")
    parser.add_argument("cleaned_path", help="Path to cleaned CSV file")
    parser.add_argument("output_path", help="Path to output validation report JSON")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format for both files (default: auto)")

    args = parser.parse_args()

    result = main(args.input_path, args.cleaned_path, args.output_path,
                  input_format=args.input_format)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
