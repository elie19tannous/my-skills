# Grading Rubric & Deviation Report

The load-bearing step of a playbook review is grading each governed clause's
ACTUAL language against the playbook band — and, separately, checking whether an
escalation trigger fires. The two are orthogonal: a clause can be within-fallback
and still trigger mandatory sign-off.

## Grade against the band

| Grade | Rule | Default action |
|-------|------|----------------|
| At-target | Language meets the preferred position | Accept as-is |
| Within-fallback | Off-target but inside the acceptable band | Accept (push to target only if cheap) |
| Off-playbook | Worse than the band, not a hard redline | Counter to fallback; flag term owner |
| Redline-breach | Hits a never-accept term | HIGH; do not concede; escalate |

Rules:
- Grade the real clause language, never the topic. A playbook entry existing is
  not compliance.
- Deviation from target is normal — within-fallback is an accept, not a fight.
- When language is ambiguous between two grades, grade DOWN (toward
  off-playbook / redline). Over-accepting is the failure mode this guards against.
- A missing clause the playbook governs is a deviation, not a blank: treat the
  omission as the counterparty's (usually adverse) position.

## The escalation layer (orthogonal to grade)

A trigger is a condition that must be routed to a named approver BEFORE agreeing,
regardless of how the clause grades:

| Trigger example | Routes to |
|-----------------|-----------|
| Total contract value over threshold | Deal partner |
| Liability cap above the fallback ceiling | Deal partner / risk |
| Cross-border personal-data transfer | GC / DPO |
| Exclusivity or most-favored-customer pricing | Business owner |
| Non-standard forum / mandatory foreign arbitration | Partner |
| Indemnity carve-out beyond the standard set | GC |

Never suppress a trigger because the grade looks clean or the team is in a hurry.
The trigger exists for exactly the fast, attractive deal.

## Deviation / negotiation report

Table sorted by severity:
redline-breach & fired triggers → off-playbook → within-fallback → at-target.

Columns:

| Location | Term | Grade | Escalation | Counter-move | Fallback language |
|----------|------|-------|------------|--------------|-------------------|

- **Counter-move** vocabulary: accept / push to target / counter to fallback /
  reject / escalate to <owner>.
- **Fallback language**: paste the exact playbook clause text where one exists,
  so the negotiator can drop it straight into the redline.

Headline count:
"X/Y governed terms at-target or within-fallback; Z off-playbook, W redline
breaches, V escalations required."

Do not clear a contract for signature while any redline breach is open or any
escalation trigger is unrouted.

## Anti-fabrication

- No playbook position for a term → "ungoverned," never a guessed band.
- Never downgrade a redline to off-playbook to make a deal closable.
- Never suppress a trigger for speed.
- The playbook is a default; flag deal-specific risk for human judgment rather
  than mechanically applying the band.
