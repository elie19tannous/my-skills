# DataDesigner Capabilities — Full Engine Surface

> **Why this doc exists:** the synthesis recipes use ~5 column types, but DataDesigner (DD)
> is a much larger engine. This is the canonical inventory of the *whole* surface so the
> agent can reach for the right primitive (traces, MCP, person sampling, rollout ingestion,
> chaining) instead of hand-rolling it. Read `references/recipe_patterns.md` first for *which
> template*; read this when a task needs a capability the templates don't already wire up.
>
> All class names are exact (verified against live v0.6.1 docs + repo internals).

## Engine Identity

| Attribute | Value |
|---|---|
| PyPI package | `data-designer` (`pip install data-designer`) |
| Version targeted | **0.6.1** — skill pins **DD ≥ 0.6** |
| License | Apache-2.0 |
| Repo | `NVIDIA-NeMo/DataDesigner` (github.com/NVIDIA-NeMo/DataDesigner) |
| Python | ≥ 3.10 (skill targets 3.12+) |
| Deployment | **Library mode** (assumed) — microservice mode is out of scope |
| Workflow | CLI `validate` → `preview` → `create`; Python `DataDesignerConfigBuilder` + `DataDesigner` |
| Agent context | `data-designer agent context` emits a curated API surface for coding agents — run it (SKILL.md step 2) before writing any config; never guess types/params |

**Package split (gotcha):** `data_designer` is a namespace across three installed packages —
`data-designer-config` (Pydantic schemas, `DataDesignerConfigBuilder`) → `data-designer-engine`
(generation, DAG, MCP, AIMD) → `data-designer` (interface `DataDesigner`, CLI). Dependency flow
is one-way; plugins must not import the interface layer.

Canonical entry points (report 08): `DataDesigner.validate()`, `.preview()`, `.create()`;
`DataDesignerConfigBuilder.add_model_config()` / `.add_column()` / `.with_seed_dataset()` /
`.add_processor()` / `.add_tool_config()` / `.build()`. (Verified against installed v0.6.0:
the model method is `add_model_config()`, not `add_model()`.)

---

## 1. Column Types (11)

All inherit `SingleColumnConfig` (shared: `name`, `drop`, `column_type` discriminator;
read-only computed `required_columns` / `side_effect_columns`). Columns form a DAG: deps are
auto-extracted from `{{ jinja }}` references — **never set `required_columns` manually** (custom
columns declare deps in the decorator). Legend for stage relevance: PT=pre-training,
CPT=continued-pretraining, SFT, RL, RSN=reasoning, EVAL, MM=multimodal.

| Column | Config class | What it does | LLM-data use | Stage | Skill today |
|---|---|---|---|---|---|
| LLM-Text | `LLMTextColumnConfig` | Free-form text from a Jinja prompt | core generation primitive | all | ✅ used |
| LLM-Code | `LLMCodeColumnConfig` | Code in a target lang; auto-strips markdown fences | code SFT, RSN | SFT, RSN | ✅ used |
| LLM-Structured | `LLMStructuredColumnConfig` | JSON **guaranteed** to match a Pydantic model / JSON schema (`output_format`) | schema-locked records, JSON-repair, tool args | SFT, EVAL, agentic | ◑ underused |
| LLM-Judge | `LLMJudgeColumnConfig` | LLM-as-judge scoring across rubrics; score read as `{{ col.ScoreName.score }}` | quality filtering, rejection sampling | EVAL, RL, all | ✅ used |
| Sampler | `SamplerColumnConfig` | Statistical/categorical values, no LLM call (§2) | diversity axes, demographics | all | ◑ 3 of 14 |
| Expression | `ExpressionColumnConfig` | Deterministic Jinja transform (`expr`) | score extraction, derived/flatten | all | ✅ used |
| Validation | `ValidationColumnConfig` | Annotates pass/fail vs rules; never mutates data (§validators) | code/CoT verification | SFT-code, RSN | ◑ code-only |
| Seed Dataset | `SeedDatasetColumnConfig` | Marks columns sourced from seed data; DAG roots (§4) | ground generation in real data | all | ◑ 2 of 6 sources |
| Embedding | `EmbeddingColumnConfig` | Dense vectors (`target_column`, `embedding_model`) | dedup, leakage/similarity | PT (dedup), EVAL | ❌ unused |
| Image | `ImageColumnConfig` | Image gen / image-to-image (`extra_body`, `multi_modal_context`) | multimodal alignment | MM | ❌ unused (DEFERRED) |
| Custom | `CustomColumnConfig` | Arbitrary logic via `@dd.custom_column_generator`; `allow_resize` 1:N/N:1 | escape hatch, row explosion | all | ◑ partial |

**Column lifecycle:** `[Seed / Sampler]` (roots) → `[Expression / LLM]` (middle) →
`[Validation / Judge / Embedding]` (leaves). Side-effect columns (`{name}__trace`,
`{name}__reasoning_content`) generate in their parent's pass.

**`drop=True` pattern:** generate a scaffolding column (prompt context, raw person object,
intermediate draft), reference it downstream, then exclude it from output. Idiomatic — keeps the
final schema clean.

**LLM column shared knobs** (Text/Code/Structured/Judge): `with_trace` (§6), `tool_alias` (§7),
`extract_reasoning_content` (§6), `multi_modal_context`. SQL/code dialects via `CodeLang`:
`PYTHON`, `SQL_POSTGRES`, `SQL_ANSI`, `SQL_MYSQL`, `SQL_SQLITE`, `SQL_TSQL`, `SQL_BIGQUERY`.

---

## 2. Samplers (14 + conditional)

`SamplerColumnConfig(sampler_type=dd.SamplerType.X, params=...)`. No LLM call — fast,
deterministic, the cheapest diversity axis. (See report 01/08 for the full enum.)

| Sampler | Params class | Generates | Skill today |
|---|---|---|---|
| `UUID` | `UUIDSamplerParams` | UUID4 ids | ◑ |
| `Category` | `CategorySamplerParams` | categorical (optional `weights`) | ✅ used |
| `Subcategory` | `SubcategorySamplerParams` | hierarchical parent→child | ✅ used |
| `Uniform` | `UniformSamplerParams` | int/float range (`low`, `high`) | ◑ |
| `Gaussian` | `GaussianSamplerParams` | normal (`mean`, `std_dev`) | ◑ |
| `Bernoulli` | `BernoulliSamplerParams` | binary (`probability`) | ✅ used |
| `Bernoulli Mixture` | `BernoulliMixtureSamplerParams` | binary from mixture components | ❌ |
| `Binomial` | `BinomialSamplerParams` | successes in n trials | ❌ |
| `Poisson` | `PoissonSamplerParams` | count data (lambda) | ❌ |
| `Scipy` | `ScipySamplerParams` | **any `scipy.stats` distribution** — full escape hatch | ❌ |
| `Person` | `PersonSamplerParams` | census-grounded persona (§5) | ❌ |
| `PersonFromFaker` | `PersonFromFakerSamplerParams` | Faker persona (§5) | ❌ |
| `Datetime` | `DatetimeSamplerParams` | timestamp in range (`start_date`, `end_date`) | ◑ |
| `Timedelta` | `TimeDeltaSamplerParams` | durations | ❌ |

**Conditional sampling** — the distribution changes based on an already-generated column,
producing cross-column correlations with **no LLM/code cost**. Two surfaces appear in the docs vs
the skill: research report 01 shows `params=dd.ConditionalGaussianSamplerParams(conditions={...})`;
`references/domain_knowledge.md` documents the skill's working form `conditional_params={"col == 'x'": Params(...)}`.
**Verified against installed v0.6.0:** `ConditionalGaussianSamplerParams` is *not* exported in the
public `data_designer.config` namespace — use the `conditional_params=` form the skill already
validates; treat the report-01 name as the underlying mechanism only. The dependency column is
auto-added to `required_columns`.

> Prefer conditional samplers over a custom column for purely numeric/categorical correlations —
> faster and no model overhead.

---

## 3. Validators

`ValidationColumnConfig(target_columns=[...], validator_type=..., validator_params=...,
batch_size=...)`. Annotates a `{name}__is_valid` (and type-specific) columns; **does not mutate
or filter** — filtering happens post-generation (§6). Three validator types:

| Type | Params class | Does | Skill today |
|---|---|---|---|
| `"code"` | `CodeValidatorParams(code_lang=...)` | Ruff (Python) / SQLFluff (SQL) lint → `__is_valid`, `__python_linter_score` (0–10), `__python_linter_severity`, `__python_linter_messages` | ✅ used (ruff) |
| `"callable"` | `LocalCallableValidatorParams(validation_function=fn, output_schema=None)` | runs `fn(df)->df` (must return `is_valid`); maximally flexible | ❌ unused |
| `"remote"` | `RemoteValidatorParams(endpoint_url, timeout, max_retries, retry_backoff, max_parallel_requests, output_schema)` | POST batches to an HTTP validator; auto-retries 429/5xx | ❌ unused |

`batch_size` guidance: code 5–20, callable 10–50, remote 1–10. The callable/remote validators are
the native path for **programmatic CoT/answer verification** (reasoning stage) — currently
hand-rolled in pandas.

---

## 4. Seed Sources (6) + strategies

`config_builder.with_seed_dataset(source, sampling_strategy=..., selection_strategy=...)`. Every
seed column becomes a Jinja variable automatically. The skill treats DD as **one seed source per
pipeline** (see `references/domain_knowledge.md`); plan reference-document injection around that.

| Source | Class | Notes | Skill today |
|---|---|---|---|
| Local file | `LocalFileSeedSource(path=)` | csv/parquet/json/jsonl + globs; YAML-serializable | ✅ used |
| DataFrame | `DataFrameSeedSource(df=)` | in-memory; **NOT YAML-serializable** (persist to parquet first) | ✅ used |
| HuggingFace | `HuggingFaceSeedSource(path=, token=None)` | streams HF Hub directly; path is `datasets/<org>/<repo>/data/<split>.parquet` (not `<org>/<repo>`); `token` only for private/gated | ❌ unused |
| Directory | `DirectorySeedSource(path=, file_pattern=, recursive=True)` | one row per file, **metadata only** (`source_path`, `relative_path`, `file_name`, ...) | ❌ unused |
| File contents | `FileContentsSeedSource(path=, file_pattern=, encoding="utf-8")` | like Directory **plus** full text in a `content` column — **document-extraction primitive** | ✅ used |
| Agent rollout | `AgentRolloutSeedSource(format=dd.AgentRolloutFormat.X)` | ingests real agent traces as rows (§7) | ❌ unused |

**Sampling strategy** (`sampling_strategy=`): `SamplingStrategy.ORDERED` (default; cycles back to
row 0 when `num_records > len(seed)`) or `SamplingStrategy.SHUFFLE`. There is **no
without-replacement** stop — cycling is always the behavior; for 1:1 mapping set
`num_records <= len(seed)`.

**Selection strategy** (`selection_strategy=`) — slice/partition a seed for distributed gen:
- `IndexRange(start=, end=)` — contiguous row range.
- `PartitionBlock(index=, num_partitions=)` — one of N equal blocks; clean scale-out (worker i
  generates partition i, no overlap).

---

## 5. Person Sampling

Two backends, both via `SamplerColumnConfig`. Mark `drop=True` and promote fields with
`ExpressionColumnConfig` to keep output flat. The user-side **persona-seeding** pattern ("who is
asking") is NVIDIA's diversity primitive across Nemotron post-training (SFT, safety/refusal,
instruction-following, tool-use rollouts).

| Concern | `PersonFromFaker` | `Person` (Nemotron-Personas) |
|---|---|---|
| Enum / params | `PERSON_FROM_FAKER` / `PersonFromFakerSamplerParams` | `PERSON` / `PersonSamplerParams` |
| Backend | Faker library | PGM-trained, census-grounded (~53M personas, 9 locales) |
| Setup | none | NGC API key + `data-designer download personas --locale ...` |
| Realism | uncorrelated PII | correlated demographics (no 18-yo with 30-yr career) |
| Locales | all Faker locales | 9: `en_US`, `en_IN`, `en_SG`, `fr_FR`, `hi_Deva_IN`, `hi_Latn_IN`, `ja_JP`, `ko_KR`, `pt_BR` |
| Params | `locale` (req), `age_range`, `sex` | `locale` (req), `sex`, `city`, `age_range`, `with_synthetic_personas`, `select_field_values` |
| OCEAN / narrative traits | no | yes, when `with_synthetic_personas=True` |
| YAML-serializable | yes | yes |
| Use | prototyping / no-NGC fallback | production demographic diversity |

`with_synthetic_personas=True` adds OCEAN Big-Five traits (`{{ person.openness.description }}`,
`.t_score`) plus domain persona one-liners (`professional_persona`, `healthcare_persona`,
`finance_persona`, ...). `select_field_values={"state": ["NY","CA"]}` slices demographics without
post-processing. **Gotcha (report 08):** `PersonSampler` raises `PersonSamplerConstraintsError` if
locale+sex+age+city is too narrow — handle it or fall back to Faker.

---

## 6. Pipeline Machinery

### Processors

`config_builder.add_processor(...)`; run in add-order at three lifecycle hooks —
`process_before_batch` / `process_after_batch` (row count **invariant**, else
`DatasetGenerationError`) / `process_after_generation` (row count may change — **the only safe
place to filter/dedup rows**). Two built-ins:

| Processor | Config class | Use |
|---|---|---|
| Drop columns | `DropColumnsProcessorConfig(name, column_names)` | remove cols (preserved in `dropped-columns/`); `drop=True` on a column is the shorthand |
| Schema transform | `SchemaTransformProcessorConfig(name, template)` | **native ChatML / ShareGPT / messages export** — Jinja `template` dict reshapes rows into the training format; renders per row (json.dumps→Jinja→json.loads) so a `messages` value is a real `list[dict]`, not a string. Output to `processors-files/{name}/` (verified DD 0.6); load with `results.load_processor_dataset("{name}")`. Materializes on `create()`, **not** `preview()`. |

`SchemaTransformProcessorConfig` is the native JSONL/ChatML conversion tool — prefer it over
hand-reshaping in pandas. Row filtering/dedup must be a custom processor's
`process_after_generation()` (no built-in filter/dedup processor).

### Workflow chaining (native generate→evaluate→filter→refine)

DD expresses multi-stage pipelines **two complementary ways**:

1. **Intra-config DAG (always available):** columns reference each other via `{{ }}`; the engine
   topo-sorts and runs them, with **per-column model routing** (each column picks its own
   `model_alias` — fast model for scaffolding, large model for the hard step). This is the native
   generate→evaluate→filter loop inside one config: LLM column → `LLMJudgeColumnConfig` →
   `ExpressionColumnConfig` extract → filter. Report 08: there is **no chaining of separate
   `DataDesigner` instances** — composition is one config with interdependent columns.
2. **`compose_workflow` stages (experimental):** `DataDesigner.compose_workflow(name)` →
   `.add_stage(stage_name, config_builder, num_records=, output_processors=[...], output="processor:<name>")`
   → `.run()` → `WorkflowResults`. Each stage runs a full `create()`, writes its own artifacts,
   and passes a selected parquet downstream as a `LocalFileSeedSource`. Use for processor-only
   stages (e.g. a ChatML reshape stage) or when a step depends on the *cleaned* output of another.
   **Caveats:** linear only (no DAG/branches/joins yet); no stage-level resume; use
   `results.export("x.jsonl")` not `push_to_hub()` for processor outputs.

> For most synthesis tasks the intra-config DAG is enough; reach for `compose_workflow` only when
> a processor-only boundary or staged seed hand-off is genuinely cleaner.

### Message traces

`with_trace=dd.TraceType.X` on any LLM column captures the conversation as a `{name}__trace`
side-effect column (a `list[dict]`, ChatML-shaped — not a string):

| `TraceType` | Captures |
|---|---|
| `NONE` (default) | nothing |
| `LAST_MESSAGE` | final assistant message only |
| `ALL_MESSAGES` | full history: system/user/assistant/tool, incl. `tool_calls` + tool results |

`with_trace=TraceType.ALL_MESSAGES` is **the** primitive for agentic/tool-use SFT — the trace *is*
the training datum, in standard ChatML, no extra transform. Tool-call `arguments` are a
JSON-encoded **string** inside the dict (`json.loads` to read fields).

### `extract_reasoning_content`

`extract_reasoning_content=True` on any LLM column produces `{name}__reasoning_content` (the final
assistant message's CoT, whitespace-stripped, `None` if absent). **This flag is dual-purpose:**

1. **Local-reasoning-model workaround** (SKILL.md rule): Qwen/DeepSeek-style local models put ALL
   output in the reasoning field, leaving `content` empty — you MUST set this flag (and keep
   `max_tokens ≥ 2048`) or get zero results with no error.
2. **CoT-capture feature** (reasoning stage): isolates chain-of-thought as its own column for
   CoT-distillation SFT and reasoning-quality filtering.

Combine with `with_trace` on the same column to keep both the full trace and the isolated CoT.

---

## 7. Agentic / Tool Use

### Live tool use via MCP (generate *new* trajectories)

Three components: **provider** → **ToolConfig** → **LLM column with `tool_alias`**. The engine runs
a tool-call loop (model requests call → engine executes → result appended → repeat) until a final
answer or the turn budget is hit.

| Piece | Class / field | Notes |
|---|---|---|
| Remote provider | `MCPProvider(name, endpoint, api_key, provider_type)` | `provider_type` = `"sse"` (default) or `"streamable_http"`; `api_key` references an env var |
| Local provider | `LocalStdioMCPProvider(name, command, args, env)` | launches an MCP server subprocess |
| Tool config | `ToolConfig(tool_alias, providers, allow_tools=None, max_tool_call_turns=5, timeout_sec=60.0)` | budgets + allowlist; attach via `DataDesignerConfigBuilder(tool_configs=[...])` or `add_tool_config()` |
| Enable on column | `LLMTextColumnConfig(..., tool_alias="...", with_trace=TraceType.ALL_MESSAGES)` | works on Text/Code/Structured/Judge |

Providers attach to the engine: `DataDesigner(mcp_providers=[...])`. Three independent safety
budgets, all on `ToolConfig`: `max_tool_call_turns` (default 5; parallel calls in one cycle = one
turn; **150** for deep research), `timeout_sec` (per call), `allow_tools` (capability allowlist —
scope a column to a tool subset to train targeted skills).

### Agent rollout ingestion (distill *existing* traces)

`AgentRolloutSeedSource(format=dd.AgentRolloutFormat.X)` ingests agent session files **directly off
disk** — no preprocessing — into a normalized row schema (`trace_id`, `messages`,
`tool_call_count`, `final_assistant_message`, ...).

| `AgentRolloutFormat` | Agent | Default path |
|---|---|---|
| `CLAUDE_CODE` | Claude Code | `~/.claude/projects` |
| `CODEX` | OpenAI Codex CLI | `~/.codex/sessions` |
| `HERMES_AGENT` | Hermes Agent | `~/.hermes/sessions` |
| `PI_CODING_AGENT` | Pi Coding Agent | `~/.pi/agent/sessions` (active path auto-resolved) |
| `ATIF` | ATIF / Harbor spec | explicit `path=` required |

This is a **zero-overhead path from our own Claude Code / OMC sessions to training data**.

### Rejection-sampling pattern (RL/agentic data)

Standard loop, all DD-native: generate trajectories (`with_trace=ALL_MESSAGES`, high temp) →
`LLMJudgeColumnConfig` scores → keep only high-value rows via a `recommended_for_sft` boolean
(e.g. *all 5 judge dims ≥ 4 AND `training_value == "high"`*). Distill rollouts by exploding one
trace into N rows with `CustomColumnConfig(allow_resize=True)` (one row per tool interaction), then
annotate/score/filter. **Trajectory length is a near-free quality signal** — shorter trajectories
correlate with correctness, so message count can filter as well as a judge (see report 04, MuSiQue
stats).

---

## 8. Extensibility & Infra

### Plugin system — capability documented, **NOT built in v1.x**

DD has a stable (v0.6.0) plugin system: three plugin types — Column Generator
(`SingleColumnConfig` + `ColumnGeneratorFullColumn`/`ColumnGeneratorCellByCell`), Seed Reader
(`SeedSource`/`FileSystemSeedReader`), Processor (`ProcessorConfig` + `Processor`) — discovered via
the `data_designer.plugins` entry-point group (a `Plugin(config_qualified_name, impl_qualified_name,
plugin_type=PluginType.X)` object). First-party example: `data-designer-retrieval-sdg` (RAG/embedding
SDG). A CLI catalog (`data-designer plugin list/search/install`) supports private catalogs.

> **Scope decision (proposal §6.3, X1):** authoring/publishing a MAGIC DD plugin is **EXCLUDED from
> v1.x** — it's a product decision, not a methodology-template task. Documented here so the agent
> knows the capability exists; **do not build it.** For one-off custom logic use the inline
> `@dd.custom_column_generator` decorator (the `Custom` column), not a packaged plugin.

### Multimodal / VLM stack — **DEFERRED to v1.5**

Full image-gen, image-to-image (an `ImageColumnConfig` can reference a prior image column as
context), and image/audio/video context (`multi_modal_context`) plus VLM long-doc recipes exist.
Per proposal §6.2 (D1) the whole multimodal stage is deferred — documented, not yet exercised.

### Async DAG engine + adaptive (AIMD) concurrency — reconcile with older parallelism guidance

From **v0.6.0 the async DAG engine is the default** (`DATA_DESIGNER_ASYNC_ENGINE=1`;
`AsyncTaskScheduler` dispatches each task the instant its deps are ready, overlapping independent
columns/rows). It uses **per-model AIMD** (Additive-Increase/Multiplicative-Decrease) concurrency:
drops ~75% on a 429, adds a slot after ~25 consecutive successes — it **auto-tunes** the right
concurrency level.

> **Reconciliation:** SKILL.md's fixed `max_parallel_requests` table predates v0.6 adaptive
> concurrency. On DD ≥ 0.6, `max_parallel_requests` is a **ceiling**, not a fixed level — AIMD
> starts conservative and ramps within it. Treat the SKILL.md values as starting ceilings; let
> AIMD self-tune. The one knob that still matters for slow self-hosted endpoints is `timeout`.
> (Sync engine remains available via `DATA_DESIGNER_ASYNC_ENGINE=0` for deterministic ordering.)

Model config recap (well-covered by the skill): `ModelConfig(alias, model, provider,
inference_parameters)`; `ChatCompletionInferenceParams` (`temperature`, `top_p`, `max_tokens`,
`max_parallel_requests`, `timeout`; temp/top_p accept `UniformDistribution`/`ManualDistribution`
for per-request variability) and `EmbeddingInferenceParams`. Default providers: `nvidia`, `openai`,
`openrouter`; Anthropic/vLLM/TGI/Together via custom `ModelProvider`.

> **Provider-specific notes (gemini).** Two empirically-observed quirks of the `gemini` provider
> (DD 0.6.0):
> - **`max_tokens`: use ≥ 512.** `gemini-flash-*` accounts for the output budget differently from
>   OpenAI-style providers — a cap that looks generous for a short output (e.g. `128` for a one-line
>   summary) can get consumed such that only ~3–4 output tokens are emitted, producing truncated
>   fragments. Seen live: `max_tokens=128` → `"all day),"`; the same config at `512` → a full
>   coherent sentence. Default to `≥ 512` for gemini even for short fields.
> - **Do not pass `seed`.** Gemini rejects the `seed` parameter with HTTP 400; omit it from
>   `ChatCompletionInferenceParams` (and any `extra_body`) when `provider="gemini"`.
