# Baseline: Outlier Detection

## Minimum Acceptable Behavior

A correctly guided agent should:

1. **Test normality first** for each numeric column:
   - `temperature`: Shapiro-Wilk p > 0.05 likely (normal with some spikes) -- though spikes may affect the test
   - `humidity`: Shapiro-Wilk p < 0.05 (right-skewed, non-normal)
   - `pressure`: Shapiro-Wilk p > 0.05 (normal distribution)

2. **Choose method per column**:
   - `temperature`: Z-score (normal distribution, spikes will show as high Z-scores)
   - `humidity`: IQR (skewed data, Z-score would give misleading results)
   - `pressure`: Z-score (normal distribution)
   - If using `--method both` from the script, that is also acceptable as long as the agent interprets results through the correct lens.

3. **Report outliers per column**:
   - `temperature`: ~15 outliers (the sensor_03 spikes at 85-95, clearly outside 3-sigma from mean ~22)
   - `humidity`: Some outliers in the long tail, exact count depends on IQR threshold
   - `pressure`: Few or no outliers expected in a normal distribution with std 5

4. **Interpret results**:
   - Temperature spikes from sensor_03 look like malfunctions (localized to one sensor, extreme deviation) -- likely errors to investigate/remove
   - Humidity tail values may be legitimate environmental readings (not localized to one sensor) -- flag but do not assume error

## Failure Modes

- Applies the same method (e.g., IQR only) to all columns without checking distribution
- Does not run normality test before choosing method
- Reports outlier counts without sample values or context
- Does not distinguish between likely errors (sensor spikes) and natural extreme values (humidity tail)
- Runs outlier detection on `sensor_id` or `reading_time` (non-numeric columns)
