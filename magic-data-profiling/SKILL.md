---
name: magic-data-profiling
description: Profile datasets — run quality scoring, distribution analysis, outlier detection, and issue detection. Use when assessing data quality, running quality_score.py, getting a quality overview, or profiling before cleaning.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: medium
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - profiling
  - statistics
  - quality
  - eda
  scripts:
  - scripts/distribution_analysis.py
  - scripts/correlation_matrix.py
  - scripts/outlier_detection.py
  - scripts/quality_score.py
  - scripts/detect_all_issues.py
  - scripts/deep_quality_analysis.py
  - scripts/detect_categories.py
  - scripts/classify_answers.py
  dependencies:
  - pandas
  - numpy
  - scipy
  - matplotlib
  - seaborn
  when_to_use: 'When user wants to understand data quality, distributions, or characteristics. Trigger phrases: profile, quality, check quality, assess, what types, categorize, classify, outliers, distributions, summarize data.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "profile this data" / "what's the quality?" / "run a quality check"
- "assess data quality" / "how clean is this data?"
- "detect issues" / "find problems in this dataset"
- "what's the quality score?"
- "categorize" / "find categories" / "what types of data?"
- "classify answers" / "what answer types?"
- "summarize this data" / "check for outliers" / "show distributions" / "data quality check"

These produce the SAME behavior as running the profiling workflow. Slash commands are shortcuts — natural language works equally well.

## When to Use

- Need to understand data characteristics before cleaning or analysis
- Need distribution analysis (skewness, normality tests)
- Need to detect outliers or assess data quality
- Need correlation analysis with significance testing
- Need to discover categorical groupings or classify value types

**When NOT to Use:** Use magic-statistical-analysis for hypothesis testing; use magic-data-exploration for pattern discovery. Data is already profiled and results are available — re-profile only after transformations.

## Data Processing Expertise

### Thinking

Before profiling any dataset, ask:
- **What quality level does this use case need?** — A quick exploratory analysis tolerates more issues than production data feeding a model. Match quality expectations to purpose before interpreting scores.
- **What are the deal-breakers?** — Some issues are blocking (wrong types, corrupt rows, join key with 40% nulls) while others are cosmetic (trailing whitespace). Triage by downstream impact, not count.
- **Does the aggregate score tell the whole story?** — A 95/100 quality score can still have a corrupted primary key column. The aggregate masks critical column-level failures because high-quality columns dilute the broken ones. Always inspect per-column breakdown.
- **How big is this dataset?** — Datasets >1M rows need sampling for initial profiling. Running all 6 sub-analyses sequentially on large data takes 30+ minutes and may OOM on correlation heatmaps.
- **Am I profiling the right snapshot?** — After cleaning, re-profile to verify improvements. Profiling before AND after is essential. A single profiling pass tells you what exists, not whether fixes worked.
- **Which outlier method fits?** — IQR assumes nothing about distribution shape (use for skewed data). Z-score assumes normality (use when Shapiro-Wilk passes). On small samples (<50 rows), both are unreliable — consider manual inspection.

### Rules

- **Column type detection before profiling**: Always detect column types first. Use text metrics (length distribution, vocabulary) for text columns; numeric metrics (mean, std, quartiles) for numeric columns. Applying numeric profiling to text columns produces meaningless NaN statistics.
- **Per-column breakdown is mandatory**: Never present an aggregate quality score without the per-column dimension scores (completeness, validity, uniqueness). The worst column matters more than the average.
- **Distribution shape drives method choice**: Run normality test (Shapiro-Wilk) before choosing correlation method (Pearson for normal, Spearman for non-normal) or outlier method (Z-score for normal, IQR for skewed).
- **Sample before full-scale on large data**: Use `sample_rows.py` or `load_file.py --nrows 10000` to create a sample for initial profiling on datasets >1M rows. Run full profiling only on targeted columns after reviewing sample results.
- **Sampling has uncertainty**: When profiling from a sample, explicitly note that rare patterns (<0.1% frequency) may be missed. Report sample size alongside all findings. Always recommend targeted full-scale profiling for critical columns after sample review.
- **Cache expensive operations**: For repeated profiling (e.g., re-profile after cleaning), cache distribution stats and correlation matrices keyed by input hash + operation. Avoid recomputing unchanged columns — store intermediate results and reuse when input hasn't changed.
- **Memory-aware scaling**: When transitioning from sample to full dataset, estimate memory requirements (row_count × avg_row_bytes). For datasets >1GB in memory, profile columns in batches or chunks rather than loading the entire DataFrame at once. Correlation heatmaps on 25+ columns at full scale can OOM — compute pairwise on targeted column pairs instead.
- **Quality scores have blind spots**: A composite quality score measures structural quality (completeness, type consistency, format uniformity) but NOT semantic validity or business rule compliance. A dataset can score 95/100 while having critical domain issues (e.g., 80% of a status column being "ACTIVE" in historical data, or all dates in the future). Always complement quality scoring with content validation (`magic-data-validation`) for domain-specific rules.
- **Category detection cascade**: Try first-line extraction first (structured text), then TF-IDF/KMeans clustering (unstructured text), then cardinality analysis (low-cardinality columns). The auto method follows this cascade.
- **Binary classification limitation**: `classify_answers.py` only matches single-char binary (0/1/yes/no/true/false). Multi-digit binary strings like "10010111" are classified as "integer" because they match the integer regex first. If your dataset contains 8-bit binary, inspect classification results and reclassify manually.
- **When to use LLM**: Profiling is deterministic — use code, not LLM. If profiling reveals data that needs semantic interpretation (e.g., "is this column name or address?"), hand off to `magic-data-synthesis` for semantic analysis. Never use LLM for computing statistics.

### Constraints

- MUST detect column types before profiling — applying numeric stats to text columns produces silent garbage (NaN means, zero variance)
- MUST report per-column dimension scores alongside any aggregate quality score — a dataset scoring 95/100 can have a corrupted primary key column or a join key with 40% nulls
- MUST report uncertainty — note sample size when profiling sampled data; note that heuristic scores are not absolute measures
- MUST NOT run `detect_all_issues.py` on datasets >1M rows without first sampling — use `sample_rows.py` or `load_file.py --nrows` to create a sample. The script runs 6 sub-analyses sequentially, taking 30+ minutes and risking OOM on correlation heatmaps
- MUST NOT skip normality test before choosing correlation method — Pearson on non-normal data gives misleading coefficients
- NEVER report an aggregate quality score without the per-column breakdown — high-quality columns dilute the score of broken ones; the worst column is what matters
- NEVER run outlier detection on small samples (<50 rows) without noting the limitation — IQR and Z-score thresholds are unreliable with few data points; report sample size alongside results
- NEVER report quality score without context — a score of 80/100 means different things for a 100-row sample vs a 1M-row production dataset; always report score alongside row count, column count, and use case context

## Seed Patterns

### Quality score computation
```python
import pandas as pd
import numpy as np

def quality_score(df: pd.DataFrame) -> dict:
    total_cells = df.shape[0] * df.shape[1]
    missing_pct = (df.isna().sum().sum() / total_cells * 100) if total_cells else 0
    completeness = max(0, 100 - missing_pct * 2)

    # Consistency: mixed types per column
    mixed = sum(1 for c in df.columns if df[c].dtype == object
                and 0.1 < pd.to_numeric(df[c], errors="coerce").notna().mean() < 0.9)
    consistency = max(0, 100 - (mixed / len(df.columns) * 200))

    # Uniqueness: duplicate rows
    dup_pct = df.duplicated().mean() * 100
    uniqueness = max(0, 100 - dup_pct)

    # Validity: IQR outlier rate on numeric columns
    num = df.select_dtypes(include=[np.number])
    outlier_n = 0
    for c in num.columns:
        s = num[c].dropna()
        if len(s) < 4: continue
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        outlier_n += ((s < Q1 - 1.5*(Q3-Q1)) | (s > Q3 + 1.5*(Q3-Q1))).sum()
    validity = max(0, 100 - (outlier_n / max(num.count().sum(), 1) * 5))

    overall = completeness*0.30 + consistency*0.25 + uniqueness*0.20 + validity*0.25
    grade = "A" if overall>=90 else "B" if overall>=75 else "C" if overall>=60 else "D" if overall>=40 else "F"
    return {"overall": round(overall,1), "grade": grade,
            "completeness": round(completeness,1), "consistency": round(consistency,1),
            "uniqueness": round(uniqueness,1), "validity": round(validity,1)}
```

### Distribution analysis (numeric + text)
```python
from scipy import stats
import pandas as pd
import numpy as np

def analyze_distributions(df: pd.DataFrame, col: str) -> dict:
    s = df[col].dropna()
    if pd.api.types.is_numeric_dtype(s):
        sample = s.sample(min(len(s), 5000), random_state=42) if len(s) > 5000 else s
        _, p = stats.shapiro(sample)
        return {
            "type": "numeric",
            "skewness": float(stats.skew(s)),
            "kurtosis": float(stats.kurtosis(s)),
            "is_normal": p > 0.05,
            "shape": "normal" if p > 0.05 else ("right_skewed" if stats.skew(s) > 2 else "left_skewed" if stats.skew(s) < -2 else "non-normal"),
        }
    else:
        lengths = s.astype(str).str.len()
        return {
            "type": "text",
            "mean_length": float(lengths.mean()),
            "median_length": float(lengths.median()),
            "vocab_size": len(set(" ".join(s.astype(str)).lower().split())),
        }
```

### Outlier detection (IQR for skewed, Z-score for normal)
```python
import numpy as np
from scipy import stats

def detect_outliers(series, method="iqr"):
    s = series.dropna()
    if len(s) < 4:
        return {"count": 0, "indices": []}
    if method == "iqr":
        Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
        IQR = Q3 - Q1
        mask = (s < Q1 - 1.5*IQR) | (s > Q3 + 1.5*IQR)
    else:  # zscore
        mask = np.abs(stats.zscore(s)) > 3.0
    return {"count": int(mask.sum()), "pct": round(mask.mean()*100, 2),
            "indices": s[mask].index.tolist()[:20]}
```

### Category detection (cardinality + first-line)
```python
import pandas as pd

def detect_categories(series: pd.Series, min_group_size: int = 10) -> dict:
    clean = series.dropna()
    ratio = clean.nunique() / len(clean) if len(clean) else 1
    if ratio < 0.1:  # Low cardinality = categorical
        counts = clean.value_counts()
        cats = [{"label": str(v)[:60], "count": int(c), "pct": round(c/len(clean)*100, 2)}
                for v, c in counts.head(20).items() if c >= min_group_size]
        return {"method": "cardinality", "categories": cats}
    # Try first-line extraction for structured text
    first_lines = clean.astype(str).str.split('\n').str[0].str.strip()
    counts = first_lines.value_counts()
    valid = counts[counts >= min_group_size]
    if len(valid) >= 2:
        cats = [{"label": str(v)[:60], "count": int(c), "pct": round(c/len(clean)*100, 2)}
                for v, c in valid.items()]
        return {"method": "first_line", "categories": cats}
    return {"method": "none", "categories": []}
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `quality_score.py` | A | `python3 quality_score.py data.parquet logs/quality.json` | Custom weights (completeness 50% for ML training), additional dimensions (timeliness, relevance), domain-specific thresholds, per-column scoring. Standard mode: fixed 4-dimension formula (completeness 30%, consistency 25%, uniqueness 20%, validity 25%). |
| `detect_all_issues.py` | A | `python3 detect_all_issues.py data.parquet report.json` | `--include-content-validation` for sentinel checks; `--sentinel-patterns` for custom sentinel list |
| `distribution_analysis.py` | A | `python3 distribution_analysis.py data.csv dist.json` | `--columns col1,col2` to limit scope on wide datasets |
| `outlier_detection.py` | A | `python3 outlier_detection.py data.csv outliers.json` | `--method zscore --threshold 3.0` for normal data (BUG: default threshold 1.5 is wrong for zscore); `--method both` for dual detection |
| `correlation_matrix.py` | A | `python3 correlation_matrix.py data.csv corr.json` | `--method pearson\|spearman` to override auto; `--columns` to limit scope. Outputs 3 artifacts: JSON + CSV matrix + PNG heatmap |
| `deep_quality_analysis.py` | A | `python3 deep_quality_analysis.py data.csv analysis.json` | `--depth deep` for full investigation (default is `surface`); `--columns` for targeted analysis; `--sample N` for large datasets |
| `detect_categories.py` | A | `python3 detect_categories.py --input data.csv --output cats.json` | `--column name` to override auto-selection; `--method tfidf_kmeans` to force clustering (requires sklearn) |
| `classify_answers.py` | A | `python3 classify_answers.py --input data.csv --output classify.json` | `--column col` when auto-selection picks wrong column; `--sample N` for large datasets |

**Reference implementations** -- read patterns, write custom code:

*(none — all profiling scripts are now scriptable)*

Scripts accept `--input-format` (auto/csv/tsv/jsonl/json/parquet/excel). Most use positional arguments (`input_file output_file`); `detect_categories.py` and `classify_answers.py` use `--input`/`--output` flags.

### Outlier Method Comparison
| Method | Best For | Assumption | Sensitivity |
|--------|----------|------------|-------------|
| IQR | Skewed data | None | Moderate (1.5xIQR) |
| Z-score | Normal data | Normality | High (>3 sigma) |

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For profiling specifically:** Profiling output (quality scores, issue reports) is always worth saving — it's cheap to store and expensive to re-profile large data. Save the profiling results JSON even if you don't checkpoint the data itself.

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| Quality score output | **Always** | Cheap to save, baseline for all downstream work |
| Issue detection output | **Always** | Findings drive the cleaning plan |
| Deep quality analysis | **Always** | Expensive to re-run, especially on large data |
| Large dataset (>500K rows) | **Always unconditionally** | Profiling takes 20-30 minutes; never re-run |
| Small dataset, quick profile | **Yes** | Even cheap profiles are worth persisting |

- `quality_report.json` — the output of `quality_score.py`
- `issues_report.json` — the output of `detect_all_issues.py` (single JSON with nested sub-analyses: `{sentinels, quality, distributions, outliers, correlations, categories, answer_classification, errors}`)
- `deep_analysis.json` — the output of `deep_quality_analysis.py`

For large datasets (>500K rows), profiling runs take 20–30 minutes. Save the output unconditionally.

Include provenance metadata: source file, timestamp, row counts, profiling methods used.

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

If profiling fails:
1. Read error JSON — check `suggestion` field
2. Read script source to understand the failure mode
3. Inspect first 20 rows to understand data shape
4. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| No numeric columns | All text/categorical data | Use text profiling metrics (length distribution, vocabulary) |
| Shapiro-Wilk fails | Column too large (>5000) | Script auto-samples; check sample size in output |
| MemoryError on heatmap | Too many columns | Use `--columns` to limit scope to relevant columns |
| Profiling very slow | Dataset >1M rows | Use `sample_rows.py` or `load_file.py --nrows 10000` to create a sample; profile the sample first, then run full profiling on targeted columns |
| Empty classification results | Column has no matching patterns | Check column content; try a different `--column` |
| No categories found | Text is too uniform or too unique | Lower `--min-group-size` or try a different `--method` |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Profiling guide | `references/profiling_guide.md` | Unusual results or edge cases |
| Distributions | `references/distribution_interpretation.md` | Extreme skewness or unexpected shapes |

**Do NOT Load** `references/distribution_interpretation.md` for quick quality checks — only needed when distributions show extreme skewness or unexpected shapes that require interpretation guidance.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- After running `detect_all_issues.py` or `deep_quality_analysis.py`, present quality score, anomaly flags, and top findings summary to user. Include: overall score/grade, critical issues count, and 2-3 most impactful findings with sample values. Wait for user direction before proceeding.

### Presenting Findings

After profiling, present findings as structured, actionable proposals:

1. **Categorize findings** into three groups:
   - **Tasks requiring decision** — Quality issues needing user input (sentinel replacement, missing value strategy, format conversion)
   - **Auto-resolvable** — Low-severity items the agent can fix deterministically (whitespace, encoding)
   - **No action needed** — Expected data characteristics, informational flags

2. **Present each decision task** with:
   - Concrete description with numbers (e.g., "42 sentinel values in column X")
   - Sample values from the data
   - Numbered options (e.g., A. Fill via synthesis, B. Drop rows, C. Custom fix)
   - Recommended option with rationale

3. **Wait for user decisions** before proceeding to cleaning/synthesis/transformation

4. **Record decisions** in `logs/analysis_journal.md` using the User Decisions format

### Next-Step Guidance

After presenting the profiling summary, provide next-step guidance:
> Quality score: X/100. I found N issues — here's what stands out:
> 1. [Most impactful finding with concrete numbers]
> 2. [Second finding]
> I'd suggest exploring these further before deciding on a processing plan.

### Workspace Integration
- Update `workspace_state.md` with profiling results (score, grade, key findings).
- Log profiling decisions in `logs/analysis_journal.md`.
