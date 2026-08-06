#!/usr/bin/env python3
"""
Chart Selector - Recommend chart types based on data relationships
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def detect_column_type(series):
    """Detect semantic type of a column."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif pd.api.types.is_object_dtype(series):
        # Check if it's text (avg length > 20) vs categorical
        non_null = series.dropna()
        if len(non_null) == 0:
            return "categorical"
        avg_len = non_null.astype(str).str.len().mean()
        if avg_len > 20:
            return "text"
        return "categorical"
    return "categorical"


def analyze_columns(df):
    """Analyze all columns for visualization suitability."""
    analysis = {}
    for col in df.columns:
        col_type = detect_column_type(df[col])
        unique_count = df[col].nunique()

        suitable_for = []
        if col_type == "numeric":
            suitable_for = ["distribution", "correlation", "trend", "comparison"]
        elif col_type == "datetime":
            suitable_for = ["trend"]
        elif col_type == "categorical":
            if unique_count <= 20:
                suitable_for = ["comparison", "composition", "ranking", "grouping"]
            else:
                suitable_for = ["ranking"]
        elif col_type == "text":
            suitable_for = ["text_analysis"]

        analysis[col] = {
            "type": col_type,
            "unique": unique_count,
            "suitable_for": suitable_for
        }

    return analysis


def recommend_for_distribution(df, col_analysis):
    """Recommend charts for distribution analysis."""
    recommendations = []
    numeric_cols = [col for col, info in col_analysis.items() if info["type"] == "numeric"]

    for col in numeric_cols:
        recommendations.append({
            "relationship": "distribution",
            "chart_type": "histogram",
            "columns": [col],
            "reason": f"Show distribution of {col}",
            "priority": 1
        })
        recommendations.append({
            "relationship": "distribution",
            "chart_type": "kde",
            "columns": [col],
            "reason": f"Smoothed density estimate for {col}",
            "priority": 2
        })
        recommendations.append({
            "relationship": "distribution",
            "chart_type": "box",
            "columns": [col],
            "reason": f"Show quartiles and outliers for {col}",
            "priority": 2
        })

    return recommendations


def recommend_for_comparison(df, col_analysis):
    """Recommend charts for comparing groups."""
    recommendations = []
    numeric_cols = [col for col, info in col_analysis.items() if info["type"] == "numeric"]
    categorical_cols = [col for col, info in col_analysis.items()
                       if info["type"] == "categorical" and info["unique"] <= 20]

    for cat_col in categorical_cols:
        for num_col in numeric_cols:
            recommendations.append({
                "relationship": "comparison",
                "chart_type": "bar",
                "columns": [cat_col, num_col],
                "reason": f"Compare {num_col} across {cat_col}",
                "priority": 1
            })
            recommendations.append({
                "relationship": "comparison",
                "chart_type": "box",
                "columns": [cat_col, num_col],
                "reason": f"Compare {num_col} distributions by {cat_col}",
                "priority": 2
            })

    return recommendations


def recommend_for_trend(df, col_analysis):
    """Recommend charts for time series."""
    recommendations = []
    datetime_cols = [col for col, info in col_analysis.items() if info["type"] == "datetime"]
    numeric_cols = [col for col, info in col_analysis.items() if info["type"] == "numeric"]

    for dt_col in datetime_cols:
        for num_col in numeric_cols:
            recommendations.append({
                "relationship": "trend",
                "chart_type": "line",
                "columns": [dt_col, num_col],
                "reason": f"Show {num_col} over time ({dt_col})",
                "priority": 1
            })
            recommendations.append({
                "relationship": "trend",
                "chart_type": "area",
                "columns": [dt_col, num_col],
                "reason": f"Show cumulative {num_col} over time",
                "priority": 2
            })

    return recommendations


def recommend_for_correlation(df, col_analysis):
    """Recommend charts for correlation analysis."""
    recommendations = []
    numeric_cols = [col for col, info in col_analysis.items() if info["type"] == "numeric"]

    # Pairwise combinations
    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i+1:]:
            recommendations.append({
                "relationship": "correlation",
                "chart_type": "scatter",
                "columns": [col1, col2],
                "reason": f"Explore relationship between {col1} and {col2}",
                "priority": 1
            })

    # Heatmap if 3+ numeric columns
    if len(numeric_cols) >= 3:
        recommendations.append({
            "relationship": "correlation",
            "chart_type": "heatmap",
            "columns": numeric_cols,
            "reason": "Correlation matrix for all numeric variables",
            "priority": 1
        })

    return recommendations


def recommend_for_composition(df, col_analysis):
    """Recommend charts for part-to-whole."""
    recommendations = []
    categorical_cols = [col for col, info in col_analysis.items()
                       if info["type"] == "categorical" and info["unique"] <= 20]

    for col in categorical_cols:
        recommendations.append({
            "relationship": "composition",
            "chart_type": "horizontal_bar",
            "columns": [col],
            "reason": f"Show composition of {col} (horizontal bars preferred over pie)",
            "priority": 1
        })

    return recommendations


def recommend_for_ranking(df, col_analysis):
    """Recommend charts for ranking."""
    recommendations = []
    numeric_cols = [col for col, info in col_analysis.items() if info["type"] == "numeric"]
    categorical_cols = [col for col, info in col_analysis.items()
                       if info["type"] == "categorical" and info["unique"] <= 30]

    for cat_col in categorical_cols:
        for num_col in numeric_cols:
            recommendations.append({
                "relationship": "ranking",
                "chart_type": "horizontal_bar",
                "columns": [cat_col, num_col],
                "reason": f"Rank {cat_col} by {num_col}",
                "priority": 1
            })

    return recommendations


def recommend_for_text(df, col_analysis):
    """Recommend charts for text analysis."""
    recommendations = []
    text_cols = [col for col, info in col_analysis.items() if info["type"] == "text"]

    for col in text_cols:
        recommendations.append({
            "relationship": "text_analysis",
            "chart_type": "word_frequency_bar",
            "columns": [col],
            "reason": f"Show most common terms in {col}",
            "priority": 1
        })
        recommendations.append({
            "relationship": "text_analysis",
            "chart_type": "text_length_histogram",
            "columns": [col],
            "reason": f"Show text length distribution for {col}",
            "priority": 2
        })

    return recommendations


def score_recommendation(rec, df, col_analysis):
    """Score a recommendation 0-100 based on data characteristics.

    Considers time series detection, categorical detection, and distribution
    detection to adjust scores. Higher priority recommendations start with
    a higher base score.

    Args:
        rec: Recommendation dict with chart_type, columns, priority, etc.
        df: The DataFrame being analyzed.
        col_analysis: Column analysis dict from analyze_columns().

    Returns:
        (score, reason) tuple.
    """
    # Base score from priority (priority 1 → 80, priority 2 → 60, etc.)
    priority = rec.get("priority", 2)
    base = max(100 - (priority - 1) * 20, 20)
    score = base
    reasons = []

    columns = rec.get("columns", [])
    chart_type = rec.get("chart_type", "")
    relationship = rec.get("relationship", "")

    # --- Time series detection ---
    has_time_col = False
    for col in columns:
        if col not in df.columns:
            continue
        info = col_analysis.get(col, {})
        col_type = info.get("type", "")
        if col_type == "datetime":
            has_time_col = True
            break
        # Check monotonically increasing numeric (index-like or timestamp-like)
        if col_type == "numeric" and len(df[col].dropna()) > 2:
            if df[col].dropna().is_monotonic_increasing:
                has_time_col = True
                break

    if has_time_col:
        if chart_type in ("line", "area"):
            score += 15
            reasons.append("time series data favors line/area charts")
        elif chart_type in ("bar", "scatter"):
            score -= 10
            reasons.append("time series data is better shown with line charts")

    # --- Categorical detection ---
    has_low_cardinality_cat = False
    for col in columns:
        info = col_analysis.get(col, {})
        if info.get("type") == "categorical" and info.get("unique", 999) < 20:
            has_low_cardinality_cat = True
            break

    if has_low_cardinality_cat:
        if chart_type in ("bar", "horizontal_bar"):
            score += 10
            reasons.append("low-cardinality categorical column favors bar charts")
        elif chart_type in ("scatter", "line"):
            score -= 5
            reasons.append("categorical data is better compared with bar charts")

    # --- Distribution detection (single numeric column) ---
    if (len(columns) == 1
            and col_analysis.get(columns[0], {}).get("type") == "numeric"):
        if chart_type == "histogram":
            score += 15
            reasons.append("single numeric column is ideal for histogram")
        elif chart_type in ("box", "kde"):
            score += 5
            reasons.append("single numeric column suits distribution charts")

    # --- Correlation boost for many numeric columns ---
    if relationship == "correlation" and chart_type == "heatmap":
        num_numeric = sum(1 for i in col_analysis.values() if i.get("type") == "numeric")
        if num_numeric >= 5:
            score += 10
            reasons.append("many numeric columns make heatmap especially useful")

    # Clamp to 0-100
    score = max(0, min(100, score))

    reason = "; ".join(reasons) if reasons else "standard recommendation based on data types"
    return score, reason


def get_anti_recommendations():
    """Return list of anti-patterns to avoid."""
    return [
        {"chart_type": "pie", "reason": "Difficult to compare angles; use horizontal bar instead"},
        {"chart_type": "3d_bar", "reason": "3D distorts perception; use 2D"},
        {"chart_type": "3d_pie", "reason": "Worst of both worlds; use horizontal bar"},
        {"chart_type": "dual_axis", "reason": "Can mislead by manipulating scale"},
        {"chart_type": "donut", "reason": "Same issues as pie chart"},
        {"chart_type": "radar", "reason": "Hard to read; use small multiples instead"}
    ]


def main(input_path: str, output_path: str, relationship: str = "auto",
         input_format: str = "auto") -> dict:
    """
    Recommend chart types based on data relationship.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output JSON file
        relationship: Type of relationship to analyze

    Returns:
        Dictionary with success status and recommendations
    """
    try:
        # Read data
        df = load_dataframe(input_path, format=input_format)
        rows_in = len(df)

        if rows_in == 0:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a CSV file with at least one row"
            }

        # Analyze columns
        col_analysis = analyze_columns(df)

        # Generate recommendations based on relationship
        recommendations = []

        if relationship == "auto":
            # Generate all recommendations
            recommendations.extend(recommend_for_distribution(df, col_analysis))
            recommendations.extend(recommend_for_comparison(df, col_analysis))
            recommendations.extend(recommend_for_trend(df, col_analysis))
            recommendations.extend(recommend_for_correlation(df, col_analysis))
            recommendations.extend(recommend_for_composition(df, col_analysis))
            recommendations.extend(recommend_for_ranking(df, col_analysis))
            recommendations.extend(recommend_for_text(df, col_analysis))
        elif relationship == "distribution":
            recommendations = recommend_for_distribution(df, col_analysis)
        elif relationship == "comparison":
            recommendations = recommend_for_comparison(df, col_analysis)
        elif relationship == "trend":
            recommendations = recommend_for_trend(df, col_analysis)
        elif relationship == "correlation":
            recommendations = recommend_for_correlation(df, col_analysis)
        elif relationship == "composition":
            recommendations = recommend_for_composition(df, col_analysis)
        elif relationship == "ranking":
            recommendations = recommend_for_ranking(df, col_analysis)
        else:
            return {
                "success": False,
                "error": f"Unknown relationship type: {relationship}",
                "suggestion": "Use: auto, distribution, comparison, trend, correlation, composition, ranking"
            }

        # Score each recommendation
        for rec in recommendations:
            s, r = score_recommendation(rec, df, col_analysis)
            rec["score"] = s
            rec["reason"] = r

        # Sort by score descending (higher is better)
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        # Build result
        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "recommendations": recommendations,
            "anti_recommendations": get_anti_recommendations(),
            "column_analysis": col_analysis
        }

        # Write output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check the file path"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recommend chart types based on data relationships")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument("--relationship", default="auto",
                       choices=["auto", "distribution", "comparison", "trend",
                               "correlation", "composition", "ranking"],
                       help="Type of relationship to analyze")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()

    result = main(args.input_path, args.output_path, args.relationship,
                  input_format=args.input_format)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
