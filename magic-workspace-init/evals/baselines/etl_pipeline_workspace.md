# Baseline: ETL Pipeline Workspace

## Minimum Acceptable Behavior

An agent WITHOUT the workspace-init skill would typically:
- Initialize at the project root, conflicting with existing dbt data/ and logs/ directories
- Not recognize the risk of nested or conflicting workspace structures
- Not consider ETL-specific directories for recurring pipeline workflows
- Not set up workspace_state.md for cross-session continuity
- Create ambiguous paths where data/input/ could mean dbt seeds or MAGIC input

## With-Skill Expected Improvements

An agent WITH the workspace-init skill should:
1. **Conflict detection** — recognize that data/ and logs/ already exist with different semantics (dbt, not MAGIC) and refuse to init at the project root
2. **Subdirectory isolation** — suggest creating magic-workspace/ (or similar) as a sibling or child directory to avoid path collisions
3. **Anti-pattern avoidance** — never nest inside another MAGIC workspace; never create ambiguous checkpoint paths
4. **ETL-appropriate structure** — for recurring pipelines, consider adding staging/ or archive/ directories beyond the standard layout
5. **Session continuity** — set up workspace_state.md to support the monthly re-run workflow
6. **Integration guidance** — explain the flow: raw CSV arrives monthly -> MAGIC workspace cleans it -> output goes to dbt seeds/

## Key Differentiators

The skill prevents the most dangerous workspace anti-pattern: initializing inside an existing project where directory names collide. Without the skill, an agent would overwrite or conflict with dbt's data/ directory, causing silent data loss or path confusion. The skill's NEVER rules (no nested workspaces, no absolute paths) protect against these failures.
