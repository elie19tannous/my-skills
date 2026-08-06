#!/usr/bin/env python3
"""
Single-Column Generation / Transformation CLI
===============================================
Batch-mode LLM-driven column generation using ADK LlmAgent.

Supports: fill missing, replace sentinels, translate, convert format
(HTML to markdown), extract structured data, annotate, and more.

Per-row quality metadata columns are appended to output:
  _synthesis_confidence, _synthesis_model, _synthesis_mode, _synthesis_timestamp

Usage:
    python generate_column.py INPUT_PATH OUTPUT_PATH --column COLUMN_NAME \\
      --agent-yaml YAML_PATH [--target-rows null_only|sentinel|all] \\
      [--sentinel-patterns '["X","N/A"]'] \\
      [--prompt-template "Generate a definition for: {word}"] \\
      [--few-shot-path examples.json] [--reference-paths ref1.csv,ref2.csv] \\
      [--model MODEL] [--sample-size N] [--dry-run] [--max-cost FLOAT] \\
      [--batch-size N] [--workspace DIR]
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

def load_dataframe(path, format="auto", **kwargs):
    """Stub: load a DataFrame from path. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    ext = str(path).rsplit(".", 1)[-1].lower()
    fmt = format if format != "auto" else ext
    if fmt == "parquet":
        return pd.read_parquet(path)
    if fmt in ("jsonl", "ndjson"):
        return pd.read_json(path, lines=True)
    if fmt == "json":
        return pd.read_json(path)
    if fmt == "tsv":
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)
def format_success(output_path=None, rows_in=0, rows_out=0, summary=None, warnings=None):
    """Stub: format a success result dict. See magic-data-lifecycle SKILL.md for full pattern."""
    return {"success": True, "output_path": output_path, "rows_in": rows_in, "rows_out": rows_out, "summary": summary or {}, "warnings": warnings or []}
def format_error(message, suggestion=None, rows_in=None):
    """Stub: format an error result dict."""
    import sys
    result = {"success": False, "error": message}
    if suggestion:
        result["suggestion"] = suggestion
    if rows_in is not None:
        result["rows_in"] = rows_in
    print(result, file=sys.stderr)
    sys.exit(1)
def output_result(result):
    """Stub: print result JSON and exit."""
    import json, sys
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result.get("success") else 1)
def save_checkpoint(df, workspace, step=1, operation="checkpoint"):
    """Stub: save a checkpoint CSV. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    import os
    p = Path(workspace) / f"ckpt_step{step}_{operation}.csv"
    os.makedirs(workspace, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)

class _io_utils:
    @staticmethod
    def load_dataframe(path, format="auto", **kwargs):
        import pandas as pd
        ext = str(path).rsplit(".", 1)[-1].lower()
        fmt = format if format != "auto" else ext
        if fmt == "parquet":
            return pd.read_parquet(path)
        if fmt in ("jsonl", "ndjson"):
            return pd.read_json(path, lines=True)
        if fmt == "json":
            return pd.read_json(path)
        if fmt == "tsv":
            return pd.read_csv(path, sep="\t")
        return pd.read_csv(path)
    @staticmethod
    def save_dataframe(df, path, format="auto", input_format=None):
        ext = str(path).rsplit(".", 1)[-1].lower()
        fmt = format if format != "auto" else ext
        if fmt == "parquet":
            df.to_parquet(path, index=False)
        elif fmt in ("jsonl", "ndjson"):
            df.to_json(path, orient="records", lines=True)
        elif fmt == "json":
            df.to_json(path, orient="records", indent=2)
        elif fmt == "tsv":
            df.to_csv(path, sep="\t", index=False)
        else:
            df.to_csv(path, index=False)
    @staticmethod
    def detect_format_from_path(path):
        return str(path).rsplit(".", 1)[-1].lower()

def build_agent(*args, **kwargs):
    """Stub: build an ADK agent — legacy ADK, not available standalone."""
    return None
def run_agent(agent, prompt, session_id=None):
    """Stub: run an ADK agent — legacy ADK, not available standalone."""
    return ""
class CostAccumulator:
    """Stub: cost accumulator for LLM calls."""
    def __init__(self, max_cost=None):
        self.max_cost = max_cost
        self.total_usd = 0.0
        self.call_count = 0
        self.costs_by_model = {}
    def estimate_cost(self, prompt_tokens=0, completion_tokens=0, model=""):
        return 0.0
    def check_budget(self, estimated_cost):
        if self.max_cost is None:
            return True
        return self.total_usd + estimated_cost <= self.max_cost
    def summary(self):
        return {"total_usd": self.total_usd, "call_count": self.call_count}
class CostLimitExceeded(Exception):
    def __init__(self, actual=0.0, limit=0.0):
        self.actual = actual
        self.limit = limit
        super().__init__(f"Cost limit exceeded: ${actual:.4f} > ${limit:.4f}")

try:
    from synthesis_utils import sanitize_for_prompt, detect_sentinels
except ImportError:
    def sanitize_for_prompt(text, max_length=None):
        """Stub: sanitize text for prompt inclusion. See magic-data-synthesis SKILL.md for full pattern."""
        result = str(text).strip().replace("\n", " ")
        if max_length:
            result = result[:max_length]
        return result
    def detect_sentinels(series, patterns=None):
        """Stub: detect sentinel values in a series."""
        _SENTINELS = {"N/A", "NA", "n/a", "None", "none", "null", "NULL", "NaN", "nan", "-", "TBD", "tbd", "X", "x", ""}
        pat_set = set(patterns) if patterns else _SENTINELS
        indices = [i for i, v in enumerate(series) if str(v).strip() in pat_set]
        return {"sentinel_count": len(indices), "sentinel_indices": indices}

try:
    from synthesis_prompt_builder import build_row_prompt, count_tokens, select_few_shot_examples
except ImportError:
    def build_row_prompt(row, column_config, few_shot_examples=None, reference_data=None, **kwargs):
        """Stub: build a row-level prompt. See magic-data-synthesis SKILL.md for full pattern."""
        col = column_config.get("name", "output")
        ctx = "\n".join(f"  {k}: {v}" for k, v in row.items() if k != col)
        return f"Generate the '{col}' value for this row:\n{ctx}\n\nValue:"
    def count_tokens(text, model="gpt-4o-mini"):
        """Stub: estimate token count."""
        return max(1, len(str(text)) // 4)
    def select_few_shot_examples(target_row, examples, n=3, **kwargs):
        """Stub: select few-shot examples."""
        return (examples or [])[:n]

import pandas as pd

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Target Row Selection
# ──────────────────────────────────────────────────────────────

def identify_target_rows(
    df: pd.DataFrame,
    column: str,
    target_rows: str,
    sentinel_patterns: Optional[list[str]] = None,
) -> list[int]:
    """
    Identify which row indices need generation.

    Args:
        df: Input DataFrame
        column: Column name to inspect
        target_rows: One of "null_only", "sentinel", "all"
        sentinel_patterns: Sentinel values to detect (for target_rows="sentinel")

    Returns:
        List of integer row indices to process
    """
    if target_rows == "all":
        return list(range(len(df)))

    if target_rows == "null_only":
        if column not in df.columns:
            # Column doesn't exist yet — all rows are targets
            return list(range(len(df)))
        mask = df[column].isna()
        return list(df.index[mask])

    if target_rows == "sentinel":
        if column not in df.columns:
            return list(range(len(df)))
        # Null rows are always targets
        null_mask = df[column].isna()
        # Detect sentinel values
        non_null = df[column].dropna()
        if len(non_null) > 0:
            sentinel_info = detect_sentinels(non_null, patterns=sentinel_patterns)
            sentinel_idx = set(sentinel_info.get("sentinel_indices", []))
        else:
            sentinel_idx = set()
        # Combine null and sentinel indices
        target_idx = set(df.index[null_mask].tolist()) | sentinel_idx
        return sorted(target_idx)

    # Fallback: treat as "all"
    return list(range(len(df)))


# ──────────────────────────────────────────────────────────────
# Few-Shot & Reference Loading
# ──────────────────────────────────────────────────────────────

def load_few_shot_examples(path: str) -> list[dict]:
    """
    Load few-shot examples from a JSON file.

    Expected format: a JSON array of dicts, each dict representing one example row.
    """
    p = Path(path)
    if not p.exists():
        logger.warning("Few-shot examples file not found: %s", path)
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "examples" in data:
        return data["examples"]
    logger.warning("Few-shot file format not recognized; expected list or {examples: [...]}.")
    return []


def load_reference_datasets(paths: list[str]) -> list[pd.DataFrame]:
    """Load reference datasets from CSV/Parquet/JSONL paths."""
    datasets = []
    for p in paths:
        try:
            datasets.append(load_dataframe(p))
        except Exception as e:
            logger.warning("Could not load reference dataset %s: %s", p, e)
    return datasets


# ──────────────────────────────────────────────────────────────
# Column Config Builder (maps CLI args to prompt builder format)
# ──────────────────────────────────────────────────────────────

def build_column_config(
    column: str,
    prompt_template: Optional[str] = None,
) -> dict:
    """
    Build a column_config dict suitable for synthesis_prompt_builder.build_row_prompt().

    Args:
        column: Target column name
        prompt_template: Optional custom prompt template string

    Returns:
        Column config dict
    """
    config: dict = {"name": column}
    if prompt_template:
        config["custom_prompt"] = prompt_template
    return config


# ──────────────────────────────────────────────────────────────
# Model Identifier Extraction
# ──────────────────────────────────────────────────────────────

def extract_model_identifier(agent_yaml_path: str, model_override: Optional[str] = None) -> str:
    """
    Extract the model identifier string from the agent YAML or override.

    Returns:
        Model identifier string (e.g., "openai/gpt-4o-mini")
    """
    if model_override:
        return model_override
    try:
        import yaml
        with open(agent_yaml_path, "r") as f:
            config = yaml.safe_load(f)
        if isinstance(config, dict):
            model = config.get("model")
            if isinstance(model, str):
                return model
            if isinstance(model, dict):
                return model.get("model_code") or model.get("model") or "openai/gpt-4o-mini"
    except Exception:
        pass
    return "openai/gpt-4o-mini"


# ──────────────────────────────────────────────────────────────
# Dry Run
# ──────────────────────────────────────────────────────────────

def dry_run_report(
    df: pd.DataFrame,
    target_indices: list[int],
    column: str,
    column_config: dict,
    model_id: str,
    few_shot_examples: list[dict],
    reference_context: str,
    prompt_template: Optional[str] = None,
) -> dict:
    """
    Estimate tokens and cost for a dry run without making API calls.

    Builds prompts for a sample of target rows to estimate per-row token usage,
    then extrapolates to the full set.

    Returns:
        Dict with estimation details
    """
    accumulator = CostAccumulator()

    n_target = len(target_indices)
    if n_target == 0:
        return {
            "success": True,
            "dry_run": True,
            "rows_total": len(df),
            "rows_to_process": 0,
            "estimated_prompt_tokens": 0,
            "estimated_completion_tokens": 0,
            "estimated_total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "model": model_id,
        }

    # Sample up to 5 rows for estimation
    sample_size = min(5, n_target)
    import random
    sample_indices = random.sample(target_indices, sample_size)

    prompt_tokens_list = []
    for idx in sample_indices:
        row = df.iloc[idx].to_dict()
        # Select few-shot examples for this row
        selected_examples = select_few_shot_examples(
            target_row=row,
            examples=few_shot_examples,
            n=3,
        ) if few_shot_examples else []

        prompt = build_row_prompt(
            row=row,
            column_config=column_config,
            few_shot_examples=selected_examples,
            reference_data=reference_context if reference_context else None,
        )
        token_count = count_tokens(prompt, model_id)
        prompt_tokens_list.append(token_count)

    avg_prompt_tokens = sum(prompt_tokens_list) / len(prompt_tokens_list)
    # Estimate completion at 25% of prompt tokens (heuristic for single-value output)
    avg_completion_tokens = max(50, int(avg_prompt_tokens * 0.25))

    total_prompt_tokens = int(avg_prompt_tokens * n_target)
    total_completion_tokens = int(avg_completion_tokens * n_target)

    estimated_cost = accumulator.estimate_cost(
        prompt_tokens=total_prompt_tokens,
        completion_tokens=total_completion_tokens,
        model=model_id,
    )

    return {
        "success": True,
        "dry_run": True,
        "rows_total": len(df),
        "rows_to_process": n_target,
        "sample_size_for_estimate": sample_size,
        "avg_prompt_tokens_per_row": round(avg_prompt_tokens, 1),
        "avg_completion_tokens_per_row": avg_completion_tokens,
        "estimated_prompt_tokens": total_prompt_tokens,
        "estimated_completion_tokens": total_completion_tokens,
        "estimated_total_tokens": total_prompt_tokens + total_completion_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "model": model_id,
    }


# ──────────────────────────────────────────────────────────────
# Reference Context Builder
# ──────────────────────────────────────────────────────────────

def build_reference_context_str(reference_datasets: list[pd.DataFrame], max_rows: int = 20) -> str:
    """
    Build a combined reference context string from multiple reference datasets.

    Args:
        reference_datasets: List of reference DataFrames
        max_rows: Maximum rows to include per reference dataset

    Returns:
        Formatted reference context string
    """
    if not reference_datasets:
        return ""

    sections = []
    for i, ref_df in enumerate(reference_datasets):
        sample = ref_df.head(max_rows)
        lines = []
        lines.append(f"Reference dataset {i + 1} ({len(ref_df)} rows, showing first {len(sample)}):")
        lines.append(f"Columns: {', '.join(ref_df.columns.tolist())}")
        for _, row in sample.iterrows():
            row_str = " | ".join(f"{k}: {sanitize_for_prompt(str(v), max_length=200)}" for k, v in row.items())
            lines.append(f"  {row_str}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


# ──────────────────────────────────────────────────────────────
# Core Generation Loop
# ──────────────────────────────────────────────────────────────

def generate_column(
    df: pd.DataFrame,
    target_indices: list[int],
    column: str,
    agent,
    column_config: dict,
    model_id: str,
    few_shot_examples: list[dict],
    reference_context: str,
    cost_accumulator: CostAccumulator,
    batch_size: int = 10,
    workspace: Optional[str] = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Run LLM generation for each target row and merge results back into the DataFrame.

    Args:
        df: Input DataFrame (modified in place for the target column)
        target_indices: Row indices to process
        column: Target column name
        agent: Configured LlmAgent
        column_config: Column config for prompt builder
        model_id: Model identifier string
        few_shot_examples: Pre-loaded few-shot examples
        reference_context: Pre-built reference context string
        cost_accumulator: CostAccumulator instance for tracking/limiting cost
        batch_size: Rows to process before checkpointing
        workspace: Directory for checkpoint files

    Returns:
        Tuple of (result_df, stats_dict)
    """
    result_df = df.copy()

    # Initialize metadata columns if not present (object dtype to accept mixed values)
    for _meta_col in ("_synthesis_confidence", "_synthesis_model", "_synthesis_mode", "_synthesis_timestamp"):
        if _meta_col not in result_df.columns:
            result_df[_meta_col] = pd.Series([None] * len(result_df), dtype=object)

    # Ensure target column exists and has object dtype to accept string values
    if column not in result_df.columns:
        result_df[column] = pd.Series([None] * len(result_df), dtype=object)
    elif result_df[column].dtype != object:
        result_df[column] = result_df[column].astype(object)

    stats = {
        "rows_processed": 0,
        "rows_succeeded": 0,
        "rows_failed": 0,
        "cost_limit_reached": False,
        "checkpoint_path": None,
    }

    for batch_start in range(0, len(target_indices), batch_size):
        batch_indices = target_indices[batch_start:batch_start + batch_size]

        for idx in batch_indices:
            row = result_df.iloc[idx].to_dict()
            timestamp = datetime.now(timezone.utc).isoformat()

            # Select few-shot examples for this row
            selected_examples = select_few_shot_examples(
                target_row=row,
                examples=few_shot_examples,
                n=3,
            ) if few_shot_examples else []

            # Build prompt
            prompt = build_row_prompt(
                row=row,
                column_config=column_config,
                few_shot_examples=selected_examples,
                reference_data=reference_context if reference_context else None,
            )

            # Check cost budget before calling
            estimated_prompt_tokens = count_tokens(prompt, model_id)
            estimated_completion_tokens = max(50, int(estimated_prompt_tokens * 0.25))
            estimated_call_cost = cost_accumulator.estimate_cost(
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=estimated_completion_tokens,
                model=model_id,
            )

            if not cost_accumulator.check_budget(estimated_call_cost):
                stats["cost_limit_reached"] = True
                logger.warning(
                    "Cost limit would be exceeded at row %d. Stopping generation. "
                    "Processed %d/%d rows.",
                    idx,
                    stats["rows_processed"],
                    len(target_indices),
                )
                # Checkpoint completed work
                if workspace:
                    ckpt_path = save_checkpoint(
                        result_df, workspace,
                        step=1, operation="generate_column_partial",
                    )
                    stats["checkpoint_path"] = ckpt_path
                break

            # Run the agent
            try:
                response = run_agent(agent, prompt)
                response_text = response.strip() if response else ""

                # Determine confidence
                confidence = 1.0 if response_text else 0.0

                # Write results
                result_df.at[result_df.index[idx], column] = response_text
                result_df.at[result_df.index[idx], "_synthesis_confidence"] = confidence
                result_df.at[result_df.index[idx], "_synthesis_model"] = model_id
                result_df.at[result_df.index[idx], "_synthesis_mode"] = "batch"
                result_df.at[result_df.index[idx], "_synthesis_timestamp"] = timestamp

                stats["rows_succeeded"] += 1

                # Track cost (approximate — run_agent does not return litellm response)
                cost_accumulator.total_usd += estimated_call_cost
                cost_accumulator.call_count += 1
                model_key = model_id
                cost_accumulator.costs_by_model[model_key] = (
                    cost_accumulator.costs_by_model.get(model_key, 0.0) + estimated_call_cost
                )

                if cost_accumulator.max_cost is not None and cost_accumulator.total_usd > cost_accumulator.max_cost:
                    stats["cost_limit_reached"] = True
                    logger.warning(
                        "Cost limit exceeded after row %d: $%.4f > $%.4f",
                        idx,
                        cost_accumulator.total_usd,
                        cost_accumulator.max_cost,
                    )
                    if workspace:
                        ckpt_path = save_checkpoint(
                            result_df, workspace,
                            step=1, operation="generate_column_partial",
                        )
                        stats["checkpoint_path"] = ckpt_path
                    stats["rows_processed"] += 1
                    break

            except CostLimitExceeded:
                stats["cost_limit_reached"] = True
                if workspace:
                    ckpt_path = save_checkpoint(
                        result_df, workspace,
                        step=1, operation="generate_column_partial",
                    )
                    stats["checkpoint_path"] = ckpt_path
                break

            except Exception as e:
                logger.error("Generation failed for row %d: %s", idx, e)
                result_df.at[result_df.index[idx], "_synthesis_confidence"] = 0.0
                result_df.at[result_df.index[idx], "_synthesis_model"] = model_id
                result_df.at[result_df.index[idx], "_synthesis_mode"] = "batch"
                result_df.at[result_df.index[idx], "_synthesis_timestamp"] = timestamp
                stats["rows_failed"] += 1

            stats["rows_processed"] += 1

        else:
            # Inner loop completed normally (no break) — continue to next batch
            # Checkpoint at end of each batch
            if workspace and stats["rows_processed"] > 0:
                ckpt_path = save_checkpoint(
                    result_df, workspace,
                    step=1, operation="generate_column_batch",
                )
                stats["checkpoint_path"] = ckpt_path
            continue

        # Inner loop broke out — stop processing batches
        break

    return result_df, stats


# ──────────────────────────────────────────────────────────────
# Output Saving
# ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, output_path: str, output_format: str = "auto",
                input_format: str = None) -> str:
    """
    Save the result DataFrame using io_utils (supports CSV, TSV, Parquet, JSONL, JSON, Excel).
    """
    _io_utils.save_dataframe(df, output_path, format=output_format, input_format=input_format)
    return str(output_path)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Single-column generation/transformation using LLM agents (batch mode)."
    )

    # Positional
    parser.add_argument("input_path", help="Path to input data file (CSV, Parquet, JSONL)")
    parser.add_argument("output_path", help="Path to output data file (CSV, Parquet, JSONL)")

    # Required
    parser.add_argument("--column", required=True, help="Target column name to generate or fill")
    parser.add_argument("--agent-yaml", required=True, help="Path to YAML agent config file")

    # Target row selection
    parser.add_argument(
        "--target-rows",
        choices=["null_only", "sentinel", "all"],
        default="null_only",
        help="Which rows to process (default: null_only)",
    )
    parser.add_argument(
        "--sentinel-patterns",
        type=str,
        default=None,
        help='JSON array of sentinel patterns, e.g. \'["X","N/A","TBD"]\'',
    )

    # Prompt configuration
    parser.add_argument(
        "--prompt-template",
        type=str,
        default=None,
        help="Custom prompt template string with {column} placeholders for row fields",
    )
    parser.add_argument(
        "--few-shot-path",
        type=str,
        default=None,
        help="Path to JSON file with few-shot examples",
    )
    parser.add_argument(
        "--reference-paths",
        type=str,
        default=None,
        help="Comma-separated paths to reference datasets (CSV, Parquet, JSONL)",
    )

    # Model override
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model identifier (e.g., openai/gpt-4o-mini)",
    )

    # Sampling and cost controls
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Run on a random subset of N rows for preview",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show plan without making API calls (estimated tokens, cost, rows)",
    )
    parser.add_argument(
        "--max-cost",
        type=float,
        default=None,
        help="Maximum cost in USD; abort and checkpoint when reached",
    )

    # Batch and workspace
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of rows to process per batch (default: 10)",
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Directory for checkpoint files",
    )
    parser.add_argument(
        "--output-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Output file format (default: auto)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None):
    """Main entry point."""
    args = parse_args(argv)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    # ── 1. Load input data ──────────────────────────────────
    try:
        df = load_dataframe(args.input_path)
    except Exception as e:
        output_result(format_error(
            f"Failed to load input file: {e}",
            suggestion="Check file path and format (CSV, Parquet, JSONL supported)",
        ))
        return  # output_result calls sys.exit, but be safe

    rows_in = len(df)
    logger.info("Loaded %d rows from %s", rows_in, args.input_path)

    # ── 2. Parse sentinel patterns ──────────────────────────
    sentinel_patterns = None
    if args.sentinel_patterns:
        try:
            sentinel_patterns = json.loads(args.sentinel_patterns)
            if not isinstance(sentinel_patterns, list):
                output_result(format_error(
                    "--sentinel-patterns must be a JSON array",
                    suggestion='Example: \'["X","N/A","TBD"]\'',
                ))
                return
        except json.JSONDecodeError as e:
            output_result(format_error(
                f"Invalid JSON in --sentinel-patterns: {e}",
                suggestion='Example: \'["X","N/A","TBD"]\'',
            ))
            return

    # ── 3. Identify target rows ─────────────────────────────
    target_indices = identify_target_rows(
        df, args.column, args.target_rows, sentinel_patterns,
    )

    # Apply --sample-size if specified
    if args.sample_size and args.sample_size < len(target_indices):
        import random
        random.seed(42)  # Reproducible sampling
        target_indices = sorted(random.sample(target_indices, args.sample_size))
        logger.info("Sampled %d target rows (from %d)", len(target_indices), len(target_indices))

    logger.info(
        "Target rows: %d (mode=%s, column=%s)",
        len(target_indices), args.target_rows, args.column,
    )

    if len(target_indices) == 0:
        output_result(format_success(
            output_path=args.output_path,
            rows_in=rows_in,
            rows_out=rows_in,
            summary={"message": "No target rows to process", "target_mode": args.target_rows},
            warnings=["No rows matched the target criteria; output is unchanged."],
        ))
        return

    # ── 4. Load few-shot examples and references ────────────
    few_shot_examples: list[dict] = []
    if args.few_shot_path:
        few_shot_examples = load_few_shot_examples(args.few_shot_path)
        logger.info("Loaded %d few-shot examples", len(few_shot_examples))

    reference_datasets: list[pd.DataFrame] = []
    if args.reference_paths:
        ref_paths = [p.strip() for p in args.reference_paths.split(",") if p.strip()]
        reference_datasets = load_reference_datasets(ref_paths)
        logger.info("Loaded %d reference datasets", len(reference_datasets))

    reference_context = build_reference_context_str(reference_datasets)

    # ── 5. Build column config ──────────────────────────────
    column_config = build_column_config(
        column=args.column,
        prompt_template=args.prompt_template,
    )

    # ── 6. Resolve model identifier ─────────────────────────
    model_id = extract_model_identifier(args.agent_yaml, args.model)
    logger.info("Model: %s", model_id)

    # ── 7. Dry run ──────────────────────────────────────────
    if args.dry_run:
        report = dry_run_report(
            df=df,
            target_indices=target_indices,
            column=args.column,
            column_config=column_config,
            model_id=model_id,
            few_shot_examples=few_shot_examples,
            reference_context=reference_context,
            prompt_template=args.prompt_template,
        )
        output_result(report)
        return

    # ── 8. Build agent from YAML ────────────────────────────
    try:
        agent = build_agent(args.agent_yaml, model_override=args.model)
    except Exception as e:
        output_result(format_error(
            f"Failed to build agent from YAML: {e}",
            suggestion="Check agent YAML config file format and model settings",
        ))
        return

    # ── 9. Setup workspace for checkpoints ──────────────────
    workspace = args.workspace
    if workspace:
        Path(workspace).mkdir(parents=True, exist_ok=True)

    # ── 10. Initialize cost accumulator ─────────────────────
    cost_accumulator = CostAccumulator(max_cost=args.max_cost)

    # ── 11. Run generation ──────────────────────────────────
    try:
        result_df, stats = generate_column(
            df=df,
            target_indices=target_indices,
            column=args.column,
            agent=agent,
            column_config=column_config,
            model_id=model_id,
            few_shot_examples=few_shot_examples,
            reference_context=reference_context,
            cost_accumulator=cost_accumulator,
            batch_size=args.batch_size,
            workspace=workspace,
        )
    except Exception as e:
        output_result(format_error(
            f"Generation failed: {e}",
            suggestion="Check agent config, model availability, and API credentials",
            rows_in=rows_in,
        ))
        return

    # ── 12. Save output ─────────────────────────────────────
    # Detect input format from input path for smart output format resolution
    _input_fmt = _io_utils.detect_format_from_path(args.input_path)
    try:
        output_path = save_output(result_df, args.output_path, output_format=args.output_format,
                                  input_format=_input_fmt)
    except Exception as e:
        output_result(format_error(
            f"Failed to save output: {e}",
            suggestion="Check output path and disk space",
            rows_in=rows_in,
        ))
        return

    rows_out = len(result_df)

    # ── 13. Build summary ───────────────────────────────────
    summary = {
        "column": args.column,
        "target_mode": args.target_rows,
        "rows_targeted": len(target_indices),
        "rows_processed": stats["rows_processed"],
        "rows_succeeded": stats["rows_succeeded"],
        "rows_failed": stats["rows_failed"],
        "model": model_id,
        "mode": "batch",
        "cost": cost_accumulator.summary(),
    }

    if stats.get("cost_limit_reached"):
        summary["cost_limit_reached"] = True
        summary["checkpoint_path"] = stats.get("checkpoint_path")

    if args.sample_size:
        summary["sample_size"] = args.sample_size

    warnings = []
    if stats["rows_failed"] > 0:
        warnings.append(f"{stats['rows_failed']} rows failed during generation.")
    if stats.get("cost_limit_reached"):
        warnings.append(
            f"Cost limit reached (${cost_accumulator.total_usd:.4f} / "
            f"${cost_accumulator.max_cost:.4f}). "
            f"Partial results saved."
        )

    output_result(format_success(
        output_path=output_path,
        rows_in=rows_in,
        rows_out=rows_out,
        summary=summary,
        warnings=warnings,
    ))


if __name__ == "__main__":
    main()
