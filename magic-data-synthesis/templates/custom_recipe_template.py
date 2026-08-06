"""
Custom Recipe Template — DataDesigner Recipe Skeleton
======================================================
Starting point for building your own DataDesigner recipe from scratch.
Customization points are marked with "# ADAPT:" comments.

Steps to adapt:
1. Change the seed path to point to your input CSV/JSONL
2. Edit the model alias, name, and parameters for your provider
3. Add or remove columns to match your desired output schema
4. Edit each column's prompt to reference your seed columns via {{ column_name }}

Usage:
    data-designer validate templates/custom_recipe_template.py
    data-designer preview templates/custom_recipe_template.py --num-records 5
    data-designer create templates/custom_recipe_template.py --num-records 100
"""
from pathlib import Path
from data_designer.config.config_builder import (
    DataDesignerConfigBuilder,
    ModelConfig,
)
from pathlib import Path
from data_designer.config.models import ChatCompletionInferenceParams
from pathlib import Path
from data_designer.config.seed_source_types import LocalFileSeedSource


def load_config_builder() -> DataDesignerConfigBuilder:
    """Build a custom DataDesigner config. Adapt all sections marked with ADAPT."""

    # --- Model Config ---
    # ADAPT: change alias, model name, provider, and inference parameters.
    # Provider "local" expects a running LM Studio / vLLM endpoint at
    # http://localhost:1234/v1 configured in ~/.data-designer/model_providers.yaml.
    # Other supported providers: "gemini", "openai", "anthropic".
    local_model = ModelConfig(
        alias="local-text",                        # ADAPT: unique name for this model
        model="qwen/qwen3.5-35b-a3b",              # ADAPT: model identifier
        inference_parameters=ChatCompletionInferenceParams(
            max_parallel_requests=1,               # ADAPT: increase for cloud providers
            temperature=0.7,                       # ADAPT: 0.0 = deterministic, 1.0 = creative
            max_tokens=4096,                       # ADAPT: cap output length
            extra_body={"enable_thinking": False}, # ADAPT: remove for non-Qwen models
        ),
        provider="local",                          # ADAPT: "local" | "gemini" | "openai"
        skip_health_check=True,                    # ADAPT: set False to verify connectivity
    )

    builder = DataDesignerConfigBuilder()
    builder.add_model_config(local_model)

    # --- Seed Data ---
    # ADAPT: change seed path to your input file (CSV or JSONL).
    # Columns in the seed file become available as {{ column_name }} in prompts.
    seed = LocalFileSeedSource(path=str(Path(__file__).parent / "sample_seed.csv"))
    builder.with_seed_dataset(seed)

    # --- Output Column ---
    # ADAPT: rename "output", change the prompt, and reference your seed columns.
    # Add more builder.add_column(...) blocks for multi-column recipes.
    # Later columns can reference earlier columns via {{ column_name }}.
    builder.add_column(
        column_type="llm-text",
        name="output",                             # ADAPT: rename to your desired column name
        prompt=(
            "You are a helpful assistant. "
            # ADAPT: write your task description here.
            # Reference seed columns using {{ column_name }} syntax, e.g.:
            #   "Given the text '{{ text }}' and its category '{{ category }}'..."
            "Given the input '{{ text }}', generate a concise, accurate response. "
            "Output ONLY the result — no preamble, no quotes."
            # ADAPT: edit prompt above
        ),
        model_alias="local-text",                  # ADAPT: match the alias defined above
        extract_reasoning_content=True,            # ADAPT: set False for non-reasoning models
    )

    return builder
