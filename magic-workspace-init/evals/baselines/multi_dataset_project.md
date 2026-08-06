# Baseline: Multi-Dataset Project

## Minimum Acceptable Behavior

An agent WITHOUT the workspace-init skill would typically:
- Dump all three data sources into a single flat directory
- Not create per-dataset subdirectories
- Not consider project type when deciding workspace structure
- Not verify that pyarrow is installed (needed for Parquet files)
- Possibly over-scaffold with pipeline-specific directories for a one-off task

## With-Skill Expected Improvements

An agent WITH the workspace-init skill should:
1. **Project type recognition** — identify this as a multi-dataset project and adapt the workspace accordingly
2. **Per-dataset organization** — create subdirectories under data/input/ for each source (sales/, inventory/, returns/) to keep sources separate before merging
3. **Appropriate scaffolding** — include data/checkpoints/ for intermediate merge results, but skip ETL-specific directories (staging/, archive/) since this is a one-off analysis
4. **Dependency awareness** — verify pyarrow is installed since inventory data is in Parquet format
5. **Data placement guidance** — advise the user on how to organize files (symlink vs copy, per-source subdirs)

## Key Differentiators

The skill teaches agents to match workspace complexity to project type. Without the skill, agents either under-scaffold (flat directory, no checkpoints) or over-scaffold (full ETL structure for a one-off task). The project type guidance ensures the workspace is fit-for-purpose.
