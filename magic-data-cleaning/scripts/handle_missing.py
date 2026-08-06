#!/usr/bin/env python3
"""
Missing value handling script.
Handles missing values using various strategies: auto, median, mean, mode, knn, drop, or fill.
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


def get_column_type(series):
    """Determine if a column is numeric, categorical, or text."""
    # Skip if all null
    if series.isna().all():
        return "empty"

    # Check if numeric
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    # Check if it's object/string type (pandas 3.x uses dtype 'str', not 'object')
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return "empty"

        # If unique values are small relative to total, it's categorical
        unique_ratio = len(non_null.unique()) / len(non_null)
        if unique_ratio < 0.5:  # More than 50% repetition
            return "categorical"
        else:
            return "text"

    return "other"


def impute_with_knn(df, columns_to_impute, k=5):
    """Impute using KNN. Fallback to median if sklearn not available."""
    try:
        from sklearn.impute import KNNImputer

        # Only use numeric columns for KNN
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_to_process = [col for col in columns_to_impute if col in numeric_cols]

        if not cols_to_process:
            return df, {}

        # Create imputer
        imputer = KNNImputer(n_neighbors=k)

        # Impute
        df[cols_to_process] = imputer.fit_transform(df[cols_to_process])

        return df, {col: "knn" for col in cols_to_process}

    except ImportError:
        # Fallback to median
        result = {}
        for col in columns_to_impute:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
                result[col] = "median (knn unavailable)"
        return df, result


def auto_strategy(df):
    """
    Apply automatic strategy based on column type and missing percentage.
    - >50% missing → drop column
    - numeric <100K rows → KNN (k=5)
    - numeric >=100K rows → median
    - categorical → mode
    - text → empty string
    """
    columns_imputed = {}
    columns_dropped = []
    rows_dropped = 0

    # First pass: identify columns to drop
    for col in df.columns:
        missing_pct = df[col].isna().sum() / len(df)
        if missing_pct > 0.5:
            columns_dropped.append(col)

    # Drop columns
    df = df.drop(columns=columns_dropped)

    # Second pass: impute remaining columns
    numeric_cols_for_knn = []

    for col in df.columns:
        if df[col].isna().sum() == 0:
            continue

        col_type = get_column_type(df[col])

        if col_type == "numeric":
            if len(df) < 100000:
                # Use KNN for smaller datasets
                numeric_cols_for_knn.append(col)
            else:
                # Use median for larger datasets
                df[col] = df[col].fillna(df[col].median())
                columns_imputed[col] = "median"

        elif col_type == "categorical":
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
                columns_imputed[col] = "mode"

        elif col_type == "text":
            df[col] = df[col].fillna("")
            columns_imputed[col] = "empty_string"

        elif col_type == "empty":
            # Column is all null, will be handled by drop logic
            pass

    # Apply KNN to numeric columns if any
    if numeric_cols_for_knn:
        df, knn_results = impute_with_knn(df, numeric_cols_for_knn)
        columns_imputed.update(knn_results)

    return df, {
        "columns_imputed": columns_imputed,
        "columns_dropped": columns_dropped,
        "rows_dropped": rows_dropped
    }


def main(input_path: str, output_path: str, strategy: str = "auto",
         columns: str = None, input_format: str = "auto",
         output_format: str = "auto", flatten_depth: int = 0,
         chunk_size: int = None) -> dict:
    """
    Handle missing values in the dataset.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        strategy: Strategy to use (auto, median, mean, mode, knn, drop_rows, drop_cols, fill_value)
        columns: Comma-separated list of columns to process (None = all)
        input_format: File format for input (auto, csv, jsonl, json, parquet)
        output_format: File format for output (auto, csv, jsonl, json, parquet)

    Returns:
        Dictionary with success status and summary
    """
    try:
        # Read input data
        df = load_dataframe(input_path, format=input_format, flatten_depth=flatten_depth,
                            chunk_size=chunk_size)

        # Quality gate: check for empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        rows_in = len(df)

        # Parse columns if provided
        target_columns = None
        if columns:
            target_columns = [c.strip() for c in columns.split(",")]
            # Validate columns exist
            invalid_cols = [c for c in target_columns if c not in df.columns]
            if invalid_cols:
                return {
                    "success": False,
                    "error": f"Columns not found: {invalid_cols}",
                    "suggestion": "Check column names and try again"
                }

        # Apply strategy
        summary = {}

        if strategy == "auto":
            df, summary = auto_strategy(df)
            strategy_used = "auto"

        elif strategy == "median":
            columns_imputed = {}
            cols_to_process = target_columns or df.columns
            for col in cols_to_process:
                if pd.api.types.is_numeric_dtype(df[col]) and df[col].isna().sum() > 0:
                    df[col] = df[col].fillna(df[col].median())
                    columns_imputed[col] = "median"
            summary = {
                "columns_imputed": columns_imputed,
                "columns_dropped": [],
                "rows_dropped": 0
            }
            strategy_used = "median"

        elif strategy == "mean":
            columns_imputed = {}
            cols_to_process = target_columns or df.columns
            for col in cols_to_process:
                if pd.api.types.is_numeric_dtype(df[col]) and df[col].isna().sum() > 0:
                    df[col] = df[col].fillna(df[col].mean())
                    columns_imputed[col] = "mean"
            summary = {
                "columns_imputed": columns_imputed,
                "columns_dropped": [],
                "rows_dropped": 0
            }
            strategy_used = "mean"

        elif strategy == "mode":
            columns_imputed = {}
            cols_to_process = target_columns or df.columns
            for col in cols_to_process:
                if df[col].isna().sum() > 0:
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col] = df[col].fillna(mode_val[0])
                        columns_imputed[col] = "mode"
            summary = {
                "columns_imputed": columns_imputed,
                "columns_dropped": [],
                "rows_dropped": 0
            }
            strategy_used = "mode"

        elif strategy == "knn":
            cols_to_process = target_columns or df.select_dtypes(include=[np.number]).columns.tolist()
            df, knn_results = impute_with_knn(df, cols_to_process)
            summary = {
                "columns_imputed": knn_results,
                "columns_dropped": [],
                "rows_dropped": 0
            }
            strategy_used = "knn"

        elif strategy == "drop_rows":
            initial_rows = len(df)
            if target_columns:
                df = df.dropna(subset=target_columns)
            else:
                df = df.dropna()
            rows_dropped = initial_rows - len(df)
            summary = {
                "columns_imputed": {},
                "columns_dropped": [],
                "rows_dropped": rows_dropped
            }
            strategy_used = "drop_rows"

        elif strategy == "drop_cols":
            cols_to_drop = []
            cols_to_check = target_columns or df.columns
            for col in cols_to_check:
                if df[col].isna().sum() > 0:
                    cols_to_drop.append(col)
            df = df.drop(columns=cols_to_drop)
            summary = {
                "columns_imputed": {},
                "columns_dropped": cols_to_drop,
                "rows_dropped": 0
            }
            strategy_used = "drop_cols"

        elif strategy == "fill_value":
            columns_imputed = {}
            cols_to_process = target_columns or df.columns
            for col in cols_to_process:
                if df[col].isna().sum() > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                        columns_imputed[col] = "fill_0"
                    else:
                        df[col] = df[col].fillna("")
                        columns_imputed[col] = "fill_empty"
            summary = {
                "columns_imputed": columns_imputed,
                "columns_dropped": [],
                "rows_dropped": 0
            }
            strategy_used = "fill_value"

        else:
            return {
                "success": False,
                "error": f"Unknown strategy: {strategy}",
                "suggestion": "Use one of: auto, median, mean, mode, knn, drop_rows, drop_cols, fill_value"
            }

        # Quality gate: check for empty output
        if df.empty:
            return {
                "success": False,
                "error": "Output is empty after processing",
                "suggestion": "Strategy removed all data. Try a different approach"
            }

        rows_out = len(df)

        # Save output
        save_dataframe(df, output_path, format=output_format, input_format=input_format)

        # Build result
        summary["strategy_used"] = strategy_used
        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "summary": summary
        }

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check that the file path is correct"
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
            "suggestion": "Check input file format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handle missing values")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output file")
    parser.add_argument("--strategy", default="auto",
                        choices=["auto", "median", "mean", "mode", "knn", "drop_rows", "drop_cols", "fill_value"],
                        help="Strategy for handling missing values")
    parser.add_argument("--columns", help="Comma-separated list of columns to process")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto-detect from extension)")
    parser.add_argument("--flatten-depth", type=int, default=0,
                        help="Flatten nested JSON objects to this depth (0=no flattening)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(args.input_path, args.output_path, args.strategy, args.columns,
                  args.input_format, args.output_format, getattr(args, 'flatten_depth', 0),
                  chunk_size=args.chunk_size)

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
            ckpt_path = maybe_checkpoint(output_path, "handle_missing", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
