#!/usr/bin/env python3
"""
Compute descriptive statistics with narrative interpretation.

Analyzes numeric, text, and categorical columns with appropriate statistics
and generates human-readable narratives with uncertainty language.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import glob
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)

def maybe_checkpoint(df, path, metadata=None):
    """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)


def detect_column_type(series: pd.Series) -> str:
    """Detect if column is numeric, text, or categorical."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        # Check if text (avg length > 50 chars) or categorical
        non_null = series.dropna()
        if len(non_null) == 0:
            return "categorical"

        avg_length = non_null.astype(str).str.len().mean()
        try:
            unique_ratio = len(non_null.unique()) / len(non_null)
        except TypeError:
            # Non-hashable values (dict/list) — treat as text
            return "text"

        # Text if long strings or high unique ratio
        if avg_length > 50 or unique_ratio > 0.5:
            return "text"
        else:
            return "categorical"

    return "categorical"


def compute_numeric_stats(series: pd.Series, col_name: str) -> Dict[str, Any]:
    """Compute statistics for numeric columns."""
    # Skip boolean columns (numpy doesn't support arithmetic on bools)
    if series.dtype == bool:
        return {
            "count": 0,
            "narrative": f"Column '{col_name}' is a boolean column and cannot be analyzed numerically."
        }

    clean = series.dropna()

    if len(clean) == 0:
        return {
            "count": 0,
            "narrative": f"Column '{col_name}' contains no valid numeric values."
        }

    stats = {
        "count": int(len(clean)),
        "mean": float(clean.mean()),
        "std": float(clean.std()),
        "min": float(clean.min()),
        "p25": float(clean.quantile(0.25)),
        "median": float(clean.quantile(0.50)),
        "p75": float(clean.quantile(0.75)),
        "max": float(clean.max()),
        "skewness": float(clean.skew()),
        "kurtosis": float(clean.kurtosis()),
    }

    # Coefficient of variation (only if mean != 0)
    if stats["mean"] != 0:
        stats["cv"] = float(stats["std"] / abs(stats["mean"]))
    else:
        stats["cv"] = None

    # Generate narrative
    narrative_parts = []

    # Distribution shape
    if abs(stats["skewness"]) < 0.5:
        skew_desc = "appears approximately symmetric"
    elif stats["skewness"] > 0:
        skew_desc = "appears right-skewed"
    else:
        skew_desc = "appears left-skewed"

    narrative_parts.append(
        f"'{col_name}' {skew_desc} with a median of {stats['median']:.2f}"
    )

    # Compare mean and median
    if abs(stats["mean"] - stats["median"]) / stats["std"] > 0.5 if stats["std"] > 0 else False:
        if stats["mean"] > stats["median"]:
            narrative_parts.append(
                f"suggesting values may cluster below the mean of {stats['mean']:.2f}"
            )
        else:
            narrative_parts.append(
                f"suggesting values may cluster above the mean of {stats['mean']:.2f}"
            )

    # Variability
    if stats["cv"] is not None:
        if stats["cv"] < 0.15:
            var_desc = "low variability"
        elif stats["cv"] < 0.30:
            var_desc = "moderate variability"
        else:
            var_desc = "high variability"

        narrative_parts.append(
            f"The data shows {var_desc} (CV={stats['cv']:.2f})"
        )

    # Range
    range_val = stats["max"] - stats["min"]
    narrative_parts.append(
        f"with values ranging from {stats['min']:.2f} to {stats['max']:.2f}"
    )

    stats["narrative"] = ". ".join(narrative_parts) + "."

    return stats


def compute_text_stats(series: pd.Series, col_name: str) -> Dict[str, Any]:
    """Compute statistics for text columns."""
    clean = series.dropna().astype(str)

    if len(clean) == 0:
        return {
            "count": 0,
            "narrative": f"Column '{col_name}' contains no valid text values."
        }

    # Word counts
    word_counts = clean.str.split().str.len()
    char_lengths = clean.str.len()

    # Vocabulary analysis
    all_words = ' '.join(clean.values).lower().split()
    unique_words = set(all_words)

    # Top terms (simple frequency count)
    from collections import Counter
    word_freq = Counter(all_words)
    top_10 = [{"term": word, "count": count} for word, count in word_freq.most_common(10)]

    stats = {
        "count": int(len(clean)),
        "unique": int(clean.nunique()),
        "vocabulary_size": len(unique_words),
        "avg_word_count": float(word_counts.mean()),
        "avg_char_length": float(char_lengths.mean()),
        "top_10_terms": top_10
    }

    # Generate narrative
    narrative_parts = []

    narrative_parts.append(
        f"'{col_name}' contains {stats['count']} text entries with an average length "
        f"of {stats['avg_word_count']:.1f} words"
    )

    # Vocabulary richness
    vocab_ratio = stats['vocabulary_size'] / len(all_words) if len(all_words) > 0 else 0
    if vocab_ratio > 0.5:
        narrative_parts.append(
            f"The text appears to have high vocabulary diversity ({stats['vocabulary_size']} unique terms)"
        )
    elif vocab_ratio > 0.2:
        narrative_parts.append(
            f"The text shows moderate vocabulary diversity ({stats['vocabulary_size']} unique terms)"
        )
    else:
        narrative_parts.append(
            f"The text may contain repetitive language ({stats['vocabulary_size']} unique terms)"
        )

    # Uniqueness
    unique_ratio = stats['unique'] / stats['count']
    if unique_ratio > 0.9:
        narrative_parts.append(
            f"Most entries appear unique ({stats['unique']} distinct values)"
        )
    elif unique_ratio < 0.5:
        narrative_parts.append(
            f"Many entries may be duplicated ({stats['unique']} distinct values out of {stats['count']})"
        )

    stats["narrative"] = ". ".join(narrative_parts) + "."

    return stats


def compute_categorical_stats(series: pd.Series, col_name: str) -> Dict[str, Any]:
    """Compute statistics for categorical columns."""
    clean = series.dropna()

    if len(clean) == 0:
        return {
            "count": 0,
            "narrative": f"Column '{col_name}' contains no valid categorical values."
        }

    try:
        value_counts = clean.value_counts()
    except TypeError:
        # Non-hashable values (dict/list) — convert to string first
        clean = clean.astype(str)
        value_counts = clean.value_counts()

    stats = {
        "count": int(len(clean)),
        "unique": int(len(value_counts)),
        "mode": str(value_counts.index[0]) if len(value_counts) > 0 else None,
        "mode_freq": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
        "value_counts": {str(k): int(v) for k, v in value_counts.head(20).items()}
    }

    # Generate narrative
    narrative_parts = []

    narrative_parts.append(
        f"'{col_name}' contains {stats['unique']} distinct categories across {stats['count']} observations"
    )

    if stats['mode'] is not None:
        mode_pct = (stats['mode_freq'] / stats['count']) * 100
        narrative_parts.append(
            f"The most common value is '{stats['mode']}' appearing in {mode_pct:.1f}% of cases"
        )

    # Distribution balance
    if len(value_counts) > 1:
        top_pct = (value_counts.iloc[0] / stats['count']) * 100
        if top_pct > 80:
            narrative_parts.append(
                "suggesting a highly imbalanced distribution"
            )
        elif top_pct > 50:
            narrative_parts.append(
                "suggesting a moderately imbalanced distribution"
            )
        else:
            narrative_parts.append(
                "suggesting a relatively balanced distribution"
            )

    stats["narrative"] = ". ".join(narrative_parts) + "."

    return stats


def main(input_path: str, output_path: str, columns: Optional[str] = None,
         input_format: str = "auto") -> Dict[str, Any]:
    """
    Compute descriptive statistics with narrative interpretation.

    Args:
        input_path: Path to input CSV/Parquet
        output_path: Path to save statistics JSON
        columns: Comma-separated column names (default: all)

    Returns:
        Result dictionary with statistics and narratives
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

        # Select columns
        if columns:
            col_list = [c.strip() for c in columns.split(',')]
            missing = set(col_list) - set(df.columns)
            if missing:
                return {
                    "success": False,
                    "error": f"Columns not found: {missing}",
                    "suggestion": f"Available columns: {list(df.columns)}"
                }
            df = df[col_list]

        # Analyze by type
        statistics = {
            "numeric": {},
            "text": {},
            "categorical": {}
        }

        for col in df.columns:
            col_type = detect_column_type(df[col])

            if col_type == "numeric":
                statistics["numeric"][col] = compute_numeric_stats(df[col], col)
            elif col_type == "text":
                statistics["text"][col] = compute_text_stats(df[col], col)
            else:
                statistics["categorical"][col] = compute_categorical_stats(df[col], col)

        # Build result
        result = {
            "success": True,
            "output_path": str(output_path),
            "rows_in": rows_in,
            "rows_out": rows_in,  # No filtering
            "statistics": statistics,
            "caveats": [
                "Descriptive statistics summarize observed patterns but do not imply causation",
                "Outliers may influence mean and standard deviation",
                "Text analysis uses simple frequency counting and may not capture semantic meaning",
                "Categorical analysis is limited to frequency distributions"
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
    parser = argparse.ArgumentParser(description="Compute descriptive statistics with narratives")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet path")
    parser.add_argument("--output", default="logs/descriptive_stats.json", help="Output JSON path (default: logs/descriptive_stats.json)")
    parser.add_argument("--columns", help="Comma-separated column names (default: all)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        # Validate input file exists
        input_file = Path(args.input)
        if not input_file.exists():
            print(json.dumps({
                "success": False,
                "error": f"Input file not found: {args.input}"
            }, indent=2))
            sys.exit(1)

        steps = [
            f"Read data from {args.input}",
            f"Select columns: {args.columns or '(all columns)'}",
            "Detect column types (numeric, text, categorical)",
            "Compute numeric stats: mean, std, min, p25, median, p75, max, skewness, kurtosis, CV",
            "Compute text stats: word counts, vocabulary size, top terms",
            "Compute categorical stats: unique counts, mode, value distribution",
            "Generate narrative interpretations",
            f"Write statistics JSON to {args.output}"
        ]
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "descriptive_stats",
                "input": args.input,
                "output": args.output,
                "steps": steps,
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(
        input_path=args.input,
        output_path=args.output,
        columns=args.columns,
        input_format=args.input_format
    )

    if result.get("success") and args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "format": getattr(args, "output_format", "json"),
            "input_path": getattr(args, "input_path", getattr(args, "input", "")),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(args.output, "stats", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["success"] else 1)
