#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""
Write DataFrames or Parquet files to a database table with a mandatory safety gate.

Critical design rules encoded here:
- Read-only connections CANNOT write; this script always creates a NEW
  engine with read_only=False — the caller must not pass a read-only engine.
- The PAUSE gate (confirm_write) fires before ANY write; no code path
  skips it. This mirrors the "human-in-the-loop" pattern for destructive ops.
- 'upsert' mode is intentionally unimplemented: UPSERT semantics differ
  across dialects (ON CONFLICT for PG/SQLite, ON DUPLICATE KEY for MySQL).
  Raise NotImplementedError with guidance rather than silently do the wrong thing.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    import pandas as pd
except ImportError:
    print("pandas required: pip install 'pandas>=2.0'", file=sys.stderr)
    sys.exit(1)

try:
    from sqlalchemy.engine import Engine
    from sqlalchemy import inspect as sa_inspect, text
except ImportError:
    print("SQLAlchemy required: pip install 'sqlalchemy>=2.0'", file=sys.stderr)
    sys.exit(1)

# Import connection helpers from the loading skill sibling
_loading_scripts = Path(__file__).parent.parent.parent / "magic-data-loading" / "scripts"
sys.path.insert(0, str(_loading_scripts))
from connect_database import connect, resolve_credential, sanitize_url


def confirm_write(table_name: str, row_count: int, mode: str) -> bool:
    """
    PAUSE gate — must fire before any write operation.

    In non-interactive (pipeline) mode this always returns True and prints
    a clear audit log line so downstream tooling can detect write events.
    In interactive mode (stdin is a TTY) it prompts the user and returns
    their choice, defaulting to abort on unexpected input.

    Design rule: all writes must pass through this gate. No code path
    in deliver_dataframe may call to_sql without calling confirm_write first.
    """
    warning = (
        f"[WRITE GATE] About to write {row_count} rows to '{table_name}' "
        f"(mode={mode}). "
        + ("This will DROP and recreate the table." if mode == "replace" else "")
    )
    print(warning)

    if sys.stdin.isatty():
        # Interactive: ask explicitly
        answer = input("Proceed? [y/N] ").strip().lower()
        return answer == "y"

    # Non-interactive (pipeline): auto-approve but log clearly
    print("[WRITE GATE] Non-interactive mode — proceeding automatically.")
    return True


def _compare_columns(df: pd.DataFrame, db_cols: dict) -> dict:
    """
    Compare DataFrame columns against DB column dict {name: type_str}.

    Returns missing (in DB not in df), extra (in df not in DB),
    and type_mismatches (advisory list of dicts with actual pandas dtypes).
    Broad heuristic — not authoritative, just advisory.
    """
    df_cols = set(df.columns)
    db_col_names = set(db_cols.keys())
    missing = sorted(db_col_names - df_cols)
    extra = sorted(df_cols - db_col_names)

    type_mismatches = []
    for col in df_cols & db_col_names:
        db_type = db_cols[col].upper()
        pandas_dtype = str(df[col].dtype)
        if "INT" in db_type and "int" not in pandas_dtype and "float" not in pandas_dtype:
            type_mismatches.append({"column": col, "db_type": db_type, "pandas_dtype": pandas_dtype})
        elif "FLOAT" in db_type or "REAL" in db_type or "DOUBLE" in db_type:
            if "float" not in pandas_dtype and "int" not in pandas_dtype:
                type_mismatches.append({"column": col, "db_type": db_type, "pandas_dtype": pandas_dtype})

    return {"missing": missing, "extra": extra, "type_mismatches": type_mismatches}


def validate_schema_compatibility(
    engine: Engine, df: pd.DataFrame, table_name: str
) -> dict:
    """
    Compare DataFrame columns against the existing table schema.

    Returns a compatibility report:
      compatible (bool), missing (cols in DB not in df),
      extra (cols in df not in DB), type_mismatches (list of dicts).

    type_mismatches is advisory — SQLAlchemy/the DB driver may coerce types
    automatically, but callers should review mismatches before writing.
    """
    inspector = sa_inspect(engine)

    if table_name not in inspector.get_table_names():
        return {
            "compatible": True,
            "missing": [],
            "extra": list(df.columns),
            "type_mismatches": [],
            "note": f"Table '{table_name}' does not exist yet — will be created.",
        }

    db_cols = {col["name"]: str(col["type"]) for col in inspector.get_columns(table_name)}
    comparison = _compare_columns(df, db_cols)
    compatible = len(comparison["missing"]) == 0 and len(comparison["type_mismatches"]) == 0

    return {
        "compatible": compatible,
        "missing": comparison["missing"],
        "extra": comparison["extra"],
        "type_mismatches": comparison["type_mismatches"],
    }


def _validate_mode(mode: str) -> None:
    """Raise appropriate error for invalid or unimplemented write modes."""
    if mode == "upsert":
        raise NotImplementedError(
            "upsert mode is not yet implemented. "
            "UPSERT semantics differ across dialects: use ON CONFLICT DO UPDATE "
            "(PostgreSQL/SQLite) or ON DUPLICATE KEY UPDATE (MySQL) via raw SQL "
            "or a dialect-specific library such as sqlalchemy-upsert."
        )
    if mode not in ("append", "replace"):
        raise ValueError(f"Unknown mode '{mode}'. Choose 'append' or 'replace'.")


def deliver_dataframe(
    engine: Engine,
    df: pd.DataFrame,
    table_name: str,
    mode: str = "append",
) -> dict:
    """
    Write df to table_name using the given mode.

    Modes:
      append  — INSERT rows; table must exist or will be created.
      replace — DROP table, recreate, INSERT all rows. Data loss is permanent.
      upsert  — Not implemented. Dialect-specific; raise NotImplementedError.

    The PAUSE gate fires before any write. Callers cannot bypass it from
    outside this function — it is the single entry point for all writes.

    Design rule: the engine passed here MUST have read_only=False.
    Passing a read-only engine will raise at write time, not silently succeed.
    """
    _validate_mode(mode)

    # PAUSE gate — mandatory before any write
    approved = confirm_write(table_name, len(df), mode)
    if not approved:
        return {"success": False, "reason": "Write aborted by user at PAUSE gate."}

    # pandas if_exists values match our mode names exactly for append/replace
    df.to_sql(table_name, engine, if_exists=mode, index=False)

    return {
        "success": True,
        "rows_written": len(df),
        "table": table_name,
        "mode": mode,
    }


def _load_parquet_input(input_path: str) -> "pd.DataFrame":
    """Load a Parquet file and print a confirmation line. Returns the DataFrame."""
    df = pd.read_parquet(input_path)
    print(f"Loaded {len(df)} rows from {input_path}")
    return df


def _print_deliver_result(result: dict) -> None:
    """Print delivery result to stdout, or write abort reason to stderr and exit."""
    if result["success"]:
        print(
            f"Wrote {result['rows_written']} rows to "
            f"'{result['table']}' (mode={result['mode']})"
        )
    else:
        print(result["reason"], file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Deliver a Parquet file to a database table."
    )
    parser.add_argument(
        "--env-var",
        default="DATABASE_URL",
        help="Environment variable holding the connection URL (default: DATABASE_URL)",
    )
    parser.add_argument("--table", required=True, help="Target table name")
    parser.add_argument(
        "--mode",
        choices=["append", "replace"],
        default="append",
        help="Write mode: append (INSERT) or replace (DROP+CREATE+INSERT)",
    )
    parser.add_argument("--input", required=True, help="Path to input Parquet file")
    args = parser.parse_args()

    try:
        url = resolve_credential(args.env_var)
        print(f"Connecting via: {sanitize_url(url)}")
        engine = connect(args.env_var, read_only=False)
        df = _load_parquet_input(args.input)

        compat = validate_schema_compatibility(engine, df, args.table)
        if not compat["compatible"]:
            print(f"Schema warning: {compat}", file=sys.stderr)

        _print_deliver_result(deliver_dataframe(engine, df, args.table, mode=args.mode))

    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except NotImplementedError as e:
        print(f"Not implemented: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Delivery error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
