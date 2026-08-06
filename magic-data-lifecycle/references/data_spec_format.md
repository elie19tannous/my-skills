# Workspace Data Spec Format

The spec lives at `{workspace}/specs/data-spec.md`. The agent reads and writes it directly — no parser scripts.

## Required Sections

- **Discovery Summary** — data overview, quality baseline
- **Schema** — column table with types, requirements, notes
- **Processing Tasks** — categorized: cleaning, transformation, synthesis, enrichment, etc.
- **Success Criteria** — verification method per task (programmatic, text parsing, agent review, LLM judge)
- **Approach** — step-by-step plan referencing skills/scripts
- **Refinement History** — changes over time

## Template

```markdown
# Data Spec: [dataset name]

## Discovery Summary
- **Rows:** N | **Columns:** N | **Quality Score:** X/100
- **Key issues:** [brief list]

## Schema
| Column | Type | Required | Notes |
|--------|------|----------|-------|
| col_a  | string | yes    | Primary key |

## Processing Tasks
### Cleaning
- [ ] Task 1: [description] — Impact: [rows affected]

### Transformation
- [ ] Task 2: [description] — Impact: [columns affected]

### Synthesis
- [ ] Task 3: [description] — Impact: [rows to fill]

## Success Criteria
| Task | Metric | Target | Method |
|------|--------|--------|--------|
| Task 1 | null_rate | <= 5% | Programmatic |

## Approach
1. Step 1: [skill/script] — [what it does]
2. Step 2: [skill/script] — [what it does]

## Refinement History
- [date]: Initial spec created from discovery
```

See the lifecycle SKILL.md for how to use this spec within the lifecycle phases.
