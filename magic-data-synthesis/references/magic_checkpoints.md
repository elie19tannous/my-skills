# MAGIC Checkpoints — Saving DataDesigner Output

## Why Checkpoint Immediately After `create`

LLM generation cost is non-recoverable. DataDesigner writes a raw `dataset.parquet` under `artifacts/<name>/`, but this is not a MAGIC checkpoint. Translate to a MAGIC checkpoint immediately after `create` completes — before any post-processing — so recovery is possible if anything fails downstream.

## Checkpoint Translation — Inline One-Liner

After `data-designer create` finishes:

```python
python -c "
import glob, pandas as pd
from pathlib import Path

def save_checkpoint(df: pd.DataFrame, step: str, workspace: str = 'workspace'):
    existing = sorted(glob.glob(f'{workspace}/data/checkpoints/ckpt_*_*.parquet'))
    next_num = int(existing[-1].split('ckpt_')[1][:2]) + 1 if existing else 1
    out = Path(workspace) / 'data' / 'checkpoints' / f'ckpt_{next_num:02d}_{step}.parquet'
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f'Saved: {out}')

save_checkpoint(
    pd.read_parquet('workspace/<project>/artifacts/<run>/dataset.parquet'),
    'synthesized'
)
"
```

`save_checkpoint()` writes the canonical `ckpt_XX_synthesized.parquet` file to the workspace with auto-incremented prefix. Implement it inline in your script.

## Sidecar `.meta.json` Content

Save a sidecar alongside the checkpoint parquet. Minimum required fields:

```json
{
  "checkpoint": "ckpt_05_synthesized",
  "step": "synthesized",
  "model": "nvidia/nemotron-3-nano-30b-a3b",
  "rows": 9500,
  "columns": ["question", "reasoning_trace", "final_answer", "reasoning_judge_result"],
  "cost_usd": 7.83,
  "recipe": "workspace/myproject/configs/reasoning_trace.py",
  "dd_artifact_path": "workspace/myproject/artifacts/reasoning_trace_run1/",
  "created_at": "2026-04-17T14:32:00Z"
}
```

Source `cost_usd` from the final `metadata.json` in the DD artifact directory:

```python
python -c "
import json
meta = json.load(open('workspace/<project>/artifacts/<run>/metadata.json'))
# See cost_control.md for the full get_pricing() and price_from_metadata() implementations
inp_tokens = meta.get('input_tokens', 0)
out_tokens = meta.get('output_tokens', 0)
print(f'Tokens: {inp_tokens} in / {out_tokens} out')
"
```

## Checkpoint Naming Convention

MAGIC checkpoints use zero-padded two-digit prefix + step name:

```
ckpt_01_loaded.parquet
ckpt_02_profiled.parquet
ckpt_03_cleaned.parquet
ckpt_04_explored.parquet
ckpt_05_synthesized.parquet   ← DataDesigner output lands here
ckpt_05_synthesized.meta.json ← sidecar
```

`save_checkpoint()` handles auto-incrementing the prefix (see implementation above).

## Resume Pattern

If the synthesis run was interrupted after some batches completed, check for an existing checkpoint before re-running:

```python
python -c "
import glob, os
checkpoints = sorted(glob.glob('workspace/<project>/ckpt_*_synthesized.parquet'))
if checkpoints:
    latest = checkpoints[-1]
    print(f'Resume from: {latest}')
else:
    print('No checkpoint found — run from scratch')
"
```

DataDesigner writes incremental Parquet batches to `artifacts/<name>/` during generation. If a run was partially completed, the artifact directory may contain partial data — inspect row count before deciding whether to resume or restart.

For column-level resumption (e.g., a single LLM column failed): re-run with a modified recipe that excludes already-completed columns, then merge the partial outputs. This is uncommon — DataDesigner's `shutdown_error_rate=0.5` guard usually means either all columns complete or the run aborts early.

## Checkpoint Integrity Check

After saving, verify the checkpoint is readable and has the expected row count:

```python
python -c "
import pandas as pd
df = pd.read_parquet('path/to/ckpt_05_synthesized.parquet')
print(f'rows={len(df)}, cols={list(df.columns)}')
"
```

If row count is less than expected, the run may have been truncated — check the DD artifact `metadata.json` for `num_records` vs `num_records_generated`.
