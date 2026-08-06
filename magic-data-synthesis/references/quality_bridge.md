# Quality Bridge — Extracting DD Quality Signals

## Overview

DataDesigner quality signals live inside the generated Parquet columns, not in a separate report file. Two column types carry quality data:

- **Judge columns** (`LLMJudgeColumnConfig`): dict values shaped `{rubric: {score, reasoning}}`
- **Validation columns** (`ValidationColumnConfig`): dict values shaped `{is_valid: bool}`

Use the `extract_dd_quality()` function below to parse these into a structured quality report.

## Extracting Quality

```python
import numpy as np
import pandas as pd

def extract_dd_quality(parquet_path: str) -> dict:
    df = pd.read_parquet(parquet_path)
    report = {"dd_judge": {}, "dd_validation": {}, "rows_passed": len(df)}
    for col in df.columns:
        if col.endswith("_judge_result"):
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) else {}
            for rubric in sample:
                scores = df[col].apply(lambda x: x.get(rubric, {}).get("score", 0) if isinstance(x, dict) else 0)
                max_score = scores.max() or 1
                report["dd_judge"][rubric] = {
                    "mean": float(scores.mean()), "mean_100": float(scores.mean() / max_score * 100),
                    "median": float(scores.median()), "stddev": float(scores.std()), "n": int(len(scores)),
                    "pass_rate": float((scores >= (max_score * 0.6)).mean()),
                }
        elif col.endswith("_validity_result"):
            valid = df[col].apply(lambda x: x.get("is_valid", False) if isinstance(x, dict) else False)
            report["dd_validation"][col] = {"pass_rate": float(valid.mean()), "n_valid": int(valid.sum()), "n_total": len(df)}
    return report
```

Usage:
```python
python -c "
import json; exec(open('extract_quality.py').read())
print(json.dumps(extract_dd_quality('workspace/<project>/ckpt_05_synthesized.parquet'), indent=2))
"
```

## Output Structure

```json
{
  "dd_judge": {
    "ReasoningQuality": {
      "mean": 3.42,
      "mean_100": 85.5,
      "median": 4.0,
      "stddev": 0.71,
      "n": 9500,
      "pass_rate": 0.91,
      "histogram": {"categories": [0, 1, 2, 3, 4], "counts": [12, 45, 210, 2100, 7133]}
    },
    "AnswerCorrectness": { "..." : "..." }
  },
  "dd_validation": {
    "code_validity_result": {
      "pass_rate": 0.94,
      "n_valid": 8930,
      "n_total": 9500
    }
  },
  "rows_passed": 8930
}
```

`mean_100` normalizes raw scores to a 0–100 scale: `mean / max_score * 100`.

## Interpreting Judge Scores (mean_100)

| mean_100 | Interpretation | Action |
|---|---|---|
| ≥ 70 | Good — meets quality bar | Deliver as-is |
| 60–69 | Acceptable — minor quality issues | Deliver with note, or filter low rows |
| < 60 | Below bar — regenerate or filter heavily | Filter to rows with score ≥ threshold, then assess count |

These thresholds match the MAGIC release gates (≥70 for standard E2E, ≥60 for exploratory pipelines).

## Multi-Rubric Scoring

All rubrics on a single `LLMJudgeColumnConfig` are evaluated in **one LLM call per row**. Adding more rubrics (more `dd.Score` entries) increases output tokens per row but does NOT add LLM calls.

Scores are stored as a nested dict in the judge column:

```
df["reasoning_judge_result"].iloc[0]
# → {"ReasoningQuality": {"score": 4, "reasoning": "..."}, "AnswerCorrectness": {"score": 3, "reasoning": "..."}}
```

Access in Jinja (e.g., for ExpressionColumn extraction):
```jinja2
{{ reasoning_judge_result.ReasoningQuality.score }}
```

Note: `.score` is mandatory — `{{ reasoning_judge_result.ReasoningQuality }}` returns the full dict.

## Validation Columns

`ValidationColumnConfig` produces `{is_valid: bool}` per row. Zero LLM cost — runs a local linter (ruff for Python) or your custom callable.

```python
# Manual extraction (without quality_utils):
valid_mask = df["code_validity_result"].apply(lambda x: x.get("is_valid", False))
pass_rate = valid_mask.mean()
n_valid = valid_mask.sum()
```

## Quality Gate Pattern

Standard post-generation workflow:

```python
# 1. Extract quality report
report = extract_dd_quality("ckpt_05_synthesized.parquet")

# 2. Check thresholds
for rubric, stats in report["dd_judge"].items():
    if stats["mean_100"] < 60:
        print(f"WARN: {rubric} mean_100={stats['mean_100']:.1f} — below threshold")

# 3. Filter low-quality rows if needed
df = pd.read_parquet("ckpt_05_synthesized.parquet")
judge_col = "reasoning_judge_result"
score_col_name = "ReasoningQuality"
scores = df[judge_col].apply(lambda x: x.get(score_col_name, {}).get("score", 0))
df_filtered = df[scores >= 3].copy()  # keep score 3–4 (≥75%)
print(f"Kept {len(df_filtered)}/{len(df)} rows after filtering")

# 4. Drop judge columns before delivery (optional)
df_filtered = df_filtered.drop(columns=[judge_col])
```

## Minimum Sample Size for Stable Mean

Using CLT (σ=20, 95% CI):

| Rows | SE | 95% CI half-width |
|---|---|---|
| 50 | 2.83 | ±5.5 pts |
| **100** | 2.00 | **±3.9 pts (recommended minimum)** |
| 300 | 1.15 | ±2.3 pts |

Always generate at least 100 rows before interpreting `mean_100`. Use n=300 (3 × 100-row preview runs) for gate decisions.

## Implementation

The `extract_dd_quality` function shown above should be implemented inline in your script. It parses judge and validation columns from the generated Parquet file into a structured quality report.
