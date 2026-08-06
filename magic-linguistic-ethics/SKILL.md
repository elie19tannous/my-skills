---
name: magic-linguistic-ethics
description: Apply CARE / FPIC / community-sovereignty / license-compliance / sacred-text gating across every linguistic project phase. Use whenever the user mentions FPIC, CARE principles, Indigenous data, data sovereignty, community engagement, license audit, attribution, sacred text, restricted corpus, religious text use, endangered-language data, model card ethics statement, or asks 'is it OK to use this dataset for training'. Routed by magic-linguistic-orchestrator EARLY (Scope phase seed) and AGAIN at Release (final gate). **You should also use this skill whenever a non-English dataset is being added** — every dataset crosses an ethics boundary, even open-licensed ones. CARE complements FAIR; license terms ≠ community-use norms.
license: Apache-2.0
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  test_coverage: advisory  # structurally validated, not behaviorally tested (no executable tests by design)
  phase: 1
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - ethics
  - fpic
  - care
  - license
  - sacred-text
  - low-resource
  dependencies: []
---

## When to Use

- Any new dataset being considered for training/eval (early — before download).
- Endangered or Indigenous language data of any kind.
- Religious / sacred text use (Bible-NLP, Quranic, Vedic, Indigenous oral histories).
- License audit before release (open / community-gated / restricted decision).
- Attribution and provenance tracking design.
- Drafting a model card's "Ethics" / "Limitations" / "Intended Use" sections.
- Routing decisions involving community-controlled archives (DELAMAN, ELAR, AILLA, PARADISEC).

**When NOT to use:** the dataset is your own English-only synthetic data with no community attribution issues; or the operation is a pure technical refactor with no data implications. Even then, ask once — under-using ethics is the modal failure mode.

## Why this skill is A-tier (and not optional)

A "good" engineer can build a tokenizer, mine bitext, fine-tune a model. None of that protects against:
- Training on a dataset whose community didn't consent to model use, even if the license technically permits it.
- Releasing a model that generates Sacred Indigenous content without permission.
- Stripping attribution lineage during a dataset merge so credit becomes irrecoverable.
- Using "open" Bible-NLP for a commercial chatbot whose generations the source community would not endorse.

These are the high-cost mistakes. They damage communities, harm professional reputation, and increasingly carry regulatory consequences (EU AI Act, Indigenous data sovereignty laws, GDPR-like cultural data protections). This skill is mandatory routing — not optional polish.

## CARE complements FAIR (does not replace it)

FAIR (Findable, Accessible, Interoperable, Reusable) is the technical-data discipline. CARE adds the social discipline:

| FAIR | CARE |
|---|---|
| Findable — metadata + identifiers | Collective benefit — does this serve the source community? |
| Accessible — fetchable | Authority to control — community decides terms |
| Interoperable — standard formats | Responsibility — for harms downstream |
| Reusable — clear license | Ethics — through engagement, not just consent |

A dataset can be FAIR (standardized, downloadable, openly licensed) and still violate CARE (community wasn't asked, terms favor the user not the source).

**The rule:** every dataset routing through `magic-linguistic-corpus` or `magic-linguistic-bitext` MUST pass through this skill at least once for a CARE check, even if FAIR is satisfied.

## FPIC — Free, Prior, Informed Consent

FPIC is the standard for Indigenous and traditional knowledge use. Often misunderstood as "got a signature → done". Real FPIC requires all four:

| F: Free | Without coercion or pressure |
| P: Prior | Before the data is used / collected (not retroactive) |
| I: Informed | Community understood what models trained on this data could do |
| C: Consent | Affirmative; can be withdrawn |

**FPIC is process, not document.** A signed license without ongoing engagement is not FPIC.

For projects involving Indigenous data, route to a partner organization (e.g., Te Hiku Media for te reo Māori; First Languages Australia; ELAR for many endangered languages) BEFORE first contact with raw data.

## License Audit Workflow

**MANDATORY READ** [`references/license_audit.md`](references/license_audit.md) before any dataset-mix release.

Quick decision tree:

```
Does the dataset have an explicit license?
├── NO → don't use; or contact source for clarification
└── YES
    ├── CC0 / Public Domain → check for community norms anyway (CARE step)
    ├── CC-BY → attribution required; track in registry
    ├── CC-BY-SA → ShareAlike obligation propagates to model output license
    ├── CC-BY-NC → COMMERCIAL use blocked; common dataset-mix gotcha
    ├── CC-BY-ND → no derivatives; usually blocks training
    ├── Custom community license (Māori Data License, etc.) → respect terms; usually requires community-gated release
    ├── ODbL / similar database licenses → propagate ShareAlike to derived data
    └── No-NC, derivative-allowed, attribution-required → standard "open" dataset
```

**Compatibility check**: when mixing N datasets for training:
- Any CC-BY-NC in the mix → entire model is non-commercial-use only.
- Any CC-BY-SA in the mix → entire model output must propagate the SA term.
- ND blocks derivative use; if mixed, you've already violated terms.

## Sacred-Text / Culturally-Sensitive Material Gating

**Framework + 5 canonical examples** (Q6 resolution from ralplan iter-2). NOT a hardcoded blocklist — a decision framework anchored by examples.

**MANDATORY READ** [`references/sacred_text_gating.md`](references/sacred_text_gating.md) before training on or releasing models that touch any of:

| Example | What's restricted | Why |
|---|---|---|
| Quranic text | Generation/transformation; respectful contextual handling | Religious community standards on representation |
| Indigenous oral histories | Public release; transformation into model output | Custodian permission required; many are not for outsider use |
| Sami yoik recordings | Use in non-Sami contexts; commercial training | Cultural ownership; Sami Council guidelines |
| Aboriginal Australian songlines | Recording, distribution, model use | Custodian-permission required; Indigenous Cultural and Intellectual Property (ICIP) protocols |
| Bible-NLP / liturgical text | Commercial training; distortion of canonical text | Many translations under permissive license but communities prefer non-commercial use |

The framework: source community involvement → use intent → distribution scope → technical safeguards. Apply it to any text you're unsure about.

## Attribution Registry

Every dataset entry traces to:
- Source URL or citation.
- License (with version + date).
- Date acquired.
- Permission record (if FPIC required).
- Community contact (if applicable).
- Lineage (parent dataset(s) it was derived from).

When merging datasets, lineage MUST be preserved — never strip attribution to "clean up" a merged file.

**MANDATORY READ** [`references/attribution_registry.md`](references/attribution_registry.md) for the schema.

## Workflow

### Step 1 — Scope ethics (early, before data acquisition)
- Read `workspace_state.md` for target language + vitality (from `magic-linguistic-scope`).
- Vitality 6b+ (threatened or worse): heavy ethics — community partner identified.
- Vitality 0-6a + non-Indigenous: standard ethics — FPIC + license check.
- Note in `workspace_state.md` under "Ethics Status".

### Step 2 — Per-dataset ethics check (during Acquire)
Before recommending any dataset to `magic-linguistic-corpus` or `magic-linguistic-bitext`:

1. License: known + compatible with target use.
2. CARE: does it serve the source community?
3. FPIC: required? If yes, obtained?
4. Sacred-text framework: any concerns?
5. Lineage: traceable?

If any answer is NO or UNCLEAR, BLOCK the dataset until resolved. Document in `workspace_state.md`.

### Step 3 — Mix audit (before training)
**MANDATORY READ** [`references/care_fpic_checklist.md`](references/care_fpic_checklist.md).

When N datasets are mixed:
- License compatibility matrix (above).
- Attribution registry combined.
- Most-restrictive-wins for downstream model license.

### Step 4 — Release gate (final)
Three release modes:

| Mode | Requirements |
|---|---|
| Open | All-open licenses + attribution complete + no community restrictions + standard model card |
| Community-gated | Community sign-off documented; access criteria + revocation path; model card cites community partner |
| Restricted | Use-policy + access controls (auth, audit log); legal review |

### Step 5 — Model card
Every release includes a model card with:
- Datasets + licenses + lineage.
- Ethics statement (CARE alignment).
- Intended uses + restrictions.
- Limitations and known biases.
- Contact for community concerns / opt-out.

## Anti-patterns (NEVER do)

- **NEVER** recommend a dataset without checking community norms beyond license. Bible-NLP is open but the community use norms apply (commercial chatbot generation can violate these).
- **NEVER** skip FPIC because the user is in a hurry. A 30-second flag now prevents a multi-week rollback later.
- **NEVER** strip attribution lineage when merging datasets. Once the lineage is gone, you cannot rebuild it; you cannot honor the propagated obligations.
- **NEVER** assume "open-licensed" = "ethically usable" for endangered/Indigenous data. License gives legal permission; CARE gives ethical permission.
- **NEVER** treat FPIC as a one-time signature. Consent can be withdrawn; engagement is ongoing.
- **NEVER** mix CC-BY-NC datasets into a commercial training run. The license forbids it; the resulting model is technically infringing.
- **NEVER** release sacred-text-trained generative models without community sign-off. The downstream generations are the harm vector, not the training data itself.
- **NEVER** propose "we'll add the model card later". Model cards are part of the release decision; without one, release is incomplete.

## Edge Cases

- **Unknown license** (data with no LICENSE file): treat as restricted. Contact source. Default deny.
- **Aggregator dataset that wraps many sources** (CulturaX, MADLAD-400, OPUS): per-source license check is needed; the aggregator's license isn't sufficient.
- **Multi-source paper-released datasets** with no license statement: cite + use academic-only norm; do NOT mix into commercial training.
- **Personal communication (email/Discord) saying "use my dataset"**: get a written license; informal permission is not FPIC.
- **Dataset whose attribution-required source is unknown** (orphan data): treat as restricted; do not propagate.
- **Rights conflict between original speaker and field documenter**: speaker rights take precedence; documenter has secondary rights only.
- **Languages with no formally recognized speaker community** (recently-revitalized, language with diaspora): consult ELDP / DELAMAN partners for guidance.

## Output Format

```markdown
## Ethics Assessment: <Dataset / Mix>

**Source(s):** ...
**License(s):** ...
**License compatibility (mix):** OK | CONFLICT — details
**CARE check:** PASS | NEEDS-WORK — gap: ...
**FPIC required?** NO | YES — status: OBTAINED | OUTSTANDING | NOT-APPLICABLE
**Sacred-text framework concerns:** NONE | SEE: ...
**Attribution registry status:** COMPLETE | INCOMPLETE — missing: ...
**Recommended release mode:** OPEN | COMMUNITY-GATED | RESTRICTED
**Outstanding actions:** ...
```
