#!/usr/bin/env python3
"""
Validate data against JSON schema.

Checks type conformance, nullability, range, pattern, length, and allowed values.
Reports violations with specific row indices and sample values.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import glob
import json
import os
import shutil
import sys
import time
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

def maybe_checkpoint(df, path, metadata=None):
    """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)


def validate_type(series: pd.Series, expected_type: str) -> tuple[bool, list]:
    """Validate column type matches expected type."""
    violations = []
    non_null = series.dropna()

    if len(non_null) == 0:
        return True, []

    if expected_type == "numeric":
        if not pd.api.types.is_numeric_dtype(series):
            # Try to convert
            try:
                pd.to_numeric(non_null)
            except:
                invalid_idx = []
                for idx, val in non_null.items():
                    try:
                        float(val)
                    except:
                        invalid_idx.append(idx)
                if invalid_idx:
                    violations.append({
                        "rows": invalid_idx[:100],  # Limit to 100
                        "sample_values": non_null.iloc[:5].tolist()
                    })

    elif expected_type == "datetime":
        try:
            pd.to_datetime(non_null)
        except:
            invalid_idx = []
            for idx, val in non_null.items():
                try:
                    pd.to_datetime(val)
                except:
                    invalid_idx.append(idx)
            if invalid_idx:
                violations.append({
                    "rows": invalid_idx[:100],
                    "sample_values": non_null.iloc[:5].tolist()
                })

    elif expected_type == "boolean":
        valid_vals = {0, 1, True, False, '0', '1', 'true', 'false', 'True', 'False'}
        invalid_idx = []
        for idx, val in non_null.items():
            if val not in valid_vals:
                invalid_idx.append(idx)
        if invalid_idx:
            violations.append({
                "rows": invalid_idx[:100],
                "sample_values": non_null.iloc[:5].tolist()
            })

    # text and categorical accept anything
    return len(violations) == 0, violations


def validate_nullable(series: pd.Series, nullable: bool) -> tuple[bool, list]:
    """Validate nullability constraint."""
    if not nullable and series.isnull().any():
        null_idx = series[series.isnull()].index.tolist()
        return False, [{
            "rows": null_idx[:100],
            "sample_values": [None]
        }]
    return True, []


def validate_range(series: pd.Series, min_val: float = None, max_val: float = None) -> tuple[bool, list]:
    """Validate numeric range constraints."""
    violations = []
    non_null = series.dropna()

    if len(non_null) == 0:
        return True, []

    # Convert to numeric
    try:
        numeric = pd.to_numeric(non_null)
    except:
        return True, []  # Type validation will catch this

    if min_val is not None:
        below_min = numeric < min_val
        if below_min.any():
            idx = non_null[below_min].index.tolist()
            violations.append({
                "constraint": f"min={min_val}",
                "rows": idx[:100],
                "sample_values": non_null[below_min].iloc[:5].tolist()
            })

    if max_val is not None:
        above_max = numeric > max_val
        if above_max.any():
            idx = non_null[above_max].index.tolist()
            violations.append({
                "constraint": f"max={max_val}",
                "rows": idx[:100],
                "sample_values": non_null[above_max].iloc[:5].tolist()
            })

    return len(violations) == 0, violations


def validate_pattern(series: pd.Series, pattern: str) -> tuple[bool, list]:
    """Validate text pattern constraint."""
    non_null = series.dropna().astype(str)

    if len(non_null) == 0:
        return True, []

    try:
        matches = non_null.str.match(pattern)
        if not matches.all():
            invalid_idx = non_null[~matches].index.tolist()
            return False, [{
                "rows": invalid_idx[:100],
                "sample_values": non_null[~matches].iloc[:5].tolist()
            }]
    except Exception as e:
        return False, [{
            "rows": [],
            "sample_values": [f"Pattern error: {str(e)}"]
        }]

    return True, []


def validate_max_length(series: pd.Series, max_length: int) -> tuple[bool, list]:
    """Validate maximum string length constraint."""
    non_null = series.dropna().astype(str)

    if len(non_null) == 0:
        return True, []

    too_long = non_null.str.len() > max_length
    if too_long.any():
        invalid_idx = non_null[too_long].index.tolist()
        return False, [{
            "rows": invalid_idx[:100],
            "sample_values": non_null[too_long].iloc[:5].tolist()
        }]

    return True, []


def validate_allowed_values(series: pd.Series, allowed_values: list) -> tuple[bool, list]:
    """Validate categorical allowed values constraint."""
    non_null = series.dropna()

    if len(non_null) == 0:
        return True, []

    # Convert allowed values to set for faster lookup
    allowed_set = set(allowed_values)

    # Convert series values to comparable types
    invalid_mask = ~non_null.isin(allowed_set)

    if invalid_mask.any():
        invalid_idx = non_null[invalid_mask].index.tolist()
        return False, [{
            "rows": invalid_idx[:100],
            "sample_values": non_null[invalid_mask].iloc[:5].tolist()
        }]

    return True, []


def validate_column(df: pd.DataFrame, col_name: str, col_schema: dict) -> list:
    """Validate a single column against its schema."""
    violations = []

    if col_name not in df.columns:
        return [{
            "column": col_name,
            "rule": "column_exists",
            "count": len(df),
            "sample_values": [],
            "rows": []
        }]

    series = df[col_name]

    # Type validation
    expected_type = col_schema.get("dtype")
    if expected_type:
        valid, type_violations = validate_type(series, expected_type)
        if not valid:
            for v in type_violations:
                violations.append({
                    "column": col_name,
                    "rule": f"type={expected_type}",
                    "count": len(v["rows"]),
                    "sample_values": v["sample_values"][:5],
                    "rows": v["rows"]
                })

    # Nullability validation
    nullable = col_schema.get("nullable", True)
    valid, null_violations = validate_nullable(series, nullable)
    if not valid:
        for v in null_violations:
            violations.append({
                "column": col_name,
                "rule": "nullable=false",
                "count": len(v["rows"]),
                "sample_values": v["sample_values"][:5],
                "rows": v["rows"]
            })

    # Constraint validations
    constraints = col_schema.get("constraints", {})

    # Range constraints
    if "min" in constraints or "max" in constraints:
        valid, range_violations = validate_range(
            series,
            constraints.get("min"),
            constraints.get("max")
        )
        if not valid:
            for v in range_violations:
                violations.append({
                    "column": col_name,
                    "rule": v["constraint"],
                    "count": len(v["rows"]),
                    "sample_values": v["sample_values"][:5],
                    "rows": v["rows"]
                })

    # Pattern constraint
    if "pattern" in constraints:
        valid, pattern_violations = validate_pattern(series, constraints["pattern"])
        if not valid:
            for v in pattern_violations:
                violations.append({
                    "column": col_name,
                    "rule": f"pattern={constraints['pattern'][:50]}...",
                    "count": len(v["rows"]),
                    "sample_values": v["sample_values"][:5],
                    "rows": v["rows"]
                })

    # Max length constraint
    if "max_length" in constraints:
        valid, length_violations = validate_max_length(series, constraints["max_length"])
        if not valid:
            for v in length_violations:
                violations.append({
                    "column": col_name,
                    "rule": f"max_length={constraints['max_length']}",
                    "count": len(v["rows"]),
                    "sample_values": v["sample_values"][:5],
                    "rows": v["rows"]
                })

    # Allowed values constraint
    if "allowed_values" in constraints:
        valid, value_violations = validate_allowed_values(series, constraints["allowed_values"])
        if not valid:
            for v in value_violations:
                violations.append({
                    "column": col_name,
                    "rule": "allowed_values",
                    "count": len(v["rows"]),
                    "sample_values": v["sample_values"][:5],
                    "rows": v["rows"]
                })

    return violations


def main(input_path: str, schema_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Validate data against JSON schema.

    Args:
        input_path: Path to input CSV/Parquet file
        schema_path: Path to JSON schema file
        output_path: Path to save validation report
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Result dictionary with validation results
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

        schema_file = Path(schema_path)
        if not schema_file.exists():
            return {
                "success": False,
                "error": f"Schema file not found: {schema_path}",
                "suggestion": "Verify the schema file path exists"
            }

        # Load data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input data is empty",
                "suggestion": "Provide non-empty dataset for validation",
                "valid": False
            }

        # Load schema
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Validate each column
        all_violations = []
        checks_passed = 0
        checks_failed = 0

        for col_name, col_schema in schema.get("columns", {}).items():
            col_violations = validate_column(df, col_name, col_schema)
            all_violations.extend(col_violations)

            # Count checks
            num_rules = 1 + len(col_schema.get("constraints", {}))  # type + constraints
            if not col_schema.get("nullable", True):
                num_rules += 1

            if col_violations:
                checks_failed += len(col_violations)
                checks_passed += max(0, num_rules - len(col_violations))
            else:
                checks_passed += num_rules

        # Validate row count range
        row_count_range = schema.get("row_count_range", {})
        if row_count_range:
            row_count = len(df)
            min_rows = row_count_range.get("min", 0)
            max_rows = row_count_range.get("max", float('inf'))

            if row_count < min_rows or row_count > max_rows:
                all_violations.append({
                    "column": "_row_count",
                    "rule": f"row_count_range=[{min_rows}, {max_rows}]",
                    "count": 1,
                    "sample_values": [row_count],
                    "rows": []
                })
                checks_failed += 1
            else:
                checks_passed += 1

        # Prepare result
        is_valid = len(all_violations) == 0

        result = {
            "success": True,
            "output_path": str(output_path),
            "valid": is_valid,
            "rows_in": len(df),
            "rows_out": len(df),
            "violations": all_violations,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed
        }

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and schema structure"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate data against JSON schema")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet file")
    parser.add_argument("--schema", required=True, help="Schema JSON file")
    parser.add_argument("--output", default="logs/schema_validation.json", help="Output validation report JSON (default: logs/schema_validation.json)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        if not os.path.isfile(args.input):
            print(json.dumps({"success": False, "error": f"Input file not found: {args.input}"}, indent=2))
            sys.exit(1)
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "validate_schema",
                "input": args.input,
                "output": args.output,
                "steps": [
                    "Load input CSV/Parquet file",
                    "Load JSON schema from --schema path",
                    "Validate each column against type, nullability, and constraints",
                    "Check row count range if specified in schema",
                    "Write validation report JSON to output path"
                ],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(args.input, args.schema, args.output, input_format=args.input_format)
    if result.get("success") and args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "format": getattr(args, "output_format", "json"),
            "input_path": getattr(args, "input_path", getattr(args, "input", "")),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(args.output, "validate_schema", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
