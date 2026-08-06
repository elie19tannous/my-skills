# Domain Knowledge — Seeds, Jinja, Conditional Sampling, References

## Seed Datasets

DataDesigner supports one seed source per pipeline. Seed columns are auto-registered as DAG nodes — do not add them manually.

| Class | Use case |
|---|---|
| `dd.LocalFileSeedSource(path="...")` | CSV, Parquet, JSON, JSONL, or glob pattern on disk |
| `dd.HuggingFaceSeedSource(path="...", token=None)` | HuggingFace Hub dataset |
| `dd.DataFrameSeedSource(df=pandas_df)` | In-memory DataFrame — NOT serializable; convert to Parquet first |
| `dd.FileContentsSeedSource(path="...", file_pattern="*.md")` | File text contents as a column (`content`, `source_path`, `file_name`) |
| `dd.DirectorySeedSource(path="...", recursive=True)` | Directory of files |
| `dd.AgentRolloutSeedSource(format=dd.AgentRolloutFormat.CLAUDE_CODE)` | Claude/Codex/Hermes agent traces |

**Key rules:**
- Column names must be valid Jinja2 identifiers (snake_case).
- Paths resolve from **CWD at config load time**, not from the recipe file location.
- `DataFrameSeedSource` cannot be serialized — use `LocalFileSeedSource.from_dataframe(df, path)` to persist first.
- Use `sampling_strategy=dd.SamplingStrategy.SHUFFLE` to avoid row-order clustering in training data.

```python
config_builder.with_seed_dataset(
    dd.LocalFileSeedSource(path="workspace/myproject/data/input/train.csv"),
    sampling_strategy=dd.SamplingStrategy.SHUFFLE,
)
# Seed columns (e.g., "question", "answer") are now available as {{ question }}, {{ answer }}
```

## Jinja Templating in Prompts

All `prompt`, `system_prompt`, and `ExpressionColumnConfig.expr` fields support Jinja2.

```jinja2
{{ column_name }}                         # Seed or sampler column value
{{ structured_col.field_name }}           # Field access on LLMStructured output
{{ judge_col.ScoreName.score }}           # Judge score integer — .score is mandatory
{{ judge_col.ScoreName.reasoning }}       # Judge score rationale string
{% if has_input == 1 %}{{ input }}{% endif %}  # Bernoulli conditional (0 or 1)
{% if context %}Context: {{ context }}{% endif %}  # Truthiness check
{{ values | join(", ") }}                 # Join filter
{{ price | round(2) }}                    # Round filter
{{ product_info | jsonpath('$.features[0]') | first }}  # DD custom jsonpath filter
```

**Blocked in prompts:** `{% import %}`, `{% macro %}`, `{% set %}`, `{% extends %}`, `{% block %}`, nested `{% for %}`.

All column references are validated at compile time (`data-designer validate`). A missing reference is a compile error.

## Conditional Sampling

Use `conditional_params` on `SamplerColumnConfig` to produce category-specific values — the primary mechanism for domain-appropriate output variation.

```python
dd.SamplerColumnConfig(
    name="answer_format_hint",
    sampler_type=dd.SamplerType.CATEGORY,
    params=dd.CategorySamplerParams(values=["exact numerical"]),  # default
    conditional_params={
        "category == 'bit_manipulation'": dd.CategorySamplerParams(
            values=["8-bit binary string (e.g., 10010111)"]
        ),
        "category == 'numeral_system'": dd.CategorySamplerParams(
            values=["Roman numeral (e.g., XIV)"]
        ),
    },
)
# In prompts: "Answer format: {{ answer_format_hint }}"
```

Condition expressions are evaluated per-row against the Jinja sandbox. The condition string must reference an already-resolved column.

**Hierarchical sampling** (domain → sub-topic coherence):

```python
dd.SamplerColumnConfig(
    name="task_category",
    sampler_type=dd.SamplerType.SUBCATEGORY,
    params=dd.SubcategorySamplerParams(
        category="task_domain",   # parent column name
        values={
            "Writing":    ["summarization", "email drafting", "creative fiction"],
            "Coding":     ["debugging", "code review", "algorithm design"],
            "Analysis":   ["data interpretation", "comparison", "root cause"],
        },
    ),
)
```

## `domain-knowledge.yaml` Schema

Optional project-level knowledge file at `workspace/<project>/knowledge/domain-knowledge.yaml`.

```yaml
domain:
  name: "Mathematical Reasoning"

categories:
  - name: bit_manipulation
    answer_format: "8-bit binary string (e.g., 10010111)"
    answer_regex: "^[01]{8}$"
  - name: numeral_system
    answer_format: "Roman numeral (e.g., XIV)"

quality_criteria:
  - name: step_by_step
    description: "Reasoning must show individual steps"
    weight: 0.3
  - name: mathematical_accuracy
    description: "All intermediate calculations must be correct"
    weight: 0.4

reference_documents:
  - path: "data/reference/domain_guide.md"
    usage: "system_prompt"

seed_datasets:
  - path: "data/input/train.csv"
    columns: [prompt, answer]
    sampling: shuffle
```

YAML → DD config mapping:

| YAML field | DD config |
|---|---|
| `categories[].name` | `CategorySamplerParams(values=[...])` |
| `categories[].answer_format` | `conditional_params` per category |
| `quality_criteria[]` | `LLMJudgeColumnConfig.scores` entries |
| `reference_documents[usage=system_prompt]` | Read file → static `system_prompt` string |
| `seed_datasets[0].path` | `LocalFileSeedSource(path=...)` |

## Injecting Reference Documents into Prompts

**Critical constraint:** DD supports **only one seed source per pipeline**. If the seed slot holds structured data (e.g., `train.csv`), inject reference documents as **static strings** in `system_prompt`.

```python
from pathlib import Path

domain_guide = Path("workspace/myproject/data/reference/domain_guide.md").read_text()

dd.LLMTextColumnConfig(
    name="reasoning_trace",
    model_alias="gen",
    system_prompt=(
        "You are a mathematical reasoning expert.\n\n"
        f"Domain conventions:\n{domain_guide}\n\n"
        "Follow these conventions for all generated traces."
    ),
    prompt="Problem: {{ prompt }}\nAnswer format: {{ answer_format_hint }}",
)
```

Only use `FileContentsSeedSource` for references when you have **no structured seed** — it consumes the single seed slot.

Check for reference files before loading (reference loading is optional):

```python
ref_path = Path("workspace/myproject/data/reference/domain_guide.md")
domain_context = ref_path.read_text() if ref_path.exists() else ""
```
