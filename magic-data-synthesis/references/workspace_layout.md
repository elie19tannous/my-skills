# DataDesigner Workspace Layout

Example workspace structure for a synthesis project.

## Directory Structure

```
workspace/my-project/
├── configs/
│   ├── reasoning_trace.py       # Recipe config (load_config_builder pattern)
│   └── domain-knowledge.yaml    # Optional domain knowledge
├── data/
│   ├── input/
│   │   └── train.csv            # Seed data
│   └── checkpoints/
│       ├── synthesized.parquet  # DD output saved as MAGIC checkpoint
│       └── synthesized.meta.json
├── artifacts/
│   ├── preview/
│   │   ├── dataset.parquet      # 5-row preview output
│   │   └── metadata.json        # Token usage, cost, timing
│   └── run_001/
│       ├── dataset.parquet      # Full run output
│       └── metadata.json        # Final cost + quality
└── workspace_state.md           # Lifecycle tracking
```

## Template Editing Guide

When adapting a recipe template from `templates/`:

### Step 1: Copy template
```bash
cp skills/magic-data-synthesis/templates/reasoning_trace_template.py \
   workspace/my-project/configs/reasoning_trace.py
```

### Step 2: Edit the recipe

Key customization points (marked with comments in templates):

| What to change | Where in config | Example |
|---|---|---|
| Seed data source | `add_seed(LocalFileSeedSource(...))` | Change `path` to your CSV/JSONL |
| Column prompts | `LLMTextColumnConfig(prompt=...)` | Reference your seed columns via `{{ col_name }}` |
| Model | `model_alias` on each column | Match an alias in your model config |
| Judge rubrics | `LLMJudgeColumnConfig(scores=[...])` | Define domain-specific quality criteria |
| Output columns | Column `name` fields | Match your target schema |

### Step 3: Validate
```bash
data-designer validate workspace/my-project/configs/reasoning_trace.py
```

### Step 4: Preview (5 rows)
```bash
data-designer preview workspace/my-project/configs/reasoning_trace.py \
  --num-records 5 --save-results \
  --artifact-path workspace/my-project/artifacts/preview
```

### Step 5: Check cost estimate
```python
from cost_utils import estimate_from_preview
import json

meta = json.load(open("workspace/my-project/artifacts/preview/metadata.json"))
estimate = estimate_from_preview(meta, full_num_records=9500)
print(f"Estimated cost: ${estimate:.2f}")
```

### Step 6: Full run (after PAUSE approval)
```bash
data-designer create workspace/my-project/configs/reasoning_trace.py \
  --num-records 9500 \
  --artifact-path workspace/my-project/artifacts/run_001
```

## Model Configuration

DataDesigner uses model aliases defined at config level. MAGIC translates env vars:

| MAGIC env var | DD equivalent |
|---|---|
| `OPENAI_API_KEY` | `ModelProvider(name="openai", api_key=...)` |
| `NVIDIA_API_KEY` | `ModelProvider(name="nvidia", api_key=...)` |
| `MAGIC_LLM_BASE_URL` | `ModelProvider(name="openai", base_url=...)` for local models |

Local models (LM Studio, vLLM) use the OpenAI-compatible provider with custom `base_url`.
