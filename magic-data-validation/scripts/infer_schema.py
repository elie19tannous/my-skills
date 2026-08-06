#!/usr/bin/env python3
"""
Auto-generate JSON schema from data.

Detects column types and infers constraints based on observed values.
Supports strict mode for tighter constraint enforcement.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import re

def load_dataframe(path, **kwargs):
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def detect_column_type(series: pd.Series) -> str:
    """Detect the semantic type of a column."""
    # Drop nulls for type detection
    non_null = series.dropna()
    if len(non_null) == 0:
        return "text"

    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        # Check if boolean (0/1 only)
        unique_vals = non_null.unique()
        if set(unique_vals).issubset({0, 1, True, False}):
            return "boolean"
        return "numeric"

    # Check if datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # For object/string types
    if pd.api.types.is_object_dtype(series):
        # Try to parse as datetime
        try:
            pd.to_datetime(non_null.head(100))
            return "datetime"
        except:
            pass

        # Check cardinality for categorical
        cardinality_ratio = len(non_null.unique()) / len(non_null)
        if cardinality_ratio < 0.05 or len(non_null.unique()) <= 20:
            return "categorical"

        return "text"

    return "text"


def detect_text_pattern(series: pd.Series) -> str | None:
    """Detect common text patterns like email, phone, URL."""
    non_null = series.dropna().astype(str)
    if len(non_null) == 0:
        return None

    # Sample for performance
    sample = non_null.head(1000)

    # Email pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if sample.str.match(email_pattern).mean() > 0.8:
        return email_pattern

    # Phone pattern (basic)
    phone_pattern = r'^\+?1?\d{9,15}$'
    if sample.str.replace(r'[\s\-\(\)]', '', regex=True).str.match(phone_pattern).mean() > 0.8:
        return r'^\+?[\d\s\-\(\)]{9,20}$'

    # URL pattern
    url_pattern = r'^https?://[^\s]+$'
    if sample.str.match(url_pattern).mean() > 0.8:
        return url_pattern

    return None


def infer_column_schema(series: pd.Series, col_name: str, strict: bool = False) -> dict:
    """Infer schema constraints for a single column."""
    schema = {
        "dtype": detect_column_type(series),
        "nullable": bool(series.isnull().any()),
        "constraints": {}
    }

    # In strict mode, set nullable=false if no nulls observed
    if strict and not series.isnull().any():
        schema["nullable"] = False

    non_null = series.dropna()

    # Numeric constraints
    if schema["dtype"] == "numeric":
        if len(non_null) > 0:
            if strict:
                # Use p5-p95 for tighter bounds
                schema["constraints"]["min"] = float(non_null.quantile(0.05))
                schema["constraints"]["max"] = float(non_null.quantile(0.95))
            else:
                schema["constraints"]["min"] = float(non_null.min())
                schema["constraints"]["max"] = float(non_null.max())
            schema["constraints"]["mean"] = float(non_null.mean())

    # Text constraints
    elif schema["dtype"] == "text":
        if len(non_null) > 0:
            str_series = non_null.astype(str)
            schema["constraints"]["max_length"] = int(str_series.str.len().max())

            # Detect pattern
            pattern = detect_text_pattern(series)
            if pattern:
                schema["constraints"]["pattern"] = pattern

    # Categorical constraints
    elif schema["dtype"] == "categorical":
        if len(non_null) > 0:
            unique_vals = non_null.unique().tolist()
            # Convert to JSON-serializable types
            schema["constraints"]["allowed_values"] = [
                str(v) if not isinstance(v, (int, float, bool, str)) else v
                for v in unique_vals
            ]

    # Boolean constraints
    elif schema["dtype"] == "boolean":
        # No additional constraints needed
        pass

    # Datetime constraints
    elif schema["dtype"] == "datetime":
        try:
            dt_series = pd.to_datetime(non_null)
            if len(dt_series) > 0:
                schema["constraints"]["min"] = dt_series.min().isoformat()
                schema["constraints"]["max"] = dt_series.max().isoformat()
        except:
            pass

    return schema


def detect_mixed_types(df: pd.DataFrame) -> list:
    """
    Detect columns with mixed types (e.g., numbers and strings coexisting).

    Returns a list of warning dicts, each with:
      - column: column name
      - types_found: list of detected types and their percentages
      - suggestion: recommended cleaning action
    """
    warnings = []

    for col in df.columns:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        # Skip already-typed columns (numeric, datetime, bool)
        if pd.api.types.is_numeric_dtype(df[col]):
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            continue
        if pd.api.types.is_bool_dtype(df[col]):
            continue

        # For object columns, check what types the values actually are
        str_vals = non_null.astype(str)
        total = len(str_vals)

        # Count numeric-parseable values
        numeric_mask = pd.to_numeric(str_vals, errors="coerce").notna()
        numeric_count = int(numeric_mask.sum())
        numeric_pct = round(numeric_count / total * 100, 1)

        # Count datetime-parseable values (sample for performance)
        sample = str_vals.head(500)
        datetime_count = 0
        try:
            dt_parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
            datetime_count = int(dt_parsed.notna().sum())
        except Exception:
            pass
        datetime_pct = round(datetime_count / len(sample) * 100, 1) if len(sample) > 0 else 0.0

        # Remaining are pure strings
        string_pct = round((total - numeric_count) / total * 100, 1)

        # Flag if there's a meaningful mix (both >5%)
        types_found = []
        if numeric_pct > 5:
            types_found.append({"type": "numeric", "pct": numeric_pct})
        if datetime_pct > 5 and datetime_pct != numeric_pct:
            types_found.append({"type": "datetime", "pct": datetime_pct})
        if string_pct > 5 and numeric_pct > 5:
            types_found.append({"type": "string", "pct": string_pct})

        if len(types_found) >= 2:
            # Build suggestion
            if numeric_pct > 50:
                suggestion = (
                    f"Column appears mostly numeric ({numeric_pct}%). "
                    f"Consider using pd.to_numeric(errors='coerce') to convert, "
                    f"then handle {string_pct}% non-numeric values as missing."
                )
            elif datetime_pct > 50:
                suggestion = (
                    f"Column appears mostly datetime ({datetime_pct}%). "
                    f"Consider using pd.to_datetime(errors='coerce') to convert."
                )
            else:
                suggestion = (
                    f"Column has mixed types. Consider splitting into separate "
                    f"columns or standardizing to a single type."
                )

            warnings.append({
                "column": col,
                "types_found": types_found,
                "suggestion": suggestion,
            })

    return warnings


def infer_schema(df: pd.DataFrame, strict: bool = False) -> dict:
    """Infer complete schema from DataFrame."""
    schema = {
        "columns": {},
        "row_count_range": {},
        "warnings": [],
    }

    # Infer column schemas
    for col in df.columns:
        schema["columns"][col] = infer_column_schema(df[col], col, strict)

    # Detect mixed type warnings
    schema["warnings"] = detect_mixed_types(df)

    # Row count range
    row_count = len(df)
    if strict:
        # Tight range in strict mode (±10%)
        schema["row_count_range"]["min"] = int(row_count * 0.9)
        schema["row_count_range"]["max"] = int(row_count * 1.1)
    else:
        # Loose range (±50%)
        schema["row_count_range"]["min"] = int(row_count * 0.5)
        schema["row_count_range"]["max"] = int(row_count * 1.5)

    return schema


def main(input_path: str, output_path: str, strict: bool = False, input_format: str = "auto") -> dict:
    """
    Auto-generate JSON schema from data.

    Args:
        input_path: Path to input CSV/Parquet file
        output_path: Path to save generated schema JSON
        strict: If true, tighter constraints (narrower ranges, required non-null)
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Result dictionary with schema and metadata
    """
    try:
        # Read input
        input_file = Path(input_path)
        if not input_file.exists():
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path exists"
            }

        # Load data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input data is empty",
                "suggestion": "Provide non-empty dataset for schema inference"
            }

        # Infer schema
        schema = infer_schema(df, strict)

        # Save schema
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(schema, f, indent=2, default=str)

        return {
            "success": True,
            "output_path": str(output_path),
            "rows_in": len(df),
            "schema": schema
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and data integrity"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-generate JSON schema from data")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet file")
    parser.add_argument("--output", default="logs/schema.json", help="Output schema JSON file (default: logs/schema.json)")
    parser.add_argument("--strict", action="store_true", help="Use strict mode for tighter constraints")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()

    result = main(args.input, args.output, args.strict, input_format=args.input_format)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
