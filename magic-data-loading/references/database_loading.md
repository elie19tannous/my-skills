# Database Loading Reference

## Connection String Patterns

| Dialect | Pattern | Default Port | Driver |
|---------|---------|-------------|--------|
| PostgreSQL | `postgresql://user:pass@host:5432/dbname` | 5432 | psycopg2 |
| MySQL | `mysql+pymysql://user:pass@host:3306/dbname` | 3306 | pymysql |
| SQLite | `sqlite:///path/to/file.db` | N/A | built-in |
| SQLite (memory) | `sqlite:///:memory:` | N/A | built-in |

## Environment Variable Convention

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Primary connection string (any dialect) |
| `PG_URL` | PostgreSQL-specific override |
| `MYSQL_URL` | MySQL-specific override |

## Read-Only Enforcement

| Dialect | Method | Level |
|---------|--------|-------|
| SQLite | `PRAGMA query_only = ON` | Connection |
| PostgreSQL | `SET default_transaction_read_only = ON` | Session |
| MySQL | `SET SESSION TRANSACTION READ ONLY` | Session |

## Safety Best Practices

1. **Never embed credentials in code** — Use environment variables exclusively
2. **Sanitize connection strings in logs** — Replace password with `***`
3. **Use parameterized queries** — Never interpolate user input into SQL strings
4. **Set row limits** — Default to 10,000 rows; require explicit override for larger extracts
5. **Chunked reads for large tables** — Use `chunk_size` parameter to avoid memory exhaustion
6. **Check table size before full extract** — `SELECT COUNT(*) FROM table` before `SELECT * FROM table`

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Wrong driver installed | `ModuleNotFoundError: No module named 'psycopg2'` | `pip install psycopg2-binary` |
| Connection string typo | `OperationalError: could not translate host name` | Check host, port, database name |
| Read-only violation | `ReadOnlyError` or `OperationalError` | Create new connection with `read_only=False` |
| SQL injection | Unexpected query results or errors | Use parameterized queries, never f-strings |
| Memory exhaustion on large table | Process killed or `MemoryError` | Use `chunked_read()` with `chunk_size=5000` |
| Stale connection | `OperationalError: server closed the connection` | Use `pool_pre_ping=True` in `create_engine()` |

## Timeout Configuration

| Dialect | Parameter | Example |
|---------|-----------|---------|
| PostgreSQL | `connect_args={"options": "-c statement_timeout=30000"}` | 30s timeout |
| MySQL | `connect_args={"read_timeout": 30}` | 30s timeout |
| SQLite | Not natively supported | Use application-level timeout |
