#!/usr/bin/env python3
"""
CALLABLE TOOL — detect_format.py
Detect file format characteristics for data loading.

Detects:
- File format (CSV, TSV, Parquet, JSON, JSONL, Excel, text)
- Character encoding
- Delimiter (for delimited files)
- BOM presence
- Header presence
- Estimated row count and file size
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import chardet
import pandas as pd


def detect_bom(file_path: str) -> tuple[bool, Optional[str]]:
    """
    Detect BOM (Byte Order Mark) in file.

    Returns:
        (has_bom, encoding_with_bom)
    """
    with open(file_path, 'rb') as f:
        first_bytes = f.read(4)

    bom_signatures = {
        b'\xef\xbb\xbf': 'utf-8-sig',
        b'\xff\xfe\x00\x00': 'utf-32-le',
        b'\x00\x00\xfe\xff': 'utf-32-be',
        b'\xff\xfe': 'utf-16-le',
        b'\xfe\xff': 'utf-16-be',
    }

    for bom, encoding in bom_signatures.items():
        if first_bytes.startswith(bom):
            return True, encoding

    return False, None


def detect_encoding(file_path: str, sample_size: int = 100000) -> str:
    """
    Detect file encoding using chardet.

    Args:
        file_path: Path to file
        sample_size: Number of bytes to sample

    Returns:
        Detected encoding name
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)

    result = chardet.detect(raw_data)
    encoding = result.get('encoding') or 'utf-8'
    confidence = result.get('confidence', 0.0)

    # Only fall back to utf-8 if chardet returned no encoding or is very
    # uncertain. A low threshold (0.05) preserves non-ASCII detections that
    # chardet is weakly confident about — better than silently assuming utf-8
    # for files that clearly contain 0x80-0xFF bytes (Latin-1 family).
    if confidence < 0.05 or encoding is None:
        encoding = 'utf-8'

    return encoding


def detect_delimiter(file_path: str, encoding: str) -> Optional[str]:
    """
    Detect delimiter for delimited text files using csv.Sniffer.

    Returns:
        Detected delimiter or None
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            # Read sample for sniffing
            sample = f.read(8192)

            if not sample.strip():
                return None

            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=',\t|;')
            return dialect.delimiter
    except (csv.Error, Exception):
        return None


def detect_header(file_path: str, encoding: str, delimiter: Optional[str]) -> bool:
    """
    Detect if file has header row.

    Uses csv.Sniffer.has_header() for delimited files.
    """
    if not delimiter:
        return False

    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = []
            for i, row in enumerate(reader):
                rows.append(row)
                if i >= 5:
                    break
            if len(rows) < 2:
                return False
            first_row = rows[0]
            # Header heuristic: first row has no purely-numeric values and looks like names
            numeric_count = sum(1 for v in first_row if v.replace('.', '').replace('-', '').isdigit())
            if numeric_count == 0 and all(len(v.strip()) < 64 for v in first_row):
                return True
            # Fallback to Sniffer on first few complete records
            try:
                sample = '\n'.join([delimiter.join(r) for r in rows])
                sniffer = csv.Sniffer()
                return sniffer.has_header(sample)
            except csv.Error:
                return True
    except Exception:
        return True


def detect_format_from_extension(file_path: str) -> str:
    """
    Detect format from file extension.
    """
    ext = Path(file_path).suffix.lower()

    format_map = {
        '.csv': 'csv',
        '.tsv': 'tsv',
        '.txt': 'text',
        '.parquet': 'parquet',
        '.pq': 'parquet',
        '.json': 'json',
        '.jsonl': 'jsonl',
        '.ndjson': 'jsonl',
        '.xlsx': 'excel',
        '.xls': 'excel',
    }

    return format_map.get(ext, 'text')


def detect_format_from_content(file_path: str, encoding: str) -> str:
    """
    Detect format by inspecting file content.
    """
    # Check for binary formats first
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8)

            # Parquet magic number
            if header.startswith(b'PAR1'):
                return 'parquet'

            # Excel magic numbers
            if header.startswith(b'\xd0\xcf\x11\xe0') or header.startswith(b'PK\x03\x04'):
                return 'excel'
    except Exception:
        pass

    # Check text-based formats
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            first_line = f.readline().strip()

            if not first_line:
                return 'text'

            # Check if it's JSON
            try:
                json.loads(first_line)
                # Could be JSONL or JSON
                second_line = f.readline().strip()
                if second_line:
                    try:
                        json.loads(second_line)
                        return 'jsonl'
                    except json.JSONDecodeError:
                        pass
                return 'json'
            except json.JSONDecodeError:
                pass

            # Check for common delimiters
            if '\t' in first_line:
                return 'tsv'
            elif ',' in first_line:
                return 'csv'
            else:
                return 'text'
    except Exception:
        return 'text'


def estimate_rows(file_path: str, file_format: str, encoding: str, delimiter: Optional[str]) -> int:
    """
    Estimate number of rows in file.

    Uses sampling for large files.
    """
    file_size = os.path.getsize(file_path)

    # For small files, count exactly
    if file_size < 10 * 1024 * 1024:  # 10MB
        try:
            if file_format in ['csv', 'tsv'] and delimiter:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    return sum(1 for _ in reader)
            elif file_format in ['text', 'jsonl']:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    return sum(1 for _ in f)
        except Exception:
            pass

    # For large files, estimate based on sample
    try:
        if file_format in ['csv', 'tsv', 'text']:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                sample_size = min(100000, file_size)
                sample = f.read(sample_size)
                lines_in_sample = sample.count('\n')

                if lines_in_sample > 0:
                    estimated = int((file_size / sample_size) * lines_in_sample)
                    return estimated
        elif file_format == 'jsonl':
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                sample_size = min(100000, file_size)
                sample = f.read(sample_size)
                lines_in_sample = sample.count('\n')

                if lines_in_sample > 0:
                    estimated = int((file_size / sample_size) * lines_in_sample)
                    return estimated
    except Exception:
        pass

    return 0


def detect_columns(file_path: str, file_format: str, encoding: str, delimiter: Optional[str], has_header: bool) -> int:
    """
    Detect number of columns in file.
    """
    try:
        if file_format in ['csv', 'tsv'] and delimiter:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                first_line = f.readline().strip()
                if first_line:
                    return len(first_line.split(delimiter))
        elif file_format == 'json':
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                content = f.read()
                data = json.loads(content)
                if isinstance(data, list) and len(data) > 0:
                    return len(data[0].keys()) if isinstance(data[0], dict) else 0
                elif isinstance(data, dict):
                    return len(data.keys())
        elif file_format == 'jsonl':
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                first_line = f.readline().strip()
                if first_line:
                    obj = json.loads(first_line)
                    return len(obj.keys()) if isinstance(obj, dict) else 0
        elif file_format == 'parquet':
            df = pd.read_parquet(file_path)
            return len(df.columns)
        elif file_format == 'excel':
            df = pd.read_excel(file_path, nrows=1)
            return len(df.columns)
    except Exception:
        pass

    return 0


def main(input_path: str, output_path: str) -> Dict[str, Any]:
    """
    Detect file format characteristics.

    Args:
        input_path: Path to input file
        output_path: Path to write detection results (JSON)

    Returns:
        Dictionary with detection results
    """
    try:
        # Validate input file exists
        if not os.path.isfile(input_path):
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path is correct"
            }

        # Get file size
        file_size_bytes = os.path.getsize(input_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Detect BOM
        has_bom, bom_encoding = detect_bom(input_path)

        # Detect encoding
        if has_bom and bom_encoding:
            encoding = bom_encoding
        else:
            encoding = detect_encoding(input_path)

        # Detect format from extension
        format_ext = detect_format_from_extension(input_path)

        # Detect format from content
        format_content = detect_format_from_content(input_path, encoding)

        # Use content detection if extension is generic
        file_format = format_content if format_ext == 'text' else format_ext

        # Detect delimiter
        delimiter = None
        if file_format in ['csv', 'tsv', 'text']:
            detected_delim = detect_delimiter(input_path, encoding)
            if detected_delim:
                delimiter = detected_delim
            elif file_format == 'tsv':
                delimiter = '\t'
            elif file_format == 'csv':
                delimiter = ','

        # Detect header
        has_header = detect_header(input_path, encoding, delimiter)

        # Estimate rows (subtract header row for CSV/TSV if has_header)
        estimated_rows = estimate_rows(input_path, file_format, encoding, delimiter)
        if has_header and file_format in ['csv', 'tsv'] and estimated_rows > 0:
            estimated_rows -= 1

        # Detect columns
        columns_detected = detect_columns(input_path, file_format, encoding, delimiter, has_header)

        result = {
            "success": True,
            "output_path": output_path,
            "format": file_format,
            "encoding": encoding,
            "delimiter": delimiter,
            "has_header": has_header,
            "has_bom": has_bom,
            "estimated_rows": estimated_rows,
            "file_size_mb": round(file_size_mb, 2),
            "columns_detected": columns_detected
        }

        # Write result to output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check file permissions and format compatibility"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect file format characteristics")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to write detection results (JSON)")

    args = parser.parse_args()

    result = main(args.input_path, args.output_path)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
