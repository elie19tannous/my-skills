# Contamination Detection — Reference

Loaded by `magic-linguistic-eval` Step 4. Cross-reference `magic-linguistic-corpus/references/contamination_audit.md` for the upstream methodology.

## Two-sided contamination

1. **(a) Train mix vs your eval set** — easy; you control both. Use 13-gram exact match (GPT-3 standard) + MinHash for paraphrase contamination.
2. **(b) Eval set vs base-model pretrain** — hard; pretrain often unknown. Use proxies:
   - Eval release date vs base-model training cutoff.
   - Known inclusions (FLORES in The Pile, etc.).
   - Membership inference attacks (recent research; experimental).

## Side (b) cheat sheet

| Eval set | Release | In likely pretrain |
|---|---|---|
| FLORES-200 | 2022-07 | YES — most 2023+ pretrains |
| NTREX-128 | 2022-11 | LIKELY in 2024+ |
| Belebele | 2023-08 | LIKELY in 2024+ |
| AfroBench | 2024-12 | UNLIKELY in pre-2025 models |
| SEACrowd v2 | 2025 | UNLIKELY in pre-2025 models |
| Custom held-out (post-2026) | n/a | NONE if not published |

For high-stakes commercial release: build a custom held-out (200-500 samples, post-cutoff) to get an uncontaminated number.

## Reporting

When contamination risk exists, ALWAYS report:
- "FLORES-200 score is a LOWER BOUND on quality (model has seen the test set during pretrain)."
- Provide alternative held-out scores when available.

## See also

- See `magic-linguistic-corpus/references/contamination_audit.md` for full methodology.
- **Sainz, O., et al.** (2023). *NLP Evaluation in Trouble*. EMNLP findings.
- **Magar, I., & Schwartz, R.** (2022). *Data Contamination*. ACL.
- **Brown, T., et al.** (2020). GPT-3 paper — 13-gram standard.
