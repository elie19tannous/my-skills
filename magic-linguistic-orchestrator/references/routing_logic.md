# Routing Logic — Reference

Loaded on demand by the orchestrator when a query is ambiguous or spans multiple skills.

## Single-skill routes (high-confidence)

| Trigger phrase / pattern | Skill |
|---|---|
| "Glottolog", "ISO 639", "Joshi class", "WALS feature", "URIEL", "transfer source", "what languages are similar to X" | scope |
| "NFC", "NFKC", "confusable", "romanize", "transliterate", "diacritic restoration", "Unicode normalization" | scripts |
| "tokenizer fertility", "BPE", "SentencePiece", "byte fallback", "vocab extension", "FOCUS / OFA / HyperOfa" | tokenize |
| "FPIC", "CARE principles", "data sovereignty", "license audit", "attribution", "sacred text" | ethics |
| "OLDI", "CulturaX", "MADLAD-400", "Glot500", "language ID", "GlotLID", "deduplication", "contamination audit" | corpus |
| "LASER3", "SONAR", "Vecalign", "hunalign", "Bleualign", "bitext mining", "parallel corpus" | bitext |
| "MAD-X", "BAD-X", "LoRA", "QLoRA", "Unsloth", "LLaMA-Factory", "Axolotl", "vocabulary expansion", "continued pretraining" | transfer |
| "UniMorph", "SIGMORPHON", "FST", "HFST", "morpheme segmentation", "agglutinative", "polysynthetic" | morph |
| "UD", "Universal Dependencies", "treebank", "parser", "agreement probe", "constituency parse" | syntax |
| "WordNet", "OMW", "FrameNet", "PropBank", "SRL", "semantic role", "MWE", "PARSEME" | semantics |
| "RST", "PDTB", "GUM", "coreference", "discourse marker", "coherence", "rhetorical structure" | discourse |
| "ELAN", "Praat", "FLEx", "Toolbox", "SayMore", "Lhotse", "G2P", "grapheme to phoneme", "IPA", "Whisper", "MMS", "ESPnet" | speech |
| "annotation guidelines", "IAA", "Cohen kappa", "Fleiss", "Krippendorff alpha", "active learning", "adjudication" | annotate |
| "FLORES+", "NTREX", "Belebele", "AfroBench", "IndicXTREME", "SEACrowd", "chrF", "spBLEU", "COMET", "MetricX", "GEMBA-MQM", "BLiMP" | eval |
| "code-switching", "code-mixing", "Hinglish", "Spanglish", "matrix language frame" | codeswitch (optional, may not exist yet) |
| "cognates", "Swadesh list", "sound change", "proto-language", "historical linguistics" | historical (optional) |
| "lexicography", "dictionary building", "sense splitting", "MWE inventory", "lemma" | lexicon (optional) |

## Multi-skill / sequential routes

| User goal | Route order |
|---|---|
| Build LLM for low-resource language | scope → ethics → corpus → scripts → tokenize → bitext → transfer → eval → ethics |
| Fix garbled output for non-Latin script | scripts → tokenize → eval |
| Translate into low-resource language | scope → ethics → bitext → transfer → eval |
| Build a Cantonese model from scratch | scope → ethics → scripts → corpus → tokenize → transfer → eval |
| Process field data (ELAN/FLEx) | speech → annotate → corpus → ethics |
| Annotate a treebank | scope → annotate → syntax |
| Tokenizer audit | scope (resource class) → scripts (normalization) → tokenize (fertility) |
| Quality estimation for an existing model | eval → (refinement to bitext/transfer if needed) |

## Disambiguation question templates

Use AskUserQuestion with at most 4 options + "Other".

**Template 1: Output quality issue**
> "What's the symptom you see for [language] output?"
> - Garbled characters / unknown glyphs → scripts
> - Random/repeated tokens → tokenize
> - Plausible but wrong content → bitext / transfer / eval
> - Slow generation / context-window blowup → tokenize (fertility)

**Template 2: Data ingestion**
> "What kind of source are you starting from?"
> - Web crawl / Common Crawl → corpus
> - Bible / parallel text → bitext
> - Field recordings (audio + ELAN) → speech
> - PDF documents → corpus + (scripts if non-Latin)

**Template 3: Evaluation framing**
> "What does 'evaluate' mean for your project?"
> - MT quality on a benchmark → eval
> - Grammatical knowledge probing → eval (BLiMP-style)
> - Per-dialect / per-register fairness → eval
> - Contamination check → eval

## When to skip routing

- Query is purely conversational ("what's the difference between BPE and unigram?") → answer directly, optionally suggest the relevant skill at the end.
- User has already declared the skill ("/linguistic:tokenize, audit my SentencePiece") → route immediately, skip triage.
- Query is outside linguistic domain ("clean my CSV") → route to magic-data sister suite (`magic-data-cleaning`).

## In-domain, no-skill-matches: decompose + route to nearest skills

**Trigger condition:** the query is in the linguistic domain (mentions a language name, IPA, BPE, FLORES, morphology, etc.) BUT no single skill's trigger pattern in the table above exhaustively covers the request.

Examples of queries that hit this fallback:
- "Build a dialect classifier for Hausa varieties"
- "Help me with language revitalization tooling for Sami"
- "Set up NER training for Yoruba"
- "Build a speech-to-speech translation pipeline for Quechua"

**Procedure (5 steps):**

1. **Decompose** the request into linguistic sub-tasks.
2. **Match each sub-task** to the nearest existing skill from the 18 in the suite.
3. **Label confidence** per match: `high` / `medium` / `low` based on how tightly the skill's triggers cover the sub-task.
4. **Caveat statement:** explicitly state `"no single skill covers this end-to-end; routing N partial matches"` BEFORE listing routes. This prevents overclaiming coverage.
5. **Out-of-suite handoff:** if a sub-task is non-linguistic (e.g., classifier model training, downstream serving infrastructure), recommend handing back to `magic-data-pipelines` or generic Claude.

**Refuse-and-log condition:** if fewer than 2 partial matches can be identified, refuse politely AND append a `## Skill-gap candidate: <one-line query summary>` entry to `workspace_state.md`. Suggest the user file an issue or propose a new skill.

### Worked example

```
Query: "build a dialect classifier for Hausa varieties"

Decomposition:
- variety enumeration + mutual intelligibility   → magic-linguistic-scope (high confidence)
- dialect-balanced corpus acquisition            → magic-linguistic-corpus (medium confidence)
- variety politics + speaker authority           → magic-linguistic-ethics (high confidence)
- classifier model training                      → out of suite — hand back to magic-data-pipelines

Routing decision:
  No single skill covers dialect classification end-to-end. Routing 3 partial matches:
  → magic-linguistic-scope, magic-linguistic-corpus, magic-linguistic-ethics (in that order).
  The classifier training itself is out-of-suite; recommend handing the trained-model step
  back to magic-data-pipelines after this suite finishes the data + ethics pipeline.
```

### Skill-gap candidate logging

When a query gets 0-1 nearest matches, append to `workspace_state.md`:

```
## Skill-gap candidate: <one-line query summary>
- Query: "<verbatim user query>"
- Date: <ISO date>
- Considered skills: <none, or list of <2 partial matches>
- Recommendation: file an issue or propose a new skill (magic-linguistic-<gap-name>)
```

This creates an evidence trail for future skill-gap analysis without silently failing the user.

## Routing logging

Every routing decision should be appended to workspace_state.md under "Skill Routing History":

```
- [2026-04-23T14:32Z] magic-linguistic-tokenize -- task: fertility audit for Yoruba SentencePiece -- result: fertility 3.4 vs 1.8 baseline; recommended OFA vocab extension
```

This enables (a) cross-session resume, (b) audit trail for ethics-gated decisions, (c) regression analysis when an earlier decision needs revisiting.
