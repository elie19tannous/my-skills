"""
Code Generation Template — DataDesigner Recipe
================================================
Generates code solutions with validation. Use for: code synthesis,
programming exercises, function generation with test cases.

Adapt this template:
1. Change seed data to your problem descriptions
2. Edit prompts for your target language/domain
3. Add ValidationColumnConfig for code execution checking (if needed)
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
    """Build a DataDesigner config for code generation with reasoning."""

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

    # ADAPT: change seed to your problem descriptions dataset
    seed = LocalFileSeedSource(path=str(Path(__file__).parent / "sample_seed.csv"))
    builder.with_seed_dataset(seed)

    # Column 1: Generate a coding problem related to the data
    builder.add_column(
        column_type="llm-text",
        name="problem",
        prompt=(
            "Given the data field '{{ text }}' (category: {{ category }}), write a short "
            "Python programming problem that involves processing or validating "
            "this type of data. Output ONLY the problem statement."
        ),
        model_alias="local-text",
    )

    # Column 2: Generate the solution code
    builder.add_column(
        column_type="llm-text",
        name="solution",
        prompt=(
            "Write a Python function that solves this problem:\n"
            "{{ problem }}\n\n"
            "Output ONLY the Python code — no explanation, no markdown fences."
        ),
        model_alias="local-text",
    )

    return builder
