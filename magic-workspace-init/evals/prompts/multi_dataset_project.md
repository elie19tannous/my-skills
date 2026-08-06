# Eval: Multi-Dataset Project

## Task

You are setting up a workspace for a project that involves three separate data sources:
- `sales/` — monthly CSV exports from the sales system (12 files, ~50MB total)
- `inventory/` — daily inventory snapshots in Parquet format (365 files, ~200MB total)
- `returns/` — customer returns data in JSONL format (1 file, ~5MB)

The user wants to merge these into a unified dataset for analysis. Set up an appropriate workspace structure.

## Context

- The directory is empty
- All three data sources are on the user's local machine
- The user expects to run this analysis once (not a recurring pipeline)
- Total data volume is ~255MB — fits in memory but warrants checkpoints

## Expected Behaviors (for scoring)

- [ ] Agent recognizes this as a multi-dataset project type
- [ ] Agent creates per-dataset subdirectories under data/input/ (e.g., data/input/sales/, data/input/inventory/, data/input/returns/)
- [ ] Agent sets up data/checkpoints/ for intermediate merge results
- [ ] Agent does not add ETL-specific directories (staging/, archive/) since this is a one-off analysis
- [ ] Agent verifies environment has pyarrow (needed for Parquet)
- [ ] Agent advises on data placement — symlink or copy to input subdirs
