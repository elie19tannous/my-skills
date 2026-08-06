"""
Instruction Tuning Template — DataDesigner Recipe
==================================================
Generates instruction-response pairs for supervised fine-tuning (SFT) datasets.
Use for: instruction following, chat fine-tuning, RLHF training data.

Adapt this template:
1. Change seed path to your input data
2. Edit the "instruction" prompt to generate domain-relevant tasks
3. The "response" column references {{ instruction }} and seed columns
4. Change model_alias to match your configured model

Usage:
    data-designer validate templates/instruction_tuning_template.py
    data-designer preview templates/instruction_tuning_template.py --num-records 5
    data-designer create templates/instruction_tuning_template.py --num-records 100
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
    """Build a DataDesigner config for instruction-tuning pair generation."""

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

    # --- Column 1: generate an instruction/task about the item ---
    builder.add_column(
        column_type="llm-text",
        name="instruction",
        prompt=(
            "You are creating training data for a domain-specific model. "
            "Given the item '{{ text }}' (category: '{{ category }}', "
            "label: '{{ label }}'), write a specific instruction "
            "or task that a user could be asked to complete. "
            "Examples: explain the concept, use it in a sentence, classify it, "
            "compare with a related item, or describe its properties. "
            "Output ONLY the instruction — no preamble, no quotes."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    # --- Column 2: generate the ideal response to the instruction ---
    builder.add_column(
        column_type="llm-text",
        name="response",
        prompt=(
            "You are a helpful assistant. "
            "Complete the following instruction about '{{ text }}': "
            "{{ instruction }} "
            "Provide a clear, accurate, and complete response. "
            "Output ONLY the response — no preamble, no meta-commentary."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    return builder
