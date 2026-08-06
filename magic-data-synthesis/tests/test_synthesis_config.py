#!/usr/bin/env python3
"""
Unit tests for skills/magic-data-synthesis/scripts/synthesis_config.py.

Covers:
- validate_column_config()   — valid config, missing fields, unknown/valid strategies,
                               strategy-specific required fields, depends_on type check
- validate_config()          — top-level structure, duplicates, dependency warnings,
                               circular dependency, sentinel_patterns, output_schema
- validate_yaml_paths()      — existing path passes, missing path fails, bad YAML fails
- topological_sort()         — linear chain, diamond, independent columns, circular raises
- detect_circular_dependencies() — no cycle returns None, simple cycle, complex cycle
- build_generation_plan()    — column_order, strategy fields preserved, top-level keys
- load_config()              — valid JSON, missing file, invalid JSON
"""

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — allow direct imports without package installation
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from synthesis_config import (
    STRATEGIES,
    build_generation_plan,
    detect_circular_dependencies,
    load_config,
    topological_sort,
    validate_column_config,
    validate_config,
    validate_yaml_paths,
)


# ===========================================================================
# Helpers
# ===========================================================================

def _col(name, strategy, **kwargs):
    """Return a minimal column config dict."""
    base = {"name": name, "strategy": strategy}
    base.update(kwargs)
    return base


def _config(*columns, **top_level):
    """Return a minimal synthesis config dict."""
    cfg = {"columns": list(columns)}
    cfg.update(top_level)
    return cfg


# ===========================================================================
# Tests: validate_column_config()
# ===========================================================================

class TestValidateColumnConfig:
    """Tests for validate_column_config(index, col_config)."""

    # --- valid configs -------------------------------------------------------

    def test_valid_llm_text(self):
        col = _col("my_text", "llm_text")
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_valid_llm_structured(self):
        col = _col("parsed", "llm_structured", output_columns=["a", "b"])
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_valid_statistical_sample(self):
        col = _col("sampled", "statistical_sample", source_column="age")
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_valid_expression(self):
        col = _col("derived", "expression", expr="row['a'] + row['b']")
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_valid_reference_lookup(self):
        col = _col("enriched", "reference_lookup",
                   reference_path="ref.csv", join_key="id")
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_optional_fields_do_not_cause_errors(self):
        col = _col("my_text", "llm_text",
                   depends_on=["col_a"],
                   agent_yaml="agent.yaml",
                   description="Some description")
        errors = validate_column_config(col, 0)
        assert errors == []

    # --- missing name --------------------------------------------------------

    def test_missing_name_returns_error(self):
        col = {"strategy": "llm_text"}
        errors = validate_column_config(col, 0)
        field_errors = [e["field"] for e in errors]
        assert "name" in field_errors

    def test_missing_name_error_contains_index(self):
        col = {"strategy": "llm_text"}
        errors = validate_column_config(col, 3)
        assert any(e.get("column_index") == 3 for e in errors)

    # --- missing strategy ----------------------------------------------------

    def test_missing_strategy_returns_error(self):
        col = {"name": "col_a"}
        errors = validate_column_config(col, 0)
        field_errors = [e["field"] for e in errors]
        assert "strategy" in field_errors

    def test_missing_strategy_returns_early(self):
        """When strategy is absent the validator should return without checking
        strategy-specific required fields (no spurious extra errors)."""
        col = {"name": "col_a"}
        errors = validate_column_config(col, 0)
        # Only the strategy error should be present, not errors about
        # strategy-specific required fields (which are unknown without strategy).
        strategy_errors = [e for e in errors if e.get("field") == "strategy"]
        assert len(strategy_errors) == 1

    # --- unknown strategy ----------------------------------------------------

    def test_unknown_strategy_returns_error(self):
        col = _col("col_a", "magic_generator")
        errors = validate_column_config(col, 0)
        assert len(errors) == 1
        assert "magic_generator" in errors[0]["error"]

    def test_unknown_strategy_lists_valid_options(self):
        col = _col("col_a", "not_a_strategy")
        errors = validate_column_config(col, 0)
        error_text = errors[0]["error"]
        for valid_name in STRATEGIES:
            assert valid_name in error_text

    # --- strategy-specific required fields -----------------------------------

    def test_llm_structured_requires_output_columns(self):
        col = _col("parsed", "llm_structured")  # missing output_columns
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "output_columns" in fields

    def test_reference_lookup_requires_reference_path(self):
        col = _col("enriched", "reference_lookup", join_key="id")
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "reference_path" in fields

    def test_reference_lookup_requires_join_key(self):
        col = _col("enriched", "reference_lookup", reference_path="ref.csv")
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "join_key" in fields

    def test_expression_requires_expr(self):
        col = _col("derived", "expression")
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "expr" in fields

    def test_statistical_sample_requires_source_column(self):
        col = _col("sampled", "statistical_sample")
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "source_column" in fields

    def test_llm_text_has_no_extra_required_fields(self):
        """llm_text only requires name + strategy, nothing else."""
        col = _col("my_text", "llm_text")
        errors = validate_column_config(col, 0)
        assert errors == []

    # --- depends_on must be list ---------------------------------------------

    def test_depends_on_as_string_returns_error(self):
        col = _col("col_b", "llm_text", depends_on="col_a")
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "depends_on" in fields

    def test_depends_on_as_dict_returns_error(self):
        col = _col("col_b", "llm_text", depends_on={"col": "col_a"})
        errors = validate_column_config(col, 0)
        fields = [e["field"] for e in errors]
        assert "depends_on" in fields

    def test_depends_on_as_list_is_valid(self):
        col = _col("col_b", "llm_text", depends_on=["col_a"])
        errors = validate_column_config(col, 0)
        assert errors == []

    def test_depends_on_empty_list_is_valid(self):
        col = _col("col_b", "llm_text", depends_on=[])
        errors = validate_column_config(col, 0)
        assert errors == []

    # --- non-dict input -------------------------------------------------------

    def test_non_dict_column_config_returns_single_error(self):
        errors = validate_column_config("not a dict", 2)
        assert len(errors) == 1
        assert errors[0].get("column_index") == 2


# ===========================================================================
# Tests: validate_config()
# ===========================================================================

class TestValidateConfig:
    """Tests for validate_config(config, base_dir)."""

    # --- valid full config ---------------------------------------------------

    def test_valid_full_config_is_valid(self):
        cfg = _config(
            _col("name", "llm_text"),
            _col("age", "statistical_sample", source_column="age_raw"),
        )
        result = validate_config(cfg)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_valid_config_returns_expected_keys(self):
        cfg = _config(_col("col", "llm_text"))
        result = validate_config(cfg)
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result

    # --- missing 'columns' key -----------------------------------------------

    def test_missing_columns_key_is_invalid(self):
        result = validate_config({"output_schema": {}})
        assert result["valid"] is False
        fields = [e.get("field") for e in result["errors"]]
        assert "columns" in fields

    # --- empty columns list --------------------------------------------------

    def test_empty_columns_list_is_invalid(self):
        result = validate_config({"columns": []})
        assert result["valid"] is False
        assert any("empty" in e["error"].lower() for e in result["errors"])

    # --- duplicate column names ----------------------------------------------

    def test_duplicate_column_names_are_invalid(self):
        cfg = _config(
            _col("col_a", "llm_text"),
            _col("col_a", "llm_text"),
        )
        result = validate_config(cfg)
        assert result["valid"] is False
        assert any("Duplicate" in e.get("error", "") for e in result["errors"])

    def test_unique_column_names_are_valid(self):
        cfg = _config(
            _col("col_a", "llm_text"),
            _col("col_b", "llm_text"),
        )
        result = validate_config(cfg)
        assert result["valid"] is True

    # --- dependency on non-existent column (warning, not error) --------------

    def test_dependency_on_nonexistent_column_produces_warning(self):
        cfg = _config(
            _col("col_b", "llm_text", depends_on=["source_col_not_generated"]),
        )
        result = validate_config(cfg)
        # Should be a WARNING, not an error — external source columns are allowed
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert any("source_col_not_generated" in w.get("dependency", "")
                   for w in result["warnings"])

    # --- circular dependency detection ----------------------------------------

    def test_circular_dependency_is_invalid(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["B"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        result = validate_config(cfg)
        assert result["valid"] is False
        assert any("Circular" in e.get("error", "") for e in result["errors"])

    def test_three_way_circular_dependency_is_invalid(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["C"]),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["B"]),
        )
        result = validate_config(cfg)
        assert result["valid"] is False
        assert any("Circular" in e.get("error", "") for e in result["errors"])

    # --- sentinel_patterns ---------------------------------------------------

    def test_sentinel_patterns_as_list_is_valid(self):
        cfg = _config(
            _col("col", "llm_text"),
            sentinel_patterns=["TODO", "N/A"],
        )
        result = validate_config(cfg)
        assert result["valid"] is True

    def test_sentinel_patterns_not_a_list_is_invalid(self):
        cfg = _config(
            _col("col", "llm_text"),
            sentinel_patterns="TODO",
        )
        result = validate_config(cfg)
        assert result["valid"] is False
        fields = [e.get("field") for e in result["errors"]]
        assert "sentinel_patterns" in fields

    def test_sentinel_patterns_absent_is_valid(self):
        cfg = _config(_col("col", "llm_text"))
        result = validate_config(cfg)
        assert result["valid"] is True

    # --- output_schema -------------------------------------------------------

    def test_output_schema_as_dict_is_valid(self):
        cfg = _config(
            _col("col", "llm_text"),
            output_schema={"col": "string"},
        )
        result = validate_config(cfg)
        assert result["valid"] is True

    def test_output_schema_not_a_dict_is_invalid(self):
        cfg = _config(
            _col("col", "llm_text"),
            output_schema=["col", "string"],
        )
        result = validate_config(cfg)
        assert result["valid"] is False
        fields = [e.get("field") for e in result["errors"]]
        assert "output_schema" in fields

    def test_output_schema_absent_is_valid(self):
        cfg = _config(_col("col", "llm_text"))
        result = validate_config(cfg)
        assert result["valid"] is True


# ===========================================================================
# Tests: validate_yaml_paths()
# ===========================================================================

class TestValidateYamlPaths:
    """Tests for validate_yaml_paths(config, base_dir)."""

    def test_existing_valid_yaml_passes(self, tmp_path):
        yaml_file = tmp_path / "agent.yaml"
        yaml_file.write_text("system_prompt: Hello\n")
        cfg = _config(_col("col", "llm_text", agent_yaml="agent.yaml"))
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert errors == []

    def test_missing_yaml_path_fails(self, tmp_path):
        cfg = _config(_col("col", "llm_text", agent_yaml="nonexistent.yaml"))
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert len(errors) == 1
        assert "nonexistent.yaml" in errors[0]["error"]

    def test_missing_yaml_error_includes_column_name(self, tmp_path):
        cfg = _config(_col("my_col", "llm_text", agent_yaml="missing.yaml"))
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert errors[0]["column"] == "my_col"

    def test_invalid_yaml_content_fails(self, tmp_path):
        bad_yaml = tmp_path / "bad.yaml"
        # Write content that is syntactically invalid YAML (tab-indented mapping)
        bad_yaml.write_text("key: [\nunclosed bracket\n")
        cfg = _config(_col("col", "llm_text", agent_yaml="bad.yaml"))
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert len(errors) == 1
        assert "YAML parse error" in errors[0]["error"]

    def test_no_agent_yaml_field_produces_no_errors(self, tmp_path):
        cfg = _config(_col("col", "llm_text"))
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert errors == []

    def test_multiple_columns_multiple_yaml_errors(self, tmp_path):
        cfg = _config(
            _col("col_a", "llm_text", agent_yaml="missing_a.yaml"),
            _col("col_b", "llm_text", agent_yaml="missing_b.yaml"),
        )
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert len(errors) == 2

    def test_mixed_existing_and_missing_yaml(self, tmp_path):
        good_yaml = tmp_path / "good.yaml"
        good_yaml.write_text("system_prompt: ok\n")
        cfg = _config(
            _col("col_a", "llm_text", agent_yaml="good.yaml"),
            _col("col_b", "llm_text", agent_yaml="bad.yaml"),
        )
        errors = validate_yaml_paths(cfg, base_dir=str(tmp_path))
        assert len(errors) == 1
        assert errors[0]["column"] == "col_b"


# ===========================================================================
# Tests: topological_sort()
# ===========================================================================

class TestTopologicalSort:
    """Tests for topological_sort(config)."""

    def test_linear_chain_a_b_c(self):
        """A -> B -> C should produce [A, B, C] order."""
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["B"]),
        )
        order = topological_sort(cfg)
        assert order.index("A") < order.index("B")
        assert order.index("B") < order.index("C")

    def test_diamond_dependency(self):
        """
        A -> B -> D
        A -> C -> D
        D must come last, A must come first.
        """
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["A"]),
            _col("D", "llm_text", depends_on=["B", "C"]),
        )
        order = topological_sort(cfg)
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("D")
        assert order.index("C") < order.index("D")

    def test_independent_columns_all_present(self):
        """Columns with no dependencies can appear in any order but all must be present."""
        cfg = _config(
            _col("X", "llm_text"),
            _col("Y", "llm_text"),
            _col("Z", "llm_text"),
        )
        order = topological_sort(cfg)
        assert set(order) == {"X", "Y", "Z"}
        assert len(order) == 3

    def test_single_column(self):
        cfg = _config(_col("solo", "llm_text"))
        order = topological_sort(cfg)
        assert order == ["solo"]

    def test_circular_dependency_raises_value_error(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["B"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        with pytest.raises(ValueError, match="[Cc]ircular"):
            topological_sort(cfg)

    def test_three_node_cycle_raises_value_error(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["C"]),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["B"]),
        )
        with pytest.raises(ValueError):
            topological_sort(cfg)

    def test_order_length_equals_column_count(self):
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "statistical_sample", source_column="raw", depends_on=["A"]),
        )
        order = topological_sort(cfg)
        assert len(order) == 3

    def test_external_dependency_not_in_columns_is_ignored(self):
        """depends_on entries not in the columns list are ignored for sorting."""
        cfg = _config(
            _col("A", "llm_text", depends_on=["external_source"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        order = topological_sort(cfg)
        assert order.index("A") < order.index("B")


# ===========================================================================
# Tests: detect_circular_dependencies()
# ===========================================================================

class TestDetectCircularDependencies:
    """Tests for detect_circular_dependencies(config)."""

    def test_no_cycle_returns_none(self):
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
        )
        assert detect_circular_dependencies(cfg) is None

    def test_simple_two_node_cycle_returns_involved_columns(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["B"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        cycle = detect_circular_dependencies(cfg)
        assert cycle is not None
        assert "A" in cycle
        assert "B" in cycle

    def test_three_node_cycle_returns_all_involved(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["C"]),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["B"]),
        )
        cycle = detect_circular_dependencies(cfg)
        assert cycle is not None
        assert set(cycle) == {"A", "B", "C"}

    def test_no_cycle_with_independent_columns(self):
        cfg = _config(
            _col("X", "llm_text"),
            _col("Y", "llm_text"),
        )
        assert detect_circular_dependencies(cfg) is None

    def test_partial_cycle_only_returns_cycle_nodes(self):
        """Only nodes involved in the cycle should be returned, not free nodes."""
        cfg = _config(
            _col("free", "llm_text"),
            _col("A", "llm_text", depends_on=["B"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        cycle = detect_circular_dependencies(cfg)
        assert cycle is not None
        assert "free" not in cycle

    def test_complex_dag_returns_none(self):
        """A valid DAG with several edges should not be flagged as cyclic."""
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["A"]),
            _col("D", "llm_text", depends_on=["B", "C"]),
            _col("E", "llm_text", depends_on=["D"]),
        )
        assert detect_circular_dependencies(cfg) is None


# ===========================================================================
# Tests: build_generation_plan()
# ===========================================================================

class TestBuildGenerationPlan:
    """Tests for build_generation_plan(config)."""

    def test_correct_column_order_linear_chain(self):
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
            _col("C", "llm_text", depends_on=["B"]),
        )
        plan = build_generation_plan(cfg)
        order = plan["column_order"]
        assert order.index("A") < order.index("B")
        assert order.index("B") < order.index("C")

    def test_plan_contains_all_columns(self):
        cfg = _config(
            _col("X", "llm_text"),
            _col("Y", "statistical_sample", source_column="X"),
        )
        plan = build_generation_plan(cfg)
        assert len(plan["columns"]) == 2
        names = {c["name"] for c in plan["columns"]}
        assert names == {"X", "Y"}

    def test_strategy_specific_fields_preserved(self):
        cfg = _config(
            _col("parsed", "llm_structured",
                 output_columns=["first", "last"],
                 description="Split name"),
        )
        plan = build_generation_plan(cfg)
        col_entry = plan["columns"][0]
        assert col_entry["output_columns"] == ["first", "last"]
        assert col_entry["description"] == "Split name"

    def test_expression_expr_field_preserved(self):
        expr_str = "row['a'] * 2"
        cfg = _config(_col("doubled", "expression", expr=expr_str))
        plan = build_generation_plan(cfg)
        assert plan["columns"][0]["expr"] == expr_str

    def test_reference_lookup_fields_preserved(self):
        cfg = _config(
            _col("enriched", "reference_lookup",
                 reference_path="lookup.csv",
                 join_key="id",
                 enrich_columns=["city", "country"]),
        )
        plan = build_generation_plan(cfg)
        col_entry = plan["columns"][0]
        assert col_entry["reference_path"] == "lookup.csv"
        assert col_entry["join_key"] == "id"
        assert col_entry["enrich_columns"] == ["city", "country"]

    def test_sentinel_patterns_included(self):
        cfg = _config(
            _col("col", "llm_text"),
            sentinel_patterns=["TODO", "N/A", "???"],
        )
        plan = build_generation_plan(cfg)
        assert plan["sentinel_patterns"] == ["TODO", "N/A", "???"]

    def test_output_schema_included(self):
        schema = {"col": "string", "age": "integer"}
        cfg = _config(
            _col("col", "llm_text"),
            output_schema=schema,
        )
        plan = build_generation_plan(cfg)
        assert plan["output_schema"] == schema

    def test_sentinel_patterns_none_when_absent(self):
        cfg = _config(_col("col", "llm_text"))
        plan = build_generation_plan(cfg)
        assert plan["sentinel_patterns"] is None

    def test_output_schema_none_when_absent(self):
        cfg = _config(_col("col", "llm_text"))
        plan = build_generation_plan(cfg)
        assert plan["output_schema"] is None

    def test_total_columns_count(self):
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text"),
            _col("C", "llm_text"),
        )
        plan = build_generation_plan(cfg)
        assert plan["total_columns"] == 3

    def test_plan_columns_contain_depends_on(self):
        cfg = _config(
            _col("A", "llm_text"),
            _col("B", "llm_text", depends_on=["A"]),
        )
        plan = build_generation_plan(cfg)
        b_entry = next(c for c in plan["columns"] if c["name"] == "B")
        assert b_entry["depends_on"] == ["A"]

    def test_plan_columns_without_depends_on_default_to_empty_list(self):
        cfg = _config(_col("A", "llm_text"))
        plan = build_generation_plan(cfg)
        a_entry = plan["columns"][0]
        assert a_entry["depends_on"] == []

    def test_circular_dependency_raises_in_plan(self):
        cfg = _config(
            _col("A", "llm_text", depends_on=["B"]),
            _col("B", "llm_text", depends_on=["A"]),
        )
        with pytest.raises(ValueError):
            build_generation_plan(cfg)


# ===========================================================================
# Tests: load_config()
# ===========================================================================

class TestLoadConfig:
    """Tests for load_config(config_path)."""

    def test_valid_json_loads_correctly(self, tmp_path):
        cfg_data = {
            "columns": [
                {"name": "col_a", "strategy": "llm_text"}
            ]
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(cfg_data))
        loaded = load_config(str(config_file))
        assert loaded == cfg_data

    def test_complex_valid_json_round_trips(self, tmp_path):
        cfg_data = {
            "columns": [
                {"name": "text_col", "strategy": "llm_text", "depends_on": []},
                {"name": "struct_col", "strategy": "llm_structured",
                 "output_columns": ["a", "b"], "depends_on": ["text_col"]},
            ],
            "sentinel_patterns": ["TODO"],
            "output_schema": {"text_col": "string"},
        }
        config_file = tmp_path / "complex.json"
        config_file.write_text(json.dumps(cfg_data))
        loaded = load_config(str(config_file))
        assert loaded == cfg_data

    def test_missing_file_raises_file_not_found_error(self, tmp_path):
        missing = tmp_path / "does_not_exist.json"
        with pytest.raises(FileNotFoundError):
            load_config(str(missing))

    def test_invalid_json_raises_json_decode_error(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{not valid json >>>")
        with pytest.raises(json.JSONDecodeError):
            load_config(str(bad_json))

    def test_empty_json_object_loads(self, tmp_path):
        config_file = tmp_path / "empty.json"
        config_file.write_text("{}")
        loaded = load_config(str(config_file))
        assert loaded == {}

    def test_json_array_at_root_loads(self, tmp_path):
        config_file = tmp_path / "array.json"
        config_file.write_text("[]")
        loaded = load_config(str(config_file))
        assert loaded == []
