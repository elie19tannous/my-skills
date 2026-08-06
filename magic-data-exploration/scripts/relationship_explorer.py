#!/usr/bin/env python3
"""
Pairwise relationship exploration with visualization.
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


def analyze_numeric_numeric(df, col_a, col_b, chart_path):
    """Analyze relationship between two numeric columns."""
    data = df[[col_a, col_b]].dropna()

    if len(data) < 10:
        return None

    r, p = stats.pearsonr(data[col_a], data[col_b])

    # Create scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(data[col_a], data[col_b], alpha=0.5)
    plt.xlabel(col_a)
    plt.ylabel(col_b)
    plt.title(f"{col_a} vs {col_b}\n(r={r:.3f}, p={p:.4f})")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Determine strength
    if abs(r) > 0.7:
        strength = "strong"
    elif abs(r) > 0.4:
        strength = "moderate"
    else:
        strength = "weak"

    direction = "positive" if r > 0 else "negative"

    if p < 0.01:
        interpretation = f"A {strength} {direction} correlation appears present between '{col_a}' and '{col_b}' (r={r:.3f}, p < 0.01)"
    elif p < 0.05:
        interpretation = f"A {strength} {direction} correlation may exist between '{col_a}' and '{col_b}' (r={r:.3f}, p < 0.05)"
    else:
        interpretation = f"Little evidence of correlation between '{col_a}' and '{col_b}' (r={r:.3f}, p={p:.3f})"

    return {
        "col_a": col_a,
        "col_b": col_b,
        "type": "numeric_numeric",
        "strength": strength,
        "chart_path": chart_path,
        "interpretation": interpretation,
        "score": abs(r)  # For ranking
    }


def analyze_numeric_categorical(df, numeric_col, cat_col, chart_path):
    """Analyze relationship between numeric and categorical columns."""
    # Limit to reasonable number of categories
    if df[cat_col].nunique() > 10:
        return None

    data = df[[numeric_col, cat_col]].dropna()

    if len(data) < 10:
        return None

    # Create box plot
    plt.figure(figsize=(10, 6))
    data.boxplot(column=numeric_col, by=cat_col)
    plt.suptitle("")
    plt.title(f"{numeric_col} by {cat_col}")
    plt.xlabel(cat_col)
    plt.ylabel(numeric_col)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()

    # Statistical test
    groups = [group_df[numeric_col].dropna() for _, group_df in data.groupby(cat_col)]
    groups = [g for g in groups if len(g) > 0]

    if len(groups) < 2:
        return None

    if len(groups) == 2:
        stat, p = stats.mannwhitneyu(groups[0], groups[1], alternative='two-sided')
        test = "Mann-Whitney U"
    else:
        stat, p = stats.kruskal(*groups)
        test = "Kruskal-Wallis"

    if p < 0.01:
        strength = "strong"
        interpretation = f"'{numeric_col}' appears to differ significantly across '{cat_col}' categories ({test}, p < 0.01)"
    elif p < 0.05:
        strength = "moderate"
        interpretation = f"'{numeric_col}' may differ across '{cat_col}' categories ({test}, p < 0.05)"
    else:
        strength = "weak"
        interpretation = f"No strong evidence that '{numeric_col}' differs across '{cat_col}' categories ({test}, p={p:.3f})"

    return {
        "col_a": numeric_col,
        "col_b": cat_col,
        "type": "numeric_categorical",
        "strength": strength,
        "chart_path": chart_path,
        "interpretation": interpretation,
        "score": 1 - p  # For ranking
    }


def analyze_categorical_categorical(df, col_a, col_b, chart_path):
    """Analyze relationship between two categorical columns."""
    # Limit to reasonable number of categories
    if df[col_a].nunique() > 10 or df[col_b].nunique() > 10:
        return None

    data = df[[col_a, col_b]].dropna()

    if len(data) < 10:
        return None

    # Create cross-tabulation
    ct = pd.crosstab(data[col_a], data[col_b])

    # Chi-square test
    chi2, p, dof, expected = stats.chi2_contingency(ct)

    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(ct, annot=True, fmt='d', cmap='Blues')
    plt.title(f"{col_a} vs {col_b}\n(χ²={chi2:.2f}, p={p:.4f})")
    plt.xlabel(col_b)
    plt.ylabel(col_a)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()

    if p < 0.01:
        strength = "strong"
        interpretation = f"'{col_a}' and '{col_b}' appear to be associated (χ²={chi2:.2f}, p < 0.01)"
    elif p < 0.05:
        strength = "moderate"
        interpretation = f"'{col_a}' and '{col_b}' may be associated (χ²={chi2:.2f}, p < 0.05)"
    else:
        strength = "weak"
        interpretation = f"No strong evidence of association between '{col_a}' and '{col_b}' (χ²={chi2:.2f}, p={p:.3f})"

    return {
        "col_a": col_a,
        "col_b": col_b,
        "type": "categorical_categorical",
        "strength": strength,
        "chart_path": chart_path,
        "interpretation": interpretation,
        "score": 1 - p  # For ranking
    }


def main(input_path: str, output_path: str,
         max_pairs: int = 10, columns: str = None,
         input_format: str = "auto") -> dict:
    """
    Pairwise relationship exploration.

    Args:
        input_path: Path to input CSV
        output_path: Path to output CSV
        max_pairs: Maximum number of pairs to analyze
        columns: Comma-separated columns to analyze (None = all)

    Returns:
        dict: Relationship analysis results
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

        # Determine columns to analyze
        if columns is None:
            cols = df.columns.tolist()
        else:
            cols = [c.strip() for c in columns.split(",")]
            cols = [c for c in cols if c in df.columns]

        # Create chart directory
        chart_dir = Path(output_path).parent / f"{Path(output_path).stem}_charts"
        chart_dir.mkdir(exist_ok=True, parents=True)

        relationships = []

        # Analyze all pairs
        for i, col_a in enumerate(cols):
            for col_b in cols[i+1:]:
                # Determine column types
                col_a_numeric = pd.api.types.is_numeric_dtype(df[col_a])
                col_b_numeric = pd.api.types.is_numeric_dtype(df[col_b])

                chart_path = str(chart_dir / f"{col_a}_vs_{col_b}.png")

                if col_a_numeric and col_b_numeric:
                    result = analyze_numeric_numeric(df, col_a, col_b, chart_path)
                elif col_a_numeric and not col_b_numeric:
                    result = analyze_numeric_categorical(df, col_a, col_b, chart_path)
                elif not col_a_numeric and col_b_numeric:
                    result = analyze_numeric_categorical(df, col_b, col_a, chart_path)
                else:
                    result = analyze_categorical_categorical(df, col_a, col_b, chart_path)

                if result:
                    relationships.append(result)

        # Sort by score (most interesting first) and limit
        relationships.sort(key=lambda x: x.get("score", 0), reverse=True)
        relationships = relationships[:max_pairs]

        # Remove score from output
        for rel in relationships:
            rel.pop("score", None)

        # Create output dataframe
        output_df = pd.DataFrame(relationships)
        output_df.to_csv(output_path, index=False)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": len(df),
            "rows_out": len(output_df),
            "pairs_analyzed": len(relationships),
            "relationships": relationships,
            "chart_dir": str(chart_dir)
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
    parser = argparse.ArgumentParser(description="Explore pairwise relationships")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument("--max-pairs", type=int, default=10, help="Maximum pairs to analyze")
    parser.add_argument("--columns", help="Comma-separated columns to analyze")
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

    result = main(args.input_path, args.output_path, args.max_pairs, args.columns,
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
        ckpt_path = maybe_checkpoint(output_path, "relationships", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
