#!/usr/bin/env python3
"""
Synthesis Prompt Builder for MAGIC Data Agent Skills
=====================================================
ADK-native prompt construction module. Builds system-level InstructionProvider
callables and row-level user prompt strings for LLM-based data synthesis.

No Jinja2 or external template engines — prompts are plain Python string
concatenation following ADK's native format.

Key features:
- InstructionProvider callables for system-level prompts (ADK-native)
- Plain string construction for row-level user prompts
- Few-shot example selection (key column match + TF-IDF semantic similarity)
- Multi-dataset reference context inclusion
- Token budget management via tiktoken with truncation
- Dynamic validation criteria and output schema description generation

Usage:
    python synthesis_prompt_builder.py --demo
    python synthesis_prompt_builder.py --count-tokens "Your prompt text here"
    python synthesis_prompt_builder.py --generate-criteria column_configs.json
    python synthesis_prompt_builder.py --generate-schema output_schema.json
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from synthesis_utils import sanitize_for_prompt, tfidf_similarity
except ImportError:
    def sanitize_for_prompt(text, max_length=None):
        """Stub: sanitize text for prompt inclusion. See magic-data-synthesis SKILL.md for full pattern."""
        result = str(text).strip().replace("\n", " ")
        if max_length:
            result = result[:max_length]
        return result
    def tfidf_similarity(a, b):
        """Stub: TF-IDF cosine similarity between two strings."""
        return 0.0

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Type Aliases
# ──────────────────────────────────────────────────────────────

# InstructionProvider: a callable that receives ReadonlyContext and returns str.
# We type it loosely as Callable[[Any], str] so the module does not require
# google-adk at import time (it is optional for standalone use).
InstructionProvider = Callable[[Any], str]


# ──────────────────────────────────────────────────────────────
# Prompt Template Constants (reference examples for common tasks)
# ──────────────────────────────────────────────────────────────

PROMPT_EXAMPLES = {
    "fill_missing": (
        "You are filling in missing values for the '{column}' column.\n"
        "Use the provided row context to infer a plausible value.\n"
        "Return only the value — no explanation, no markdown.\n\n"
        "Row context:\n{row_context}\n\n"
        "Generate the '{column}' value:"
    ),
    "translate": (
        "Translate the '{source_column}' text to {target_language}.\n"
        "Preserve meaning, tone, and formatting. Return only the translation.\n\n"
        "Source text: {source_text}\n\n"
        "Translation:"
    ),
    "annotate": (
        "Annotate the following text for '{annotation_type}'.\n"
        "Return only the annotation value — no explanation.\n\n"
        "Text: {text}\n\n"
        "Annotation:"
    ),
    "summarize": (
        "Summarize the following text in {max_words} words or fewer.\n"
        "Return only the summary — no preamble.\n\n"
        "Text: {text}\n\n"
        "Summary:"
    ),
    "html_to_markdown": (
        "Convert the following HTML to clean Markdown.\n"
        "Preserve headers, lists, links, and emphasis. Remove inline styles.\n"
        "Return only the Markdown — no explanation.\n\n"
        "HTML:\n{html}\n\n"
        "Markdown:"
    ),
    "extract_structured": (
        "Extract structured data from the following text.\n"
        "Return a JSON object with these fields: {fields}.\n"
        "Return only the JSON object — no explanation, no code fences.\n\n"
        "Text: {text}\n\n"
        "JSON:"
    ),
}


# ──────────────────────────────────────────────────────────────
# InstructionProvider Factory
# ──────────────────────────────────────────────────────────────

def create_instruction_provider(config: dict) -> InstructionProvider:
    """
    Create an ADK-native InstructionProvider callable from a synthesis config.

    The returned callable accepts a ReadonlyContext (or any object) and returns
    a system-level instruction string. ADK does NOT apply {var} substitution on
    InstructionProvider results — dynamic content must be embedded by the callable.

    Config keys (all optional):
        base_instruction (str): Core system instruction text
        column_name (str): Column being synthesized
        domain_instructions (str): Domain-specific guidance
        output_constraints (dict): Constraints like max_length, format, allowed_values
        task_type (str): One of fill_missing, translate, annotate, summarize,
                         html_to_markdown, extract_structured
        language (str): Output language (default: English)
        strict_mode (bool): If True, adds "Return ONLY the value" enforcement

    Args:
        config: Configuration dict for the instruction provider

    Returns:
        Callable[[Any], str] — ADK InstructionProvider
    """
    # Capture config at closure creation time
    _config = dict(config)

    def instruction_provider(context: Any) -> str:
        """
        ADK-native InstructionProvider: constructs the system instruction string.

        Args:
            context: ReadonlyContext from ADK (can access session state if needed)

        Returns:
            System instruction string for the LlmAgent
        """
        parts = []

        # Base instruction
        base = _config.get("base_instruction", "").strip()
        if base:
            parts.append(base)
        else:
            # Build a default instruction from task_type or column_name
            task_type = _config.get("task_type", "")
            column_name = _config.get("column_name", "the target column")
            if task_type and task_type in PROMPT_EXAMPLES:
                parts.append(
                    f"You are a data synthesis assistant generating values for "
                    f"the '{column_name}' column using the '{task_type}' strategy."
                )
            else:
                parts.append(
                    f"You are a data synthesis assistant generating values for "
                    f"the '{column_name}' column."
                )

        # Language constraint
        language = _config.get("language", "").strip()
        if language and language.lower() not in ("english", "en"):
            parts.append(f"Respond in {language}.")

        # Domain instructions
        domain = _config.get("domain_instructions", "").strip()
        if domain:
            parts.append(f"Domain guidance:\n{domain}")

        # Output constraints
        constraints = _config.get("output_constraints", {})
        if constraints:
            constraint_lines = []
            max_length = constraints.get("max_length")
            if max_length:
                constraint_lines.append(f"- Maximum length: {max_length} characters")
            min_length = constraints.get("min_length")
            if min_length:
                constraint_lines.append(f"- Minimum length: {min_length} characters")
            allowed_values = constraints.get("allowed_values")
            if allowed_values and isinstance(allowed_values, list):
                vals = ", ".join(str(v) for v in allowed_values[:20])
                constraint_lines.append(f"- Allowed values: {vals}")
            output_format = constraints.get("format")
            if output_format:
                constraint_lines.append(f"- Output format: {output_format}")
            null_tolerance = constraints.get("null_tolerance")
            if null_tolerance is not None:
                if null_tolerance:
                    constraint_lines.append("- Null/empty output is acceptable")
                else:
                    constraint_lines.append("- Never return null or empty output")
            if constraint_lines:
                parts.append("Output constraints:\n" + "\n".join(constraint_lines))

        # Strict mode enforcement
        if _config.get("strict_mode", True):
            parts.append(
                "Return ONLY the synthesized value — no explanation, no preamble, "
                "no markdown formatting, no code fences."
            )

        # Try to access session state for dynamic metadata
        try:
            if hasattr(context, "state") and context.state:
                dataset_meta = context.state.get("dataset_metadata")
                if dataset_meta and isinstance(dataset_meta, dict):
                    meta_parts = []
                    row_count = dataset_meta.get("row_count")
                    if row_count:
                        meta_parts.append(f"Dataset row count: {row_count}")
                    col_count = dataset_meta.get("column_count")
                    if col_count:
                        meta_parts.append(f"Dataset column count: {col_count}")
                    if meta_parts:
                        parts.append("Dataset context: " + ", ".join(meta_parts))
        except Exception:
            pass  # Session state access is best-effort

        return "\n\n".join(parts)

    return instruction_provider


# ──────────────────────────────────────────────────────────────
# Few-Shot Example Selection
# ──────────────────────────────────────────────────────────────

def select_few_shot_examples(
    target_row: dict,
    examples: list[dict],
    key_column: Optional[str] = None,
    n: int = 3,
    semantic_columns: Optional[list[str]] = None,
) -> list[dict]:
    """
    Select the best N few-shot examples from a list for a given target row.

    Selection strategy (in order of priority):
    1. Key column exact match: examples where key_column value equals target
    2. TF-IDF semantic similarity on semantic_columns (or all str columns)
    3. Order of appearance (fallback)

    Args:
        target_row: The row for which to find similar examples
        examples: List of example dicts (completed rows with output values)
        key_column: Column name to use for exact-match pre-filtering (e.g., "pos")
        n: Number of examples to return (default 3)
        semantic_columns: Column names to use for semantic similarity scoring.
                          If None, all string-valued columns in target_row are used.

    Returns:
        List of up to n example dicts, best matches first
    """
    if not examples:
        return []

    if n <= 0:
        return []

    # Step 1: Exact key column match — prefer these examples
    if key_column and key_column in target_row:
        target_key_val = target_row.get(key_column)
        key_matches = [
            ex for ex in examples
            if str(ex.get(key_column, "")).strip() == str(target_key_val).strip()
        ]
        non_matches = [
            ex for ex in examples
            if str(ex.get(key_column, "")).strip() != str(target_key_val).strip()
        ]
        candidate_pool = key_matches + non_matches
    else:
        candidate_pool = list(examples)

    if not candidate_pool:
        return []

    # Step 2: Semantic similarity scoring via TF-IDF
    # Build target text from semantic_columns or all string columns
    if semantic_columns:
        cols_to_use = [c for c in semantic_columns if c in target_row]
    else:
        cols_to_use = [
            k for k, v in target_row.items()
            if isinstance(v, str) and v.strip()
        ]

    if cols_to_use:
        target_text = " ".join(
            str(target_row.get(c, "")) for c in cols_to_use
        ).strip()

        scored = []
        for ex in candidate_pool:
            ex_text = " ".join(
                str(ex.get(c, "")) for c in cols_to_use
            ).strip()
            if target_text and ex_text:
                score = tfidf_similarity(target_text, ex_text)
            else:
                score = 0.0
            # Bonus for key column exact match
            if key_column and key_column in target_row:
                target_key_val = target_row.get(key_column)
                if str(ex.get(key_column, "")).strip() == str(target_key_val).strip():
                    score += 1.0  # Priority boost
            scored.append((score, ex))

        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [ex for _, ex in scored[:n]]
    else:
        # No text columns — just use first n from candidate pool
        selected = candidate_pool[:n]

    return selected


# ──────────────────────────────────────────────────────────────
# Reference Context Builder
# ──────────────────────────────────────────────────────────────

def build_reference_context(
    row: dict,
    reference_datasets: list[dict],
    join_configs: list[dict],
) -> str:
    """
    Build a reference context string from multiple reference datasets.

    For each reference dataset, looks up matching rows by the configured join key
    and formats them as labeled context sections.

    reference_datasets: List of dicts, each with:
        name (str): Dataset label for the prompt
        rows (list[dict]): Rows from the reference dataset

    join_configs: List of dicts (one per reference_datasets entry), each with:
        source_key (str): Column in the target row to match on
        reference_key (str): Column in the reference dataset to match against
        max_rows (int): Maximum number of matched rows to include (default 3)
        columns (list[str]): Which reference columns to include (default: all)

    Args:
        row: The current target row
        reference_datasets: List of reference dataset descriptors
        join_configs: Join configuration for each reference dataset

    Returns:
        Formatted reference context string, or empty string if no matches
    """
    if not reference_datasets or not join_configs:
        return ""

    context_parts = []

    for i, (dataset, join_cfg) in enumerate(zip(reference_datasets, join_configs)):
        dataset_name = dataset.get("name", f"Reference {i + 1}")
        ref_rows = dataset.get("rows", [])
        source_key = join_cfg.get("source_key", "")
        reference_key = join_cfg.get("reference_key", source_key)
        max_rows = join_cfg.get("max_rows", 3)
        columns_to_include = join_cfg.get("columns")

        if not ref_rows:
            context_parts.append(
                f"[{dataset_name}]: No data available."
            )
            continue

        # Look up matching rows
        target_val = str(row.get(source_key, "")).strip() if source_key else ""
        if target_val and reference_key:
            matched = [
                r for r in ref_rows
                if str(r.get(reference_key, "")).strip() == target_val
            ]
        else:
            matched = []

        if not matched:
            context_parts.append(
                f"[{dataset_name}]: No match found for {source_key}={target_val!r}."
            )
            continue

        # Format matched rows
        matched = matched[:max_rows]
        row_lines = []
        for j, ref_row in enumerate(matched, 1):
            if columns_to_include:
                display_cols = {
                    k: v for k, v in ref_row.items()
                    if k in columns_to_include
                }
            else:
                display_cols = ref_row

            cols_str = " | ".join(
                f"{k}: {sanitize_for_prompt(str(v), max_length=500)}"
                for k, v in display_cols.items()
            )
            row_lines.append(f"  [{j}] {cols_str}")

        context_parts.append(
            f"[{dataset_name}] ({len(matched)} match{'es' if len(matched) != 1 else ''}):\n"
            + "\n".join(row_lines)
        )

    if not context_parts:
        return ""

    return "Reference context:\n" + "\n\n".join(context_parts)


# ──────────────────────────────────────────────────────────────
# Token Counting and Truncation
# ──────────────────────────────────────────────────────────────

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count the number of tokens in a text string using tiktoken.

    Falls back to a rough character-based estimate (4 chars per token) if
    tiktoken is not installed or the model encoding is unavailable.

    Args:
        text: Text to count tokens for
        model: Model identifier for tiktoken encoding selection

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    try:
        import tiktoken

        # Normalize model name: strip provider prefix (e.g., "openai/gpt-4o-mini" -> "gpt-4o-mini")
        normalized_model = model.split("/")[-1] if "/" in model else model

        try:
            enc = tiktoken.encoding_for_model(normalized_model)
        except KeyError:
            # Fall back to cl100k_base (GPT-4 family encoding)
            enc = tiktoken.get_encoding("cl100k_base")

        return len(enc.encode(text))
    except ImportError:
        logger.debug("tiktoken not installed; using character-based token estimate")
        # Rough estimate: ~4 characters per token for English text
        return max(1, len(text) // 4)
    except Exception as e:
        logger.debug("Token counting failed (%s); using character estimate", e)
        return max(1, len(text) // 4)


def truncate_to_budget(
    text: str,
    max_tokens: int,
    model: str = "gpt-4o-mini",
    truncation_marker: str = "\n[... truncated to fit token budget ...]",
) -> str:
    """
    Truncate text to fit within a token budget.

    Uses binary search on character length to find the longest prefix that
    fits within max_tokens. Appends a truncation marker when truncated.

    Args:
        text: Text to potentially truncate
        max_tokens: Maximum allowed token count
        model: Model identifier for tiktoken encoding
        truncation_marker: String to append when truncating

    Returns:
        Possibly truncated text that fits within max_tokens
    """
    if not text:
        return text

    if max_tokens <= 0:
        return ""

    current_tokens = count_tokens(text, model)
    if current_tokens <= max_tokens:
        return text

    marker_tokens = count_tokens(truncation_marker, model)
    target_tokens = max_tokens - marker_tokens
    if target_tokens <= 0:
        return truncation_marker[:max_tokens * 4]  # Rough char fallback

    # Binary search for the right character cutoff
    low, high = 0, len(text)
    while low < high - 1:
        mid = (low + high) // 2
        if count_tokens(text[:mid], model) <= target_tokens:
            low = mid
        else:
            high = mid

    truncated = text[:low].rstrip()
    if truncated:
        return truncated + truncation_marker
    return truncation_marker


# ──────────────────────────────────────────────────────────────
# Row Prompt Builder
# ──────────────────────────────────────────────────────────────

def _format_row_data(row: dict, column_config: dict) -> str:
    """Format a row's context columns as a readable string for the prompt."""
    context_columns = column_config.get("context_columns") or column_config.get("depends_on", [])
    column_name = column_config.get("name", "")

    lines = []
    if context_columns:
        cols_to_show = [c for c in context_columns if c in row and c != column_name]
    else:
        cols_to_show = [k for k in row.keys() if k != column_name]

    for col in cols_to_show:
        val = row.get(col)
        if val is not None:
            safe_val = sanitize_for_prompt(str(val), max_length=1000)
            lines.append(f"  {col}: {safe_val}")

    return "\n".join(lines) if lines else "  (no context columns)"


def _format_few_shot_block(
    examples: list[dict],
    column_config: dict,
) -> str:
    """Format few-shot examples as a prompt block."""
    if not examples:
        return ""

    column_name = column_config.get("name", "output")
    context_columns = column_config.get("context_columns") or column_config.get("depends_on", [])

    lines = [f"Examples ({len(examples)} provided):"]
    for i, ex in enumerate(examples, 1):
        lines.append(f"\n  Example {i}:")
        # Show context columns
        if context_columns:
            for col in context_columns:
                if col in ex and col != column_name:
                    safe_val = sanitize_for_prompt(str(ex.get(col, "")), max_length=500)
                    lines.append(f"    {col}: {safe_val}")
        else:
            for k, v in ex.items():
                if k != column_name:
                    safe_val = sanitize_for_prompt(str(v), max_length=500)
                    lines.append(f"    {k}: {safe_val}")
        # Show the target output value
        target_val = ex.get(column_name)
        if target_val is not None:
            safe_target = sanitize_for_prompt(str(target_val), max_length=500)
            lines.append(f"    -> {column_name}: {safe_target}")

    return "\n".join(lines)


def build_row_prompt(
    row: dict,
    column_config: dict,
    few_shot_examples: Optional[list[dict]] = None,
    reference_data: Optional[str] = None,
    domain_instructions: Optional[str] = None,
    token_budget: Optional[int] = None,
    model: str = "gpt-4o-mini",
) -> str:
    """
    Build a plain string user prompt for row-level synthesis.

    This prompt is passed as new_message to runner.run_async(). No Jinja2 or
    template engines — plain Python string concatenation following ADK's native
    prompt format.

    The prompt structure:
    1. Task description
    2. Domain instructions (if any)
    3. Output schema/constraints
    4. Few-shot examples (if any)
    5. Reference context (if any)
    6. Current row data
    7. Generation request

    If token_budget is specified, sections are truncated from the bottom up
    (reference data truncated first, then examples, then row data) to fit.

    Args:
        row: The current row dict (all available column values)
        column_config: Column config dict with keys:
            name (str): Column to generate
            description (str, optional): Column description
            context_columns or depends_on (list[str], optional): Columns to include as context
            output_schema (dict, optional): Schema constraints for output
            task_type (str, optional): Task type hint
            custom_prompt (str, optional): Custom prompt template string
        few_shot_examples: Pre-selected few-shot examples (use select_few_shot_examples)
        reference_data: Pre-formatted reference context string (use build_reference_context)
        domain_instructions: Domain-specific instructions string
        token_budget: Maximum tokens for the prompt (None = no limit)
        model: Model identifier for token counting

    Returns:
        Plain string prompt ready for LLM consumption
    """
    column_name = column_config.get("name", "output")
    description = column_config.get("description", "")
    task_type = column_config.get("task_type", "")
    custom_prompt = column_config.get("custom_prompt", "")
    output_schema = column_config.get("output_schema", {})

    # Handle custom prompt — render with row context and return
    if custom_prompt and custom_prompt.strip():
        rendered = _render_custom_prompt(
            custom_prompt=custom_prompt,
            row=row,
            column_config=column_config,
            few_shot_examples=few_shot_examples or [],
            reference_data=reference_data or "",
            domain_instructions=domain_instructions or "",
        )
        if token_budget:
            rendered = truncate_to_budget(rendered, token_budget, model)
        return rendered

    # Build prompt sections
    sections = []

    # 1. Task description
    if description:
        task_line = (
            f"Generate the '{column_name}' column value for the row below.\n"
            f"Column description: {description}"
        )
    elif task_type and task_type in PROMPT_EXAMPLES:
        task_line = (
            f"Generate the '{column_name}' column value for the row below.\n"
            f"Task type: {task_type}"
        )
    else:
        task_line = f"Generate the '{column_name}' column value for the row below."
    sections.append(task_line)

    # 2. Domain instructions
    if domain_instructions and domain_instructions.strip():
        sections.append(f"Instructions:\n{domain_instructions.strip()}")

    # 3. Output constraints from schema
    if output_schema and isinstance(output_schema, dict):
        schema_desc = _format_output_schema_inline(output_schema)
        if schema_desc:
            sections.append(f"Output constraints:\n{schema_desc}")

    # 4. Few-shot examples
    if few_shot_examples:
        examples_block = _format_few_shot_block(few_shot_examples, column_config)
        if examples_block:
            sections.append(examples_block)

    # 5. Reference context
    if reference_data and reference_data.strip():
        sections.append(reference_data.strip())

    # 6. Current row data
    row_data_str = _format_row_data(row, column_config)
    sections.append(f"Current row:\n{row_data_str}")

    # 7. Generation request
    sections.append(
        f"Generate the '{column_name}' value (return ONLY the value, nothing else):"
    )

    prompt = "\n\n".join(sections)

    # Apply token budget if specified
    if token_budget and token_budget > 0:
        current_tokens = count_tokens(prompt, model)
        if current_tokens > token_budget:
            prompt = _apply_token_budget(
                row=row,
                column_config=column_config,
                few_shot_examples=few_shot_examples or [],
                reference_data=reference_data or "",
                domain_instructions=domain_instructions or "",
                output_schema=output_schema,
                task_line=task_line,
                token_budget=token_budget,
                model=model,
            )
            logger.debug(
                "Prompt truncated from %d to %d tokens for column '%s'",
                current_tokens,
                count_tokens(prompt, model),
                column_name,
            )

    return prompt


def _format_output_schema_inline(output_schema: dict) -> str:
    """Format output schema constraints as inline text for the prompt."""
    lines = []
    if "type" in output_schema:
        lines.append(f"- Type: {output_schema['type']}")
    if "max_length" in output_schema:
        lines.append(f"- Maximum length: {output_schema['max_length']} characters")
    if "min_length" in output_schema:
        lines.append(f"- Minimum length: {output_schema['min_length']} characters")
    if "max_words" in output_schema:
        lines.append(f"- Maximum words: {output_schema['max_words']}")
    if "format" in output_schema:
        lines.append(f"- Format: {output_schema['format']}")
    if "allowed_values" in output_schema:
        vals = output_schema["allowed_values"]
        if isinstance(vals, list):
            lines.append(f"- Allowed values: {', '.join(str(v) for v in vals[:20])}")
    if "pattern" in output_schema:
        lines.append(f"- Pattern: {output_schema['pattern']}")
    if "nullable" in output_schema:
        if output_schema["nullable"]:
            lines.append("- May be empty/null")
        else:
            lines.append("- Must not be empty or null")
    return "\n".join(lines)


def _render_custom_prompt(
    custom_prompt: str,
    row: dict,
    column_config: dict,
    few_shot_examples: list[dict],
    reference_data: str,
    domain_instructions: str,
) -> str:
    """
    Render a custom prompt string with available context variables.

    Available substitutions (simple str.format-style, keys must exist):
        {column_name}       — name of the column being generated
        {row_context}       — formatted row context string
        {examples_block}    — formatted few-shot examples block
        {reference_context} — reference data string
        {domain_instructions} — domain instructions
    """
    column_name = column_config.get("name", "output")
    row_context = _format_row_data(row, column_config)
    examples_block = _format_few_shot_block(few_shot_examples, column_config)

    try:
        rendered = custom_prompt.format(
            column_name=column_name,
            row_context=row_context,
            examples_block=examples_block,
            reference_context=reference_data,
            domain_instructions=domain_instructions,
        )
    except KeyError:
        # If format keys are missing, return the prompt with available substitutions
        try:
            rendered = custom_prompt.format_map(
                _SafeFormatMap({
                    "column_name": column_name,
                    "row_context": row_context,
                    "examples_block": examples_block,
                    "reference_context": reference_data,
                    "domain_instructions": domain_instructions,
                })
            )
        except Exception:
            rendered = custom_prompt

    return rendered


class _SafeFormatMap(dict):
    """A dict subclass that returns the key placeholder for missing keys."""
    def __missing__(self, key: str) -> str:
        return f"{{{key}}}"


def _apply_token_budget(
    row: dict,
    column_config: dict,
    few_shot_examples: list[dict],
    reference_data: str,
    domain_instructions: str,
    output_schema: dict,
    task_line: str,
    token_budget: int,
    model: str,
) -> str:
    """
    Rebuild the prompt with token budget enforcement.

    Truncation priority (first to truncate):
    1. Reference data (least critical)
    2. Few-shot examples (reduce count from the least-similar end)
    3. Domain instructions (truncate if very long)
    4. Row data (truncate individual values as last resort)
    """
    column_name = column_config.get("name", "output")

    # Fixed sections that are always included
    generation_request = (
        f"Generate the '{column_name}' value (return ONLY the value, nothing else):"
    )
    row_data_str = _format_row_data(row, column_config)

    # Build schema constraint section
    schema_section = ""
    if output_schema:
        schema_desc = _format_output_schema_inline(output_schema)
        if schema_desc:
            schema_section = f"Output constraints:\n{schema_desc}"

    # Calculate fixed budget
    fixed_parts = [task_line, generation_request, row_data_str]
    if domain_instructions:
        fixed_parts.append(f"Instructions:\n{domain_instructions.strip()}")
    if schema_section:
        fixed_parts.append(schema_section)

    fixed_text = "\n\n".join(p for p in fixed_parts if p)
    fixed_tokens = count_tokens(fixed_text, model)
    remaining_budget = token_budget - fixed_tokens

    # Allocate remaining budget between examples and reference data
    # Strategy: examples get 60%, reference gets 40%
    examples_budget = int(remaining_budget * 0.6)
    reference_budget = remaining_budget - examples_budget

    # Truncate reference data
    truncated_ref = ""
    if reference_data and reference_data.strip() and reference_budget > 50:
        truncated_ref = truncate_to_budget(reference_data.strip(), reference_budget, model)

    # Truncate few-shot examples by reducing count
    truncated_examples = []
    if few_shot_examples and examples_budget > 50:
        for n_ex in range(len(few_shot_examples), 0, -1):
            subset = few_shot_examples[:n_ex]
            ex_block = _format_few_shot_block(subset, column_config)
            if count_tokens(ex_block, model) <= examples_budget:
                truncated_examples = subset
                if n_ex < len(few_shot_examples):
                    logger.info(
                        "Reduced few-shot examples from %d to %d to fit token budget for '%s'",
                        len(few_shot_examples),
                        n_ex,
                        column_name,
                    )
                break

    # Rebuild prompt with truncated sections
    sections = [task_line]
    if domain_instructions and domain_instructions.strip():
        sections.append(f"Instructions:\n{domain_instructions.strip()}")
    if schema_section:
        sections.append(schema_section)
    if truncated_examples:
        ex_block = _format_few_shot_block(truncated_examples, column_config)
        if ex_block:
            sections.append(ex_block)
    if truncated_ref:
        sections.append(truncated_ref)
    sections.append(f"Current row:\n{row_data_str}")
    sections.append(generation_request)

    return "\n\n".join(sections)


# ──────────────────────────────────────────────────────────────
# Dynamic Criteria and Schema Generation
# ──────────────────────────────────────────────────────────────

def generate_criteria(column_configs: list[dict]) -> dict:
    """
    Generate validation criteria JSON from column configs.

    The resulting criteria dict maps column names to their validation rules,
    suitable for use with validate_synthetic.py's criteria-based checks.

    Each column config may contain:
        name (str): Column name
        strategy (str): Generation strategy
        output_schema (dict): Schema constraints
        validation (dict): Explicit validation rules
        sentinel_patterns (list): Patterns to treat as missing/invalid

    Args:
        column_configs: List of column config dicts from synthesis config

    Returns:
        Dict mapping column names to validation criteria dicts, plus a
        top-level "_meta" key with overall criteria metadata.
    """
    criteria: dict[str, Any] = {"_meta": {"generated_from": "column_configs"}}

    for col in column_configs:
        name = col.get("name")
        if not name:
            continue

        col_criteria: dict[str, Any] = {}

        # Strategy-derived constraints
        strategy = col.get("strategy", "")
        if strategy in ("llm_text", "llm_structured"):
            col_criteria["allow_empty"] = False
            col_criteria["require_non_sentinel"] = True

        # From output_schema
        output_schema = col.get("output_schema", {})
        if output_schema and isinstance(output_schema, dict):
            if "type" in output_schema:
                col_criteria["type"] = output_schema["type"]
            if "max_length" in output_schema:
                col_criteria["max_length"] = output_schema["max_length"]
            if "min_length" in output_schema:
                col_criteria["min_length"] = output_schema["min_length"]
            if "allowed_values" in output_schema:
                col_criteria["allowed_values"] = output_schema["allowed_values"]
            if "pattern" in output_schema:
                col_criteria["pattern"] = output_schema["pattern"]
            if "nullable" in output_schema:
                col_criteria["allow_empty"] = bool(output_schema["nullable"])
            if "min_val" in output_schema:
                col_criteria["min_val"] = output_schema["min_val"]
            if "max_val" in output_schema:
                col_criteria["max_val"] = output_schema["max_val"]

        # Explicit validation rules override schema-derived ones
        validation = col.get("validation", {})
        if validation and isinstance(validation, dict):
            col_criteria.update(validation)

        # Sentinel patterns
        sentinel_patterns = col.get("sentinel_patterns")
        if sentinel_patterns and isinstance(sentinel_patterns, list):
            col_criteria["sentinel_patterns"] = sentinel_patterns
        elif strategy in ("llm_text", "llm_structured"):
            # Default sentinel patterns for LLM-generated columns
            col_criteria.setdefault(
                "sentinel_patterns",
                ["N/A", "n/a", "TBD", "TODO", "PLACEHOLDER", ""]
            )

        # Description for documentation
        description = col.get("description", "")
        if description:
            col_criteria["description"] = description

        criteria[name] = col_criteria

    return criteria


def generate_output_schema_description(output_schema: dict) -> str:
    """
    Generate a human-readable description of an output schema dict.

    This description is suitable for inclusion in prompts, documentation,
    or as the basis for a judge rubric.

    The output schema may contain:
        type (str): Data type (text, numeric, categorical, boolean, etc.)
        max_length (int): Maximum character length
        min_length (int): Minimum character length
        max_words (int): Maximum word count
        min_words (int): Minimum word count
        format (str): Format description (e.g., "ISO date", "JSON", "Markdown")
        allowed_values (list): Enumerated allowed values
        pattern (str): Regex pattern the value must match
        nullable (bool): Whether null/empty is acceptable
        min_val (float): Minimum numeric value
        max_val (float): Maximum numeric value
        description (str): Human description of the column
        examples (list): Example valid values

    Args:
        output_schema: Output schema dict

    Returns:
        Human-readable description string
    """
    if not output_schema or not isinstance(output_schema, dict):
        return "No schema constraints specified."

    lines = []

    # Description first
    if "description" in output_schema:
        lines.append(f"Description: {output_schema['description']}")

    # Type
    if "type" in output_schema:
        lines.append(f"Type: {output_schema['type']}")

    # Length constraints
    length_parts = []
    if "min_length" in output_schema:
        length_parts.append(f"minimum {output_schema['min_length']}")
    if "max_length" in output_schema:
        length_parts.append(f"maximum {output_schema['max_length']}")
    if length_parts:
        lines.append(f"Character length: {', '.join(length_parts)}")

    # Word count constraints
    word_parts = []
    if "min_words" in output_schema:
        word_parts.append(f"minimum {output_schema['min_words']}")
    if "max_words" in output_schema:
        word_parts.append(f"maximum {output_schema['max_words']}")
    if word_parts:
        lines.append(f"Word count: {', '.join(word_parts)}")

    # Numeric range
    range_parts = []
    if "min_val" in output_schema:
        range_parts.append(f">= {output_schema['min_val']}")
    if "max_val" in output_schema:
        range_parts.append(f"<= {output_schema['max_val']}")
    if range_parts:
        lines.append(f"Value range: {' and '.join(range_parts)}")

    # Format
    if "format" in output_schema:
        lines.append(f"Format: {output_schema['format']}")

    # Pattern
    if "pattern" in output_schema:
        lines.append(f"Pattern: {output_schema['pattern']}")

    # Allowed values
    if "allowed_values" in output_schema:
        vals = output_schema["allowed_values"]
        if isinstance(vals, list):
            vals_preview = vals[:10]
            suffix = f" (and {len(vals) - 10} more)" if len(vals) > 10 else ""
            lines.append(f"Allowed values: {', '.join(str(v) for v in vals_preview)}{suffix}")

    # Nullable
    if "nullable" in output_schema:
        lines.append(
            "Nullable: yes (empty/null values are acceptable)"
            if output_schema["nullable"]
            else "Nullable: no (must have a non-empty value)"
        )

    # Examples
    if "examples" in output_schema:
        examples = output_schema["examples"]
        if isinstance(examples, list) and examples:
            ex_strs = [f'"{ex}"' for ex in examples[:5]]
            lines.append(f"Examples: {', '.join(ex_strs)}")

    if not lines:
        return "Schema is present but contains no recognizable constraints."

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# LLM-as-Judge Rubric Generation
# ──────────────────────────────────────────────────────────────

def generate_judge_rubric(
    column_name: str,
    user_guidance: str,
    output_schema: Optional[dict] = None,
    scoring_dimensions: Optional[list[str]] = None,
) -> dict:
    """
    Generate a structured LLM-as-judge rubric from user guidance.

    The rubric is suitable for use with validate_synthetic.py's LLM-as-judge mode.

    Args:
        column_name: Name of the column being evaluated
        user_guidance: User's quality description
                       (e.g., "definitions should be accurate, formal, include usage examples")
        output_schema: Optional schema constraints to incorporate into rubric
        scoring_dimensions: Optional list of dimension names to use instead of auto-derived

    Returns:
        Dict with rubric structure: dimensions, scale, threshold, prompt_template
    """
    # Parse dimensions from user guidance if not provided
    if not scoring_dimensions:
        scoring_dimensions = _extract_dimensions_from_guidance(user_guidance)

    # Build dimension specs
    dimensions = []
    for dim in scoring_dimensions:
        dimensions.append({
            "name": dim,
            "description": f"Evaluate {dim.lower()} of the generated {column_name}",
            "scale": "1-5",
            "weight": 1.0 / len(scoring_dimensions) if scoring_dimensions else 1.0,
        })

    # Build schema constraints section for the rubric
    schema_constraints = ""
    if output_schema:
        schema_constraints = generate_output_schema_description(output_schema)

    # Build judge prompt template
    dim_list = "\n".join(
        f"  {i + 1}. {d['name']} (1-5): {d['description']}"
        for i, d in enumerate(dimensions)
    )

    prompt_template = (
        f"You are evaluating the quality of a generated value for the '{column_name}' column.\n"
        f"User guidance: {user_guidance}\n"
    )
    if schema_constraints:
        prompt_template += f"\nSchema constraints:\n{schema_constraints}\n"

    prompt_template += (
        f"\nEvaluate the following value on these dimensions:\n{dim_list}\n\n"
        f"Generated value: {{generated_value}}\n"
        f"Source row context: {{row_context}}\n\n"
        f"Return a JSON object with a 'scores' dict (dimension name -> score 1-5), "
        f"an 'overall' score (1-5), and a 'reasoning' string.\n"
        f"Example: {{\"scores\": {{\"accuracy\": 4, \"clarity\": 5}}, "
        f"\"overall\": 4.5, \"reasoning\": \"...\"}}"
    )

    return {
        "column": column_name,
        "user_guidance": user_guidance,
        "dimensions": dimensions,
        "scale": "1-5",
        "threshold": 3.0,  # Minimum acceptable overall score
        "aggregation": "weighted_mean",
        "prompt_template": prompt_template,
    }


def _extract_dimensions_from_guidance(guidance: str) -> list[str]:
    """Extract quality dimension names from user guidance text."""
    # Common quality dimension keywords to look for
    known_dimensions = [
        "accuracy", "accuracy", "relevance", "clarity", "coherence",
        "formality", "completeness", "conciseness", "fluency",
        "correctness", "factuality", "consistency", "naturalness",
        "grammar", "style", "tone", "readability",
    ]

    guidance_lower = guidance.lower()
    found = []
    seen = set()
    for dim in known_dimensions:
        if dim in guidance_lower and dim not in seen:
            found.append(dim.capitalize())
            seen.add(dim)

    # Default dimensions if nothing specific found
    if not found:
        found = ["Accuracy", "Relevance", "Quality"]

    return found[:5]  # Cap at 5 dimensions


# ──────────────────────────────────────────────────────────────
# Schema Inference from Sample Values
# ──────────────────────────────────────────────────────────────

def infer_output_schema(
    column_name: str,
    sample_values: list[Any],
) -> dict:
    """
    Infer an output schema dict from a sample of column values.

    Analyzes value types, lengths, patterns, and distributions to produce
    a JSON schema dict with inferred constraints.

    Args:
        column_name: Name of the column
        sample_values: List of sample values (up to ~100 recommended)

    Returns:
        Schema dict with: type, min_length, max_length, nullable,
                          allowed_values (if categorical), min_val, max_val (if numeric)
    """
    if not sample_values:
        return {"type": "text", "description": f"Schema for '{column_name}' (no samples)"}

    # Filter out None/null
    non_null = [v for v in sample_values if v is not None and str(v).strip() != ""]
    null_count = len(sample_values) - len(non_null)
    nullable = null_count > 0

    if not non_null:
        return {
            "type": "text",
            "nullable": True,
            "description": f"Schema for '{column_name}' (all samples are null)",
        }

    schema: dict[str, Any] = {"description": f"Inferred schema for '{column_name}'"}

    # Check if numeric
    numeric_vals = []
    for v in non_null:
        try:
            numeric_vals.append(float(str(v)))
        except (ValueError, TypeError):
            pass

    if len(numeric_vals) >= len(non_null) * 0.8:
        schema["type"] = "numeric"
        schema["min_val"] = round(min(numeric_vals), 6)
        schema["max_val"] = round(max(numeric_vals), 6)
        schema["nullable"] = nullable
        return schema

    # String analysis
    str_vals = [str(v) for v in non_null]
    lengths = [len(s) for s in str_vals]
    schema["min_length"] = min(lengths)
    schema["max_length"] = max(lengths)
    schema["nullable"] = nullable

    # Check for categorical (low cardinality)
    unique_vals = list(set(str_vals))
    n_unique = len(unique_vals)
    n_total = len(str_vals)

    if n_unique <= 20 or (n_unique < 50 and n_unique < n_total * 0.05):
        schema["type"] = "categorical"
        schema["allowed_values"] = sorted(unique_vals)
    elif max(lengths) > 100:
        schema["type"] = "text"
    else:
        schema["type"] = "short_text"

    return schema


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def _demo_mode():
    """Run a demonstration of all key builder functions."""
    print("=== synthesis_prompt_builder.py Demo ===\n")

    # Demo 1: InstructionProvider
    print("--- 1. InstructionProvider ---")
    config = {
        "column_name": "definition",
        "domain_instructions": "Definitions should be formal, encyclopedic, and under 100 words.",
        "output_constraints": {"max_length": 500, "nullable": False},
        "strict_mode": True,
    }
    provider = create_instruction_provider(config)
    instruction = provider(None)
    print(instruction)
    print()

    # Demo 2: Few-shot selection
    print("--- 2. Few-shot Example Selection ---")
    examples = [
        {"word": "cat", "pos": "noun", "definition": "A small domesticated carnivorous mammal."},
        {"word": "run", "pos": "verb", "definition": "To move swiftly on foot."},
        {"word": "dog", "pos": "noun", "definition": "A domesticated carnivorous mammal."},
        {"word": "quick", "pos": "adjective", "definition": "Moving fast or doing something in a short time."},
        {"word": "jump", "pos": "verb", "definition": "To push oneself off the ground into the air."},
    ]
    target = {"word": "walk", "pos": "verb"}
    selected = select_few_shot_examples(target, examples, key_column="pos", n=2)
    print(f"Selected {len(selected)} examples for target {target}:")
    for ex in selected:
        print(f"  {ex}")
    print()

    # Demo 3: Row prompt
    print("--- 3. Row Prompt ---")
    col_config = {
        "name": "definition",
        "description": "Dictionary definition of the word",
        "context_columns": ["word", "pos"],
        "output_schema": {"max_length": 300, "nullable": False},
    }
    row = {"word": "stride", "pos": "verb", "pronunciation": "/straɪd/"}
    prompt = build_row_prompt(
        row=row,
        column_config=col_config,
        few_shot_examples=selected,
        domain_instructions="Use formal encyclopedic style. Maximum 50 words.",
    )
    print(prompt)
    print()

    # Demo 4: Token counting
    print("--- 4. Token Counting ---")
    token_count = count_tokens(prompt)
    print(f"Prompt token count: {token_count}")
    print()

    # Demo 5: Criteria generation
    print("--- 5. Criteria Generation ---")
    col_configs = [
        {
            "name": "definition",
            "strategy": "llm_text",
            "output_schema": {"max_length": 300, "nullable": False},
        },
        {
            "name": "pos",
            "strategy": "llm_structured",
            "output_schema": {
                "allowed_values": ["noun", "verb", "adjective", "adverb"],
                "nullable": False,
            },
        },
    ]
    criteria = generate_criteria(col_configs)
    print(json.dumps(criteria, indent=2))
    print()

    # Demo 6: Schema description
    print("--- 6. Output Schema Description ---")
    schema = {
        "type": "text",
        "min_length": 10,
        "max_length": 200,
        "nullable": False,
        "examples": ["A small domesticated mammal.", "The act of moving swiftly."],
    }
    desc = generate_output_schema_description(schema)
    print(desc)
    print()

    print("=== Demo complete ===")


def main():
    parser = argparse.ArgumentParser(
        description="ADK-native synthesis prompt builder utilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python synthesis_prompt_builder.py --demo
  python synthesis_prompt_builder.py --count-tokens "Hello world"
  python synthesis_prompt_builder.py --generate-criteria column_configs.json
  python synthesis_prompt_builder.py --generate-schema output_schema.json
  python synthesis_prompt_builder.py --infer-schema values.json --column-name mycolumn
        """,
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration of all builder functions",
    )
    parser.add_argument(
        "--count-tokens",
        metavar="TEXT",
        help="Count tokens in TEXT (uses tiktoken)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model name for token counting (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--generate-criteria",
        metavar="CONFIG_JSON",
        help="Generate validation criteria from column configs JSON file",
    )
    parser.add_argument(
        "--generate-schema",
        metavar="SCHEMA_JSON",
        help="Generate human-readable description from output schema JSON file",
    )
    parser.add_argument(
        "--infer-schema",
        metavar="VALUES_JSON",
        help="Infer output schema from sample values JSON file (list of values)",
    )
    parser.add_argument(
        "--column-name",
        default="column",
        help="Column name for --infer-schema (default: column)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Write JSON output to file (default: stdout)",
    )

    args = parser.parse_args()

    if args.demo:
        _demo_mode()
        return

    result = None

    if args.count_tokens:
        count = count_tokens(args.count_tokens, model=args.model)
        result = {
            "success": True,
            "token_count": count,
            "model": args.model,
            "text_length": len(args.count_tokens),
        }

    elif args.generate_criteria:
        path = Path(args.generate_criteria)
        if not path.exists():
            print(json.dumps({"success": False, "error": f"File not found: {args.generate_criteria}"}))
            sys.exit(1)
        with open(path) as f:
            col_configs = json.load(f)
        if not isinstance(col_configs, list):
            col_configs = col_configs.get("columns", [col_configs])
        criteria = generate_criteria(col_configs)
        result = {"success": True, "criteria": criteria}

    elif args.generate_schema:
        path = Path(args.generate_schema)
        if not path.exists():
            print(json.dumps({"success": False, "error": f"File not found: {args.generate_schema}"}))
            sys.exit(1)
        with open(path) as f:
            schema = json.load(f)
        description = generate_output_schema_description(schema)
        result = {"success": True, "description": description, "schema": schema}

    elif args.infer_schema:
        path = Path(args.infer_schema)
        if not path.exists():
            print(json.dumps({"success": False, "error": f"File not found: {args.infer_schema}"}))
            sys.exit(1)
        with open(path) as f:
            values = json.load(f)
        if not isinstance(values, list):
            print(json.dumps({"success": False, "error": "Values JSON must be a list"}))
            sys.exit(1)
        schema = infer_output_schema(args.column_name, values)
        result = {"success": True, "schema": schema, "sample_count": len(values)}

    else:
        parser.print_help()
        return

    if result is not None:
        output_str = json.dumps(result, indent=2, default=str)
        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w") as f:
                f.write(output_str)
            print(json.dumps({"success": True, "output_path": str(output_path)}, indent=2))
        else:
            print(output_str)

    sys.exit(0 if (result is None or result.get("success", True)) else 1)


if __name__ == "__main__":
    main()
