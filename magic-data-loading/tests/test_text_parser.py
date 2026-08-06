#!/usr/bin/env python3
"""Unit tests for skills/magic-data-loading/scripts/text_parser.py."""

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest

SCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "text_parser.py"
)


class TestTextParser:
    """Tests for text_parser.py script."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_jsonl(self, filename, records):
        """Write a list of dicts as JSONL."""
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return path

    def _read_output_csv(self, path):
        """Read the output CSV and return list of dicts."""
        rows = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        return rows, reader.fieldnames

    def run_script(self, *args):
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True, text=True, timeout=30
        )
        return result

    def test_tag_value_structured_format(self):
        """Parse structured tag-value format with tag-value template."""
        entry_text = """憲章:hin3 zoeng1 (pos:名詞)
<explanation>
yue:一個國家或者地區最大嘅法律文件
eng:constitution; charter
<eg>
yue:聯合國憲章
eng:Charter of the United Nations
----
<explanation>
yue:second definition
eng:second definition english"""

        records = [{"text": entry_text}]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(input_path, output_path, "--template", "tag-value")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_in"] == 1
        assert result["rows_out"] == 1
        assert result["rows_parsed"] == 1

        # Read the output CSV and verify columns
        rows, fieldnames = self._read_output_csv(output_path)
        assert len(rows) == 1
        row = rows[0]

        assert row["word"] == "憲章"
        assert row["pronunciation"] == "hin3 zoeng1"
        assert row["pos"] == "名詞"
        assert "一個國家" in row["definitions_yue"]
        assert "constitution" in row["definitions_eng"]
        assert "聯合國憲章" in row["examples_yue"]
        # Multiple definitions joined by ||
        assert "second definition" in row["definitions_yue"]

    def test_key_value_template(self):
        """Parse simple key:value pairs using key-value template."""
        entry_text = """name: Alice
age: 30
city: Hong Kong"""

        records = [{"text": entry_text}]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(input_path, output_path, "--template", "key-value")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_parsed"] == 1

        rows, fieldnames = self._read_output_csv(output_path)
        assert len(rows) == 1
        row = rows[0]

        assert row["name"] == "Alice"
        assert row["age"] == "30"
        assert row["city"] == "Hong Kong"

    def test_delimited_template(self):
        """Parse text with ---- separators using delimited template."""
        entry_text = """First section content here.
Some more text in the first section.
----
Second section content here.
----
Third section content here."""

        records = [{"text": entry_text}]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(input_path, output_path, "--template", "delimited")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_parsed"] == 1

        rows, fieldnames = self._read_output_csv(output_path)
        assert len(rows) == 1
        row = rows[0]

        assert "section_1" in row
        assert "section_2" in row
        assert "section_3" in row
        assert "First section" in row["section_1"]
        assert "Second section" in row["section_2"]
        assert "Third section" in row["section_3"]

    def test_preserve_fields(self):
        """The --preserve-fields flag should carry over specified fields from input."""
        entry_text = """name: Alice
role: engineer"""

        records = [
            {"id": "rec_001", "text": entry_text, "metadata": {"source": "wiki"}},
        ]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(
            input_path, output_path,
            "--template", "key-value",
            "--preserve-fields", "id,metadata.source",
        )
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        rows, fieldnames = self._read_output_csv(output_path)
        assert len(rows) == 1
        row = rows[0]

        # Preserved fields should be present (dot notation flattened with underscore)
        assert row["id"] == "rec_001"
        assert row["metadata_source"] == "wiki"
        # Parsed fields should also be present
        assert row["name"] == "Alice"
        assert row["role"] == "engineer"

    def test_multiple_records(self):
        """Multiple input records should each be parsed independently."""
        records = [
            {"text": "name: Alice\nage: 25"},
            {"text": "name: Bob\nage: 30"},
            {"text": "name: Charlie\nage: 35"},
        ]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(input_path, output_path, "--template", "key-value")
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_in"] == 3
        assert result["rows_out"] == 3
        assert result["rows_parsed"] == 3
        assert result["parse_success_rate"] == 100.0

        rows, _ = self._read_output_csv(output_path)
        assert len(rows) == 3
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"
        assert rows[2]["name"] == "Charlie"

    def test_csv_input_format(self):
        """The parser should also accept CSV input files."""
        csv_path = os.path.join(self.tmpdir, "input.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "text"])
            writer.writerow(["1", "color: red\nsize: large"])
            writer.writerow(["2", "color: blue\nsize: small"])

        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(
            csv_path, output_path,
            "--template", "key-value",
            "--preserve-fields", "id",
        )
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True
        assert result["rows_in"] == 2

        rows, _ = self._read_output_csv(output_path)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["color"] == "red"

    def test_custom_separator(self):
        """The --separator flag should change how multi-values are joined."""
        entry_text = """key: value1
key: value2
key: value3"""

        records = [{"text": entry_text}]
        input_path = self._make_jsonl("input.jsonl", records)
        output_path = os.path.join(self.tmpdir, "output.csv")

        proc = self.run_script(
            input_path, output_path,
            "--template", "key-value",
            "--separator", " | ",
        )
        result = json.loads(proc.stdout)

        assert proc.returncode == 0
        assert result["success"] is True

        rows, _ = self._read_output_csv(output_path)
        # Multiple values for 'key' should be joined with " | "
        assert rows[0]["key"] == "value1 | value2 | value3"
