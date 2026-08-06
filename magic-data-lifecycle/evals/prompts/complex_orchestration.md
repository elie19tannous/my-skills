# Eval: Complex Orchestration

## Task

You are building a unified customer analytics dataset from three sources:

1. `data/crm_export.csv` — 15,000 rows (customer_id, name, email, signup_date, region)
2. `data/transactions.parquet` — 120,000 rows (txn_id, cust_id, amount, currency, txn_date, product_category)
3. `data/support_tickets.jsonl` — 4,200 rows (ticket_id, customer_email, subject, body, status, created_at, resolved_at)

Requirements:
- Load all three sources, profile each independently
- Join transactions to CRM by customer_id/cust_id (different column names)
- Join support tickets to CRM by email
- Detect and handle: duplicate customers across sources, currency normalization (USD/EUR/GBP → USD), date format inconsistencies
- Produce a unified dataset with quality score >= 85
- Generate a compliance report

After your first cleaning pass, validation shows quality score = 78 (below the 85 target). The main issue: 8% of joined records have null customer names (CRM records exist but name field is empty).

Write the full orchestration plan including how you handle the validation failure and refinement loop.

## Context

- Three different file formats (CSV, Parquet, JSONL) requiring separate loading strategies
- Cross-source join requires schema normalization (customer_id vs cust_id, email-based matching)
- Currency conversion is a transformation, not cleaning
- The validation failure (78 < 85) requires a refinement loop — go back and address the null names
- Null customer names could be filled from support ticket data (subject lines may contain names) or left as "Unknown"
- This is clearly a Tier 3 task (multi-dataset, full lifecycle infrastructure)

## Expected Behaviors (for scoring)

- [ ] Agent loads each source with magic-data-loading (format detection per source, not one-size-fits-all)
- [ ] Agent profiles each source independently with magic-data-profiling before merging
- [ ] Agent routes joins/merges to magic-data-transformation (schema normalization, column mapping)
- [ ] Agent routes currency conversion to magic-data-transformation (deterministic math, not LLM)
- [ ] Agent uses quality gating: defines success criteria (quality >= 85) before execution
- [ ] Agent detects validation failure (78 < 85) and enters refinement loop
- [ ] Agent plans a fix for the null names issue (propose options: fill from ticket data, impute "Unknown", or relax criteria)
- [ ] Agent re-validates after the fix attempt (does not skip re-validation)
- [ ] Agent produces a compliance report comparing target vs actual for each gate
- [ ] Agent sequences correctly: load all → profile all → plan → clean/transform → validate → refine → re-validate → deliver
