#!/usr/bin/env python3
"""
DataFrame reshaping operations.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
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


def pivot_operation(df, index_col, columns_col, values_col):
    """Perform pivot operation."""
    if index_col not in df.columns:
        raise ValueError(f"Index column '{index_col}' not found")
    if columns_col not in df.columns:
        raise ValueError(f"Columns column '{columns_col}' not found")
    if values_col and values_col not in df.columns:
        raise ValueError(f"Values column '{values_col}' not found")

    result = df.pivot(index=index_col, columns=columns_col, values=values_col)
    result = result.reset_index()

    # Flatten column names if multi-level
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(map(str, col)).strip('_') for col in result.columns.values]

    return result


def melt_operation(df, id_vars, value_vars=None, var_name='variable', value_name='value'):
    """Perform melt operation."""
    if id_vars:
        id_vars_list = [v.strip() for v in id_vars.split(",")]
        for col in id_vars_list:
            if col not in df.columns:
                raise ValueError(f"ID variable '{col}' not found")
    else:
        id_vars_list = None

    if value_vars:
        value_vars_list = [v.strip() for v in value_vars.split(",")]
        for col in value_vars_list:
            if col not in df.columns:
                raise ValueError(f"Value variable '{col}' not found")
    else:
        value_vars_list = None

    result = pd.melt(df, id_vars=id_vars_list, value_vars=value_vars_list,
                     var_name=var_name, value_name=value_name)

    return result


def stack_operation(df):
    """Perform stack operation (pivot columns to rows)."""
    # Set first column as index if not already indexed
    if df.index.name is None and len(df.columns) > 0:
        df = df.set_index(df.columns[0])

    result = df.stack().reset_index()
    result.columns = ['index', 'variable', 'value']

    return result


def unstack_operation(df):
    """Perform unstack operation (pivot rows to columns)."""
    # Assume first two columns are index levels
    if len(df.columns) < 3:
        raise ValueError("Unstack requires at least 3 columns (2 index + 1 value)")

    df = df.set_index([df.columns[0], df.columns[1]])
    result = df.unstack().reset_index()

    # Flatten column names if multi-level
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ['_'.join(map(str, col)).strip('_') for col in result.columns.values]

    return result


def main(input_path: str, output_path: str,
         operation: str = "pivot", index_col: str = None,
         columns_col: str = None, values_col: str = None,
         id_vars: str = None, value_vars: str = None,
         var_name: str = "variable", value_name: str = "value",
         input_format: str = "auto", output_format: str = "auto") -> dict:
    """
    DataFrame reshaping operations.

    Args:
        input_path: Path to input CSV
        output_path: Path to output CSV
        operation: "pivot" | "melt" | "stack" | "unstack"
        index_col: Index column for pivot
        columns_col: Columns column for pivot
        values_col: Values column for pivot
        id_vars: ID variables for melt (comma-separated)
        value_vars: Value variables for melt (comma-separated)
        var_name: Variable name for melt
        value_name: Value name for melt

    Returns:
        dict: Reshape results
    """
    try:
        # Load data
        df = load_dataframe(input_path, format=input_format)

        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        shape_before = list(df.shape)

        # Perform operation
        if operation == "pivot":
            if not index_col or not columns_col:
                return {
                    "success": False,
                    "error": "Pivot requires index_col and columns_col",
                    "suggestion": "Specify --index-col and --columns-col"
                }
            result_df = pivot_operation(df, index_col, columns_col, values_col)

        elif operation == "melt":
            result_df = melt_operation(df, id_vars, value_vars, var_name, value_name)

        elif operation == "stack":
            result_df = stack_operation(df)

        elif operation == "unstack":
            result_df = unstack_operation(df)

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "suggestion": "Use one of: pivot, melt, stack, unstack"
            }

        shape_after = list(result_df.shape)

        # Save output
        save_dataframe(result_df, output_path, format=output_format, input_format=input_format)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(result_df),
            "shape_before": shape_before,
            "shape_after": shape_after,
            "summary": {
                "operation": operation
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
            "suggestion": "Check column names and operation parameters"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and operation parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reshape DataFrames")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--operation", choices=["pivot", "melt", "stack", "unstack"],
                        default="pivot", help="Reshape operation")
    parser.add_argument("--index_col", "--index-col", help="Index column for pivot")
    parser.add_argument("--columns_col", "--columns-col", help="Columns column for pivot")
    parser.add_argument("--values_col", "--values-col", help="Values column for pivot")
    parser.add_argument("--id_vars", "--id-vars", help="ID variables for melt (comma-separated)")
    parser.add_argument("--value_vars", "--value-vars", help="Value variables for melt (comma-separated)")
    parser.add_argument("--var_name", "--var-name", default="variable", help="Variable name for melt")
    parser.add_argument("--value_name", "--value-name", default="value", help="Value name for melt")
    parser.add_argument("--input-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Output file format (default: auto-detect from extension)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(args.input_path, args.output_path, args.operation,
                  args.index_col, args.columns_col, args.values_col,
                  args.id_vars, args.value_vars, args.var_name, args.value_name,
                  args.input_format, args.output_format)

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
            ckpt_path = maybe_checkpoint(output_path, "reshape", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
