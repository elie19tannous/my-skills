#!/usr/bin/env python3
"""
Cleaning plan executor script.
Reads a cleaning plan JSON and applies per-column strategies.
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.


import argparse
import glob
import json
import os
import shutil
import sys
import time
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


def load_data(input_path, input_format="auto", flatten_depth=0, chunk_size=None):
    """Load data using io_utils, supporting CSV, JSONL, JSON, Parquet, TSV, Excel."""
    return load_dataframe(input_path, format=input_format, flatten_depth=flatten_depth,
                          chunk_size=chunk_size)


def save_data(df, output_path, output_format="auto", input_format=None):
    """Save data using io_utils in format matching the output file extension."""
    save_dataframe(df, output_path, format=output_format, input_format=input_format)


def apply_median_imputation(df, col, params):
    """Apply median imputation to a column."""
    if pd.api.types.is_numeric_dtype(df[col]):
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)
        return {"applied": "median_imputation", "value": float(median_val)}
    else:
        raise ValueError(f"Column {col} is not numeric, cannot apply median imputation")


def apply_mean_imputation(df, col, params):
    """Apply mean imputation to a column."""
    if pd.api.types.is_numeric_dtype(df[col]):
        mean_val = df[col].mean()
        df[col].fillna(mean_val, inplace=True)
        return {"applied": "mean_imputation", "value": float(mean_val)}
    else:
        raise ValueError(f"Column {col} is not numeric, cannot apply mean imputation")


def apply_mode_imputation(df, col, params):
    """Apply mode imputation to a column."""
    mode_val = df[col].mode()
    if len(mode_val) > 0:
        df[col].fillna(mode_val[0], inplace=True)
        return {"applied": "mode_imputation", "value": str(mode_val[0])}
    else:
        raise ValueError(f"Column {col} has no mode value")


def apply_knn_imputation(df, col, params):
    """Apply KNN imputation to a column."""
    try:
        from sklearn.impute import KNNImputer

        k = params.get("k", 5)

        # Only use numeric columns for KNN
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if col not in numeric_cols:
            raise ValueError(f"Column {col} is not numeric, cannot apply KNN imputation")

        # Create imputer
        imputer = KNNImputer(n_neighbors=k)

        # Impute
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

        return {"applied": "knn_imputation", "k": k}

    except ImportError:
        # Fallback to median
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)
        return {"applied": "median_imputation (knn unavailable)", "value": float(median_val)}


def apply_drop_rows(df, col, params):
    """Drop rows with missing values in the column."""
    initial_rows = len(df)
    df.dropna(subset=[col], inplace=True)
    rows_dropped = initial_rows - len(df)
    return {"applied": "drop_rows", "rows_dropped": rows_dropped}


def apply_drop_column(df, col, params):
    """Drop the column."""
    if col in df.columns:
        df.drop(columns=[col], inplace=True)
        return {"applied": "drop_column", "column": col}
    else:
        raise ValueError(f"Column {col} not found")


def apply_fill_empty_string(df, col, params):
    """Fill missing values with empty string."""
    df[col].fillna("", inplace=True)
    return {"applied": "fill_empty_string"}


def apply_fuzzy_match(df, col, params):
    """Apply fuzzy matching to standardize values."""
    # This is a placeholder - real implementation would use fuzzy matching library
    # For now, just do basic string normalization
    df[col] = df[col].astype(str).str.strip().str.lower()
    return {"applied": "fuzzy_match (basic normalization)"}


def apply_parse_formats(df, col, params):
    """Parse and standardize date/time/number formats."""
    format_type = params.get("format_type", "auto")

    if format_type == "date" or format_type == "auto":
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            return {"applied": "parse_formats", "format_type": "date"}
        except Exception:
            pass

    if format_type == "numeric" or format_type == "auto":
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            return {"applied": "parse_formats", "format_type": "numeric"}
        except Exception:
            pass

    return {"applied": "parse_formats", "format_type": "none (no conversion)"}


def apply_custom_mapping(df, col, params):
    """Apply custom value mapping."""
    mapping = params.get("mapping", {})

    if not mapping:
        raise ValueError("Custom mapping requires 'mapping' parameter")

    df[col] = df[col].map(lambda x: mapping.get(str(x), x))
    return {"applied": "custom_mapping", "mappings": len(mapping)}


def apply_trim_whitespace(df, col, params):
    """Trim whitespace from text column."""
    df[col] = df[col].astype(str).str.strip()
    return {"applied": "trim_whitespace"}


def apply_fix_encoding(df, col, params):
    """Fix common encoding issues."""
    # Common mojibake patterns and their fixes
    mojibake_fixes = {
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã ': 'à',
        'â€™': "'",
        'â€œ': '"',
        'â€': '"',
        'â€"': '–',
        'Â': ' ',
    }

    for wrong, correct in mojibake_fixes.items():
        df[col] = df[col].astype(str).str.replace(wrong, correct, regex=False)

    return {"applied": "fix_encoding", "patterns_fixed": len(mojibake_fixes)}


def apply_remove_duplicates(df, params):
    """Remove duplicate rows (global operation)."""
    initial_rows = len(df)
    subset = params.get("subset", None)

    if subset:
        df.drop_duplicates(subset=subset, inplace=True)
    else:
        df.drop_duplicates(inplace=True)

    rows_removed = initial_rows - len(df)
    return {"applied": "remove_duplicates", "rows_removed": rows_removed}


def main(input_path: str, output_path: str, plan_path: str,
         input_format: str = "auto", output_format: str = "auto",
         flatten_depth: int = 0, chunk_size: int = None) -> dict:
    """
    Execute a cleaning plan.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output CSV file
        plan_path: Path to cleaning plan JSON file
        input_format: Input file format (auto, csv, tsv, jsonl, json, parquet, excel)
        output_format: Output file format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Dictionary with success status and summary
    """
    try:
        # Read input data (format-aware: CSV, JSONL, JSON, Parquet)
        df = load_data(input_path, input_format, flatten_depth=flatten_depth,
                       chunk_size=chunk_size)

        # Quality gate: check for empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        rows_in = len(df)

        # Read cleaning plan
        with open(plan_path, 'r') as f:
            plan = json.load(f)

        # Validate plan format
        if "version" not in plan or "columns" not in plan:
            return {
                "success": False,
                "error": "Invalid plan format",
                "suggestion": "Plan must include 'version' and 'columns' fields"
            }

        # Strategy mapping
        strategy_functions = {
            "median_imputation": apply_median_imputation,
            "mean_imputation": apply_mean_imputation,
            "mode_imputation": apply_mode_imputation,
            "knn_imputation": apply_knn_imputation,
            "drop_rows": apply_drop_rows,
            "drop_column": apply_drop_column,
            "fill_empty_string": apply_fill_empty_string,
            "fuzzy_match": apply_fuzzy_match,
            "parse_formats": apply_parse_formats,
            "custom_mapping": apply_custom_mapping,
            "trim_whitespace": apply_trim_whitespace,
            "fix_encoding": apply_fix_encoding,
        }

        # Track results
        column_results = {}
        global_operations = []

        # Process column-specific operations
        columns_config = plan.get("columns", {})
        for col, config in columns_config.items():
            strategy = config.get("strategy")
            params = config.get("params", {})

            if not strategy:
                continue

            # Check if column exists
            if col not in df.columns and strategy != "drop_column":
                column_results[col] = {
                    "error": f"Column {col} not found in data"
                }
                continue

            # Apply strategy
            try:
                if strategy in strategy_functions:
                    result = strategy_functions[strategy](df, col, params)
                    column_results[col] = result
                else:
                    column_results[col] = {
                        "error": f"Unknown strategy: {strategy}"
                    }
            except Exception as e:
                column_results[col] = {
                    "error": str(e)
                }

        # Process global operations (like remove_duplicates)
        global_config = plan.get("global", {})
        if "remove_duplicates" in global_config:
            params = global_config["remove_duplicates"].get("params", {})
            try:
                result = apply_remove_duplicates(df, params)
                global_operations.append(result)
            except Exception as e:
                global_operations.append({
                    "error": str(e)
                })

        # Quality gate: check for empty output
        if df.empty:
            return {
                "success": False,
                "error": "Output is empty after processing",
                "suggestion": "Plan removed all data. Adjust strategies"
            }

        rows_out = len(df)

        # Save output (format-aware: matches output file extension)
        save_data(df, output_path, output_format, input_format=input_format)

        # Build result
        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "summary": {
                "plan_version": plan.get("version"),
                "columns_processed": len(column_results),
                "column_results": column_results,
                "global_operations": global_operations
            }
        }

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check that all file paths are correct"
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": f"Invalid JSON in plan file: {plan_path}",
            "suggestion": "Ensure plan file contains valid JSON"
        }
    except pd.errors.EmptyDataError:
        return {
            "success": False,
            "error": "Input file is empty or invalid",
            "suggestion": "Provide a valid CSV file with data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input files and plan format"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute data cleaning plan")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("plan_path", help="Path to cleaning plan JSON file (format: {\"version\": \"1.0\", \"columns\": {\"col_name\": {\"strategy\": \"...\", \"params\": {...}}}})")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto)")
    parser.add_argument("--flatten-depth", type=int, default=0,
                        help="Flatten nested JSON objects to this depth (0=no flattening)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        # Validate inputs exist
        if not os.path.isfile(args.input_path):
            print(json.dumps({
                "success": False,
                "error": f"Input file not found: {args.input_path}"
            }, indent=2))
            sys.exit(1)
        if not os.path.isfile(args.plan_path):
            print(json.dumps({
                "success": False,
                "error": f"Plan file not found: {args.plan_path}"
            }, indent=2))
            sys.exit(1)

        # Read plan to describe operations
        try:
            with open(args.plan_path, 'r') as f:
                plan = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(json.dumps({
                "success": False,
                "error": f"Invalid plan file: {e}"
            }, indent=2))
            sys.exit(1)

        steps = []
        columns_config = plan.get("columns", {})
        for col, config in columns_config.items():
            strategy = config.get("strategy", "unknown")
            steps.append(f"Apply '{strategy}' to column '{col}'")
        global_config = plan.get("global", {})
        if "remove_duplicates" in global_config:
            steps.append("Remove duplicate rows")

        explain_result = {
            "success": True,
            "execution_plan": {
                "operation": "execute_cleaning_plan",
                "input": args.input_path,
                "output": args.output_path,
                "plan_file": args.plan_path,
                "steps": steps if steps else ["No cleaning operations defined in plan"],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(explain_result, indent=2))
        sys.exit(0)

    result = main(args.input_path, args.output_path, args.plan_path,
                  input_format=args.input_format, output_format=args.output_format,
                  flatten_depth=getattr(args, 'flatten_depth', 0),
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
        ckpt_path = maybe_checkpoint(args.output_path, "clean", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
