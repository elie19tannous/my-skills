#!/usr/bin/env python3
"""
Data Quality Score Script
Compute composite data quality score (0-100) across multiple dimensions.
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


def assess_completeness(df: pd.DataFrame) -> dict:
    """
    Assess data completeness (30% weight).

    Score: 100 - (missing_pct * 100 / max_missing)
    """
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isna().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0

    # Score 0 if more than 50% missing overall
    if missing_pct > 50:
        score = 0.0
        detail = f"{missing_pct:.1f}% of data is missing (critical level)"
    else:
        # Linear scaling: 0% missing = 100, 50% missing = 0
        score = max(0, 100 - (missing_pct * 2))
        detail = f"{missing_pct:.1f}% of data is missing"

    # Add per-column breakdown
    col_missing = df.isna().sum()
    high_missing_cols = col_missing[col_missing > len(df) * 0.3].to_dict()

    if high_missing_cols:
        detail += f". High missing: {list(high_missing_cols.keys())}"

    return {
        "score": float(score),
        "detail": detail,
        "missing_pct": float(missing_pct),
        "high_missing_columns": {k: int(v) for k, v in high_missing_cols.items()}
    }


def assess_consistency(df: pd.DataFrame) -> dict:
    """
    Assess data consistency (25% weight).

    Checks for mixed types per column and inconsistent formats.
    """
    issues = []
    issue_count = 0

    for col in df.columns:
        series = df[col].dropna()

        if len(series) == 0:
            continue

        # Check for mixed types (numeric and string in same column)
        if pd.api.types.is_object_dtype(series):
            # Try to convert to numeric
            numeric_count = pd.to_numeric(series, errors='coerce').notna().sum()
            total_count = len(series)

            # If 10-90% can be converted to numeric, it's likely mixed
            if 0.1 < (numeric_count / total_count) < 0.9:
                issues.append(f"'{col}' has mixed types (numeric and text)")
                issue_count += 1

        # Check for inconsistent string formats (for string columns)
        if pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
            # Check for inconsistent whitespace
            has_leading = series.astype(str).str.match(r'^\s+').any()
            has_trailing = series.astype(str).str.match(r'\s+$').any()

            if has_leading or has_trailing:
                issues.append(f"'{col}' has inconsistent whitespace")
                issue_count += 1

    # Score based on percentage of columns with issues
    total_cols = len(df.columns)
    issue_pct = (issue_count / total_cols * 100) if total_cols > 0 else 0

    score = max(0, 100 - issue_pct * 2)  # Penalize heavily

    if issue_count == 0:
        detail = "No consistency issues detected"
    else:
        detail = f"{issue_count} consistency issue(s) found"

    return {
        "score": float(score),
        "detail": detail,
        "issues": issues[:5]  # Limit to first 5 for readability
    }


def assess_uniqueness(df: pd.DataFrame) -> dict:
    """
    Assess data uniqueness (20% weight).

    Checks for exact row duplicates.
    """
    total_rows = len(df)
    # Exclude non-hashable columns (dict/list) before duplicate check
    hashable_cols = []
    for col in df.columns:
        try:
            df[col].iloc[:1].apply(hash)
            hashable_cols.append(col)
        except (TypeError, ValueError):
            pass
    if hashable_cols:
        duplicate_rows = df[hashable_cols].duplicated().sum()
    else:
        duplicate_rows = 0
    duplicate_pct = (duplicate_rows / total_rows * 100) if total_rows > 0 else 0

    # Score: 100 - duplicate_pct
    score = max(0, 100 - duplicate_pct)

    if duplicate_rows == 0:
        detail = "No duplicate rows found"
    else:
        detail = f"{duplicate_rows} duplicate row(s) ({duplicate_pct:.1f}%)"

    return {
        "score": float(score),
        "detail": detail,
        "duplicate_count": int(duplicate_rows),
        "duplicate_pct": float(duplicate_pct)
    }


def assess_validity(df: pd.DataFrame) -> dict:
    """
    Assess data validity (25% weight).

    Checks for outliers and invalid values.
    """
    numeric_df = df.select_dtypes(include=[np.number])

    if len(numeric_df.columns) == 0:
        return {
            "score": 100.0,
            "detail": "No numeric columns to validate"
        }

    total_numeric_values = numeric_df.count().sum()
    outlier_count = 0

    # Detect outliers using IQR method
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()

        if len(series) < 4:
            continue

        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        outlier_count += outliers

    outlier_pct = (outlier_count / total_numeric_values * 100) if total_numeric_values > 0 else 0

    # Score: penalize for high outlier percentage
    if outlier_pct > 20:
        score = 0.0
        detail = f"High outlier rate: {outlier_pct:.1f}% (critical)"
    else:
        score = max(0, 100 - outlier_pct * 5)  # 5x penalty
        detail = f"{outlier_pct:.1f}% outliers detected"

    return {
        "score": float(score),
        "detail": detail,
        "outlier_count": int(outlier_count),
        "outlier_pct": float(outlier_pct)
    }


def compute_overall_score(dimensions: dict) -> tuple:
    """
    Compute weighted overall score.

    Weights: completeness (30%), consistency (25%), uniqueness (20%), validity (25%)
    """
    weights = {
        "completeness": 0.30,
        "consistency": 0.25,
        "uniqueness": 0.20,
        "validity": 0.25
    }

    overall_score = sum(
        dimensions[dim]["score"] * weights[dim]
        for dim in weights.keys()
    )

    # Determine grade
    if overall_score >= 90:
        grade = "A"
    elif overall_score >= 75:
        grade = "B"
    elif overall_score >= 60:
        grade = "C"
    elif overall_score >= 40:
        grade = "D"
    else:
        grade = "F"

    return float(overall_score), grade


def generate_recommendations(dimensions: dict, overall_score: float) -> list:
    """Generate actionable recommendations based on low-scoring dimensions."""
    recommendations = []

    # Check each dimension
    if dimensions["completeness"]["score"] < 70:
        recommendations.append(
            "COMPLETENESS: Address missing data - consider imputation or removal of "
            "high-missing columns/rows"
        )

    if dimensions["consistency"]["score"] < 70:
        issues = dimensions["consistency"].get("issues", [])
        if issues:
            recommendations.append(
                f"CONSISTENCY: Fix data type and format issues - {len(issues)} issue(s) detected"
            )

    if dimensions["uniqueness"]["score"] < 80:
        recommendations.append(
            "UNIQUENESS: Remove duplicate rows to improve data quality"
        )

    if dimensions["validity"]["score"] < 70:
        recommendations.append(
            "VALIDITY: Investigate and handle outliers - consider domain knowledge "
            "to determine if they are errors or legitimate extreme values"
        )

    # Overall recommendation
    if overall_score < 60:
        recommendations.insert(0, "CRITICAL: Overall quality is low - prioritize data cleaning before analysis")

    if not recommendations:
        recommendations.append("Data quality is good - no critical issues detected")

    return recommendations


def main(input_path: str, output_path: str, input_format: str = "auto") -> dict:
    """
    Compute composite data quality score (0-100).

    Args:
        input_path: Path to input file
        output_path: Path to output JSON file
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Quality assessment results
    """
    try:
        # Read input data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: check for empty input
        if len(df) == 0:
            return {
                "success": False,
                "error": "Input dataset is empty",
                "suggestion": "Provide a dataset with at least one row"
            }

        # Assess each dimension
        dimensions = {
            "completeness": assess_completeness(df),
            "consistency": assess_consistency(df),
            "uniqueness": assess_uniqueness(df),
            "validity": assess_validity(df)
        }

        # Compute overall score
        overall_score, grade = compute_overall_score(dimensions)

        # Generate recommendations
        recommendations = generate_recommendations(dimensions, overall_score)

        # Prepare output
        output_data = {
            "success": True,
            "output_path": output_path,
            "overall_score": overall_score,
            "grade": grade,
            "dimensions": dimensions,
            "recommendations": recommendations
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
    parser = argparse.ArgumentParser(description="Compute data quality score")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output JSON file")
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

    result = main(args.input_path, args.output_path, args.input_format)

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
        ckpt_path = maybe_checkpoint(output_path, "quality", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("success") else 1)
