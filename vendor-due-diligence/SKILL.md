---
name: vendor-due-diligence
description: Run a structured due-diligence pass on a vendor / supplier / service contract before signing or renewing, focused on the terms that create the most downside — data security & privacy, liability caps & carve-outs, service levels (SLAs) & remedies, termination & exit / data return, and indemnity allocation. Use when a user asks you to vet, diligence, or risk-assess a vendor agreement, SaaS/MSA/DPA, supplier or outsourcing contract; when they want a "what could go wrong" checklist before onboarding a vendor; when they ask which clauses to push back on; or when procurement/security/legal need a shared risk view. Covers a scored diligence checklist, the liability-cap adequacy test, SLA/credit realism, sub-processor and data-return exit risk, indemnity mutuality, and a prioritized gap report with owners. Do NOT treat this as a security audit of the vendor's actual systems or as jurisdiction-specific legal/regulatory advice; it reviews the contract and the diligence posture, not the vendor's live controls.
license: MIT
compatibility: No network required for the workflow or the offline clause-coverage scanner (Python stdlib only). Actual verification of a vendor's security posture (audits, pen-test reports, certifications) and jurisdiction-specific regulatory obligations are separate and out of scope for the offline pass.
---

# Vendor Due Diligence

## Instructions

> **Core rule:** vendor risk is asymmetric. A contract can look complete and still leave you exposed on the five clauses that decide what happens when things go wrong: **data security, liability caps, SLAs, termination/exit, and indemnity.** Diligence is not "did we get a signature" — it is "when this vendor breaches, loses our data, or goes dark, what do we actually recover and how fast do we get out?"

### Step 1: Frame the Engagement & Risk Tier
The same contract needs light or heavy diligence depending on exposure. Pin down:

| Question | Why it matters |
|----------|----------------|
| What does the vendor touch? | Personal/regulated data, production systems, money movement → highest tier |
| Criticality & switching cost | If the vendor going down stops your business, exit terms matter far more |
| Data classification | PII, PHI, PCI, secrets → data-security and DPA terms are non-negotiable |
| Spend & term length | Larger/longer deals justify pushing on caps and exit |
| Regulatory context | Regulated industry may mandate specific clauses (flag; route specifics to counsel/compliance) |

Set a tier (low / medium / high / critical). The tier sets how hard each area below must be scrutinized.

### Step 2: Data Security & Privacy
The area most likely to cause a reportable, expensive incident.

- **Security commitments**: are concrete controls promised (encryption in transit/at rest, access control, secure SDLC) or just "reasonable measures"?
- **Certifications / audits**: does the contract require and give you rights to evidence (SOC 2 Type II, ISO 27001, pen-test summaries, audit rights)?
- **Breach notification**: is there a defined notification window (e.g. "without undue delay / within X hours"), and does it include enough detail to meet *your* regulatory clock?
- **Data Processing Addendum (DPA)**: for personal data, is there a DPA with processing scope, sub-processors, cross-border transfer mechanism, and deletion obligations?
- **Sub-processors**: is there a list, a right to object, and flow-down of the same obligations?
- **Data location & sovereignty**: where is data stored/processed? Does it satisfy your legal constraints?

Flag "reasonable security measures" with no specifics, no breach-notice window, or no DPA for personal data as high-tier gaps.

### Step 3: Liability Caps & Carve-Outs
Where the money is decided. Read the cap AND its exceptions together — one is meaningless without the other.

| Test | Adequate | Red flag |
|------|----------|----------|
| Cap size | Sized to realistic worst-case loss (often a multiple of annual fees for high-risk data) | Cap = 1 month's fees / a token amount vs the harm a breach could cause |
| Data-breach carve-out | Data/security incidents excluded from (or given a super-cap above) the general cap | Breach losses squeezed under a tiny general cap |
| Indemnity carve-out | IP-infringement and confidentiality/data indemnities sit outside the cap | All indemnities pulled under the cap |
| Excluded damages | Mutual and reasonable | Consequential-damages waiver that guts your only real remedy |
| Mutuality | Cap and exclusions apply to both sides | One-sided cap protecting only the vendor |

The single most common trap: a low general cap that also swallows data-breach and indemnity liability, leaving you with token recovery after a major incident.

### Step 4: Service Levels (SLAs) & Remedies
An SLA with no teeth is marketing.

- **Defined metrics**: uptime %, response/resolution times, measured how and by whom (vendor self-report vs independent)?
- **Realistic targets**: does "99.9%" match the criticality, and is the measurement window gamed (monthly averages hide outages)?
- **Remedies**: are service credits the *sole* remedy, and are they trivial? A 5% credit does not cover a day of downtime for a critical system.
- **Chronic-failure right**: does repeated SLA breach give you a **termination right** (not just credits)? This is the clause that actually protects you.
- **Exclusions**: are maintenance windows, force majeure, and "your fault" exclusions so broad they hollow out the SLA?

Flag credits-as-sole-remedy with no chronic-failure termination right for a critical vendor as a high gap.

### Step 5: Termination & Exit / Data Return
How you get out — and get your data back — is where lock-in bites.

- **Termination rights**: for cause (breach, insolvency), for convenience (notice period), and on chronic SLA failure.
- **Data return & deletion**: on exit, does the vendor return your data in a usable format within a defined window, then delete it and certify deletion?
- **Transition assistance**: is there a defined exit-assistance/transition period so you can migrate without a cliff?
- **Post-termination survival**: do confidentiality, data-protection, and liability terms survive termination?
- **Auto-renewal traps**: silent auto-renewal with a long opt-out notice window is a lock-in trap — flag it.

Flag missing data-return-in-usable-format, no transition assistance for a critical vendor, or a hostile auto-renewal as exit risks.

### Step 6: Indemnity Allocation
Who pays when a third party sues.

- **IP-infringement indemnity**: does the vendor indemnify you if their product infringes a third party's IP (with defense, and a fix/replace/refund remedy)?
- **Data-breach / confidentiality indemnity**: does the vendor indemnify you for losses from their security failure?
- **Mutuality & scope**: is the indemnity one-sided (only you indemnify the vendor)? Are the carve-outs from the cap (Step 3) aligned?
- **Procedure**: notice, control of defense, settlement consent — reasonable and workable?

Flag a missing IP-infringement indemnity, a one-sided indemnity, or an indemnity that is entirely capped away as high gaps.

### Step 7: Produce the Diligence Gap Report
Deliver a scored, prioritized report. For each area (data security, liability, SLA, termination/exit, indemnity):

| Field | Content |
|-------|---------|
| Area | The five diligence areas + any deal-specific ones |
| Finding | What the contract says / is missing |
| Severity | Critical (do-not-sign) / High (must-fix) / Medium (negotiate) / Low (note) |
| Owner | Who resolves it — legal, security, procurement, business |
| Ask | Concrete redline or evidence request (e.g. "add breach-notice within 72h", "provide SOC 2 report") |

End with a headline: "Vendor risk tier: [tier]. X critical / Y high gaps. Recommendation: [proceed / proceed-with-conditions / do-not-onboard]." Never green-light a critical-tier vendor with an open data-security or liability-cap gap.

### Step 8: Diligence Discipline
- Contract review is not a systems audit. Do **not** claim the vendor "is secure" from the contract alone — require evidence (SOC 2, ISO cert, pen-test summary) and mark it Unverified until produced.
- Do **not** give jurisdiction-specific regulatory conclusions (GDPR/CCPA/HIPAA applicability, cross-border transfer validity) — flag the requirement and route to compliance/counsel.
- Do **not** wave through a missing clause because "the vendor is reputable." Reputation is not a contractual remedy.
- Separate **contract gaps** (fixable by redline) from **evidence gaps** (fixable by the vendor producing documents) — they have different owners.

## Examples

### Example 1: SaaS Vendor Touching Customer PII
**Input:** "We're onboarding a SaaS analytics vendor that will hold our customers' personal data — diligence this MSA."
**Output:** Risk tier: HIGH (personal data, production integration). Findings: (1) Data security — contract promises only "commercially reasonable measures," no breach-notice window, and there is no DPA — CRITICAL; ask for a DPA with a 72-hour breach-notice, sub-processor list + objection right, and a SOC 2 Type II report (Unverified until produced). (2) Liability — cap is 3 months' fees and data-breach losses fall under it — HIGH; ask for a data-breach super-cap and to carve IP/confidentiality indemnities out of the cap. (3) SLA — 99.5% with service credits as sole remedy, no chronic-failure termination — Medium; add a termination right after N consecutive breaches. (4) Exit — data returned only "on request," no format or deletion certificate — HIGH; require usable-format return within 30 days + certified deletion. (5) Indemnity — IP indemnity present, no data-breach indemnity — High; add one. Headline: tier HIGH, 1 critical / 3 high; proceed-with-conditions only.

### Example 2: Low-Risk Tooling Vendor
**Input:** "Quick check on a $200/mo project-management tool — do we need heavy diligence?"
**Output:** Risk tier: LOW (no regulated data, not business-critical, low spend, monthly term). Light pass: confirm (a) a breach-notice clause and basic security statement exist, (b) you can export your data and cancel monthly without penalty, (c) no hostile auto-renewal. The liability cap and SLA are proportionate to a $200/mo tool and not worth heavy negotiation. No critical/high gaps found; proceed. Note: if usage later expands to hold customer data, re-tier and re-run the data-security and DPA steps.

### Example 3: Critical Infrastructure Supplier with Lock-In
**Input:** "This vendor runs our payment processing. Legal signed but I want a risk view before renewal."
**Output:** Risk tier: CRITICAL (money movement, business-stopping if down). Findings: (1) Liability — general cap swallows everything including data-breach and IP indemnity — CRITICAL; renewal must carve these out and add a super-cap. (2) SLA — 99.9% but credits are sole remedy and there is no chronic-failure or material-degradation termination right — CRITICAL for a payments vendor; add a hard termination trigger. (3) Exit — 90-day auto-renewal with a 90-day opt-out window and no transition assistance — HIGH lock-in; negotiate an exit-assistance period and shorten the opt-out. (4) Data security — SOC 2 required annually (good) but last report not on file — mark Unverified; obtain it. (5) Indemnity — mutual and adequate. Headline: tier CRITICAL, 2 critical / 1 high; do-not-renew until the cap and termination gaps are fixed.

## Bundled Resources

### References
- `references/diligence-checklist.md` -- The full scored checklist across the five areas (data security & privacy, liability caps & carve-outs, SLAs & remedies, termination & exit, indemnity), with the risk-tiering rubric, the liability-cap adequacy test, and the gap-report format. Consult when running a diligence pass end to end.
- `references/red-flag-clauses.md` -- Catalogue of the specific vendor-contract red flags (token liability cap, breach losses under the cap, credits-as-sole-remedy, "reasonable measures" with no specifics, no DPA, data-return "on request" only, hostile auto-renewal, one-sided indemnity) with the fix/ask for each. Consult when writing the gap-report "Ask" column.

### Scripts
- `scripts/diligence_scanner.py` -- Offline clause-coverage scanner (Python stdlib only, no network). Scans a vendor contract's plaintext and reports which of the key diligence clauses appear present vs missing (breach notification, DPA/sub-processors, liability cap, data-breach carve-out, SLA + credits, chronic-failure termination, data-return/deletion, auto-renewal, IP & data-breach indemnity), plus a rough risk-tier hint from data-sensitivity keywords. It flags coverage gaps for human review; it does NOT judge whether a present clause is adequate. Run: `python scripts/diligence_scanner.py --help`

## Gotchas

- A liability cap and its carve-outs are one clause, not two. A "generous" super-cap is worthless if data-breach and indemnity losses are still pulled under a tiny general cap — always read them together.
- "Reasonable security measures" is not a security commitment. Without named controls, a breach-notice window, and evidence rights (SOC 2 / audit), you have nothing enforceable — treat it as a gap, not a control.
- Service credits are usually the vendor's cap on SLA liability, not your remedy. The clause that actually protects you is the right to terminate for chronic or material SLA failure. Its absence is the real gap.
- Uptime percentages hide behind the measurement window. 99.9% "monthly average" can mask a multi-hour outage; check how and by whom availability is measured.
- No DPA for personal data is a critical gap regardless of how good the security clause reads. Personal/regulated data needs the processing terms, sub-processor controls, and deletion obligations a DPA carries.
- Exit is where lock-in bites. "Data returned on request" with no format, window, or deletion certificate — plus a hostile auto-renewal — can trap you long after you want out. Diligence the exit as hard as the entry.
- Contract review ≠ vetting the vendor's real security. A perfect data-security clause with no SOC 2/ISO evidence produced is Unverified, not "secure." Keep contract gaps and evidence gaps separate.
- Do not clear a clause because the vendor is well-known. Reputation is not a remedy; the contract is what you can enforce.
- The scanner reports presence/absence by pattern only. A clause it marks "present" may still be inadequate (a cap that exists but is too low), and it will miss unusually worded clauses. Use it as a coverage worklist, then judge adequacy by hand.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| NIST — third-party / supply-chain risk management (SP 800-161) | https://csrc.nist.gov/pubs/sp/800/161/r1/final | The framework for vendor/supply-chain security diligence and what evidence to require |
| Cloud Security Alliance — CAIQ / STAR | https://cloudsecurityalliance.org/star | The standard vendor security questionnaire and certification registry to request as evidence |
| EU GDPR Art. 28 (processor obligations / DPA content) | https://gdpr-info.eu/art-28-gdpr/ | The required contents of a data processing agreement for personal data (route specifics to compliance/counsel) |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **filesystem**: open the MSA, DPA, SLA exhibit, and security schedule so each diligence area is read against the actual contract, not a summary.
- **fetch / web-fetch**: pull the vendor's public trust/security page, certification registry entry (e.g. CSA STAR), or standard-form terms to compare against what is presented.

Contract diligence turns on exact wording and produced evidence. Where a clause, exhibit, or certification cannot be read, mark it a gap/Unverified rather than assuming coverage.

## Troubleshooting

### Error: "Diligence passed but the vendor breach still cost us everything"
Cause: The liability cap and its carve-outs were read separately, so a low general cap that swallowed data-breach and indemnity liability slipped through.
Solution: Always read the cap with its exceptions. For high/critical data vendors, require a data-breach super-cap and carve IP/confidentiality/data indemnities out of the general cap. Re-run the liability-cap adequacy test in the checklist.

### Error: "The security clause looked great but the vendor had no real controls"
Cause: Contract language was mistaken for verified security posture; no evidence was required.
Solution: A security clause is a promise, not proof. Require and review evidence (SOC 2 Type II, ISO 27001, pen-test summary) and mark the area Unverified until produced. Keep the contract gap and the evidence gap as separate line items with different owners.

### Error: "We couldn't get our data out / were auto-renewed against our will"
Cause: Exit terms were under-diligenced — data-return format/window, deletion certification, transition assistance, and auto-renewal notice were not scrutinized.
Solution: Diligence the exit as hard as the entry: require usable-format data return within a defined window, certified deletion, a transition-assistance period for critical vendors, and flag any auto-renewal with a long opt-out notice as a lock-in risk to renegotiate.
