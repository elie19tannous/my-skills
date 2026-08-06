# Pipeline Phases — Reference

Detailed reference for the 5-phase linguistic pipeline. Loaded on demand by the orchestrator when the user requests phase-level detail or transitions between phases.

## Why 5 phases (not magic-data's 5 Discover/Plan/Execute/Validate/Deliver)

The linguistic pipeline is data-and-model-shaped, not data-only. It collapses magic-data's Discover+Plan into Scope (strategic up-front decisions), folds Execute and Validate into the bidirectional Acquire/Analyze/Evaluate triad (linguistic work iterates between them), and renames Deliver to Release (community sign-off is heavier than a data hand-off).

| magic-data | magic-linguistic | Reason |
|---|---|---|
| Discover | Scope | Linguistic scoping is more strategic (typology, resource class, ethics seed) than discovery (profile data) |
| Plan | (in Scope) | Plan emerges from Scope; not a separate phase |
| Execute | Acquire + Analyze | Linguistic execution splits into data vs analysis layers |
| Validate | Evaluate | Renamed; same role |
| Deliver | Release | Community/ethics layer is heavier |

## Phase: Scope (deep dive)

**Inputs:** user request mentioning a language or NLP task.
**Outputs:** workspace_state.md populated with language(s), Glottolog code, resource class, typology, script policy, ethics seed.

**Mandatory steps:**
1. Resolve language name to ISO 639-3 + Glottolog ID. Do NOT proceed with ambiguous strings (e.g. "Chinese" — clarify to Mandarin/yue/wuu/...).
2. Look up resource class (Joshi 2020). Class 0-2 require radically different workflows than class 3-5.
3. Pull typology vector from WALS/Grambank/URIEL. Identify top 3 typologically-similar transfer-source languages.
4. Determine script policy: Unicode blocks involved, normalization (NFC vs NFKC), confusable risk, romanization needs.
5. Surface ethics flags: is the language community known to have data-sovereignty norms? Sacred-text presence? Endangered status?

**Common scope-phase mistakes:**
- Treating dialects as a single language (Cantonese vs Mandarin vs Hakka — all "Chinese" in some catalogs but require separate scope).
- Skipping URIEL lookup and assuming English is a good transfer source for everything.
- Defaulting NFKC without script-policy review.

## Phase: Acquire (deep dive)

**Inputs:** scope-phase outputs.
**Outputs:** data manifest (monolingual + parallel + alignment), tokenizer plan, adapter/vocab strategy.

**Mandatory steps:**
1. Pull catalogs from `magic-linguistic-corpus` (OLDI, CulturaX, MADLAD-400, Glot500, regional community sources).
2. For MT: design parallel-data strategy via `magic-linguistic-bitext`. Class 0-2 may need Bible-text bootstrapping; class 3-5 may use NLLB-style mining.
3. Run `magic-linguistic-scripts` normalization audit on raw data BEFORE tokenizer training.
4. Run `magic-linguistic-tokenize` fertility audit on existing/baseline tokenizer; recommend vocab extension if fertility > 3.0 vs English.
5. Per-dataset ethics check via `magic-linguistic-ethics` (license, attribution, sacred-text, FPIC).

**Common acquire-phase mistakes:**
- Treating BibleNLP as register-balanced (it's not — produces archaic/liturgical drift).
- Skipping deduplication after merging multiple catalogs (CulturaX + MADLAD overlap heavily).
- Choosing a vocab-extension method without first measuring fertility.
- Forgetting to record license terms — required for Release.

## Phase: Analyze (deep dive)

**Inputs:** acquire-phase data.
**Outputs:** linguistic-analysis artifacts needed for downstream training/eval (morphology tables, treebanks, IPA lexicons, discourse-tagged samples, IAA-validated annotations).

**Mandatory steps (only those needed for the user's goal):**
1. Morphology if MRL → `magic-linguistic-morph`.
2. Syntactic eval if testing structural generalization → `magic-linguistic-syntax`.
3. SRL/MWE coverage if RAG/structured extraction → `magic-linguistic-semantics`.
4. Discourse if long-context generation/summarization → `magic-linguistic-discourse`.
5. Speech if oral data sources or G2P needed → `magic-linguistic-speech`.
6. Annotation workflow if creating gold data → `magic-linguistic-annotate`.

**Phase parallelism:** Analyze sub-skills are independent. Route in parallel WHEN the user has explicitly requested all outputs; otherwise route serially to avoid waste.

## Phase: Evaluate (deep dive)

**Inputs:** trained/adapted model + acquire+analyze outputs.
**Outputs:** evaluation report with per-language, per-register, per-dialect breakdowns; contamination assessment; error taxonomy.

**Mandatory steps:**
1. Choose benchmarks via `magic-linguistic-eval` (avoid BLEU as primary on MRLs).
2. Run contamination check (FLORES is in many pretrain mixes; check eval/pretrain overlap).
3. Stratify by register/dialect/length (sociolinguistic fairness).
4. If applicable, BLiMP-style probing for grammatical knowledge.

## Phase: Release (deep dive)

**Inputs:** evaluation passing thresholds.
**Outputs:** released model + model card + community sign-off (where required).

**Mandatory steps:**
1. License-compliance audit via `magic-linguistic-ethics`.
2. Attribution registry update.
3. Community review (where applicable — FPIC requires this).
4. Release-mode decision: open / community-gated / restricted.

## Cross-phase: Refinement

Refinement loops back from any phase to any earlier phase:
- Eval reveals tokenizer fertility issue → loop to Acquire (re-train tokenizer).
- Analyze finds morphological complexity not covered by current tokenizer → loop to Acquire.
- Release ethics audit fails → loop to Acquire (re-license or remove dataset).
