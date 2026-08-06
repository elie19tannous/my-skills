# Baseline: Basic CSV Load

## Minimum Acceptable Behavior

An agent WITHOUT the data-loading skill would typically:
- Load the file directly with `pd.read_csv("data/sales_q4.csv")` assuming UTF-8 and comma delimiter
- Not run format detection first
- Not validate after loading
- Not save a checkpoint

## With-Skill Expected Improvements

An agent WITH the data-loading skill should:
1. **Format detection first** — run content-based detection rather than trusting the `.csv` extension
2. **Encoding awareness** — detect encoding before loading, even if UTF-8 is likely
3. **Post-load validation** — verify row count, check for all-null columns, confirm types inferred
4. **Checkpoint** — save loaded data with a descriptive filename
5. **Reporting** — provide row count, column count, and dtype summary

## Key Differentiators

The skill should prevent silent failures. Without the skill, an agent loading a tab-separated file named `.csv` would get a single-column DataFrame with no error — the skill teaches agents to detect format by content, not extension.
