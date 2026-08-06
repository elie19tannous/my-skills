# Contamination Audit (Two-Sided) — Reference

Loaded by `magic-linguistic-corpus` Step 6.

## Two sides of contamination

1. **(a) Train mix vs your eval set.** Easy: you control both sides. Use 13-gram exact match (the standard from GPT-3) plus dedup-style MinHash for paraphrase contamination.
2. **(b) Your eval set vs the base model's pretrain.** Hard: pretrain is often unknown. Use proxies:
   - Is FLORES-200 (or your specific eval) in The Pile? (Often yes for English splits.)
   - Is the eval text on Wikipedia / Common Crawl (which dominate most pretrains)?
   - Is the eval set's release date PRIOR TO the model's training cutoff?

Skipping (b) is the most common contamination failure — you compute "clean" eval scores against a base that already memorized the eval.

## 13-gram exact match (standard)

The GPT-3 / OpenAI / NLLB convention. For each (eval-text, train-text) pair: count distinct 13-token shingles in the eval that appear verbatim in train. Threshold for "contaminated":
- 0% — pristine.
- 0-2% — acceptable; report.
- 2-10% — meaningful contamination; flag in model card.
- > 10% — eval is compromised; rewrite or use a different split.

For low-resource where 13-gram may be too long for short eval items, also report 7-gram and 5-gram counts.

## MinHash for paraphrase contamination

Exact 13-gram match misses paraphrased contamination (paraphrase the eval into the training data — common in synthetic-data leakage). MinHash with threshold 0.7-0.8 catches this.

## Common contamination patterns

| Pattern | Example | Mitigation |
|---|---|---|
| Eval set IS in pretrain | FLORES-200 in The Pile | Use a held-out, dated-after-training-cutoff alternative (NTREX-128 for many directions) |
| Eval source IS in train | Wiki paragraphs in eval, Wiki in train | Filter Wiki from train OR replace eval with non-Wiki |
| Synthetic data leakage | LLM generates eval-like patterns from in-context | Hold out eval prompts during synthesis |
| Test split released after training cutoff but its source pre-existed | "Held-out" set is repackaged old source | Verify the underlying text wasn't in pretrain |
| Cross-source repetition | News article appears in multiple crawls | Cross-source dedup (above) |

## Eval-set release date as a contamination proxy

Models pretrained before YYYY-MM-DD cannot have memorized text first published after YYYY-MM-DD. Use this as a strong signal:

| Eval set | Release date | Likely contamination in major models |
|---|---|---|
| FLORES-200 | 2022-07 | YES (in many post-2022 pretrains) |
| NTREX-128 | 2022-11 | LIKELY in recent models |
| Belebele | 2023-08 | LIKELY in 2024+ models |
| SEACrowd v2 | 2025 | UNLIKELY in pre-2025 models |
| AfroBench | 2024-12 | UNLIKELY in pre-2025 models |
| Your custom held-out | 2026-04 | NONE (if not published) |

## Reporting format

```json
{
  "eval_set": "FLORES-200 yor-eng",
  "train_mix": "yoruba-corpus-2026-04-23",
  "side_a": {
    "13gram_match_ratio": 0.012,
    "7gram_match_ratio": 0.045,
    "minhash_match_ratio": 0.018,
    "verdict": "MILD — flag in model card"
  },
  "side_b": {
    "eval_release_date": "2022-07",
    "base_model_pretrain_cutoff": "2024-04",
    "known_inclusions": ["The Pile contains FLORES test set"],
    "verdict": "LIKELY contaminated — consider NTREX or custom held-out"
  },
  "snapshot_date": "2026-04-23"
}
```

## What to do when contamination is found

- **In your control**: rewrite/replace the eval set; or filter the train mix.
- **Base-model contamination**: switch to alternative eval; or use the contaminated eval but report it transparently as a *lower bound* on model quality (since the model has seen it).
- **Document everything**: the model card MUST cite contamination findings. Hiding contamination is the unethical move.

## See also

- **Brown, T., et al.** (2020). GPT-3 paper — origin of 13-gram contamination check.
- **Carlini, N., et al.** (2021). *Extracting Training Data from Large Language Models*. USENIX Security.
- **Magar, I., & Schwartz, R.** (2022). *Data Contamination: From Memorization to Exploitation*. ACL.
- **Sainz, O., et al.** (2023). *NLP Evaluation in Trouble: On the Need to Measure LLM Data Contamination for each Benchmark*. EMNLP findings.
