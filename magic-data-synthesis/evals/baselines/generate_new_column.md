# Baseline: Generate New Column

## Minimum Acceptable Agent Behavior

A competent agent given this task and the magic-data-synthesis SKILL.md should:

### Must Do (failure if missing)
1. **Sentinel detection**: Recognize that `tags` contains sentinel values ("TBD", "N/A") AND nulls — this is a `fill-sentinels` scenario, not `fill-missing`
2. **New column handling**: Recognize that `summary` is a new column requiring `transform` mode (all rows need generation)
3. **Preview gate**: Run dry-run or sample-size preview before full synthesis on 2,000 rows
4. **Validation**: Validate synthesized output for both columns

### Should Do (quality indicators)
5. **Correct sentinel patterns**: Configure sentinel patterns to include both "TBD" and "N/A"
6. **Dependency declaration**: Declare that both tags and summary depend on title and body
7. **Agent configs**: Create separate YAML agent configs with task-specific instructions (tagging vs summarization are different tasks)
8. **Cost estimation**: Run --dry-run to estimate total cost across both columns before proceeding
9. **Domain instructions**: Provide format guidance (comma-separated tags; 2-3 sentence summaries)

### May Do (advanced behaviors)
10. **Multi-column config**: Build a single synthesis config with both columns and correct dependency ordering
11. **Different strategies**: Use `llm_text` for summary, potentially `llm_structured` for tags if extracting as a list
12. **Few-shot examples**: Provide example tag sets for common article types
13. **Separate validation criteria**: Code-based for tags (non-empty, comma-separated format) and LLM-as-judge for summaries (accuracy, completeness)

## Anti-Patterns (should NOT do)
- Use `fill-missing` mode for tags (misses the 800 sentinel rows — only processes the 200 nulls)
- Use `fill-missing` mode for summary (it is a new column, not a partially-filled one)
- Skip sentinel pattern configuration (default patterns may not include "TBD")
- Process both columns with identical prompts (tagging and summarization need different instructions)
- Skip the preview gate — 2,000 rows of LLM calls without verification
- Generate tags and summaries using regex/code (these require semantic understanding)
