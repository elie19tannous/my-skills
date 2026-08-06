#!/usr/bin/env python3
"""
Automatic hypothesis test selection and execution.

Selects appropriate statistical test based on data characteristics,
computes effect sizes, confidence intervals, and provides interpretations.
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
from typing import Any, Dict, Optional

import pandas as pd
import numpy as np
from scipy import stats

# Fuzzy column suggestion support + io_utils
try:
    from error_utils import suggest_column, format_column_error
except ImportError:
    suggest_column = None
    format_column_error = None
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


def check_normality(data: np.ndarray, max_samples: int = 5000) -> tuple[float, bool]:
    """
    Check normality using Shapiro-Wilk test.

    Args:
        data: Array of values
        max_samples: Maximum samples for test (Shapiro-Wilk limitation)

    Returns:
        (p_value, is_normal)
    """
    if len(data) < 3:
        return 0.0, False

    # Sample if too large
    if len(data) > max_samples:
        sample = np.random.choice(data, size=max_samples, replace=False)
    else:
        sample = data

    statistic, p_value = stats.shapiro(sample)
    return float(p_value), p_value > 0.05


def check_equal_variance(groups: list[np.ndarray]) -> tuple[float, bool]:
    """Check equal variance using Levene's test."""
    if len(groups) < 2:
        return 0.0, True

    statistic, p_value = stats.levene(*groups)
    return float(p_value), p_value > 0.05


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> tuple[float, str]:
    """
    Compute Cohen's d effect size for two groups.

    Returns:
        (effect_size, interpretation)
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0, "negligible"

    d = (np.mean(group1) - np.mean(group2)) / pooled_std

    # Interpretation
    abs_d = abs(d)
    if abs_d < 0.2:
        interpretation = "negligible"
    elif abs_d < 0.5:
        interpretation = "small"
    elif abs_d < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return float(d), interpretation


def eta_squared(groups: list[np.ndarray]) -> tuple[float, str]:
    """
    Compute eta-squared effect size for ANOVA.

    Returns:
        (effect_size, interpretation)
    """
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)

    # Between-group sum of squares
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)

    # Total sum of squares
    ss_total = np.sum((all_data - grand_mean) ** 2)

    if ss_total == 0:
        return 0.0, "negligible"

    eta_sq = ss_between / ss_total

    # Interpretation
    if eta_sq < 0.01:
        interpretation = "negligible"
    elif eta_sq < 0.06:
        interpretation = "small"
    elif eta_sq < 0.14:
        interpretation = "medium"
    else:
        interpretation = "large"

    return float(eta_sq), interpretation


def rank_biserial(group1: np.ndarray, group2: np.ndarray, u_statistic: float) -> tuple[float, str]:
    """
    Compute rank-biserial correlation for Mann-Whitney U test.

    Returns:
        (effect_size, interpretation)
    """
    n1, n2 = len(group1), len(group2)

    # Rank-biserial correlation
    r = 1 - (2 * u_statistic) / (n1 * n2)

    # Interpretation (similar to Cohen's d thresholds)
    abs_r = abs(r)
    if abs_r < 0.2:
        interpretation = "negligible"
    elif abs_r < 0.5:
        interpretation = "small"
    elif abs_r < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return float(r), interpretation


def cramers_v(contingency_table: np.ndarray) -> tuple[float, str]:
    """
    Compute Cramér's V effect size for chi-square test.

    Returns:
        (effect_size, interpretation)
    """
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1

    if n == 0 or min_dim == 0:
        return 0.0, "negligible"

    v = np.sqrt(chi2 / (n * min_dim))

    # Interpretation
    if v < 0.1:
        interpretation = "negligible"
    elif v < 0.3:
        interpretation = "small"
    elif v < 0.5:
        interpretation = "medium"
    else:
        interpretation = "large"

    return float(v), interpretation


def perform_ttest(groups: list[np.ndarray], group_names: list[str],
                   equal_var: bool, alpha: float) -> Dict[str, Any]:
    """Perform independent samples t-test."""
    group1, group2 = groups

    if equal_var:
        statistic, p_value = stats.ttest_ind(group1, group2)
        test_name = "Independent t-test"
    else:
        statistic, p_value = stats.ttest_ind(group1, group2, equal_var=False)
        test_name = "Welch's t-test"

    # Effect size
    effect_size_val, effect_interp = cohens_d(group1, group2)

    # Confidence interval for difference in means
    diff = np.mean(group1) - np.mean(group2)
    se_diff = np.sqrt(np.var(group1, ddof=1) / len(group1) + np.var(group2, ddof=1) / len(group2))
    df = len(group1) + len(group2) - 2
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    ci_lower = diff - t_crit * se_diff
    ci_upper = diff + t_crit * se_diff

    # Interpretation
    if p_value < alpha:
        interp = (
            f"The test suggests a statistically significant difference between {group_names[0]} "
            f"and {group_names[1]} (p={p_value:.4f}). The effect size appears {effect_interp} "
            f"(Cohen's d={effect_size_val:.3f}), indicating the practical significance may "
            f"{'be substantial' if abs(effect_size_val) > 0.5 else 'be limited'}."
        )
    else:
        interp = (
            f"The test does not provide sufficient evidence of a difference between {group_names[0]} "
            f"and {group_names[1]} (p={p_value:.4f}). However, this does not prove the groups are "
            f"equivalent; a larger sample may be needed."
        )

    return {
        "test_used": test_name,
        "test_reason": f"Two groups detected; normality {'satisfied' if equal_var else 'satisfied but unequal variances'}",
        "result": {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": {
                "name": "Cohen's d",
                "value": effect_size_val,
                "interpretation": effect_interp
            },
            "confidence_interval": {
                "lower": float(ci_lower),
                "upper": float(ci_upper),
                "level": 1 - alpha
            },
            "interpretation": interp
        }
    }


def perform_mann_whitney(groups: list[np.ndarray], group_names: list[str],
                          alpha: float) -> Dict[str, Any]:
    """Perform Mann-Whitney U test."""
    group1, group2 = groups

    statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')

    # Effect size
    effect_size_val, effect_interp = rank_biserial(group1, group2, statistic)

    # Interpretation
    if p_value < alpha:
        interp = (
            f"The test suggests a statistically significant difference in distributions between "
            f"{group_names[0]} and {group_names[1]} (p={p_value:.4f}). The effect size appears "
            f"{effect_interp} (rank-biserial r={effect_size_val:.3f})."
        )
    else:
        interp = (
            f"The test does not provide sufficient evidence of a distributional difference between "
            f"{group_names[0]} and {group_names[1]} (p={p_value:.4f})."
        )

    return {
        "test_used": "Mann-Whitney U test",
        "test_reason": "Two groups detected; normality assumption not satisfied",
        "result": {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": {
                "name": "Rank-biserial correlation",
                "value": effect_size_val,
                "interpretation": effect_interp
            },
            "confidence_interval": None,  # Not applicable
            "interpretation": interp
        }
    }


def perform_anova(groups: list[np.ndarray], group_names: list[str],
                   alpha: float) -> Dict[str, Any]:
    """Perform one-way ANOVA."""
    statistic, p_value = stats.f_oneway(*groups)

    # Effect size
    effect_size_val, effect_interp = eta_squared(groups)

    # Interpretation
    if p_value < alpha:
        interp = (
            f"The test suggests statistically significant differences among the {len(groups)} groups "
            f"(p={p_value:.4f}). The effect size appears {effect_interp} (η²={effect_size_val:.3f}). "
            f"Post-hoc tests may be needed to identify which groups differ."
        )
    else:
        interp = (
            f"The test does not provide sufficient evidence of differences among the {len(groups)} "
            f"groups (p={p_value:.4f})."
        )

    return {
        "test_used": "One-way ANOVA",
        "test_reason": f"{len(groups)} groups detected; normality and equal variance assumptions satisfied",
        "result": {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": {
                "name": "Eta-squared",
                "value": effect_size_val,
                "interpretation": effect_interp
            },
            "confidence_interval": None,  # Not applicable for ANOVA
            "interpretation": interp
        }
    }


def perform_kruskal(groups: list[np.ndarray], group_names: list[str],
                     alpha: float) -> Dict[str, Any]:
    """Perform Kruskal-Wallis H test."""
    statistic, p_value = stats.kruskal(*groups)

    # Effect size (epsilon-squared approximation)
    all_data = np.concatenate(groups)
    n = len(all_data)
    k = len(groups)
    epsilon_sq = (statistic - k + 1) / (n - k) if n > k else 0

    if epsilon_sq < 0.01:
        effect_interp = "negligible"
    elif epsilon_sq < 0.06:
        effect_interp = "small"
    elif epsilon_sq < 0.14:
        effect_interp = "medium"
    else:
        effect_interp = "large"

    # Interpretation
    if p_value < alpha:
        interp = (
            f"The test suggests statistically significant differences in distributions among the "
            f"{len(groups)} groups (p={p_value:.4f}). The effect size appears {effect_interp} "
            f"(ε²≈{epsilon_sq:.3f}). Post-hoc tests may be needed to identify which groups differ."
        )
    else:
        interp = (
            f"The test does not provide sufficient evidence of distributional differences among the "
            f"{len(groups)} groups (p={p_value:.4f})."
        )

    return {
        "test_used": "Kruskal-Wallis H test",
        "test_reason": f"{len(groups)} groups detected; normality assumption not satisfied",
        "result": {
            "statistic": float(statistic),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": {
                "name": "Epsilon-squared (approx)",
                "value": float(epsilon_sq),
                "interpretation": effect_interp
            },
            "confidence_interval": None,  # Not applicable
            "interpretation": interp
        }
    }


def perform_chi_square(df: pd.DataFrame, group_col: str, value_col: str,
                        alpha: float) -> Dict[str, Any]:
    """Perform chi-square test of independence."""
    contingency_table = pd.crosstab(df[group_col], df[value_col])

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    # Effect size
    effect_size_val, effect_interp = cramers_v(contingency_table.values)

    # Interpretation
    if p_value < alpha:
        interp = (
            f"The test suggests a statistically significant association between {group_col} "
            f"and {value_col} (p={p_value:.4f}). The effect size appears {effect_interp} "
            f"(Cramér's V={effect_size_val:.3f})."
        )
    else:
        interp = (
            f"The test does not provide sufficient evidence of an association between {group_col} "
            f"and {value_col} (p={p_value:.4f})."
        )

    return {
        "test_used": "Chi-square test of independence",
        "test_reason": "Both variables are categorical",
        "result": {
            "statistic": float(chi2),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": {
                "name": "Cramér's V",
                "value": effect_size_val,
                "interpretation": effect_interp
            },
            "confidence_interval": None,  # Not applicable
            "interpretation": interp
        }
    }


def main(input_path: str, output_path: str,
         group_col: Optional[str] = None, value_col: Optional[str] = None,
         test: str = "auto", alpha: float = 0.05,
         input_format: str = "auto") -> Dict[str, Any]:
    """
    Automatic hypothesis test selection and execution.

    Args:
        input_path: Path to input CSV/Parquet
        output_path: Path to save results JSON
        group_col: Column with group labels
        value_col: Column with values to compare
        test: Test type or "auto"
        alpha: Significance level

    Returns:
        Result dictionary with test results and interpretation
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

        # Validate columns
        if not group_col or not value_col:
            return {
                "success": False,
                "error": "Both group_col and value_col are required",
                "suggestion": "Specify which column contains groups and which contains values"
            }

        missing_cols = [c for c in [group_col, value_col] if c not in df.columns]
        if missing_cols:
            valid = list(df.columns)
            if format_column_error is not None:
                return format_column_error(missing_cols, valid)
            elif suggest_column is not None:
                detail = suggest_column(missing_cols[0], valid)
                return {"success": False, **detail}
            else:
                return {
                    "success": False,
                    "error": f"Column(s) not found: {missing_cols}",
                    "available_columns": sorted(valid)
                }

        # Prepare data
        df_clean = df[[group_col, value_col]].dropna()

        if len(df_clean) < 3:
            return {
                "success": False,
                "error": "Insufficient data after removing missing values",
                "suggestion": "At least 3 observations are required"
            }

        # Split into groups
        group_names = sorted(df_clean[group_col].unique())
        groups = [df_clean[df_clean[group_col] == name][value_col].values for name in group_names]

        # Group statistics
        group_stats = {
            str(name): {
                "n": int(len(g)),
                "mean": float(np.mean(g)) if len(g) > 0 else None,
                "std": float(np.std(g, ddof=1)) if len(g) > 1 else None
            }
            for name, g in zip(group_names, groups)
        }

        # Determine test
        result_data = {}

        if test != "auto":
            # Manual test selection
            if test == "ttest":
                result_data = perform_ttest(groups[:2], group_names[:2], True, alpha)
            elif test == "welch":
                result_data = perform_ttest(groups[:2], group_names[:2], False, alpha)
            elif test == "mann_whitney":
                result_data = perform_mann_whitney(groups[:2], group_names[:2], alpha)
            elif test == "anova":
                result_data = perform_anova(groups, group_names, alpha)
            elif test == "kruskal_wallis":
                result_data = perform_kruskal(groups, group_names, alpha)
            elif test == "chi_square":
                result_data = perform_chi_square(df_clean, group_col, value_col, alpha)
            else:
                return {
                    "success": False,
                    "error": f"Unknown test: {test}",
                    "suggestion": "Use 'auto' or one of: ttest, welch, mann_whitney, anova, kruskal_wallis, chi_square"
                }
        else:
            # Auto selection
            # Check if categorical
            is_value_numeric = pd.api.types.is_numeric_dtype(df_clean[value_col])

            if not is_value_numeric:
                # Both categorical → chi-square
                result_data = perform_chi_square(df_clean, group_col, value_col, alpha)
            elif len(groups) == 2:
                # Two groups
                # Check normality
                _, g1_normal = check_normality(groups[0])
                _, g2_normal = check_normality(groups[1])

                if g1_normal and g2_normal:
                    # Check equal variance
                    _, equal_var = check_equal_variance(groups)
                    result_data = perform_ttest(groups, group_names, equal_var, alpha)
                else:
                    result_data = perform_mann_whitney(groups, group_names, alpha)
            else:
                # Three or more groups
                # Check normality for all groups
                all_normal = all(check_normality(g)[1] for g in groups)

                if all_normal:
                    _, equal_var = check_equal_variance(groups)
                    if equal_var:
                        result_data = perform_anova(groups, group_names, alpha)
                    else:
                        # ANOVA is somewhat robust to unequal variances with balanced designs
                        result_data = perform_anova(groups, group_names, alpha)
                        result_data["caveats"] = result_data.get("caveats", []) + [
                            "Unequal variances detected; ANOVA may be less reliable"
                        ]
                else:
                    result_data = perform_kruskal(groups, group_names, alpha)

        # Build final result
        result = {
            "success": True,
            "output_path": str(output_path),
            "rows_in": rows_in,
            "rows_out": len(df_clean),
            **result_data,
            "groups": group_stats,
            "caveats": result_data.get("caveats", []) + [
                f"Test assumes observations are independent and randomly sampled",
                f"Statistical significance (p<{alpha}) does not imply practical importance",
                "Correlation does not imply causation",
                f"Sample sizes: {', '.join(f'{name}={len(g)}' for name, g in zip(group_names, groups))}"
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
    parser = argparse.ArgumentParser(description="Automatic hypothesis testing")
    parser.add_argument("--input", required=True, help="Input CSV/Parquet path")
    parser.add_argument("--output", default="logs/hypothesis_test.json", help="Output JSON path (default: logs/hypothesis_test.json)")
    parser.add_argument("--group_col", help="Group column name")
    parser.add_argument("--value_col", help="Value column name")
    parser.add_argument("--test", default="auto",
                        choices=["auto", "ttest", "welch", "mann_whitney",
                                 "anova", "kruskal_wallis", "chi_square"],
                        help="Test type (default: auto)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
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
        if not os.path.isfile(args.input):
            print(json.dumps({"success": False, "error": f"Input file not found: {args.input}"}, indent=2))
            sys.exit(1)
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "hypothesis_test",
                "input": args.input,
                "output": args.output,
                "steps": [
                    "Load input CSV/Parquet file",
                    "Validate group_col and value_col columns",
                    "Check normality and variance of groups",
                    "Auto-select or apply specified statistical test",
                    "Compute effect size and confidence intervals",
                    "Write JSON results to output path"
                ],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(
        input_path=args.input,
        output_path=args.output,
        group_col=args.group_col,
        value_col=args.value_col,
        test=args.test,
        alpha=args.alpha,
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
        ckpt_path = maybe_checkpoint(args.output, "hypothesis_test", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["success"] else 1)
