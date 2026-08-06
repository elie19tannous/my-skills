#!/usr/bin/env python3
"""
Correlation Matrix Script
Compute pairwise correlations with significance testing and visualizations.
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
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


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


# Colorblind-safe palette
COLORBLIND_SAFE_COLORS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442']


def test_normality(series: pd.Series, sample_size: int = 5000) -> bool:
    """Test if a series follows a normal distribution."""
    clean_data = series.dropna()

    if len(clean_data) < 3:
        return False

    # Use Shapiro-Wilk test (cap at 5000 samples)
    sample_data = clean_data.sample(n=min(len(clean_data), sample_size), random_state=42)

    try:
        _, p_value = stats.shapiro(sample_data)
        return p_value > 0.05
    except Exception:
        return False


def compute_correlation_matrix(df: pd.DataFrame, method: str = "auto") -> tuple:
    """
    Compute correlation matrix with appropriate method.

    Returns:
        tuple: (correlation_matrix, method_used)
    """
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])

    if len(numeric_df.columns) == 0:
        raise ValueError("No numeric columns found in dataset")

    # Determine method
    if method == "auto":
        # Check if any column is non-normal
        is_any_non_normal = False
        for col in numeric_df.columns:
            if not test_normality(numeric_df[col]):
                is_any_non_normal = True
                break

        method_used = "spearman" if is_any_non_normal else "pearson"
    else:
        method_used = method

    # Compute correlation matrix
    if method_used == "pearson":
        corr_matrix = numeric_df.corr(method='pearson')
    else:
        corr_matrix = numeric_df.corr(method='spearman')

    return corr_matrix, method_used


def compute_pairwise_significance(df: pd.DataFrame, method: str, min_significance: float) -> list:
    """Compute p-values for pairwise correlations."""
    numeric_df = df.select_dtypes(include=[np.number])
    columns = numeric_df.columns.tolist()

    significant_pairs = []

    for i, col_a in enumerate(columns):
        for col_b in columns[i+1:]:
            # Get clean data
            data_a = numeric_df[col_a].dropna()
            data_b = numeric_df[col_b].dropna()

            # Align indices
            common_idx = data_a.index.intersection(data_b.index)
            data_a = data_a.loc[common_idx]
            data_b = data_b.loc[common_idx]

            if len(data_a) < 3:
                continue

            # Compute correlation and p-value
            try:
                if method == "pearson":
                    r, p = stats.pearsonr(data_a, data_b)
                else:
                    r, p = stats.spearmanr(data_a, data_b)

                significant_pairs.append({
                    "col_a": col_a,
                    "col_b": col_b,
                    "r": float(r),
                    "p": float(p),
                    "significant": p < min_significance
                })
            except Exception:
                continue

    return significant_pairs


def generate_heatmap(corr_matrix: pd.DataFrame, output_path: str, method: str):
    """Generate correlation heatmap with colorblind-safe palette."""
    plt.figure(figsize=(12, 10))

    # Use diverging colormap (colorblind-safe)
    cmap = sns.diverging_palette(220, 20, as_cmap=True)

    # Create heatmap
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap=cmap,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8}
    )

    plt.title(f'Correlation Heatmap ({method.capitalize()})', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Save figure
    heatmap_path = output_path.replace('.json', '_heatmap.png')
    plt.savefig(heatmap_path, dpi=150, bbox_inches='tight')
    plt.close()

    return heatmap_path


def detect_multicollinearity(corr_matrix: pd.DataFrame, threshold: float = 0.9) -> list:
    """Detect highly correlated variable pairs (multicollinearity warnings)."""
    warnings = []

    columns = corr_matrix.columns.tolist()
    for i, col_a in enumerate(columns):
        for col_b in columns[i+1:]:
            r = corr_matrix.loc[col_a, col_b]
            if abs(r) > threshold:
                warnings.append(
                    f"High correlation between '{col_a}' and '{col_b}': r={r:.3f} "
                    f"(consider removing one to avoid multicollinearity)"
                )

    return warnings


def main(input_path: str, output_path: str,
         method: str = "auto", min_significance: float = 0.05,
         input_format: str = "auto") -> dict:
    """
    Compute pairwise correlations with significance testing.

    Args:
        input_path: Path to input file
        output_path: Path to output JSON file
        method: Correlation method ("auto", "pearson", "spearman")
        min_significance: Significance threshold for p-values (default: 0.05)
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel)

    Returns:
        dict: Correlation analysis results
    """
    try:
        # Validate method
        if method not in ["auto", "pearson", "spearman"]:
            return {
                "success": False,
                "error": f"Invalid method: {method}",
                "suggestion": "Use 'auto', 'pearson', or 'spearman'"
            }

        # Read input data
        df = load_dataframe(input_path, format=input_format)

        # Quality gate: check for empty input
        if len(df) == 0:
            return {
                "success": False,
                "error": "Input dataset is empty",
                "suggestion": "Provide a dataset with at least one row"
            }

        # Check for numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) == 0:
            return {
                "success": False,
                "error": "No numeric columns found in dataset",
                "suggestion": "Correlation analysis requires at least two numeric columns"
            }

        if len(numeric_df.columns) < 2:
            return {
                "success": False,
                "error": "Need at least 2 numeric columns for correlation analysis",
                "suggestion": f"Found only {len(numeric_df.columns)} numeric column(s)"
            }

        # Compute correlation matrix
        corr_matrix, method_used = compute_correlation_matrix(df, method)

        # Save correlation matrix as CSV with row labels (index must be preserved)
        matrix_csv_path = output_path.replace('.json', '_matrix.csv')
        Path(matrix_csv_path).parent.mkdir(parents=True, exist_ok=True)
        corr_matrix.to_csv(matrix_csv_path)

        # Generate heatmap
        heatmap_path = generate_heatmap(corr_matrix, output_path, method_used)

        # Compute pairwise significance
        significant_pairs = compute_pairwise_significance(df, method_used, min_significance)

        # Sort by absolute correlation (descending)
        significant_pairs.sort(key=lambda x: abs(x['r']), reverse=True)

        # Detect multicollinearity
        multicollinearity_warnings = detect_multicollinearity(corr_matrix)

        # Prepare output
        output_data = {
            "success": True,
            "output_path": output_path,
            "matrix_csv_path": matrix_csv_path,
            "heatmap_path": heatmap_path,
            "method_used": method_used,
            "significant_pairs": significant_pairs,
            "multicollinearity_warnings": multicollinearity_warnings
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
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Ensure dataset has at least 2 numeric columns"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input data format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute correlation matrix with significance testing")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument("--method", default="auto", choices=["auto", "pearson", "spearman"],
                        help="Correlation method (default: auto)")
    parser.add_argument("--min_significance", type=float, default=0.05,
                        help="Significance threshold (default: 0.05)")
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

    result = main(args.input_path, args.output_path, args.method, args.min_significance,
                  args.input_format)

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            def maybe_checkpoint(df_or_path, tag, save=True, checkpoint_format=None, metadata=None):
                """Stub: save checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
                from pathlib import Path
                p = Path(str(df_or_path) + ".ckpt.json") if isinstance(df_or_path, str) else Path(str(df_or_path))
                return str(p)
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(output_path, "correlation", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("success") else 1)
