"""
Q&A Generation Template — DataDesigner Recipe
==============================================
Generates question-answer pairs from seed data.
Use for: retrieval datasets, reading comprehension, FAQ generation, RLHF preference data.

Adapt this template:
1. Change seed path to your input data
2. Edit the "question" prompt to generate natural questions from your domain
3. The "answer" column references {{ word }} and {{ question }} from earlier columns
4. Change model_alias to match your configured model

Usage:
    data-designer validate templates/qa_generation_template.py
    data-designer preview templates/qa_generation_template.py --num-records 5
    data-designer create templates/qa_generation_template.py --num-records 100
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
    """Build a DataDesigner config for Q&A pair generation."""

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

    # --- Column 1: generate a natural question answered by this item ---
    builder.add_column(
        column_type="llm-text",
        name="question",
        prompt=(
            "You are an expert creating quiz questions from structured data. "
            "The answer to your question is '{{ text }}' "
            "(category: '{{ category }}', label: '{{ label }}'). "
            "Write a clear, natural question that this item would answer. "
            "Output ONLY the question — no preamble, no quotes."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    # --- Column 2: generate a complete answer referencing the item and question ---
    builder.add_column(
        column_type="llm-text",
        name="answer",
        prompt=(
            "You are a helpful assistant. "
            "Question: {{ question }} "
            "Answer this question using the item '{{ text }}' "
            "(category: '{{ category }}'). "
            "Write a complete, informative answer. "
            "Output ONLY the answer — no preamble, no quotes."
        ),
        model_alias="local-text",
        extract_reasoning_content=True,
    )

    return builder
