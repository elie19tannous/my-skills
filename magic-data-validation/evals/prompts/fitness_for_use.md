# Eval: Fitness for Use

## Task

You have a dataset `clinical_trial_results.csv` with 25,000 rows from a multi-site clinical trial:
- `patient_id` (integer, unique)
- `site` (categorical: "NYC", "LA", "Chicago", "Houston", "Miami")
- `treatment_group` (categorical: "control", "drug_a", "drug_b")
- `age` (integer, range 18-85)
- `baseline_score` (numeric, 0-100)
- `followup_score` (numeric, 0-100)
- `adverse_event` (boolean)
- `dropout` (boolean)
- `notes` (free text, nullable)

The dataset will be used for TWO purposes:
1. **Regulatory submission** -- strict requirements, zero tolerance for missing data in key columns, every record must be traceable
2. **Internal ML model** -- training a predictive model for adverse events, can tolerate some noise

Known complexities:
- Site "Houston" has 95% `dropout=False` (potential survivorship bias)
- Overall correlation between `age` and `followup_score` is positive, but within each `treatment_group` it is negative (Simpson's paradox)
- 500 `notes` fields contain "see attached" or "refer to chart" (useless placeholder text)
- `baseline_score` and `followup_score` have a few values above 100 (data entry errors)

Validate this dataset with appropriate strictness for EACH use case. Identify the statistical pitfalls and explain why they matter differently for each use case.

## Expected Behaviors (for scoring)

- [ ] Agent asks about or acknowledges the two different downstream use cases
- [ ] Agent applies stricter validation rules for regulatory submission than for ML training
- [ ] Agent detects survivorship bias in the Houston site data
- [ ] Agent detects Simpson's paradox in age vs. followup_score across treatment groups
- [ ] Agent detects out-of-range values (>100) in score columns
- [ ] Agent runs content validation on `notes` and flags "see attached" / "refer to chart" as placeholders
- [ ] Agent explains why Simpson's paradox matters more for regulatory reporting than ML training
- [ ] Agent differentiates inferred schema from target/expected schema
- [ ] Agent recommends different validation thresholds per use case (e.g., 0% null tolerance for regulatory, 1-2% acceptable for ML)
- [ ] Agent follows the full validation ordering: schema -> constraints -> content -> sanity
