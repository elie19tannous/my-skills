# Baseline: Basic Pattern Detection

## Expected Agent Behavior

### Minimum Requirements

1. **Runs pattern detection**: Agent uses `detect_patterns.py` or generates equivalent code that detects variance, correlations, and outliers across numeric columns (`units_sold`, `revenue`, `discount_pct`).

2. **Reports with confidence levels**: Each finding includes a confidence level (high/medium/low) based on statistical strength, not just presence.

3. **Uses uncertainty language**: Findings use hedging language such as "may indicate", "appears to show", "suggests a pattern" rather than definitive claims like "proves" or "causes".

4. **Identifies at least one pattern**: Agent detects at least one of:
   - High variance in `revenue` or `units_sold`
   - Temporal patterns in `date` (weekly/monthly cycles)
   - Distribution anomalies in `discount_pct`
   - Differences across `region` or `product` segments

5. **No causation claims**: Agent does not claim that one variable causes changes in another. Correlations are reported as associations, not causal relationships.

### Quality Indicators

- Agent suggests next steps (e.g., "run segment analysis by region to see if this pattern holds across groups")
- Agent mentions the possibility that observed patterns may be artifacts of sample composition
- Agent considers whether patterns are practically significant, not just statistically significant
