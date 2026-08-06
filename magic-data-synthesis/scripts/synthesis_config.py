#!/usr/bin/env python3
"""
Synthesis Configuration Loader and Validator
=============================================
Load and validate JSON synthesis configs: required fields per strategy,
dependency graph via Kahn's algorithm, circular dependency detection,
YAML agent config path validation, flexible sentinel pattern config.

Usage:
    python synthesis_config.py config.json [--validate-only] [--output plan.json]

Output:
    JSON with validated config, topological order, and generation plan.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.

import argparse
import json
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any, Optional

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


# ──────────────────────────────────────────────────────────────
# Strategy Definitions
# ──────────────────────────────────────────────────────────────

STRATEGIES = {
    "llm_text": {
        "required": ["name", "strategy"],
        "optional": ["depends_on", "agent_yaml", "few_shot_examples", "target_rows",
                      "model", "sentinel_patterns", "description"],
        "description": "LLM generates plain text output per row",
    },
    "llm_structured": {
        "required": ["name", "strategy", "output_columns"],
        "optional": ["depends_on", "agent_yaml", "few_shot_examples", "target_rows",
                      "model", "output_schema", "description"],
        "description": "LLM extracts/generates structured data into multiple columns",
    },
    "statistical_sample": {
        "required": ["name", "strategy", "source_column"],
        "optional": ["depends_on", "distribution", "seed", "description"],
        "description": "Sample values from existing column distribution",
    },
    "expression": {
        "required": ["name", "strategy", "expr"],
        "optional": ["depends_on", "description"],
        "description": "Evaluate a Python expression per row",
    },
    "reference_lookup": {
        "required": ["name", "strategy", "reference_path", "join_key"],
        "optional": ["depends_on", "enrich_columns", "match_type", "description"],
        "description": "Look up values from a reference dataset",
    },
}


# ──────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────

def validate_column_config(col_config: dict, index: int) -> list[dict]:
    """
    Validate a single column config entry.

    Returns list of validation errors (empty if valid).
    """
    errors = []

    if not isinstance(col_config, dict):
        return [{"column_index": index, "error": "Column config must be a dict"}]

    # Check required 'name' field
    if "name" not in col_config:
        errors.append({
            "column_index": index,
            "field": "name",
            "error": "Missing required field 'name'",
        })

    # Check required 'strategy' field
    strategy = col_config.get("strategy")
    if not strategy:
        errors.append({
            "column_index": index,
            "column": col_config.get("name", f"column_{index}"),
            "field": "strategy",
            "error": "Missing required field 'strategy'",
        })
        return errors

    # Check strategy is known
    if strategy not in STRATEGIES:
        errors.append({
            "column_index": index,
            "column": col_config.get("name", f"column_{index}"),
            "field": "strategy",
            "error": f"Unknown strategy '{strategy}'. Valid: {list(STRATEGIES.keys())}",
        })
        return errors

    # Check strategy-specific required fields
    strategy_def = STRATEGIES[strategy]
    for field in strategy_def["required"]:
        if field not in col_config:
            errors.append({
                "column_index": index,
                "column": col_config.get("name", f"column_{index}"),
                "field": field,
                "error": f"Missing required field '{field}' for strategy '{strategy}'",
            })

    # Validate depends_on is a list
    depends_on = col_config.get("depends_on")
    if depends_on is not None and not isinstance(depends_on, list):
        errors.append({
            "column_index": index,
            "column": col_config.get("name", f"column_{index}"),
            "field": "depends_on",
            "error": "'depends_on' must be a list of column names",
        })

    return errors


def validate_yaml_paths(config: dict, base_dir: Optional[str] = None) -> list[dict]:
    """
    Validate that YAML agent config paths in the config exist.

    Args:
        config: Full synthesis config
        base_dir: Base directory for resolving relative paths

    Returns:
        List of validation errors
    """
    errors = []
    base = Path(base_dir) if base_dir else Path.cwd()

    for col in config.get("columns", []):
        yaml_path = col.get("agent_yaml")
        if yaml_path:
            resolved = base / yaml_path
            if not resolved.exists():
                errors.append({
                    "column": col.get("name"),
                    "field": "agent_yaml",
                    "error": f"YAML agent config not found: {yaml_path}",
                    "resolved_path": str(resolved),
                })
            else:
                # Try to parse it
                try:
                    import yaml
                    with open(resolved) as f:
                        yaml.safe_load(f)
                except Exception as e:
                    errors.append({
                        "column": col.get("name"),
                        "field": "agent_yaml",
                        "error": f"YAML parse error: {e}",
                    })

    return errors


def validate_config(config: dict, base_dir: Optional[str] = None) -> dict:
    """
    Validate a full synthesis configuration.

    Args:
        config: Synthesis config dict
        base_dir: Base directory for resolving relative paths

    Returns:
        Dict with: valid (bool), errors (list), warnings (list)
    """
    errors = []
    warnings = []

    # Check top-level structure
    if not isinstance(config, dict):
        return {"valid": False, "errors": [{"error": "Config must be a dict"}], "warnings": []}

    if "columns" not in config:
        errors.append({"field": "columns", "error": "Missing required field 'columns'"})
        return {"valid": False, "errors": errors, "warnings": warnings}

    if not isinstance(config["columns"], list):
        errors.append({"field": "columns", "error": "'columns' must be a list"})
        return {"valid": False, "errors": errors, "warnings": warnings}

    if len(config["columns"]) == 0:
        errors.append({"field": "columns", "error": "'columns' list is empty"})
        return {"valid": False, "errors": errors, "warnings": warnings}

    # Validate each column
    column_names = set()
    for i, col in enumerate(config["columns"]):
        col_errors = validate_column_config(col, i)
        errors.extend(col_errors)

        name = col.get("name")
        if name:
            if name in column_names:
                errors.append({
                    "column_index": i,
                    "column": name,
                    "error": f"Duplicate column name '{name}'",
                })
            column_names.add(name)

    # Validate dependencies reference existing columns
    for col in config["columns"]:
        for dep in col.get("depends_on", []):
            if dep not in column_names:
                # Dependency on an existing dataset column (not generated) is OK — just warn
                warnings.append({
                    "column": col.get("name"),
                    "dependency": dep,
                    "warning": f"Dependency '{dep}' not in columns list — assumed to exist in source data",
                })

    # Check for circular dependencies
    cycle = detect_circular_dependencies(config)
    if cycle:
        errors.append({
            "error": "Circular dependency detected",
            "cycle": cycle,
        })

    # Validate YAML paths
    yaml_errors = validate_yaml_paths(config, base_dir)
    errors.extend(yaml_errors)

    # Validate sentinel_patterns
    sentinel_patterns = config.get("sentinel_patterns")
    if sentinel_patterns is not None and not isinstance(sentinel_patterns, list):
        errors.append({"field": "sentinel_patterns", "error": "'sentinel_patterns' must be a list"})

    # Validate output_schema
    output_schema = config.get("output_schema")
    if output_schema is not None and not isinstance(output_schema, dict):
        errors.append({"field": "output_schema", "error": "'output_schema' must be a dict"})

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


# ──────────────────────────────────────────────────────────────
# Dependency Graph (Kahn's Algorithm)
# ──────────────────────────────────────────────────────────────

def build_dependency_graph(config: dict) -> tuple[dict[str, list[str]], dict[str, int]]:
    """
    Build adjacency list and in-degree map from config dependencies.

    Args:
        config: Synthesis config with columns and depends_on

    Returns:
        (adjacency_list, in_degree): Maps of column -> [dependents] and column -> in_degree
    """
    columns = {col["name"] for col in config["columns"]}
    adjacency: dict[str, list[str]] = {name: [] for name in columns}
    in_degree: dict[str, int] = {name: 0 for name in columns}

    for col in config["columns"]:
        name = col["name"]
        for dep in col.get("depends_on", []):
            if dep in columns:
                adjacency[dep].append(name)
                in_degree[name] += 1

    return adjacency, in_degree


def topological_sort(config: dict) -> list[str]:
    """
    Compute topological order of columns using Kahn's algorithm.

    Args:
        config: Synthesis config with columns and depends_on

    Returns:
        List of column names in generation order

    Raises:
        ValueError: If circular dependency detected
    """
    adjacency, in_degree = build_dependency_graph(config)

    # Start with columns that have no dependencies
    queue = deque([name for name, deg in in_degree.items() if deg == 0])
    order = []

    while queue:
        current = queue.popleft()
        order.append(current)

        for dependent in adjacency.get(current, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(in_degree):
        remaining = set(in_degree.keys()) - set(order)
        raise ValueError(f"Circular dependency detected among columns: {remaining}")

    return order


def detect_circular_dependencies(config: dict) -> Optional[list[str]]:
    """
    Detect circular dependencies in the config.

    Returns:
        List of column names involved in the cycle, or None if no cycle.
    """
    try:
        topological_sort(config)
        return None
    except ValueError:
        # Find the actual cycle
        adjacency, in_degree = build_dependency_graph(config)
        remaining = {name for name, deg in in_degree.items() if deg > 0}

        # Simple cycle extraction: follow dependencies from remaining nodes
        if remaining:
            return sorted(remaining)
        return None


# ──────────────────────────────────────────────────────────────
# Generation Plan
# ──────────────────────────────────────────────────────────────

def build_generation_plan(config: dict) -> dict:
    """
    Build a complete generation plan from a validated config.

    Returns:
        Dict with: column_order, columns (with resolved config), sentinel_patterns, output_schema
    """
    column_order = topological_sort(config)

    # Build column map
    column_map = {col["name"]: col for col in config["columns"]}

    # Build plan entries
    plan_columns = []
    for name in column_order:
        col = column_map[name]
        entry = {
            "name": name,
            "strategy": col["strategy"],
            "depends_on": col.get("depends_on", []),
        }

        # Copy strategy-specific fields
        for key, value in col.items():
            if key not in ("name", "strategy", "depends_on"):
                entry[key] = value

        plan_columns.append(entry)

    return {
        "column_order": column_order,
        "columns": plan_columns,
        "sentinel_patterns": config.get("sentinel_patterns"),
        "output_schema": config.get("output_schema"),
        "total_columns": len(column_order),
    }


# ──────────────────────────────────────────────────────────────
# Config Loading
# ──────────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    """
    Load synthesis config from a JSON file.

    Args:
        config_path: Path to JSON config file

    Returns:
        Parsed config dict

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config is not valid JSON
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        return json.load(f)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Validate synthesis config and generate execution plan"
    )
    parser.add_argument("config", help="Path to JSON synthesis config")
    parser.add_argument("--validate-only", action="store_true",
                        help="Only validate, don't generate plan")
    parser.add_argument("--output", "-o", help="Write plan to output file")
    parser.add_argument("--base-dir", help="Base directory for resolving relative paths")

    args = parser.parse_args()

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        output_result(format_error(str(e)))
    except json.JSONDecodeError as e:
        output_result(format_error(f"Invalid JSON: {e}"))

    # Validate
    base_dir = args.base_dir or str(Path(args.config).parent)
    validation = validate_config(config, base_dir=base_dir)

    if not validation["valid"]:
        result = {
            "success": False,
            "error": "Config validation failed",
            "validation_errors": validation["errors"],
            "warnings": validation["warnings"],
        }
        output_result(result)

    if args.validate_only:
        result = {
            "success": True,
            "message": "Config is valid",
            "warnings": validation["warnings"],
            "column_count": len(config.get("columns", [])),
        }
        output_result(result)

    # Build generation plan
    try:
        plan = build_generation_plan(config)
    except ValueError as e:
        output_result(format_error(f"Dependency resolution failed: {e}"))

    result = {
        "success": True,
        "plan": plan,
        "warnings": validation["warnings"],
    }

    # Write output if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        result["output_path"] = str(output_path)

    output_result(result)


if __name__ == "__main__":
    main()
