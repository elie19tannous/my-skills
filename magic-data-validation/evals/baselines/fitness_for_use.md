# Baseline: Fitness for Use

## Minimum Acceptable Behavior

A competent agent guided by SKILL.md should:

1. **Acknowledge the two different downstream use cases** and tailor validation accordingly:
   - Regulatory submission: zero tolerance for nulls in key columns, strict range enforcement, full traceability
   - ML training: can tolerate 1-2% nulls in non-target columns, focus on feature quality rather than completeness

2. **Detect statistical pitfalls:**
   - Survivorship bias: Houston site has 95% `dropout=False`, meaning the data over-represents patients who stayed in the trial
   - Simpson's paradox: overall positive correlation between `age` and `followup_score` reverses within each `treatment_group` -- aggregate analysis would produce misleading conclusions

3. **Explain why pitfalls matter differently per use case:**
   - Simpson's paradox is critical for regulatory reporting (wrong conclusion about treatment efficacy) but may be less critical for ML (the model can learn conditional relationships)
   - Survivorship bias affects both use cases but regulatory requires explicit acknowledgment and handling

4. **Run content validation on `notes`:**
   - Flag "see attached" and "refer to chart" as useless placeholder text
   - These are NOT caught by schema validation (they are valid strings)

5. **Detect out-of-range values:**
   - `baseline_score` and `followup_score` values >100 are data entry errors (valid range 0-100)

6. **Differentiate inferred from target schema:**
   - Inferred schema will show max values >100 (because they exist in data)
   - Target schema should enforce max=100 (because that is the valid range)
   - Agent should reconcile the two

## Key Knowledge Signals

The agent demonstrates SKILL.md knowledge if it:
- Asks about or discusses fitness-for-use before defining rules
- Applies different strictness levels for the two use cases
- Detects both survivorship bias and Simpson's paradox
- Runs content validation on `notes` as a separate step from schema validation
- Distinguishes inferred schema from target schema
- Follows the full validation ordering: schema -> constraints -> content -> sanity
- Mentions that LLM-based analysis might help with free-text `notes` evaluation (cross-reference to magic-data-synthesis)

## Common Failure Modes

- Agent applies identical validation rules for both use cases
- Agent misses Simpson's paradox because it only looks at aggregate statistics
- Agent misses survivorship bias because Houston's dropout rate "looks fine" in isolation
- Agent validates `notes` with schema checks only and misses placeholder text
- Agent treats inferred schema as ground truth without comparing to expected range (0-100)
- Agent does not mention that statistical pitfalls have different implications for regulatory vs. ML use
