#!/usr/bin/env python3
"""
Check cross-column constraints.

Validates relationships between columns including comparisons, conditional nulls,
unique combinations, and vocabulary checks.
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.


import argparse
import json
import os
import sys
import time
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


def check_comparison_constraint(df: pd.DataFrame, columns: list, params: dict) -> dict:
    """
    Check comparison constraint between two columns.

    Params: {"operator": ">|<|>=|<=|==|!="}
    Example: col_a > col_b
    """
    if len(columns) != 2:
        return {
            "valid": False,
            "error": "Comparison requires exactly 2 columns"
        }

    col_a, col_b = columns
    operator = params.get("operator", ">")

    if col_a not in df.columns or col_b not in df.columns:
        return {
            "valid": False,
            "error": f"Missing columns: {[c for c in columns if c not in df.columns]}"
        }

    # Get non-null rows for both columns
    valid_rows = df[[col_a, col_b]].dropna()

    if len(valid_rows) == 0:
        return {"valid": True, "violations": 0, "sample_rows": []}

    # Perform comparison
    try:
        if operator == ">":
            mask = valid_rows[col_a] > valid_rows[col_b]
        elif operator == "<":
            mask = valid_rows[col_a] < valid_rows[col_b]
        elif operator == ">=":
            mask = valid_rows[col_a] >= valid_rows[col_b]
        elif operator == "<=":
            mask = valid_rows[col_a] <= valid_rows[col_b]
        elif operator == "==":
            mask = valid_rows[col_a] == valid_rows[col_b]
        elif operator == "!=":
            mask = valid_rows[col_a] != valid_rows[col_b]
        else:
            return {
                "valid": False,
                "error": f"Unknown operator: {operator}"
            }

        violations = ~mask
        violation_count = violations.sum()

        if violation_count > 0:
            violation_indices = valid_rows[violations].index.tolist()
            sample_rows = []
            for idx in violation_indices[:5]:
                sample_rows.append({
                    "row": int(idx),
                    col_a: df.loc[idx, col_a],
                    col_b: df.loc[idx, col_b]
                })

            return {
                "valid": False,
                "violations": int(violation_count),
                "sample_rows": sample_rows
            }

        return {"valid": True, "violations": 0, "sample_rows": []}

    except Exception as e:
        return {
            "valid": False,
            "error": f"Comparison failed: {str(e)}"
        }


def check_conditional_null_constraint(df: pd.DataFrame, columns: list, params: dict) -> dict:
    """
    Check conditional null constraint.

    Params: {"condition": "if_null|if_not_null"}
    Example: if col_a is null, col_b must be null
    """
    if len(columns) != 2:
        return {
            "valid": False,
            "error": "Conditional null requires exactly 2 columns"
        }

    col_a, col_b = columns
    condition = params.get("condition", "if_null")

    if col_a not in df.columns or col_b not in df.columns:
        return {
            "valid": False,
            "error": f"Missing columns: {[c for c in columns if c not in df.columns]}"
        }

    # Apply condition
    if condition == "if_null":
        # If col_a is null, col_b must be null
        trigger_mask = df[col_a].isnull()
        expected_mask = df[col_b].isnull()
    elif condition == "if_not_null":
        # If col_a is not null, col_b must be not null
        trigger_mask = df[col_a].notnull()
        expected_mask = df[col_b].notnull()
    else:
        return {
            "valid": False,
            "error": f"Unknown condition: {condition}"
        }

    # Find violations
    violations_mask = trigger_mask & ~expected_mask
    violation_count = violations_mask.sum()

    if violation_count > 0:
        violation_indices = df[violations_mask].index.tolist()
        sample_rows = []
        for idx in violation_indices[:5]:
            sample_rows.append({
                "row": int(idx),
                col_a: df.loc[idx, col_a],
                col_b: df.loc[idx, col_b]
            })

        return {
            "valid": False,
            "violations": int(violation_count),
            "sample_rows": sample_rows
        }

    return {"valid": True, "violations": 0, "sample_rows": []}


def check_unique_together_constraint(df: pd.DataFrame, columns: list, params: dict) -> dict:
    """
    Check unique together constraint.

    Example: combination of [col_a, col_b] must be unique
    """
    if len(columns) < 2:
        return {
            "valid": False,
            "error": "Unique together requires at least 2 columns"
        }

    missing = [c for c in columns if c not in df.columns]
    if missing:
        return {
            "valid": False,
            "error": f"Missing columns: {missing}"
        }

    # Check for duplicates
    duplicates = df[df.duplicated(subset=columns, keep=False)]

    if len(duplicates) > 0:
        # Group by the columns to find duplicate sets
        grouped = duplicates.groupby(columns).size().reset_index(name='count')
        sample_rows = []

        for _, group in grouped.head(5).iterrows():
            # Find first occurrence
            mask = pd.Series([True] * len(df))
            for col in columns:
                mask &= (df[col] == group[col])

            indices = df[mask].index.tolist()
            sample_rows.append({
                "duplicate_value": {col: group[col] for col in columns},
                "occurrences": int(group['count']),
                "rows": indices[:10]
            })

        return {
            "valid": False,
            "violations": len(duplicates),
            "sample_rows": sample_rows
        }

    return {"valid": True, "violations": 0, "sample_rows": []}


def check_vocabulary_constraint(df: pd.DataFrame, columns: list, params: dict) -> dict:
    """
    Check vocabulary constraint.

    Params: {"allowed_values": [list of allowed values]}
    Example: col_a values must be in allowed list
    """
    if len(columns) != 1:
        return {
            "valid": False,
            "error": "Vocabulary constraint requires exactly 1 column"
        }

    col = columns[0]
    allowed_values = params.get("allowed_values", [])

    if col not in df.columns:
        return {
            "valid": False,
            "error": f"Missing column: {col}"
        }

    if not allowed_values:
        return {
            "valid": False,
            "error": "No allowed values specified"
        }

    # Check for values not in vocabulary
    allowed_set = set(allowed_values)
    non_null = df[col].dropna()

    invalid_mask = ~non_null.isin(allowed_set)
    violation_count = invalid_mask.sum()

    if violation_count > 0:
        invalid_values = non_null[invalid_mask].unique()
        violation_indices = non_null[invalid_mask].index.tolist()

        sample_rows = []
        for val in invalid_values[:5]:
            rows_with_val = non_null[non_null == val].index.tolist()
            sample_rows.append({
                "invalid_value": val,
                "occurrences": len(rows_with_val),
                "rows": rows_with_val[:10]
            })

        return {
            "valid": False,
            "violations": int(violation_count),
            "sample_rows": sample_rows
        }

    return {"valid": True, "violations": 0, "sample_rows": []}


def check_constraint(df: pd.DataFrame, constraint: dict) -> dict:
    """Check a single constraint."""
    constraint_type = constraint.get("type")
    columns = constraint.get("columns", [])
    params = constraint.get("params", {})

    if constraint_type == "comparison":
        return check_comparison_constraint(df, columns, params)
    elif constraint_type == "conditional_null":
        return check_conditional_null_constraint(df, columns, params)
    elif constraint_type == "unique_together":
        return check_unique_together_constraint(df, columns, params)
    elif constraint_type == "vocabulary":
        return check_vocabulary_constraint(df, columns, params)
    else:
        return {
            "valid": False,
            "error": f"Unknown constraint type: {constraint_type}"
        }


def main(input_path: str, constraints_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Check cross-column constraints.

    Args:
        input_path: Path to input CSV/Parquet file
        constraints_path: Path to constraints JSON file
        output_path: Path to save validation report
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Result dictionary with constraint check results
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

        constraints_file = Path(constraints_path)
        if not constraints_file.exists():
            return {
                "success": False,
                "error": f"Constraints file not found: {constraints_path}",
                "suggestion": "Verify the constraints file path exists"
            }

        # Load data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input data is empty",
                "suggestion": "Provide non-empty dataset for constraint checking",
                "valid": False
            }

        # Load constraints
        with open(constraints_path, 'r') as f:
            constraints_config = json.load(f)

        constraints_list = constraints_config.get("constraints", [])

        if not constraints_list:
            return {
                "success": True,
                "output_path": str(output_path),
                "valid": True,
                "constraints_checked": 0,
                "constraints_passed": 0,
                "violations": []
            }

        # Check each constraint
        violations = []
        constraints_passed = 0

        for i, constraint in enumerate(constraints_list):
            constraint_type = constraint.get("type", "unknown")
            columns = constraint.get("columns", [])

            result = check_constraint(df, constraint)

            if "error" in result:
                violations.append({
                    "constraint": f"{constraint_type}({', '.join(columns)})",
                    "count": 0,
                    "sample_rows": [],
                    "error": result["error"]
                })
            elif not result.get("valid", True):
                violations.append({
                    "constraint": f"{constraint_type}({', '.join(columns)})",
                    "count": result.get("violations", 0),
                    "sample_rows": result.get("sample_rows", [])
                })
            else:
                constraints_passed += 1

        # Prepare result
        is_valid = len(violations) == 0

        result = {
            "success": True,
            "output_path": str(output_path),
            "valid": is_valid,
            "constraints_checked": len(constraints_list),
            "constraints_passed": constraints_passed,
            "violations": violations
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
            "suggestion": "Check input file format and constraints structure"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check cross-column constraints")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet file")
    parser.add_argument("--constraints", required=True,
                        help="Constraints JSON file (format: {\"constraints\": [{\"type\": \"comparison|vocabulary|conditional_null|unique_together\", \"columns\": [...], \"params\": {...}}]})")
    parser.add_argument("--output", required=True, help="Output validation report JSON")
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

    result = main(args.input, args.constraints, args.output, input_format=args.input_format)

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output)
        if output_path:
            meta = {
                "script": os.path.relpath(__file__),
                "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
                "rows_in": result.get("rows_in", 0),
                "rows_out": result.get("rows_out", 0),
                "duration_seconds": round(time.time() - _start_time, 3),
            }
            ckpt_path = maybe_checkpoint(output_path, "constraints", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
