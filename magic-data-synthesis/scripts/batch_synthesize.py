#!/usr/bin/env python3
"""
Batch Synthesize — Multi-Column Synthesis/Transformation CLI
=============================================================
Full multi-column synthesis/transformation with checkpoint/resume.
Loads a JSON synthesis config, resolves column dependencies via topological
sort, generates/transforms columns in dependency order using LLM agents,
and supports column-level AND batch-level checkpoint/resume.

Modes:
  fill-sentinels  — only process rows where target column matches sentinel patterns
  fill-missing    — only process rows where target column is null/NaN
  transform       — process all rows (default)

Usage:
    python batch_synthesize.py INPUT_PATH OUTPUT_PATH --config CONFIG_JSON \\
      [--mode fill-sentinels|fill-missing|transform] \\
      [--batch-size 100] [--sample-size N] [--dry-run] [--max-cost FLOAT] \\
      [--workspace DIR] [--no-cleanup] [--resume]
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.

import argparse
import json
import logging
import os
import shutil
import sys
import time
import uuid
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import numpy as np

# ──────────────────────────────────────────────────────────────
# Path Setup
# ──────────────────────────────────────────────────────────────

_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILLS_DIR = _SCRIPT_DIR.parent.parent


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
def find_latest_checkpoint(workspace, prefix="ckpt"):
    """Stub: find the latest checkpoint file in a workspace."""
    import glob
    from pathlib import Path
    files = sorted(glob.glob(str(Path(workspace) / f"{prefix}*.csv")))
    return files[-1] if files else None

class _io_utils:
    @staticmethod
    def load_dataframe(path, format="auto", flatten_depth=0, **kwargs):
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
    def add(self, model="", prompt_tokens=0, completion_tokens=0):
        pass
    def summary(self):
        return {"total_usd": self.total_usd, "call_count": self.call_count}
class CostLimitExceeded(Exception):
    def __init__(self, actual=0.0, limit=0.0):
        self.actual = actual
        self.limit = limit
        super().__init__(f"Cost limit exceeded: ${actual:.4f} > ${limit:.4f}")

try:
    from synthesis_utils import sanitize_for_prompt, detect_sentinels, extract_json_from_response
except ImportError:
    def sanitize_for_prompt(text, max_length=None):
        """Stub: sanitize text for prompt inclusion. See magic-data-synthesis SKILL.md for full pattern."""
        result = str(text).strip().replace("\n", " ")
        if max_length:
            result = result[:max_length]
        return result
    def detect_sentinels(series, patterns=None):
        """Stub: detect sentinel values in a series."""
        _SENTINELS = {"N/A", "NA", "n/a", "None", "none", "null", "NULL", "NaN", "nan", "-", "TBD", "x", "X", ""}
        pat_set = set(patterns) if patterns else _SENTINELS
        count = int(series.astype(str).str.strip().isin(pat_set).sum())
        return {"sentinel_count": count, "sentinel_rate": round(count / max(len(series), 1), 4)}
    def extract_json_from_response(text):
        """Stub: extract JSON substring from LLM response text."""
        import re
        text = text.strip()
        # Strip markdown fences
        text = re.sub(r"```(?:json)?\n?", "", text).strip().rstrip("`").strip()
        # Find first { ... } block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group() if match else text

try:
    from synthesis_config import load_config, validate_config, build_generation_plan, topological_sort
except ImportError:
    def load_config(config_path):
        """Stub: load synthesis config JSON. See magic-data-synthesis SKILL.md for full pattern."""
        import json
        with open(config_path, "r") as f:
            return json.load(f)
    def validate_config(config, base_dir=None):
        """Stub: validate synthesis config."""
        return {"valid": True, "errors": [], "warnings": []}
    def build_generation_plan(config):
        """Stub: build generation plan from config."""
        columns = config.get("columns", [])
        return {"column_order": [c["name"] for c in columns], "columns": columns, "sentinel_patterns": config.get("sentinel_patterns"), "total_columns": len(columns)}
    def topological_sort(config):
        """Stub: topological sort of column dependencies."""
        return [c["name"] for c in config.get("columns", [])]

try:
    from sentinel_patterns import EXACT_SENTINELS
except ImportError:
    EXACT_SENTINELS = {"N/A", "NA", "n/a", "na", "N/a", "None", "none", "NONE", "null", "NULL", "Null", "NaN", "nan", "NAN", "-", "--", "---", ".", "..", "...", "?", "??", "???", "TBD", "tbd", "TODO", "todo", "MISSING", "missing", "Missing", "UNKNOWN", "unknown", "Unknown", "X", "x", "placeholder", "Placeholder", "PLACEHOLDER"}

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

DEFAULT_BATCH_SIZE = 100
DEFAULT_MODE = "transform"
VALID_MODES = ("fill-sentinels", "fill-missing", "transform")
COST_LIMIT_EXIT_CODE = 2

# Default sentinel patterns (used when config doesn't specify any)
DEFAULT_SENTINEL_PATTERNS = list(EXACT_SENTINELS)

# Metadata column names
META_CONFIDENCE = "_synthesis_confidence"
META_MODEL = "_synthesis_model"
META_MODE = "_synthesis_mode"
META_TIMESTAMP = "_synthesis_timestamp"


# ──────────────────────────────────────────────────────────────
# Checkpoint Management
# ──────────────────────────────────────────────────────────────

def _progress_path(workspace: str, column_name: str) -> str:
    """Return the column-level progress file path."""
    safe_name = column_name.replace("/", "_").replace("\\", "_").replace(" ", "_")
    return str(Path(workspace) / f"col_{safe_name}_progress.json")


def _batch_checkpoint_path(workspace: str, batch_num: int) -> str:
    """Return the batch-level checkpoint file path."""
    return str(Path(workspace) / f"ckpt_batch_{batch_num:03d}.csv")


def save_column_progress(workspace: str, column_name: str, status: str,
                         batches_completed: int = 0, total_batches: int = 0,
                         extra: Optional[dict] = None):
    """Save column-level progress to a JSON file."""
    progress = {
        "column": column_name,
        "status": status,
        "batches_completed": batches_completed,
        "total_batches": total_batches,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        progress.update(extra)

    path = _progress_path(workspace, column_name)
    with open(path, "w") as f:
        json.dump(progress, f, indent=2, default=str)


def load_column_progress(workspace: str, column_name: str) -> Optional[dict]:
    """Load column-level progress, or None if no checkpoint exists."""
    path = _progress_path(workspace, column_name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_batch_checkpoint(workspace: str, batch_num: int, df_batch: pd.DataFrame):
    """Save a batch checkpoint as a CSV file."""
    path = _batch_checkpoint_path(workspace, batch_num)
    df_batch.to_csv(path, index=False)
    return path


def load_batch_checkpoints(workspace: str) -> list[str]:
    """Find all batch checkpoint files in the workspace, sorted by batch number."""
    import glob
    pattern = str(Path(workspace) / "ckpt_batch_*.csv")
    return sorted(glob.glob(pattern))


def cleanup_checkpoints(workspace: str):
    """Remove all checkpoint files from the workspace."""
    import glob

    # Remove column progress files
    for f in glob.glob(str(Path(workspace) / "col_*_progress.json")):
        try:
            os.remove(f)
        except OSError:
            pass

    # Remove batch checkpoint files
    for f in glob.glob(str(Path(workspace) / "ckpt_batch_*.csv")):
        try:
            os.remove(f)
        except OSError:
            pass


# ──────────────────────────────────────────────────────────────
# Row Selection by Mode
# ──────────────────────────────────────────────────────────────

def get_target_row_mask(df: pd.DataFrame, column_name: str, mode: str,
                        sentinel_patterns: Optional[list[str]] = None) -> pd.Series:
    """
    Return a boolean mask indicating which rows should be processed.

    Args:
        df: Input DataFrame
        column_name: Target column to check
        mode: Processing mode (fill-sentinels, fill-missing, transform)
        sentinel_patterns: Sentinel patterns for fill-sentinels mode

    Returns:
        Boolean Series (True = process this row)
    """
    if mode == "transform":
        # Process all rows
        return pd.Series(True, index=df.index)

    if mode == "fill-missing":
        # Process rows where target column is null/NaN
        if column_name not in df.columns:
            # Column doesn't exist yet — all rows need generation
            return pd.Series(True, index=df.index)
        return df[column_name].isna()

    if mode == "fill-sentinels":
        patterns = sentinel_patterns or DEFAULT_SENTINEL_PATTERNS
        if column_name not in df.columns:
            return pd.Series(True, index=df.index)

        # Check for NaN OR sentinel pattern match
        is_null = df[column_name].isna()
        str_vals = df[column_name].astype(str).str.strip()
        is_sentinel = str_vals.isin(patterns)
        return is_null | is_sentinel

    # Fallback: process all rows
    return pd.Series(True, index=df.index)


# ──────────────────────────────────────────────────────────────
# Prompt Building for Row
# ──────────────────────────────────────────────────────────────

def build_prompt_for_row(row: dict, column_config: dict,
                         available_columns: list[str]) -> str:
    """
    Build a plain-text prompt for a single row based on column config.

    Uses depends_on columns as context, the column description as guidance,
    and requests a single value output.

    Args:
        row: Row data as dict
        column_config: Column config from the generation plan
        available_columns: List of columns available in the current dataset

    Returns:
        Prompt string for the LLM
    """
    col_name = column_config["name"]
    description = column_config.get("description", "")
    depends_on = column_config.get("depends_on", [])
    strategy = column_config.get("strategy", "llm_text")

    # Build context from dependency columns
    context_parts = []
    for dep_col in depends_on:
        if dep_col in row and row[dep_col] is not None:
            sanitized = sanitize_for_prompt(str(row[dep_col]))
            context_parts.append(f"  {dep_col}: {sanitized}")

    # Also include other available columns as context (excluding the target)
    for col in available_columns:
        if col != col_name and col not in depends_on and col in row:
            val = row[col]
            if val is not None and not (isinstance(val, float) and np.isnan(val)):
                sanitized = sanitize_for_prompt(str(val))
                context_parts.append(f"  {col}: {sanitized}")

    # Build prompt
    parts = []

    if description:
        parts.append(
            f"Generate the '{col_name}' column value for the row below.\n"
            f"Column description: {description}"
        )
    else:
        parts.append(f"Generate the '{col_name}' column value for the row below.")

    if context_parts:
        parts.append("Row context:\n" + "\n".join(context_parts))

    # Output format guidance
    if strategy == "llm_structured":
        output_columns = column_config.get("output_columns", [])
        output_schema = column_config.get("output_schema", {})
        fields_spec = json.dumps(output_columns) if output_columns else json.dumps(output_schema)
        # Use a strong directive that primes the model to start immediately with `{`.
        # Thinking models often write a verbose preamble even when told not to;
        # the explicit "Your response must begin with {" anchors the first token.
        parts.append(
            "OUTPUT FORMAT — CRITICAL:\n"
            "Your response MUST begin with `{` and end with `}`. "
            "Output ONLY a valid JSON object with no preamble, no reasoning steps, "
            "no explanation, and no code fences.\n"
            f"Required fields: {fields_spec}"
        )
    else:
        parts.append(
            f"Return only the value for '{col_name}' — no explanation, no markdown, no quotes."
        )

    return "\n\n".join(parts)


# ──────────────────────────────────────────────────────────────
# Dry-Run Estimation
# ──────────────────────────────────────────────────────────────

def estimate_dry_run(df: pd.DataFrame, plan: dict, mode: str,
                     sentinel_patterns: Optional[list[str]] = None,
                     batch_size: int = DEFAULT_BATCH_SIZE) -> dict:
    """
    Estimate work to be done without making any API calls.

    Returns:
        Dict with columns, estimated calls, token estimates, and cost estimates.
    """
    accumulator = CostAccumulator()
    column_estimates = []

    for col_config in plan["columns"]:
        col_name = col_config["name"]
        strategy = col_config["strategy"]

        # Only LLM strategies involve API calls
        if strategy not in ("llm_text", "llm_structured"):
            column_estimates.append({
                "column": col_name,
                "strategy": strategy,
                "llm_calls": 0,
                "estimated_tokens": 0,
                "estimated_cost_usd": 0.0,
                "note": "Non-LLM strategy — no API calls needed",
            })
            continue

        # Count target rows
        mask = get_target_row_mask(df, col_name, mode, sentinel_patterns)
        target_rows = int(mask.sum())

        # Estimate tokens per call (rough heuristic)
        avg_prompt_tokens = 250  # average prompt size
        avg_completion_tokens = 50  # average response size

        total_prompt_tokens = target_rows * avg_prompt_tokens
        total_completion_tokens = target_rows * avg_completion_tokens

        # Estimate cost
        model = col_config.get("model", "openai/gpt-4o-mini")
        per_call_cost = accumulator.estimate_cost(
            prompt_tokens=avg_prompt_tokens,
            completion_tokens=avg_completion_tokens,
            model=model,
        )
        total_cost = per_call_cost * target_rows

        num_batches = (target_rows + batch_size - 1) // batch_size if target_rows > 0 else 0

        column_estimates.append({
            "column": col_name,
            "strategy": strategy,
            "model": model,
            "target_rows": target_rows,
            "llm_calls": target_rows,
            "num_batches": num_batches,
            "estimated_prompt_tokens": total_prompt_tokens,
            "estimated_completion_tokens": total_completion_tokens,
            "estimated_total_tokens": total_prompt_tokens + total_completion_tokens,
            "estimated_cost_usd": round(total_cost, 6),
        })

    # Totals
    total_calls = sum(c.get("llm_calls", 0) for c in column_estimates)
    total_tokens = sum(c.get("estimated_total_tokens", 0) for c in column_estimates)
    total_cost = sum(c.get("estimated_cost_usd", 0.0) for c in column_estimates)

    return {
        "total_rows": len(df),
        "total_columns": len(column_estimates),
        "column_order": plan["column_order"],
        "columns": column_estimates,
        "totals": {
            "llm_calls": total_calls,
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 6),
        },
    }


# ──────────────────────────────────────────────────────────────
# Non-LLM Strategy Executors
# ──────────────────────────────────────────────────────────────

def execute_expression_strategy(df: pd.DataFrame, col_config: dict) -> pd.DataFrame:
    """Execute an expression strategy — evaluate a Python expression per row."""
    col_name = col_config["name"]
    expr = col_config.get("expr", "")
    if not expr:
        logger.warning("Expression strategy for '%s' has empty expr — skipping", col_name)
        return df

    try:
        df[col_name] = df.eval(expr)
    except Exception as e:
        logger.error("Expression evaluation failed for '%s': %s", col_name, e)
        # Fall back to apply with eval
        try:
            df[col_name] = df.apply(lambda row: eval(expr, {"__builtins__": {}}, row.to_dict()), axis=1)
        except Exception as e2:
            raise ValueError(f"Expression '{expr}' failed for column '{col_name}': {e2}") from e2

    return df


def execute_statistical_sample_strategy(df: pd.DataFrame, col_config: dict) -> pd.DataFrame:
    """Execute a statistical_sample strategy — sample from existing column distribution."""
    col_name = col_config["name"]
    source_column = col_config.get("source_column", "")
    seed = col_config.get("seed")

    if source_column not in df.columns:
        raise ValueError(
            f"Source column '{source_column}' not found for statistical_sample "
            f"strategy on column '{col_name}'"
        )

    source_values = df[source_column].dropna()
    if len(source_values) == 0:
        raise ValueError(f"Source column '{source_column}' has no non-null values")

    rng = np.random.default_rng(seed)
    sampled = rng.choice(source_values.values, size=len(df), replace=True)
    df[col_name] = sampled

    return df


def execute_reference_lookup_strategy(df: pd.DataFrame, col_config: dict) -> pd.DataFrame:
    """Execute a reference_lookup strategy — join with a reference dataset."""
    col_name = col_config["name"]
    reference_path = col_config.get("reference_path", "")
    join_key = col_config.get("join_key", "")
    enrich_columns = col_config.get("enrich_columns", [])
    match_type = col_config.get("match_type", "left")

    if not reference_path or not join_key:
        raise ValueError(
            f"reference_lookup strategy for '{col_name}' requires "
            f"'reference_path' and 'join_key'"
        )

    ref_df = load_dataframe(reference_path)

    if join_key not in df.columns:
        raise ValueError(f"Join key '{join_key}' not found in input dataset")
    if join_key not in ref_df.columns:
        raise ValueError(f"Join key '{join_key}' not found in reference dataset")

    # Select columns to enrich
    if enrich_columns:
        ref_cols = [join_key] + [c for c in enrich_columns if c in ref_df.columns]
    else:
        ref_cols = ref_df.columns.tolist()

    ref_subset = ref_df[ref_cols].drop_duplicates(subset=[join_key])

    df = df.merge(ref_subset, on=join_key, how=match_type, suffixes=("", "_ref"))

    return df


# ──────────────────────────────────────────────────────────────
# YAML Model Resolution Helper
# ──────────────────────────────────────────────────────────────

def _read_model_from_yaml(yaml_path: str) -> Optional[str]:
    """Read the model identifier from a YAML agent config file."""
    try:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            return None
        model = config.get("model")
        if isinstance(model, str):
            return model
        if isinstance(model, dict):
            return model.get("model_code") or model.get("model")
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────────────────────
# LLM Column Processing
# ──────────────────────────────────────────────────────────────

def process_llm_column(
    df: pd.DataFrame,
    col_config: dict,
    mode: str,
    sentinel_patterns: Optional[list[str]],
    batch_size: int,
    workspace: str,
    cost_accumulator: CostAccumulator,
    resume_from_batch: int = 0,
) -> pd.DataFrame:
    """
    Process a single LLM-based column: identify target rows, process in batches,
    checkpoint after each batch.

    Args:
        df: Working DataFrame (modified in place with generated values)
        col_config: Column config from the generation plan
        mode: Processing mode
        sentinel_patterns: Sentinel patterns for fill-sentinels mode
        batch_size: Number of rows per batch
        workspace: Directory for checkpoint files
        cost_accumulator: Cost tracking accumulator
        resume_from_batch: Batch number to resume from (0 = start fresh)

    Returns:
        Updated DataFrame with generated column values
    """
    col_name = col_config["name"]
    strategy = col_config["strategy"]

    # Resolve model: config JSON > YAML agent config > default
    agent_yaml = col_config.get("agent_yaml")
    model = col_config.get("model")
    if model is None and agent_yaml:
        model = _read_model_from_yaml(agent_yaml)
    if model is None:
        model = "openai/gpt-4o-mini"

    # Build or load the agent
    if agent_yaml:
        agent = build_agent(agent_yaml, model_override=model)
    else:
        # Create a minimal agent config in workspace
        agent_yaml_path = str(Path(workspace) / f"agent_{col_name}.yaml")
        agent_config = {
            "name": f"synthesizer_{col_name}",
            "model": model,
            "instruction": (
                f"You are a data synthesis assistant. Generate accurate values "
                f"for the '{col_name}' column based on the provided row context. "
                f"Return only the value — no explanation, no formatting."
            ),
        }
        import yaml
        with open(agent_yaml_path, "w") as f:
            yaml.safe_dump(agent_config, f)
        agent = build_agent(agent_yaml_path, model_override=model)

    # Get instruction override from config
    instruction_override = col_config.get("instruction")

    # Determine target rows
    mask = get_target_row_mask(df, col_name, mode, sentinel_patterns)
    target_indices = df.index[mask].tolist()

    if not target_indices:
        logger.info("Column '%s': no target rows — skipping", col_name)
        return df

    # Ensure target column exists
    if col_name not in df.columns:
        df[col_name] = np.nan

    # Pre-initialize LLM output columns as object dtype to prevent FutureWarning/
    # error when assigning strings into float64 columns (pandas ≥ 2.1).
    if strategy in ("llm_text", "llm_structured"):
        if df[col_name].dtype != object:
            df[col_name] = df[col_name].astype(object)
    if strategy == "llm_structured":
        output_columns = col_config.get("output_columns", [])
        for out_col in output_columns:
            if out_col not in df.columns or df[out_col].dtype != object:
                df[out_col] = pd.Series([None] * len(df), dtype=object)

    # Available columns for context
    available_columns = [c for c in df.columns if not c.startswith("_synthesis_")]

    # Split into batches
    total_batches = (len(target_indices) + batch_size - 1) // batch_size
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info(
        "Column '%s': %d target rows, %d batches (resume from batch %d)",
        col_name, len(target_indices), total_batches, resume_from_batch,
    )

    for batch_num in range(total_batches):
        if batch_num < resume_from_batch:
            logger.info("Column '%s': skipping batch %d (already completed)", col_name, batch_num)
            continue

        # Get batch indices
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(target_indices))
        batch_indices = target_indices[start_idx:end_idx]

        logger.info(
            "Column '%s': processing batch %d/%d (%d rows)",
            col_name, batch_num + 1, total_batches, len(batch_indices),
        )

        # Process each row in the batch
        for row_idx in batch_indices:
            row_data = df.loc[row_idx].to_dict()

            # Build prompt
            prompt = build_prompt_for_row(row_data, col_config, available_columns)

            # Run agent
            try:
                session_id = str(uuid.uuid4())
                response = run_agent(agent, prompt, session_id=session_id)

                # Bug 4 fix: track cost after each ADK runner call.
                # run_agent() returns a plain string, so estimate tokens from
                # prompt/response lengths (1 token ≈ 4 chars is a conservative estimate).
                if cost_accumulator:
                    try:
                        est_prompt_tokens = max(1, len(prompt) // 4)
                        est_completion_tokens = max(1, len(response) // 4)
                        cost_accumulator.add(
                            model=model,
                            prompt_tokens=est_prompt_tokens,
                            completion_tokens=est_completion_tokens,
                        )
                    except CostLimitExceeded:
                        raise
                    except Exception:
                        pass  # cost tracking is best-effort

                # Handle structured output
                if strategy == "llm_structured":
                    try:
                        # Use extract_json_from_response to handle thinking-model
                        # responses that prefix the JSON with reasoning text.
                        json_text = extract_json_from_response(response)
                        parsed = json.loads(json_text)
                        if isinstance(parsed, dict):
                            output_columns = col_config.get("output_columns", [])
                            for out_col in output_columns:
                                if out_col in parsed:
                                    df.at[row_idx, out_col] = parsed[out_col]
                            # Store the extracted JSON (not the full thinking text)
                            df.at[row_idx, col_name] = json_text
                        else:
                            df.at[row_idx, col_name] = json_text
                    except json.JSONDecodeError:
                        df.at[row_idx, col_name] = response
                else:
                    df.at[row_idx, col_name] = response.strip()

                # Set quality metadata
                df.at[row_idx, META_CONFIDENCE] = 0.8  # Default confidence for batch mode
                df.at[row_idx, META_MODEL] = model
                df.at[row_idx, META_MODE] = "batch"
                df.at[row_idx, META_TIMESTAMP] = timestamp

            except CostLimitExceeded:
                # Save checkpoint before aborting
                logger.warning(
                    "Cost limit reached during column '%s', batch %d",
                    col_name, batch_num,
                )
                save_column_progress(
                    workspace, col_name, "cost_limit",
                    batches_completed=batch_num, total_batches=total_batches,
                )
                raise

            except Exception as e:
                logger.error(
                    "Error generating value for column '%s', row %d: %s",
                    col_name, row_idx, e,
                )
                df.at[row_idx, col_name] = np.nan
                df.at[row_idx, META_CONFIDENCE] = 0.0
                df.at[row_idx, META_MODEL] = model
                df.at[row_idx, META_MODE] = "batch"
                df.at[row_idx, META_TIMESTAMP] = timestamp

        # Track cost (approximate — actual cost is tracked per response in CostAccumulator)
        # Check budget before continuing
        if not cost_accumulator.check_budget(0):
            save_column_progress(
                workspace, col_name, "cost_limit",
                batches_completed=batch_num + 1, total_batches=total_batches,
            )
            raise CostLimitExceeded(cost_accumulator.total_usd, cost_accumulator.max_cost)

        # Save batch checkpoint
        batch_df = df.loc[batch_indices]
        save_batch_checkpoint(workspace, batch_num, batch_df)

        # Update column progress
        save_column_progress(
            workspace, col_name, "in_progress",
            batches_completed=batch_num + 1, total_batches=total_batches,
        )

        logger.info("Column '%s': batch %d/%d complete", col_name, batch_num + 1, total_batches)

    return df


# ──────────────────────────────────────────────────────────────
# Output Helpers
# ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, output_path: str, output_format: str = "auto",
                input_format: str = None):
    """Save the output DataFrame using io_utils (supports CSV, TSV, Parquet, JSONL, JSON, Excel)."""
    _io_utils.save_dataframe(df, output_path, format=output_format, input_format=input_format)


# ──────────────────────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Batch multi-column synthesis/transformation with checkpoint/resume"
    )
    parser.add_argument("input_path", help="Path to input data file (CSV, Parquet, JSON, JSONL)")
    parser.add_argument("output_path", help="Path to output data file")
    parser.add_argument("--config", required=True, help="Path to JSON synthesis config")
    parser.add_argument(
        "--mode", choices=VALID_MODES, default=DEFAULT_MODE,
        help="Processing mode: fill-sentinels, fill-missing, or transform (default: transform)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
        help=f"Number of rows per batch (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--sample-size", type=int, default=None,
        help="Random sample N rows for preview (runs on subset only)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show plan without making API calls or writing output",
    )
    parser.add_argument(
        "--max-cost", type=float, default=None,
        help="Maximum total cost in USD — abort and checkpoint if exceeded",
    )
    parser.add_argument(
        "--workspace", type=str, default=None,
        help="Directory for checkpoint files (default: output_path directory)",
    )
    parser.add_argument(
        "--no-cleanup", action="store_true",
        help="Keep checkpoint files after successful completion",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from existing checkpoints (skip completed columns/batches)",
    )
    parser.add_argument(
        "--output-format", default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Output file format (default: auto)",
    )
    parser.add_argument(
        "--flatten-depth", type=int, default=0,
        help="Flatten nested JSON objects to this depth (0=no flattening)",
    )
    parser.add_argument(
        "--base-url", type=str, default=None,
        help="LLM API base URL (overrides MAGIC_LLM_BASE_URL env var)",
    )
    parser.add_argument(
        "--api-key", type=str, default=None,
        help="LLM API key (overrides MAGIC_LLM_API_KEY env var)",
    )
    parser.add_argument(
        "--smart-sample", action="store_true", default=False,
        help="Ensure sampled rows include those with missing/sentinel values",
    )
    parser.add_argument(
        "--stratify-column", type=str, default=None,
        help="Column to use for stratified sampling",
    )

    args = parser.parse_args()

    # Thread LLM config CLI flags to environment variables
    if args.base_url:
        os.environ["MAGIC_LLM_BASE_URL"] = args.base_url
    if args.api_key:
        os.environ["MAGIC_LLM_API_KEY"] = args.api_key

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stderr,
    )

    start_time = time.time()

    # ── 1. Load config ──────────────────────────────────────
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        output_result(format_error(str(e), suggestion="Check the --config path"))
    except json.JSONDecodeError as e:
        output_result(format_error(
            f"Invalid JSON in config: {e}",
            suggestion="Ensure the config file contains valid JSON",
        ))

    # ── 2. Validate config ──────────────────────────────────
    config_dir = str(Path(args.config).parent)
    validation = validate_config(config, base_dir=config_dir)

    if not validation["valid"]:
        result = {
            "success": False,
            "error": "Config validation failed",
            "validation_errors": validation["errors"],
            "warnings": validation["warnings"],
        }
        output_result(result)

    if validation["warnings"]:
        for w in validation["warnings"]:
            logger.warning("Config warning: %s", w)

    # ── 3. Build generation plan ────────────────────────────
    try:
        plan = build_generation_plan(config)
    except ValueError as e:
        output_result(format_error(
            f"Dependency resolution failed: {e}",
            suggestion="Check for circular dependencies in the config",
        ))

    column_order = plan["column_order"]
    sentinel_patterns = plan.get("sentinel_patterns") or DEFAULT_SENTINEL_PATTERNS

    logger.info("Generation plan: %d columns in order: %s", len(column_order), column_order)

    # ── 4. Load input data ──────────────────────────────────
    _flatten_depth = getattr(args, 'flatten_depth', 0)
    try:
        df = _io_utils.load_dataframe(args.input_path, flatten_depth=_flatten_depth)
    except FileNotFoundError:
        output_result(format_error(
            f"Input file not found: {args.input_path}",
            suggestion="Check the input file path",
        ))
    except Exception as e:
        output_result(format_error(
            f"Failed to load input data: {e}",
            suggestion="Check the input file format and encoding",
        ))

    rows_in = len(df)
    logger.info("Loaded %d rows from %s", rows_in, args.input_path)

    # Validate depends_on columns exist in source data
    available_cols = set(df.columns)
    for col_config in plan["columns"]:
        depends_on = col_config.get("depends_on", [])
        for dep in depends_on:
            if dep not in available_cols:
                logger.warning(
                    "Column '%s' depends_on '%s' which is not in the source data. "
                    "Available columns: %s",
                    col_config["name"], dep, sorted(available_cols),
                )

    if rows_in == 0:
        output_result(format_error(
            "Input file is empty",
            suggestion="Provide a non-empty input file",
            rows_in=0,
        ))

    # ── 5. Sample if requested ──────────────────────────────
    if args.sample_size and args.sample_size < rows_in:
        if args.stratify_column and args.stratify_column in df.columns:
            # Stratified sampling
            from sklearn.model_selection import train_test_split
            try:
                _, df = train_test_split(
                    df, test_size=args.sample_size, stratify=df[args.stratify_column],
                    random_state=42,
                )
                df = df.reset_index(drop=True)
                logger.info("Stratified-sampled %d rows by '%s'", len(df), args.stratify_column)
            except Exception as e:
                logger.warning("Stratified sampling failed (%s), falling back to smart/plain", e)
                df = df.sample(n=args.sample_size, random_state=42).reset_index(drop=True)
        elif args.smart_sample:
            # Smart sampling: ensure rows with missing/sentinel values are included
            target_cols = [c["name"] for c in plan["columns"]]
            needs_work = pd.Series(False, index=df.index)
            for tc in target_cols:
                if tc in df.columns:
                    needs_work |= df[tc].isna()
                    str_vals = df[tc].astype(str).str.strip()
                    needs_work |= str_vals.isin(sentinel_patterns)
                else:
                    needs_work |= True  # Column doesn't exist — all rows need work

            work_rows = df[needs_work]
            ok_rows = df[~needs_work]

            # Guarantee at least 30% of sample from rows needing work
            min_work = min(len(work_rows), max(1, int(args.sample_size * 0.3)))
            remaining = args.sample_size - min_work

            work_sample = work_rows.sample(n=min(min_work, len(work_rows)), random_state=42)
            ok_sample = ok_rows.sample(n=min(remaining, len(ok_rows)), random_state=42)

            df = pd.concat([work_sample, ok_sample]).sample(frac=1, random_state=42).reset_index(drop=True)
            logger.info("Smart-sampled %d rows (%d needing work, %d ok)", len(df), len(work_sample), len(ok_sample))
        else:
            df = df.sample(n=args.sample_size, random_state=42).reset_index(drop=True)
            logger.info("Sampled %d rows for preview", args.sample_size)

    # ── Setup workspace ─────────────────────────────────────
    workspace = args.workspace or str(Path(args.output_path).parent)
    os.makedirs(workspace, exist_ok=True)

    # ── 6. Dry-run mode ─────────────────────────────────────
    if args.dry_run:
        estimates = estimate_dry_run(
            df, plan, args.mode, sentinel_patterns, args.batch_size,
        )
        result = {
            "success": True,
            "dry_run": True,
            "input_path": args.input_path,
            "output_path": args.output_path,
            "mode": args.mode,
            "batch_size": args.batch_size,
            "sample_size": args.sample_size,
            "rows_in": rows_in,
            "rows_sampled": len(df),
            "plan": estimates,
            "warnings": validation.get("warnings", []),
        }
        if args.max_cost is not None:
            total_est = estimates["totals"]["estimated_cost_usd"]
            result["budget"] = {
                "max_cost_usd": args.max_cost,
                "estimated_cost_usd": total_est,
                "within_budget": total_est <= args.max_cost,
            }
        output_result(result)

    # ── 7. Initialize cost tracking ─────────────────────────
    cost_accumulator = CostAccumulator(max_cost=args.max_cost)

    # ── 8. Resume logic ─────────────────────────────────────
    completed_columns = set()
    resume_batches = {}  # column_name -> batch to resume from

    if args.resume:
        for col_name in column_order:
            progress = load_column_progress(workspace, col_name)
            if progress:
                if progress.get("status") == "completed":
                    completed_columns.add(col_name)
                    logger.info("Resume: column '%s' already completed — skipping", col_name)
                elif progress.get("status") == "in_progress":
                    resume_batches[col_name] = progress.get("batches_completed", 0)
                    logger.info(
                        "Resume: column '%s' resuming from batch %d",
                        col_name, resume_batches[col_name],
                    )

    # ── 9. Process columns in topological order ─────────────
    column_map = {col["name"]: col for col in plan["columns"]}
    column_results = {}
    cost_limit_hit = False

    for col_idx, col_name in enumerate(column_order):
        col_config = column_map[col_name]
        strategy = col_config["strategy"]

        logger.info(
            "Processing column %d/%d: '%s' (strategy: %s)",
            col_idx + 1, len(column_order), col_name, strategy,
        )

        # Skip completed columns (resume mode)
        if col_name in completed_columns:
            column_results[col_name] = {"status": "skipped_resume", "strategy": strategy}
            continue

        try:
            if strategy in ("llm_text", "llm_structured"):
                # LLM-based generation
                resume_batch = resume_batches.get(col_name, 0)
                df = process_llm_column(
                    df=df,
                    col_config=col_config,
                    mode=args.mode,
                    sentinel_patterns=sentinel_patterns,
                    batch_size=args.batch_size,
                    workspace=workspace,
                    cost_accumulator=cost_accumulator,
                    resume_from_batch=resume_batch,
                )

            elif strategy == "expression":
                df = execute_expression_strategy(df, col_config)

            elif strategy == "statistical_sample":
                df = execute_statistical_sample_strategy(df, col_config)

            elif strategy == "reference_lookup":
                df = execute_reference_lookup_strategy(df, col_config)

            else:
                logger.warning("Unknown strategy '%s' for column '%s' — skipping", strategy, col_name)
                column_results[col_name] = {
                    "status": "skipped",
                    "reason": f"Unknown strategy '{strategy}'",
                }
                continue

            # Mark column as completed
            save_column_progress(workspace, col_name, "completed")
            column_results[col_name] = {"status": "completed", "strategy": strategy}
            logger.info("Column '%s' completed successfully", col_name)

        except CostLimitExceeded as e:
            logger.warning("Cost limit exceeded: %s", e)
            column_results[col_name] = {
                "status": "cost_limit",
                "strategy": strategy,
                "cost_at_abort": round(e.actual, 6),
                "cost_limit": round(e.limit, 6),
            }
            cost_limit_hit = True
            break

        except Exception as e:
            logger.error("Failed to process column '%s': %s", col_name, e)
            save_column_progress(workspace, col_name, "failed", extra={"error": str(e)})
            column_results[col_name] = {
                "status": "failed",
                "strategy": strategy,
                "error": str(e),
            }
            # Continue to next column — don't abort the whole pipeline
            continue

    # ── 10. Save output ─────────────────────────────────────
    elapsed = round(time.time() - start_time, 2)
    rows_out = len(df)
    _input_fmt = _io_utils.detect_format_from_path(args.input_path)

    try:
        save_output(df, args.output_path, output_format=args.output_format,
                    input_format=_input_fmt)
    except Exception as e:
        output_result(format_error(
            f"Failed to save output: {e}",
            suggestion="Check disk space and write permissions",
            rows_in=rows_in,
        ))

    # ── 11. Cleanup checkpoints ─────────────────────────────
    if not args.no_cleanup and not cost_limit_hit:
        cleanup_checkpoints(workspace)
        logger.info("Cleaned up checkpoint files")

    # ── 12. Build final result ──────────────────────────────
    completed_count = sum(1 for r in column_results.values() if r.get("status") == "completed")
    failed_count = sum(1 for r in column_results.values() if r.get("status") == "failed")
    skipped_count = sum(1 for r in column_results.values() if r.get("status") in ("skipped", "skipped_resume"))

    summary = {
        "columns_total": len(column_order),
        "columns_completed": completed_count,
        "columns_failed": failed_count,
        "columns_skipped": skipped_count,
        "column_order": column_order,
        "column_results": column_results,
        "mode": args.mode,
        "batch_size": args.batch_size,
        "sample_size": args.sample_size,
        "elapsed_seconds": elapsed,
        "cost": cost_accumulator.summary(),
    }

    warnings = validation.get("warnings", [])

    if cost_limit_hit:
        # Exit with special code for cost limit
        result = {
            "success": False,
            "error": "Cost limit exceeded — partial results saved",
            "output_path": str(args.output_path),
            "rows_in": rows_in,
            "rows_out": rows_out,
            "summary": summary,
            "warnings": warnings,
        }
        print(json.dumps(result, indent=2, default=str))
        sys.exit(COST_LIMIT_EXIT_CODE)

    result = format_success(
        output_path=args.output_path,
        rows_in=rows_in,
        rows_out=rows_out,
        summary=summary,
        warnings=warnings,
    )
    output_result(result)


if __name__ == "__main__":
    main()
