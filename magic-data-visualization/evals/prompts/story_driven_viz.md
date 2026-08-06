# Eval: Story-Driven Visualization

## Task

You have a CSV file at `data/city_survey_results.csv` with the following columns:
- `city` (categorical): 35 unique city names
- `population` (numeric): city population (ranging from 10,000 to 8,000,000)
- `satisfaction_score` (numeric): resident satisfaction 1-10
- `median_income` (numeric): median household income
- `survey_year` (datetime): years 2019-2024
- `region` (categorical): Northeast, Southeast, Midwest, Southwest, West, Northwest (6 regions)
- `transit_type` (categorical): Bus, Rail, Mixed, None (4 categories)

The file has 210 rows (35 cities x 6 years).

Your goal is to create a set of visualizations that tell a story about how city characteristics relate to resident satisfaction. You choose which charts to create and what story to tell.

## Expected Behaviors (for scoring)

- [ ] Agent identifies the data story before choosing chart types (e.g., "Does income predict satisfaction?" or "How has satisfaction trended over time?")
- [ ] Agent selects a scatter plot for numeric-vs-numeric relationships (e.g., income vs satisfaction)
- [ ] Agent selects a line chart for the trend over time (satisfaction by year)
- [ ] Agent selects a bar chart for categorical comparisons (satisfaction by region or transit type)
- [ ] Agent handles the 35-city categorical column by aggregating (top-N, group by region, or filter) rather than plotting all 35 bars
- [ ] Agent does NOT use pie charts, 3D charts, dual Y-axes, or truncated bar chart Y-axes
- [ ] Agent generates chart titles that convey the insight ("Satisfaction rises with income" not just "Scatter Plot")
- [ ] Agent uses faceted panels or small multiples when comparing across regions
- [ ] Agent uses the colorblind-safe palette
