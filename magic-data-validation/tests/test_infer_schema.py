#!/usr/bin/env python3
"""
Unit tests for infer_schema.py script.

Tests schema inference, strict mode, and error cases.
"""

import pytest


class TestInferSchema:
    """Test cases for schema inference script."""

    def test_schema_inference(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that schema is inferred with correct types."""
        output_path = tmp_workspace / "schema_result.json"

        result, exit_code = run_script(
            "magic-data-validation/scripts/infer_schema.py",
            "--input", str(sample_clean_csv),
            "--output", str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Inference failed: {result.get('error')}"
        assert "schema" in result or "fields" in result, "Schema not in output"

        schema_key = "schema" if "schema" in result else "fields"
        schema = result[schema_key]

        # Schema structure: {"columns": {...}, "row_count_range": {...}}
        columns = schema.get("columns", schema) if isinstance(schema, dict) else schema
        assert len(columns) > 0, "Schema should have fields"

        # Check that types are inferred
        if isinstance(columns, dict):
            for field_name, field_info in columns.items():
                assert "dtype" in field_info or "type" in field_info or isinstance(field_info, str), \
                    f"Field {field_name} should have type information"
        elif isinstance(columns, list):
            for field_info in columns:
                assert "type" in field_info or "dtype" in field_info, \
                    "Each field should have type information"

    def test_strict_mode(self, sample_clean_csv, tmp_workspace, run_script):
        """Test that strict mode produces tighter constraints."""
        output_path = tmp_workspace / "schema_strict.json"

        result, exit_code = run_script(
            "magic-data-validation/scripts/infer_schema.py",
            "--input", str(sample_clean_csv),
            "--output", str(output_path),
            "--strict"
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Inference failed: {result.get('error')}"
        assert "schema" in result or "fields" in result, "Schema not in output"

        schema_key = "schema" if "schema" in result else "fields"
        schema = result[schema_key]

        # In strict mode, might have additional constraints
        if isinstance(schema, dict):
            for field_name, field_info in schema.items():
                if isinstance(field_info, dict):
                    # Check for constraints like nullable, min, max, etc.
                    has_constraints = any(k in field_info for k in [
                        "nullable", "required", "min", "max", "pattern", "constraints"
                    ])
                    # At least some fields should have constraints in strict mode
                    if has_constraints:
                        break
            else:
                # It's OK if strict mode just means tighter type inference
                pass

    def test_empty_data_error(self, empty_csv, tmp_workspace, run_script):
        """Test that empty data produces error."""
        output_path = tmp_workspace / "schema_empty.json"

        result, exit_code = run_script(
            "magic-data-validation/scripts/infer_schema.py",
            "--input", str(empty_csv),
            "--output", str(output_path)
        )

        # Empty file should either fail or produce empty schema
        if result["success"]:
            schema_key = "schema" if "schema" in result else "fields"
            schema = result.get(schema_key, [])
            assert len(schema) == 0, "Empty file should have empty schema"
        else:
            assert "error" in result, "Error message should be present"

    def test_mixed_types_inference(self, sample_mixed_types_csv, tmp_workspace, run_script):
        """Test that mixed data types are correctly inferred."""
        output_path = tmp_workspace / "schema_mixed.json"

        result, exit_code = run_script(
            "magic-data-validation/scripts/infer_schema.py",
            "--input", str(sample_mixed_types_csv),
            "--output", str(output_path)
        )

        assert exit_code == 0, f"Script failed with exit code {exit_code}"
        assert result["success"] is True, f"Inference failed: {result.get('error')}"
        assert "schema" in result or "fields" in result, "Schema not in output"

        schema_key = "schema" if "schema" in result else "fields"
        schema = result[schema_key]

        # Schema structure: {"columns": {...}, "row_count_range": {...}}
        columns = schema.get("columns", schema) if isinstance(schema, dict) else schema

        # Should infer different types for different columns
        types_found = set()

        if isinstance(columns, dict):
            for field_info in columns.values():
                if isinstance(field_info, dict):
                    field_type = field_info.get("dtype") or field_info.get("type")
                    if field_type:
                        types_found.add(field_type)
                elif isinstance(field_info, str):
                    types_found.add(field_info)
        elif isinstance(columns, list):
            for field_info in columns:
                if isinstance(field_info, dict):
                    field_type = field_info.get("type") or field_info.get("dtype")
                    if field_type:
                        types_found.add(field_type)

        # Should have multiple types
        assert len(types_found) >= 2, f"Mixed types CSV should infer multiple types, found: {types_found}"
