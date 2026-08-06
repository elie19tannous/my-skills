"""
Text Generation Template — DataDesigner Recipe
================================================
Generates text content for one or more columns based on seed data context.
Use for: filling missing values, translation, annotation, summarization.

Adapt this template:
1. Change seed path to your input data
2. Edit column prompts to reference your seed columns via {{ column_name }}
3. Change model_alias to match your configured model
4. Add LLMJudge for quality scoring if needed

Usage:
    data-designer validate templates/text_generation_template.py
    data-designer preview templates/text_generation_template.py --num-records 5
    data-designer create templates/text_generation_template.py --num-records 100
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
    """Build a DataDesigner config for text generation."""

    # --- Model Config ---
    # Adapt alias, model name, provider, and parameters.
    # Provider "local" must be configured in ~/.data-designer/model_providers.yaml
    # pointing to your LM Studio / vLLM endpoint (http://localhost:1234/v1).
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

    # --- Config Builder ---
    builder = DataDesignerConfigBuilder()
    builder.add_model_config(local_model)

    # --- Seed Data: adapt path to your input file ---
    seed = LocalFileSeedSource(path=str(Path(__file__).parent / "sample_seed.csv"))
    builder.with_seed_dataset(seed)

    # --- Column: text generation ---
    # Adapt prompt to reference your seed columns with {{ column_name }}
    # extract_reasoning_content=True captures output from reasoning models
    # that put all content in the reasoning/thinking field.
    builder.add_column(
        column_type="llm-text",
        name="description",
        prompt=(
            "You are a helpful assistant. "
            "Given the item '{{ text }}' with category '{{ category }}' "
            "and label '{{ label }}', provide a concise description. "
            "Output ONLY the description — no explanation, no quotes."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    return builder
