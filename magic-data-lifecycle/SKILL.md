---
name: magic-data-lifecycle
description: 'Routing and orchestration knowledge for data processing tasks. Provides pipeline ordering (load → profile → clean → transform → validate → deliver), skill routing table (which magic-data-* skill handles which operation), quality gating guidance, and checkpoint strategy. Read this skill to understand how data processing phases connect and which skill to invoke for each step. Use when: the task involves multiple data operations, you need to decide which skill handles a specific operation, or the user''s request spans multiple processing steps. Trigger keywords: process data, data pipeline, which skill, what order, how to approach this data.'
license: Apache-2.0
metadata:
  domain: data-science
  complexity: high
  requires_llm: false
  test_coverage: advisory  # structurally validated, not behaviorally tested (no executable tests by design)
  phase: 0
  supports_pipeline: true
  supports_generation: false
  entry_point: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - lifecycle
  - orchestration
  - workflow
  - quality
  dependencies:
  - pandas
  - numpy
  when_to_use: 'When task involves multiple data processing steps or user needs help deciding which skill to use. Trigger phrases: process data, data pipeline, which skill, what order, coordinate steps, multi-step, how to approach this data.'
---

## Natural Language Triggers

This skill provides routing knowledge — read it when you need to decide which magic-data-* skills to use and in what order. Useful when:
- "which skill handles this?" / "what order should I process data?"
- "how to approach this data pipeline" / "coordinate multiple steps"
- The task spans multiple data processing steps (load + clean + validate)
- You need to decide which skill handles a specific operation
- The user's request is vague and you need a framework for breaking it down

For the full interactive pipeline workflow with phases, tiers, PAUSE gates, and workspace tracking, see the `/data:lifecycle` command instead.

## When to Use

- Task involves multiple data processing steps that need coordination
- You need to decide which magic-data-* skill handles a specific operation
- The user's request is vague and spans multiple potential skills
- You want pipeline ordering guidance (what comes after loading? when to validate?)

**When NOT to Use:**
- Single, isolated operations — use the specific skill directly (e.g., "just load this file" → magic-data-loading)
- User wants the full interactive pipeline with phase tracking → suggest `/data:lifecycle` command instead

## Data Processing Expertise

> **Universal knowledge** — consumed by all three modes: interactive agents (Way 1), programmatic pipeline extractors (Way 2), and agents writing custom pipeline code (Way 3). Nothing below requires interactive session infrastructure.

### Thinking

Before starting any data processing task, ask:
- **What's the scope?** — Is this a single operation (load one file, fix one column), a multi-step pipeline (load → clean → validate → deliver), or a multi-dataset project (merge 5 sources, cross-reference)? Scope determines how much infrastructure is warranted and which skills to invoke.
- **What's already known?** — Has discovery happened? Is there a quality score? Has profiling been run? Don't repeat work. Check prior context before starting new analysis.
- **What data exists in the workspace?** — If the user's request is vague ("help me with my data", "I need to work with some files"), check the workspace for existing data files before asking. List files in `data/input/` and offer to work with what's already there. This turns a vague question into a concrete starting point.
- **What's the quality baseline?** — A quality score without context is meaningless. A 65/100 on a raw government export is expected; a 65/100 on cleaned production data is a problem. Baseline comparison drives the plan.
- **What does "done" look like?** — Define success criteria before execution. "Clean the data" is not a success criterion. "Null rate below 5%, no sentinel values, schema-valid" is.
- **Which skill handles each step?** — Lifecycle's value is routing, not execution. Every processing step has a dedicated MAGIC skill. Use the routing table below; don't write custom code for operations a skill already covers.
- **What order do the phases go?** — Discovery must precede planning. Planning must precede execution. Validation must follow execution. This sequence exists because each phase's output feeds the next — profiling results inform the cleaning plan, the cleaning plan determines what to validate.

### Rules

**Phase sequence — Discover, Plan, Execute, Validate, Deliver:**
```
Discover → Plan → Execute → Validate → Deliver
    ↑         ↑       ↑         ↑          ↑
    └─────────┴───────┴─────────┴──────────┘
              (refinement — from any phase)
```
Phases can loop back but never skip forward. You cannot execute without a plan (even an implicit one). You cannot validate without executing something. You can always return to discovery when new information appears.

**Skill routing — which skill handles which operation:**

| Operation | Skill | When to Route |
|-----------|-------|---------------|
| Load files (CSV, JSON, Parquet, Excel) | magic-data-loading | Any file ingestion — format detection, encoding, multi-source merge |
| Profile data quality | magic-data-profiling | Quality scoring, issue detection, distribution analysis |
| Clean data | magic-data-cleaning | Missing values, duplicates, normalization, sentinel replacement |
| Validate data | magic-data-validation | Schema validation, constraint checking, fitness-for-use |
| Generate/fill data with LLM | magic-data-synthesis | LLM-based generation, translation, fill-missing, transform |
| Reshape/join/aggregate | magic-data-transformation | Pivot, melt, merge, group-by, derive columns |
| Explore patterns | magic-data-exploration | Pattern detection, correlation, segmentation, hypothesis |
| Visualize | magic-data-visualization | Charts, plots, audience-appropriate graphics |
| Statistical tests | magic-statistical-analysis | Hypothesis testing, significance, regression |
| Final report | magic-report-generation | Assemble findings into structured deliverable |
| Workspace setup | magic-workspace-init | Directory scaffolding, environment verification |

**Pipeline ordering — skills compose in a standard sequence:**
1. **Load** (magic-data-loading) — get data into memory, validate format
2. **Profile** (magic-data-profiling) — understand quality baseline, detect issues
3. **Clean** (magic-data-cleaning) — fix issues identified by profiling
4. **Transform** (magic-data-transformation) — reshape, join, aggregate as needed
5. **Synthesize** (magic-data-synthesis) — LLM-based generation only when code/regex cannot solve it
6. **Validate** (magic-data-validation) — verify against success criteria
7. **Deliver** (magic-report-generation) — report, export, checkpoint

Not every pipeline uses every step. A "load and profile" task stops at step 2. A "clean this CSV" task is steps 1-3-6. The sequence defines ordering constraints, not mandatory steps.

**Quality gating between phases:**
- Discovery → Plan: profiling must complete before planning. Quality score establishes baseline.
- Plan → Execute: success criteria must be defined. "Clean the data" is not a criterion; "null rate < 5%, no sentinels" is.
- Execute → Validate: every execution step produces a checkpointable artifact. Validation compares artifact against criteria.
- Validate → Deliver: compliance report must pass. If it fails, loop back to Execute or Plan.

**Discovery environment (80/20):**
- Use predefined MAGIC skill scripts for ~80% of operations (format detection, quality scoring, issue detection, cleaning)
- Write custom code for ~20% (edge cases, domain-specific logic, unusual data structures)
- The agent exercises judgment on which path fits each situation

**When to use LLM:** Lifecycle routing itself is deterministic — use the skill routing table above. LLM-based synthesis (generating data, translating text, filling semantic gaps) is handled by `magic-data-synthesis`. Route to synthesis when the operation requires semantic understanding that code/regex cannot provide.

### Constraints

- MUST run auto-profiling on first data load (any scope) — quality score establishes the baseline everything else builds on
- MUST route operations to the appropriate MAGIC skill — don't write custom cleaning code when magic-data-cleaning handles it
- MUST define success criteria before execution (multi-step pipelines)
- MUST validate after execution — compare results against success criteria
- MUST test custom code on a sample before applying to the full dataset
- MUST NOT skip discovery — even "just clean this" needs profiling to know what to clean
- MUST NOT force heavyweight infrastructure on simple tasks — a single-column fix does not need a data spec, analysis journal, and compliance report
- NEVER claim causation from correlation — route statistical claims to magic-statistical-analysis
- NEVER skip the synthesis preview gate — LLM synthesis at scale has real cost implications
- NEVER apply custom code to the full dataset without sample testing first

## Seed Patterns

### Pipeline phase template with checkpoint strategy
```python
# Standard lifecycle pipeline skeleton — adapt to your task
# Checkpoints marked with [CKPT] where the judgment call is usually "yes"
# Agent decides based on the cost/risk table in ## Checkpointing

from pathlib import Path

data_dir = Path("data")
ckpt_dir = data_dir / "checkpoints"
ckpt_dir.mkdir(parents=True, exist_ok=True)

# Phase 1: Discover — load + auto-profile
df = load_file("input/raw.csv")                           # magic-data-loading
quality = run_quality_score(df)                           # magic-data-profiling
save_checkpoint(df, ckpt_dir / "loaded.parquet",          # [CKPT] always: first state
    metadata={"source": "input/raw.csv", "quality": quality})

# Phase 2: Plan — review findings, define criteria (no data change, no checkpoint needed)
success_criteria = {"max_null_rate": 0.05, "min_quality_score": 85}

# Phase 3: Execute — clean / transform / synthesize
df_clean = clean(df)                                      # magic-data-cleaning
save_checkpoint(df_clean, ckpt_dir / "cleaned.parquet",   # [CKPT]: before synthesis
    metadata={"operations": ["impute_median", "dedup"]})

df_synth = synthesize_columns(df_clean, cols=["summary"]) # magic-data-synthesis (LLM)
save_checkpoint(df_synth, ckpt_dir / "synthesized.parquet", # [CKPT] always: LLM cost
    metadata={"model": "gpt-4o", "cols_added": ["summary"]})

# Phase 4: Validate — compare against criteria (lightweight, no checkpoint needed)
validation_result = validate(df_synth, success_criteria)  # magic-data-validation

# Phase 5: Deliver — final export
df_synth.to_parquet("output/final.parquet", index=False)  # final output = checkpoint itself
```

### Provenance logging (workspace state entry)
```markdown
## Current State
- **Phase:** Execute
- **Quality Score:** 72/100 → 88/100 (after cleaning)
- **Dataset:** sales_q4.csv (2,500 rows, 6 columns)
- **Skills Applied:** magic-data-loading, magic-data-profiling, magic-data-cleaning
- **Last Checkpoint:** data/checkpoints/cleaned_sales.csv
- **Pending:** Validation against success criteria

## Decision Log
| Timestamp | Decision | Rationale |
|-----------|----------|-----------|
| 2026-04-30T10:15:00Z | Use median imputation for price column | 8% missing, right-skewed distribution |
| 2026-04-30T10:32:00Z | Drop rows with null product_id | Primary key — cannot impute meaningfully |
```

## Checkpointing

Checkpointing is an **agent judgment call**, not a mechanical rule. The agent decides whether to save intermediate data based on the cost and risk of the current operation — not on a fixed "save after every step" policy. This applies in both interactive sessions and pipeline code generation.

### When to decide "yes, checkpoint here"

Use this decision framework at each phase boundary:

| Signal | Checkpoint? | Reasoning |
|---|---|---|
| LLM synthesis step just completed | **Always** | LLM calls cost money and time; never re-run if avoidable |
| Expensive computation (>1 min, large dataset) | **Yes** | Recovery cost is high |
| Before a destructive/irreversible operation (drop columns, dedup) | **Yes** | Preserve the pre-op state for rollback |
| Pipeline has ≥3 phases total | **Yes** at each major boundary | Restartability from mid-pipeline matters |
| Simple 1-2 step pipeline on small data | **Optional** | Recovery is cheap; skip if overhead isn't worth it |
| Profiling output (JSON summary, not the data itself) | **Yes** | Cheap to save; expensive to re-profile large data |
| Quick in-memory transformation (<10s, <100K rows) | **Skip if next step is safe** | Agent judgment: is the next step reversible? |

### Naming: convention vs practice

The practice of saving intermediate data is universal — both in interactive sessions and in generated pipeline code.

What differs is the naming convention:
- **Interactive sessions:** `ckpt_NN_description.ext` (e.g., `ckpt_03_cleaned.csv`) — numbered for easy orientation
- **Pipeline code:** Descriptive names work equally well: `corpus_loaded.jsonl → corpus_enriched.jsonl → corpus_validated.jsonl`

There is no mandatory naming convention. Choose names that make the pipeline state obvious to a reader.

### Canonical `save_checkpoint()` helper

This pattern lives here — reference it from generated pipeline code rather than redefining it each time:

```python
import json, datetime
from pathlib import Path
import pandas as pd

def save_checkpoint(df: pd.DataFrame, path: str, metadata: dict = None) -> str:
    """Save intermediate pipeline data with provenance metadata.

    Call at phase boundaries where the cost of re-running the preceding step
    justifies persisting the result. Agent decides when — this is the HOW.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    suffix = p.suffix.lower()
    if suffix == ".parquet":
        df.to_parquet(p, index=False)
    elif suffix == ".jsonl":
        df.to_json(p, orient="records", lines=True, force_ascii=False)
    else:
        df.to_csv(p, index=False)
    meta = {
        "rows": len(df),
        "cols": list(df.columns),
        "saved_at": datetime.datetime.utcnow().isoformat(),
        **(metadata or {}),
    }
    p.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return str(p)

# Example: save after loading (always — loading is the first phase, cheap to save)
save_checkpoint(loaded_df, "data/loaded.parquet", {"source": "input/raw.csv"})

# Example: save after LLM synthesis (always — expensive to re-run)
save_checkpoint(synthesized_df, "data/synthesized.parquet", {"model": "gpt-4o", "cols_generated": ["summary"]})

# Example: skip checkpoint (quick in-memory filter before a safe next step)
filtered_df = df[df["status"] == "active"]  # no checkpoint needed
```

**Resume from checkpoint:** Read `workspace_state.md` to find the latest checkpoint and current phase. Resume from there rather than re-running the full pipeline.

## Pipeline Composition

When a task involves multiple skills in sequence (e.g., "load, profile, clean, deliver"),
the agent chains operations where each step's output becomes the next step's input.

### How Script Categories Map Across Modes

| Script category | Interactive mode (conversation) | Pipeline mode (saved to file) |
|----------------|--------------------------------|-------------------------------|
| **Callable tool** (e.g., `download_hf_dataset.py`) | Agent calls via CLI: `python3 download_hf_dataset.py --dataset org/name` | Agent writes the download logic inline: `from huggingface_hub import snapshot_download; snapshot_download(...)` |
| **Scriptable tool — standard** (e.g., `quality_score.py`) | Agent calls via CLI: `python3 quality_score.py data.parquet logs/quality.json` | Agent writes standard profiling logic inline (adapted from skill patterns) |
| **Scriptable tool — custom** (e.g., `handle_missing.py` with per-column strategies) | Agent reads source, writes custom code, runs in conversation | Agent writes the SAME custom code into the pipeline step |
| **Reference impl** (e.g., `generate_report.py`) | Agent reads patterns, writes custom code, runs inline | Agent writes the SAME custom code into the pipeline step |

**Key principle:** Skill scripts are read at pipeline generation time (the agent learns from them), NOT imported at pipeline runtime. Each pipeline step is self-contained Python code that runs without the skills directory.

### Example: HuggingFace -> Profile -> Clean -> Validate -> Deliver

```python
import json
import pandas as pd
from pathlib import Path

INPUT_DIR = Path("data/input/hf")
CHECKPOINT_DIR = Path("data/checkpoints")
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
FORCE = "--force" in __import__("sys").argv

# 1. Download (inline — adapted from download_hf_dataset.py patterns)
if FORCE or not (CHECKPOINT_DIR / "01_downloaded.parquet").exists():
    from huggingface_hub import snapshot_download
    snapshot_download("org/name", repo_type="dataset", local_dir=str(INPUT_DIR),
                      allow_patterns=["*.parquet"])
    df = pd.read_parquet(INPUT_DIR / "train.parquet")
    df.to_parquet(CHECKPOINT_DIR / "01_downloaded.parquet", index=False)

# 2. Profile (inline — adapted from quality_score.py patterns)
if FORCE or not (CHECKPOINT_DIR / "02_quality.json").exists():
    df = pd.read_parquet(CHECKPOINT_DIR / "01_downloaded.parquet")
    null_pct = df.isnull().mean().mean() * 100
    dup_pct = df.duplicated().mean() * 100
    score = round(100 - null_pct - dup_pct, 1)
    Path(CHECKPOINT_DIR / "02_quality.json").write_text(json.dumps({"score": score}))

# 3. Clean missing values (inline — adapted from handle_missing.py patterns)
if FORCE or not (CHECKPOINT_DIR / "03_cleaned.parquet").exists():
    df = pd.read_parquet(CHECKPOINT_DIR / "01_downloaded.parquet")
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "")
    df.to_parquet(CHECKPOINT_DIR / "03_cleaned.parquet", index=False)

# 4. Validate (inline — adapted from sanity_check.py patterns)
if FORCE or not (CHECKPOINT_DIR / "04_validation.json").exists():
    df = pd.read_parquet(CHECKPOINT_DIR / "03_cleaned.parquet")
    checks = {"row_count": len(df), "null_cols": int(df.isnull().any().sum()),
              "dup_count": int(df.duplicated().sum())}
    Path(CHECKPOINT_DIR / "04_validation.json").write_text(json.dumps(checks))

# 5. Deliver (inline — using huggingface_hub directly)
if FORCE or True:  # Delivery steps always run (no checkpoint to check)
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo("org/output", repo_type="dataset", private=True, exist_ok=True)
    api.upload_folder(folder_path=str(CHECKPOINT_DIR), repo_id="org/output", repo_type="dataset")
```

### Agent Interpretation Between Steps

In an **ad-hoc pipeline**, the agent reads each step's output before deciding the next step.
For example, after profiling, the agent reads the quality score to determine whether cleaning
is needed and which strategy to use.

In a **rerunnable pipeline**, these decisions are baked into the script at authoring time
(e.g., always use auto strategy, or write a custom cleaning module that encodes the strategy).

### When to Use Pipeline Composition vs Custom Code

- **Use pipeline composition** when each step's standard mode is sufficient
- **Drop to custom code** when a step needs task-specific logic (custom SQL, per-column cleaning rules, custom chart annotations)
- **Mix both** — standard steps as inline adapted code, custom steps as separate modules

### Output Path Conventions

| Output type | Interactive naming | Pipeline naming |
|-------------|-------------------|-----------------|
| JSON reports | `logs/{operation}.json` | `{NN}_{step}.json` (e.g., `02_quality.json`) |
| Data checkpoints | `data/checkpoints/ckpt_{operation}.parquet` | `{NN}_{step}.parquet` (e.g., `03_cleaned.parquet`) |
| Charts | `charts/{operation}.png` | `charts/{operation}.png` |
| Pipeline directories | — | `workspace/pipelines/{name}/` |
| Step modules | — | `workspace/pipelines/{name}/steps/` |

## Rerunnable Pipelines

When the user asks for a pipeline they can re-run later ("build a pipeline", "I'll rerun this weekly"):

### Pipeline Tier Decision

| Signal | Single-file pipeline | Project pipeline |
|--------|---------------------|-----------------|
| Number of steps | ≤5 | 6+ |
| Custom logic per step | ≤20 lines | 20+ lines |
| Will be maintained/edited | Unlikely | Yes |
| Re-run frequency | Occasional | Regular/scheduled |
| Config changes between runs | Just paths/dataset | Multiple parameters |
| Team collaboration | Solo | Multiple people |

Start with Single-file pipeline. Upgrade to Project pipeline when the file gets unwieldy.

### Single-file pipeline

A single Python script with checkpoint guards between steps. The agent generates this by saving its working conversation code to a file.

```python
# workspace/pipelines/clean_and_deliver.py
"""Rerunnable pipeline. Run: python3 clean_and_deliver.py [--force]"""
import pandas as pd
import json
from pathlib import Path

FORCE = "--force" in __import__("sys").argv

# --- Config (edit for different runs) ---
DATASET = "org/customer-survey"
OUTPUT_REPO = "org/customer-survey-cleaned"
CKPT = Path("../../data/checkpoints")
CKPT.mkdir(parents=True, exist_ok=True)

# --- Step 1: Download ---
if FORCE or not (CKPT / "01_downloaded.parquet").exists():
    from huggingface_hub import snapshot_download
    snapshot_download(DATASET, repo_type="dataset", local_dir="../../data/input/hf",
                      allow_patterns=["*.parquet"])
    df = pd.read_parquet("../../data/input/hf/train.parquet")
    df.to_parquet(CKPT / "01_downloaded.parquet", index=False)
    print(f"[download] done — {len(df)} rows")
else:
    print("[download] skip — checkpoint exists")

# --- Step 2: Clean (CUSTOM for this dataset) ---
if FORCE or not (CKPT / "02_cleaned.parquet").exists():
    df = pd.read_parquet(CKPT / "01_downloaded.parquet")
    rows_in = len(df)
    df['age'] = df.groupby('region')['age'].transform(lambda x: x.fillna(x.median()))
    df['salary'] = df['salary'].fillna(df['salary'].median())
    df = df.dropna(subset=['email'])
    df.to_parquet(CKPT / "02_cleaned.parquet", index=False)
    print(f"[clean] done — {rows_in} → {len(df)} rows")
else:
    print("[clean] skip — checkpoint exists")

# --- Step 3: Deliver ---
from huggingface_hub import HfApi
api = HfApi()
api.create_repo(OUTPUT_REPO, repo_type="dataset", private=True, exist_ok=True)
api.upload_file(path_or_fileobj=str(CKPT / "02_cleaned.parquet"),
                path_in_repo="train.parquet", repo_id=OUTPUT_REPO, repo_type="dataset")
print(f"[deliver] done — uploaded to {OUTPUT_REPO}")
```

**Key:** Each step checks `if FORCE or not checkpoint.exists()`. Re-running skips completed steps. Pass `--force` to re-run everything.

### Project pipeline

When the pipeline grows beyond ~5 steps or has substantial custom logic per step, structure it as a project:

```
workspace/pipelines/customer_survey/
├── pipeline.py              ← orchestrator (copy from skills/magic-data-lifecycle/references/pipeline_template.py)
├── config.py                ← all parameters (dataset, paths, options)
├── steps/
│   ├── __init__.py
│   ├── step_01_download.py  ← each step: def run(input_path, output_path, config) -> dict
│   ├── step_02_profile.py
│   ├── step_03_clean.py     ← custom logic for this dataset
│   └── step_04_deliver.py
└── README.md                ← what this does, how to re-run
```

Each step module exports one function: `def run(input_path: str, output_path: str, config: dict) -> dict`.

**To create a Project pipeline:** Copy the template and fill in the STEPS list:
```bash
cp skills/magic-data-lifecycle/references/pipeline_template.py workspace/pipelines/<name>/pipeline.py
```
The template handles checkpoint resume, `--from-step`/`--steps`/`--force`/`--status` CLI flags, run logging, and error handling. You only customize the STEPS list and config.

The orchestrator (pipeline.py) is copied from `skills/magic-data-lifecycle/references/pipeline_template.py`. The agent fills in the STEPS list and config — the template handles checkpoint resume, `--from-step`, `--steps`, `--force`, `--status` CLI flags, run logging, and error handling.

```bash
python3 pipeline.py                    # run all, skip completed
python3 pipeline.py --from-step clean  # resume from clean
python3 pipeline.py --steps clean deliver  # only these steps
python3 pipeline.py --force            # ignore checkpoints
python3 pipeline.py --status           # show what's done/pending
```

### When to NOT Use a Pipeline

Not every data task should be a pipeline. Pipelines make **proven approaches repeatable**, not automate discovery.

| Question | If YES → Pipeline | If NO → Interactive |
|----------|-------------------|---------------------|
| Will someone run this exact process again? | Yes | No |
| Will the approach stay the same next time? | Yes | No |
| Does reproducibility matter (audits, compliance)? | Yes | No |
| Will a different person need to run this? | Yes | No |

If all four answers are "no", stay interactive. If two or more are "yes", build a pipeline.

### Key Principles

- **Self-contained steps:** Each step has all its logic inline — no imports from skill scripts at runtime
- **Checkpoint = completion:** Existence of the output file means the step is done
- **Config at top:** Dataset names, paths, thresholds — easy to change for different runs
- **Custom code persists:** Agent-written custom logic lives in the pipeline file/modules, not in chat history

## Script Execution Decision Logic

When you encounter a data processing step, use this three-step decision process.

### Step 1: Identify the Script Category

Check the relevant skill's `## Reference Scripts` section. Scripts are categorized as:

- **Callable tool** — always call directly via CLI (e.g., `connect_database.py`, `inspect_hf_dataset.py`)
- **Scriptable tool** — call directly for standard use, OR read + adapt for advanced (e.g., `quality_score.py`, `handle_missing.py`)
- **Reference implementation** — always read source and write custom code (e.g., `generate_report.py`, `derive_columns.py`)

### Step 2: Decide Based on Task Requirements

**For callable tools:** Always call directly. No decision needed.

**For scriptable tools, ask:** "Does the default mode handle this task?"
- YES (standard profiling, standard cleaning, standard detection) — call directly via CLI
- NO (per-column strategies, custom thresholds, domain-specific rules) — read source, write custom code

**For reference implementations:** Always read and adapt. No decision needed.

### Step 3: Check Pipeline Context

If this step is part of a **rerunnable pipeline** (user said "build a pipeline", "I'll rerun this"):
- Write each step's logic INLINE in the pipeline script — self-contained, no imports from skill scripts
- The agent reads skill patterns at generation time and writes adapted code directly into the pipeline
- For steps that truly need custom logic (>20 lines): write a helper module in `workspace/pipelines/{name}/steps/`

### Scriptable Tool Tiers

- **Tier A (26 scripts):** Standard mode works with just input + output paths. Call directly for any standard operation. Examples: `quality_score.py`, `detect_patterns.py`, `chart_selector.py`.
- **Tier B (13 scripts):** CLI is well-defined but always needs task-specific args beyond input/output. Call directly with the documented required params. Examples: `extract_data.py` (needs `--query`), `hypothesis_test.py` (needs `--group_col` + `--value_col`).

The tier does NOT change the decision logic — it only affects how many args the agent must provide.

### Decision Quick-Reference

| Situation | Action |
|-----------|--------|
| Standardized operation (connect, inspect, download, deliver) | Call the callable tool directly |
| Standard analysis — Tier A (profile, detect issues, basic stats, charts) | Call the scriptable tool directly with input + output |
| Standard analysis — Tier B (aggregate, reshape, hypothesis test) | Call the scriptable tool with required params from SKILL.md |
| Custom per-column logic, domain-specific rules | Read scriptable tool source, write custom code |
| SQL query or custom data transform | Read reference impl source, write custom code |
| Rerunnable pipeline — standard step | Write adapted code inline in pipeline script |
| Rerunnable pipeline — custom step | Write as module in `workspace/pipelines/{name}/steps/` |

### Examples

**Example 1: "Profile this data"**
1. Script = `quality_score.py` → category = scriptable tool (Tier A)
2. Do I need custom dimensions or weights? → No
3. Decision: CALL DIRECTLY — `python3 quality_score.py data.parquet logs/quality.json`

**Example 2: "Clean missing values — use KNN for age, median for salary"**
1. Script = `handle_missing.py` → category = scriptable tool (Tier A)
2. Do defaults suffice? → No, user wants per-column strategies
3. Can I express this via CLI args? → No, `--strategy` takes one value for all columns
4. Decision: READ source, WRITE custom code with per-column logic

**Example 3: "Extract last 30 days of orders from PostgreSQL"**
1. Script = `extract_data.py` → category = scriptable tool (Tier B)
2. `--query` is required and always task-specific SQL
3. Decision: CALL DIRECTLY with task-specific query — `python3 extract_data.py --query "SELECT ..."`

**Example 4: "Build a rerunnable pipeline: download, clean, deliver"**
1. Multi-step + rerunnable → write self-contained pipeline with inline code for ALL steps
2. Each step: inline adapted code from skill patterns (no `from quality_score import ...`)
3. Save as `workspace/pipelines/clean_and_deliver.py` (or `workspace/pipelines/clean_and_deliver/pipeline.py` if complex)

### Three Execution Modes

| Mode | When | Agent strategy |
|------|------|---------------|
| **Single operation** | User asks for one thing ("profile this", "clean that") | Check script category, use default or customize based on requirements |
| **Ad-hoc pipeline** | User chains multiple steps but does not need rerunning | Use best tool per step — mix CLI calls and custom code freely |
| **Rerunnable pipeline** | User explicitly wants reproducibility | Write self-contained inline code for each step. For custom steps (>20 lines), write helper modules in `workspace/pipelines/{name}/steps/`. |

## Self-Healing

If lifecycle coordination fails:

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Skill not found / not triggered | Wrong skill name or missing trigger | Check Skills Reference table; use exact skill names |
| Quality score unavailable | Profiling not run or script missing | Run `quality_score.py` from magic-data-profiling |
| Validation fails repeatedly (3+ loops) | Success criteria may be unreachable | Present status to user; suggest relaxing criteria or changing approach |
| Workspace state inconsistent | Manual edits or interrupted session | Re-read data files directly; rebuild workspace_state.md from checkpoints |
| Script errors from downstream skill | Wrong input format or missing dependency | Check the specific skill's Self-Healing table |
| Resume fails after interruption | Missing checkpoint or stale workspace state | List checkpoint files; find latest valid one; restart from there |

## Skills Reference

| Phase | Primary Skills | Key Scripts |
|-------|---------------|-------------|
| Discover | magic-data-loading, magic-data-exploration, magic-data-profiling | quality_score.py, detect_all_issues.py, deep_quality_analysis.py |
| Plan | magic-data-profiling (findings presentation) | findings_presenter.py (optional) |
| Execute | magic-data-cleaning, magic-data-synthesis, magic-data-transformation | Per-skill scripts |
| Validate | magic-data-validation, magic-data-profiling | quality_score.py, validate_schema.py, content_validator.py |
| Deliver | magic-report-generation | generate_report.py |

## Edge Cases

- **No problems found, no processing needed:** Proceed directly to Deliver. A clean dataset is a valid outcome — document it.
- **Simple task reveals unexpected complexity:** Propose escalation from single-op to multi-step pipeline. User can decline.
- **User wants to skip discovery:** Run at minimum surface profiling (quality_score.py). Discovery can be fast but not absent.
- **Success criteria unreachable after 3+ attempts:** Present status. Suggest accepting current results or changing the approach. Don't loop indefinitely.
- **Resume mid-pipeline:** Read workspace_state.md + latest checkpoint + data spec. Continue from where processing stopped.
- **Multiple datasets:** Each dataset gets its own profiling and cleaning pass. Cross-dataset operations (joins, merges) use magic-data-transformation.
- **New problems during execution:** Trigger refinement — update plan, loop back to the appropriate phase.

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Data spec format | `references/data_spec_format.md` | Drafting or updating data specs for multi-step pipelines |

