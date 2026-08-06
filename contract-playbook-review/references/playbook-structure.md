# Playbook Structure — Targets, Fallbacks, Redlines, Triggers

A negotiation playbook is a structured set of positions the firm has pre-agreed
for recurring contract terms. It exists so a reviewer can triage a draft fast
and consistently without re-deciding the firm's risk appetite on every deal.

## The four position types (per term)

| Type | Question it answers | Example (liability cap) |
|------|---------------------|-------------------------|
| Target | What do we open with / prefer? | Cap = 12 months' fees |
| Fallback band | How far will we concede WITHOUT escalation? | Up to 24 months' fees, or 2x annual fees |
| Hard redline | What will we NEVER accept? | Uncapped liability; carve-outs that swallow the cap |
| Escalation trigger | What must a named person approve first? | Any cap above 24 months, or any deal > $500k |

Target and fallback describe a *band*: at-target is the top of the band,
within-fallback is anywhere inside it, off-playbook is below/worse than the band
but not yet a redline, and a redline breach is a hard stop.

## A per-term entry looks like

```
Term: Limitation of Liability
  target:    "aggregate cap = 12 months' fees paid in the prior 12 months"
  fallback:  "up to 24 months' fees, or 2x annual fees, whichever is lower"
  redline:   "no uncapped liability; no cap carve-out beyond the standard
              set (IP indemnity, confidentiality, willful misconduct)"
  trigger:   "cap > 24 months OR total contract value > $500k -> partner"
  owner:     "Deal partner (risk); GC for indemnity carve-outs"
  fallback_language: "<the exact clause text to paste when countering>"
```

Not every term needs all five. Some terms are redline-only ("never grant a
perpetual, irrevocable licence to our IP"), some are trigger-only ("any
cross-border personal-data transfer -> GC"), some are band-only.

## Loading the right section

Playbooks are organized by **contract type** because the governed terms differ:

| Contract type | Terms the playbook typically governs |
|---------------|--------------------------------------|
| NDA | Confidentiality term, definition + carve-outs, residuals, permitted use, return/destruction, forum |
| MSA / services | Liability cap, indemnity, IP, termination, SLA/remedies, warranties, insurance, assignment |
| SaaS / subscription | Availability SLA, data protection/DPA, security, price escalation, auto-renewal, exit/data return |
| DPA / data | Sub-processors, cross-border transfer, breach notice window, audit rights, deletion |
| Lease | Term/renewal, rent escalation, repair obligations, assignment/sublet, break clause |
| Employment | Non-compete scope, IP assignment, notice period, confidentiality, restrictive covenants |

Load the section matching the contract type before grading. A term that is
governed in one type may be ungoverned in another.

## Owners and approvers

Every off-playbook or triggered term routes to a named human. The playbook names
who: commonly the deal partner (legal risk), the business owner (commercial
terms like price/exclusivity), and the GC/DPO (data, indemnity, regulated
counterparties). The reviewer's job is to route, not to decide the exception.

## What the playbook is NOT

- It is not deal-specific legal advice. It is a default calibrated to the typical
  deal; an unusual counterparty or risk can make a standard band wrong.
- It is not a substitute for reading the clause. A band tells you the acceptable
  range; only the actual clause language tells you whether a clause is inside it.
- It is not static. When the market or the law moves, positions should be
  updated — but that is a separate maintenance task, not part of a review pass.
