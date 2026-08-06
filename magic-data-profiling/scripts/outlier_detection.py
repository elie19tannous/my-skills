#!/usr/bin/env python3
"""
Outlier Detection Script
Detect statistical outliers in numeric columns using IQR and/or Z-score methods.
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
from scipy import stats


def load_dataframe(path, format="auto", **kwargs):
    """Stub: load a DataFrame from path. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    ext = str(path).rsplit(".", 1)[-1].lower()
    fmt = format if format != "auto" else ext
    if fmt in ("parquet",):
        return pd.read_parquet(path)
    if fmt in ("jsonl", "ndjson"):
        return pd.read_json(path, lines=True)
    if fmt in ("json",):
        return pd.read_json(path)
    if fmt in ("tsv",):
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)


def detect_outliers_iqr(series: pd.Series, threshold: float = 1.5) -> dict:
    """Detect outliers using Interquartile Range (IQR) method."""
    clean_data = series.dropna()

    if len(clean_data) == 0:
        return None

    # Calculate quartiles
    Q1 = clean_data.quantile(0.25)
    Q3 = clean_data.quantile(0.75)
    IQR = Q3 - Q1

    # Calculate bounds
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR

    # Identify outliers
    outlier_mask = (clean_data < lower_bound) | (clean_data > upper_bound)
    outlier_values = clean_data[outlier_mask].tolist()
    outlier_indices = clean_data[outlier_mask].index.tolist()

    # Limit to first 20 for readability
    outlier_values_display = outlier_values[:20]
    outlier_indices_display = [int(idx) for idx in outlier_indices[:20]]

    return {
        "method": "iqr",
        "count": len(outlier_values),
        "pct": float(len(outlier_values) / len(clean_data) * 100),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_values": outlier_values_display,
        "outlier_indices": outlier_indices_display
    }


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> dict:
    """Detect outliers using Z-score method."""
    clean_data = series.dropna()

    if len(clean_data) == 0:
        return None

    # Calculate z-scores
    z_scores = np.abs(stats.zscore(clean_data))

    # Identify outliers
    outlier_mask = z_scores > threshold
    outlier_values = clean_data[outlier_mask].tolist()
    outlier_indices = clean_data[outlier_mask].index.tolist()

    # Calculate bounds (mean ± threshold * std)
    mean = clean_data.mean()
    std = clean_data.std()
    lower_bound = mean - threshold * std
    upper_bound = mean + threshold * std

    # Limit to first 20 for readability
    outlier_values_display = outlier_values[:20]
    outlier_indices_display = [int(idx) for idx in outlier_indices[:20]]

    return {
        "method": "zscore",
        "count": len(outlier_values),
        "pct": float(len(outlier_values) / len(clean_data) * 100),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_values": outlier_values_display,
        "outlier_indices": outlier_indices_display
    }


def analyze_outlier_overlap(iqr_result: dict, zscore_result: dict) -> dict:
    """Analyze overlap between IQR and Z-score outlier detection methods."""
    iqr_indices = set(iqr_result["outlier_indices"])
    zscore_indices = set(zscore_result["outlier_indices"])

    overlap_indices = iqr_indices.intersection(zscore_indices)
    only_iqr = iqr_indices - zscore_indices
    only_zscore = zscore_indices - iqr_indices

    return {
        "overlap_count": len(overlap_indices),
        "only_iqr_count": len(only_iqr),
        "only_zscore_count": len(only_zscore)
    }


def main(input_path: str, output_path: str,
         method: str = "iqr", threshold: float = 1.5,
         columns: str = None, input_format: str = "auto") -> dict:
    """
    Detect statistical outliers in numeric columns.

    Args:
        input_path: Path to input file
        output_path: Path to output JSON file
        method: Detection method ("iqr", "zscore", "both")
        threshold: IQR multiplier (default: 1.5) or Z-score threshold (default: 3.0 when method=zscore)
        columns: Comma-separated column names (optional, default: all numeric)
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Outlier detection results
    """
    try:
        # Validate method
        if method not in ["iqr", "zscore", "both"]:
            return {
                "success": False,
                "error": f"Invalid method: {method}",
                "suggestion": "Use 'iqr', 'zscore', or 'both'"
            }

        # Read input data
        df = load_dataframe(input_path, format=input_format)
        rows_in = len(df)

        # Quality gate: check for empty input
        if rows_in == 0:
            return {
                "success": False,
                "error": "Input dataset is empty",
                "suggestion": "Provide a dataset with at least one row"
            }

        # Parse columns parameter
        if columns:
            column_list = [col.strip() for col in columns.split(',')]
            # Validate columns exist
            missing_cols = [col for col in column_list if col not in df.columns]
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Columns not found: {missing_cols}",
                    "suggestion": f"Available columns: {list(df.columns)}"
                }
        else:
            # Select only numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            column_list = numeric_df.columns.tolist()

        if len(column_list) == 0:
            return {
                "success": False,
                "error": "No numeric columns found in dataset",
                "suggestion": "Outlier detection requires numeric columns"
            }

        # Detect outliers
        outliers = {}
        all_outlier_indices = set()

        for col in column_list:
            series = df[col]

            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(series):
                continue

            col_results = {}

            if method in ["iqr", "both"]:
                iqr_result = detect_outliers_iqr(series, threshold)
                if iqr_result:
                    if method == "both":
                        col_results["iqr"] = iqr_result
                    else:
                        col_results = iqr_result
                    all_outlier_indices.update(iqr_result["outlier_indices"])

            if method in ["zscore", "both"]:
                # Use threshold 3.0 for zscore if still default 1.5
                zscore_threshold = threshold if method == "zscore" else 3.0
                zscore_result = detect_outliers_zscore(series, zscore_threshold)
                if zscore_result:
                    if method == "both":
                        col_results["zscore"] = zscore_result
                        # Add overlap analysis
                        if "iqr" in col_results:
                            col_results["overlap"] = analyze_outlier_overlap(
                                col_results["iqr"],
                                col_results["zscore"]
                            )
                    else:
                        col_results = zscore_result
                    all_outlier_indices.update(zscore_result["outlier_indices"])

            if col_results:
                outliers[col] = col_results

        # Calculate total outlier statistics
        total_outlier_rows = len(all_outlier_indices)
        total_outlier_pct = float(total_outlier_rows / rows_in * 100) if rows_in > 0 else 0.0

        # Prepare output
        output_data = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "method": method,
            "threshold": threshold,
            "outliers": outliers,
            "total_outlier_rows": total_outlier_rows,
            "total_outlier_pct": total_outlier_pct
        }

        # Write output JSON
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        return output_data

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check the file path and try again"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect statistical outliers in numeric columns")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument("--method", default="iqr", choices=["iqr", "zscore", "both"],
                        help="Detection method (default: iqr)")
    parser.add_argument("--threshold", type=float, default=1.5,
                        help="IQR multiplier (default: 1.5) or Z-score threshold")
    parser.add_argument("--columns", help="Comma-separated column names (optional)")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(args.input_path, args.output_path, args.method, args.threshold,
                  args.columns, args.input_format)

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            def maybe_checkpoint(path, tag, save=True, checkpoint_format=None, metadata=None):
                """Stub: save checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
                return None
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(output_path, "outliers", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("success") else 1)
