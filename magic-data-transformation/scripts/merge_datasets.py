#!/usr/bin/env python3
"""
Dataset merging with join-explosion detection.
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
def save_dataframe(df, path, **kwargs):
    """Stub: save DataFrame to file. See magic-data-loading SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.parquet': df.to_parquet(p, index=False)
    elif p.suffix in ('.jsonl', '.json'): df.to_json(p, orient='records', lines=p.suffix == '.jsonl')
    else: df.to_csv(p, index=False)

def maybe_checkpoint(df, path, metadata=None):
    """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)


def main(input_path: str, right_path: str, output_path: str,
         how: str = "inner", on: str = None,
         left_on: str = None, right_on: str = None,
         input_format: str = "auto", right_format: str = "auto",
         output_format: str = "auto") -> dict:
    """
    Dataset merging with join-explosion detection.

    Args:
        input_path: Path to left input file
        right_path: Path to right input file
        output_path: Path to output file
        how: Join type (inner, left, right, outer)
        on: Column(s) to join on (comma-separated)
        left_on: Left join column(s) (comma-separated)
        right_on: Right join column(s) (comma-separated)
        input_format: File format for left input (auto, csv, tsv, jsonl, json, parquet, excel)
        right_format: File format for right input (auto, csv, tsv, jsonl, json, parquet, excel)
        output_format: File format for output (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Merge results
    """
    try:
        # Load data
        df_left = load_dataframe(input_path, format=input_format)
        df_right = load_dataframe(right_path, format=right_format)

        if df_left.empty:
            return {
                "success": False,
                "error": "Left input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        if df_right.empty:
            return {
                "success": False,
                "error": "Right input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        rows_left = len(df_left)
        rows_right = len(df_right)

        # Determine join keys
        if on:
            on_cols = [c.strip() for c in on.split(",")]
            # Validate columns exist in both dataframes
            for col in on_cols:
                if col not in df_left.columns:
                    return {
                        "success": False,
                        "error": f"Column '{col}' not found in left dataset",
                        "suggestion": f"Available columns: {', '.join(df_left.columns)}"
                    }
                if col not in df_right.columns:
                    return {
                        "success": False,
                        "error": f"Column '{col}' not found in right dataset",
                        "suggestion": f"Available columns: {', '.join(df_right.columns)}"
                    }
            merge_kwargs = {"on": on_cols if len(on_cols) > 1 else on_cols[0]}

        elif left_on and right_on:
            left_on_cols = [c.strip() for c in left_on.split(",")]
            right_on_cols = [c.strip() for c in right_on.split(",")]

            if len(left_on_cols) != len(right_on_cols):
                return {
                    "success": False,
                    "error": "left_on and right_on must have same number of columns",
                    "suggestion": "Provide matching column pairs"
                }

            # Validate columns
            for col in left_on_cols:
                if col not in df_left.columns:
                    return {
                        "success": False,
                        "error": f"Column '{col}' not found in left dataset",
                        "suggestion": f"Available columns: {', '.join(df_left.columns)}"
                    }

            for col in right_on_cols:
                if col not in df_right.columns:
                    return {
                        "success": False,
                        "error": f"Column '{col}' not found in right dataset",
                        "suggestion": f"Available columns: {', '.join(df_right.columns)}"
                    }

            merge_kwargs = {
                "left_on": left_on_cols if len(left_on_cols) > 1 else left_on_cols[0],
                "right_on": right_on_cols if len(right_on_cols) > 1 else right_on_cols[0]
            }

        else:
            return {
                "success": False,
                "error": "Must specify either 'on' or both 'left_on' and 'right_on'",
                "suggestion": "Provide join key columns"
            }

        # Validate join type
        valid_how = ["inner", "left", "right", "outer"]
        if how not in valid_how:
            return {
                "success": False,
                "error": f"Invalid join type: {how}",
                "suggestion": f"Use one of: {', '.join(valid_how)}"
            }

        # Perform merge with indicator
        result_df = pd.merge(df_left, df_right, how=how, indicator=True, **merge_kwargs)

        rows_out = len(result_df)

        # Count matched/unmatched
        matched = (result_df['_merge'] == 'both').sum()
        unmatched_left = (result_df['_merge'] == 'left_only').sum()
        unmatched_right = (result_df['_merge'] == 'right_only').sum()

        # Remove merge indicator column
        result_df = result_df.drop('_merge', axis=1)

        # Detect join explosion
        explosion_detected = False
        warnings = []

        max_input_rows = max(rows_left, rows_right)
        if rows_out > 2 * max_input_rows:
            explosion_detected = True
            warnings.append(
                f"Join explosion detected: output has {rows_out} rows, "
                f"much larger than inputs ({rows_left}, {rows_right}). "
                f"Check for duplicate keys or many-to-many relationships."
            )

        # Check for unexpected unmatched rows in inner join
        if how == "inner" and (unmatched_left > 0 or unmatched_right > 0):
            # This shouldn't happen with inner join
            pass

        if how == "left" and unmatched_left > 0.5 * rows_left:
            warnings.append(
                f"Warning: {unmatched_left} left rows ({100*unmatched_left/rows_left:.1f}%) "
                f"did not match. Check join keys."
            )

        if how == "right" and unmatched_right > 0.5 * rows_right:
            warnings.append(
                f"Warning: {unmatched_right} right rows ({100*unmatched_right/rows_right:.1f}%) "
                f"did not match. Check join keys."
            )

        # Save output
        save_dataframe(result_df, output_path, format=output_format, input_format=input_format)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_left": rows_left,
            "rows_right": rows_right,
            "rows_out": rows_out,
            "join_type": how,
            "matched": int(matched),
            "unmatched_left": int(unmatched_left),
            "unmatched_right": int(unmatched_right),
            "explosion_detected": explosion_detected,
            "warnings": warnings
        }

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check file paths and try again"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and join parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge datasets")
    parser.add_argument("input_path", help="Path to left CSV file")
    parser.add_argument("right_path", help="Path to right CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--how", choices=["inner", "left", "right", "outer"],
                        default="inner", help="Join type")
    parser.add_argument("--on", help="Column(s) to join on (comma-separated)")
    parser.add_argument("--left-on", help="Left join column(s) (comma-separated)")
    parser.add_argument("--right-on", help="Right join column(s) (comma-separated)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Left input file format (default: auto-detect from extension)")
    parser.add_argument("--right-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Right input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Output file format (default: auto-detect from extension)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        if not os.path.isfile(args.input_path):
            print(json.dumps({"success": False, "error": f"Input file not found: {args.input_path}"}, indent=2))
            sys.exit(1)
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "merge",
                "input": args.input_path,
                "output": args.output_path,
                "steps": [
                    "Load left CSV file from input_path",
                    "Load right CSV file from right_path",
                    "Validate join key columns in both datasets",
                    f"Perform {args.how} join on specified keys",
                    "Detect join explosion (output rows >> input rows)",
                    "Write merged CSV to output path"
                ],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(args.input_path, args.right_path, args.output_path,
                  args.how, args.on, args.left_on, args.right_on,
                  args.input_format, args.right_format, args.output_format)

    if result.get("success") and args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_left", result.get("rows_in", 0)),
            "rows_out": result.get("rows_out", 0),
            "format": getattr(args, "output_format", "json"),
            "input_path": getattr(args, "input_path", getattr(args, "input", "")),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(args.output_path, "merge", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
