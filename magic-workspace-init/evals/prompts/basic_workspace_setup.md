# Eval: Basic Workspace Setup

## Task

You are starting a new data processing project. The user has a CSV file with 5,000 rows of customer transaction data they want to clean and analyze. Set up a MAGIC workspace in the current directory, verify the environment is ready, and guide the user on next steps.

## Context

- This is a fresh directory with no existing files
- The user has Python 3.11 with pandas and numpy installed
- The data file has not been provided yet — the user will add it after setup
- This is a standard analysis task, not a quick one-off

## Expected Behaviors (for scoring)

- [ ] Agent runs init_workspace.py (or equivalent) to create directory structure
- [ ] Agent verifies Python environment (checks for required packages)
- [ ] Agent creates standard workspace directories (data/input, data/checkpoints, data/output, configs, reports, charts, logs, scripts)
- [ ] Agent checks and reports workspace_status from script output
- [ ] Agent guides user to place data file in data/input/
- [ ] Agent does not create .env files automatically
