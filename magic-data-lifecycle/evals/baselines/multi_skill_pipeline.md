# Baseline: Multi-Skill Pipeline

## Minimum Acceptable Behavior

An agent WITHOUT the lifecycle skill would typically:
- Write a single Python script that handles all three operations (fill text, remove sentinels, normalize dates) in one pass
- Not distinguish between deterministic operations (cleaning) and semantic operations (synthesis)
- Apply LLM to everything, or apply regex to everything — no routing judgment
- Not define success criteria upfront — just run transforms and report what changed
- Not validate after cleaning — assume the operations worked

## With-Skill Expected Improvements

An agent WITH the lifecycle skill should:
1. **Operation classification** — distinguish cleaning (deterministic: dates, sentinels, dedup) from synthesis (semantic: filling review_text) and route accordingly
2. **Correct skill routing** — date normalization → magic-data-cleaning, sentinel removal → magic-data-cleaning, text fill → magic-data-synthesis, dedup → magic-data-cleaning
3. **Success criteria first** — define measurable targets before executing (null rate < X%, zero sentinels, all dates ISO)
4. **Sequencing** — clean deterministic issues first, then synthesize into clean data. Don't synthesize review text for rows that will be dropped as duplicates.
5. **Post-execution validation** — re-profile or validate to confirm success criteria are met

## Key Differentiators

The critical distinction is between cleaning and synthesis. Without the skill, an agent treats everything as a pandas operation or everything as an LLM task. The lifecycle skill teaches the agent that deterministic operations (regex, type casting, dedup) go to cleaning, while semantic operations (generating text, translation) go to synthesis. This routing decision affects cost (LLM calls are expensive), quality (regex is more reliable for date parsing), and pipeline ordering (clean before synthesize).
