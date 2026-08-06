# Sacred-Text / Culturally-Sensitive Material Gating — Reference

Loaded by `magic-linguistic-ethics` Step 2.

This is a **framework + 5 canonical examples**, NOT a closed list. Apply the framework to any text you're unsure about. Per Q6 ralplan iter-2 resolution.

## The Framework — four questions

For each candidate corpus or text, answer:

1. **Source community involvement.** Is there a recognized community whose tradition this text belongs to? Was the community involved in the data's creation, curation, or release?

2. **Use intent.** Will the model trained on this generate text in this tradition? Will it be used to discuss, transform, summarize, or translate this tradition?

3. **Distribution scope.** Will the model be released openly, gated to a community, or restricted? Will outputs be public-facing?

4. **Technical safeguards.** Can the model refuse to generate certain things? Can outputs be reviewed before release? Is there a feedback channel?

The answers determine the gate level:

| Answers indicate... | Gate level |
|---|---|
| No community concerns + open distribution + safeguards | OPEN — proceed with standard ethics |
| Community concerns OR sensitive distribution | COMMUNITY-GATED — explicit sign-off required |
| Sacred / restricted material + generative use | RESTRICTED — usually decline; alternative approaches |
| Community-controlled material without sign-off | DECLINE until sign-off obtained |

## The 5 Canonical Examples

### 1. Quranic text

**What's restricted:** transformation (paraphrase, summarization, generation in style of). Direct quotation in attributive contexts is generally OK.

**Why:** Religious community standards on representation; concerns about distortion of canonical text; concerns about generated text being mistaken for canonical.

**Practical:** training on Arabic-language LLM that includes Qur'anic Arabic is widely accepted; releasing a model that GENERATES "Quranic-style" text is widely considered inappropriate. Add safeguards (refusal patterns) in chatbot deployment.

### 2. Indigenous oral histories

**What's restricted:** public release (often custodian-only). Use in model output without permission.

**Why:** Custodian permission is required by ICIP (Indigenous Cultural and Intellectual Property) frameworks. Many oral traditions are not for outsider use, even with technical access.

**Practical:** route to the source archive (e.g., AILLA, ELAR, PARADISEC) — they've handled access protocols. Don't go around the archive.

### 3. Sami yoik recordings

**What's restricted:** use in non-Sami contexts, commercial training, generation of yoik-style content.

**Why:** Cultural ownership; Sami Council guidelines; specific yoiks are often person-specific (about a named individual or family).

**Practical:** Sami Council has published guidelines for yoik use; check before any audio-LLM work touches Sami audio archives.

### 4. Aboriginal Australian songlines

**What's restricted:** recording, distribution, model use without custodian permission. Some songlines are gender-restricted or initiate-only.

**Why:** Indigenous Cultural and Intellectual Property protocols; custodian permission required.

**Practical:** First Languages Australia and AIATSIS protocols apply. Many songline recordings exist in archives that explicitly require protocol-compliance for access.

### 5. Bible-NLP / liturgical text

**What's restricted:** commercial generative use; distortion of canonical text in model output; use as primary training data without diverse complement.

**Why:** Many translations are open-licensed but communities prefer non-commercial use of generative outputs. Bible-only training also produces archaic-register drift, harming the very low-resource languages it's used for.

**Practical:** standard low-resource MT training using Bible-NLP is widely accepted (it's often the only parallel data); commercial chatbot generation in archaic religious register is widely contested. Use Bible as ONE source among many; flag in model card.

## Beyond the 5 Examples — Apply the Framework

You will encounter cases not on this list. The framework applies:

| Case | Framework application |
|---|---|
| Vedic Sanskrit text | Like Quranic — community standards on transformation; safeguards in deployment |
| Buddhist sutra translations | Often more permissive; check per-tradition (Tibetan vs Theravada) |
| Native American songs | Custodian permission; use ICIP framework |
| African ritual texts (e.g., Ifá divination verses) | Community-controlled; route to local researchers |
| Dead Sea Scrolls / similar archive texts | Academic-only is common; check archive license |
| Folk songs of recently-recorded communities | Singer rights + community rights both apply |
| Personal letters / diaries (historical) | Privacy + literary heritage rights |
| Endangered-language children's stories | Often community-controlled even if "open" elsewhere |

## What this skill does NOT do

- This skill does NOT decide for the community whether use is OK. It triggers the conversation; community + appropriate authorities decide.
- This skill does NOT replace legal counsel. Some cases (especially commercial) need lawyers.
- This skill does NOT block all sensitive material — it gates and documents.

## When to escalate to a human

- Any case the framework flags as potentially restricted AND the project intends to proceed.
- Any case where the user pushes back on the framework's recommendation.
- Any case involving commercial release of culturally-sensitive material.
- Any case involving children's cultural material.

Escalation: pause the workflow; user takes the question to community partners + legal review.

## Red-flag patterns in user requests

- "We just need to train on it; we won't release the model." — model artifacts can leak; not a sufficient safeguard.
- "It's already on the internet so it's fair game." — internet availability ≠ permission; many sacred texts are online without community sign-off.
- "We'll add the ethics review later." — ethics has to gate, not follow.
- "The license says we can." — license ≠ CARE.
- "I'm a member of the community so it's fine." — individual membership doesn't grant community-level authority.

## See also

- **CARE Principles**: https://www.gida-global.org/care
- **AIATSIS Guidelines for Ethical Research in Australian Indigenous Studies**: https://aiatsis.gov.au/research/ethical-research
- **OCAP Principles** (FNIGC, Canada): https://fnigc.ca/ocap-training/
- **Te Mana Raraunga Māori Data Sovereignty**: https://www.temanararaunga.maori.nz/
- **WIPO Indigenous Knowledge framework**: https://www.wipo.int/tk/en/
