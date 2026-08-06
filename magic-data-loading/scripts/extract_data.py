#!/usr/bin/env python3
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.
"""
Execute SQL queries with safety guards and write results to Parquet or dicts.

Safety rules encoded here:
- Always use parameterised queries (params dict passed to pd.read_sql)
- Inject LIMIT if not present and row_limit is set, to prevent runaway fetches
- SQLite does not support native query timeouts — documented, not silently skipped
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator, Optional

try:
    import pandas as pd
except ImportError:
    print("pandas required: pip install 'pandas>=2.0'", file=sys.stderr)
    sys.exit(1)

try:
    from sqlalchemy.engine import Engine
except ImportError:
    print("SQLAlchemy required: pip install 'sqlalchemy>=2.0'", file=sys.stderr)
    sys.exit(1)

# Import connection helpers from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from connect_database import connect, resolve_credential, sanitize_url


def _inject_limit(query: str, row_limit: int) -> str:
    """
    Append LIMIT clause if the query does not already contain one.

    Case-insensitive check; only appends when row_limit > 0.
    This is a last-resort guard — callers should write explicit LIMITs.
    """
    if row_limit and not re.search(r"\bLIMIT\b", query, re.IGNORECASE):
        return f"{query.rstrip().rstrip(';')} LIMIT {row_limit}"
    return query


def extract_to_checkpoint(
    engine: Engine,
    query: str,
    output_path: str,
    params: Optional[dict] = None,
) -> dict:
    """
    Execute query and save results as Parquet at output_path.

    Returns metadata dict: rows, columns, path.

    Parquet is chosen as the checkpoint format because it preserves
    dtypes and is readable by all downstream MAGIC skills.
    params is passed directly to pd.read_sql for parameterised execution —
    never interpolate user values into the query string.
    """
    df = pd.read_sql(query, engine, params=params)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "path": output_path,
    }


def query_as_records(
    engine: Engine,
    query: str,
    row_limit: int = 10000,
    params: Optional[dict] = None,
) -> list:
    """
    Execute query and return results as a list of dicts.

    row_limit is enforced by injecting a LIMIT clause when missing.
    Default cap of 10 000 prevents accidental full-table pulls that
    would exceed agent memory budgets.

    Note: SQLite has no native statement timeout. For PostgreSQL, set
    statement_timeout in the connection options if needed.
    """
    safe_query = _inject_limit(query, row_limit)
    df = pd.read_sql(safe_query, engine, params=params)
    return df.to_dict(orient="records")


def chunked_read(
    engine: Engine,
    query: str,
    chunk_size: int = 5000,
) -> Iterator[pd.DataFrame]:
    """
    Yield DataFrames in chunks to avoid loading large result sets into memory.

    Uses pd.read_sql with chunksize. Each yielded chunk is a complete
    DataFrame slice — consumers can process or write them independently.
    """
    chunks = pd.read_sql(query, engine, chunksize=chunk_size)
    for chunk in chunks:
        yield chunk


def _print_records(records: list) -> None:
    """Print up to 5 sample records and a total count to stdout."""
    print(f"Returned {len(records)} rows")
    for rec in records[:5]:
        print(f"  {rec}")
    if len(records) > 5:
        print(f"  ... ({len(records) - 5} more rows)")


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser for the extract command."""
    parser = argparse.ArgumentParser(
        description="Extract data from a database via SQL query."
    )
    parser.add_argument(
        "--env-var",
        default="DATABASE_URL",
        help="Environment variable holding the connection URL (default: DATABASE_URL)",
    )
    parser.add_argument("--query", required=True, help="SQL query to execute")
    parser.add_argument(
        "--output",
        default=None,
        help="Save results to this Parquet file path (omit to print as records)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10000,
        help="Row limit injected when LIMIT not present in query (default: 10000)",
    )
    return parser


def main():
    args = _build_arg_parser().parse_args()

    try:
        url = resolve_credential(args.env_var)
        print(f"Connecting via: {sanitize_url(url)}")
        engine = connect(args.env_var, read_only=True)

        if args.output:
            meta = extract_to_checkpoint(engine, args.query, args.output)
            print(
                f"Saved {meta['rows']} rows x {len(meta['columns'])} columns "
                f"to {meta['path']}"
            )
        else:
            _print_records(query_as_records(engine, args.query, row_limit=args.limit))

    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Extraction error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
