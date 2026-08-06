---
name: magic-data-synthesis
description: 'Synthesize, generate, and transform data using LLM-based operations via DataDesigner engine. Use when: (1) filling missing values/sentinels with contextual content, (2) translating columns, (3) converting formats (HTML→markdown), (4) annotating/labeling records, (5) extracting structured data from text, (6) generating new columns from existing context. Trigger keywords: synthesize, generate, fill missing, translate, annotate, enrich, LLM generation, DataDesigner.'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: high
  requires_llm: true
  phase: 2
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 6
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - synthesis
  - generation
  - llm
  - transformation
  - enrichment
  - annotation
  scripts:
  - scripts/synthesis_config.py
  - scripts/generate_column.py
  - scripts/batch_synthesize.py
  - scripts/synthesis_prompt_builder.py
  - scripts/enrich_from_reference.py
  - scripts/validate_synthetic.py
  dependencies:
  - pandas
  - numpy
  - data-designer
  - tiktoken
  when_to_use: 'When generating data using LLM or creating synthetic examples. Trigger phrases: synthesize, generate, fill missing, translate, annotate, enrich, augment data, create new examples, DataDesigner, LLM generation.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "synthesize data" / "generate missing values" / "fill in the blanks with LLM"
- "translate this column" / "convert HTML to markdown"
- "annotate these records" / "label this data"
- "enrich this dataset" / "generate descriptions"
- "fill the TBD placeholders" / "replace sentinels with real content"
- "use DataDesigner" / "run data-designer"

These produce the SAME behavior as the synthesis workflow. Natural language works equally well.

## When to Use

- Columns have missing values, sentinels ("X", "N/A", "TBD"), or placeholders needing contextual generation
- Format conversion (HTML→markdown), translation, annotation, labeling, summarization
- Structured field extraction from unstructured text into multiple columns
- Reference join leaves gaps → LLM fills remaining (use `enrich_from_reference.py` first)

**When NOT to Use:** Rule-based fixes (regex, type casting, dedup) → magic-data-cleaning. Reshaping, joins, aggregation → magic-data-transformation. Schema enforcement → magic-data-validation. If a Python function can produce correct output for every case, use programmatic generation instead of DataDesigner.

## Data Processing Expertise

### Domain Knowledge

> **Universal** — consumed by interactive agents (Way 1), programmatic extractors (Way 2), and agents writing custom pipeline code (Way 3).

```yaml
engine: DataDesigner (primary), batch_synthesize.py (legacy reference)
config_format: Python file with load_config_builder() function
preview_gate: HARD GATE — always before full generation, even in autonomous mode
pipeline_mode: agent generates synthesize_column() function, calls inline
model_config: MAGIC_LLM_* env vars (MODEL, BASE_URL, API_KEY, MAX_TOKENS); provider="local" targets LM Studio at localhost:1234; MCP templates also read MAGIC_TOOL_MODEL (tool-capable model)
seed_types: LocalFileSeedSource (workspace files), DataFrameSeedSource (checkpoints)
quality_control: LLMJudgeColumnConfig with multi-rubric scoring (one call per row)
quality_threshold: mean_100 >= 70% good, >= 60% acceptable, < 60% regenerate
output_format: parquet (default), csv, jsonl
cost_control: estimate_from_preview() before create(); local models = $0
feasibility_rule: assess per column — synthesize (LLM) vs code (expression) vs enrich (join) vs skip
thinking_tags: auto-stripped (<think>, <reasoning>, <thought>, <reflection>) for local models
prompt_sanitization: injection patterns filtered, whitespace normalized, values truncated
dd_install_check: importlib.util.find_spec("data_designer") — guide install if absent
dd_version: ">=0.6 — async DAG engine + per-model AIMD adaptive concurrency are the v0.6 default"
capability_reference: references/datadesigner_capabilities.md — full engine surface (11 columns, 14 samplers, 6 seed sources, processors, workflow chaining, message traces, MCP tool-use, agent-rollout ingestion, person sampling). Read it when a task needs a primitive the recipe templates don't already wire up.
```

**Feasibility decision per column:**
| Task | Use LLM (this skill) | Use Code (other skills) |
|------|---------------------|------------------------|
| Fill missing descriptions, translate, annotate | Yes | No |
| Date normalization, type casting, regex replace | No | Yes — cleaning/transformation |
| Value exists in reference table | No | Yes — `enrich_from_reference.py` first |
| Entity extraction, summarization | Yes | No |

### Thinking

Before any synthesis, ask:
- **Can code handle this?** — Deterministic transforms (regex, type cast) → use cleaning/transformation. LLM only when contextual understanding is required.
- **Does a reference dataset have the answer?** — Join first, synthesize only the gaps.
- **What's the cost at scale?** — Preview on 5-20 rows. Extrapolate. A bad prompt on 50K rows = $100+ wasted.
- **Which model fits this task?** — Larger models produce higher quality but may be 10–50× slower for local inference. Match model size to output complexity:
  - **Short outputs** (glosses, labels, single sentences, yes/no): Small models (1–8B params) usually suffice. Speed: 10–50 tok/s locally.
  - **Medium outputs** (definitions, short paragraphs, translations): Mid-range models (8–30B) balance quality and speed. Speed: 3–15 tok/s locally.
  - **Complex outputs** (multi-paragraph, nuanced reasoning, creative text): Large models (30B+) needed. Speed: 1–5 tok/s locally.
  Always test with the 5-row preview — measure BOTH quality AND speed. If preview takes >30s per row for short-output tasks, switch to a smaller model.
- **Thinking vs non-thinking models** — Reasoning models (Qwen 3.5, DeepSeek R1) use 3000+ internal tokens before producing output. For simple generation tasks (definitions, translations), this overhead is wasted — prefer non-thinking models (Gemma, Llama, Phi) which produce output directly. Reserve thinking models for tasks requiring multi-step reasoning (complex annotation, code generation, mathematical derivation).

### Rules

- **Feasibility assessment per column**: Every column proposed for synthesis must pass a feasibility check — can code handle this? (→ cleaning/transformation). Does a reference dataset have the answer? (→ enrich first). Only synthesize when contextual understanding is required.
- **Preview gate is non-negotiable**: Always run `data-designer preview` before `data-designer create`, even in autonomous mode. A bad prompt on 50K rows = $100+ wasted, producing content harder to clean than the original sentinels.
- **Pre-filter seed data**: Remove rows with sentinel values or nulls in the target column before synthesis. DataDesigner generates for ALL rows in the seed; unfiltered sentinels get "translated" literally (TBD→"À déterminer").
- **Validate config before preview**: Run `data-designer validate` before `data-designer preview` — catches config errors before any API calls or cost.
- **Mutation ordering**: Never mix deterministic cleaning and LLM synthesis in the same pass. Clean first (types, encoding, whitespace), checkpoint, then synthesize on the cleaned data.
- **DataDesigner vs. programmatic generation**: Not all synthesis tasks require the DataDesigner LLM engine. Choose the right approach:

  | Task | Use DataDesigner (LLM) | Use Programmatic (Code) |
  |------|----------------------|------------------------|
  | Fill sentinels/placeholders with contextual text | Yes | No |
  | Translate text columns | Yes | No |
  | Annotate, label, or classify free text | Yes | No |
  | Extract entities from unstructured text | Yes | No |
  | Generate data following known mathematical/logical rules | No | Yes |
  | Generate data matching a mechanical template with variable substitution | No | Yes |
  | Generate synthetic examples requiring natural language variation | Yes | No |
  | Augment training data where diversity of phrasing matters | Yes | No |
  | Format conversion with deterministic rules (date formats, unit conversions) | No | Yes — use cleaning/transformation |

  **Decision heuristic:** Ask "Can I write a Python function that produces correct output for every input?" If yes, use programmatic generation — it's faster, cheaper, and provably correct. If output quality depends on semantic understanding, creativity, or contextual reasoning, use DataDesigner.

  **Document the routing decision:** When choosing programmatic over DataDesigner (or vice versa), state the reason in the output. Example: "Using programmatic generation because bit manipulation rules are deterministic — LLM arithmetic is unreliable (verified: 1/10 correct in prior test)." This makes the decision reviewable and helps users understand when LLM cost is being incurred vs. avoided.
- **Parallel request tuning**: The `max_parallel_requests` parameter in ModelConfig controls how many LLM calls DataDesigner makes simultaneously. Tune it based on the endpoint:

  | Endpoint Type | Suggested Parallelism | Why |
  |--------------|----------------------|-----|
  | Local small model (<10B params, e.g. Gemma 3n) | 2–4 | GPU memory is the bottleneck; higher parallelism causes slowdown or OOM |
  | Local large model (>10B params, e.g. Qwen 35B) | 1–2 | Model weights consume most GPU memory; minimal room for batch parallelism |
  | Cloud API (Gemini, OpenAI) | 4–8 | Rate limits, not memory, are the constraint; check provider docs for limits |
  | Cloud batch API (OpenAI batch, Vertex batch) | 10–20+ | Batch APIs are designed for throughput; limited by cost budget, not infra |

  When in doubt, start with `max_parallel_requests=2`, measure throughput on preview, then scale up. Doubling parallelism on a local endpoint and seeing no speedup means the GPU is saturated.

  **DD ≥0.6 reconciliation:** From v0.6 the async DAG engine is the default and applies **per-model AIMD adaptive concurrency** — it drops ~75% on a 429 and adds a slot after a run of successes, so it auto-tunes the live concurrency level. On DD ≥0.6 treat the table values as a **ceiling**, not a fixed level: AIMD starts conservative and ramps within `max_parallel_requests`. The knob that still matters for slow self-hosted endpoints is `timeout`. Set `DATA_DESIGNER_ASYNC_ENGINE=0` only if you need deterministic sync ordering. (Full detail: `references/datadesigner_capabilities.md` §8.)
- **Quality verification at scale**: Preview validates a small sample, but full runs need post-generation quality checks:

  | Dataset Size | Verification Strategy |
  |-------------|---------------------|
  | < 20 rows | Review all rows manually |
  | 20–100 rows | Skim all, flag any that look wrong |
  | 100–500 rows | Review a random 10% sample (minimum 20 rows) + automated checks |
  | > 500 rows | Automated checks first, then manual review of flagged rows |

  **Automated quality signals** (check these before presenting results):
  - Empty or whitespace-only outputs → generation failed silently
  - Outputs that echo the input verbatim → prompt may be malformed
  - Outputs in the wrong language (when generating non-English content) → verify first 5 rows
  - Outputs significantly shorter or longer than the preview sample → model may be truncating or hallucinating
  - Duplicate outputs across different input rows → model may be ignoring seed context
  - Mode collapse: many rows producing near-identical phrasing → increase temperature or add diversity samplers

  **Domain-specific spot checks**: For tasks with ambiguous inputs (e.g., terms with multiple meanings), flag entries where the generated output may reflect the wrong sense. Example: "bank" means both a financial institution and a river bank — a model may pick the wrong sense depending on context.
- **Verification scope (what the test suite actually exercises vs. documents)**: The engine integration is verified end-to-end through `validate` → `preview` → `create`: a `create()` run is asserted to persist a well-formed dataset on disk with the expected row count. **Documented but NOT exercised by tests:** partitioned/sharded scale runs, checkpoint/resume, multi-batch merge beyond a small smoke run, and cloud-cost controls. Treat those as design guidance to verify against your own endpoint before a large run — they are not covered by an automated test.
- **When to use LLM**: Deterministic text fixes (whitespace, encoding, casing) are always code via cleaning. Semantic operations (filling sentinels with meaningful content, translation, annotation) require LLM via this skill.

### Constraints

- MUST pre-filter seed data before synthesis — remove rows with sentinel values (TBD, N/A, X) or nulls in the target column from the seed dataset. DataDesigner generates for ALL rows in the seed; if sentinels are included, they get "translated" literally (e.g., TBD→"À déterminer") or nulls produce garbage. Filter first, generate, then merge back.
- MUST run preview/dry-run before full-scale synthesis — present cost estimate to user
- MUST validate output with quality checks before checkpointing as complete
- MUST assess feasibility per column — LLM is not the default; it's chosen when code cannot solve it
- MUST run `data-designer validate` before preview — catches config errors before any API calls
- SHOULD use a SEPARATE, ideally stronger, judge model for rejection sampling. WHY: a model judging its own output (same model as the generator) is a **known-weak placeholder, not a calibrated gate** — it tends to rate its own work favourably, so the filter passes low-quality rows. The bundled templates expose a distinct `judge`/`judge-model` alias (set `MAGIC_*_JUDGE_MODEL` + `_PROVIDER` to a stronger/cloud judge); when you leave it pointed at the generator model, treat the judge scores as a smoke signal, not a quality guarantee, and spot-check the kept rows manually.
- NEVER skip the preview gate, even in autonomous/pipeline mode. WHY: a bad prompt on 50K rows = $100+ wasted, and produces content HARDER to clean than the original sentinels
- NEVER synthesize binary data — text-representable only
- NEVER use a local reasoning model (Qwen, DeepSeek) without `extract_reasoning_content=True`. WHY: these models put ALL output in the reasoning/thinking field — the `content` field returns empty, giving you zero results with no error. SET IT ON the LLM column (`LLMTextColumnConfig`/`LLMCodeColumnConfig`), NOT on `ChatCompletionInferenceParams` (that raises a Pydantic "Extra inputs are not permitted"). NOTE: this flag is **dual-purpose** — beyond the local-model workaround it is also the native **CoT-capture feature** (emits a `{column}__reasoning_content` column) for reasoning-stage data; pair it with `with_trace` to keep both the full trace and the isolated chain-of-thought (see `references/datadesigner_capabilities.md` §6).
- NEVER set `max_tokens` below 2048 with local reasoning models. WHY: they use 3000+ tokens for internal reasoning before producing the answer; low limits truncate mid-thinking and return empty output
- NEVER assume `enable_thinking: false` works for all models. WHY: LM Studio Qwen ignores this flag; use `extract_reasoning_content=True` instead as the reliable approach
- NEVER skip output language verification on preview when generating non-English content. WHY: models default to English even when explicitly asked for another language — always visually verify the first 5 rows
- NEVER retry a failing LLM endpoint more than once without diagnosing the failure. WHY: blindly retrying a dead endpoint wastes time; instead health-check the endpoint, save partial results, and offer a fallback provider
- MUST save partial results before switching providers or stopping. WHY: DataDesigner writes completed batches to `tmp-partial-parquet-files/` — these contain already-generated rows that should not be re-generated
- MUST offer a fallback provider when the primary fails: local model failed → offer Gemini (if GOOGLE_API_KEY set); cloud API failed → offer local model (if LM Studio running)

## Seed Patterns

> **Adaptable snippets** — agents copy and adapt these for custom pipelines.

### Pipeline synthesis function (DataDesigner CLI)
```python
import subprocess, json, pandas as pd

def synthesize_column(seed_path: str, config_path: str, num_records: int, artifact_path: str) -> pd.DataFrame:
    """Run DD synthesis via CLI. Informed by magic-data-synthesis SKILL.md."""
    # Validate config first
    subprocess.run(["data-designer", "validate", config_path], check=True)
    # Preview for cost estimation (5 rows)
    subprocess.run([
        "data-designer", "preview", config_path,
        "--num-records", "5", "--save-results",
        "--artifact-path", f"{artifact_path}/preview",
    ], check=True)
    # Full generation (after PAUSE gate approval)
    subprocess.run([
        "data-designer", "create", config_path,
        "--num-records", str(num_records),
        "--artifact-path", artifact_path,
    ], check=True)
    # Load result
    from pathlib import Path
    parquet = next(Path(artifact_path).rglob("*.parquet"))
    return pd.read_parquet(parquet)
```

### Minimal single-column config (load_config_builder pattern)
```python
# File: workspace/configs/my_recipe.py
from data_designer.config.config_builder import DataDesignerConfigBuilder, ModelConfig
from data_designer.config.models import ChatCompletionInferenceParams
from data_designer.config.seed_source_types import LocalFileSeedSource

def load_config_builder() -> DataDesignerConfigBuilder:
    # ADAPT: model config — change provider/model for your endpoint
    model = ModelConfig(
        alias="my-model", model="gemini-3.1-flash-lite-preview",
        inference_parameters=ChatCompletionInferenceParams(
            max_parallel_requests=4, temperature=0.7, max_tokens=256,
        ),
        provider="gemini",  # must exist in ~/.data-designer/model_providers.yaml
        skip_health_check=True,
    )
    builder = DataDesignerConfigBuilder()
    builder.add_model_config(model)
    # ADAPT: seed data path
    builder.with_seed_dataset(LocalFileSeedSource(path="data/input.csv"))
    # ADAPT: column prompt — use {{ col_name }} for Jinja references to seed columns
    builder.add_column(
        column_type="llm-text", name="definition",
        prompt="Given word={{ word }} and pos={{ pos }}, write a definition.",
        model_alias="my-model",
    )
    return builder
```

### Multi-column config with dependency ordering
```python
# File: workspace/configs/multi_column_recipe.py
from data_designer.config.config_builder import DataDesignerConfigBuilder, ModelConfig
from data_designer.config.models import ChatCompletionInferenceParams
from data_designer.config.seed_source_types import LocalFileSeedSource

def load_config_builder() -> DataDesignerConfigBuilder:
    model = ModelConfig(
        alias="gemini", model="gemini-2.5-flash-lite",
        inference_parameters=ChatCompletionInferenceParams(
            max_parallel_requests=4, temperature=0.7, max_tokens=512,
        ),
        provider="gemini", skip_health_check=True,
    )
    builder = DataDesignerConfigBuilder()
    builder.add_model_config(model)
    builder.with_seed_dataset(LocalFileSeedSource(path="data/input/products.csv"))

    # Column 1: classify product type (depends on name + description)
    builder.add_column(
        column_type="llm-text", name="product_type",
        prompt="Classify this product: name={{ name }}, desc={{ description }}. Return one of: Electronics, Clothing, Home, Food.",
        model_alias="gemini",
    )
    # Column 2: generate marketing copy (depends on product_type — ordering matters)
    builder.add_column(
        column_type="llm-text", name="marketing_copy",
        prompt="Write a one-sentence marketing tagline for {{ name }} ({{ product_type }}): {{ description }}",
        model_alias="gemini",
        depends_on=["product_type"],  # ensures product_type is generated first
    )
    return builder
```

### Monitoring long DataDesigner runs
```python
import subprocess
from pathlib import Path

def run_with_progress(config_path: str, num_records: int, artifact_path: str, log_path: str = "/tmp/dd_progress.log"):
    """Run DataDesigner create with progress logging."""
    with open(log_path, "w") as log:
        proc = subprocess.Popen(
            ["data-designer", "create", config_path,
             "--num-records", str(num_records),
             "--artifact-path", artifact_path],
            stderr=log, stdout=log,
        )
    # Progress is logged in format:
    #   "🌦️ llm-text column 'X' progress: N/M (P%) complete, N ok, 0 failed, R rec/s, eta Ts"
    # Monitor with: tail -f /tmp/dd_progress.log
    return proc
```

**Reading progress:** DataDesigner logs progress lines with emoji weather indicators:
- 🌧️ = early (<25%), 🌦️ = progressing (25-50%), ⛅ = halfway (50-75%), 🌤️ = almost done (75-95%), ☀️ = complete
- Each line includes: completed/total, ok/failed counts, records/second, ETA
- For agent use: run in background, monitor with `tail -f`, check `proc.poll()` for completion

### Legacy: batch_synthesize (reference only)
```python
# For simple fill operations when DataDesigner is not installed:
# python batch_synthesize.py input.csv output.csv --config config.json \
#   --mode fill-sentinels --sample-size 20 --dry-run
# See batch_synthesize.py source for full CLI args
```

## Procedures [Interactive mode]

> **DataDesigner workflow** — the agent owns the terminal throughout.

1. **Resolve CLI** — `command -v data-designer 2>/dev/null || (test -x .venv/bin/data-designer && realpath .venv/bin/data-designer) || echo CLI_NOT_FOUND`. If not found, guide install: `pip install data-designer`.
2. **Discover schemas** — Run `data-designer agent context` to learn available model aliases, column types, sampler types, validators, and processors. Inspect schemas for every type you plan to use. Never guess types or parameters.
3. Read this SKILL.md → assess feasibility per column
4. Read `references/recipe_patterns.md` → pick template matching the task
5. `mkdir -p workspace/configs` then write recipe as `workspace/configs/<name>.py` with `load_config_builder()` function
6. Edit the recipe for user's data (seed path, column prompts, model alias, judges if needed)
7. `data-designer validate workspace/configs/<name>.py` — expect "✅ Configuration is valid"
8. `data-designer preview workspace/configs/<name>.py --num-records 5 --save-results --artifact-path workspace/artifacts/preview`
9. **Review preview quality** — load `dataset.parquet` from preview results. Check for:
   - **Diversity**: mode collapse (records clustering around same patterns/phrasings), structural monotony (same template across all records), sampler effectiveness
   - **Data quality**: instruction compliance (follows prompt constraints), internal consistency (data within a record agrees with itself), encoding integrity, plausibility
   - **Design choices**: right column types being used (e.g., sampler instead of LLM for fixed-set values)
   Quality is statistical, not per-record — fix systemic issues that affect many records, don't chase cosmetic flaws in individual ones.
10. Compute estimate (local models = $0, cloud models: extrapolate from preview token counts × target rows)
11. **PAUSE (always) — Preview Gate (MANDATORY):** Show cost estimate + sample rows + quality assessment. Wait for user approval.
12. `data-designer create workspace/configs/<name>.py --num-records <N> --artifact-path workspace/artifacts/run_001`
13. Save checkpoint with provenance metadata (model, prompt template, row count, quality scores, cost)
14. *(If recipe includes LLMJudge column)* Check judge calibration: are scores consistent across similar-quality records? Does the judge catch visible problems?
15. Present results to user: row count, sample output, quality scores (if judge present), cost
16. If quality < 70% threshold → modify prompt/few-shot in config, loop to step 7

**When DataDesigner is not installed:** Display install guidance (`pip install data-designer`). For simple fill operations, `batch_synthesize.py` remains available as a legacy fallback.

## Triggered by Findings

This skill is often invoked after profiling findings (from magic-data-profiling or explore mode). When routed here from findings:
- sentinel_values → fill-sentinels mode
- missing_values → fill-missing mode
- Translation/annotation request → transform mode with appropriate prompt

Carry the decision context (columns, sentinel patterns, approach) into the synthesis config.

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `synthesis_config.py` | B | `python3 synthesis_config.py config.json --validate-only` | `--output plan.json` to save execution plan |
| `enrich_from_reference.py` | B | `python3 enrich_from_reference.py data.csv enriched.csv --reference-paths ref.csv --source-key id --reference-key ref_id` | `--match-type fuzzy --fuzzy-threshold 85` for name matching; `--join-config config.json` for multi-dataset joins. No LLM calls — purely deterministic |
| `validate_synthetic.py` | B | `python3 validate_synthetic.py synthetic.csv report.json --original-path original.csv` | `--criteria-json` + `--agent-yaml` to enable LLM-as-judge (opt-in, NOT automatic); `--sentinel-patterns` to check sentinel leakage. Caveat: `detect_approach()` auto-routes text columns to LLM-judge even without `--agent-yaml` — statistical-only mode is reliable only for numeric/categorical datasets |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `batch_synthesize.py` | Multi-column LLM synthesis with checkpoint/resume | Requires config JSON; SKILL.md says "legacy reference only"; cost accumulator with `--max-cost` abort |
| `generate_column.py` | Per-row LLM value generation | `--column` + `--agent-yaml` both required and fully task-specific; per-row cost accumulation; `--dry-run` token/cost estimation |

**Utility (unchanged):**

| Script | Notes |
|--------|-------|
| `synthesis_prompt_builder.py` | Library module with CLI wrappers for debugging; primarily imported by other scripts |

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For synthesis specifically:** Synthesis involves LLM API calls (cost, time) and produces content that cannot be regenerated identically. The judgment here almost always lands on "yes, checkpoint":
- Save after preview gate passes — preserves the approved sample for reference
- Save after full generation completes — the primary synthesis result
- Save partial results on failure — DataDesigner writes completed batches to `tmp-partial-parquet-files/` that should be recovered before retrying

**Suggested names:** `ckpt_synthesis_preview.csv`, `ckpt_synthesis_complete.csv`, `ckpt_synthesis_partial.csv`.

Include provenance metadata: model used, prompt template, row count, quality scores, cost estimate.

**Batch synthesis checkpointing (>50 rows):**

For long-running synthesis, checkpoint incrementally rather than only at completion:

| Dataset Size | Checkpoint Strategy |
|-------------|-------------------|
| < 50 rows | Checkpoint once at completion — preview is the safety net |
| 50–500 rows | Let DataDesigner handle partials via `tmp-partial-parquet-files/`; checkpoint merged result at completion |
| 500–5,000 rows | Split into batches of 100–500; checkpoint after each batch; merge at end |
| > 5,000 rows | Split into batches; checkpoint after each; consider parallel batches with separate artifact paths |

**Resuming from partial results:** DataDesigner writes completed batches to `tmp-partial-parquet-files/` within the artifact path. If a run is interrupted:
1. List parquet files in the artifact directory — each contains a completed batch
2. Count completed rows vs total seed rows
3. Create a new seed file with only the remaining rows (filter by ID/index)
4. Run DataDesigner on the reduced seed; merge with existing partials after completion

**Merge pattern:**
```python
from pathlib import Path
import pandas as pd

def merge_partial_results(artifact_dir: str, seed_df: pd.DataFrame, id_col: str = None) -> pd.DataFrame:
    """Merge partial DataDesigner results from interrupted runs."""
    partials = sorted(Path(artifact_dir).rglob("*.parquet"))
    if not partials:
        return pd.DataFrame()
    merged = pd.concat([pd.read_parquet(p) for p in partials], ignore_index=True)
    if id_col and id_col in merged.columns:
        merged = merged.drop_duplicates(subset=[id_col], keep="last")
    return merged
```

## Self-Healing

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `data-designer` not found | Package not installed | `pip install data-designer` |
| Preview returns empty | Config error or model misconfigured | Run `data-designer validate` first |
| Quality < 60% across rubrics | Prompt too vague or wrong model | Add few-shot, refine prompt, try larger model |
| Cost estimate too high | Too many rows or expensive model | Reduce num_records, switch to local model ($0), or use cheaper cloud model |
| `CostLimitExceeded` (legacy) | `--max-cost` hit in batch_synthesize | Checkpoint written; adjust budget or `--resume` |
| Zero rows processed | Wrong mode (fill-missing vs fill-sentinels) | Check if values are NaN vs string sentinels |
| `Failed to load model` (LM Studio) | Model unloaded due to memory pressure or another model loaded | 1. Save partial results (check `tmp-partial-parquet-files/`). 2. Ask user to reload the model in LM Studio. 3. If GOOGLE_API_KEY is set, offer Gemini as fallback. |
| Connection refused / timeout | LLM endpoint is down or unreachable | 1. Health check: `curl -s <endpoint>/v1/models`. 2. Save partial results. 3. If local → suggest cloud fallback. If cloud → suggest local fallback. |
| HTTP 429 / rate limit | Too many requests to cloud API | Wait with backoff (30s, 60s, 120s). After 3 retries, save partial and stop. Suggest reducing `max_parallel_requests` to 1. |
| HTTP 401/403 / auth error | API key invalid, expired, or missing | Guide user to check/refresh the key (`echo $GOOGLE_API_KEY`). Offer local model as zero-cost alternative. |
| Process killed / OOM (local) | Model too large for available RAM | Save partial results. Suggest a smaller model (e.g., 8B instead of 35B) or switch to cloud API. |

### Failure Recovery Procedure

When `data-designer create` fails mid-generation, follow this sequence:

1. **Health check** — verify the LLM endpoint is reachable:
   ```bash
   curl -s http://localhost:1234/v1/models  # local
   curl -s -H "Authorization: Bearer $GOOGLE_API_KEY" https://generativelanguage.googleapis.com/v1beta/openai/models  # Gemini
   ```

2. **Check partial output** — DataDesigner saves completed batches:
   ```bash
   ls <artifact-path>/dataset/tmp-partial-parquet-files/
   # Each batch_NNNNN.parquet contains already-generated rows
   ```

3. **Recover partial results** — merge completed batches into a checkpoint:
   ```python
   import pandas as pd
   from pathlib import Path
   partials = sorted(Path("<artifact-path>/dataset/tmp-partial-parquet-files").glob("*.parquet"))
   if partials:
       recovered = pd.concat([pd.read_parquet(p) for p in partials], ignore_index=True)
       recovered.to_csv("data/checkpoints/ckpt_synthesis_partial.csv", index=False)
       print(f"Recovered {len(recovered)} rows from {len(partials)} batches")
   ```

4. **Decide next action**:
   - **Transient failure** (rate limit, brief network issue) → retry after backoff
   - **Persistent failure** (model unloaded, key expired) → fix the issue, then resume
   - **Fallback** — switch provider:
     - Local failed + `GOOGLE_API_KEY` set → offer Gemini
     - Cloud failed + LM Studio running → offer local model
   - **Resume** — re-run with reduced count on filtered seed:
     ```bash
     data-designer create <config> --num-records <remaining_rows> --artifact-path <new_path>
     ```

## Reference Guides

| Doc | When to Read |
|-----|-------------|
| `references/recipe_patterns.md` | **MANDATORY** before step 2 — choosing which template; also the DD recipe-pattern catalog (trajectory capture, rejection sampling, multi-judge, distractor injection, …) |
| `references/datadesigner_capabilities.md` | When a task needs a DD primitive beyond the recipe templates — traces, MCP tool-use, person sampling, agent-rollout ingestion, workflow chaining, seed-source expansion, async/AIMD concurrency |
| `references/cost_control.md` | When estimating cost for cloud models |
| `references/quality_bridge.md` | When recipe includes LLMJudge column |
| `references/domain_knowledge.md` | When configuring seeds, Jinja prompts, or conditional sampling |
| `references/magic_checkpoints.md` | When saving DD output to MAGIC workspace |

**Do NOT Load** for DataDesigner workflows:
- `references/script_detailed_reference.md` — legacy batch_synthesize CLI reference (deleted; use DataDesigner CLI instead)
