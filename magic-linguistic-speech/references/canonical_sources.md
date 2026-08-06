# Canonical Sources — magic-linguistic-speech

Snapshot 2026-04-23.

## Field annotation tools
- **ELAN** (Max Planck Institute). https://archive.mpi.nl/tla/elan
- **Praat** (Boersma & Weenink). https://www.fon.hum.uva.nl/praat/
- **FLEx FieldWorks** (SIL International). https://software.sil.org/fieldworks/
- **SayMore** (SIL). https://software.sil.org/saymore/
- **Toolbox** (SIL legacy). https://software.sil.org/toolbox/

## Speech ML frameworks
- **Lhotse**: https://github.com/lhotse-speech/lhotse
- **ESPnet**: https://github.com/espnet/espnet
- **k2 / icefall**: https://github.com/k2-fsa/icefall
- **SpeechBrain**: https://github.com/speechbrain/speechbrain
- **NeMo** (NVIDIA): https://github.com/NVIDIA/NeMo

## ASR models
- **Pratap, V., et al.** (2024). *MMS: Massively Multilingual Speech*. arXiv.
- **Radford, A., et al.** (2022/2023). *Whisper: Robust Speech Recognition via Large-Scale Weak Supervision*. OpenAI.
- **Baevski, A., et al.** (2020). *wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations*. NeurIPS.

## TTS models
- **Kim, J., Kong, J., Son, J.** (2021). *VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech*. ICML.
- **Ren, Y., et al.** (2021). *FastSpeech 2: Fast and High-Quality End-to-End Text to Speech*. ICLR.
- **Coqui TTS / XTTS**: https://github.com/coqui-ai/TTS

## G2P
- **Lee, J., et al.** (2020). *Massively Multilingual Pronunciation Modeling with WikiPron*. LREC.
- **Gorman, K., et al.** (2020-2023). SIGMORPHON G2P shared task papers.

## Foundational phonetics + phonology
- **Ladefoged, P., & Johnson, K.** (2014). *A Course in Phonetics* (7th ed.). Cengage. — Authoritative IPA + phonetics reference.
- **Hayes, B.** (2009). *Introductory Phonology*. Wiley-Blackwell.
- **Ashby, M., & Maidment, J.** (2005). *Introducing Phonetic Science*. Cambridge.

## Field documentation + endangered-language ML
- **Gippert, J., Himmelmann, N., Mosel, U.** (eds.) (2006). *Essentials of Language Documentation*. De Gruyter Mouton.
- **Bird, S.** (2020). *Decolonising Speech and Language Technology*. COLING.

## Archives
- **ELAR** (Endangered Languages Archive): https://www.elararchive.org/
- **AILLA** (Archive of the Indigenous Languages of Latin America): https://ailla.utexas.org/
- **PARADISEC** (Pacific And Regional Archive for Digital Sources in Endangered Cultures): https://www.paradisec.org.au/
- **DELAMAN** (Digital Endangered Languages and Musics Archives Network): https://www.delaman.org/

## Refresh procedure

- MMS / Whisper: model checkpoints update; re-pin quarterly.
- Lhotse + transformers + torch: rapid; re-pin quarterly.
- ELAN / Praat / FLEx: stable; re-check annually.
- WikiPron: continuous updates; re-pull annually.
