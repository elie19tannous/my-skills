---
name: magic-statistical-analysis
description: Perform descriptive statistics, hypothesis testing, and correlation analysis with mandatory uncertainty communication. Use when computing statistics, testing hypotheses, comparing groups, or analyzing correlations with significance.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: high
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - statistics
  - hypothesis-testing
  - correlation
  - analysis
  scripts:
  - scripts/descriptive_stats.py
  - scripts/hypothesis_test.py
  - scripts/correlation_analysis.py
  dependencies:
  - pandas
  - numpy
  - scipy
  - matplotlib
  - seaborn
  when_to_use: 'When computing statistics or testing hypotheses. Trigger phrases: statistics, statistical, hypothesis test, t-test, chi-square, correlation, regression, significance, p-value, distribution, balance check.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "run a statistical test" / "compare these groups"
- "is this difference significant?" / "test the hypothesis"
- "compute correlations" / "what's the correlation?"
- "descriptive statistics" / "summarize the numbers"

These produce the SAME behavior as the statistical analysis workflow.

## When to Use

- Need descriptive statistics with narrative interpretation
- Need hypothesis testing (group comparisons)
- Need correlation analysis with significance
- After magic-data-profiling or magic-data-cleaning, before reporting
- Results naturally feed into `magic-report-generation` for structured deliverables, or `magic-data-visualization` for charts illustrating the findings

**When NOT to Use:** Use magic-data-profiling for initial exploration; use magic-data-exploration for pattern discovery.

## Data Processing Expertise

### Thinking

Before running any statistical test, ask:
- **Am I exploring or confirming?** — Exploratory analysis generates hypotheses; confirmatory analysis tests them. Using the same data for both inflates false discovery rates. If you explored the data to find a pattern and now want to test it, you need a held-out sample or an explicit acknowledgment that this is post-hoc.
- **What is the minimum meaningful effect size?** — A p-value < 0.05 with Cohen's d = 0.01 is statistically significant but practically meaningless. Before testing, define what magnitude of difference matters for the domain. For example, a 0.1% improvement in click-through rate may be noise; a 2% improvement may be actionable.
- **Is my sample representative?** — Selection bias, survivorship bias, and convenience sampling all produce misleading results regardless of test power. Consider how the data was collected and whether the sample reflects the population you want to draw conclusions about.
- **How many tests am I running?** — Each additional test inflates the false discovery rate. Running 20 tests at alpha=0.05 yields ~1 false positive by chance. Apply Bonferroni correction (alpha / number_of_tests) for 3-5 tests, or FDR (Benjamini-Hochberg) for 6+ tests.
- **Are my groups independent?** — Paired observations (before/after on the same subjects) require paired tests. Using unpaired tests on paired data discards valuable information and reduces power.

### Rules

- **Test selection by data characteristics**: Determine the test by (1) number of groups, (2) whether the value column is numeric, and (3) whether the data is normally distributed. Follow the matrix: 2 groups + normal = t-test; 2 groups + non-normal = Mann-Whitney U; >2 groups + normal = one-way ANOVA; >2 groups + non-normal = Kruskal-Wallis; both categorical = chi-square.
- **Normality testing before parametric tests**: Always check normality with the Shapiro-Wilk test before choosing a parametric test. If p < 0.05, the normality assumption is violated — use the non-parametric alternative. The script auto-selects, but verify the selection in results.
- **Effect size reporting alongside p-values**: Every hypothesis test must report an effect size (Cohen's d for t-tests, eta-squared for ANOVA, rank-biserial for Mann-Whitney U, epsilon-squared for Kruskal-Wallis, Cramer's V for chi-square). The p-value tells you whether an effect exists; the effect size tells you whether it matters.
- **Multiple comparison correction**: When running 3+ tests on the same dataset, apply correction. 1-2 tests: none needed (standard alpha=0.05). 3-5 tests: Bonferroni (alpha / number_of_tests). 6+ tests: FDR Benjamini-Hochberg (controls false discovery proportion).
- **Correlation method selection**: Use Pearson for normally distributed columns with linear relationships. Use Spearman for non-normal data or non-linear monotonic relationships. Auto-selection checks normality of all columns and falls back to Spearman if any column fails.
- **When to use LLM**: Statistics is deterministic — always use code for computation. Interpretation of results for narrative reports (explaining what findings mean for a specific domain) is optional LLM work via `magic-report-generation`. Never use LLM to compute statistics.

### Constraints

- MUST include effect size with every hypothesis test (Cohen's d, eta-squared, rank-biserial, epsilon-squared, or Cramer's V as appropriate)
- MUST include confidence intervals where applicable (t-tests)
- MUST use uncertainty language in interpretations: "suggests", "appears to", "may indicate"
- MUST include a caveats array in every output
- MUST check normality (Shapiro-Wilk) before selecting parametric tests
- MUST apply multiple comparison correction when running 3+ tests on the same dataset
- NEVER report a p-value without the corresponding effect size — a significant p-value with negligible effect size is misleading
- NEVER use parametric tests on non-normal data without checking — invalid p-values result from violated assumptions; the script auto-selects, but if overriding manually, verify normality first
- NEVER claim causation from correlation — "X correlates with Y" is not "X causes Y"
- NEVER use "proves" or "definitively shows" — statistical tests provide evidence, not proof
- NEVER ignore multiple comparison correction when running 3+ tests — reporting only significant results from many tests is cherry-picking (inflated false discovery rate)
- NEVER conclude "no difference" from a non-significant result — absence of evidence is not evidence of absence (Type II error); report power analysis or confidence interval width instead

## Seed Patterns

### Descriptive statistics computation
```python
import pandas as pd
import numpy as np

def descriptive_stats(df: pd.DataFrame, columns: list[str] = None) -> dict:
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    stats = {}
    for col in cols:
        s = df[col].dropna()
        stats[col] = {
            "n": len(s), "mean": float(s.mean()), "std": float(s.std()),
            "median": float(s.median()), "skewness": float(s.skew()),
            "p25": float(s.quantile(0.25)), "p75": float(s.quantile(0.75)),
        }
        # Flag distribution shape
        stats[col]["shape"] = (
            "symmetric" if abs(stats[col]["skewness"]) < 0.5
            else "right-skewed" if stats[col]["skewness"] > 0
            else "left-skewed"
        )
    return stats
```

### Hypothesis test selection and execution
```python
from scipy import stats as sp
import numpy as np

def auto_test(groups: list[np.ndarray], alpha: float = 0.05) -> dict:
    # Check normality for each group
    all_normal = all(sp.shapiro(g)[1] > 0.05 for g in groups if len(g) >= 3)

    if len(groups) == 2:
        g1, g2 = groups
        if all_normal:
            stat, p = sp.ttest_ind(g1, g2)
            pooled_std = np.sqrt(((len(g1)-1)*g1.var(ddof=1) + (len(g2)-1)*g2.var(ddof=1)) / (len(g1)+len(g2)-2))
            d = (g1.mean() - g2.mean()) / pooled_std if pooled_std else 0
            return {"test": "t-test", "p": p, "effect_size": ("Cohen's d", d)}
        else:
            stat, p = sp.mannwhitneyu(g1, g2, alternative="two-sided")
            r = 1 - (2 * stat) / (len(g1) * len(g2))
            return {"test": "Mann-Whitney U", "p": p, "effect_size": ("rank-biserial r", r)}
    else:  # 3+ groups
        if all_normal:
            stat, p = sp.f_oneway(*groups)
            grand = np.concatenate(groups)
            ss_b = sum(len(g)*(g.mean()-grand.mean())**2 for g in groups)
            eta2 = ss_b / ((grand - grand.mean())**2).sum()
            return {"test": "ANOVA", "p": p, "effect_size": ("eta-squared", eta2)}
        else:
            stat, p = sp.kruskal(*groups)
            return {"test": "Kruskal-Wallis", "p": p, "statistic": stat}
```

### Correlation analysis with significance
```python
from scipy import stats as sp
import pandas as pd, numpy as np

def correlate(df: pd.DataFrame, method: str = "auto", alpha: float = 0.05) -> list[dict]:
    num_cols = df.select_dtypes(include=[np.number]).columns
    all_normal = all(sp.shapiro(df[c].dropna())[1] > 0.05 for c in num_cols if len(df[c].dropna()) >= 3)
    use = "pearson" if (method == "auto" and all_normal) or method == "pearson" else "spearman"
    compute = sp.pearsonr if use == "pearson" else sp.spearmanr

    results = []
    for i, a in enumerate(num_cols):
        for b in num_cols[i+1:]:
            mask = df[a].notna() & df[b].notna()
            if mask.sum() < 3: continue
            r, p = compute(df.loc[mask, a], df.loc[mask, b])
            results.append({"a": a, "b": b, "r": float(r), "p": float(p),
                            "significant": p < alpha, "method": use})
    return sorted(results, key=lambda x: abs(x["r"]), reverse=True)
```

### Multiple comparison correction
```python
import numpy as np

def bonferroni(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    adjusted_alpha = alpha / len(p_values)
    return [{"p": p, "adjusted_alpha": adjusted_alpha,
             "significant": p < adjusted_alpha} for p in p_values]

def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    n = len(p_values)
    ranked = sorted(enumerate(p_values), key=lambda x: x[1])
    results = [None] * n
    for rank, (idx, p) in enumerate(ranked, 1):
        threshold = (rank / n) * alpha
        results[idx] = {"p": p, "rank": rank, "threshold": threshold,
                        "significant": p <= threshold}
    return results
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `descriptive_stats.py` | A | `python3 descriptive_stats.py --input data.csv --output stats.json` | `--columns col1,col2` to restrict; `--explain` for verbose narrative |
| `correlation_analysis.py` | A | `python3 correlation_analysis.py --input data.csv --output corr.json` | `--method pearson\|spearman\|kendall` to override auto; `--columns` to restrict; `--min_significance` to adjust |
| `hypothesis_test.py` | B | `python3 hypothesis_test.py --input data.csv --output test.json --group_col region --value_col revenue` | `--group_col` and `--value_col` functionally required; `--test` to override auto; `--explain` for narrative |

**Reference implementations** -- read patterns, write custom code:

*(none — all statistics scripts are now scriptable)*

Scripts accept `--input` / `--output` named flags and `--input-format` (auto/csv/tsv/jsonl/json/parquet/excel).

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For statistical analysis specifically:**

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After hypothesis testing | **Always** | Statistical results ARE the deliverable |
| After correlation analysis | **Yes** | Expensive on large datasets (pairwise computation) |
| After descriptive stats | **Optional** | Cheap to re-compute; save if feeding into a report |
| After regression/modeling | **Always** | Model fitting is expensive; coefficients are the output |

**Suggested names:** `stats_descriptive.json`, `stats_hypothesis.json`, `stats_correlation.json`, `stats_regression.json`

Include provenance metadata: input file, test parameters, sample sizes, alpha level, correction method.

**Save pattern:**
```python
import json, datetime
from pathlib import Path

def save_checkpoint(df, path: str, metadata: dict = None) -> str:
    """Save data + provenance metadata. Use at phase boundaries."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == ".parquet":
        df.to_parquet(p, index=False)
    elif p.suffix == ".jsonl":
        df.to_json(p, orient="records", lines=True, force_ascii=False)
    else:
        df.to_csv(p, index=False)
    meta = {
        "rows": len(df), "cols": list(df.columns),
        "saved_at": datetime.datetime.utcnow().isoformat(),
        **(metadata or {}),
    }
    p.with_suffix(".meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False)
    )
    return str(p)
```

## Self-Healing

If analysis fails:
1. Read error JSON — check `suggestion` field
2. Read script source to understand the failure mode
3. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Too few samples for test | Small group size | Use non-parametric test or note limitation |
| Non-numeric group column | Wrong column specified | Check column types, use categorical column for grouping |
| Constant column | Zero variance | Skip column, note in warnings |
| Normality violated + small sample | Shapiro-Wilk p < 0.05 with n < 30 | Use non-parametric alternative (Mann-Whitney U or Kruskal-Wallis); do NOT force parametric test |
| Tiny effect + huge sample | p < 0.001 but Cohen's d < 0.1 | Report: "Statistically significant but practically negligible effect (d = X)." Do not emphasize the finding |
| Multicollinearity warning | |r| > 0.9 between predictors | Consider dropping one of the correlated variables before modeling |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Test selection | `references/test_selection_guide.md` | Choosing the right statistical test |
| Interpretation | `references/interpretation_guide.md` | Writing statistical narratives |
| Pitfalls | `references/statistical_pitfalls.md` | Results seem unexpected or contradictory |

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- If statistically significant findings are detected, present them with effect sizes, confidence intervals, and caveats. Include: test used, p-value, effect size interpretation, and sample size context. Ask the user which findings to highlight in reporting before proceeding.

### Workspace Integration
- Update `workspace_state.md` with analysis results.
- Log statistical decisions in `logs/analysis_journal.md`.
