# Recipe Patterns — When to Use Which Template

## Template Decision Table

| Input shape | Goal | Template |
|---|---|---|
| **Existing data with missing/sentinel values** | Fill/enrich columns (definitions, translations, annotations) | `text_generation_template.py` (local) or `text_generation_gemini_template.py` (cloud) |
| Q&A seed CSV (`question`, `answer`) | Chain-of-thought reasoning traces | `reasoning_trace_template.py` |
| Document/passage seed | Grounded Q&A pairs | `qa_generation_template.py` |
| No seed (sampler-driven) | Open-domain Q&A | `qa_generation_template.py` |
| No seed, task diversity needed | Instruction-following dataset (Alpaca/ShareGPT) | `instruction_tuning_template.py` |
| No seed, code tasks | Python/SQL generation with validation | `code_generation_template.py` |
| Anything else | Custom schema, multi-modal, agent traces, etc. | `custom_recipe_template.py` |

**Quick pick by speed:**
- Fast iteration / CI testing → `text_generation_gemini_template.py` (Gemini, ~2 rec/s)
- Privacy / offline / free → `text_generation_template.py` (local LM Studio, ~0.1 rec/s)

## Template Summaries

### `reasoning_trace_template.py`
**Use for:** Nemotron-style chain-of-thought datasets where an existing Q&A corpus is the seed.

Key columns: seed `question`/`answer` → sampler `difficulty`/`domain` → LLM `reasoning_trace` → LLM `final_answer` → `LLMJudgeColumn` (ReasoningQuality + AnswerCorrectness) → Expression score extractions.

Cost profile: ~3,500 tokens/row combined. Most expensive template — CoT output is verbose.

Pitfalls:
- Use `SamplingStrategy.SHUFFLE` to avoid clustering by seed order.
- Guard judge score extraction: `{{ col.ScoreName.score if col.ScoreName.score is not none else 0 }}`
- Avoid seed column name collisions with sampler columns (`difficulty`, `domain`).

### `qa_generation_template.py`
**Use for:** Generating question-answer pairs from source documents, or open-domain Q&A via samplers.

Context-grounded variant: seed = passages/contexts → LLM `question` → LLM `answer` → judge (Groundedness + Completeness).

Open-domain variant: replace seed with `CategorySampler` for topic/domain, then generate both question and answer.

Cost profile: ~2,000 tokens/row average.

### `instruction_tuning_template.py`
**Use for:** Alpaca/ShareGPT-style `instruction + input + output` triplets with diverse task coverage.

Key technique: `SUBCATEGORY` sampler for coherent domain→task pairings. `BERNOULLI` `has_input` flag controls whether an input field exists per row. Use `{% if has_input == 1 %}` in prompts to conditionalize.

Cost profile: ~2,000 tokens/row average (input column generated for ~60% of rows).

### `code_generation_template.py`
**Use for:** Python or SQL code generation with correctness validation.

Key columns: sampler `industry_sector` → subcategory `topic` → sampler `code_complexity` → LLM `instruction` → `LLMCodeColumn` (strips markdown fences automatically) → `LLMJudgeColumn` (Relevance/Pythonic/Readability/Efficiency) → `ValidationColumn` (ruff linter, zero LLM cost).

Cost profile: ~1,500 tokens/row. `ValidationColumn` has zero LLM cost.

Pitfalls:
- Use `LLMCodeColumnConfig`, not `LLMTextColumnConfig`, for generated code.
- Set `ValidationColumn.batch_size=100` for runs > 1,000 rows (default is 10).
- SQL: use dialect-specific `CodeLang.SQL_SQLITE` / `SQL_POSTGRES`.

### `custom_recipe_template.py`
**Use for:** Any schema that doesn't fit the four above — novel tasks, multi-modal, agent traces, structured JSON output.

Start here when: output is not text/code/Q&A, you need `LLMStructuredColumnConfig` with a Pydantic `output_format`, or you need `@dd.custom_column_generator` for deterministic logic.

Pitfalls:
- `@dd.custom_column_generator` decorator is **mandatory** for `CustomColumnConfig`.
- `side_effect_columns` must be declared in the decorator for any column the generator writes beyond its own name.
- `output_format` takes a **Pydantic class**, not an instance.

## Axes-of-Diversity Mental Model

Every recipe needs variation along at least two axes to produce a useful training set:

1. **Content axis** — what the data is about (seed rows, `CategorySampler`, `SubcategorySampler`)
2. **Style/format axis** — how it is expressed (difficulty, tone, `answer_format_hint`, `PersonSampler`)
3. **Quality axis** — signal for filtering (`LLMJudgeColumn` scores, `ValidationColumn`)

If your recipe only varies on one axis, add a sampler column for a second.

## Column Execution Order

DataDesigner executes columns in DAG order (topological sort, insertion-order tiebreak):

```
SeedDataset columns (auto, no deps)
  → SamplerColumns (no deps)
    → LLMTextColumns (reference seed + sampler outputs)
      → LLMJudgeColumns (reference LLM outputs)
        → ExpressionColumns (extract scores from judge dicts)
          → ValidationColumns (operate on LLM/Code columns)
```

Always define columns in this order. A column can only reference columns defined before it.

## DataDesigner Recipe Patterns (from NeMo recipes)

Proven, citable patterns from DataDesigner's own recipes; source: `research/datadesigner/00-FINAL §5`.
Each pattern is directly implementable via DD config — no custom pipeline code required.

---

### Pattern 1 — Full ChatML trajectory capture as the training datum

**What it is:** Set `with_trace=dd.TraceType.ALL_MESSAGES` on any LLM column. DD automatically
creates a side-effect column `{column_name}__trace` containing the complete conversation history
(system / user / assistant / tool roles) as a `list[dict]` in standard ChatML format. The trace,
not the final answer string, is the training datum.

**When to use it:** Any agentic or tool-use SFT dataset where the *trajectory* — the sequence of
tool calls, tool results, and intermediate reasoning — is what you want the model to learn from.
Also useful for debugging prompt rendering.

**DD mechanism:** `with_trace=dd.TraceType.ALL_MESSAGES` parameter on `LLMTextColumnConfig`,
`LLMCodeColumnConfig`, `LLMStructuredColumnConfig`, or `LLMJudgeColumnConfig`.

```python
builder.add_column(
    dd.LLMTextColumnConfig(
        name="answer",
        prompt="Use tools as needed to answer: {{ question }}",
        model_alias="...",
        tool_alias="my-tools",
        with_trace=dd.TraceType.ALL_MESSAGES,   # trace column: answer__trace
    )
)
```

**Empirical result:** The trace output is in ChatML / OpenAI messages format and is ready for
direct SFT training without additional transformation (see `04-agent-rollout-and-tool-use-mcp.md`,
Notable Detail 7).


---

### Pattern 2 — Rejection sampling on judge score + trajectory length

**What it is:** After generating trajectories, add an `LLMJudgeColumnConfig` to score each output,
then derive a boolean `recommended_for_sft` filter column. Separately, use trajectory
message-count as a near-free quality signal: shorter trajectories correlate with correctness.

**When to use it:** RL/RLHF data pipelines; any recipe where you generate multiple candidates and
want to retain only high-signal examples. The trajectory-length filter is especially effective for
multi-hop research or reasoning tasks.

**DD mechanism:**
- `LLMJudgeColumnConfig` → one judge score per quality dimension.
- `ExpressionColumnConfig` to derive `recommended_for_sft`: `True` only when all scores ≥ threshold.
- `ExpressionColumnConfig` (or `CustomColumnConfig`) on `message_count` for length filter.

```python
# Boolean filter derived from judge scores
builder.add_column(
    dd.ExpressionColumnConfig(
        name="recommended_for_sft",
        expr="{{ correctness.correct >= 1 and message_count <= 35 }}",
    )
)
```

**Empirical result (MuSiQue 2–4 hop, Deep Research recipe):**
Correct trajectories average 31 messages vs. 67 for incorrect ones (Claude Opus 4.5 on MuSiQue).
Filtering by message count is nearly as effective as a judge model at a fraction of the cost
(see `04-agent-rollout-and-tool-use-mcp.md` §Observed Trajectory Statistics).


---

### Pattern 3 — Specialist multi-judge architecture

**What it is:** Instead of one omnibus judge, deploy N independent `LLMJudgeColumnConfig` columns,
each assessing a different quality dimension with its own rubric. Use separate
`ExpressionColumnConfig` columns to extract each score. The Nemotron-Super SQL recipe uses
5 judges × 3 dimensions = 15 independent signals.

**When to use it:** Any recipe where quality has multiple independent axes (e.g., correctness,
relevance, code style, faithfulness, training utility). Multiple independent judges avoid position
bias and produce separately filterable signals — you can, for example, drop on faithfulness alone
without discarding otherwise high-quality examples.

**DD mechanism:** One `LLMJudgeColumnConfig` per dimension (or per judge), each with its own
`scores=[]` list. Each judge can use a different `model_alias` for adversarial diversity.

```python
builder.add_column(
    dd.LLMJudgeColumnConfig(
        name="judge_groundedness",
        model_alias="judge-a",
        prompt="Evaluate groundedness: ...",
        scores=[dd.Score(name="groundedness", description="...", options={0: "No", 1: "Partial", 2: "Yes"})],
    )
)
builder.add_column(
    dd.LLMJudgeColumnConfig(
        name="judge_faithfulness",
        model_alias="judge-b",
        prompt="Evaluate faithfulness: ...",
        scores=[dd.Score(name="faithfulness", description="...", options={0: "No", 1: "Yes"})],
    )
)
```

**Empirical result:** The Agent Rollout Distillation recipe uses 5 quality dimensions
(groundedness, standalone_task, response_quality, faithfulness, training_utility) with per-score
thresholds; `recommended_for_sft` requires all five ≥ 4 (see `04-agent-rollout-and-tool-use-mcp.md`
§Recipe 1, step 3).

**Cross-links:** Pattern applies across all stages; primary reference in methodology eval section
(see `00-FINAL §5` pattern 3).

---

### Pattern 4 — Controlled hallucination via Bernoulli gate

**What it is:** Add a Bernoulli sampler column (`SamplerColumnConfig` with
`sampler_type=SamplerType.BERNOULLI`, e.g. `is_hallucination`, p=0.3) then
use a Jinja conditional in the LLM prompt to produce either a factual or a deliberately
hallucinated answer on each row. The flag is retained as a label for training hallucination
detectors or preference models.

**When to use it:** Safety / alignment datasets; building hallucination-detection or fact-checking
training sets; any recipe that needs a controlled factual/non-factual binary split across rows.

**DD mechanism:** `SamplerColumnConfig` with `BernoulliSamplerParams` → Jinja `{% if %}` in the
LLM prompt column.

```python
builder.add_column(
    dd.SamplerColumnConfig(
        name="is_hallucination",
        sampler_type=dd.SamplerType.BERNOULLI,
        params=dd.BernoulliSamplerParams(p=0.3),
    )
)
builder.add_column(
    dd.LLMTextColumnConfig(
        name="answer",
        prompt=(
            "{% if is_hallucination == 1 %}"
            "Provide a plausible-sounding but factually incorrect answer to: {{ question }}"
            "{% else %}"
            "Provide an accurate, grounded answer to: {{ question }}"
            "{% endif %}"
        ),
        model_alias="...",
    )
)
```

**Empirical result:** Generalizes to any binary treatment split — factual/hallucinated,
safe/unsafe, helpful/unhelpful — using the same Bernoulli gate pattern (see `00-FINAL §5`
pattern 4).

---

### Pattern 5 — Distractor injection

**What it is:** For SQL / table-grounded Q&A recipes, add 1–2 irrelevant tables and 3–5 distractor
columns alongside the relevant tables in the prompt. This forces the model to discriminate between
relevant and irrelevant schema elements during generation, producing harder and more realistic
training examples.

**When to use it:** SQL generation, table QA, schema-grounded NLU tasks. Do not use when seed data
is already sparse — distractors require sufficient schema breadth in the seed.

**DD mechanism:** Typically implemented via `LLMStructuredColumnConfig` or `ExpressionColumnConfig`
to assemble the schema context, combined with `SamplerColumnConfig` to select distractor
tables/columns from a pool. See `00-FINAL §5` pattern 5 and Nemotron-Super SQL recipe for exact
column arrangement.

**Empirical result:** +15 percentage-point improvement on the BIRD benchmark accuracy in the
Nemotron-Super SQL recipe (see `00-FINAL §5` pattern 5).

---

### Pattern 6 — Qualifier-lock / slot-binding

**What it is:** When generating multi-step or comparative questions, pin the question's referents
(year, metric, subgroup, entity) explicitly into the answer-generation prompt — not just the
question prompt. This prevents "silent substitution" where the model silently replaces the correct
referent with a plausible one in its answer.

**When to use it:** Multi-step QA, time-series questions, metric-comparison tasks, any recipe
where the question specifies a precise qualifier (e.g., "in Q3 2024", "for the 18–24 age group",
"using GAAP revenue") that must be respected in the answer.

**DD mechanism:** `ExpressionColumnConfig` to extract and name the qualifier slot explicitly, then
pass it as a named variable into the downstream `LLMTextColumnConfig` prompt template.

```python
builder.add_column(
    dd.ExpressionColumnConfig(
        name="locked_year",
        expr="{{ question | regex_search('\\b(20\\d\\d)\\b') | first }}",
    )
)
builder.add_column(
    dd.LLMTextColumnConfig(
        name="answer",
        prompt=(
            "Answer the question for the year {{ locked_year }} specifically.\n"
            "Question: {{ question }}"
        ),
        model_alias="...",
    )
)
```

**Empirical result:** Reduces answer drift in multi-hop QA; described as a quality-critical
technique in the Nemotron-Super SQL and multi-hop research recipes (see `00-FINAL §5` pattern 6).

---

### Pattern 7 — `drop=True` scaffolding columns

**What it is:** Mark intermediate "scaffolding" columns — chain-of-thought steps, schema summaries,
draft answers, context expansions — with `drop=True`. DD will generate these columns in DAG order
so downstream columns can reference them, but will exclude them from the final output parquet/JSONL.
The dropped columns are preserved in a separate `dropped-columns/` artifact directory.

**When to use it:** Any multi-column recipe that uses intermediate LLM outputs as generation
scaffolding but does not want those columns in the final training dataset. Keeps the output schema
clean without a separate cleanup stage.

**DD mechanism:** `drop=True` parameter on any column config. Equivalent to adding a
`DropColumnsProcessorConfig` for that column, but co-located with the column definition.

```python
builder.add_column(
    dd.LLMTextColumnConfig(
        name="answer_draft",        # scaffolding — used by answer_final, not needed in output
        prompt="Draft a rough answer to: {{ question }}",
        model_alias="...",
        drop=True,                  # excluded from final dataset; saved to dropped-columns/
    )
)
builder.add_column(
    dd.LLMTextColumnConfig(
        name="answer_final",
        prompt="Improve this draft: {{ answer_draft }}\nQuestion: {{ question }}",
        model_alias="...",
    )
)
```

**Empirical result:** Standard operational pattern across all NeMo DD recipes; see `03-processors-
workflow-chaining-traces.md` §Drop Columns Processor.

---

### Pattern 8 — Two-stage question obfuscation

**What it is:** Generate question text in two LLM passes: the first pass drafts the question
(possibly with explicit references to the source document, table name, or entity that "gives away"
the answer); the second pass rewrites the draft to remove those breadcrumbs, producing a harder
question that requires genuine reasoning rather than keyword matching.

**When to use it:** Hard search / retrieval datasets; agent benchmark data; any recipe where
you want questions that do not trivially reveal the answer through surface overlap with the source.

**DD mechanism:** Two sequential `LLMTextColumnConfig` columns — `question_draft` (with `drop=True`)
and `question` — where the second column references the draft:

```python
builder.add_column(
    dd.LLMTextColumnConfig(
        name="question_draft",
        prompt="Write a question about: {{ context }}",
        model_alias="...",
        drop=True,
    )
)
builder.add_column(
    dd.LLMTextColumnConfig(
        name="question",
        prompt=(
            "Rewrite this question to remove any direct references to source documents, "
            "table names, or entities that reveal the answer:\n{{ question_draft }}"
        ),
        model_alias="...",
    )
)
```

**Empirical result:** Used in the Deep Research Trajectories recipe and Nemotron search-agent
recipes to ensure generated questions require multi-hop retrieval (see `04-agent-rollout-and-tool-
use-mcp.md` §Recipe 3 and `00-FINAL §5` pattern 8).

---

### Pattern 9 — JSON-repair normalization column

**What it is:** Add a dedicated `LLMStructuredColumnConfig` pass immediately after any column that
produces semi-structured or fragile JSON output. The normalization column receives the raw output
and a Pydantic schema, and DD's structured-output engine guarantees a schema-valid result.

**When to use it:** Any recipe where an upstream `LLMTextColumnConfig` is expected to output JSON
but may produce malformed output (missing fields, extra prose, wrong types). Also useful after
`AgentRolloutSeedSource` ingestion to normalize heterogeneous trace metadata.

**DD mechanism:** `LLMStructuredColumnConfig` with `output_format=MyPydanticModel`. The column
receives the raw text as a prompt variable and returns a guaranteed-valid Pydantic-typed dict.

```python
from pydantic import BaseModel

class NormalizedRecord(BaseModel):
    instruction: str
    response: str
    difficulty: str

builder.add_column(
    dd.LLMTextColumnConfig(
        name="raw_output",
        prompt="Generate a training record as JSON: ...",
        model_alias="...",
        drop=True,
    )
)
builder.add_column(
    dd.LLMStructuredColumnConfig(
        name="record",
        prompt="Parse and repair this JSON into the required schema:\n{{ raw_output }}",
        model_alias="...",
        output_format=NormalizedRecord,     # Pydantic class (not instance)
    )
)
```

**Empirical result:** Standard repair pattern used in the Agent Rollout Distillation recipe's
`trace_digest` and `sft_record` columns (see `04-agent-rollout-and-tool-use-mcp.md` §Recipe 1);
generalizes to any semi-structured upstream output. Note: `output_format` takes a **Pydantic class**,
not an instance.

---

### Pattern 10 — Persona-seeding for diversity

**What it is:** Seed each row with a sampled persona describing "who is asking" — their role,
goal, communication style, technical level, locale — so that the generated question/instruction
varies in tone and framing across the dataset rather than converging to a single register.
DataDesigner provides two persona primitives: `PersonFromFaker` (zero-setup, any Faker locale)
and the `PersonSampler` / Nemotron-Personas (9 locales, ~53 M census-grounded personas with
OCEAN traits and domain personas).

**When to use it:** Any SFT, instruction-following, safety, or preference dataset where stylistic
and demographic diversity is required. Especially important for post-training data (instruction
following, safety/refusal, tool use) where a single "assistant voice" leads to mode collapse.

**DD mechanism:** `SamplerColumnConfig` with `PersonSamplerParams` or `PersonFromFakerParams`,
then reference the persona fields in downstream `LLMTextColumnConfig` prompt templates.

```python
# Zero-setup Faker personas
builder.add_column(
    dd.SamplerColumnConfig(
        name="persona",
        sampler_type=dd.SamplerType.PERSON_FROM_FAKER,
        params=dd.PersonFromFakerSamplerParams(locale="en_US"),
    )
)
# Or Nemotron-Personas (census-grounded, OCEAN traits)
builder.add_column(
    dd.SamplerColumnConfig(
        name="persona",
        sampler_type=dd.SamplerType.PERSON,
        params=dd.PersonSamplerParams(locale="en_US"),
    )
)
builder.add_column(
    dd.LLMTextColumnConfig(
        name="question",
        prompt=(
            "Write a question as if you are {{ persona.name }}, "
            "a {{ persona.occupation }} asking about {{ topic }}."
        ),
        model_alias="...",
    )
)
```

**Empirical result:** Used across Nemotron post-training pipelines (SFT, safety/refusal,
instruction-following, tool-use rollouts) as the primary diversity primitive. Without persona
seeding, repeated generation over the same seed converges to a narrow register and vocabulary
distribution (see `00-FINAL §3.4` and `00-FINAL §5` pattern 10).

