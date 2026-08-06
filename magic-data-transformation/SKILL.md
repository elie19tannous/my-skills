---
name: magic-data-transformation
description: 'Transform data by reshaping, aggregating, merging, deriving columns, and delivering to external destinations (database, HuggingFace Hub). Use when: (1) pivoting, melting, or unpivoting tables, (2) grouping and aggregating data, (3) joining or merging multiple datasets, (4) creating calculated or derived columns, (5) uploading/delivering/pushing data to HuggingFace Hub or database. Trigger keywords: pivot, melt, reshape, groupby, aggregate, merge, join, vlookup, deliver, upload, HuggingFace, push to Hub.'
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
  - transformation
  - reshape
  - aggregate
  - merge
  - join
  scripts:
  - scripts/reshape.py
  - scripts/aggregate.py
  - scripts/merge_datasets.py
  - scripts/derive_columns.py
  - scripts/validate_transform.py
  - scripts/deliver_to_db.py
  - scripts/deliver_to_hf.py
  dependencies:
  - pandas
  - numpy
  when_to_use: 'When reshaping, joining, or deriving data. Trigger phrases: transform, reshape, pivot, melt, merge, join, aggregate, group by, derive column, split dataset, convert format, instruction tuning.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "pivot this data" / "reshape the table"
- "merge these datasets" / "join the tables"
- "aggregate by group" / "group by and sum"
- "create a calculated column" / "derive a new field"
- "unpivot" / "wide to long" / "long to wide" / "vlookup" / "cross tab"
- "upload to HuggingFace" / "push to HF Hub" / "deliver to HuggingFace"
- "publish dataset to Hub" / "create HF repo"

These produce the SAME behavior as the transformation workflow.

## When to Use

- Need to pivot, melt, stack, or unstack data
- Need group-by aggregations
- Need to merge/join multiple datasets
- Need to create calculated or derived columns
- After magic-data-cleaning, before analysis

**When NOT to Use:** Use magic-data-cleaning for quality fixes; use magic-data-exploration for analysis.

## Data Processing Expertise

### Thinking

Before transforming data, ask:
- **What shape does the downstream consumer need?** — Reports need wide format; ML models often need long format. Reshape to match the destination, not to satisfy an intermediate preference.
- **Am I changing the grain?** — Aggregation reduces rows (detail to summary); melt increases rows (wide to long). Track row count before and after to verify the transform worked correctly. A 1000-row table melted across 4 value columns should produce exactly 4000 rows.
- **What order should I apply transforms?** — Type cast first so join keys match and aggregation columns are numeric. Join before filtering so you have full context. Filter before expensive aggregations. Derive columns after joins so all source data is available. Aggregate after all columns exist. Reshape last for final output format.
- **Will this join explode?** — Before any merge, check cardinality. If the join key has duplicates in both tables, you get a many-to-many cartesian product. A 1000-row left table joined to a 500-row right table where each side has 10 duplicates on the key produces 100,000 rows, not 1000.
- **Can I verify the result?** — After any transform, spot-check: do the numbers add up? Are join keys preserved? Did row counts change as expected? A group-by sum should equal the original column total.

### Rules

- **Transformation ordering**: Type cast → join/merge → filter → derive columns → aggregate → reshape. This ordering prevents type mismatches on join keys, ensures all columns are available for derivation, and reshapes only after all data is finalized. Adapt when the specific task demands it — this is guidance, not a rigid sequence.
- **Grain change awareness**: Every operation that changes row count must report `rows_in` vs `rows_out`. Aggregation should reduce rows. Melt multiplies rows by the number of value columns. Pivot reduces rows. If the direction is wrong, the transform logic has a bug.
- **Join explosion detection**: Before merging, check `df[key].duplicated().sum()` on both sides. If both have duplicates, you have a many-to-many join — aggregate or deduplicate one side first. After merging, verify `rows_out <= 2 * max(rows_left, rows_right)`; if violated, flag as explosion.
- **Conditional mapping**: Use `np.where` chains for multi-branch categorical logic (SQL CASE/WHEN equivalent). Use `pd.eval()` for arithmetic and simple single-condition derivations. Never use raw `eval()`.
- **Aggregation grain**: When aggregating, verify that the group-by columns define the intended grain. If you group by `[region]` but need `[region, product]`, you lose product-level detail silently. Check output row count against expected number of groups.
- **Reshape guidance**: Pivot requires unique (index, columns) pairs — deduplicate or aggregate first. Melt is the inverse: it creates NaN for value columns that had no data in the original wide format; these structural NaNs are expected, not data quality issues.
- **When to use LLM**: Data transformation is deterministic — use code, not LLM. If a derived column requires semantic interpretation (categorizing free text into buckets, extracting entities from descriptions), hand off to `magic-data-synthesis`. Regex-based string extraction and numeric derivations stay in transformation code.

### Constraints

- MUST track row count changes (`rows_in` vs `rows_out`) for every operation
- MUST validate transform output before checkpointing — check shape, key columns, null patterns. For schema-level validation (type constraints, value ranges, business rules), hand off to `magic-data-validation`
- MUST cast join keys to the same type before merging (`df['id'] = df['id'].astype(str)`)
- MUST report `shape_before` and `shape_after` for every reshape operation
- MUST NOT use chained indexing — use `.loc[]` instead
- MUST NOT use `iterrows()` or `apply()` on large DataFrames (>10K rows) — use vectorized operations
- MUST NOT allow silent join explosions without warning the user
- MUST NOT use raw `eval()` — only `pd.eval()` for safe expression evaluation
- NEVER join without checking cardinality first — a many-to-many join silently produces a cartesian product that can exhaust memory
- NEVER pivot without deduplicating — duplicate (index, columns) pairs raise ValueError or silently pick the last value
- NEVER aggregate without confirming the group-by grain matches the intended output — grouping by too few columns silently drops detail

## Seed Patterns

### Reshape: pivot and melt
```python
import pandas as pd

# Pivot: long to wide (requires unique index+columns pairs)
df_deduped = df.drop_duplicates(subset=[index_col, columns_col])
wide = df_deduped.pivot(index=index_col, columns=columns_col, values=values_col)
wide = wide.reset_index()
if isinstance(wide.columns, pd.MultiIndex):
    wide.columns = ['_'.join(map(str, c)).strip('_') for c in wide.columns]

# Melt: wide to long (inverse of pivot)
long = pd.melt(df, id_vars=['name', 'region'],
               value_vars=['q1_sales', 'q2_sales', 'q3_sales', 'q4_sales'],
               var_name='quarter', value_name='sales')
# Expected: rows_out == rows_in * len(value_vars)
```

### Aggregate: group-by with multiple functions
```python
import pandas as pd
import numpy as np

# Group-by with multiple aggregation functions
agg_dict = {
    'revenue': ['sum', 'mean', 'count'],
    'quantity': ['sum', 'min', 'max'],
}
result = df.groupby(['region', 'category']).agg(agg_dict).reset_index()
# Flatten multi-level columns
result.columns = ['_'.join(map(str, c)).strip('_') for c in result.columns]
# Verify: result row count == number of unique (region, category) pairs
assert len(result) == df.groupby(['region', 'category']).ngroups
```

### Merge: join with explosion check
```python
import pandas as pd

def safe_merge(left, right, on, how='left'):
    # Pre-merge cardinality check
    left_dups = left[on].duplicated().sum()
    right_dups = right[on].duplicated().sum()
    if left_dups > 0 and right_dups > 0:
        raise ValueError(
            f"Many-to-many join detected on '{on}': "
            f"{left_dups} left dups, {right_dups} right dups. "
            f"Deduplicate one side first."
        )
    # Cast join keys to same type
    left[on] = left[on].astype(str)
    right[on] = right[on].astype(str)
    result = pd.merge(left, right, on=on, how=how, indicator=True)
    # Post-merge explosion check
    if len(result) > 2 * max(len(left), len(right)):
        raise ValueError(f"Join explosion: {len(result)} rows from {len(left)}+{len(right)} inputs")
    return result
```

### Derive: conditional column mapping
```python
import numpy as np

# np.where chain: SQL CASE/WHEN equivalent
# Each np.where(condition, value_if_true, value_if_false) is one branch.
# Chain by nesting another np.where as the else clause.
df['grade'] = np.where(df['score'] >= 90, 'excellent',
              np.where(df['score'] >= 70, 'good',
              np.where(df['score'] >= 50, 'average',
                       'poor')))

# Arithmetic derivation via pd.eval (safe, no raw eval)
df['profit_margin'] = pd.eval('(revenue - cost) / revenue', local_dict={'revenue': df['revenue'], 'cost': df['cost']})
```

### Validate: post-transform integrity check
```python
import pandas as pd

def validate_transform(original, transformed, key_columns=None):
    report = {'shape_before': original.shape, 'shape_after': transformed.shape}
    # Check for unexpected new nulls
    for col in set(original.columns) & set(transformed.columns):
        orig_nulls = original[col].isna().sum()
        new_nulls = transformed[col].isna().sum()
        if new_nulls > orig_nulls:
            report.setdefault('warnings', []).append(
                f"Column '{col}': {new_nulls - orig_nulls} new nulls introduced"
            )
    # Key column preservation
    if key_columns:
        for col in key_columns:
            if col not in transformed.columns:
                report.setdefault('errors', []).append(f"Key column '{col}' missing")
    report['valid'] = 'errors' not in report
    return report
```

## Database Delivery

### Domain Knowledge

When delivering transformed data to a database:

- **Write modes**: `append` (INSERT rows), `replace` (DROP + CREATE + INSERT), `upsert` (not yet implemented — use append with deduplication)
- **PAUSE gate**: ALL database writes require explicit confirmation. The `confirm_write()` function must fire before any write operation. This is non-negotiable — even in autonomous mode.
- **Schema validation**: Before writing, validate that DataFrame columns match the target table schema. Report missing columns, extra columns, and type mismatches.
- **Read-only override**: Database connections are read-only by default. Writes require explicitly creating a connection with `read_only=False`.

### Delivery Code Pattern

```python
from sqlalchemy import create_engine
import pandas as pd

def deliver_to_db(df, env_var, table, mode="append"):
    engine = create_engine(os.environ[env_var])  # NOT read-only
    # Validate schema compatibility first
    # PAUSE: confirm before writing
    print(f"⚠️  WRITE: {len(df)} rows → {table} (mode={mode})")
    df.to_sql(table, engine, if_exists=mode, index=False)
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Callable tools** -- call directly via CLI:

| Script | Purpose | CLI usage |
|--------|---------|-----------|
| `deliver_to_db.py` | Write transformed data to database table | `python3 deliver_to_db.py --input data.parquet --table target_table` (accepts Parquet only, not CSV) |
| `deliver_to_hf.py` | Publish dataset to HuggingFace Hub | `python3 deliver_to_hf.py --input dataset_folder/ --repo org/repo-name` (`--input` expects a folder path, not a single file) |

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `validate_transform.py` | A | `python3 validate_transform.py original.csv transformed.csv report.csv` (note: 3 positional args — original, transformed, output) | `--expected-shape rows,cols` for dimensional assertion; `--key-columns id,date` to verify key preservation |
| `aggregate.py` | B | `python3 aggregate.py data.csv agg.csv --group_cols region --agg_cols revenue --functions mean,sum,count` | `--group_cols` and `--agg_cols` are functionally required; `--explain` for dry-run |
| `merge_datasets.py` | B | `python3 merge_datasets.py left.csv right.csv merged.csv --on customer_id --how left` | `--on` is functionally required (without it, joins on all shared columns → explosion risk); `--left-on`/`--right-on` when key names differ |
| `reshape.py` | B | `python3 reshape.py data.csv reshaped.csv --operation pivot --index_col date --columns_col region --values_col revenue` | `--operation` defaults to `pivot`, but pivot hard-fails without `--index_col`/`--columns_col`. Note: `--operation stack\|unstack` need only input/output (no column params) |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `derive_columns.py` | Safe expression evaluation for computed columns | Safe `pd.eval()` sandbox; blocked unsafe patterns; `--expressions` is effectively required |

Scripts accept `--input-format` and `--output-format` (auto/csv/tsv/jsonl/json/parquet/excel).

## HuggingFace Delivery

### When to Use
- User wants to publish processed data to HuggingFace Hub
- Need to push a dataset repo with proper metadata and dataset card
- Need to create a PR-based upload for team review

### Thinking
Before delivering to HuggingFace, ask:
- **What visibility?** — Default to private. Only make public if the user explicitly requests it. Gated access requires manual setup after creation.
- **Does a dataset card exist?** — If not, generate one with `generate_dataset_card.py` (from `magic-data-loading` scripts) before uploading.
- **Batch or incremental?** — Use batch (default) for final deliveries. Use incremental for checkpoint pushes.

### Callable Scripts

| Script | Purpose | CLI usage |
|--------|---------|-----------|
| `deliver_to_hf.py` | Upload folder to HF dataset repo | `python3 deliver_to_hf.py --input data/output/ --repo org/name [--private] [--create-pr] [--yes]` |

### PAUSE Gate (Defense in Depth)

Uploads to HuggingFace are **irreversible for public repos**. Two layers of protection:

1. **SKILL.md layer (you):** Before calling `deliver_to_hf.py`, present the upload plan to the user:
   - Repository name and visibility
   - Files to upload (count and total size)
   - Whether this creates a new repo or updates existing
   Ask for explicit confirmation before proceeding.

2. **Script layer:** `deliver_to_hf.py` has a built-in `--confirm` prompt. Only bypass with `--yes` when the user has already confirmed in step 1.

### Callable Tool Pipeline Pattern

When writing pipeline inline code (not calling the script), use this library call directly:

```python
# deliver_to_hf.py pattern
from huggingface_hub import HfApi
api = HfApi()
api.create_repo("org/name", repo_type="dataset", private=True, exist_ok=True)
api.upload_folder(folder_path="data/output/", repo_id="org/name", repo_type="dataset")
```

### Visibility Options
- `--private` (default) — only you and collaborators can see it
- `--public` — anyone can access; requires dataset card
- `--gated` — listed publicly but requires access approval
- `--create-pr` — creates a draft PR instead of direct push (for team review)

### Workflow
1. Confirm destination repo name and visibility with user
2. Generate dataset card: `generate_dataset_card.py --input data.parquet --repo org/name`
3. Upload: `deliver_to_hf.py --input data/output/ --repo org/name --private`
4. Report: share the Hub URL with the user

### Constraints
- MUST confirm visibility with user before uploading (PAUSE gate)
- MUST generate a dataset card before uploading to public/gated repos
- MUST default to --private for new repos
- MUST NOT upload without user confirmation unless in autonomous mode with --yes
- MUST NOT include credentials in dataset cards or commit messages

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For transformation specifically:**

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After join/merge | **Always** | Joins can explode row counts silently; save to inspect |
| After aggregation | **Always** | Aggregation is lossy — pre-agg data is gone |
| After column derivation | **Optional** | Derivation is cheap to re-run; skip if next step is also cheap |
| After reshape (pivot/melt) | **Yes** | Pivots can fail on re-run if upstream data changes |
| Multi-step transformation chain | **Yes** at each boundary | Restartability matters |

**Suggested names:** `merged.parquet`, `aggregated_by_region.parquet`, `transformed.jsonl`

Include provenance metadata: operations applied, shape before/after, columns added/removed.

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

If a transformation fails:
1. Read error JSON — check `suggestion` field
2. Read the script source to understand the failure mode
3. Inspect input data shape and column names before retrying
4. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Join explosion (rows_out >> rows_in) | Many-to-many join | Check join key uniqueness on both sides, deduplicate or aggregate one side first, use left join |
| Pivot ValueError | Duplicate index entries | Aggregate first (`groupby().first()` or `.mean()`), then pivot |
| KeyError on column | Column name mismatch | Check column names with `df.columns.tolist()`, watch for whitespace |
| Type mismatch on join | int vs string IDs | Cast both join keys to same type: `df['id'] = df['id'].astype(str)` |
| Null count increases after melt | Structural NaN from reshape | This is expected behavior — melt creates NaN for value columns with no data in the original wide format. Do not impute unless the nulls represent genuinely missing data. |
| MemoryError during merge | Dataset too large for in-memory join | Use chunked processing or filter before joining |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Pandas operations | `references/pandas_operations.md` | Complex groupby, merging, or performance issues |
| Join patterns | `references/join_patterns.md` | Join explosion or choosing join type |
| Performance patterns | `references/performance_patterns.md` | Large data (>1M rows), window functions, memory optimization |

**Do NOT Load** `references/join_patterns.md` for simple derive_columns or aggregate operations — only needed for merge/join tasks. **Do NOT Load** `references/performance_patterns.md` for datasets under 100K rows.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- If a planned transformation would change row count by >2x (pivot explosion, melt from wide to long, many-to-many join), present the expected shape change and impact before proceeding.

### Workspace Integration
- Update `workspace_state.md` with transformation results (operation, shape before/after, columns added).
- Log transformation decisions in `logs/analysis_journal.md` — what was transformed, why, and the row count before/after.
