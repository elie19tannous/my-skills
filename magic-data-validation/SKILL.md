---
name: magic-data-validation
description: Validate datasets against inferred or custom schemas, check cross-column constraints, detect sentinel/placeholder values, and catch statistical pitfalls (Simpson's paradox, join explosion). Use when verifying data quality after cleaning, enforcing schemas before delivery, checking for content placeholders, or sanity-checking transformation results.
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
  - validation
  - schema
  - constraints
  - pitfalls
  scripts:
  - scripts/infer_schema.py
  - scripts/validate_schema.py
  - scripts/check_constraints.py
  - scripts/content_validator.py
  - scripts/sanity_check.py
  - scripts/validate_statistics.py
  dependencies:
  - pandas
  - numpy
  when_to_use: 'When verifying data correctness or enforcing rules. Trigger phrases: validate, check format, verify schema, enforce constraints, check for placeholders, sanity check, data quality rules.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "validate this data" / "check the schema"
- "verify data quality" / "run sanity checks"
- "check constraints" / "enforce the schema"
- "are there any data issues left?"
- "check for pitfalls" / "detect sentinels" / "verify schema" / "is this data ready for modeling" / "content quality check"

These produce the SAME behavior as the validation workflow.

## When to Use

- After data cleaning, verify data quality
- Need to infer or enforce a schema
- Need cross-column constraint checking
- Need to detect statistical pitfalls (join explosion, Simpson's paradox, etc.)

**When NOT to Use:** Use magic-data-cleaning to fix issues; use magic-data-profiling for exploration.

## Data Processing Expertise

### Thinking

Before validating, ask:
- **Fitness for what use?** — Validation criteria depend on downstream use. A dataset feeding a dashboard has different quality thresholds than one training a model. Define what "valid" means for THIS use case before writing a single rule.
- **What's the cost of false positives vs. false negatives?** — Overly strict validation rejects good data (FP); overly lenient validation lets bad data through (FN). A pipeline that drops 30% of valid records because of one tight constraint is worse than one that lets a few edge cases through. Calibrate strictness to the use case.
- **Am I validating clean or dirty data?** — Validating before cleaning catches issues to fix; validating after cleaning verifies fixes worked. Both are valuable but serve different purposes. Know which you are doing.
- **Does the inferred schema match the target schema?** — An inferred schema reflects what IS in the data, not what SHOULD BE. A column inferred as `text` may be a malformatted `numeric`. Review and adjust inferred schemas against the intended target schema before enforcing them.
- **What validation ordering?** — Run checks from cheapest to most expensive: schema (structural) first, then constraints (rule-based), then content (semantic), then sanity (statistical). Each layer catches issues the previous one misses.

### Rules

- **Validation ordering**: Always follow schema -> constraints -> content -> sanity. Schema validation is fast and catches structural issues. Content validation is slower and catches semantic issues. Running sanity checks before fixing schema violations wastes effort on data that will change.
- **Fitness-for-use drives strictness**: A model training dataset can tolerate 1-2% nulls in non-target columns; a financial reporting dataset cannot tolerate any. Define acceptable thresholds per column per use case, not globally.
- **Inferred schema != target schema**: Inferred schemas describe what exists. Target schemas describe what should exist. Always compare inferred against target and reconcile before enforcing. A column of zip codes inferred as `numeric` will lose leading zeros if enforced as integers.
- **Constraint types**: Range constraints (min/max for numerics), enum constraints (allowed values for categoricals), pattern constraints (regex for text like emails/phones), cross-column constraints (start_date < end_date), and uniqueness constraints (primary keys). Match constraint type to column semantics.
- **Content validation for text columns**: Schema validation checks type and length but cannot detect sentinel strings like "N/A", "TBD", "placeholder", or single-space strings that are semantically empty. Always run content validation on text columns separately.
- **When to use LLM**: Schema checking, constraint evaluation, and statistical sanity checks are deterministic -- use code, not LLM. Content validation of free-text fields (detecting nonsense text, placeholder prose, machine-generated filler) may benefit from LLM-based analysis via `magic-data-synthesis`. Use LLM only when regex/pattern-based detection is insufficient.

### Constraints

- MUST validate in order: schema -> constraints -> content -> sanity -- each layer depends on the previous being clean
- MUST always run sanity_check on analysis results to catch statistical pitfalls
- MUST validate after any transformation -- transformations introduce new failure modes (type coercion errors, join explosions, aggregation artifacts)
- MUST NOT infer schema from a sample and enforce in strict mode -- sampling bias produces schemas that silently reject valid production data; always infer from the full dataset, or review and loosen constraints manually before enforcing
- MUST NOT skip content validation on text columns just because schema passes -- schema checks type and length; it will not catch "N/A", "TBD", "placeholder", or single-space strings
- NEVER apply numeric validation rules to text columns -- this produces 100% failure rates that look like catastrophic data quality; check column types first; use content validation for text columns
- NEVER ignore pitfall warnings from sanity_check -- Simpson's paradox and join explosion silently invalidate downstream analysis; investigate every warning even if the data "looks fine" in aggregate
- NEVER infer schema from only the first few rows -- sampling bias produces a schema that does not represent the full dataset; use `infer_schema.py` on the full dataset or a representative stratified sample

## Seed Patterns

### Schema inference
```python
import pandas as pd
import numpy as np

def infer_schema(df: pd.DataFrame, strict: bool = False) -> dict:
    schema = {}
    for col in df.columns:
        s = df[col].dropna()
        if pd.api.types.is_numeric_dtype(df[col]):
            dtype = "numeric"
            constraints = {"min": float(s.min()), "max": float(s.max())}
        elif s.nunique() / max(len(s), 1) < 0.05 or s.nunique() <= 20:
            dtype = "categorical"
            constraints = {"allowed_values": s.unique().tolist()}
        else:
            dtype = "text"
            constraints = {"max_length": int(s.astype(str).str.len().max())}
        schema[col] = {
            "dtype": dtype,
            "nullable": bool(df[col].isnull().any()),
            "constraints": constraints,
        }
    return schema
```

### Schema validation against target
```python
import pandas as pd

def validate_schema(df: pd.DataFrame, schema: dict) -> list[dict]:
    violations = []
    for col, spec in schema.items():
        if col not in df.columns:
            violations.append({"column": col, "issue": "missing_column"})
            continue
        if not spec.get("nullable", True) and df[col].isnull().any():
            null_count = int(df[col].isnull().sum())
            violations.append({"column": col, "issue": "unexpected_nulls",
                               "count": null_count})
        if spec["dtype"] == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
            violations.append({"column": col, "issue": "type_mismatch",
                               "expected": "numeric", "actual": str(df[col].dtype)})
    return violations
```

### Constraint checking (range, enum, pattern)
```python
import pandas as pd
import re

def check_constraints(df: pd.DataFrame, schema: dict) -> list[dict]:
    violations = []
    for col, spec in schema.items():
        if col not in df.columns:
            continue
        c = spec.get("constraints", {})
        s = df[col].dropna()
        if "min" in c and pd.api.types.is_numeric_dtype(s):
            below = s[s < c["min"]]
            if len(below):
                violations.append({"column": col, "rule": "min",
                                   "count": len(below), "sample": below.head(5).tolist()})
        if "max" in c and pd.api.types.is_numeric_dtype(s):
            above = s[s > c["max"]]
            if len(above):
                violations.append({"column": col, "rule": "max",
                                   "count": len(above), "sample": above.head(5).tolist()})
        if "allowed_values" in c:
            invalid = s[~s.isin(c["allowed_values"])]
            if len(invalid):
                violations.append({"column": col, "rule": "enum",
                                   "count": len(invalid), "sample": invalid.head(5).tolist()})
        if "pattern" in c:
            non_match = s[~s.astype(str).str.match(c["pattern"])]
            if len(non_match):
                violations.append({"column": col, "rule": "pattern",
                                   "count": len(non_match), "sample": non_match.head(5).tolist()})
    return violations
```

### Content validation (sentinel and placeholder detection)
```python
import pandas as pd

SENTINELS = {"N/A", "n/a", "NA", "TBD", "TODO", "placeholder", "test",
             "null", "none", "undefined", "missing", "-", "--", "...", " "}

def validate_content(df: pd.DataFrame, text_cols: list[str],
                     min_length: int = 3) -> list[dict]:
    issues = []
    for col in text_cols:
        s = df[col].dropna().astype(str)
        # Sentinel detection
        sentinel_mask = s.isin(SENTINELS)
        if sentinel_mask.any():
            issues.append({"column": col, "issue": "sentinel_values",
                           "count": int(sentinel_mask.sum()),
                           "examples": s[sentinel_mask].unique()[:5].tolist()})
        # Short content detection
        short_mask = s.str.len() < min_length
        if short_mask.any():
            issues.append({"column": col, "issue": "short_content",
                           "count": int(short_mask.sum()),
                           "threshold": min_length})
    return issues
```

### Sanity check (statistical plausibility)
```python
import pandas as pd
import numpy as np

def sanity_check(df: pd.DataFrame) -> list[dict]:
    warnings = []
    row_count = len(df)
    for col in df.select_dtypes(include=[np.number]).columns:
        s = df[col].dropna()
        if len(s) == 0:
            continue
        # Order-of-magnitude outlier
        if s.median() != 0 and s.max() > 1000 * s.median():
            warnings.append({"pitfall": "magnitude_outlier", "column": col,
                             "detail": f"max ({s.max():.2f}) > 1000x median ({s.median():.2f})"})
    # Join explosion risk: near-unique columns
    for col in df.columns:
        if df[col].nunique() / row_count > 0.95 and row_count > 100:
            warnings.append({"pitfall": "join_explosion", "column": col,
                             "detail": f"{df[col].nunique()}/{row_count} unique values"})
    # Simpson's paradox: check if correlation reverses within groups
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if len(num_cols) >= 2 and cat_cols:
        c1, c2 = num_cols[0], num_cols[1]
        overall = df[[c1, c2]].corr().iloc[0, 1]
        for gc in cat_cols[:2]:
            if 2 <= df[gc].nunique() <= 10:
                for name, g in df.groupby(gc):
                    if len(g) > 20:
                        group_corr = g[[c1, c2]].corr().iloc[0, 1]
                        if not np.isnan(group_corr) and np.sign(overall) != np.sign(group_corr):
                            warnings.append({"pitfall": "simpsons_paradox",
                                             "columns": [c1, c2], "group": gc})
                            break
    return warnings
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `infer_schema.py` | A | `python3 infer_schema.py --input data.csv --output schema.json` | `--strict` for p5-p95 bounds and ±10% row range (production schema gates) |
| `content_validator.py` | A | `python3 content_validator.py data.csv report.json` | `--distribution-check` for length variance anomalies; `--group-by col` for per-group breakdown; `--depth deep` for thorough inspection; `--sentinel-values X,TODO` for custom list |
| `validate_schema.py` | B | `python3 validate_schema.py --input data.csv --schema schema.json --output report.json` | `--explain` for per-violation explanations. Schema from `infer_schema.py` or hand-authored |
| `sanity_check.py` | A | `python3 sanity_check.py --input data.csv --output sanity.json` | No selective detector flags — runs all 7 pitfalls (join explosion, survivorship bias, Simpson's paradox, look-ahead, selection bias, metric gaming, ecological fallacy) |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `check_constraints.py` | Cross-column constraint checking | Typed constraint dispatching (comparison, vocabulary, conditional_null, unique_together); requires hand-authored constraints JSON |
| `validate_statistics.py` | Internal consistency of statistical results | Requires cross-skill artifact (`descriptive_stats.py` JSON output); tolerance-gated stat comparison |

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For validation specifically:**

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After schema validation | **Yes** | Captures validation state; report is a deliverable |
| After constraint checking | **Yes** | Constraint violations are the output — save them |
| After content validation (sentinel/placeholder detection) | **Yes** | Results inform cleaning decisions |
| After sanity checks (Simpson's paradox, join explosion) | **Yes** | Sanity findings are expensive to reproduce |
| Quick inline validation before next step | **Skip** | Recovery is trivial |

**Suggested names:** `validated_schema.json`, `constraint_report.json`, `content_issues.json`, `sanity_report.json`

Include metadata: source file validated, timestamp, validation type, pass/fail summary.

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

If validation fails unexpectedly:
1. Read error output -- check for `suggestion` field in JSON reports
2. Read the relevant script source to understand the failure mode
3. Inspect the data with sampling before re-running

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Schema mismatch | Data changed after schema inferred | Re-infer schema on current data |
| Missing constraint file | Not generated yet | Run `infer_schema.py --strict` first |
| 100% column failure rate | Numeric rules applied to text column | Check column dtype; use content_validator for text |
| All rows flagged as short content | CJK text with `min_content_length=3` | Enable `--cjk-aware` (default) which uses `min_content_length=1` for CJK-dominant columns |
| Constraint file format error | Hand-edited JSON with syntax error | Validate JSON before passing to check_constraints |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Common pitfalls | `references/common_pitfalls.md` | Pitfall detected in sanity_check |
| Schema format | `references/schema_format.md` | Creating custom schemas |
| Domain validation | `references/domain_validation.md` | MANDATORY -- before defining constraints or reviewing schema |

**Do NOT Load** `references/common_pitfalls.md` unless sanity_check.py flags a specific pitfall. **Do NOT Load** `references/schema_format.md` when using inferred schemas -- only needed when creating custom schemas from scratch.

## Triggered by Findings

This skill is often invoked after findings presentation or as part of the lifecycle validation phase. When routed here from a findings decision:

| Findings Action | Validation Approach |
|----------------|-------------------|
| Schema issues -> VALIDATE | Schema inference + validation against target |
| Constraint violations | Constraint checking with domain-specific rules |
| Post-transform verification | Sanity check to detect pitfalls |
| Content quality check | Content validation for sentinel and content length scanning |

Validation often triggers further routing -- schema issues may route to `magic-data-transformation`, content issues may route to `magic-data-cleaning` or `magic-data-synthesis`.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- If schema inference produces type warnings (ambiguous column types, nullable conflicts, unexpected inferred types), present warnings and proposed schema to user for review before enforcing validation.

### Workspace Integration
- Update `workspace_state.md` with validation results.
- Log validation decisions in `logs/analysis_journal.md`.
- Store all validation reports in `logs/` alongside the data they validate. Name reports descriptively (e.g., `validation_post_cleaning.json`, `schema_check_v2.json`) so the agent can track validation history across the lifecycle.
