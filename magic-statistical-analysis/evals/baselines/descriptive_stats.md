# Baseline: Descriptive Statistics

## Minimum Acceptable Behavior

An agent WITHOUT the statistical-analysis skill would typically:
- Call `df.describe()` on all columns, including employee_id
- Report raw numbers without narrative interpretation
- Not distinguish between numeric, text, and categorical columns
- Not compute skewness or identify distribution shape
- Not report text-specific statistics (word count, vocabulary size)

## With-Skill Expected Improvements

An agent WITH the statistical-analysis skill should:
1. **Column type detection** — classify each column as numeric, text, or categorical before computing statistics, and exclude or flag employee_id as non-meaningful for continuous analysis
2. **Type-appropriate statistics** — compute mean/median/std/skewness for numeric, frequency distributions for categorical, and word count/vocabulary size for text
3. **Distribution shape** — identify whether numeric columns are symmetric, left-skewed, or right-skewed based on skewness values
4. **Narrative interpretation** — generate human-readable summaries using uncertainty language ("appears approximately symmetric", "suggests high variability")
5. **Coefficient of variation** — report CV to contextualize spread relative to the mean

## Key Differentiators

The skill prevents undifferentiated `describe()` output. Without the skill, an agent treats employee_id as a continuous variable (computing mean employee_id, which is meaningless) and provides no narrative context for the numbers. With the skill, the agent classifies columns first and provides interpretable summaries.
