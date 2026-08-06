"""
Text Generation Template (Gemini) — DataDesigner Recipe
========================================================
Same as text_generation_template.py but configured for Google Gemini API.
Fast cloud model — ideal for CI and E2E testing.

Usage:
    export GOOGLE_API_KEY=your-key
    data-designer validate templates/text_generation_gemini_template.py
    data-designer preview templates/text_generation_gemini_template.py --num-records 5
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
    """Build a DataDesigner config for text generation using Gemini."""

    # --- Model Config: Gemini via Google AI Studio (OpenAI-compatible endpoint) ---
    gemini_model = ModelConfig(
        alias="gemini-text",
        model="gemini-flash-latest",  # ADAPT: change to your preferred Gemini model
        inference_parameters=ChatCompletionInferenceParams(
            max_parallel_requests=4,
            temperature=0.7,
            # Gemini accounts for the output budget differently — keep max_tokens >= 512 or
            # outputs can truncate to a few tokens (e.g. 256→fragments, 512→full sentence).
            # Also: do NOT pass `seed` (Gemini rejects it with HTTP 400).
            max_tokens=512,
        ),
        provider="gemini",
        skip_health_check=True,
    )

    # --- Config Builder ---
    builder = DataDesignerConfigBuilder()
    builder.add_model_config(gemini_model)

    # --- Seed Data: adapt path to your input file ---
    seed = LocalFileSeedSource(path=str(Path(__file__).parent / "sample_seed.csv"))
    builder.with_seed_dataset(seed)

    builder.add_column(
        column_type="llm-text",
        name="description",
        prompt=(
            "You are a helpful assistant. "
            "Given the item '{{ text }}' with category '{{ category }}' "
            "and label '{{ label }}', provide a concise description. "
            "Output ONLY the description — no explanation, no quotes."
        ),
        model_alias="gemini-text",
    )

    return builder
