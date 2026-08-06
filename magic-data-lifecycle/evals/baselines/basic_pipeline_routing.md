# Baseline: Basic Pipeline Routing

## Minimum Acceptable Behavior

An agent WITHOUT the lifecycle skill would typically:
- Load the file directly with `pd.read_csv()` and print `.describe()` or `.info()`
- Run ad-hoc analysis without a structured discovery phase
- Not distinguish between "checking data" (discover) and "cleaning data" (execute)
- Not establish a quality baseline before suggesting actions
- Not reference any specialized skills — do everything inline with pandas

## With-Skill Expected Improvements

An agent WITH the lifecycle skill should:
1. **Phase awareness** — recognize "check this data" as a Discover phase task, not an Execute task
2. **Skill routing** — delegate loading to magic-data-loading (format detection, encoding handling) rather than raw pd.read_csv
3. **Auto-profiling** — run magic-data-profiling immediately after loading to establish quality baseline
4. **Sequencing discipline** — Discover before Plan, not jumping to cleaning suggestions without profiling first
5. **Proportional infrastructure** — recognize this as a simple check (Tier 1 or light Tier 2), not setting up data specs and compliance reports for an initial exploration

## Key Differentiators

The skill teaches agents to think in phases rather than ad-hoc operations. Without the skill, an agent would jump directly to analysis. With the skill, the agent establishes a quality baseline first and routes each operation to the right specialist skill. The lifecycle skill's value is in knowing WHICH skill to use and WHEN — not in performing the operations itself.
