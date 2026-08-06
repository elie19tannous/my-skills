#!/usr/bin/env python3
"""
Validate chart metadata against source data.

Checks column existence, chart type validity, required metadata fields,
and scores chart type appropriateness based on data characteristics.
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


VALID_CHART_TYPES = {"line", "bar", "scatter", "histogram", "box", "heatmap", "pie"}


def detect_column_type(series):
    """Detect semantic type of a column."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif pd.api.types.is_object_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return "categorical"
        avg_len = non_null.astype(str).str.len().mean()
        if avg_len > 20:
            return "text"
        return "categorical"
    return "categorical"


def score_chart_appropriateness(df, chart_metadata):
    """
    Score chart type appropriateness (0-100) based on data characteristics.

    Returns a score and a list of reasoning notes.
    """
    chart_type = chart_metadata.get("chart_type", "")
    x_col = chart_metadata.get("x_col")
    y_col = chart_metadata.get("y_col")
    columns = chart_metadata.get("columns", [])

    score = 50  # Neutral baseline
    notes = []

    # Determine x and y types where applicable
    x_type = detect_column_type(df[x_col]) if x_col and x_col in df.columns else None
    y_type = detect_column_type(df[y_col]) if y_col and y_col in df.columns else None

    x_unique = df[x_col].nunique() if x_col and x_col in df.columns else None
    y_unique = df[y_col].nunique() if y_col and y_col in df.columns else None

    if chart_type == "line":
        if x_type == "datetime":
            score = 95
            notes.append("Line chart is ideal for datetime x-axis (time series).")
        elif x_type == "numeric":
            score = 75
            notes.append("Line chart is reasonable for ordered numeric x-axis.")
        else:
            score = 30
            notes.append("Line chart is poorly suited to categorical x-axis; consider bar chart.")

    elif chart_type == "bar":
        if x_type == "categorical" and x_unique is not None and x_unique <= 30:
            score = 95
            notes.append("Bar chart is ideal for comparing values across categories.")
        elif x_type == "categorical" and x_unique is not None and x_unique > 30:
            score = 50
            notes.append("Many categories reduce bar chart readability; consider filtering top-N.")
        elif x_type == "datetime":
            score = 60
            notes.append("Bar chart can work for time series but line chart is preferred.")
        else:
            score = 40
            notes.append("Bar chart is less effective for numeric x-axis.")

    elif chart_type == "scatter":
        if x_type == "numeric" and y_type == "numeric":
            score = 95
            notes.append("Scatter plot is ideal for exploring numeric vs numeric relationships.")
        elif x_type in ("categorical", "datetime") or y_type in ("categorical", "datetime"):
            score = 35
            notes.append("Scatter plot is poorly suited when axes are not both numeric.")
        else:
            score = 50
            notes.append("Scatter plot suitability is unclear given column types.")

    elif chart_type == "histogram":
        # Histogram typically uses a single numeric column
        target_col = x_col or (columns[0] if columns else None)
        if target_col and target_col in df.columns:
            col_type = detect_column_type(df[target_col])
            if col_type == "numeric":
                score = 95
                notes.append("Histogram is ideal for showing the distribution of a numeric variable.")
            else:
                score = 20
                notes.append("Histogram requires a numeric column; this column is not numeric.")
        else:
            score = 40
            notes.append("Cannot determine target column for histogram suitability scoring.")

    elif chart_type == "box":
        if y_type == "numeric":
            score = 90
            notes.append("Box plot is ideal for showing distribution and outliers of a numeric variable.")
            if x_type == "categorical":
                score = 95
                notes.append("Grouping by categorical x-axis further enhances box plot utility.")
        elif x_type == "numeric" and y_type is None:
            score = 85
            notes.append("Box plot is appropriate for a single numeric column distribution.")
        else:
            score = 30
            notes.append("Box plot requires at least one numeric column (typically y-axis).")

    elif chart_type == "heatmap":
        # Heatmap benefits from multiple numeric columns
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if len(numeric_cols) >= 3:
            score = 90
            notes.append(f"Heatmap is appropriate with {len(numeric_cols)} numeric columns for correlation matrix.")
        elif len(numeric_cols) == 2:
            score = 65
            notes.append("Heatmap is marginal with only 2 numeric columns; scatter may be clearer.")
        else:
            score = 20
            notes.append("Heatmap requires multiple numeric columns.")

    elif chart_type == "pie":
        if x_type == "categorical" and x_unique is not None and x_unique <= 7:
            score = 60
            notes.append("Pie chart is marginally acceptable for up to 7 categories, but bar charts are preferred.")
        elif x_type == "categorical" and x_unique is not None and x_unique > 7:
            score = 20
            notes.append("Too many categories for pie chart; use bar chart instead.")
        else:
            score = 25
            notes.append("Pie chart is generally discouraged; use bar chart for better comparison.")

    return max(0, min(100, score)), notes


def main(source_path: str, chart_metadata_path: str, output_path: str,
         input_format: str = "auto") -> dict:
    """
    Validate chart metadata against source data.

    Args:
        source_path: Path to source CSV file
        chart_metadata_path: Path to chart metadata JSON file
        output_path: Path to save validation report JSON

    Returns:
        Result dictionary with validation results
    """
    try:
        # Check source file exists
        source_file = Path(source_path)
        if not source_file.exists():
            return {
                "success": False,
                "error": f"Source file not found: {source_path}",
                "suggestion": "Verify the source CSV file path exists"
            }

        # Check chart metadata file exists
        metadata_file = Path(chart_metadata_path)
        if not metadata_file.exists():
            return {
                "success": False,
                "error": f"Chart metadata file not found: {chart_metadata_path}",
                "suggestion": "Verify the chart metadata JSON file path exists"
            }

        # Load source data
        df = load_dataframe(source_path, format=input_format)

        if df.empty:
            return {
                "success": False,
                "error": "Source data is empty",
                "suggestion": "Provide a non-empty CSV file for validation"
            }

        # Load chart metadata
        with open(chart_metadata_path, 'r') as f:
            chart_metadata = json.load(f)

        checks_passed = 0
        checks_failed = 0
        failures = []

        # --- Check: required metadata fields ---
        chart_type = chart_metadata.get("chart_type")
        x_col = chart_metadata.get("x_col")
        columns = chart_metadata.get("columns", [])

        # chart_type must be present
        if chart_type is None:
            checks_failed += 1
            failures.append({
                "check": "required_field_chart_type",
                "message": "Missing required field: chart_type"
            })
        else:
            checks_passed += 1

        # x_col OR columns must be present
        if not x_col and not columns:
            checks_failed += 1
            failures.append({
                "check": "required_field_x_col_or_columns",
                "message": "Missing required field: either x_col or columns must be present"
            })
        else:
            checks_passed += 1

        # --- Check: chart_type is valid ---
        if chart_type is not None:
            if chart_type not in VALID_CHART_TYPES:
                checks_failed += 1
                failures.append({
                    "check": "chart_type_valid",
                    "message": f"Invalid chart_type '{chart_type}'. Valid types: {sorted(VALID_CHART_TYPES)}"
                })
            else:
                checks_passed += 1

        # --- Check: x_col exists in source data ---
        if x_col:
            if x_col not in df.columns:
                checks_failed += 1
                failures.append({
                    "check": "x_col_exists",
                    "message": f"x_col '{x_col}' not found in source data columns: {list(df.columns)}"
                })
            else:
                checks_passed += 1

        # --- Check: y_col exists in source data ---
        y_col = chart_metadata.get("y_col")
        if y_col:
            if y_col not in df.columns:
                checks_failed += 1
                failures.append({
                    "check": "y_col_exists",
                    "message": f"y_col '{y_col}' not found in source data columns: {list(df.columns)}"
                })
            else:
                checks_passed += 1

        # --- Check: all columns in columns list exist in source data ---
        if columns:
            missing_cols = [c for c in columns if c not in df.columns]
            if missing_cols:
                checks_failed += 1
                failures.append({
                    "check": "columns_exist",
                    "message": f"columns {missing_cols} not found in source data"
                })
            else:
                checks_passed += 1

        # --- Score appropriateness ---
        appropriateness_score = 0
        appropriateness_notes = []

        if chart_type in VALID_CHART_TYPES:
            appropriateness_score, appropriateness_notes = score_chart_appropriateness(df, chart_metadata)

        # Overall success: no hard failures
        is_valid = checks_failed == 0

        result = {
            "success": True,
            "output_path": str(output_path),
            "valid": is_valid,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "failures": failures,
            "appropriateness_score": appropriateness_score,
            "appropriateness_notes": appropriateness_notes,
            "chart_type": chart_type,
            "source_columns": list(df.columns),
            "source_rows": len(df)
        }

        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except FileNotFoundError as e:
        return {
            "success": False,
            "error": f"File not found: {str(e)}",
            "suggestion": "Check that both file paths are correct"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Invalid JSON in chart metadata: {str(e)}",
            "suggestion": "Verify the chart metadata file is valid JSON"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and chart metadata structure"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate chart metadata against source data")
    parser.add_argument("source_path", help="Path to source CSV file")
    parser.add_argument("chart_metadata_path", help="Path to chart metadata JSON file")
    parser.add_argument("output_path", help="Path to output validation report JSON")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()

    result = main(args.source_path, args.chart_metadata_path, args.output_path,
                  input_format=args.input_format)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
