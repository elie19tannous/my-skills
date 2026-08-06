# Vendor Diligence Checklist

Scored checklist across the five diligence areas. Score each item Present /
Partial / Missing, then roll up to a severity per area (Critical/High/Medium/Low)
and an overall recommendation.

## Risk tiering (do this first)

| Signal | Tier bump |
|--------|-----------|
| Handles PII/PHI/PCI or regulated data | + |
| Business-critical / hard to switch away from | + |
| Production system integration / money movement | + |
| Large spend or multi-year term | + |
| Regulated industry (finance, health, gov) | + |

0-1 signals → Low. 2 → Medium. 3 → High. 4+ or any "critical infrastructure" → Critical.

## 1. Data Security & Privacy

- [ ] Named security controls (encryption in transit/at rest, access control, secure SDLC) — not just "reasonable measures"
- [ ] Certification / audit rights (SOC 2 Type II, ISO 27001, pen-test summary access)
- [ ] Breach notification window defined (e.g. "without undue delay" or a specific hour count)
- [ ] Data Processing Addendum (DPA) present for personal data, with sub-processor list + objection right
- [ ] Cross-border transfer mechanism specified where relevant
- [ ] Data location/sovereignty stated and acceptable

## 2. Liability Caps & Carve-Outs

- [ ] Cap size proportionate to realistic worst-case loss (not a token amount)
- [ ] Data-breach losses carved out of (or super-capped above) the general cap
- [ ] IP-infringement and confidentiality/data indemnities carved out of the cap
- [ ] Excluded-damages clause is mutual and reasonable
- [ ] Cap and exclusions apply to both parties, not just the vendor

## 3. SLA & Remedies

- [ ] Metrics are defined and objectively measurable (not vendor self-report only)
- [ ] Targets are realistic for the criticality tier
- [ ] Remedy beyond service credits: a termination right on chronic/material failure
- [ ] Measurement window isn't gamed (e.g. monthly average hiding a real outage)
- [ ] Exclusions (maintenance, force majeure) aren't so broad they gut the SLA

## 4. Termination & Exit

- [ ] Termination for cause, convenience, and chronic SLA failure all present
- [ ] Data returned in a usable format within a defined window on exit
- [ ] Deletion + certification of deletion after return
- [ ] Transition-assistance period for critical vendors
- [ ] No hostile auto-renewal (long opt-out notice) — or it's flagged if present
- [ ] Confidentiality/data-protection/liability terms survive termination

## 5. Indemnity

- [ ] IP-infringement indemnity present, with defense + fix/replace/refund remedy
- [ ] Data-breach / confidentiality indemnity present
- [ ] Indemnity is mutual (not vendor-favoring only)
- [ ] Notice, defense-control, and settlement-consent procedure is workable

## Gap report format

| Area | Finding | Severity | Owner | Ask |
|------|---------|----------|-------|-----|
| e.g. Data Security | No DPA, no breach-notice window | Critical | Legal | Require DPA w/ 72h notice before signing |

Headline: "Vendor risk tier: [tier]. X critical / Y high gaps. Recommendation: [proceed / proceed-with-conditions / do-not-onboard]."
