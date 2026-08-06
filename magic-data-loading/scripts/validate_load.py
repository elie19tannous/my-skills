#!/usr/bin/env python3
"""
Validate loaded data integrity.

Checks:
- Non-empty data (rows > 0)
- Column types can be inferred
- No all-null columns
- Optional: row count matches original file
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

import pandas as pd

def load_dataframe(path, **kwargs):
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def check_non_empty(df: pd.DataFrame) -> bool:
    """Check if DataFrame has at least one row."""
    return len(df) > 0


def check_types_inferred(df: pd.DataFrame) -> bool:
    """
    Check if column types can be inferred.

    Returns False if all columns are object type with no discernible structure.
    """
    if len(df.columns) == 0:
        return False

    # Check if at least some columns have non-object types
    non_object_cols = 0
    for col in df.columns:
        dtype = df[col].dtype
        if not pd.api.types.is_object_dtype(dtype):
            non_object_cols += 1

    # If we have at least one typed column, types are inferred
    if non_object_cols > 0:
        return True

    # If all columns are object, check if data looks structured
    # (i.e., not all nulls or all same value)
    for col in df.columns:
        non_null = df[col].dropna()
        if len(non_null) > 0:
            unique_count = len(non_null.unique())
            if unique_count > 1:
                return True

    return False


def check_no_all_null_columns(df: pd.DataFrame) -> bool:
    """Check that no columns are entirely null."""
    for col in df.columns:
        if df[col].isna().all():
            return False
    return True


def count_rows_in_file(file_path: str) -> Optional[int]:
    """
    Count rows in original file.

    Returns None if count cannot be determined.
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext in ['.csv', '.txt', '.tsv']:
            # Count lines (subtract 1 for header if present)
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                line_count = sum(1 for _ in f)

            # Assume header exists, subtract 1
            return max(0, line_count - 1)

        elif file_ext in ['.jsonl', '.ndjson']:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return sum(1 for line in f if line.strip())

        elif file_ext in ['.parquet', '.pq']:
            # Use pandas to get exact count
            df = pd.read_parquet(file_path)
            return len(df)

        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return len(df)

        elif file_ext == '.json':
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                return 1
            else:
                return None

    except Exception:
        return None

    return None


def main(input_path: str, original_path: Optional[str] = None,
         output_path: Optional[str] = None, input_format: str = "auto") -> Dict[str, Any]:
    """
    Validate loaded data (row count > 0, column types inferred, no silent data loss).

    Args:
        input_path: Path to loaded CSV file
        original_path: Optional path to original file for row count comparison
        output_path: Optional path to write validation results (JSON)

    Returns:
        Dictionary with validation results
    """
    try:
        # Validate input file exists
        if not os.path.isfile(input_path):
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path is correct"
            }

        # Load data
        df = load_dataframe(input_path, format=input_format)

        rows = len(df)
        columns = len(df.columns)

        # Run validation checks
        checks = {
            "non_empty": check_non_empty(df),
            "types_inferred": check_types_inferred(df),
            "no_all_null_cols": check_no_all_null_columns(df)
        }

        # Check row count match if original file provided
        if original_path:
            original_rows = count_rows_in_file(original_path)
            if original_rows is not None:
                checks["row_count_match"] = (rows == original_rows)
                checks["original_rows"] = original_rows
                checks["loaded_rows"] = rows
                if rows < original_rows:
                    checks["rows_lost"] = original_rows - rows
                    checks["loss_percentage"] = round((original_rows - rows) / original_rows * 100, 2)

        # Overall validity
        valid = all([
            checks["non_empty"],
            checks["types_inferred"],
            checks["no_all_null_cols"]
        ])

        # If row count check was performed, include in validity
        if "row_count_match" in checks:
            # Allow up to 1% data loss (for bad lines, etc.)
            if "loss_percentage" in checks and checks["loss_percentage"] > 1.0:
                valid = False

        result = {
            "success": True,
            "valid": valid,
            "rows": rows,
            "columns": columns,
            "checks": checks
        }

        # Add issues if not valid
        if not valid:
            issues = []
            if not checks["non_empty"]:
                issues.append("Data is empty (0 rows)")
            if not checks["types_inferred"]:
                issues.append("Column types could not be inferred")
            if not checks["no_all_null_cols"]:
                issues.append("Some columns are entirely null")
            if "loss_percentage" in checks and checks["loss_percentage"] > 1.0:
                issues.append(f"Significant data loss: {checks['loss_percentage']}% of rows")

            result["issues"] = issues

        # Write result to output file if specified
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            result["output_path"] = output_path

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check file format and accessibility"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate loaded data integrity")
    parser.add_argument("input_path", help="Path to loaded data file")
    parser.add_argument("--original_path", help="Optional path to original file for comparison")
    parser.add_argument("--output_path", help="Optional path to write validation results (JSON)")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()

    result = main(
        args.input_path,
        original_path=args.original_path,
        output_path=args.output_path,
        input_format=args.input_format,
    )

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
