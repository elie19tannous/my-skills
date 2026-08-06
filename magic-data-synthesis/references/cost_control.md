# Cost Control — Estimation, Gates, and Budget Tips

## PRICING_TABLE

All rates in $/1K tokens. Define this table inline in your script.

| Model alias | Input $/1K | Output $/1K |
|---|---|---|
| `gpt-4.1` | 0.002 | 0.008 |
| `gpt-5` | 0.003 | 0.012 |
| `gpt-4o` | 0.0025 | 0.010 |
| `gpt-4o-mini` | 0.00015 | 0.0006 |
| `nvidia/nemotron-3-nano-30b-a3b` | 0.0003 | 0.0003 |
| `claude-sonnet-4-20250514` | 0.003 | 0.015 |
| `claude-haiku-4-20250414` | 0.0008 | 0.004 |
| `ollama/*`, `lmstudio/*`, `local/*`, `localhost/*` | **0.00** | **0.00** |
| Any unknown model | 0.001 (default) | 0.004 (default) |

Local-prefix models cost $0. The `LOCAL_PATTERNS` check runs first in `get_pricing()`.

## Preview-Based Estimation Formula

DataDesigner's `preview` command runs the **full pipeline** on N=5 rows and records real token counts in `artifacts/preview/metadata.json`. This is more accurate than static tiktoken analysis because it uses the same prompts and model path as the full run.

```python
# From cost_utils.estimate_from_preview()
estimate = preview_cost * (full_N / preview_N)
```

Where:
- `preview_cost` = actual USD cost of the 5-row preview (computed from `metadata.json` token counts)
- `full_N` = number of records requested for the full run
- `preview_N` = number of preview records (default 5)

Inline usage during the workflow:

```bash
data-designer preview my_recipe.py --num-records 5 --save-results
```

```python
python -c "
import json
meta = json.load(open('artifacts/preview/metadata.json'))
preview_cost = meta.get('total_cost_usd', 0)
preview_n = meta.get('num_records', 5)
full_n = 9500
print(f'Estimated cost: \${preview_cost * (full_n / preview_n):.2f}')
"
```

## The PAUSE Gate Workflow

**Mandatory before every `data-designer create` call.** Steps:

1. Run preview: `data-designer preview <recipe> --num-records 5 --save-results`
2. Parse `artifacts/preview/metadata.json` for 5-row token counts.
3. Compute estimate via `estimate_from_preview(meta, full_N)`.
4. Present to user:

```
Pipeline: reasoning_trace (3 LLM columns), 9,500 rows
Preview:  5 rows, 14,200 tokens, $0.029
Est. full-run: ~$55 (nvidia/nemotron-3-nano-30b-a3b)
Est. time: ~45 min

Proceed? [A/B/C/D]
  A. Run full synthesis as configured
  B. Modify config (describe changes)
  C. Change model or recipe
  D. Cancel
```

Wait for explicit user approval before calling `data-designer create`.

## Example Cost Estimates (9,500-row reasoning trace, 3 LLM columns)

| Model | Est. cost |
|---|---|
| `nvidia/nemotron-3-nano-30b-a3b` | ~$7–8 |
| `gpt-4o-mini` | ~$10 |
| `gpt-4.1` | ~$129 |
| `claude-sonnet-4-20250514` | ~$232 |
| Local (ollama/lmstudio) | $0 |

## Budget Tips

**Use local models for prompt development.** Set model to `ollama/llama3` or any `local/` prefix — cost is $0. Validate prompts produce the right shape before switching to a cloud model.

**Preview validates prompt correctness cheaply.** A 5-row preview costs cents and catches Jinja template errors, malformed judge output, and bad model configs before a full run.

**Add LLM columns conservatively.** Each additional `LLMTextColumn` or `LLMJudgeColumn` multiplies cost per row. `LLMJudgeColumn` with multiple rubrics is one LLM call per row — adding rubrics to an existing judge column costs far less than adding a second judge column.

**`ValidationColumn` has zero LLM cost.** Use it freely for code/SQL syntax checks.

**Over-generate by ~1.3x if filtering post-generation.** If you plan to filter rows by quality score, generate extra rows upfront — it's cheaper than a second full run.

## Programmatic Access

Implement these utility functions inline in your script:

```python
PRICING_TABLE = {
    "gpt-4.1": (0.002, 0.008),
    "gpt-5": (0.003, 0.012),
    "gpt-4o": (0.0025, 0.010),
    "gpt-4o-mini": (0.00015, 0.0006),
    "nvidia/nemotron-3-nano-30b-a3b": (0.0003, 0.0003),
    "claude-sonnet-4-20250514": (0.003, 0.015),
    "claude-haiku-4-20250414": (0.0008, 0.004),
}
LOCAL_PREFIXES = ("ollama/", "lmstudio/", "local/", "localhost/")

def get_pricing(model: str) -> tuple[float, float]:
    if any(model.startswith(p) for p in LOCAL_PREFIXES):
        return (0.0, 0.0)
    return PRICING_TABLE.get(model, (0.001, 0.004))

def price_from_metadata(meta: dict) -> float:
    inp_rate, out_rate = get_pricing(meta.get("model", ""))
    return (meta.get("input_tokens", 0) * inp_rate + meta.get("output_tokens", 0) * out_rate) / 1000

def estimate_from_preview(meta: dict, full_num_records: int) -> float:
    preview_cost = price_from_metadata(meta)
    preview_n = meta.get("num_records", 5)
    return preview_cost * (full_num_records / preview_n)
```
