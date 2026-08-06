# Project Patterns Reference

Actionable patterns for workspace initialization based on project type, user intent, and environment.

## Project Type Patterns

| Project Type | Detection Signals | Init Actions |
|---|---|---|
| ETL Pipeline | User mentions "transform", "load", "pipeline", scheduled runs | Create `src/`, `data/raw/`, `data/processed/`, `data/output/` dirs; suggest logging setup; add `.env` template for connection strings |
| One-Off Analysis | Single file mentioned, "quick look", "just want to see" | Flat structure with `workspace/` dir; skip heavy scaffolding; prioritize fast data loading |
| Multi-Dataset | Multiple files referenced, "join", "combine", "merge" | Create `data/` with per-source subdirs; generate manifest tracking file origins; suggest a data dictionary stub |
| dbt Project | `dbt_project.yml` exists or user mentions dbt | Detect existing `models/`, `seeds/`; do NOT restructure; add `analysis/` dir for ad-hoc exploration alongside dbt |
| Airflow Project | `dags/` dir exists or user mentions Airflow | Work inside existing structure; create `notebooks/` or `exploration/` for ad-hoc work; avoid touching DAG files |
| Jupyter-First | `.ipynb` files present, user says "notebook" | Create companion `.py` scripts for reusable logic; set up `utils/` for shared helpers; keep notebooks as entrypoints |

When multiple signals overlap: existing framework files (dbt, Airflow) take priority,
then explicit user labels, then file-based detection. Ask when ambiguous.

## Post-Init Workflow Guidance

| User Situation | What They Say | Recommended Next Step |
|---|---|---|
| Have data ready | "I have a CSV", "here's my file" | Run magic-data-loading immediately; skip exploration preamble |
| Multiple files, unclear relationship | "I have these files", lists 3+ sources | Run magic-data-profiling on each; present comparison summary before merging |
| No data yet | "Setting up for a project", "will get data later" | Create directory scaffolding only; write a `README` stub with expected data format |
| Exploring possibilities | "What can I learn from this?" | Run magic-data-exploration after loading; defer structure decisions until patterns emerge |
| Resuming previous work | `workspace/` already populated, prior outputs exist | Detect existing state; summarize what was done; ask where to continue |

### Transition Rules

- Do not suggest magic-data-transformation until at least one dataset is loaded and profiled.
- Do not suggest magic-report-generation until at least one analysis has produced findings.
- When the user says "start over", archive `workspace/` to `workspace_backup_<timestamp>/`.

## Environment Setup Patterns

| Environment | Detection | Setup Actions |
|---|---|---|
| System Python | No venv, no conda, bare `python3` | Warn about global installs; suggest creating a venv; install minimal deps only |
| Conda | `conda` in PATH, `.conda/` exists, `environment.yml` present | Use `conda install` for numpy/pandas/scipy; fall back to pip for niche packages |
| venv / pip | `venv/`, `.venv/`, or `requirements.txt` present | Activate existing venv; install from requirements.txt first; append new deps |
| uv | `uv.lock` or `.python-version` present, `uv` in PATH | Use `uv pip install` for speed; respect existing lock file; do not mix with pip |

## Common Dependency Issues

When installing data analysis dependencies, watch for these known problems:

- **openpyxl missing**: Pandas silently fails on `.xlsx` reads without it.
  Always install when Excel files are detected in the workspace.
- **chardet / charset-normalizer conflicts**: If encoding detection fails,
  pin `charset-normalizer>=3.0` and remove `chardet` to avoid version collisions.
- **scipy install failures on ARM Macs**: Use `conda install scipy` instead of pip
  when on Apple Silicon; pip wheels may not be available for older scipy versions.
- **pyarrow vs fastparquet**: When Parquet files are detected, prefer `pyarrow`
  (broader support). Only use `fastparquet` if user explicitly requests it.
- **sqlalchemy + driver mismatch**: When database connections are needed,
  always install the dialect driver alongside sqlalchemy
  (e.g., `psycopg2-binary` for PostgreSQL, `pymysql` for MySQL).
- **Large dependency chains**: If the user only needs pandas + matplotlib,
  do not install the full scientific stack. Add packages incrementally
  as analysis demands them.
- **xlrd deprecation**: For `.xls` files (legacy Excel), install `xlrd>=2.0`.
  Do not use xlrd for `.xlsx` -- that requires openpyxl instead.
- **Conflicting numpy versions**: Some packages pin numpy tightly.
  When conflicts arise, install numpy first, then other packages with `--no-deps`.
