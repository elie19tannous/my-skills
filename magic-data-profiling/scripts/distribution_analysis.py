#!/usr/bin/env python3
"""
Distribution Analysis Script
Compute per-column distribution characteristics for numeric and text columns.
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


def analyze_numeric_distribution(series: pd.Series, col_name: str) -> dict:
    """Analyze distribution characteristics for a numeric column."""
    # Skip boolean columns (numpy doesn't support arithmetic on bools)
    if series.dtype == bool:
        return None

    # Remove NaN values
    clean_data = series.dropna()

    if len(clean_data) == 0:
        return None

    # Calculate skewness and kurtosis
    skewness = float(stats.skew(clean_data))
    kurtosis = float(stats.kurtosis(clean_data))

    # Shapiro-Wilk test (cap at 5000 samples)
    sample_size = min(len(clean_data), 5000)
    sample_data = clean_data.sample(n=sample_size, random_state=42) if len(clean_data) > 5000 else clean_data

    try:
        shapiro_stat, shapiro_p = stats.shapiro(sample_data)
        is_normal = shapiro_p > 0.05
    except Exception as e:
        shapiro_stat, shapiro_p = None, None
        is_normal = False

    # Determine distribution shape
    if is_normal:
        distribution_shape = "normal"
    elif abs(skewness) > 2:
        distribution_shape = "right_skewed" if skewness > 0 else "left_skewed"
    elif kurtosis > 3:
        distribution_shape = "heavy_tailed"
    elif kurtosis < -1:
        distribution_shape = "light_tailed"
    else:
        distribution_shape = "normal"

    # Calculate histogram
    hist_counts, bin_edges = np.histogram(clean_data, bins=10)
    histogram_bins = [float(edge) for edge in bin_edges]
    histogram_counts = [int(count) for count in hist_counts]

    result = {
        "skewness": skewness,
        "kurtosis": kurtosis,
        "shapiro_test": {
            "statistic": float(shapiro_stat) if shapiro_stat is not None else None,
            "p_value": float(shapiro_p) if shapiro_p is not None else None
        },
        "is_normal": is_normal,
        "distribution_shape": distribution_shape,
        "histogram_bins": histogram_bins,
        "histogram_counts": histogram_counts
    }

    return result


def analyze_text_distribution(series: pd.Series, col_name: str) -> dict:
    """Analyze distribution characteristics for a text column."""
    # Remove NaN values and convert to string
    clean_data = series.dropna().astype(str)

    if len(clean_data) == 0:
        return None

    # Character length distribution
    lengths = clean_data.str.len()
    length_distribution = {
        "mean": float(lengths.mean()),
        "median": float(lengths.median()),
        "std": float(lengths.std()),
        "min": int(lengths.min()),
        "max": int(lengths.max())
    }

    # Word count distribution
    word_counts = clean_data.str.split().str.len()
    word_count_distribution = {
        "mean": float(word_counts.mean()),
        "median": float(word_counts.median()),
        "std": float(word_counts.std())
    }

    # Vocabulary analysis
    all_words = ' '.join(clean_data).lower().split()
    vocabulary_size = len(set(all_words))

    # Top 20 terms
    from collections import Counter
    word_freq = Counter(all_words)
    top_20_terms = [
        {"term": term, "count": count}
        for term, count in word_freq.most_common(20)
    ]

    result = {
        "length_distribution": length_distribution,
        "word_count_distribution": word_count_distribution,
        "vocabulary_size": vocabulary_size,
        "top_20_terms": top_20_terms
    }

    return result


def main(input_path: str, output_path: str, columns: str = None,
         input_format: str = "auto") -> dict:
    """
    Analyze distribution characteristics for columns in a dataset.

    Args:
        input_path: Path to input file
        output_path: Path to output JSON file
        columns: Comma-separated column names (optional, default: all)
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Analysis results with distribution metrics
    """
    try:
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
            column_list = df.columns.tolist()

        # Analyze distributions
        distributions = {
            "numeric": {},
            "text": {}
        }

        for col in column_list:
            series = df[col]

            # Determine column type
            if pd.api.types.is_numeric_dtype(series):
                result = analyze_numeric_distribution(series, col)
                if result:
                    distributions["numeric"][col] = result
            elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
                result = analyze_text_distribution(series, col)
                if result:
                    distributions["text"][col] = result

        # Prepare output
        output_data = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_in,
            "distributions": distributions
        }

        # Write output JSON
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

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
    parser = argparse.ArgumentParser(description="Analyze distribution characteristics")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output JSON file")
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

    result = main(args.input_path, args.output_path, args.columns, args.input_format)

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
        ckpt_path = maybe_checkpoint(output_path, "distribution", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("success") else 1)
