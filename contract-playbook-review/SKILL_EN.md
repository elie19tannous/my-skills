---
name: contract-playbook-review
description: Review a contract against a firm's negotiation playbook — the pre-agreed set of preferred positions, acceptable fallbacks, hard redlines (never-accept terms), and escalation triggers — and produce a clause-by-clause deviation report that says, for each material term, whether it is at target, within fallback, off-playbook, or a redline breach, with the exact counter-move to take. Use when a user asks you to review a contract "against our playbook," check a redline, decide what to push back on, mark which terms need partner/business/legal escalation, or triage an inbound draft (NDA, MSA, SaaS/DPA, lease, employment, vendor) before negotiation. Covers playbook loading, clause extraction and mapping, position grading (target/fallback/off-playbook/redline), escalation-trigger detection, and a negotiation worklist. Do NOT treat playbook rules as legal advice for a specific deal, and do NOT auto-accept a term as compliant just because similar wording appears in the playbook — a fallback is only met when the actual clause language falls within the stated band, which requires reading the clause.
license: MIT
compatibility: No network required for the workflow or the offline clause/trigger scanner (Python stdlib only). Loading the firm's own playbook file is a local read; live legal research to update a position is optional and separate.
---

# Contract Playbook Review

## Instructions

> **Core rule:** a clause is "playbook-compliant" only when its ACTUAL language falls inside a stated position band (target or an acceptable fallback). A clause is NOT compliant just because the playbook has an entry for that topic, and a clause is NOT a breach just because it deviates from the target — deviation within the fallback band is expected and acceptable. Grade the real language against the band; never auto-pass or auto-fail from the topic alone. A hard redline breach is never "compliant," no matter how the counterparty frames it.

### Step 1: Load and Pin the Playbook
Before touching the contract, pin what the playbook says. A playbook is a structured set of positions, not free text.

| Element | What it defines |
|---------|-----------------|
| Target position | The firm's preferred/opening ask for a term (e.g. "liability cap = 12 months' fees") |
| Fallback band | Acceptable range the firm will concede to without escalation (e.g. "24 months' fees, or 2x fees, still OK") |
| Hard redline | A term the firm will never accept (e.g. "no uncapped indemnity," "no unilateral termination for convenience by vendor") |
| Escalation trigger | A condition that must be routed to a named approver (partner / business owner / GC / risk) before agreeing |
| Owner / approver | Who signs off when a term is off-playbook or a trigger fires |

Confirm the **contract type** (NDA, MSA, SaaS, DPA, lease, employment, vendor) and load the matching playbook section. If no playbook is supplied, say so — you cannot grade against a playbook you do not have; do not invent positions.

### Step 2: Extract the Contract's Material Clauses
Break the contract into the clauses the playbook actually governs. You are mapping the document onto the playbook, not summarizing the whole contract.

- Pull each **material term** the playbook has a position on: liability/cap, indemnity, IP ownership/licence, termination, confidentiality term, data protection, warranties, payment/pricing, governing law/venue, assignment, non-compete/exclusivity, SLA/remedies, insurance.
- Capture each clause's **location** (section/§/page) and its **operative language**, not a paraphrase — grading needs the real words.
- Flag topics the playbook covers that are **absent** from the contract (a missing liability cap is itself a deviation — silence often defaults to uncapped).

The bundled `scripts/clause_scanner.py` gives a first-pass split, tags likely clause topics, and surfaces redline/escalation trigger phrases; treat its output as a worklist, not a verdict.

### Step 3: Map Each Clause to Its Playbook Position
For every extracted clause, find the playbook entry that governs it and classify the mapping.

| Mapping | Meaning |
|---------|---------|
| Governed | The playbook has a target/fallback/redline for this exact term |
| Governed-adjacent | The playbook covers a related term; apply by analogy but note the stretch |
| Ungoverned | The clause has no playbook position → note it; do not invent a band |
| Missing-from-contract | The playbook governs a term the contract omits → treat the omission as the counterparty's position (often adverse) |

### Step 4: Grade the Position (the load-bearing step)
For each governed clause, grade the ACTUAL language against the band:

| Grade | Definition | Action |
|-------|------------|--------|
| At-target | Language meets the firm's preferred position | Accept as-is |
| Within-fallback | Language is off-target but inside the acceptable band | Accept, or push once toward target if cheap; no escalation needed |
| Off-playbook | Language is worse than the fallback band but not a hard redline | Counter to the fallback; flag for the term owner |
| Redline-breach | Language hits a never-accept term | HIGH severity; do NOT concede — counter to fallback or reject; escalate |
| Escalation-triggered | A stated trigger condition is present (e.g. amount over threshold, non-standard indemnity, data export) | Route to the named approver BEFORE agreeing, regardless of grade |

A clause can be within-fallback AND escalation-triggered at once (e.g. within the cap band but the deal size trips a partner-review trigger). Escalation is orthogonal to grade — never suppress a trigger because the grade looks fine. When language is ambiguous between two grades, grade DOWN (toward off-playbook/redline), never up.

### Step 5: Produce the Deviation / Negotiation Worklist
Deliver a table sorted by severity (redline breaches and fired triggers first, then off-playbook, then within-fallback, then at-target), each row:

| Field | Content |
|-------|---------|
| Location | Section/§/page of the clause |
| Term | The material term (liability cap, indemnity, termination, ...) |
| Grade | At-target / within-fallback / off-playbook / redline-breach |
| Escalation | None / trigger name + approver |
| Counter-move | The exact ask: accept / push to target / counter to fallback / reject / escalate to X |
| Fallback language | The specific clause text to propose (from the playbook), where the playbook supplies one |

End with a headline: "X of Y governed terms at-target or within-fallback; Z off-playbook, W redline breaches, V escalations required." Do not clear a contract for signature while any redline breach is open or any escalation trigger is unrouted.

### Step 6: Anti-Fabrication & Judgment Discipline
This skill decides what a firm can and cannot accept — so it must not invent the firm's positions or paper over a breach.

- If the playbook does not cover a term, say "ungoverned — no playbook position," never guess a target or fallback.
- Do not soften a redline-breach to "off-playbook" to make a deal look closable — a never-accept term is a hard stop until the owner decides otherwise.
- Do not suppress an escalation trigger because the commercial team is in a hurry; the trigger exists precisely for the busy path.
- The playbook is a default, not deal-specific legal advice. Where the specific deal's risk differs from the standard case, flag it for human judgment rather than mechanically applying the band.

## Examples

### Example 1: Inbound Vendor MSA
**Input:** "Review this vendor's MSA against our SaaS playbook and tell me what to push back on."
**Output:** Mapped 14 governed terms. 9 at-target or within-fallback (accept). Liability: vendor proposes uncapped indemnity for IP infringement — REDLINE BREACH (playbook: indemnity capped at the greater of fees paid / $1M); HIGH severity, do not concede, counter with the capped language. Termination: vendor-only termination for convenience on 30 days — off-playbook (playbook requires mutual or none); counter to mutual-90-days from the fallback. Data export to a non-adequacy country present → escalation trigger "cross-border data" fires → route to GC before agreeing even though the DPA clause is otherwise within-fallback. Payment net-15 is within-fallback (target net-30, band net-15 to net-45) — accept. Headline: 9/14 clear; 2 off-playbook, 1 redline breach, 1 escalation to GC. Do not sign until the uncapped indemnity is fixed and GC clears the data export.

### Example 2: Redline of an NDA
**Input:** "Is this mutual NDA within our standard? What needs partner sign-off?"
**Output:** 6 governed terms mapped. Confidentiality term: 5 years — within-fallback (target 3 years, band up to 5). Definition of Confidential Information: no carve-outs for independently-developed or already-known info — off-playbook (playbook requires the four standard exclusions); counter with the standard carve-out language. Residuals clause absent — missing-from-contract, add the playbook's standard residuals clause. Governing law = a foreign forum with mandatory arbitration seat abroad → escalation trigger "non-standard forum" → partner sign-off required before acceptance. Headline: 3/6 within band, 1 off-playbook, 1 missing term, 1 partner escalation. Push the carve-outs and residuals; get partner sign-off on the forum.

### Example 3: Triaging a Draft Before Negotiation
**Input:** "We got a 40-page services agreement. Triage it against the playbook so I know where the fights are before the call."
**Output:** Ran the clause scanner to split and topic-tag; mapped 22 governed terms. 15 at-target/within-fallback — no action. 4 off-playbook: uncapped consequential-damages exclusion missing, IP assignment (should be licence) too broad, auto-renewal with 90-day notice (band ≤ 60), audit rights one-directional. 1 redline breach: unlimited liability for data breach (playbook hard cap applies). 2 escalation triggers: total contract value over the $500k partner-review threshold, and a most-favored-customer pricing clause that trips the "non-standard pricing" trigger to the business owner. Delivered the worklist sorted with the redline and two triggers at the top, each with the counter-move and the exact fallback language to paste. Now you know the three real fights before the call.

## Bundled Resources

### References
- `references/playbook-structure.md` -- How a negotiation playbook is structured: target vs fallback band vs hard redline vs escalation trigger, per-term entries, owners/approvers, and how to load one for a given contract type. Consult when defining or loading the playbook in Step 1.
- `references/grading-rubric.md` -- The grading rubric (at-target / within-fallback / off-playbook / redline-breach) plus the orthogonal escalation-trigger layer, the grade-DOWN-when-unsure rule, and the deviation-report format. Consult when grading clauses and writing the worklist.

### Scripts
- `scripts/clause_scanner.py` -- Offline first-pass clause/trigger scanner (Python stdlib only, no network). Splits a plaintext contract into candidate clauses, tags likely clause topics (liability, indemnity, termination, IP, confidentiality, data protection, payment, governing law, assignment, non-compete, insurance), and surfaces phrases that commonly signal a hard redline (e.g. "uncapped," "unlimited liability," "sole discretion," "irrevocable," "perpetual," "indemnify and hold harmless") or an escalation trigger (dollar thresholds, cross-border data, exclusivity, most-favored-customer). It produces a mapping/triage worklist for HUMAN grading; it does NOT judge whether a clause is within a fallback band — that requires reading the clause against the actual playbook. Run: `python scripts/clause_scanner.py --help`

## Gotchas

- A playbook entry existing is NOT compliance. The biggest failure is marking a term "OK, we have a playbook position on that" without checking the actual clause language falls inside the band. Always grade the real words (Step 4).
- Deviation from the target is normal, not a breach. Within-fallback is an accept, not a fight. Do not burn negotiating capital pushing terms that are already inside the band.
- A missing clause is a position. Silence on a liability cap usually means uncapped; the counterparty's omission is their opening position, so treat missing-from-contract terms as deviations, not blanks.
- Escalation is orthogonal to grade. A clause can be perfectly within-fallback and still trip a trigger (deal size, cross-border data, exclusivity) that requires named sign-off. Never suppress a trigger because the grade looks clean.
- A redline is a hard stop, not a strong preference. Do not let "off-playbook" absorb a genuine never-accept term because the deal is attractive; escalate the redline, do not quietly concede it.
- The playbook is a default, not deal-specific advice. A standard band can be wrong for an unusual deal (regulated counterparty, unusual risk). Flag deal-specific risk for human judgment rather than mechanically applying the band.
- The scanner's topic/trigger detection is pattern-based: it will mis-tag some clauses and over-flag trigger words that are benign in context. Use it as a worklist, then grade with judgment against the real playbook.
- No playbook, no grading. If the firm's playbook is not supplied, you cannot grade against it — say so and request it; never fabricate the firm's positions.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| ABA — Contract Drafting & Negotiation resources | https://www.americanbar.org/groups/business_law/ | Standard-clause expectations and negotiation practice that inform sensible fallback bands |
| Practical Law / standard clause libraries (concept) | https://legal.thomsonreuters.com/en/products/practical-law | What a market-standard position looks like for common terms, to sanity-check a band |
| IACCM/WorldCC negotiated-terms research | https://www.worldcc.com/ | Which contract terms are most negotiated and most disputed — helps prioritize the worklist |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **filesystem**: open the firm's playbook file and the contract draft so clauses can be graded against the actual stated bands rather than assumed ones.
- **fetch / web-fetch**: pull a current market-standard reference or statute when deciding whether to update a playbook position (separate from the offline review pass).

The grading step requires the firm's real playbook and the contract's real language. Where the playbook is not supplied, request it rather than inventing positions.

## Troubleshooting

### Error: "Everything comes back 'ungoverned'"
Cause: No playbook (or the wrong contract-type section) was loaded, so there are no bands to grade against — the scanner only tags topics, it does not carry the firm's positions.
Solution: Load the correct playbook section for the contract type (NDA vs MSA vs lease each have different governed terms). Ungoverned is correct only for terms the playbook genuinely does not cover; it should shrink to a few once the right playbook is loaded.

### Error: "A within-fallback term got flagged as a fight"
Cause: The clause deviates from the target and was mistaken for a breach, when it is actually inside the acceptable fallback band.
Solution: Re-grade against the fallback band, not the target. Within-fallback is an accept; only counter it if pushing toward target is cheap. Reserve "fight" status for off-playbook and redline-breach terms.

### Error: "A redline was quietly conceded because the deal looked good"
Cause: A hard never-accept term was downgraded to off-playbook and negotiated away without the owner deciding.
Solution: Redlines are hard stops. Restore the redline grade, escalate to the named owner, and let them (not the deal pressure) decide whether to make an exception. When unsure between off-playbook and redline, grade DOWN to redline.
