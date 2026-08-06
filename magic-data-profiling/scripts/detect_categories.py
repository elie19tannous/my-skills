#!/usr/bin/env python3
"""
Detect Categories Script
Discover categorical groupings in text columns using first-line extraction,
TF-IDF/KMeans clustering, or cardinality-based enumeration.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import sys
import time
from pathlib import Path
from collections import Counter

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

# ── optional sklearn ──────────────────────────────────────────────────────────
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def _select_target_column(df: pd.DataFrame, column: str | None) -> str | None:
    """Select the best text column: explicit > longest avg text > first object."""
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not text_cols:
        return None
    if column:
        return column if column in df.columns else None
    # Pick column with longest average text length
    avg_lens = {c: df[c].dropna().astype(str).str.len().mean() for c in text_cols}
    return max(avg_lens, key=avg_lens.get)


def method_first_line(series: pd.Series, min_group_size: int) -> dict:
    """Extract first line of each value as the category label."""
    first_lines = (
        series.dropna()
        .astype(str)
        .str.split("\n", n=1)
        .str[0]
        .str.strip()
    )
    counts = Counter(first_lines)
    groups = {k: v for k, v in counts.items() if v >= min_group_size}
    return {
        "method": "first_line",
        "num_groups": len(groups),
        "groups": [{"label": k, "count": v} for k, v in sorted(groups.items(), key=lambda x: -x[1])],
        "coverage": round(sum(groups.values()) / max(len(series.dropna()), 1), 4),
    }


def method_tfidf_kmeans(series: pd.Series, min_group_size: int) -> dict:
    """Cluster values using TF-IDF features + KMeans. Falls back to bigrams if sklearn missing."""
    texts = series.dropna().astype(str).tolist()
    if len(texts) < 4:
        return {"method": "tfidf_kmeans", "error": "Too few values for clustering (<4)", "num_groups": 0, "groups": []}

    if not SKLEARN_AVAILABLE:
        # Fallback: bigram frequency grouping
        bigrams: Counter = Counter()
        for t in texts:
            words = t.lower().split()
            for i in range(len(words) - 1):
                bigrams[(words[i], words[i + 1])] += 1
        top_bigrams = bigrams.most_common(20)
        groups = [{"label": f"{a} {b}", "count": c} for (a, b), c in top_bigrams if c >= min_group_size]
        return {"method": "bigram_fallback", "num_groups": len(groups), "groups": groups, "coverage": None}

    # Determine k: sqrt heuristic, clamp [2, 15]
    k = min(15, max(2, int(len(texts) ** 0.5)))

    vec = TfidfVectorizer(max_features=500, stop_words="english", ngram_range=(1, 2))
    try:
        X = vec.fit_transform(texts)
    except ValueError:
        return {"method": "tfidf_kmeans", "error": "TF-IDF vectorization failed", "num_groups": 0, "groups": []}

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)

    cluster_counts = Counter(labels.tolist())
    # Get top terms per cluster
    feature_names = vec.get_feature_names_out()
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    groups = []
    for cluster_id, count in sorted(cluster_counts.items(), key=lambda x: -x[1]):
        if count < min_group_size:
            continue
        top_terms = [feature_names[i] for i in order_centroids[cluster_id, :3]]
        groups.append({"label": ", ".join(top_terms), "count": int(count)})

    return {
        "method": "tfidf_kmeans",
        "k": k,
        "num_groups": len(groups),
        "groups": groups,
        "coverage": round(sum(g["count"] for g in groups) / max(len(texts), 1), 4),
    }


def method_cardinality(series: pd.Series, min_group_size: int) -> dict:
    """Enumerate distinct values when cardinality is low enough."""
    value_counts = series.dropna().astype(str).value_counts()
    unique_count = len(value_counts)

    # Only enumerate if cardinality is reasonable
    if unique_count > 200:
        return {
            "method": "cardinality",
            "error": f"Too many unique values ({unique_count}) for enumeration — use tfidf_kmeans instead",
            "num_groups": unique_count,
            "groups": [],
        }

    groups = [
        {"label": label, "count": int(count)}
        for label, count in value_counts.items()
        if count >= min_group_size
    ]
    return {
        "method": "cardinality",
        "num_unique": unique_count,
        "num_groups": len(groups),
        "groups": groups,
        "coverage": round(sum(g["count"] for g in groups) / max(len(series.dropna()), 1), 4),
    }


def detect_categories(
    input_path: str,
    output_path: str,
    column: str | None = None,
    method: str = "auto",
    min_group_size: int = 2,
    input_format: str = "auto",
) -> dict:
    t0 = time.time()
    df = load_dataframe(input_path, format=input_format)

    target_col = _select_target_column(df, column)
    if target_col is None:
        result = {
            "success": False,
            "error": "No text columns found in dataset",
            "rows_in": len(df),
        }
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result

    series = df[target_col]
    unique_count = series.nunique()

    # Auto-select method
    if method == "auto":
        if unique_count <= 50:
            method = "cardinality"
        elif SKLEARN_AVAILABLE:
            method = "tfidf_kmeans"
        else:
            method = "first_line"

    if method == "first_line":
        analysis = method_first_line(series, min_group_size)
    elif method == "tfidf_kmeans":
        analysis = method_tfidf_kmeans(series, min_group_size)
    elif method == "cardinality":
        analysis = method_cardinality(series, min_group_size)
    else:
        analysis = {"error": f"Unknown method: {method}"}

    result = {
        "success": True,
        "column": target_col,
        "rows_in": len(df),
        "total_values": int(series.notna().sum()),
        "unique_values": int(unique_count),
        "min_group_size": min_group_size,
        "analysis": analysis,
        "elapsed_seconds": round(time.time() - t0, 3),
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect categorical groupings in text columns"
    )
    parser.add_argument("--input", required=True, help="Input data file path")
    parser.add_argument("--output", default="logs/categories.json", help="Output JSON report path (default: logs/categories.json)")
    parser.add_argument("--column", default=None, help="Column to analyse (default: longest text column)")
    parser.add_argument(
        "--method",
        default="auto",
        choices=["auto", "first_line", "tfidf_kmeans", "cardinality"],
        help="Grouping method (default: auto)",
    )
    parser.add_argument("--min-group-size", type=int, default=2, help="Minimum group size to report (default: 2)")
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
    )
    args = parser.parse_args()

    result = detect_categories(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        method=args.method,
        min_group_size=args.min_group_size,
        input_format=args.input_format,
    )

    if result.get("success"):
        analysis = result.get("analysis", {})
        print(
            f"[detect_categories] column={result['column']} "
            f"method={analysis.get('method', '?')} "
            f"groups={analysis.get('num_groups', 0)} → {args.output}"
        )
    else:
        print(f"[detect_categories] ERROR: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
