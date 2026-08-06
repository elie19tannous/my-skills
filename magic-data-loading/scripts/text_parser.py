#!/usr/bin/env python3
"""
Parse structured text into tabular data.

Two modes:
1. Template mode: Parse JSONL/CSV records containing text fields
   text_parser.py input.jsonl output.csv --template tag-value

2. Raw text mode: Parse raw text files with markers
   text_parser.py --input records.txt --output parsed.csv --markers "label:,value:" --field-names "label,value"
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.


import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

# Shared utilities

# Optional chardet for encoding detection
try:
    import chardet
    HAS_CHARDET = True
except ImportError:
    HAS_CHARDET = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def detect_encoding(file_path: str) -> str:
    """Detect file encoding using chardet."""
    if not HAS_CHARDET:
        return "utf-8"
    with open(file_path, "rb") as f:
        raw = f.read(10000)
    result = chardet.detect(raw)
    return result.get("encoding", "utf-8") or "utf-8"


# ── Template mode functions ──

def load_input_records(input_path):
    """Load JSONL or CSV input into list of dicts."""
    ext = os.path.splitext(input_path)[1].lower()
    records = []
    if ext in (".jsonl", ".ndjson"):
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    elif ext == ".csv":
        with open(input_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    else:
        # Try JSONL first, fall back to CSV
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            with open(input_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
    return records


def get_nested_value(record, dotted_key):
    """Get value from nested dict using dot notation. Returns None if not found."""
    keys = dotted_key.split(".")
    current = record
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current


def parse_tag_value(text, separator="||"):
    """Parse tag-value format records."""
    lines = text.strip().split("\n")
    if not lines:
        return None

    # Parse first line: word:pronunciation (pos:POS)
    first_line = lines[0].strip()
    word = ""
    pronunciation = ""
    pos = ""

    # Extract pos from parenthetical
    pos_match = re.search(r'\(pos:([^)]+)\)', first_line)
    if pos_match:
        pos = pos_match.group(1).strip()
        first_line_no_pos = first_line[:pos_match.start()].strip()
    else:
        first_line_no_pos = first_line

    # Extract word and pronunciation from "word:pronunciation"
    if ":" in first_line_no_pos:
        word, pronunciation = first_line_no_pos.split(":", 1)
        word = word.strip()
        pronunciation = pronunciation.strip()

    # Parse sections
    definitions_yue = []
    definitions_eng = []
    examples_yue = []
    examples_eng = []

    current_section = None  # "explanation" or "example"

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        if line == "<explanation>":
            current_section = "explanation"
            continue
        elif line == "<eg>":
            current_section = "example"
            continue
        elif line == "----":
            # Separator between groups — continue with same logic
            continue

        if current_section == "explanation":
            if line.startswith("yue:"):
                definitions_yue.append(line[4:].strip())
            elif line.startswith("eng:"):
                definitions_eng.append(line[4:].strip())
        elif current_section == "example":
            if line.startswith("yue:"):
                examples_yue.append(line[4:].strip())
            elif line.startswith("eng:"):
                examples_eng.append(line[4:].strip())

    return {
        "word": word,
        "pronunciation": pronunciation,
        "pos": pos,
        "definitions_yue": (
            separator.join(definitions_yue) if len(definitions_yue) > 1
            else (definitions_yue[0] if definitions_yue else "")
        ),
        "definitions_eng": (
            separator.join(definitions_eng) if len(definitions_eng) > 1
            else (definitions_eng[0] if definitions_eng else "")
        ),
        "examples_yue": (
            separator.join(examples_yue) if len(examples_yue) > 1
            else (examples_yue[0] if examples_yue else "")
        ),
        "examples_eng": (
            separator.join(examples_eng) if len(examples_eng) > 1
            else (examples_eng[0] if examples_eng else "")
        ),
    }


def parse_key_value(text, separator="||"):
    """Parse simple key:value pairs."""
    result = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key in result:
            result[key] = result[key] + separator + value
        else:
            result[key] = value
    return result if result else None


def parse_delimited(text, delimiter="----"):
    """Parse text split by delimiter into numbered sections."""
    sections = re.split(re.escape(delimiter), text)
    result = {}
    for i, section in enumerate(sections, 1):
        section = section.strip()
        if section:
            result[f"section_{i}"] = section
    return result if result else None


def template_mode(args):
    """Run template mode: parse JSONL/CSV records."""
    records = load_input_records(args.input_path)
    rows_in = len(records)
    parsed_rows = []
    rows_parsed = 0
    separator = args.separator if args.separator else "||"

    # Parse preserve fields
    preserve_fields = []
    if args.preserve_fields:
        preserve_fields = [f.strip() for f in args.preserve_fields.split(",")]

    for record in records:
        text = record.get("text", "")
        if not text:
            continue

        # Parse based on template
        if args.template == "tag-value":
            parsed = parse_tag_value(text, separator)
        elif args.template == "key-value":
            parsed = parse_key_value(text, separator)
        elif args.template == "delimited":
            parsed = parse_delimited(text)
        else:
            parsed = None

        if parsed is None:
            continue

        rows_parsed += 1

        # Add preserved fields first, then parsed fields
        output_row = {}
        for field in preserve_fields:
            val = get_nested_value(record, field)
            if val is not None:
                flat_key = field.replace(".", "_")
                output_row[flat_key] = str(val)

        output_row.update(parsed)
        parsed_rows.append(output_row)

    # Write output CSV
    if parsed_rows:
        fieldnames = list(parsed_rows[0].keys())
        # Ensure all rows have same keys
        for row in parsed_rows[1:]:
            for k in row:
                if k not in fieldnames:
                    fieldnames.append(k)

        with open(args.output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in parsed_rows:
                writer.writerow({k: row.get(k, "") for k in fieldnames})
    else:
        with open(args.output_path, "w", encoding="utf-8") as f:
            f.write("")

    rows_out = len(parsed_rows)
    result = {
        "success": True,
        "rows_in": rows_in,
        "rows_out": rows_out,
        "rows_parsed": rows_parsed,
        "parse_success_rate": round(rows_parsed / rows_in * 100, 1) if rows_in > 0 else 0.0,
    }
    return result


# ── Raw text mode functions ──

def compile_markers(marker_strings: list) -> list:
    """Compile marker strings into regex patterns."""
    patterns = []
    for m in marker_strings:
        # Try to use as-is as a regex; fall back to escaping if invalid
        try:
            patterns.append(re.compile(m))
        except re.error:
            patterns.append(re.compile(re.escape(m)))
    return patterns


def parse_text(
    content: str,
    markers: list,
    field_names: list,
    record_separator: str = "----",
    skip_empty: bool = True,
) -> list:
    """Parse marker-delimited text into records.

    Uses a state machine approach:
    1. Split content into raw records by record_separator
    2. For each record, scan lines to identify which marker/field each line belongs to
    3. Accumulate multi-line content for each field

    Args:
        content: Full text content to parse.
        markers: List of marker strings/patterns that identify fields.
        field_names: List of field names corresponding to markers.
        record_separator: Pattern that separates records.
        skip_empty: If True, skip records where all fields are empty.

    Returns:
        List of dicts, one per record, with field_names as keys.
    """
    # Compile record separator pattern
    try:
        sep_pattern = re.compile(record_separator)
    except re.error:
        sep_pattern = re.compile(re.escape(record_separator))

    # Compile marker patterns
    marker_patterns = compile_markers(markers)

    # Split into raw record blocks
    raw_records = sep_pattern.split(content)

    records = []
    for raw in raw_records:
        raw = raw.strip()
        if not raw:
            continue

        # Parse fields from this record block
        record = {name: "" for name in field_names}
        current_field = None

        for line in raw.split("\n"):
            line_stripped = line.strip()
            if not line_stripped:
                # Blank line within a record: append newline to current field if any
                if current_field is not None:
                    record[current_field] += "\n"
                continue

            # Check if this line starts with any marker
            matched = False
            for i, pattern in enumerate(marker_patterns):
                match = pattern.match(line_stripped)
                if match:
                    current_field = field_names[i] if i < len(field_names) else None
                    if current_field is not None:
                        # Get content after the marker
                        remainder = line_stripped[match.end():].strip()
                        if record[current_field]:
                            record[current_field] += "\n" + remainder
                        else:
                            record[current_field] = remainder
                    matched = True
                    break

            if not matched and current_field is not None:
                # Continuation line for current field
                if record[current_field]:
                    record[current_field] += "\n" + line_stripped
                else:
                    record[current_field] = line_stripped

        # Clean up field values
        for name in field_names:
            record[name] = record[name].strip()

        # Skip empty records if requested
        if skip_empty and all(not v for v in record.values()):
            continue

        records.append(record)

    return records


def save_output(records: list, output_path: str, output_format: str = "auto") -> None:
    """Save parsed records to CSV or JSONL."""
    if output_format == "auto":
        ext = os.path.splitext(output_path)[1].lower()
        if ext in (".jsonl", ".ndjson"):
            output_format = "jsonl"
        else:
            output_format = "csv"

    if output_format == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        if not records:
            # Write empty CSV with no rows
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("")
            return

        fieldnames = list(records[0].keys())
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)


def raw_text_mode(args):
    """Run raw text mode: parse a raw text file with markers."""
    encoding = args.encoding
    if encoding == "auto":
        encoding = detect_encoding(args.input)

    with open(args.input, "r", encoding=encoding) as f:
        content = f.read()

    markers = [m.strip() for m in args.markers.split(",")]
    field_names = [n.strip() for n in args.field_names.split(",")]

    if len(markers) != len(field_names):
        return {
            "success": False,
            "error": f"Marker count ({len(markers)}) must match field name count ({len(field_names)})",
            "records_parsed": 0,
        }

    skip_empty = not args.no_skip_empty

    records = parse_text(
        content=content,
        markers=markers,
        field_names=field_names,
        record_separator=args.record_separator,
        skip_empty=skip_empty,
    )

    save_output(records, args.output, args.output_format)

    if args.output_format == "auto":
        ext = os.path.splitext(args.output)[1].lower().lstrip(".")
        actual_format = "jsonl" if ext in ("jsonl", "ndjson") else "csv"
    else:
        actual_format = args.output_format

    result = {
        "success": True,
        "input": args.input,
        "output": args.output,
        "encoding_detected": encoding,
        "markers": markers,
        "field_names": field_names,
        "record_separator": args.record_separator,
        "records_parsed": len(records),
        "output_format": actual_format,
    }
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Parse structured text into tabular data"
    )

    # Template mode args (positional, optional)
    parser.add_argument("input_path", nargs="?", help="Input JSONL/CSV file (template mode)")
    parser.add_argument("output_path", nargs="?", help="Output CSV file (template mode)")
    parser.add_argument(
        "--template",
        choices=["tag-value", "key-value", "delimited"],
        help="Template for parsing (template mode)",
    )
    parser.add_argument(
        "--preserve-fields",
        help="Comma-separated fields to carry over from input (supports dot notation)",
    )
    parser.add_argument(
        "--separator",
        default="||",
        help="Separator for multi-values (default: ||)",
    )

    # Raw text mode args
    parser.add_argument("--input", dest="input_file", help="Input text file (raw text mode)")
    parser.add_argument("--output", dest="output_file", help="Output file (raw text mode)")
    parser.add_argument("--markers", help="Comma-separated marker patterns")
    parser.add_argument("--field-names", help="Comma-separated field names for markers")
    parser.add_argument(
        "--record-separator",
        default="----",
        help="Record separator pattern (default: ----)",
    )
    parser.add_argument(
        "--encoding",
        default="auto",
        help="Input file encoding (default: auto-detect)",
    )
    parser.add_argument(
        "--skip-empty",
        action="store_true",
        default=True,
        help="Skip records where all fields are empty (default: true)",
    )
    parser.add_argument(
        "--no-skip-empty",
        action="store_true",
        help="Include records where all fields are empty",
    )
    parser.add_argument(
        "--output-format",
        choices=["auto", "csv", "jsonl"],
        default="auto",
        help="Output format (default: auto-detect from extension)",
    )

    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    # Determine mode based on which flags were provided
    result = None
    if args.template and args.input_path and args.output_path:
        result = template_mode(args)
    elif args.input_file and args.markers and args.field_names:
        # Remap dest names for raw_text_mode
        args.input = args.input_file
        args.output = args.output_file
        result = raw_text_mode(args)
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2))

    # Auto-checkpoint support
    if hasattr(args, 'auto_checkpoint') and args.auto_checkpoint:
        output_path = getattr(args, 'output_path', None) or getattr(args, 'output', None)
        if result.get("success") and output_path and os.path.exists(output_path):
            try:
                meta = {
                    "script": os.path.relpath(__file__),
                    "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
                    "rows_in": result.get("rows_in", 0) if isinstance(result, dict) else 0,
                    "rows_out": result.get("rows_out", result.get("records_parsed", 0)) if isinstance(result, dict) else 0,
                    "duration_seconds": round(time.time() - _start_time, 3),
                }
                maybe_checkpoint(output_path, "text_parse", True,
                                 checkpoint_format=args.checkpoint_format,
                                 metadata=meta)
            except Exception:
                pass  # Checkpoint is best-effort

    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
