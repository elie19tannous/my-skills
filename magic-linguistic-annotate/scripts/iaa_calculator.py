"""Compute IAA metrics from given annotation data.

Phase 1: pure-Python implementations of Cohen κ, Fleiss κ, simple Krippendorff α.
Reads JSON input describing the annotation matrix.

Input formats:
- For Cohen κ: {"annotator_a": [...], "annotator_b": [...]}
- For Fleiss κ: {"matrix": [[count_label_1, ...], ...]}  one row per item, columns are label counts across annotators
- For α: {"annotator_a": [...], "annotator_b": [...], ..., "level": "nominal"|"ordinal"}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import cast


def cohen_kappa(a: list, b: list) -> float:
    if len(a) != len(b):
        raise ValueError("Annotation lists must be same length")
    n = len(a)
    if n == 0:
        return 0.0
    # Observed agreement
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    # Expected (chance) agreement
    labels = set(a) | set(b)
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[lab] / n) * (cb[lab] / n) for lab in labels)
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(matrix: list[list[int]]) -> float:
    """matrix[i][j] = count of annotators who gave item i label j."""
    n_items = len(matrix)
    if n_items == 0:
        return 0.0
    n_raters = sum(matrix[0])
    n_labels = len(matrix[0])

    # Row-wise agreement
    pi_list = []
    for row in matrix:
        if sum(row) != n_raters:
            raise ValueError(f"Each row must sum to n_raters={n_raters}")
        pi = (sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1)) if n_raters > 1 else 0
        pi_list.append(pi)
    p_mean = sum(pi_list) / n_items

    # Label marginals
    p_j = [sum(matrix[i][j] for i in range(n_items)) / (n_items * n_raters) for j in range(n_labels)]
    pe = sum(p * p for p in p_j)
    if pe == 1.0:
        return 1.0 if p_mean == 1.0 else 0.0
    return (p_mean - pe) / (1 - pe)


def pabak(a: list, b: list) -> float:
    """Prevalence-Adjusted Bias-Adjusted κ. For 2 annotators, binary class."""
    if len(a) != len(b):
        raise ValueError("Same length required")
    n = len(a)
    if n == 0:
        return 0.0
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    return 2 * po - 1


def bootstrap_ci(metric_fn, *args, n_iter=1000, seed=42):
    """Simple bootstrap CI of a metric over (annotator_a, annotator_b) pairs."""
    import random

    rng = random.Random(seed)
    n = len(args[0])
    if n == 0:
        return (0.0, 0.0)
    scores = []
    for _ in range(n_iter):
        idx = [rng.randrange(n) for _ in range(n)]
        sampled_args = tuple([arg[i] for i in idx] for arg in args)
        try:
            scores.append(metric_fn(*sampled_args))
        except Exception:
            continue
    if not scores:
        return (0.0, 0.0)
    scores.sort()
    lo = scores[int(0.025 * len(scores))]
    hi = scores[int(0.975 * len(scores))]
    return (lo, hi)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute IAA metrics.")
    parser.add_argument("--metric", required=True, choices=["cohen_kappa", "fleiss_kappa", "pabak"])
    parser.add_argument("--input", default="-", help="JSON input file or '-' for stdin")
    parser.add_argument("--bootstrap-ci", action="store_true", help="Compute 95%% bootstrap CI (Cohen κ / PABAK only)")
    args = parser.parse_args()

    data = json.load(sys.stdin) if args.input == "-" else json.load(open(args.input))

    if args.metric == "cohen_kappa":
        result = cohen_kappa(data["annotator_a"], data["annotator_b"])
        out = {"metric": "Cohen κ", "value": round(result, 4), "n_items": len(data["annotator_a"])}
        if args.bootstrap_ci:
            lo, hi = bootstrap_ci(cohen_kappa, data["annotator_a"], data["annotator_b"])
            out["bootstrap_ci_95"] = [round(lo, 4), round(hi, 4)]
    elif args.metric == "fleiss_kappa":
        result = fleiss_kappa(data["matrix"])
        out = {"metric": "Fleiss κ", "value": round(result, 4), "n_items": len(data["matrix"])}
    else:  # pabak
        result = pabak(data["annotator_a"], data["annotator_b"])
        out = {"metric": "PABAK", "value": round(result, 4), "n_items": len(data["annotator_a"])}
        if args.bootstrap_ci:
            lo, hi = bootstrap_ci(pabak, data["annotator_a"], data["annotator_b"])
            out["bootstrap_ci_95"] = [round(lo, 4), round(hi, 4)]

    out["interpretation"] = _interpret(cast(float, out["value"]))
    print(json.dumps(out, indent=2))
    return 0


def _interpret(v: float) -> str:
    if v < 0:
        return "Worse than chance"
    if v < 0.20:
        return "Slight"
    if v < 0.40:
        return "Fair"
    if v < 0.60:
        return "Moderate"
    if v < 0.80:
        return "Substantial / tentative"
    return "Almost perfect / good"


if __name__ == "__main__":
    sys.exit(main())
