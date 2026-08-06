# Baseline: Basic Workspace Setup

## Minimum Acceptable Behavior

An agent WITHOUT the workspace-init skill would typically:
- Create an ad-hoc directory like `output/` or dump files in the current directory
- Not verify that required Python packages are installed
- Not establish a consistent directory convention
- Not create workspace_state.md for session tracking
- Not separate input, checkpoint, and output data

## With-Skill Expected Improvements

An agent WITH the workspace-init skill should:
1. **Standardized structure** — create the full MAGIC directory tree (data/input, data/checkpoints, data/output, configs, reports, charts, logs, scripts)
2. **Environment verification** — check that pandas, numpy, and other required packages are installed before proceeding
3. **Status reporting** — present workspace_status (fresh/complete/partial/adopted) from the init script output
4. **User guidance** — direct the user to place their data file in data/input/ and explain the workspace layout
5. **No .env creation** — never auto-create .env files; only guide the user to create them if LLM features are needed

## Key Differentiators

The skill prevents workspace sprawl. Without the skill, an agent creates files in arbitrary locations, making it impossible to resume work in a later session or hand off to another agent. The standardized structure ensures every skill knows where to find inputs and write outputs.
