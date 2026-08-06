# Baseline: Fill Missing Values

## Minimum Acceptable Agent Behavior

A competent agent given this task and the magic-data-synthesis SKILL.md should:

### Must Do (failure if missing)
1. **Feasibility check**: Recognize that product description generation requires contextual understanding of name + category, confirming LLM synthesis is appropriate (not regex/code)
2. **Correct mode**: Use `fill-missing` mode since values are NaN/null (not sentinel strings)
3. **Preview before scale**: Run on a subset (sample-size) or dry-run before processing all 500 rows
4. **Validation**: Run validation on the output to verify quality

### Should Do (quality indicators)
5. **Agent config**: Create a YAML agent config with clear instruction text for description generation
6. **Dependencies**: Declare `depends_on` with context columns (name, category, and optionally price)
7. **Cost awareness**: Set `--max-cost` or at minimum estimate cost before full run
8. **Quality metadata**: Output includes `_synthesis_confidence` and other metadata columns

### May Do (advanced behaviors)
9. **Few-shot examples**: Provide example descriptions for common categories
10. **Custom validation criteria**: Configure LLM-as-judge rubric for description quality
11. **Checkpoint naming**: Use conventional checkpoint naming (ckpt_05_synthesized.csv)

## Anti-Patterns (should NOT do)
- Use `fill-sentinels` mode for NaN values (wrong mode — zero fills)
- Use `transform` mode (would regenerate existing descriptions too)
- Skip the preview/dry-run gate and go straight to full synthesis
- Skip validation entirely
- Use regex or pandas string operations (these cannot generate descriptions)
- Instantiate LlmAgent directly instead of using build_agent()
