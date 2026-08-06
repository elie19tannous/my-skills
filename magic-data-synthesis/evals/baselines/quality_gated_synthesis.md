# Baseline: Quality-Gated Synthesis with LLM Judge

## Minimum Acceptable Agent Behavior

### Must Do (failure if missing)
1. **Dual-column config**: Recipe has BOTH a text generation column AND an LLMJudge column
2. **Meaningful rubrics**: Judge scores defined with domain-specific criteria (not just "quality: good/bad")
3. **Quality extraction**: Use `extract_dd_quality()` or parse judge output to get scores
4. **Threshold check**: Compare scores against 70% threshold and report pass/fail
5. **PAUSE gate**: Show preview with BOTH generated text and quality scores

### Should Do (quality indicators)
6. **Multi-rubric**: At least 2 rubrics (e.g., accuracy + completeness or accuracy + register)
7. **Iterate on failure**: If quality < 70%, modify prompt/few-shot and re-preview
8. **Post-generation filter**: Remove or flag rows below threshold
9. **Quality report**: Present mean_100, pass_rate, histogram to user
10. **Checkpoint after gate**: Only save to MAGIC checkpoint after quality passes

### May Do (advanced behaviors)
11. **Domain-aware scoring**: Different rubrics or thresholds for "daily" vs "technical" words
12. **Few-shot refinement**: Add example definitions as Jinja context to improve quality
13. **Multiple runs**: Run 2-3 times and aggregate scores for stability
14. **Cost tracking**: Report total cost including judge calls

## Anti-Patterns (should NOT do)
- Skip quality scoring entirely and checkpoint raw output
- Use generic rubrics ("quality: 1-5") without descriptions
- Accept output below 70% threshold without iteration
- Put judge in a separate pipeline run (DD handles it in one pass)
- Use validate_synthetic.py instead of DD's built-in judge (DD judge is more integrated)
