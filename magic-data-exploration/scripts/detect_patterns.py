#!/usr/bin/env python3
"""
Automatic pattern detection in datasets.
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


def detect_temporal_cycle(df, col):
    """Detect periodic patterns in datetime columns."""
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        return None

    # Extract hour/day/month components
    if df[col].dt.hour.nunique() > 1:
        hour_dist = df[col].dt.hour.value_counts()
        if hour_dist.max() / len(df) > 0.3:
            peak_hour = hour_dist.idxmax()
            return {
                "type": "temporal_cycle",
                "description": f"Column '{col}' may show hourly patterns with peak around hour {peak_hour}",
                "evidence": f"{hour_dist.max()} records ({100*hour_dist.max()/len(df):.1f}%) occur at hour {peak_hour}",
                "confidence": "medium",
                "columns": [col]
            }

    if df[col].dt.dayofweek.nunique() > 1:
        dow_dist = df[col].dt.dayofweek.value_counts()
        if dow_dist.max() / len(df) > 0.25:
            peak_day = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dow_dist.idxmax()]
            return {
                "type": "temporal_cycle",
                "description": f"Column '{col}' appears to have weekly patterns with peak on {peak_day}",
                "evidence": f"{dow_dist.max()} records ({100*dow_dist.max()/len(df):.1f}%) occur on {peak_day}",
                "confidence": "medium",
                "columns": [col]
            }

    return None


def detect_categorical_imbalance(df, col):
    """Detect highly skewed categorical distributions."""
    if df[col].nunique() < 2 or df[col].nunique() > 50:
        return None

    dist = df[col].value_counts()
    top_pct = dist.iloc[0] / len(df)

    if top_pct > 0.8:
        return {
            "type": "categorical_imbalance",
            "description": f"Column '{col}' is highly imbalanced, dominated by value '{dist.index[0]}'",
            "evidence": f"{dist.iloc[0]} records ({100*top_pct:.1f}%) have value '{dist.index[0]}'",
            "confidence": "high",
            "columns": [col]
        }

    return None


def detect_numeric_cluster(df, col):
    """Detect bimodal or multimodal distributions."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        return None

    # Skip boolean columns (numpy doesn't support arithmetic on bools)
    if df[col].dtype == bool:
        return None

    data = df[col].dropna()
    if len(data) < 50:
        return None

    # Simple bimodality test using coefficient
    skew = stats.skew(data)
    kurt = stats.kurtosis(data)

    # Bimodal distributions often have negative kurtosis
    if kurt < -1:
        return {
            "type": "numeric_cluster",
            "description": f"Column '{col}' may exhibit multiple clusters or a bimodal distribution",
            "evidence": f"Kurtosis={kurt:.2f} suggests possible clustering",
            "confidence": "low",
            "columns": [col]
        }

    return None


def detect_text_pattern(df, col):
    """Detect common patterns in text."""
    if not pd.api.types.is_string_dtype(df[col]):
        return None

    sample = df[col].dropna().head(100)
    if len(sample) == 0:
        return None

    # URL pattern
    url_count = sample.str.contains(r'https?://', regex=True, na=False).sum()
    if url_count / len(sample) > 0.7:
        return {
            "type": "text_pattern",
            "description": f"Column '{col}' appears to contain URLs",
            "evidence": f"{url_count}/{len(sample)} sampled values match URL pattern",
            "confidence": "high",
            "columns": [col]
        }

    # Email pattern
    email_count = sample.str.contains(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', regex=True, na=False).sum()
    if email_count / len(sample) > 0.7:
        return {
            "type": "text_pattern",
            "description": f"Column '{col}' appears to contain email addresses",
            "evidence": f"{email_count}/{len(sample)} sampled values match email pattern",
            "confidence": "high",
            "columns": [col]
        }

    # Phone pattern
    phone_count = sample.str.contains(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', regex=True, na=False).sum()
    if phone_count / len(sample) > 0.7:
        return {
            "type": "text_pattern",
            "description": f"Column '{col}' may contain phone numbers",
            "evidence": f"{phone_count}/{len(sample)} sampled values match phone pattern",
            "confidence": "medium",
            "columns": [col]
        }

    return None


def detect_correlation(df, col_a, col_b):
    """Detect strong correlations between numeric columns."""
    if not (pd.api.types.is_numeric_dtype(df[col_a]) and pd.api.types.is_numeric_dtype(df[col_b])):
        return None

    # Skip boolean columns (numpy doesn't support arithmetic on bools)
    if df[col_a].dtype == bool or df[col_b].dtype == bool:
        return None

    data = df[[col_a, col_b]].dropna()
    if len(data) < 10:
        return None

    r, p = stats.pearsonr(data[col_a], data[col_b])

    if abs(r) > 0.7 and p < 0.01:
        direction = "positive" if r > 0 else "negative"
        return {
            "type": "correlation",
            "description": f"Columns '{col_a}' and '{col_b}' show a strong {direction} correlation",
            "evidence": f"r={r:.3f}, p={p:.4f}",
            "confidence": "high",
            "columns": [col_a, col_b]
        }

    return None


def detect_outlier_presence(df, col):
    """Detect columns with significant outlier percentage."""
    if not pd.api.types.is_numeric_dtype(df[col]):
        return None

    # Skip boolean columns (numpy doesn't support arithmetic on bools)
    if df[col].dtype == bool:
        return None

    data = df[col].dropna()
    if len(data) < 10:
        return None

    q1 = data.quantile(0.25)
    q3 = data.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = ((data < lower_bound) | (data > upper_bound)).sum()
    outlier_pct = outliers / len(data)

    if outlier_pct > 0.05:
        return {
            "type": "outlier_presence",
            "description": f"Column '{col}' contains a notable proportion of outliers",
            "evidence": f"{outliers} values ({100*outlier_pct:.1f}%) fall outside [Q1-1.5*IQR, Q3+1.5*IQR]",
            "confidence": "high" if outlier_pct > 0.1 else "medium",
            "columns": [col]
        }

    return None


def main(input_path: str, output_path: str, max_findings: int = 5,
         input_format: str = "auto") -> dict:
    """
    Automatic pattern detection in datasets.

    Returns:
        dict: Detection results with findings and metadata
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

        findings = []

        # Detect patterns for each column
        for col in df.columns:
            # Temporal cycles
            finding = detect_temporal_cycle(df, col)
            if finding:
                findings.append(finding)

            # Categorical imbalance
            finding = detect_categorical_imbalance(df, col)
            if finding:
                findings.append(finding)

            # Numeric clusters
            finding = detect_numeric_cluster(df, col)
            if finding:
                findings.append(finding)

            # Text patterns
            finding = detect_text_pattern(df, col)
            if finding:
                findings.append(finding)

            # Outliers
            finding = detect_outlier_presence(df, col)
            if finding:
                findings.append(finding)

        # Detect correlations between numeric column pairs (excluding booleans)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if df[col].dtype != bool]
        for i, col_a in enumerate(numeric_cols):
            for col_b in numeric_cols[i+1:]:
                finding = detect_correlation(df, col_a, col_b)
                if finding:
                    findings.append(finding)

        # Sort by confidence and limit to max_findings
        confidence_order = {"high": 3, "medium": 2, "low": 1}
        findings.sort(key=lambda x: confidence_order.get(x["confidence"], 0), reverse=True)
        findings = findings[:max_findings]

        # Determine column types
        column_types = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                column_types[col] = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                column_types[col] = "datetime"
            elif pd.api.types.is_string_dtype(df[col]):
                column_types[col] = "text"
            else:
                column_types[col] = "categorical"

        # Save findings to output
        output_df = pd.DataFrame(findings)
        output_df.to_csv(output_path, index=False)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(output_df),
            "findings": findings,
            "column_types": column_types
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
            "suggestion": "Check input data format and column types"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect patterns in datasets")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--max-findings", type=int, default=5, help="Maximum number of findings to report")
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

    result = main(args.input_path, args.output_path, args.max_findings,
                  input_format=args.input_format)

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
        ckpt_path = maybe_checkpoint(output_path, "patterns", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
