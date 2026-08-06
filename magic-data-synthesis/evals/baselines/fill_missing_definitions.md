# Baseline: Fill Missing Definitions (DataDesigner)

## Minimum Acceptable Agent Behavior

### Must Do (failure if missing)
1. **Feasibility check**: Recognize that description generation requires contextual understanding — not a regex/code task
2. **DataDesigner selection**: Use DataDesigner CLI (not legacy batch_synthesize.py) as the synthesis engine
3. **Preview before scale**: Run `data-designer preview --num-records 5` before full synthesis
4. **PAUSE gate**: Present preview results and cost estimate to user before `create`
5. **Validation**: Verify output has non-empty descriptions after synthesis

### Should Do (quality indicators)
6. **Template usage**: Copy and adapt a template from `templates/` rather than writing config from scratch
7. **Config validation**: Run `data-designer validate` before preview
8. **Prompt quality**: Reference seed columns ({{ text }}, {{ category }}, {{ label }}) in the prompt
9. **Checkpoint**: Save output as MAGIC checkpoint with provenance metadata
10. **Cost awareness**: Compute or acknowledge cost estimate (local models = $0, cloud = estimate)

### May Do (advanced behaviors)
11. **Model selection**: Choose between local (LM Studio) and cloud (Gemini) based on speed/cost tradeoff
12. **Quality scoring**: Add LLMJudge column for description quality evaluation
13. **Few-shot examples**: Include example descriptions in the prompt

## Anti-Patterns (should NOT do)
- Use `batch_synthesize.py` as the primary engine (it's legacy reference only)
- Skip the preview gate and run full synthesis immediately
- Create a YAML agent config (old workflow — DataDesigner uses Python configs)
- Use `fill-missing` or `fill-sentinels` mode flags (DataDesigner doesn't use these)
- Skip validation entirely
- Hardcode descriptions or use regex (defeats the purpose of LLM synthesis)
