---
name: magic-linguistic-orchestrator
description: Start here for any linguistic / NLP / LLM-for-low-resource-language task. Coordinates the 5-phase pipeline (Scope -> Acquire -> Analyze -> Evaluate -> Release) and routes to the right magic-linguistic-* specialist skill. Use whenever the user mentions a target language, asks about training/fine-tuning/adapting an LLM for a non-English language, mentions tokenization fertility, FLORES/Belebele/AfroBench/IndicXTREME/SEACrowd, low-resource MT, language documentation (FLEx/ELAN/Praat), code-switching, dialect data, UD treebanks, IPA/G2P, BPE/SentencePiece for under-represented scripts, or any computational linguistics workflow. Use even if the user does not explicitly say 'linguistics' -- a target language name (Yoruba, Khmer, Quechua, Cantonese, Twi, ...) is a sufficient trigger.
license: Apache-2.0
metadata:
  domain: linguistics
  complexity: high
  requires_llm: false
  phase: 0
  supports_pipeline: true
  supports_generation: false
  entry_point: true
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - low-resource
  - llm
  - orchestration
  - workflow
  - multilingual
  dependencies: []
---

## Natural Language Triggers

Activate this skill's workflow when the user says things like:

- "help me build an LLM for [language]" / "fine-tune for Yoruba/Khmer/Quechua/..."
- "my tokenizer produces garbage for [language]" / "tokenizer fertility is bad"
- "train a Cantonese model" / "low-resource MT" / "translate into Twi"
- "evaluate on FLORES / Belebele / AfroBench / IndicXTREME / SEACrowd"
- "what data exists for [language]?" / "find a parallel corpus for ..."
- "build a tokenizer for an agglutinative / polysynthetic / abugida script language"
- "annotate a treebank" / "do UD parsing for ..." / "discourse analysis on ..."
- "linguistic documentation" / "ELAN / Praat / FLEx export"
- A bare target language name + any ML/NLP verb

These produce the SAME structured behavior as `/linguistic:lifecycle` or `/linguistic:status`. Slash commands are shortcuts -- natural language works equally well.

## When to Use

- User mentions a target language (especially non-English / low-resource) AND any LLM/NLP task.
- User needs the multi-step linguistic pipeline (data, tokenizer, transfer, eval).
- Session needs phase tracking, multi-skill coordination, or workspace state.
- User is unsure which `magic-linguistic-*` specialist to use -- this skill triages.

**When NOT to Use:** A single isolated operation where the specific skill handles it directly (e.g., "just compute fertility for this tokenizer" -> `magic-linguistic-tokenize` directly). Pure data-cleaning with no linguistic content -> `magic-data-cleaning` (sister suite).

## On First Touch

1. **Check workspace** -- if no `workspace_state.md` exists in cwd, create one with: target language(s), Glottolog/ISO code (resolve via `magic-linguistic-scope`), resource class (Joshi 0-5), pipeline phase (start at Scope).
2. **Check ethics gate early** -- before recommending data sources, route to `magic-linguistic-ethics` for FPIC/CARE awareness.
3. **Identify phase** -- map the user's request to one of: Scope / Acquire / Analyze / Evaluate / Release.
4. **Route to specialist(s)** -- never duplicate specialist content; always hand off.

## Phase Indicators (every substantive response)

```
[Phase: Scope | Language: Yoruba (yor) | Resource Class: 2 | Skills routed: scope, ethics]
```

If multiple languages, list the primary; note "+N more" for additional.

## The 5-Phase Pipeline

```
Scope -> Acquire -> Analyze -> Evaluate -> Release
   |        |         |          |           |
   v        v         v          v           v
scope     corpus     morph     eval        ethics
scripts   bitext     syntax              (release gate)
tokenize  transfer   semantics
ethics    (ethics    discourse
(early    gate at    speech
gate)     each       annotate
          dataset)
```

This is NOT a rigid pipeline -- phases overlap and loop back. The orchestrator provides the **skeleton**; the agent provides the **judgment**.

**MANDATORY READ** [`references/pipeline_phases.md`](references/pipeline_phases.md) when first entering any phase, on phase transition, or when the user asks about phase scope/exit criteria. **MANDATORY READ** [`references/routing_logic.md`](references/routing_logic.md) — INCLUDING the **in-domain-no-match fallback** section — when triaging an ambiguous query, picking among multiple specialist candidates, or building the disambiguation question. Queries that are in the linguistic domain but match no single skill MUST decompose + route to ≥2 nearest skills with explicit "partial match" caveat (or refuse-and-log if <2 matches). Do NOT load both for simple status updates -- use them on-demand at decision points.

### Phase: Scope
**Goal:** Identify the target language(s), resource class, typological profile, and constraints. Set the strategic direction.

| Step | What | Specialist Skill |
|------|------|------------------|
| Resolve language | ISO 639-3 + Glottolog code; vitality (UNESCO/EGIDS) | magic-linguistic-scope |
| Resource class | Joshi 0-5 classification; data availability scan | magic-linguistic-scope |
| Typology | WALS / Grambank / URIEL feature lookup; transfer-source recommendation | magic-linguistic-scope |
| Script handling | Unicode block(s), normalization policy, romanization needs | magic-linguistic-scripts |
| Ethics seed | FPIC awareness, community contact paths, sacred-text flags | magic-linguistic-ethics |

**Phase exit criterion:** workspace_state.md has language code, resource class, typology vector, and script policy. User confirms the strategic direction.

### Phase: Acquire
**Goal:** Gather monolingual + bitext data ethically and reproducibly.

| Step | What | Specialist Skill |
|------|------|------------------|
| Monolingual corpora | OLDI / CulturaX / MADLAD-400 / Glot500 / Wikipedia / community sources | magic-linguistic-corpus |
| Parallel data | LASER3/SONAR mining, Vecalign/hunalign/Bleualign alignment | magic-linguistic-bitext |
| Adapter / vocab strategy | FOCUS/OFA/HyperOfa, MAD-X, LoRA configs | magic-linguistic-transfer |
| Script normalization | NFC/NFKC, confusable folding, diacritic restoration | magic-linguistic-scripts |
| Tokenizer audit | Fertility vs English baseline; vocab extension recommendation | magic-linguistic-tokenize |
| Per-dataset ethics | License audit, attribution, sacred-text gating | magic-linguistic-ethics |

**Phase exit criterion:** Reproducible data manifest (sources, licenses, sizes, dedup stats) + tokenizer plan.

### Phase: Analyze
**Goal:** Run linguistic analysis layers needed for evaluation, augmentation, or downstream training.

| Step | What | Specialist Skill |
|------|------|------------------|
| Morphology | UniMorph paradigms, SIGMORPHON segmenters, FST/HFST | magic-linguistic-morph |
| Syntax | UD treebank ingestion, cross-lingual parser transfer | magic-linguistic-syntax |
| Semantics | WordNet/OMW, FrameNet, PropBank-style SRL, MWE/PARSEME | magic-linguistic-semantics |
| Discourse | RST/PDTB/GUM, coreference, discourse markers | magic-linguistic-discourse |
| Speech | ELAN/Praat/FLEx -> Lhotse, G2P, IPA, low-resource ASR/TTS bridge | magic-linguistic-speech |
| Annotation | Guideline authoring, IAA (kappa/alpha/gamma), adjudication | magic-linguistic-annotate |

**Phase exit criterion:** Required analysis artifacts produced (e.g., morphology table for tokenizer audit, treebank for parser transfer eval).

### Phase: Evaluate
**Goal:** Honestly measure performance with metrics fit for the language.

| Step | What | Specialist Skill |
|------|------|------------------|
| Benchmark selection | FLORES+/NTREX/Belebele/AfroBench/IndicXTREME/SEACrowd | magic-linguistic-eval |
| Metric choice | chrF/spBLEU/COMET/MetricX/GEMBA-MQM (avoid BLEU on MRLs) | magic-linguistic-eval |
| Probing | BLiMP-style minimal pairs, agreement probes | magic-linguistic-eval |
| Contamination check | Eval-set overlap with pretrain mix | magic-linguistic-eval |
| Per-dialect / register breakdown | Sociolinguistic stratification | magic-linguistic-eval |

**Phase exit criterion:** Eval report with metric, score, baseline, contamination assessment, error taxonomy.

### Phase: Release
**Goal:** Ship with community-aligned consent and attribution.

| Step | What | Specialist Skill |
|------|------|------------------|
| Final ethics gate | License compliance, community sign-off where required, attribution registry | magic-linguistic-ethics |
| Model card | Document data, training, eval, limits, intended uses | magic-linguistic-ethics |
| Release decision | Open / community-gated / restricted | magic-linguistic-ethics |

## Triage Decision Tree (for ambiguous queries)

| User says... | First route to | Reason |
|---|---|---|
| "garbled output for [lang]" | scripts (Unicode) -> tokenize (fertility) -> eval | Script issues silently break downstream |
| "model is bad at [lang]" | eval (measure first) -> scope (resource class) -> transfer | Quantify before remediating |
| "I have ELAN files" | speech (annotation conversion) -> corpus (data ingestion) | Field-data path |
| "what data exists for X?" | scope (Glottolog) -> corpus (catalog) -> ethics (license) | Always ethics-aware |
| "translate into X" | scope -> bitext (parallel data) -> transfer (model) -> eval | Standard MT |
| "annotate a treebank" | annotate -> syntax (UD) | Annotation comes before analysis |
| "make a tokenizer for X" | scripts -> tokenize -> morph (if MRL) | Script policy first |

## Mid-Pipeline Entry

The orchestrator does NOT require starting at Scope. If the user enters mid-pipeline:

1. **Read workspace_state.md** if present -- catch up on prior decisions.
2. **Backfill missing scope facts** -- if no language code recorded, ask once and resolve via `magic-linguistic-scope`.
3. **Skip phases that are already done** -- record skip rationale in workspace_state.md.
4. **Always run ethics gate at least once** before any Release-phase action.

## Disambiguation

When a query maps to multiple skills, ask ONE clarifying question with up to 4 options. Examples:

- "fix Khmer output" -> Is it (a) garbled characters [scripts], (b) hallucinated tokens [tokenize/transfer], (c) bad translations [bitext/eval]?
- "train on African languages" -> Single language or multi-lingual? Which resource class(es)?

Do not over-disambiguate -- after ONE question, route to a best-guess skill and let the specialist refine.

## Workspace State (mirrors magic-data-lifecycle)

`workspace_state.md` is the orchestrator's memory. Structure:

```markdown
# Linguistic Workspace State

## Targets
- Primary language: <name> (ISO: <code>, Glottolog: <id>)
- Additional languages: ...
- Resource class (Joshi): <0-5>
- Typology vector: <URIEL summary or WALS features>
- Script(s): <Unicode blocks + normalization policy>

## Current Phase: <Scope | Acquire | Analyze | Evaluate | Release>

## Decisions Recorded
- [date] <decision> -- rationale: <...>

## Skill Routing History
- [date] <skill> -- task: <...> -- result: <...>

## Ethics Status
- FPIC required: <yes/no>; community contact: <if applicable>
- Sacred-text gating reviewed: <yes/no>
- License inventory: <link to manifest>

## Open Questions
- [ ] ...
```

Update on every phase transition, decision, or significant skill routing.

## Anti-Patterns (NEVER do)

- **NEVER** recommend a dataset without routing through `magic-linguistic-ethics` first. Even "open" endangered-language data may violate community norms despite legal permission.
- **NEVER** report a BLEU score for a morphologically-rich language as the primary metric. BLEU on MRLs penalizes single-morpheme edits as harshly as full mistranslations -- use chrF++ / spBLEU / COMET as primary.
- **NEVER** apply NFKC normalization without checking the script policy. NFKC collapses long-s, ligatures, and presentation forms -- destructive for historical text and Arabic.
- **NEVER** assume Joshi class 5 (English-like) workflows transfer to class 0-2. Vocabulary extension, adapter routing, and eval metric choice all change.
- **NEVER** skip ethics in mid-pipeline entries even if "the user is in a hurry". A 30-second FPIC check saves a community-relations incident.
- **NEVER** route to multiple Analyze-phase skills in parallel without confirming the user wants all outputs -- analysis is expensive and easily over-scoped.
- **NEVER** delete or overwrite `workspace_state.md` without snapshotting the prior version into `logs/`.

## Edge Cases

- **No workspace_state.md, no clear target language:** ask once, resolve via `magic-linguistic-scope`, then proceed.
- **Multiple target languages (multilingual model):** record all, pick a primary for routing decisions, escalate to scope+transfer for sampling-weight design.
- **Very high-resource language (English/Mandarin/Spanish):** orchestrator still routes, but specialists will note that low-resource heuristics may not apply.
- **Endangered / sleeping language:** route to ethics FIRST (FPIC essential); scope second; data sources may be archive-only (DELAMAN/ELAR).
- **User wants to skip ethics:** politely decline; explain that the orchestrator's pre-merge gate requires it.

## Discovery Environment

This orchestrator coordinates 12 core + 3 optional `magic-linguistic-*` specialist skills. It owns the pipeline shape and routing decisions; it does NOT own domain content. When in doubt about *what* to do, route to a specialist. When in doubt about *which* specialist, consult the Triage Decision Tree above.
