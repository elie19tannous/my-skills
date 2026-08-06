#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""
Establish database connections, run health checks, and list schema tables.

Design rules encoded here:
- Credentials come from env vars, never hardcoded (resolve_credential)
- Connections are read-only by default (connect read_only=True)
- Connection strings are sanitized before any logging (sanitize_url)
"""

import argparse
import os
import re
import sys
from typing import Optional

try:
    from sqlalchemy import create_engine, text, event
    from sqlalchemy.engine import Engine
    from sqlalchemy import inspect as sa_inspect
except ImportError:
    print("SQLAlchemy required: pip install 'sqlalchemy>=2.0'", file=sys.stderr)
    sys.exit(1)


def resolve_credential(env_var: str) -> str:
    """
    Read connection URL from environment variable.

    Design rule: credentials come from env vars, never hardcoded.
    Raises a clear error if the variable is not set so the caller
    knows exactly what to fix without inspecting source code.
    """
    value = os.environ.get(env_var)
    if not value:
        raise EnvironmentError(
            f"Environment variable '{env_var}' is not set. "
            f"Export it before running: export {env_var}=<connection-url>"
        )
    return value


def sanitize_url(url: str) -> str:
    """
    Mask the password in a connection URL for safe logging.

    Design rule: connection strings are sanitized before any logging.
    Uses urllib.parse to correctly handle passwords containing '@'.
    """
    from urllib.parse import urlparse, urlunparse
    try:
        parsed = urlparse(url)
        if parsed.password:
            masked = parsed._replace(
                netloc=f"{parsed.username}:***@{parsed.hostname}"
                + (f":{parsed.port}" if parsed.port else ""))
            return urlunparse(masked)
    except Exception:
        pass
    return url


def _setup_read_only(url: str) -> Engine:
    """
    Create an engine with dialect-specific read-only enforcement.

    - SQLite: PRAGMA query_only = ON (via connect event)
    - PostgreSQL: default_transaction_read_only=on in options
    - MySQL/MariaDB: SET SESSION TRANSACTION READ ONLY (via connect event)
    - Other dialects: engine created without read-only guard
    """
    if url.startswith("sqlite"):
        engine = create_engine(url)

        @event.listens_for(engine, "connect")
        def set_sqlite_readonly(dbapi_conn, connection_record):
            dbapi_conn.execute("PRAGMA query_only = ON")

    elif url.startswith("postgresql") or url.startswith("postgres"):
        separator = "&" if "?" in url else "?"
        url_ro = f"{url}{separator}options=-c default_transaction_read_only=on"
        engine = create_engine(url_ro)

    elif url.startswith("mysql"):
        engine = create_engine(url)

        @event.listens_for(engine, "connect")
        def set_mysql_readonly(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("SET SESSION TRANSACTION READ ONLY")
            cursor.close()

    else:
        engine = create_engine(url)

    return engine


def connect(env_var: str, read_only: bool = True) -> Engine:
    """
    Create a SQLAlchemy engine from a connection URL stored in env_var.

    Design rule: connections are read-only by default to prevent
    accidental writes during exploration and loading workflows.

    Read-only enforcement is dialect-specific:
    - SQLite: PRAGMA query_only = ON (via connect event)
    - PostgreSQL: default_transaction_read_only=on in options
    - MySQL/MariaDB: SET SESSION TRANSACTION READ ONLY (via connect event)
    """
    url = resolve_credential(env_var)
    if read_only:
        return _setup_read_only(url)
    return create_engine(url)


def health_check(engine: Engine) -> bool:
    """Execute SELECT 1 to verify the connection is alive. Returns True/False."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def list_tables(engine: Engine) -> list:
    """Return table names for all user tables via SQLAlchemy Inspector."""
    inspector = sa_inspect(engine)
    return inspector.get_table_names()


def _print_tables(tables: list) -> None:
    """Print table list to stdout, or a message when schema is empty."""
    if tables:
        print(f"Tables ({len(tables)}):")
        for t in tables:
            print(f"  - {t}")
    else:
        print("No tables found.")


def main():
    parser = argparse.ArgumentParser(
        description="Connect to a database, run a health check, and list tables."
    )
    parser.add_argument(
        "--env-var",
        default="DATABASE_URL",
        help="Environment variable holding the connection URL (default: DATABASE_URL)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Open connection in read-write mode (default: read-only)",
    )
    args = parser.parse_args()

    try:
        url = resolve_credential(args.env_var)
        print(f"Connecting via: {sanitize_url(url)}")
        engine = connect(args.env_var, read_only=not args.write)

        ok = health_check(engine)
        print(f"Health check: {'PASS' if ok else 'FAIL'}")
        if not ok:
            sys.exit(1)

        _print_tables(list_tables(engine))

    except EnvironmentError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
