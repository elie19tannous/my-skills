# Magic Data Lifecycle

Routing and orchestration knowledge for multi-step data processing tasks — the entry point that maps operations to the right skill and defines pipeline order.

## What This Skill Does

- Provides the canonical pipeline sequence: load → profile → clean → transform → validate → deliver
- Routes each operation to the correct `magic-data-*` skill via a skill routing table
- Defines quality gates, checkpoint strategy, and PAUSE points between phases

## Files

- `SKILL.md` — Agent knowledge document and frontmatter

## Related Skills

- `magic-workspace-init` — sets up the environment before the lifecycle begins
- `magic-data-loading` — first active phase of every pipeline
- `magic-data-validation` — quality gate before delivery
