#!/usr/bin/env python3
"""
Detect statistical pitfalls and sanity issues.

Identifies 7 common pitfalls: join explosion, survivorship bias, Simpson's paradox,
look-ahead bias, selection bias, metric gaming, and ecological fallacy.
Also performs order-of-magnitude checks.
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
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def check_magnitude_issues(df: pd.DataFrame) -> list:
    """Check for order-of-magnitude issues in numeric columns."""
    issues = []

    for col in df.select_dtypes(include=[np.number]).columns:
        non_null = df[col].dropna()

        if len(non_null) == 0:
            continue

        # Calculate statistics
        col_min = non_null.min()
        col_max = non_null.max()
        col_median = non_null.median()
        col_mean = non_null.mean()

        # Check if max >> median (potential outliers or scale issues)
        if col_median != 0 and col_max > 1000 * col_median:
            issues.append({
                "column": col,
                "issue": f"max ({col_max:.2f}) > 1000 * median ({col_median:.2f})",
                "severity": "warning"
            })

        # Check for negative values in typically positive columns
        if col_min < 0:
            col_lower = col.lower()
            positive_keywords = ['price', 'cost', 'count', 'quantity', 'amount', 'total', 'age', 'distance', 'weight', 'height', 'duration']
            if any(kw in col_lower for kw in positive_keywords):
                issues.append({
                    "column": col,
                    "issue": f"negative values found (min={col_min:.2f}) in typically positive column",
                    "severity": "warning"
                })

        # Check for suspiciously narrow range
        if col_max == col_min and len(non_null) > 10:
            issues.append({
                "column": col,
                "issue": f"constant value ({col_max}) across all rows",
                "severity": "info"
            })

    return issues


def detect_join_explosion(df: pd.DataFrame) -> dict | None:
    """Detect potential join explosion (very high cardinality columns)."""
    row_count = len(df)

    for col in df.columns:
        unique_count = df[col].nunique()
        cardinality_ratio = unique_count / row_count

        if cardinality_ratio > 0.95 and row_count > 100:
            return {
                "pitfall": "join_explosion",
                "description": "High cardinality column may cause join explosions",
                "evidence": f"Column '{col}' has {unique_count} unique values across {row_count} rows ({cardinality_ratio:.1%} cardinality)",
                "severity": "warning"
            }

    return None


def detect_survivorship_bias(df: pd.DataFrame) -> dict | None:
    """Detect potential survivorship bias (skewed selection/filter columns)."""
    # Look for boolean or binary columns with very skewed distributions
    for col in df.columns:
        unique_vals = df[col].dropna().unique()

        # Check for binary/boolean columns
        if len(unique_vals) == 2:
            value_counts = df[col].value_counts(normalize=True)
            max_proportion = value_counts.max()

            # If one value dominates (>95%), potential survivorship bias
            if max_proportion > 0.95:
                col_lower = col.lower()
                bias_keywords = ['active', 'approved', 'selected', 'winner', 'success', 'passed', 'qualified', 'eligible']

                if any(kw in col_lower for kw in bias_keywords):
                    return {
                        "pitfall": "survivorship_bias",
                        "description": "Highly skewed selection column may indicate survivorship bias",
                        "evidence": f"Column '{col}' has {max_proportion:.1%} of one value, suggesting filtered/selected data",
                        "severity": "warning"
                    }

    return None


def detect_simpsons_paradox(df: pd.DataFrame) -> dict | None:
    """Detect potential Simpson's paradox (correlation reversal when grouped)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Need at least 2 numeric columns and 1 categorical
    if len(numeric_cols) < 2 or len(categorical_cols) < 1:
        return None

    # Check first pair of numeric columns with first categorical column
    for cat_col in categorical_cols[:2]:  # Limit search
        unique_vals = df[cat_col].nunique()

        # Only check if categorical has 2-10 groups
        if not (2 <= unique_vals <= 10):
            continue

        for i, col1 in enumerate(numeric_cols[:3]):  # Limit search
            for col2 in numeric_cols[i+1:i+3]:
                # Calculate overall correlation
                overall_corr = df[[col1, col2]].corr().iloc[0, 1]

                if np.isnan(overall_corr):
                    continue

                # Calculate grouped correlations
                grouped_corrs = []
                for group_val in df[cat_col].unique():
                    group_df = df[df[cat_col] == group_val]
                    if len(group_df) > 10:  # Need sufficient data
                        group_corr = group_df[[col1, col2]].corr().iloc[0, 1]
                        if not np.isnan(group_corr):
                            grouped_corrs.append(group_corr)

                # Check for sign reversal
                if len(grouped_corrs) > 0:
                    avg_grouped_corr = np.mean(grouped_corrs)

                    # If overall and grouped correlations have opposite signs and are non-trivial
                    if (overall_corr * avg_grouped_corr < 0 and
                        abs(overall_corr) > 0.2 and abs(avg_grouped_corr) > 0.2):
                        return {
                            "pitfall": "simpsons_paradox",
                            "description": "Correlation reverses direction when grouped",
                            "evidence": f"Overall correlation between '{col1}' and '{col2}' is {overall_corr:.2f}, but averages {avg_grouped_corr:.2f} when grouped by '{cat_col}'",
                            "severity": "warning"
                        }

    return None


def detect_lookahead_bias(df: pd.DataFrame) -> dict | None:
    """Detect look-ahead bias (future-dated entries)."""
    from datetime import datetime

    now = datetime.now()

    # Check datetime columns
    for col in df.columns:
        try:
            # Try to parse as datetime
            dt_series = pd.to_datetime(df[col], errors='coerce')
            future_mask = dt_series > now

            future_count = future_mask.sum()
            if future_count > 0:
                future_ratio = future_count / len(df)

                if future_ratio > 0.01:  # More than 1% future dates
                    return {
                        "pitfall": "lookahead_bias",
                        "description": "Future-dated entries detected",
                        "evidence": f"Column '{col}' has {future_count} ({future_ratio:.1%}) future-dated entries",
                        "severity": "error"
                    }
        except:
            continue

    return None


def detect_selection_bias(df: pd.DataFrame) -> dict | None:
    """Detect selection bias (suspicious gaps in expected ranges)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        non_null = df[col].dropna()

        if len(non_null) < 100:
            continue

        # Check for gaps in distribution
        sorted_vals = non_null.sort_values()
        diffs = sorted_vals.diff()

        if len(diffs) > 10:
            # Calculate typical gap
            median_diff = diffs.median()

            # Look for large gaps (>10x median)
            large_gaps = diffs[diffs > 10 * median_diff]

            if len(large_gaps) > 0:
                col_lower = col.lower()
                range_keywords = ['date', 'time', 'id', 'sequence', 'number']

                if any(kw in col_lower for kw in range_keywords):
                    return {
                        "pitfall": "selection_bias",
                        "description": "Suspicious gaps detected in expected continuous range",
                        "evidence": f"Column '{col}' has {len(large_gaps)} gaps >10x the median spacing (median={median_diff:.2f})",
                        "severity": "warning"
                    }

    return None


def detect_metric_gaming(df: pd.DataFrame) -> dict | None:
    """Detect metric gaming (suspicious concentration of round numbers)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        non_null = df[col].dropna()

        if len(non_null) < 100:
            continue

        # Check for round number concentration
        # Round numbers: divisible by 5, 10, 100, etc.
        round_10 = (non_null % 10 == 0).sum()
        round_100 = (non_null % 100 == 0).sum()

        round_10_ratio = round_10 / len(non_null)
        round_100_ratio = round_100 / len(non_null)

        # If too many round numbers (>40% divisible by 10, or >15% by 100)
        if round_10_ratio > 0.4 or round_100_ratio > 0.15:
            col_lower = col.lower()
            metric_keywords = ['score', 'rating', 'revenue', 'target', 'goal', 'quota', 'performance']

            if any(kw in col_lower for kw in metric_keywords):
                return {
                    "pitfall": "metric_gaming",
                    "description": "Suspicious concentration of round numbers suggesting gaming",
                    "evidence": f"Column '{col}' has {round_10_ratio:.1%} values divisible by 10 ({round_100_ratio:.1%} by 100)",
                    "severity": "warning"
                }

    return None


def detect_ecological_fallacy(df: pd.DataFrame) -> dict | None:
    """Detect ecological fallacy (aggregated stats alongside individual data)."""
    # Look for columns with aggregation keywords alongside detail columns
    agg_keywords = ['avg', 'average', 'mean', 'total', 'sum', 'aggregate', 'group']
    detail_keywords = ['id', 'name', 'individual', 'person', 'user', 'customer']

    agg_cols = []
    detail_cols = []

    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in agg_keywords):
            agg_cols.append(col)
        if any(kw in col_lower for kw in detail_keywords):
            detail_cols.append(col)

    # If we have both aggregated and detail columns
    if len(agg_cols) > 0 and len(detail_cols) > 0:
        return {
            "pitfall": "ecological_fallacy",
            "description": "Mix of aggregated and individual-level data may lead to ecological fallacy",
            "evidence": f"Found aggregated columns {agg_cols} alongside detail columns {detail_cols}",
            "severity": "info"
        }

    return None


def main(input_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Detect statistical pitfalls and sanity issues.

    Args:
        input_path: Path to input CSV/Parquet file
        output_path: Path to save sanity check report
        input_format: File format (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        Result dictionary with detected issues
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

        # Load data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input data is empty",
                "suggestion": "Provide non-empty dataset for sanity checking"
            }

        # Run magnitude checks
        magnitude_checks = check_magnitude_issues(df)

        # Run pitfall detection
        pitfalls_detected = []

        # Check each pitfall
        pitfall_detectors = [
            detect_join_explosion,
            detect_survivorship_bias,
            detect_simpsons_paradox,
            detect_lookahead_bias,
            detect_selection_bias,
            detect_metric_gaming,
            detect_ecological_fallacy
        ]

        for detector in pitfall_detectors:
            try:
                result = detector(df)
                if result:
                    pitfalls_detected.append(result)
            except Exception as e:
                # Don't fail the entire check if one detector fails
                pass

        # Prepare result
        result = {
            "success": True,
            "output_path": str(output_path),
            "rows_in": len(df),
            "checks": {
                "magnitude_checks": magnitude_checks,
                "pitfalls_detected": pitfalls_detected
            },
            "pitfall_count": len(pitfalls_detected)
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
            "suggestion": "Check input file format and data integrity"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect statistical pitfalls and sanity issues")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet file")
    parser.add_argument("--output", default="logs/sanity_check.json", help="Output sanity check report JSON (default: logs/sanity_check.json)")
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

    result = main(args.input, args.output, input_format=args.input_format)

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
            ckpt_path = maybe_checkpoint(output_path, "sanity_check", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
