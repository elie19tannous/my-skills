#!/usr/bin/env python3
"""
Create calculated columns with safe expression evaluation.
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.


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


def parse_expressions(expressions_str=None, expressions_path=None):
    """Parse expressions from string or file."""
    if expressions_path:
        with open(expressions_path, 'r') as f:
            import json as json_lib
            expressions_dict = json_lib.load(f)
    elif expressions_str:
        # Try to parse as JSON first
        try:
            import json as json_lib
            expressions_dict = json_lib.loads(expressions_str)
        except:
            # Parse as comma-separated "new_col=expr" pairs
            expressions_dict = {}
            pairs = expressions_str.split(",")
            for pair in pairs:
                if "=" not in pair:
                    raise ValueError(f"Invalid expression format: {pair}")
                col, expr = pair.split("=", 1)
                expressions_dict[col.strip()] = expr.strip()
    else:
        raise ValueError("Must provide either expressions or expressions_path")

    return expressions_dict


def safe_eval_expression(df, col_name, expression):
    """Safely evaluate expression using pandas operations."""
    # Create a safe namespace with only pandas and numpy functions
    safe_namespace = {
        'df': df,
        'np': np,
        'pd': pd,
        'abs': abs,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
    }

    # Add column references to namespace
    for col in df.columns:
        safe_namespace[col] = df[col]

    try:
        # First try pd.eval for simple arithmetic
        if any(op in expression for op in ['+', '-', '*', '/', '>', '<', '==', '!=', '&', '|']):
            # Check for disallowed patterns
            if any(danger in expression.lower() for danger in ['import', 'exec', 'eval', '__', 'open', 'file']):
                raise ValueError(f"Potentially unsafe expression: {expression}")

            try:
                result = pd.eval(expression, local_dict=safe_namespace, global_dict={})
                return result
            except:
                pass  # Fall through to next method

        # Handle string operations
        if '.str.' in expression:
            # This is a string operation - evaluate in safe namespace
            if any(danger in expression.lower() for danger in ['import', 'exec', 'eval', '__', 'open', 'file']):
                raise ValueError(f"Potentially unsafe expression: {expression}")

            result = eval(expression, {"__builtins__": {}}, safe_namespace)
            return result

        # Handle conditional expressions with 'if'
        if 'if' in expression and 'else' in expression:
            # This is a conditional - use numpy where
            if any(danger in expression.lower() for danger in ['import', 'exec', 'eval', '__', 'open', 'file']):
                raise ValueError(f"Potentially unsafe expression: {expression}")

            # Parse simple conditional: "'high' if revenue > 1000 else 'low'"
            result = eval(expression, {"__builtins__": {}}, safe_namespace)
            return result

        # For other expressions, try safe evaluation
        if any(danger in expression.lower() for danger in ['import', 'exec', 'eval', '__', 'open', 'file']):
            raise ValueError(f"Potentially unsafe expression: {expression}")

        result = eval(expression, {"__builtins__": {}}, safe_namespace)
        return result

    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expression}': {str(e)}")


def main(input_path: str, output_path: str,
         expressions: str = None, expressions_path: str = None,
         input_format: str = "auto", output_format: str = "auto",
         chunk_size: int = None) -> dict:
    """
    Create calculated columns.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        expressions: JSON string or comma-separated "new_col=expr" pairs
        expressions_path: Path to JSON file with expression definitions
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)
        output_format: File format for output (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Derivation results
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

        # Parse expressions
        expressions_dict = parse_expressions(expressions, expressions_path)

        if not expressions_dict:
            return {
                "success": False,
                "error": "No expressions provided",
                "suggestion": "Provide expressions via --expressions or --expressions-path"
            }

        columns_created = []
        summary = {}

        # Evaluate each expression
        for col_name, expression in expressions_dict.items():
            try:
                df[col_name] = safe_eval_expression(df, col_name, expression)
                columns_created.append(col_name)
                summary[col_name] = {
                    "expression": expression,
                    "type": str(df[col_name].dtype),
                    "null_count": int(df[col_name].isna().sum())
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create column '{col_name}': {str(e)}",
                    "suggestion": "Check expression syntax and column references"
                }

        # Save output
        save_dataframe(df, output_path, format=output_format, input_format=input_format)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(df),
            "columns_created": columns_created,
            "summary": summary
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
            "suggestion": "Check expression format and syntax"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and expressions"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Derive calculated columns")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--expressions", help="JSON string or comma-separated 'new_col=expr' pairs")
    parser.add_argument("--expressions_path", "--expressions-path",
                        help="Path to JSON file with expressions (format: {\"column_name\": \"expression\"})")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        default="auto", help="Output file format (default: auto-detect from extension)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        if not os.path.isfile(args.input_path):
            print(json.dumps({"success": False, "error": f"Input file not found: {args.input_path}"}, indent=2))
            sys.exit(1)
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "derive",
                "input": args.input_path,
                "output": args.output_path,
                "steps": [
                    "Load input CSV file",
                    "Parse column expressions from --expressions or --expressions-path",
                    "Safely evaluate each expression against the dataframe",
                    "Append derived columns to the dataframe",
                    "Write resulting CSV to output path"
                ],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(args.input_path, args.output_path,
                  args.expressions, args.expressions_path,
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
        ckpt_path = maybe_checkpoint(args.output_path, "derive", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
