# Magic Workspace Init

Initialize a MAGIC data processing workspace: directory scaffolding, Python environment verification, dependency installation, and LLM configuration.

## What This Skill Does

- Creates the standard workspace directory structure and verifies the Python 3.12+ environment
- Installs required dependencies (pandas, numpy, DataDesigner, and skill-specific packages)
- Configures LLM access for skills that require it (magic-data-synthesis, magic-report-generation)

## Files

- `SKILL.md` — Agent knowledge document and frontmatter

## Related Skills

- `magic-data-lifecycle` — lifecycle orchestration begins after workspace is ready
- `magic-data-loading` — first pipeline skill after initialization
- `magic-data-synthesis` — requires LLM configuration set up by this skill
