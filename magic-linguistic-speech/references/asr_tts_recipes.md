# ASR / TTS Recipe Selection — Reference

Loaded by `magic-linguistic-speech` Step 3.

## ASR (Automatic Speech Recognition)

### Tool comparison (snapshot 2026-04-23)

| Tool | Languages | Best for |
|---|---|---|
| **MMS** (Meta Massively Multilingual Speech) | 1107 | Class 0-2 (broadest coverage) |
| **Whisper-large-v3** (OpenAI) | ~99 with quality variance | Class 3-5; English dominance |
| **NeMo** (NVIDIA) | varies | Production quality + speed |
| **SpeechBrain** | varies | Research + customization |
| **ESPnet** (k2/icefall integration) | varies (per-recipe) | Research + custom training |
| **wav2vec 2.0** | varies (per-checkpoint) | Self-supervised baseline |

### Per-class recommendations

| Class | Primary | Fallback / fine-tune |
|---|---|---|
| 0 | MMS direct | Community-collected audio + custom train |
| 1 | MMS direct | Whisper-large fine-tune (if has audio) |
| 2 | MMS direct OR Whisper-large fine-tune | Custom wav2vec |
| 3 | Whisper-large fine-tune OR MMS | Custom |
| 4 | Whisper-large or commercial | NeMo, ESPnet |
| 5 | Whisper-large or commercial | n/a |

### Whisper per-language quality (snapshot 2026-04-23)

Quality varies dramatically across Whisper's claimed 99 languages. Some "supported" languages have WER > 50%. Test before relying.

Common failure modes:
- Tone-language tone-mark stripping.
- Code-switching unmarked.
- Hallucination on silence / noise.
- Domain-narrow training (audiobook bias).

### MMS strengths + caveats

- 1107 languages with reported wav2vec-style speech encoder.
- Fine-tune-friendly.
- Per-language quality varies but coverage is unmatched.
- For class 0-2: MMS is the floor.

## TTS (Text-to-Speech)

### Tool comparison

| Tool | Audio needed for fine-tune | Quality |
|---|---|---|
| **VITS** | 5+ hours | High; mature |
| **FastSpeech2** | 10+ hours | High; faster training |
| **Tacotron2 + WaveGlow** | 10+ hours | High; mature |
| **XTTS** (Coqui) | minimal (zero-shot from speaker) | Variable; English-strong |
| **Bark** | n/a (pretrained, English-strong) | Variable; expressive |
| **MMS-TTS** | small | 1100+ languages from Meta |
| **Commercial APIs** | n/a | Best quality but cost + privacy |

### Per-class TTS recommendations

| Class | Recommendation |
|---|---|
| 0 (< 1 hr audio) | NOT VIABLE for fine-tune; consider speaker-adaptation or community recording effort |
| 1 (1-5 hr audio) | MMS-TTS or marginal VITS fine-tune; expect intelligible but unnatural output |
| 2-3 (5-20 hr audio) | VITS or FastSpeech2 fine-tune; usable quality |
| 4 (20+ hr audio) | VITS or commercial; high quality |
| 5 | Commercial best quality; VITS if open-source needed |

### Audio data requirements (recap)

Sub-1-hour audio: TTS not viable. Document this as a constraint.

## Pipeline integration

Both ASR and TTS pipelines consume Lhotse CutSets in 2026. See `references/lhotse_pipeline.md` for the Lhotse build pattern.

## Eval metrics

### ASR
- **WER** (Word Error Rate): standard but tokenization-dependent.
- **CER** (Character Error Rate): better for low-resource where word-segmentation is hard.
- **Per-language**: report both; CER more reliable for class 0-2.

### TTS
- **MOS** (Mean Opinion Score): human-rated naturalness; gold standard.
- **PESQ / STOI**: signal-quality metrics; correlate weakly with naturalness.
- **Speaker-similarity** (for voice cloning): verification-network score.

## Anti-patterns

- **Whisper for class 0-1**: MMS coverage is broader.
- **TTS fine-tune on < 1 hour**: unusable output.
- **WER on character-segmented language** (Mandarin, Khmer): use CER.
- **Skipping audio quality check** before training: noisy field recordings degrade ASR severely.

## See also

- **Pratap, V., et al.** (2024). *MMS: Massively Multilingual Speech*. arXiv.
- **Radford, A., et al.** (2022/2023). *Whisper: Robust Speech Recognition via Large-Scale Weak Supervision*. OpenAI tech report.
- **Kim, J., et al.** (2021). *VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech*. ICML.
- ESPnet: https://github.com/espnet/espnet
- NeMo: https://github.com/NVIDIA/NeMo
- Lhotse: https://github.com/lhotse-speech/lhotse
