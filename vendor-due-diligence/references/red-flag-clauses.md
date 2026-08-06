# Vendor Contract Red-Flag Clauses

Catalogue of the specific patterns that show up in bad vendor contracts, with
the fix/ask for each. Use when writing the "Ask" column of a gap report.

| Red flag | Why it matters | Fix / Ask |
|----------|-----------------|-----------|
| "Commercially reasonable security measures" with no named controls | Unenforceable — no concrete standard to hold the vendor to | Require named controls (encryption, access control, SDLC) + SOC 2/ISO evidence rights |
| Liability cap = 1-3 months' fees, no carve-outs | Token recovery after a real incident | Push for a cap proportionate to worst-case harm; carve out data-breach and IP/confidentiality indemnity |
| Data-breach losses fall under the general liability cap | The area most likely to cause real damage has the weakest remedy | Negotiate a data-breach super-cap or full carve-out |
| Service credits as the sole SLA remedy, no termination right | Vendor can under-perform indefinitely and only ever pay a small credit | Add a termination-for-chronic-failure clause (e.g. 3 breaches in 6 months) |
| "Data returned upon request" with no format, window, or deletion certificate | Real exit risk — you may never actually get usable data back | Require usable-format return within N days + certified deletion |
| Auto-renewal with a long opt-out notice window (e.g. 90 days pre-expiry, easy to miss) | Silent lock-in past the point you wanted to leave | Shorten the notice window or flag it prominently for calendaring |
| One-sided indemnity (only customer indemnifies vendor) | Asymmetric risk allocation with no reciprocal protection | Push for mutual indemnity, at minimum for IP and confidentiality |
| No DPA for personal data | Missing processing scope, sub-processor controls, deletion obligations | Require a DPA before signing; treat as a blocking gap for personal-data vendors |
| Uptime SLA measured as a "monthly average" | Can mask a multi-hour real outage inside a good-looking average | Ask how/by whom availability is measured; prefer rolling or per-incident measurement |
| No transition-assistance period for a critical vendor | Cliff-edge exit with no migration runway | Negotiate a defined transition period (e.g. 60-90 days) as part of exit terms |
| Sub-processors not listed / no objection right | Your data may flow to unknown third parties with no recourse | Require a current sub-processor list + a right to object to new ones |
| Confidentiality/liability terms don't survive termination | Protections vanish exactly when a dispute is most likely | Add an explicit survival clause for confidentiality, data protection, and liability |
