# Eval: Descriptive Statistics

## Task

You have a CSV file at `data/employee_survey.csv` containing employee satisfaction survey results. The file has 1,200 rows and columns: employee_id, department, tenure_years, satisfaction_score (1-10), salary, response_text. Compute descriptive statistics for all columns, generate narrative interpretations, and save the results.

## Context

- The dataset contains a mix of numeric (tenure_years, satisfaction_score, salary), categorical (department), and text (response_text) columns
- employee_id is numeric but should not be analyzed as a continuous variable
- You need to detect column types and apply appropriate statistics to each

## Expected Behaviors (for scoring)

- [ ] Agent detects column types (numeric, text, categorical) before computing statistics
- [ ] Agent computes central tendency (mean, median) and spread (std, IQR) for numeric columns
- [ ] Agent computes skewness and identifies distribution shape (symmetric, left/right-skewed)
- [ ] Agent computes frequency distributions for categorical columns (department)
- [ ] Agent computes text statistics (word count, vocabulary size) for text columns
- [ ] Agent generates narrative interpretations using uncertainty language ("appears", "suggests")
- [ ] Agent excludes or flags employee_id as not meaningful for continuous analysis
