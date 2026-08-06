# Eval: Outlier Detection

## Task

You have a dataset at `data/sensor_readings.csv` with 2,000 rows and these columns:
- `sensor_id` (string, 10 unique sensors)
- `temperature` (float, normally distributed around 22.0 with std 2.5, but sensor_03 has 15 readings spiking to 85-95)
- `humidity` (float, right-skewed distribution, range 30-95 with a long tail)
- `pressure` (float, normally distributed around 1013 with std 5)
- `reading_time` (datetime string)

Detect and report outliers across all numeric columns. Choose the appropriate outlier detection method for each column based on its distribution.

## Expected Behaviors (for scoring)

- [ ] Agent runs a normality test (Shapiro-Wilk or similar) on each numeric column before choosing detection method
- [ ] Agent uses Z-score for `temperature` and `pressure` (normally distributed)
- [ ] Agent uses IQR for `humidity` (right-skewed, non-normal distribution)
- [ ] Agent identifies the sensor_03 temperature spikes as clear outliers
- [ ] Agent reports outlier count, percentage, and sample values for each column
- [ ] Agent does NOT blindly apply the same method to all columns
- [ ] Agent discusses whether outliers are errors vs legitimate extreme values (the sensor spikes look like malfunctions, the humidity tail may be natural)
