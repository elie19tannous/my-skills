# Eval: Batch Synthesis Pipeline

## Task

You have a complex dataset at `data/input/real_estate.csv` with 10,000 rows:
- `listing_id` (integer, complete)
- `address` (string, complete)
- `city` (string, complete)
- `state` (string, complete)
- `zip_code` (string, complete)
- `bedrooms` (integer, complete)
- `bathrooms` (float, complete)
- `sqft` (integer, complete)
- `price` (float, complete)
- `listing_description` (string, 3,000 rows are null, 500 rows contain "TBD")
- `neighborhood_score` (float, null for all rows — new column)
- `property_type` (string, 1,000 rows contain "???" or "N/A")
- `listing_url` (string, complete — contains the listing source URL)

You also have a reference dataset at `data/reference/neighborhoods.csv` with columns: `zip_code`, `neighborhood_name`, `walkability_score`, `school_rating`, `crime_index`.

Requirements:
1. Enrich `neighborhood_score` from the reference dataset first (join on `zip_code`, compute as `walkability_score * 0.4 + school_rating * 0.3 + (10 - crime_index) * 0.3`)
2. Fill `property_type` sentinels using LLM classification based on bedrooms, bathrooms, sqft, and address
3. Generate `listing_description` for missing/sentinel rows using LLM, depending on all other columns including the enriched ones
4. Budget: maximum $15.00 for the entire pipeline
5. Validate all synthesized columns

## Expected Behaviors (for scoring)

- [ ] Agent uses `enrich_from_reference.py` or reference_lookup strategy BEFORE LLM synthesis for neighborhood_score
- [ ] Agent computes neighborhood_score via expression strategy (not LLM) since it is a deterministic formula
- [ ] Agent builds a multi-column synthesis config with correct dependency ordering: neighborhood_score first (no LLM), then property_type (LLM), then listing_description (LLM, depends on property_type and neighborhood_score)
- [ ] Agent uses `fill-sentinels` mode with patterns `["TBD", "???", "N/A"]`
- [ ] Agent sets `--max-cost 15.00` to enforce budget
- [ ] Agent runs `--dry-run` first to verify the pipeline will stay within budget
- [ ] Agent runs `--sample-size` preview (e.g., 50 rows) before full 10K run
- [ ] Agent presents preview results and cost estimate before proceeding
- [ ] Agent configures `--resume` capability in case of cost limit interruption
- [ ] Agent validates with code-based checks for neighborhood_score (value range 0-10) and property_type (allowed values), and LLM-as-judge for listing_description (quality rubric)
- [ ] Agent uses checkpoint/resume: if cost limit is hit mid-run, partial results are saved and can be resumed
- [ ] Agent does NOT use LLM for neighborhood_score — recognizes it is a deterministic computation
