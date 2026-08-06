---
name: matter-intake-scoping
description: Run a structured intake and scoping pass on a NEW legal matter before the firm commits to it — capture the facts, identify every party and their role, extract and diary the deadlines, run a conflicts-of-interest check, define the scope of the engagement, and produce a reasoned fee estimate. Use when a prospective client walks in or emails, when opening a new file, when triaging an inbound lead, when a partner asks "should we take this and what will it cost?", or when standardizing intake so nothing (a limitation date, a conflicted party, an out-of-scope expectation) slips through. Covers the intake questionnaire, a party/conflicts matrix, a deadline/limitation register, a scope-in/scope-out definition, and a fee-estimate build-up. Do NOT treat this as legal advice on the merits, do NOT let a fee estimate go out without the scope assumptions attached, and do NOT clear conflicts from names alone — a conflicts check requires searching the firm's actual client/adverse-party records, which this skill flags for but cannot perform on its own.
license: MIT
compatibility: No network required for the workflow or the bundled intake completeness checker (Python stdlib only). Running the conflicts search itself requires access to the firm's client-matter database and is separate from this skill.
---

# Matter Intake & Scoping

## Instructions

> **Core rule:** intake is a GATE, not a formality. A matter is not "open" until (1) the facts and parties are captured, (2) conflicts are cleared against the firm's real records, (3) every hard deadline is diaried, (4) scope is written down, and (5) a fee estimate ties to that scope. Skipping any gate is how firms miss a limitation date, act against an existing client, or blow a budget. Never present a fee number without its scope assumptions attached.

### Step 1: Capture the Facts
Get the story before you get the paperwork. Interview or read the inbound and record the who/what/when/where/why.

- Prefer a **neutral chronology**: dated events in order, each one atomic ("2024-03-03 — contract signed"; "2024-09-12 — payment demand sent"). One event, one line.
- Separate **fact** from **the client's characterization** ("they cheated us" is a conclusion; "invoice unpaid 90 days" is a fact). Capture both, label which is which.
- Note **what you don't yet know** — missing documents, unconfirmed dates, unnamed parties — as an open-items list. Gaps drive the next request, they do not get guessed.
- Record the client's **goal and success criteria** in their words (settlement, injunction, a clean contract, a defense). Scope and fee both flow from the goal.

The bundled `scripts/intake_check.py` scores a filled intake form for completeness and flags empty mandatory fields; treat its output as a checklist, not a sign-off.

### Step 2: Identify Every Party and Their Role
List everyone the matter touches — not just the two obvious sides.

| Field | Content |
|-------|---------|
| Legal name | Full legal/registered name, plus any trading name or alias |
| Type | Individual / company / partnership / public body / trust |
| Role | Client / adverse party / co-defendant / witness / insurer / guarantor / related entity |
| Relationship | To the client and to each other (parent/subsidiary, spouse, director, etc.) |
| Identifiers | Company/registration number, ID where lawfully held — needed for a clean conflicts search |

Capture **related and beneficially-interested** parties (parent companies, directors, spouses, guarantors). Conflicts hide in the entities you didn't think to list.

### Step 3: Run the Conflicts Check
The step that protects the firm. A conflicts check is a **search of the firm's actual client and adverse-party records** for every party from Step 2 — not a judgment from memory.

| Outcome | Meaning | Action |
|---------|---------|--------|
| No hit | No party matches an existing/former client or adverse party | Record the clear search; proceed |
| Positive conflict | A party is (or is adverse to) a current/former client | STOP; escalate to the conflicts partner — do not open the file |
| Potential / related-party conflict | A parent, affiliate, or connected person hits | Flag for partner review; may need an informed-consent waiver |
| Business/commercial conflict | Not a legal conflict but a relationship/reputational one | Flag for partner judgment |

Rules:
- Search **every** party and every alias/related entity, not just the client and the main opponent.
- A clear result must come from the **records**, not from "I don't recall a conflict." If you cannot access the client-matter database, mark conflicts **Not cleared — search pending**, never "clear."
- Where a conflict is waivable, note that informed written consent is required before proceeding; do not assume it.

### Step 4: Extract and Diary the Deadlines
Miss one and it is a negligence claim. Pull every date that has consequences.

| Type | Examples |
|------|----------|
| Limitation / prescription | Statutory time bar to file a claim — the highest-stakes date |
| Contractual | Notice periods, cure periods, option/renewal dates, response windows |
| Procedural | Filing, service, response, appeal deadlines once litigation is live |
| Regulatory / statutory | Reporting, registration, objection windows |

- For each deadline record the **date, its source (what rule/clause sets it), and how it was calculated**, and diary it with a **lead-time reminder** before the drop-dead date.
- If a limitation date is **unknown or contested, flag it as HIGH risk** and resolve it before doing anything else — an approaching bar can override whether the firm even takes the matter.
- Never state a limitation date as settled without naming the rule and the trigger date it runs from.

### Step 5: Define the Scope (In and Out)
Ambiguous scope is the root of fee disputes and negligence exposure. Write it down.

- **In scope:** the specific work the firm will do, stated as deliverables/phases ("draft and negotiate the SPA," "file and prosecute the claim to first-instance judgment").
- **Out of scope:** what the firm is NOT doing, stated explicitly ("does not include tax advice," "does not include enforcement of any judgment," "excludes appeals"). The out-of-scope list prevents scope creep and assumption.
- **Assumptions:** the facts the scope and fee rely on ("assumes uncontested," "assumes one round of comments," "assumes documents provided by client"). If an assumption fails, the scope and fee change.
- **Dependencies from the client:** documents, decisions, approvals, and information the firm needs and when.

### Step 6: Build the Fee Estimate
The number that must never go out naked. Build it up from the scope, don't pluck it.

| Component | Content |
|-----------|---------|
| Basis | Fixed fee / hourly / capped / phased / contingency (subject to local rules) — and which |
| Build-up | Estimated hours × rate by phase/fee-earner, or the fixed-fee rationale |
| Disbursements | Court/filing fees, experts, agents, translation, travel — listed separately |
| Tax | VAT/sales tax shown separately, not baked in silently |
| Assumptions link | The estimate is expressly conditioned on the Step 5 scope and assumptions |
| Range & triggers | Give a range where uncertain, and name what would push it up (contested, extra rounds, new parties) |

Rules:
- **Always attach the scope and assumptions** to the number. A fee figure with no scope is a future dispute.
- State clearly whether the figure is an **estimate or a quote/fixed fee** — the difference is legally and commercially significant.
- Where the matter is uncertain, give a **range with the drivers**, not a single false-precision number.

### Step 7: Produce the Intake & Scoping Summary
Deliver a single decision-ready pack:

| Section | Content |
|---------|---------|
| Matter summary | Client, goal, one-paragraph facts, matter type |
| Parties & conflicts | Party matrix + conflicts result (clear / positive / pending) |
| Deadlines | Deadline register with the limitation date called out at top |
| Scope | In / Out / Assumptions / Client dependencies |
| Fee | Basis, build-up, disbursements, tax, range and triggers |
| Recommendation | Take / decline / take-subject-to (conflict waiver, retainer, limitation resolved) |

End with an explicit **open / decline / hold** recommendation and the conditions attached. Do not mark a matter ready to open while any conflict is uncleared or any limitation date is unresolved.

### Step 8: Anti-Assumption Discipline
Intake fails silently when gaps get filled with guesses.

- If conflicts were not searched against the real database, say "conflicts not cleared — search pending," never "no conflicts."
- Do not invent a limitation date, a party's registration number, or a fee figure to make the pack look complete — flag the gap and request it.
- Do not soften a positive conflict or an approaching limitation bar to keep a client; those are the exact risks intake exists to catch.

## Examples

### Example 1: Inbound Commercial Dispute
**Input:** "A prospective client emailed — supplier won't pay a €180k invoice. Should we take it and what will it cost?"
**Output:** Built a chronology of 7 dated events; separated facts from the client's "they're stalling deliberately" characterization. Party matrix lists the client, the supplier (Ltd + its parent group + the personal guarantor named in the contract) — 4 conflict-search targets, not 2. Conflicts flagged **pending** (I don't have database access) — must be cleared before opening. Limitation: contract claim, prescription runs from the missed payment date; ~4 years remain — not urgent but diaried with a 6-month lead reminder. Scope in: pre-action demand + negotiation + issue proceedings to first-instance judgment; out: enforcement of any judgment, insolvency steps. Fee: phased — Phase 1 (demand/negotiation) fixed at €X + VAT; Phase 2 (litigation) hourly range €Y–€Z driven by whether the guarantor contests. Recommendation: take **subject to** conflicts clearing on all 4 parties.

### Example 2: New Corporate / Transactional Matter
**Input:** "Open a file — we're acting for the buyer on a share purchase. Standard intake."
**Output:** Captured deal facts and the client's goal (clean acquisition, close in 8 weeks). Parties: buyer (client), target company, sellers (3 individuals), the target's subsidiary — all run for conflicts because we've acted for one seller before → **potential related-party conflict flagged to the conflicts partner**; may need a waiver. Deadlines: exclusivity/lock-out expiry (contractual, 45 days) and a financing long-stop date diaried. Scope in: due diligence, SPA draft/negotiate, disclosure, completion; out: tax structuring (referred to tax team), post-completion integration, any competition filing unless triggered. Fee: capped fee to signing + hourly beyond, assumptions stated (one target, one jurisdiction, two rounds of SPA comments). Recommendation: hold — do not open until the seller-side conflict is resolved.

### Example 3: Family Matter with a Live Deadline
**Input:** "Walk-in client, wants to respond to a divorce petition she was served."
**Output:** Facts and goal captured. Parties: client, spouse, and (flagged) any minor children whose interests bear on the matter. Conflicts run on client and spouse — **cleared against records** (no prior instruction either side). Deadline is the headline: the **response/acknowledgment deadline on the served petition is a HIGH-severity procedural date** — calculated from the service date, only 9 days remain, diaried with an immediate reminder and escalated first. Scope in: file the response and represent to interim hearing; out: financial-remedy/asset division (separate phase and fee), children arrangements (separate). Fee: fixed fee for the urgent response step, hourly thereafter with a range. Recommendation: **take and act now** — the response deadline dominates; get the retainer signed today so we can file in time.

## Bundled Resources

### References
- `references/intake-questionnaire.md` -- The full structured intake questionnaire: facts/chronology, parties and roles, conflicts targets, deadlines, client goal, scope, and the information/documents to request. Use as the interview script and the file-opening checklist.
- `references/scoping-and-fees.md` -- The scoping and fee-estimate playbook: writing scope-in/scope-out/assumptions, the deadline & limitation register format, the fee build-up (basis, hours×rate/fixed, disbursements, tax, range & triggers), and the estimate-vs-quote distinction. Consult when defining scope and pricing a matter.

### Scripts
- `scripts/intake_check.py` -- Offline intake completeness checker (Python stdlib only, no network). Reads a filled intake form (simple `key: value` text or JSON) and reports which mandatory intake fields (client, parties, conflicts-status, limitation date, scope, fee-basis, etc.) are present, empty, or missing, plus warnings for high-risk blanks (e.g. conflicts not cleared, limitation date absent). It scores completeness and lists blockers; it does NOT run the conflicts search or judge the merits. Run: `python scripts/intake_check.py --help`

## Gotchas

- Intake is a gate, not paperwork. The failure mode is treating it as a form to backfill after work starts — by then a conflict or a limitation date may already be a problem. Clear the gates before opening.
- Conflicts are cleared from records, not memory. "I don't think we've acted against them" is not a conflicts check. Search every party and every related entity against the firm's actual database; if you can't, the status is "pending," not "clear."
- List the parties you didn't think of. Parents, subsidiaries, directors, spouses, guarantors, insurers — conflicts and liabilities hide in the entities left off the obvious two-sided list.
- The limitation/prescription date is the highest-stakes item on the file. If it is unknown or contested, resolve it first — an approaching bar can decide whether the firm even takes the matter and is a classic negligence trap.
- A fee number without scope is a future dispute. Never send an estimate without its scope-in, scope-out, and assumptions attached, and be explicit about estimate vs fixed quote.
- Scope-out is as important as scope-in. Unstated exclusions become client expectations. Write down what the firm is NOT doing.
- Facts are not the client's conclusions. "They defrauded us" is a characterization; capture the underlying dated events separately so scope and merits aren't built on a label.
- Don't fill gaps with guesses to look complete. A missing registration number, unconfirmed date, or absent conflicts result is an open item to request — inventing it defeats the purpose of the gate.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| ABA Model Rule 1.7 (concurrent conflicts of interest) | https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_7_conflict_of_interest_current_clients/ | The duty to check for and manage conflicts before acting for a client — the ethical basis for Step 3 |
| ABA Model Rule 1.5 (fees) | https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_1_5_fees/ | The requirement that fees be reasonable and, ideally, the basis communicated in writing — backdrop for the fee estimate and engagement scope |
| SRA Code of Conduct — client care & conflicts | https://www.sra.org.uk/solicitors/standards-regulations/code-conduct-solicitors/ | Client-care, information-on-costs, and conflict-check obligations at matter opening (E&W frame; adapt to your jurisdiction) |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **filesystem**: read the inbound documents, contracts, and served papers so facts, parties, and deadlines are extracted from the actual record rather than from a summary.
- **database / client-matter DB connector**: run the conflicts search against the firm's real client and adverse-party records — the only way to genuinely clear conflicts (Step 3).

The conflicts search must run against the firm's actual records. Where that database is not reachable, mark conflicts "pending" rather than clear.

## Troubleshooting

### Error: "The pack says conflicts are 'pending' and won't mark the matter ready to open"
Cause: The conflicts search was not run against the firm's client-matter records — this skill flags for the search but cannot perform it without database access.
Solution: Run every party and related entity from the party matrix through the firm's actual conflicts system. Once each returns a recorded result, update the status. "Pending" is the correct, safe status until a real search is done — it is designed to block file-opening until conflicts are genuinely cleared.

### Error: "The client wants a single fixed fee but the estimate came back as a range"
Cause: The matter has uncertainty (contested opponent, unknown document volume, extra parties) that a single number would misrepresent.
Solution: Either narrow the scope until a fixed fee is defensible (e.g. fix Phase 1, hourly beyond) or present the range with its named drivers so the client sees what moves the number. Do not collapse genuine uncertainty into false precision — an under-scoped fixed fee is a loss or a dispute waiting to happen.

### Error: "A limitation date is flagged HIGH but nobody has confirmed it"
Cause: The time bar is unknown or contested, which is the single highest-risk state a new matter can be in.
Solution: Resolve it before any other work — identify the governing limitation rule, the trigger date it runs from, and compute the drop-dead date, then diary it with lead-time reminders. If it cannot be confirmed quickly and the bar may be near, escalate immediately; an imminent limitation date can change whether the firm accepts the matter at all.
