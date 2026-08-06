# Baseline: Constraint Checking

## Minimum Acceptable Behavior

A competent agent guided by SKILL.md should:

1. **Define constraint types correctly:**
   - Range constraint for `salary` (30000-500000), catching the zero-salary placeholders
   - Enum constraint for `department`, catching "Ops" and "IT" as invalid values
   - Cross-column constraint for `hire_date` < `termination_date`
   - Referential integrity for `manager_id` -> `employee_id`

2. **Separate text validation from schema/constraint validation:**
   - Run content validation on `performance_notes` as a distinct step
   - Detect sentinels: "N/A" (200 rows), "TBD" (50 rows), single spaces (15 rows)
   - NOT apply numeric or categorical rules to `performance_notes`

3. **Follow the layered validation ordering:**
   - Schema validation (types, nullability) first
   - Constraint checking (range, enum, cross-column) second
   - Content validation (sentinels, placeholder text) third

4. **Report violations with specificity:**
   - Counts per violation type per column
   - Sample values showing the actual violations
   - Clear distinction between different violation categories

## Key Knowledge Signals

The agent demonstrates SKILL.md knowledge if it:
- Separates constraint types (range, enum, pattern, cross-column, referential)
- Explicitly checks column dtype before applying numeric rules
- Uses content validation (not schema validation) for free-text `performance_notes`
- Mentions that schema validation checks structure while content validation checks semantics
- Follows the ordering: schema -> constraints -> content

## Common Failure Modes

- Agent applies numeric range checks to `performance_notes` -- produces 100% failure
- Agent misses cross-column constraint (`hire_date` < `termination_date`)
- Agent treats sentinel detection as part of schema validation instead of content validation
- Agent does not check referential integrity on `manager_id`
- Agent reports violations without counts or samples
