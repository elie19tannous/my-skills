# Canonical Sources — magic-linguistic-transfer

Snapshot 2026-04-23.

## LoRA / PEFT family
- **Hu, E. J., et al.** (2021). *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR.
- **Dettmers, T., Pagnoni, A., Holtzman, A., Zettlemoyer, L.** (2023). *QLoRA: Efficient Finetuning of Quantized LLMs*. NeurIPS.
- **Liu, S.-Y., Wang, C.-Y., Yin, H., Molchanov, P., Wang, Y.-C. F., Cheng, K.-T., Chen, M.-H.** (2024). *DoRA: Weight-Decomposed Low-Rank Adaptation*. ICML.
- **Mangrulkar, S., et al.** (2022). PEFT library — https://github.com/huggingface/peft.

## Adapter family
- **Houlsby, N., et al.** (2019). *Parameter-Efficient Transfer Learning for NLP*. ICML.
- **Pfeiffer, J., et al.** (2020). *MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer*. EMNLP.
- **Pfeiffer, J., et al.** (2021). *AdapterFusion: Non-Destructive Task Composition*. EACL.
- **Parović, M., et al.** (2023). *Cross-Lingual Transfer with Target-Language-Ready Task Adapters* (BAD-X). ACL findings.
- HF Adapters library: https://github.com/adapter-hub/adapters

## Vocab extension (cross-reference with magic-linguistic-tokenize)
- **Dobler, K., & de Melo, G.** (2023). *FOCUS*. EMNLP.
- **Liu, Z., et al.** (2024). *OFA*. NAACL.
- **Wang, X., et al.** (2025). *HyperOfa*. arXiv.

## Source-language selection
- **Lin, Y.-H., et al.** (2019). *Choosing Transfer Languages for Cross-Lingual Learning*. ACL.
- **de Vries, W., Wieling, M., Nissim, M.** (2022). *Make the Best of Cross-lingual Transfer*. ACL.
- **Pires, T., Schlinger, E., Garrette, D.** (2019). *How Multilingual is Multilingual BERT?*. ACL.

## Catastrophic forgetting
- **Kirkpatrick, J., et al.** (2017). *Overcoming catastrophic forgetting in neural networks* (EWC). PNAS.
- **Aghajanyan, A., et al.** (2021). *Better Fine-Tuning by Reducing Representational Collapse*. ICLR.
- **Howard, J., & Ruder, S.** (2018). *ULMFiT*. ACL.

## Multilingual base models
- **Costa-jussà et al.** (2022). NLLB-200.
- **BigScience Workshop** (2022). BLOOM. arXiv 2211.05100.
- **Liu, Y., et al.** (2020). *Multilingual Denoising Pre-training for Neural Machine Translation* (mBART). TACL.
- **AyaTeam** (2024). Aya 23 / Aya 8B / Aya 35B series. Cohere.

## Tools
- Unsloth: https://docs.unsloth.ai/
- LLaMA-Factory: https://github.com/hiyouga/LLaMA-Factory
- Axolotl: https://github.com/OpenAccess-AI-Collective/axolotl
- TRL: https://github.com/huggingface/trl

## Refresh
- LoRA family stable; track DoRA / QLoRA-2 successors annually.
- Multilingual base landscape changes quickly; re-survey quarterly.
- Tools (Unsloth/LLaMA-Factory) iterate monthly; revisit speed benchmarks each release.
