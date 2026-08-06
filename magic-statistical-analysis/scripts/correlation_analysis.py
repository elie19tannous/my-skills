#!/usr/bin/env python3
"""
Pairwise correlation analysis with automatic method selection.

Computes correlations between numeric columns, tests significance,
generates heatmaps, and identifies multicollinearity issues.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def check_normality(series: pd.Series, max_samples: int = 5000) -> bool:
    """Check if a series is approximately normally distributed."""
    clean = series.dropna()

    if len(clean) < 3:
        return False

    # Sample if too large
    if len(clean) > max_samples:
        sample = np.random.choice(clean, size=max_samples, replace=False)
    else:
        sample = clean.values

    _, p_value = stats.shapiro(sample)
    return p_value > 0.05


def interpret_strength(r: float) -> str:
    """Interpret correlation strength."""
    abs_r = abs(r)

    if abs_r < 0.1:
        return "negligible"
    elif abs_r < 0.3:
        return "weak"
    elif abs_r < 0.7:
        return "moderate"
    elif abs_r < 0.9:
        return "strong"
    else:
        return "very_strong"


def compute_pearson(col_a: pd.Series, col_b: pd.Series) -> tuple[float, float]:
    """Compute Pearson correlation and p-value."""
    # Remove pairs with any missing values
    mask = col_a.notna() & col_b.notna()
    a_clean = col_a[mask]
    b_clean = col_b[mask]

    if len(a_clean) < 3:
        return 0.0, 1.0

    r, p_value = stats.pearsonr(a_clean, b_clean)
    return float(r), float(p_value)


def compute_spearman(col_a: pd.Series, col_b: pd.Series) -> tuple[float, float]:
    """Compute Spearman correlation and p-value."""
    # Remove pairs with any missing values
    mask = col_a.notna() & col_b.notna()
    a_clean = col_a[mask]
    b_clean = col_b[mask]

    if len(a_clean) < 3:
        return 0.0, 1.0

    r, p_value = stats.spearmanr(a_clean, b_clean)
    return float(r), float(p_value)


def create_heatmap(corr_matrix: pd.DataFrame, output_path: str) -> str:
    """Create correlation heatmap with colorblind-safe palette."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Use colorblind-safe diverging palette
    cmap = sns.diverging_palette(250, 10, as_cmap=True)

    # Create heatmap
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap=cmap,
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Correlation Coefficient'},
        ax=ax
    )

    ax.set_title('Correlation Matrix', fontsize=14, pad=20)

    # Save
    heatmap_path = str(Path(output_path).parent / 'correlation_heatmap.png')
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    plt.close()

    return heatmap_path


def main(input_path: str, output_path: str,
         method: str = "auto", columns: Optional[str] = None,
         min_significance: float = 0.05,
         input_format: str = "auto") -> Dict[str, Any]:
    """
    Pairwise correlation analysis with automatic method selection.

    Args:
        input_path: Path to input CSV/Parquet
        output_path: Path to save results JSON
        method: "auto", "pearson", or "spearman"
        columns: Comma-separated column names (default: all numeric)
        min_significance: Minimum p-value for significance (default: 0.05)

    Returns:
        Result dictionary with correlations and diagnostics
    """
    try:
        # Read input
        input_file = Path(input_path)
        if not input_file.exists():
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path is correct"
            }

        # Load data
        df = load_dataframe(input_path, format=input_format)

        rows_in = len(df)

        # Quality gate
        if rows_in == 0:
            return {
                "success": False,
                "error": "Input dataset is empty",
                "suggestion": "Provide a dataset with at least one row"
            }

        # Select numeric columns
        if columns:
            col_list = [c.strip() for c in columns.split(',')]
            missing = set(col_list) - set(df.columns)
            if missing:
                return {
                    "success": False,
                    "error": f"Columns not found: {missing}",
                    "suggestion": f"Available columns: {list(df.columns)}"
                }
            df_numeric = df[col_list].select_dtypes(include=[np.number])
        else:
            df_numeric = df.select_dtypes(include=[np.number])

        if df_numeric.shape[1] < 2:
            return {
                "success": False,
                "error": "Need at least 2 numeric columns for correlation analysis",
                "suggestion": f"Found numeric columns: {list(df_numeric.columns)}"
            }

        # Determine method
        if method == "auto":
            # Check normality for all columns
            all_normal = all(check_normality(df_numeric[col]) for col in df_numeric.columns)

            if all_normal:
                selected_method = "pearson"
                method_reason = "All numeric columns appear approximately normally distributed"
            else:
                selected_method = "spearman"
                method_reason = "One or more columns deviate from normality; using rank-based correlation"
        else:
            selected_method = method
            method_reason = f"Method manually specified as {method}"

        # Compute correlations
        correlations = []
        corr_matrix = pd.DataFrame(
            np.eye(len(df_numeric.columns)),
            index=df_numeric.columns,
            columns=df_numeric.columns
        )

        for i, col_a in enumerate(df_numeric.columns):
            for j, col_b in enumerate(df_numeric.columns):
                if i >= j:
                    continue  # Skip diagonal and lower triangle

                if selected_method == "pearson":
                    r, p_value = compute_pearson(df_numeric[col_a], df_numeric[col_b])
                else:  # spearman
                    r, p_value = compute_spearman(df_numeric[col_a], df_numeric[col_b])

                # Update matrix
                corr_matrix.loc[col_a, col_b] = r
                corr_matrix.loc[col_b, col_a] = r

                # Add to list
                correlations.append({
                    "col_a": col_a,
                    "col_b": col_b,
                    "r": float(r),
                    "p_value": float(p_value),
                    "significant": p_value < min_significance,
                    "strength": interpret_strength(r)
                })

        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x['r']), reverse=True)

        # Top correlations (top 10 by absolute value)
        top_correlations = [
            {
                "col_a": c["col_a"],
                "col_b": c["col_b"],
                "r": c["r"],
                "p_value": c["p_value"],
                "strength": c["strength"]
            }
            for c in correlations[:10]
        ]

        # Multicollinearity warnings (|r| > 0.9)
        multicollinearity_warnings = [
            {
                "col_a": c["col_a"],
                "col_b": c["col_b"],
                "r": c["r"],
                "warning": f"Very strong correlation ({c['r']:.3f}) may indicate multicollinearity"
            }
            for c in correlations if abs(c["r"]) > 0.9
        ]

        # Create heatmap
        heatmap_path = create_heatmap(corr_matrix, output_path)

        # Build result
        result = {
            "success": True,
            "output_path": str(output_path),
            "rows_in": rows_in,
            "rows_out": rows_in,  # No filtering
            "method_used": selected_method,
            "method_reason": method_reason,
            "correlations": correlations,
            "top_correlations": top_correlations,
            "multicollinearity_warnings": multicollinearity_warnings,
            "heatmap_path": heatmap_path,
            "caveats": [
                "Correlation does not imply causation",
                f"Statistical significance (p<{min_significance}) does not guarantee practical importance",
                "Outliers may strongly influence correlation coefficients",
                f"Sample size: {rows_in} observations",
                "Pearson correlation assumes linear relationships; Spearman is more robust to non-linearity",
                "Missing values are excluded pairwise, which may affect comparability across pairs"
            ]
        }

        # Save output
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and column specifications"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pairwise correlation analysis")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet path")
    parser.add_argument("--output", default="logs/correlation.json", help="Output JSON path (default: logs/correlation.json)")
    parser.add_argument("--method", default="auto",
                        choices=["auto", "pearson", "spearman"],
                        help="Correlation method (default: auto)")
    parser.add_argument("--columns", help="Comma-separated column names (default: all numeric)")
    parser.add_argument("--min_significance", type=float, default=0.05,
                        help="Minimum p-value for significance (default: 0.05)")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(
        input_path=args.input,
        output_path=args.output,
        method=args.method,
        columns=args.columns,
        min_significance=args.min_significance,
        input_format=args.input_format
    )

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output)
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
        ckpt_path = maybe_checkpoint(output_path, "correlation", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["success"] else 1)
