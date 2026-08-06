# Workspace State

<!-- Status: initializing | in_progress | complete -->
**Status:** initializing

---

## Objective

<!-- What is the goal of this data processing task? What is the target output?
     Example: "Clean and enrich the product catalog dataset for publication as a HuggingFace dataset." -->

## Data Overview

<!-- Summarize the input data: file path, format, row/column counts, key column types.
     Update as you discover more about the data.
     Example: "52,143 rows x 8 columns. CSV, UTF-8. Mix of text (text, description, summary) and categorical (category, label) columns." -->

## Data Source

<!-- Track the origin of the data being processed.
     Source type: file | database | huggingface (future)
     For databases: track connection env var, dialect, tables used.
     
     Example (file):
     - **Source type:** file
     - **Source path:** data/input/survey_responses.csv
     - **Format:** CSV, UTF-8, comma-delimited
     
     Example (database):
     - **Source type:** database
     - **Connection env var:** DATABASE_URL
     - **Dialect:** postgresql
     - **Tables used:** customers, orders, order_items
     - **Read-only:** yes
     - **Extracted at:** 2026-05-08T10:30:00 -->

## Current Plan

<!-- What steps do you plan to take? This is YOUR plan — not a fixed pipeline.
     Steps can repeat, be skipped, or emerge dynamically based on what you discover.
     Update this section whenever the plan changes.

     Example:
     1. [complete] Load and validate the raw text file
     2. [complete] Profile data quality — quality score: 62/100
     3. [in_progress] Clean text normalization issues (whitespace, encoding artifacts)
     4. [pending] Re-profile after cleaning to check improvement
     5. [pending] Synthesize missing definitions using LLM (discovered 15% null rate)
     6. [pending] Validate final output against schema -->

## Current Task

<!-- What are you working on right now? Include the specific script, arguments, and expected outcome.
     Example: "Running normalize_strings.py --input ckpt_01_loaded.csv --operations trim,encoding,whitespace --output ckpt_03_cleaned.csv" -->

## Discoveries & Blockers

<!-- Record unexpected findings, edge cases, or blockers that affect your plan.
     This is where you note things that require plan revision or human input.

     Example:
     - DISCOVERY: 15% of 'english' column has sentinel value "X" — need LLM synthesis, not imputation
     - BLOCKER: KNN imputation fails on this dataset size — switching to median strategy
     - EDGE CASE: Column 'example' contains HTML markup — need format conversion before cleaning -->

## Completed Work

<!-- Record what has been done, including checkpoint paths and key results.

     Example:
     - Loaded raw text → ckpt_01_loaded.csv (52,143 rows x 8 cols)
     - Profiled quality → logs/analysis_journal_quality.md (score: 62/100, 3 critical issues)
     - Cleaned text → ckpt_03_cleaned.csv (52,143 rows, fixed 1,247 encoding issues) -->

## Data Destination

<!-- Track where processed data will be delivered.
     Destination type: file | database | huggingface (future)
     
     Example (file):
     - **Destination type:** file
     - **Output path:** workspace/output/cleaned_data.parquet
     
     Example (database):
     - **Destination type:** database
     - **Connection env var:** DATABASE_URL
     - **Target table:** customers_cleaned
     - **Write mode:** append
     - **Last delivered:** 2026-05-08T11:00:00
     - **Rows written:** 52,143 -->

## Interaction Mode

<!-- How the agent interacts with the user during this session.
     Mode: autonomous | collaborative | supervised
     Default: collaborative

     - autonomous: Agent executes full pipeline, reports at end. Skips all PAUSE points except PAUSE (always).
     - collaborative: Agent pauses at PAUSE (collaborative+) and PAUSE (always) points to present findings and get decisions.
     - supervised: Agent pauses at ALL PAUSE points, including PAUSE (supervised), before every action.

     Per-skill overrides (optional):
     - magic-data-synthesis: supervised
     - magic-data-cleaning: collaborative -->

**Mode:** collaborative

## Lifecycle

<!-- Lifecycle tracking for Tier 2+ projects. Tier 1 (quick tasks) skip this section.
     Current phase: Discover | Plan | Execute | Validate | Deliver
     Data spec: specs/data-spec.md (created during Planning phase)
     Progress: brief status update -->

## Configuration

<!-- Environment and configuration notes.
     Example: "LLM: openai/gpt-4o-mini via ~/.magic/.env. Workspace: /path/to/workspace." -->
