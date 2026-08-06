---
name: magic-data-cleaning
description: 'Clean data by detecting issues, handling missing values, normalizing strings, and executing cleaning plans. Use when: (1) data has missing values or nulls to impute, (2) text columns need normalization or deduplication, (3) type errors or inconsistent formats need fixing, (4) planning a cleaning strategy before execution. Does NOT handle sentinel/placeholder values requiring LLM — route those to magic-data-synthesis. Trigger keywords: clean, fix nulls, handle missing, normalize, deduplicate, impute, strip whitespace.'
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
  - cleaning
  - missing-values
  - normalization
  - deduplication
  scripts:
  - scripts/detect_issues.py
  - scripts/handle_missing.py
  - scripts/normalize_strings.py
  - scripts/execute_cleaning_plan.py
  - scripts/validate_clean.py
  dependencies:
  - pandas
  - numpy
  when_to_use: 'When data has quality issues to fix. Trigger phrases: clean, fix, handle missing, nulls, duplicates, normalize, standardize, impute, remove outliers, fix data.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "clean this data" / "fix the data quality issues"
- "handle the missing values" / "impute the nulls"
- "normalize the text columns" / "fix the encoding"
- "remove duplicates" / "deduplicate"
- "fix data quality" / "impute nulls" / "standardize text" / "fix encoding"

These produce the SAME behavior as the cleaning workflow.

## When to Use

- Data has missing values, duplicates, type errors, or text issues
- Need to impute missing values or normalize strings
- Need complex multi-step cleaning with domain-specific rules
- After magic-data-profiling reveals quality issues

**When NOT to Use:** Use magic-data-validation for schema validation; use magic-data-transformation for reshaping; use magic-data-synthesis for LLM-based generation, translation, format conversion, or filling sentinel placeholders with meaningful content.

## Data Processing Expertise

### Thinking

Before executing any cleaning operation, ask:

- **Is this a cleaning problem or a synthesis problem?** — If a regex or pandas expression can fix it, it is cleaning. If a human would need to think about what value to fill, it is synthesis (route to `magic-data-synthesis`). Confusing the two wastes effort or produces nonsensical results.
- **What imputation strategy fits this column?** — The right choice depends on both the data type and the missing percentage. Numeric with <5% missing: mean/median is safe. Numeric with 5-30%: KNN preserves correlations. Numeric with >30%: the column is unreliable — consider dropping it. Categorical: mode. Text: drop or LLM fill. See the Imputation Strategy Guide below.
- **Will dropping rows introduce sampling bias?** — Dropping 5% of rows sounds harmless, but if those rows are disproportionately from one category (all from "region=Asia", all from the last month), you silently bias the dataset. Always check the distribution of what you are about to drop before executing.
- **Am I cleaning the symptom or the cause?** — Normalizing strings that were imported with wrong encoding suggests a loading issue, not a cleaning issue. Fixing symptoms without noting the root cause leads to recurring problems. Log the likely cause.
- **What is the cost of this operation?** — Dropping rows is permanent data loss. Imputation is approximation. Neither is free. Be explicit about the trade-off and why you chose it.

### Rules

- **Cleaning vs synthesis boundary**: Regex/pandas expression fixes (whitespace, encoding, type coercion, deduplication) are cleaning. Context-dependent value generation (filling sentinels with meaningful text, translation, HTML-to-markdown) is synthesis — hand off to `magic-data-synthesis`.
- **Incremental cleaning**: Clean in stages, not all at once. After each operation: checkpoint, validate, re-profile. This prevents cascading errors where one bad step corrupts downstream results. If a step makes things worse, roll back to the previous checkpoint.
- **Cleaning plan before execution**: For complex cleaning (multi-column, domain rules, fuzzy matching), generate a cleaning plan JSON specifying each step's operation, target columns, strategy, and reason. Present the plan for review before executing.
- **Mutation ordering**: Never mix deterministic cleaning and LLM synthesis in the same pass. One operation's output may corrupt another's input. Clean deterministic issues first (types, encoding, whitespace), checkpoint, then run synthesis on the cleaned data.
- **When to use LLM**: Deterministic text fixes (whitespace, encoding, casing, deduplication) are always code. Semantic operations (filling sentinel values like "X" or "TBD" with meaningful content, translation, format conversion) require LLM via `magic-data-synthesis`.

### Constraints

- MUST run issue detection before cleaning — you cannot fix what you have not measured; `detect_issues.py` surfaces the full picture before you commit to a strategy
- MUST validate after every cleaning step — compare before/after with `validate_clean.py` to catch regressions (new nulls introduced, row count drift, type changes)
- MUST preserve row count when using imputation strategies — imputation fills values, it does not remove rows; if rows disappear after imputation, something went wrong
- MUST NOT drop >50% of rows without explicit user approval — mass deletion usually signals a wrong strategy rather than genuinely bad data
- MUST NOT modify the source file — always write to a new output path; the original is the rollback point
- MUST NOT use `iterrows()` for cleaning operations — it is orders of magnitude slower than vectorized pandas; use `.apply()`, `.str`, or boolean masks instead
- NEVER drop rows without checking the distribution of what you are dropping — `df[drop_mask].groupby(key_columns).size()` reveals whether the drop is evenly distributed or silently biases the dataset toward one category
- NEVER impute text columns with `mode` — it fills every missing text value with the single most common string, producing nonsensical data; use `drop` for text columns, or route to `magic-data-synthesis` for LLM-based contextual fill
- NEVER assume false-positive nulls do not exist — the word "none" or "null" appearing as legitimate natural-language content (e.g., "none of the above", "null hypothesis") gets detected as a missing value; for text columns with sentence-length content, verify flagged values before bulk-replacing

### Imputation Strategy Guide

| Data Type | Missing % | Recommended | Why |
|-----------|-----------|-------------|-----|
| Numeric | <5% | mean or median | Fast, minimal impact on distribution |
| Numeric | 5-30% | KNN (k=5) | Preserves correlations between columns |
| Numeric | >30% | drop column | Too much imputation introduces noise |
| Categorical | Any | mode | Most common value is statistically safest |
| Text | Any | drop or LLM fill | Use `magic-data-synthesis` for LLM-based contextual fill |

## Seed Patterns

### Detect issues (missing, duplicates, outliers, text)
```python
import pandas as pd
import numpy as np

def detect_issues(df: pd.DataFrame) -> dict:
    issues = {}
    # Missing values by column
    missing = df.isna().sum()
    issues["missing"] = {col: int(n) for col, n in missing.items() if n > 0}
    # Duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        issues["duplicates"] = int(dup_count)
    # Outliers (IQR method on numeric columns)
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR > 0:
            outliers = ((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)).sum()
            if outliers > 0:
                issues.setdefault("outliers", {})[col] = int(outliers)
    return issues
```

### Handle missing values by strategy
```python
import pandas as pd
import numpy as np

def handle_missing(df: pd.DataFrame, col: str, strategy: str = "auto") -> pd.DataFrame:
    if strategy == "auto":
        missing_pct = df[col].isna().mean()
        if pd.api.types.is_numeric_dtype(df[col]):
            strategy = "mean" if missing_pct < 0.05 else "knn" if missing_pct < 0.30 else "drop_col"
        elif df[col].dtype == object:
            unique_ratio = df[col].dropna().nunique() / max(len(df[col].dropna()), 1)
            strategy = "mode" if unique_ratio < 0.5 else "drop_rows"

    if strategy == "mean":
        df[col] = df[col].fillna(df[col].mean())
    elif strategy == "median":
        df[col] = df[col].fillna(df[col].median())
    elif strategy == "mode":
        df[col] = df[col].fillna(df[col].mode()[0])
    elif strategy == "knn":
        from sklearn.impute import KNNImputer
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        df[num_cols] = KNNImputer(n_neighbors=5).fit_transform(df[num_cols])
    elif strategy == "drop_rows":
        df = df.dropna(subset=[col])
    elif strategy == "drop_col":
        df = df.drop(columns=[col])
    return df
```

### Normalize strings (whitespace, casing, unicode)
```python
import unicodedata
import pandas as pd

def normalize_strings(df: pd.DataFrame, columns: list[str] = None,
                      ops: list[str] = None) -> pd.DataFrame:
    ops = ops or ["trim", "whitespace", "unicode"]
    columns = columns or df.select_dtypes(include=["object"]).columns.tolist()
    for col in columns:
        s = df[col].astype(str)
        if "trim" in ops:
            s = s.str.strip()
        if "whitespace" in ops:
            s = s.str.replace(r"\s+", " ", regex=True)
        if "unicode" in ops:
            s = s.apply(lambda x: unicodedata.normalize("NFC", x))
        if "lower" in ops:
            s = s.str.lower()
        df[col] = s
    return df
```

### Cleaning plan execution
```python
import json
import pandas as pd

def execute_cleaning_plan(df: pd.DataFrame, plan_path: str) -> pd.DataFrame:
    with open(plan_path) as f:
        plan = json.load(f)
    for step in plan.get("steps", []):
        op = step["operation"]
        cols = step.get("columns", [])
        if op == "normalize_strings":
            for col in cols:
                df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        elif op == "handle_missing":
            strategy = step.get("strategy", "median")
            for col in cols:
                if strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    df[col] = df[col].fillna(df[col].mode()[0])
        elif op == "deduplicate":
            df = df.drop_duplicates(subset=cols, keep=step.get("keep", "first"))
    return df
```

### Validate cleaning results
```python
import pandas as pd

def validate_cleaning(df_original: pd.DataFrame, df_cleaned: pd.DataFrame) -> dict:
    report = {
        "rows_before": len(df_original),
        "rows_after": len(df_cleaned),
        "row_change_pct": round((len(df_cleaned) - len(df_original)) / len(df_original) * 100, 2),
        "nulls_before": int(df_original.isna().sum().sum()),
        "nulls_after": int(df_cleaned.isna().sum().sum()),
    }
    # Detect new nulls introduced per column
    common = set(df_original.columns) & set(df_cleaned.columns)
    new_nulls = {}
    for col in common:
        orig_n = df_original[col].isna().sum()
        clean_n = df_cleaned[col].isna().sum()
        if clean_n > orig_n:
            new_nulls[col] = int(clean_n - orig_n)
    if new_nulls:
        report["new_nulls_introduced"] = new_nulls
    report["valid"] = len(new_nulls) == 0 and report["row_change_pct"] > -10
    return report
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `detect_issues.py` | A | `python3 detect_issues.py data.csv report.json` | `--chunk-size N` for files over 500K rows |
| `handle_missing.py` | A | `python3 handle_missing.py data.csv cleaned.csv` | `--strategy median\|knn` for specific imputation; `--columns col1,col2` to restrict scope. Auto thresholds: >50% missing → drop col, <100K rows → KNN, ≥100K → median |
| `normalize_strings.py` | A | `python3 normalize_strings.py data.csv normalized.csv` | `--operations trim,encoding` to run subset; `--columns col1,col2` to restrict. Default: all 4 ops (trim, encoding fix, whitespace, unicode NFC) on all string cols |
| `validate_clean.py` | A | `python3 validate_clean.py original.csv cleaned.csv report.json` | `--input-format` when both files are non-CSV. Note: format flag applies to BOTH files |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `execute_cleaning_plan.py` | Plan-driven multi-step cleaning | JSON plan with per-column strategies; KNN with sklearn/median fallback; `--explain` dry-run pattern; 20-pattern mojibake map |

Scripts accept `--input-format` (auto/csv/tsv/jsonl/json/parquet/excel) and `--output-format`.

## Cleaning vs Synthesis Boundary

When an issue is detected, decide whether it is a cleaning task or a synthesis task:

| Signal | Route To | Rule of Thumb |
|--------|----------|--------------|
| Missing numeric values | Cleaning | Calculable fill (mean, median, KNN) |
| Whitespace, encoding, case issues | Cleaning | Deterministic text fixes |
| Duplicates | Cleaning | Row-level deduplication |
| Sentinel values ("X", "N/A", "TBD") | Synthesis (`magic-data-synthesis`) | LLM generates meaningful replacements |
| Missing text content | Synthesis (`magic-data-synthesis`) | A human would need context to fill it |
| Format conversion (HTML to markdown) | Synthesis (`magic-data-synthesis`) | Structure-preserving transformation |

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For cleaning specifically:** Cleaning involves irreversible mutations (dropping rows, overwriting values). The judgment here almost always lands on "yes, checkpoint":

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| Before first cleaning pass | **Always** | Preserves raw loaded state for rollback |
| After each distinct cleaning op when chained | **Yes** | Allows rolling back one step without losing others |
| Quick single-column fix on small data | **Skip** | Recovery is cheap, next step is safe |
| Before destructive operation (drop rows, dedup) | **Always** | Preserve pre-op state for rollback |

Incremental cleaning principle: checkpoint → clean → validate → next operation.

**Suggested names:** `cleaned_missing.parquet`, `cleaned_normalized.parquet`, `corpus_cleaned.jsonl`

Include provenance metadata: operations applied, rows affected, before/after null counts and row counts.

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

If cleaning fails:
1. Read error JSON — check `suggestion` field
2. Read script source to understand the failure mode
3. Inspect data with `detect_issues.py` to understand the root cause
4. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| TypeError in imputation | "N/A" strings in numeric column | Pre-clean with `normalize_strings.py` to remove null-like strings, then impute |
| KNN memory error | Dataset too large for KNN | Use `--strategy median` instead of KNN; median has constant memory |
| All values dropped | Drop threshold too aggressive | Lower the threshold or switch to imputation instead of dropping |
| False positive nulls in text | "none"/"null" as legitimate text content | Use context-aware null detection; check if value appears as standalone vs. within longer text |
| Type inconsistency after clean | Imputation changed column dtype | Verify types with `validate_clean.py`; cast back to original dtype if needed |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Imputation strategies | `references/imputation_strategies.md` | Choosing between imputation methods |
| Edge cases | `references/edge_cases.md` | Unusual data formats or cleaning failures |
| Domain patterns | `references/domain_patterns.md` | Financial, date/time, text dedup, address/name, encoded values |

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- **Cleaning plan approval**: After issue detection and before execution, present the cleaning plan with: issues found per column, proposed strategy (impute/drop/normalize/synthesize), and estimated impact (rows affected, data loss). Wait for user approval before executing.
- **Validation review**: If validation shows unexpected changes (row count changed >5%, new nulls introduced, quality score decreased), present before/after comparison and ask user to confirm or roll back.

### Workspace Integration
- Update `workspace_state.md` with cleaning results (strategies used, rows affected, before/after quality scores).
- Log cleaning decisions in `logs/analysis_journal.md` — what was cleaned, which strategy, rows affected, and before/after metrics.
