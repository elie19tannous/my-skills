# Baseline: Missing Value Handling

## Minimum Acceptable Behavior

An agent WITHOUT the data-cleaning skill would typically:
- Use `df.fillna(0)` or `df.dropna()` uniformly across all columns
- Not differentiate strategy by data type or missing percentage
- Not validate after imputation
- Not save a checkpoint

## With-Skill Expected Improvements

An agent WITH the data-cleaning skill should:
1. **Issue detection first** — run detection to understand the full missing value landscape before choosing strategies
2. **Type-aware strategy selection** — use mean/median for numeric with low missing %, KNN for numeric with moderate missing %, mode for categorical, drop/LLM for text
3. **Column-specific decisions** — different strategy per column, not one-size-fits-all
4. **Post-imputation validation** — verify null counts reduced, no new nulls introduced, row count preserved (for imputation strategies)
5. **Checkpoint** — save intermediate result after handling missing values

## Key Differentiators

The skill prevents two common mistakes: (1) imputing text columns with mode, which fills every missing email with the single most common string, and (2) using the same strategy for 3% missing and 18% missing, when KNN is appropriate for the latter but wasteful for the former.
