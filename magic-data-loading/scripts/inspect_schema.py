#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""
Discover table structure, columns, foreign keys, and sample data.

Uses SQLAlchemy Inspector so the same code works across SQLite,
PostgreSQL, and MySQL without dialect-specific queries.
"""

import argparse
import sys
from pathlib import Path

try:
    from sqlalchemy import text
    from sqlalchemy.engine import Engine
    from sqlalchemy import inspect as sa_inspect
except ImportError:
    print("SQLAlchemy required: pip install 'sqlalchemy>=2.0'", file=sys.stderr)
    sys.exit(1)

# Import connection helpers from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from connect_database import connect, resolve_credential, sanitize_url


def _inspect_single_table(insp, table_name: str, engine: Engine) -> dict:
    """Return schema metadata dict for one table (columns, FKs, row count)."""
    columns = []
    for col in insp.get_columns(table_name):
        columns.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "primary_key": col.get("primary_key", False),
        })

    fks = []
    for fk in insp.get_foreign_keys(table_name):
        fks.append({
            "constrained_columns": fk["constrained_columns"],
            "referred_table": fk["referred_table"],
            "referred_columns": fk["referred_columns"],
        })

    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")  # noqa: S608
            ).fetchone()
        row_count = row[0] if row else 0
    except Exception:
        row_count = None

    return {
        "table_name": table_name,
        "columns": columns,
        "foreign_keys": fks,
        "row_count": row_count,
    }


def inspect_tables(engine: Engine) -> list:
    """
    Return schema metadata for all tables.

    Each dict contains:
      table_name, columns (name/type/nullable/primary_key),
      foreign_keys, row_count_estimate.

    Row count uses COUNT(*) — exact but may be slow on very large tables.
    Column type is coerced to str for JSON-safe serialisation.
    """
    inspector = sa_inspect(engine)
    return [
        _inspect_single_table(inspector, table_name, engine)
        for table_name in inspector.get_table_names()
    ]


def _get_sample_rows(engine: Engine, table_name: str, col_names: list, n: int = 3) -> list:
    """Fetch first n rows from table_name and return as list of string-value dicts."""
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT * FROM {table_name} LIMIT {n}")  # noqa: S608
            ).fetchall()
        return [dict(zip(col_names, [str(v) for v in row])) for row in rows]
    except Exception:
        return []


def _get_detailed_columns(insp, table_name: str) -> list:
    """Return column metadata list with default field for a single table."""
    columns = []
    for col in insp.get_columns(table_name):
        columns.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "primary_key": col.get("primary_key", False),
            "default": str(col["default"]) if col.get("default") is not None else None,
        })
    return columns


def inspect_table(engine: Engine, table_name: str) -> dict:
    """
    Return detailed metadata for a single table including indexes and samples.

    Sample values are the first 3 rows cast to plain Python types so the
    result is always JSON-serialisable without a custom encoder.
    """
    inspector = sa_inspect(engine)
    columns = _get_detailed_columns(inspector, table_name)

    fks = []
    for fk in inspector.get_foreign_keys(table_name):
        fks.append({
            "constrained_columns": fk["constrained_columns"],
            "referred_table": fk["referred_table"],
            "referred_columns": fk["referred_columns"],
        })

    indexes = []
    for idx in inspector.get_indexes(table_name):
        indexes.append({
            "name": idx.get("name"),
            "columns": idx.get("column_names", []),
            "unique": idx.get("unique", False),
        })

    col_names = [c["name"] for c in columns]
    return {
        "table_name": table_name,
        "columns": columns,
        "foreign_keys": fks,
        "indexes": indexes,
        "sample_rows": _get_sample_rows(engine, table_name, col_names),
    }


def format_schema_report(tables: list) -> str:
    """
    Produce a human-readable plain-text schema report.

    One section per table, listing columns with types and row count.
    Suitable for pasting into a prompt or an analysis journal.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("DATABASE SCHEMA REPORT")
    lines.append("=" * 60)

    for t in tables:
        lines.append(f"\nTable: {t['table_name']}  (rows: {t['row_count']})")
        lines.append("-" * 40)

        for col in t["columns"]:
            pk_marker = " [PK]" if col["primary_key"] else ""
            null_marker = "" if col["nullable"] else " NOT NULL"
            lines.append(f"  {col['name']:<25} {col['type']}{pk_marker}{null_marker}")

        if t["foreign_keys"]:
            lines.append("  Foreign keys:")
            for fk in t["foreign_keys"]:
                src = ", ".join(fk["constrained_columns"])
                ref = ", ".join(fk["referred_columns"])
                lines.append(f"    {src} -> {fk['referred_table']}.{ref}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def _print_table_detail(detail: dict) -> None:
    """Print single-table inspection detail to stdout."""
    print(f"\nTable: {detail['table_name']}")
    print(f"Columns ({len(detail['columns'])}):")
    for col in detail["columns"]:
        pk = " [PK]" if col["primary_key"] else ""
        print(f"  {col['name']:<25} {col['type']}{pk}")
    if detail["foreign_keys"]:
        print("Foreign keys:")
        for fk in detail["foreign_keys"]:
            src = ", ".join(fk["constrained_columns"])
            ref = ", ".join(fk["referred_columns"])
            print(f"  {src} -> {fk['referred_table']}.{ref}")
    if detail["indexes"]:
        print("Indexes:")
        for idx in detail["indexes"]:
            print(f"  {idx['name']} on {idx['columns']} (unique={idx['unique']})")
    if detail["sample_rows"]:
        print(f"Sample rows (first {len(detail['sample_rows'])}):")
        for row in detail["sample_rows"]:
            print(f"  {row}")


def main():
    parser = argparse.ArgumentParser(
        description="Inspect database schema: tables, columns, foreign keys."
    )
    parser.add_argument(
        "--env-var",
        default="DATABASE_URL",
        help="Environment variable holding the connection URL (default: DATABASE_URL)",
    )
    parser.add_argument(
        "--table",
        default=None,
        help="Inspect a specific table in detail (default: list all tables)",
    )
    args = parser.parse_args()

    try:
        url = resolve_credential(args.env_var)
        print(f"Connecting via: {sanitize_url(url)}")
        engine = connect(args.env_var, read_only=True)

        if args.table:
            _print_table_detail(inspect_table(engine, args.table))
        else:
            print(format_schema_report(inspect_tables(engine)))

    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Schema inspection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
