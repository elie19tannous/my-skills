#!/usr/bin/env python3
"""
Group-by aggregation operations.
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
try:
    from error_utils import suggest_column, format_column_error
except ImportError:
    suggest_column = None
    format_column_error = None

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


def parse_aggregation_functions(functions_str):
    """Parse comma-separated aggregation functions."""
    valid_functions = {
        'mean': 'mean',
        'sum': 'sum',
        'count': 'count',
        'min': 'min',
        'max': 'max',
        'std': 'std',
        'median': 'median',
        'var': 'var',
        'first': 'first',
        'last': 'last'
    }

    functions = [f.strip().lower() for f in functions_str.split(",")]
    result = []

    for func in functions:
        if func in valid_functions:
            result.append(valid_functions[func])
        else:
            raise ValueError(f"Unknown aggregation function: {func}")

    return result


def main(input_path: str, output_path: str,
         group_cols: str = None, agg_cols: str = None,
         functions: str = "mean,count",
         input_format: str = "auto", output_format: str = "auto",
         chunk_size: int = None) -> dict:
    """
    Group-by aggregation.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        group_cols: Comma-separated columns to group by
        agg_cols: Comma-separated columns to aggregate (None = all numeric)
        functions: Comma-separated aggregation functions
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)
        output_format: File format for output (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Aggregation results
    """
    try:
        # Load data
        df = load_dataframe(input_path, format=input_format, chunk_size=chunk_size)

        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        # Parse group columns
        if group_cols is None:
            return {
                "success": False,
                "error": "Group columns not specified",
                "suggestion": "Specify --group-cols"
            }

        group_cols_list = [c.strip() for c in group_cols.split(",")]

        # Validate group columns
        missing_group = [c for c in group_cols_list if c not in df.columns]
        if missing_group:
            valid = list(df.columns)
            if format_column_error is not None:
                return format_column_error(missing_group, valid)
            elif suggest_column is not None:
                detail = suggest_column(missing_group[0], valid)
                return {"success": False, **detail}
            else:
                return {
                    "success": False,
                    "error": f"Group column(s) not found: {missing_group}",
                    "available_columns": sorted(valid)
                }

        # Parse aggregation columns
        if agg_cols is None:
            # Default to all numeric columns except group columns
            agg_cols_list = df.select_dtypes(include=[np.number]).columns.tolist()
            agg_cols_list = [c for c in agg_cols_list if c not in group_cols_list]
        else:
            agg_cols_list = [c.strip() for c in agg_cols.split(",")]

        # Validate aggregation columns
        missing_agg = [c for c in agg_cols_list if c not in df.columns]
        if missing_agg:
            valid = list(df.columns)
            if format_column_error is not None:
                return format_column_error(missing_agg, valid)
            elif suggest_column is not None:
                detail = suggest_column(missing_agg[0], valid)
                return {"success": False, **detail}
            else:
                return {
                    "success": False,
                    "error": f"Aggregation column(s) not found: {missing_agg}",
                    "available_columns": sorted(valid)
                }

        if not agg_cols_list:
            return {
                "success": False,
                "error": "No columns to aggregate",
                "suggestion": "Specify --agg-cols or ensure numeric columns exist"
            }

        # Parse aggregation functions
        agg_functions = parse_aggregation_functions(functions)

        # Perform aggregation
        grouped = df.groupby(group_cols_list)

        # Build aggregation dictionary
        agg_dict = {}
        for col in agg_cols_list:
            # Only apply functions that make sense for the column type
            if pd.api.types.is_numeric_dtype(df[col]):
                agg_dict[col] = agg_functions
            else:
                # For non-numeric, only use count, first, last
                agg_dict[col] = [f for f in agg_functions if f in ['count', 'first', 'last']]

        result_df = grouped.agg(agg_dict).reset_index()

        # Flatten column names if multi-level
        if isinstance(result_df.columns, pd.MultiIndex):
            result_df.columns = ['_'.join(map(str, col)).strip('_') for col in result_df.columns.values]

        # Save output
        save_dataframe(result_df, output_path, format=output_format, input_format=input_format)

        # Build summary
        aggregations = {}
        for col in agg_cols_list:
            if col in agg_dict:
                aggregations[col] = agg_dict[col]

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(result_df),
            "groups_created": len(result_df),
            "summary": {
                "group_columns": group_cols_list,
                "aggregations": aggregations
            }
        }

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check the file path and try again"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check function names and parameters"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Group-by aggregation")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--group_cols", "--group-cols", help="Comma-separated columns to group by")
    parser.add_argument("--agg_cols", "--agg-cols", help="Comma-separated columns to aggregate")
    parser.add_argument("--functions", default="mean,count",
                        help="Comma-separated aggregation functions")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto-detect from extension)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        # Validate input file exists
        if not os.path.isfile(args.input_path):
            print(json.dumps({
                "success": False,
                "error": f"Input file not found: {args.input_path}"
            }, indent=2))
            sys.exit(1)

        steps = [
            f"Read CSV from {args.input_path}",
            f"Group by columns: {args.group_cols or '(not specified)'}",
            f"Aggregate columns: {args.agg_cols or '(all numeric)'}",
            f"Apply functions: {args.functions}",
            "Flatten multi-level column names",
            f"Write aggregated CSV to {args.output_path}"
        ]
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "aggregate",
                "input": args.input_path,
                "output": args.output_path,
                "steps": steps,
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(args.input_path, args.output_path,
                  args.group_cols, args.agg_cols, args.functions,
                  args.input_format, args.output_format,
                  chunk_size=args.chunk_size)

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
        ckpt_path = maybe_checkpoint(args.output_path, "aggregate", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
