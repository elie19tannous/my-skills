# Baseline: Complex Cleaning Plan

## Minimum Acceptable Behavior

An agent WITHOUT the data-cleaning skill would typically:
- Fix issues ad-hoc as they encounter them, without a plan
- Mix cleaning and synthesis in the same pass
- Deduplicate before normalizing strings (missing duplicates that differ only by whitespace/casing)
- Impute sentinel values ("No response", "TBD") with mode or empty string instead of routing to synthesis
- Not checkpoint between stages, making rollback impossible
- Validate only at the end, if at all

## With-Skill Expected Improvements

An agent WITH the data-cleaning skill should:
1. **Full detection first** — scan all columns for all issue types before committing to any strategy
2. **Plan before execute** — produce a structured cleaning plan with ordered steps, each specifying operation, target columns, strategy, and reason
3. **Correct ordering** — normalize strings before deduplication; clean deterministic issues before imputation; clean before synthesis
4. **Cleaning vs synthesis routing** — recognize that "No response" and "TBD" sentinel values in `open_feedback` require LLM-based contextual fill (synthesis), not statistical imputation (cleaning)
5. **Staged checkpointing** — save intermediate results after each major cleaning stage for rollback capability
6. **Per-stage validation** — validate after each stage to catch regressions early, not just at the end
7. **Outlier handling** — treat negative `income` values as errors to flag/remove, not as valid data to impute over

## Key Differentiators

The skill's most critical contribution is the cleaning-vs-synthesis boundary. Without it, an agent fills "TBD" placeholders in free-text feedback with the most common response string (mode), producing thousands of identical fake responses. The skill teaches that sentinel values requiring meaningful content are a synthesis problem, not a cleaning problem. The skill also enforces the normalize-before-deduplicate ordering that prevents duplicate misses.
