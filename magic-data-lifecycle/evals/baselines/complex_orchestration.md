# Baseline: Complex Orchestration

## Minimum Acceptable Behavior

An agent WITHOUT the lifecycle skill would typically:
- Load all three files with generic pandas calls, possibly failing on JSONL or Parquet format
- Attempt to merge all sources in one step without independent profiling
- Hard-code column mappings without checking schemas first
- Not define a quality target — just merge and report results
- When validation fails (78 < 85), either give up or retry the same approach
- Not produce a compliance report or structured assessment

## With-Skill Expected Improvements

An agent WITH the lifecycle skill should:
1. **Per-source loading** — use magic-data-loading for each source with format-appropriate handling (CSV encoding detection, Parquet schema reading, JSONL line parsing)
2. **Independent profiling** — profile each source before merging to catch per-source issues early (not just aggregate issues post-merge)
3. **Schema normalization** — route joins to magic-data-transformation with explicit column mapping (customer_id → cust_id, email-based matching)
4. **Operation routing** — currency conversion → magic-data-transformation (math), date normalization → magic-data-cleaning (regex), text filling → magic-data-synthesis (semantic)
5. **Quality gating** — define quality >= 85 as a gate, not just a hope
6. **Refinement loop** — when 78 < 85, identify the specific cause (null names), propose targeted fixes, re-execute, and re-validate
7. **Compliance report** — structured comparison of target vs actual for each quality gate
8. **Convergence awareness** — if the refinement loop doesn't converge after 3 attempts, suggest criteria adjustment rather than infinite looping

## Key Differentiators

The complex orchestration test evaluates two capabilities no other skill provides: (1) cross-skill sequencing across multiple datasets with different formats, and (2) refinement loops when validation fails. Without the lifecycle skill, an agent treats a multi-source merge as a single operation. With the skill, the agent profiles each source independently, sequences operations correctly (load all → profile all → plan → execute → validate), and knows how to respond when validation fails — not by giving up or retrying blindly, but by diagnosing the specific failure, proposing targeted fixes, and re-validating.
