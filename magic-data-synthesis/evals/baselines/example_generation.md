# Baseline: Example Summary Generation

## Minimum Acceptable Agent Behavior

### Must Do (failure if missing)
1. **Sentinel detection**: Identify "X" as a placeholder/sentinel (not treat as valid content)
2. **Contextual output**: Configure prompt to produce contextually appropriate summaries
3. **Preview verification**: Run preview and confirm output quality before scaling
4. **PAUSE gate**: Show cost + samples before full generation
5. **Selective replacement**: Only replace "X" rows — don't overwrite existing valid examples

### Should Do (quality indicators)
6. **DataDesigner usage**: Use DD CLI workflow (validate → preview → create)
7. **Context columns**: Include text, category, label, description as context in prompt
8. **Quality check**: Verify generated summaries are coherent and on-topic
9. **Checkpoint**: Save with metadata tracking which rows were generated
10. **Cost estimate**: Acknowledge cost (local = $0, Gemini Flash ≈ $0.002 for 85 rows)

### May Do (advanced behaviors)
11. **Length check**: Ensure generated summaries are within expected length range
12. **LLMJudge**: Add quality scoring (fluency, relevance, coherence)
13. **Extract reasoning**: Use `extract_reasoning_content=True` if using reasoning model

## Anti-Patterns (should NOT do)
- Overwrite existing valid examples (only replace "X" sentinels)
- Skip preview — output quality MUST be verified before scaling
- Use `fill-missing` mode (the values are "X" strings, not NaN)
- Use batch_synthesize.py as primary engine
