# Canonical Sources — magic-linguistic-tokenize

Maintainer-facing reading list. Snapshot 2026-04-23.

## Foundational tokenization papers

- **Sennrich, R., Haddow, B., & Birch, A.** (2016). *Neural Machine Translation of Rare Words with Subword Units*. ACL. — Origin of BPE for NMT.
- **Kudo, T.** (2018). *Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates*. ACL. — Origin of Unigram LM tokenization.
- **Kudo, T., & Richardson, J.** (2018). *SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing*. EMNLP demo.
- **Provilkov, I., Emelianenko, D., & Voita, E.** (2020). *BPE-Dropout: Simple and Effective Subword Regularization*. ACL.

## Fertility, fairness, and tokenizer evaluation

- **Rust, P., Pfeiffer, J., Vulić, I., Ruder, S., & Gurevych, I.** (2021). *How Good is Your Tokenizer? On the Monolingual Performance of Multilingual Language Models*. ACL.
- **Petrov, A., et al.** (2023). *Language Model Tokenizers Introduce Unfairness Between Languages*. NeurIPS.
- **Ahia, O., et al.** (2023). *Do All Languages Cost the Same? Tokenization in the Era of Commercial Language Models*. EMNLP.
- **Land, S., & Bartolo, M.** (2024). *Fishing for Magikarp: Automatically Detecting Under-trained Tokens in Large Language Models*. EMNLP.

## Vocabulary extension methods

- **Dobler, K., & de Melo, G.** (2023). *FOCUS: Effective Embedding Initialization for Monolingual Specialization of Multilingual Models*. EMNLP.
- **Liu, Z., Winata, G. I., et al.** (2024). *OFA: A Framework of Initializing Unseen Subword Embeddings for Efficient Large-scale Multilingual Continued Pretraining*. NAACL.
- **Wang, X., et al.** (2025). *HyperOfa: Hypernetwork-based Vocabulary Adaptation for Cross-Lingual Transfer*. arXiv preprint.
- **Pfeiffer, J., et al.** (2020). *MAD-X: An Adapter-Based Framework for Multi-Task Cross-Lingual Transfer*. EMNLP.
- **Hu, E. J., et al.** (2021). *LoRA: Low-Rank Adaptation of Large Language Models*. ICLR.

## Low-resource & multilingual practical references

- **Costa-jussà, M. R., et al. (NLLB Team)** (2022). *No Language Left Behind: Scaling Human-Centered Machine Translation*. arXiv. — NLLB-200 tokenizer + training recipe.
- **Joshi, P., et al.** (2020). *The State and Fate of Linguistic Diversity and Inclusion in the NLP World*. ACL.
- **Adelani, D. I., et al.** (2022, 2024). *MasakhaNER 2.0: Africa-centric Transfer Learning for Named Entity Recognition*. ACL.
- **Conneau, A., Khandelwal, K., et al.** (2020). *Unsupervised Cross-lingual Representation Learning at Scale (XLM-R)*. ACL.

## Tokenizer libraries

- **SentencePiece** (Google): https://github.com/google/sentencepiece
- **HuggingFace tokenizers** (Rust): https://github.com/huggingface/tokenizers
- **tiktoken** (OpenAI, BPE): https://github.com/openai/tiktoken
- **Mamba / X-LSTM tokenizers**: experimental; check per-model docs.

## Refresh procedure

- Cached fertility baselines: snapshot 2026-04-23. Refresh quarterly.
- Vocabulary-extension methods: ICLR / ACL / EMNLP yearly cycle; review September.
- New tokenizer family releases (Llama-N, GPT-N): re-baseline within 30 days.
