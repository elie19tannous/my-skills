"""
Reasoning Trace Template — DataDesigner Recipe
===============================================
Generates chain-of-thought reasoning traces followed by a grounded definition.
Use for: training reasoning models, distillation datasets, rationale generation.

Adapt this template:
1. Change seed path to your input data
2. Edit column prompts to reference your seed columns via {{ column_name }}
3. The "definition" column references {{ reasoning }} from the first column
4. extract_reasoning_content=True captures output from thinking/reasoning models

Usage:
    data-designer validate templates/reasoning_trace_template.py
    data-designer preview templates/reasoning_trace_template.py --num-records 5
    data-designer create templates/reasoning_trace_template.py --num-records 100
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
    """Build a DataDesigner config for reasoning trace generation."""

    # --- Model Config ---
    local_model = ModelConfig(
        alias="local-text",
        model="qwen/qwen3.5-35b-a3b",
        inference_parameters=ChatCompletionInferenceParams(
            max_parallel_requests=1,
            temperature=0.7,
            max_tokens=4096,
            extra_body={"enable_thinking": False},
        ),
        provider="local",
        skip_health_check=True,
    )

    builder = DataDesignerConfigBuilder()
    builder.add_model_config(local_model)

    # --- Seed Data ---
    seed = LocalFileSeedSource(path=str(Path(__file__).parent / "sample_seed.csv"))
    builder.with_seed_dataset(seed)

    # --- Column 1: step-by-step reasoning trace ---
    # extract_reasoning_content=True captures output from reasoning/thinking models
    # that place content in the reasoning/thinking field rather than the main response.
    builder.add_column(
        column_type="llm-text",
        name="reasoning",
        prompt=(
            "You are a domain expert. "
            "Given the item '{{ text }}' (category: '{{ category }}', "
            "label: '{{ label }}'), reason step-by-step about its properties "
            "and classification. Think through: (1) key attributes and their significance, "
            "(2) how it relates to its category, (3) practical implications or use cases. "
            "Output your reasoning steps clearly, one per line."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    # --- Column 2: final definition grounded in the reasoning trace ---
    builder.add_column(
        column_type="llm-text",
        name="definition",
        prompt=(
            "You are a domain expert. "
            "Given the following reasoning about '{{ text }}': "
            "{{ reasoning }} "
            "Based on this reasoning, write a concise, accurate description "
            "for '{{ text }}'. Output ONLY the description — no preamble, no quotes."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    return builder
