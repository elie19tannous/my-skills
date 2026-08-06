#!/usr/bin/env python3
"""
Compare statistics across groups/segments.
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

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def auto_detect_group_column(df):
    """Auto-detect best grouping column (2-10 unique values)."""
    candidates = []

    for col in df.columns:
        nunique = df[col].nunique()
        if 2 <= nunique <= 10:
            # Prefer categorical or object types
            if pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
                candidates.append((col, nunique, 2))  # priority 2
            else:
                candidates.append((col, nunique, 1))  # priority 1

    if not candidates:
        return None

    # Sort by priority (desc), then by number of unique values (asc)
    candidates.sort(key=lambda x: (-x[2], x[1]))
    return candidates[0][0]


def compute_segment_stats(df, group_col, value_cols):
    """Compute statistics for each segment."""
    segments = {}

    for group_value, group_df in df.groupby(group_col):
        segment_stats = {
            "n": len(group_df),
            "pct": 100 * len(group_df) / len(df),
            "stats": {}
        }

        for col in value_cols:
            if pd.api.types.is_numeric_dtype(group_df[col]):
                segment_stats["stats"][col] = {
                    "mean": float(group_df[col].mean()),
                    "median": float(group_df[col].median()),
                    "std": float(group_df[col].std())
                }
            elif pd.api.types.is_string_dtype(group_df[col]):
                # Text stats: average word count
                word_counts = group_df[col].dropna().str.split().str.len()
                if len(word_counts) > 0:
                    segment_stats["stats"][col] = {
                        "avg_word_count": float(word_counts.mean()),
                        "median_word_count": float(word_counts.median())
                    }

        segments[str(group_value)] = segment_stats

    return segments


def test_numeric_differences(df, group_col, value_col):
    """Test for significant differences in numeric column across groups."""
    groups = [group_df[value_col].dropna() for _, group_df in df.groupby(group_col)]

    # Filter out empty groups
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 2:
        return None

    if len(groups) == 2:
        # Mann-Whitney U test
        stat, p = stats.mannwhitneyu(groups[0], groups[1], alternative='two-sided')
        test_name = "Mann-Whitney U"
    else:
        # Kruskal-Wallis test
        stat, p = stats.kruskal(*groups)
        test_name = "Kruskal-Wallis"

    significant = p < 0.05

    if significant:
        if p < 0.01:
            interpretation = f"The differences in '{value_col}' across groups appear highly significant (p < 0.01)"
        else:
            interpretation = f"The differences in '{value_col}' across groups may be significant (p < 0.05)"
    else:
        interpretation = f"No strong evidence of differences in '{value_col}' across groups (p >= 0.05)"

    return {
        "column": value_col,
        "test": test_name,
        "p_value": float(p),
        "significant": significant,
        "interpretation": interpretation
    }


def test_text_differences(df, group_col, value_col):
    """Compare text characteristics across groups."""
    groups = {}
    for group_value, group_df in df.groupby(group_col):
        text_data = group_df[value_col].dropna()
        if len(text_data) > 0:
            word_counts = text_data.str.split().str.len()
            groups[group_value] = {
                "avg_words": word_counts.mean(),
                "vocabulary": set(' '.join(text_data).lower().split())
            }

    if len(groups) < 2:
        return None

    # Compare word counts
    word_count_groups = [pd.Series([groups[k]["avg_words"]]) for k in groups.keys()]
    if len(word_count_groups) >= 2:
        group_values = list(groups.keys())
        interpretation = f"Average word count in '{value_col}' varies across groups: "
        interpretation += ", ".join([f"{k}: {groups[k]['avg_words']:.1f}" for k in group_values[:3]])

        return {
            "column": value_col,
            "test": "text_comparison",
            "p_value": None,
            "significant": False,
            "interpretation": interpretation
        }

    return None


def main(input_path: str, output_path: str,
         group_col: str = None, value_cols: str = None,
         auto_detect: bool = True, input_format: str = "auto") -> dict:
    """
    Compare statistics across groups/segments.

    Args:
        input_path: Path to input CSV
        output_path: Path to output CSV
        group_col: Column to group by
        value_cols: Comma-separated columns to analyze
        auto_detect: Auto-detect group column if not specified

    Returns:
        dict: Segmentation results
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

        # Auto-detect group column if needed
        if group_col is None and auto_detect:
            group_col = auto_detect_group_column(df)
            if group_col is None:
                return {
                    "success": False,
                    "error": "No suitable grouping column found",
                    "suggestion": "Specify a group_col with 2-10 unique values"
                }

        if group_col not in df.columns:
            return {
                "success": False,
                "error": f"Group column '{group_col}' not found",
                "suggestion": f"Available columns: {', '.join(df.columns)}"
            }

        # Determine value columns
        if value_cols is None:
            # Use all columns except group column
            value_cols_list = [c for c in df.columns if c != group_col]
        else:
            value_cols_list = [c.strip() for c in value_cols.split(",")]

        # Compute segment statistics
        segments = compute_segment_stats(df, group_col, value_cols_list)

        # Test for significant differences
        significant_differences = []

        for col in value_cols_list:
            if col == group_col:
                continue

            if pd.api.types.is_numeric_dtype(df[col]):
                result = test_numeric_differences(df, group_col, col)
                if result:
                    significant_differences.append(result)
            elif pd.api.types.is_string_dtype(df[col]):
                result = test_text_differences(df, group_col, col)
                if result:
                    significant_differences.append(result)

        # Create output dataframe
        output_rows = []
        for group_value, segment_info in segments.items():
            row = {
                "group_value": group_value,
                "n": segment_info["n"],
                "pct": segment_info["pct"]
            }
            for col, stats_dict in segment_info["stats"].items():
                for stat_name, stat_value in stats_dict.items():
                    row[f"{col}_{stat_name}"] = stat_value
            output_rows.append(row)

        output_df = pd.DataFrame(output_rows)
        output_df.to_csv(output_path, index=False)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(output_df),
            "group_column": group_col,
            "segments": segments,
            "significant_differences": significant_differences
        }

        return result

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
    parser = argparse.ArgumentParser(description="Compare statistics across groups")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--group_col", "--group-col", help="Column to group by")
    parser.add_argument("--value_cols", "--value-cols", help="Comma-separated columns to analyze")
    parser.add_argument("--no-auto-detect", dest="auto_detect", action="store_false",
                        help="Disable auto-detection of group column")
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

    result = main(args.input_path, args.output_path, args.group_col, args.value_cols,
                  args.auto_detect, input_format=args.input_format)

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            def maybe_checkpoint(df, path, metadata=None):
                """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
                from pathlib import Path
                p = Path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(p, index=False)
                return str(p)
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(output_path, "segments", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
