# Eval: ETL Pipeline Workspace

## Task

You are setting up a MAGIC workspace inside an existing dbt project. The project structure already has:
```
my-dbt-project/
├── dbt_project.yml
├── models/
├── seeds/
├── data/                  <- dbt seeds data, NOT MAGIC data
├── logs/                  <- dbt logs, NOT MAGIC logs
├── macros/
└── tests/
```

The user wants to use MAGIC skills to clean and transform a raw CSV export before loading it into dbt seeds. This will be a recurring ETL task — the user will re-run the cleaning pipeline monthly.

## Context

- The directory already has `data/` and `logs/` directories used by dbt
- Initializing at the project root would conflict with existing directories
- This is a recurring ETL pipeline, not a one-off analysis
- The raw CSV is ~80MB and arrives monthly

## Expected Behaviors (for scoring)

- [ ] Agent recognizes conflict with existing data/ and logs/ directories
- [ ] Agent suggests creating a subdirectory (e.g., magic-workspace/) to avoid conflicts
- [ ] Agent does NOT init at the project root (would create ambiguous paths)
- [ ] Agent does NOT nest inside an existing MAGIC workspace
- [ ] Agent considers ETL-specific directories (staging/ or archive/) for the recurring pipeline pattern
- [ ] Agent sets up workspace_state.md for multi-session continuity
- [ ] Agent verifies environment and reports any missing packages
- [ ] Agent explains the monthly workflow: raw CSV -> MAGIC clean -> dbt seeds
