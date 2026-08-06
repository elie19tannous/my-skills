# CARE + FPIC Checklist — Reference

Loaded by `magic-linguistic-ethics` Step 3 (mix audit) and Step 1 (scope seed).

## CARE — Concrete Checklist (not aspirational)

For each dataset, answer all four:

### C — Collective benefit
- [ ] Does the source community benefit from this use? (Direct benefit, not "general AI advancement.")
- [ ] If yes, how is benefit measured / verified?
- [ ] If no, is there a reciprocity arrangement (e.g., model access, capacity-building, financial support)?

### A — Authority to control
- [ ] Did the source community authorize this specific use? (Not just data collection — model training.)
- [ ] Can the community revoke authorization? Is the revocation path documented?
- [ ] Who has the authority to speak for the community on this question? (Hint: not always who you think.)

### R — Responsibility
- [ ] Who is accountable for harms downstream from this model?
- [ ] Is there a feedback channel for community concerns?
- [ ] Is there a process for handling complaints?

### E — Ethics
- [ ] Was engagement ongoing or one-shot?
- [ ] Were terms negotiable, or take-it-or-leave-it?
- [ ] If the community said no to one term, was the negotiation continued or abandoned?

If 3+ of these have NO/UNCLEAR answers: BLOCK. Route back to the user with specific questions to research.

## FPIC — Operational Definition

Each letter is a quality gate, not a checkbox to tick:

### F — Free
- [ ] No coercion (financial, political, employment-based)?
- [ ] Power asymmetry acknowledged?
- [ ] Time pressure was reasonable?

### P — Prior
- [ ] Consent obtained BEFORE data collection? (Not retroactive normalization.)
- [ ] If retroactive: explicitly flagged + remediated?

### I — Informed
- [ ] Community understood what an LLM is (in their language and cultural context)?
- [ ] Community understood what model outputs could be (generation, reuse, commercialization)?
- [ ] Community understood what risks exist (data leakage, attribution, dual-use)?

### C — Consent
- [ ] Affirmative — not just "didn't object"?
- [ ] Can be withdrawn — and the withdrawal process is documented?
- [ ] Specific to the use case (not a blanket "AI use" consent)?

## Common FPIC Failure Modes

1. **The colonial signature**: a regional government / NGO signs on behalf of a community. Often not the right authority.
2. **The power-imbalance handshake**: Western tech company offers funding; community feels unable to refuse. Free? No.
3. **The retroactive consent**: data was collected for linguistics research; later repurposed for ML without re-consenting.
4. **The "open license therefore consented" inference**: license terms are *legal* permission; FPIC is *ethical* permission. Different things.
5. **The blanket consent**: "data may be used for any research" — does NOT cover commercial generative AI.
6. **The asymmetric revocation**: consent obtained but no documented withdrawal process → effectively non-revocable.

## When FPIC Is Required (versus Standard License Check)

| Scenario | FPIC required? |
|---|---|
| English Wikipedia dataset | NO — standard license |
| French news corpus from a major publisher | NO — standard license |
| Yoruba Wikipedia + MasakhaNER (community-published) | LIKELY YES — check each source |
| Indigenous language documentation from ELAR | YES — community partnership through archive |
| Sacred text (Bible, Quran, Indigenous oral) | YES — religious / community gating |
| Field recordings from named individuals | YES — speaker rights |
| Recent endangered-language community texts | YES — direct community contact |
| Historical written texts (pre-1900) of any language | NO usually — but check archive |

## Engagement Pathways (use existing partnerships)

Don't try to do FPIC yourself for languages you don't have community ties to:

| Region | Partner organizations |
|---|---|
| African languages | Masakhane (https://www.masakhane.io/); per-country NLP communities |
| Indigenous Americas | AmericasNLP (https://www.americasnlp.org/); AILLA archive; per-nation tribal councils |
| Indigenous Australia | First Languages Australia; IndigenousNLP groups |
| Aotearoa / NZ | Te Hiku Media; Māori Data Sovereignty Network; MIT-Māori partnership |
| Pacific Islands | OLAC + community organizations per island |
| South Asian Indigenous | local-language NLP communities; AI4Bharat for major languages |
| European endangered (Sami, Welsh, Irish, etc.) | ELDP partner archives; UK/Norway/etc. community organizations |

When in doubt, route the question through ELDP (Endangered Languages Documentation Programme) or DELAMAN umbrella.

## Documentation: how to record this in workspace_state.md

```markdown
## Ethics Status

**Vitality (EGIDS):** <code> — <ethics-depth>
**FPIC required?** YES | NO | NOT-APPLICABLE
- If YES, status: OBTAINED | IN-PROGRESS | OUTSTANDING
- Community partner: <name + URL>
- Consent date / scope: ...
- Revocation contact: ...

**License inventory:** <link to attribution_registry.md per-dataset entries>

**Sacred-text concerns:** NONE | SEE: <ref>

**Outstanding ethics actions:**
- [ ] ...
```

## See also

- **GIDA / CARE Principles**: https://www.gida-global.org/care
- **Carroll, S. R., et al.** (2020). *The CARE Principles for Indigenous Data Governance*. Data Science Journal 19(1).
- **Anaya, J.** (2013). *Report of the Special Rapporteur on the rights of indigenous peoples* (UN). FPIC framework.
- **Te Mana Raraunga Māori Data Sovereignty Network**: https://www.temanararaunga.maori.nz/
- **First Nations Information Governance Centre (FNIGC, Canada)**: OCAP principles.
