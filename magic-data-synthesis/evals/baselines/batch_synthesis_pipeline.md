# Baseline: Batch Synthesis Pipeline

## Minimum Acceptable Agent Behavior

A competent agent given this task and the magic-data-synthesis SKILL.md should:

### Must Do (failure if missing)
1. **Reference enrichment first**: Use reference data (neighborhoods.csv) to enrich neighborhood_score BEFORE LLM synthesis — do not use LLM for deterministic lookups
2. **Correct strategy selection**: Use expression/reference_lookup strategy (not LLM) for neighborhood_score computation, since it is a deterministic formula
3. **Dependency ordering**: Process columns in correct order: neighborhood_score (reference+expression) → property_type (LLM) → listing_description (LLM, depends on enriched columns)
4. **Budget enforcement**: Set --max-cost 15.00 and configure checkpoint/resume for cost-limited runs
5. **Preview gate**: Run dry-run and/or sample preview before committing to 10,000 rows of LLM calls
6. **Validation**: Validate all synthesized columns with appropriate approaches per column type

### Should Do (quality indicators)
7. **Multi-column config**: Build a single synthesis config with all three columns and correct depends_on declarations
8. **Mixed strategies**: Use `reference_lookup` or `expression` for neighborhood_score, `llm_text` for property_type and listing_description
9. **Sentinel detection**: Configure sentinel patterns ["TBD", "???", "N/A"] and use fill-sentinels mode
10. **Appropriate validation**: Code-based checks for neighborhood_score (range 0-10), allowed-values for property_type, LLM-as-judge rubric for listing_description quality
11. **Resume capability**: Configure --resume flag so interrupted runs can continue from the last checkpoint
12. **Cost estimation**: Dry-run shows estimated cost is within $15 budget before proceeding

### May Do (advanced behaviors)
13. **Smart sampling**: Use --smart-sample to ensure preview includes rows with sentinels/nulls
14. **Enrichment before LLM**: For listing_description, include neighborhood_name from reference data as additional context
15. **Stratified preview**: Sample proportionally across property types or cities
16. **Validation criteria JSON**: Generate machine-readable criteria for automated validation
17. **Batch size tuning**: Adjust --batch-size based on row count and cost per call

## Anti-Patterns (should NOT do)
- Use LLM to generate neighborhood_score (it is a deterministic formula: walkability * 0.4 + school_rating * 0.3 + (10 - crime_index) * 0.3)
- Process listing_description before property_type (listing_description depends on property_type)
- Skip the reference enrichment step and use LLM for all three columns
- Run full 10K rows without a preview or dry-run — this could exhaust the $15 budget on bad prompts
- Use a single generic prompt for both property_type classification and listing_description generation
- Ignore checkpoint/resume — if cost limit is hit at row 5000, partial results must be recoverable
- Skip validation — the pipeline has 3 different column types requiring 3 different validation approaches
