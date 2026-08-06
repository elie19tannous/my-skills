# Lhotse Pipeline — Reference

Loaded by `magic-linguistic-speech` Step 4. Per Q8 resolution: ships 1-2 minimal recipe stubs with pinned versions.

## What Lhotse is

Lhotse (https://github.com/lhotse-speech/lhotse) is the standard 2026 representation for speech data + supervisions + features. ESPnet, k2/icefall, SpeechBrain, NeMo all consume Lhotse CutSets.

A **CutSet** = collection of **Cuts**. Each Cut = audio + metadata + supervisions (transcriptions, speaker, language, etc.) + optionally features (Mel-spec).

## Recipe stub 1: MMS fine-tune skeleton

Pinned: `transformers==4.50.x`, `torch==2.4.x`, `lhotse==1.30.x`, MMS-1B-FL102 checkpoint as of 2026-04-23.

```python
# mms_finetune_skeleton.py
# Phase 1 stub — refresh pinned versions before production use.

from lhotse import CutSet, Recording, SupervisionSegment
from transformers import (
    Wav2Vec2ForCTC, Wav2Vec2Processor, TrainingArguments, Trainer
)
import torch

# 1. Load pretrained MMS-1B (target-language adapter snapshot)
MODEL_NAME = "facebook/mms-1b-fl102"  # pinned 2026-04-23
processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)

# 2. Set target-language adapter (per MMS docs)
TARGET_LANG = "yor"  # Yoruba, ISO 639-3
model.load_adapter(TARGET_LANG)
processor.tokenizer.set_target_lang(TARGET_LANG)

# 3. Build Lhotse CutSet from your annotated data
cuts = CutSet.from_manifests(
    recordings="data/recordings.jsonl.gz",       # Lhotse recording manifest
    supervisions="data/supervisions.jsonl.gz",   # Lhotse supervision manifest
)

# 4. Convert Lhotse cuts to HF dataset format
# (snippet — full conversion requires dataloaders.py adapter)
def cut_to_features(cut):
    audio = cut.load_audio().squeeze()  # mono
    text = cut.supervisions[0].text
    inputs = processor(audio, sampling_rate=16000, text=text, return_tensors="pt")
    return inputs

# 5. Standard HuggingFace fine-tune loop
training_args = TrainingArguments(
    output_dir="./mms-yor-finetune",
    num_train_epochs=5,
    learning_rate=1e-5,
    per_device_train_batch_size=4,
    save_steps=500,
    eval_strategy="steps",
    eval_steps=500,
)
# trainer = Trainer(model=model, args=training_args, train_dataset=..., eval_dataset=..., ...)
# trainer.train()
```

**Refresh procedure**: re-validate pinned versions quarterly. MMS adapter naming + interface changes between releases.

## Recipe stub 2: Lhotse CutSet from ELAN EAF

Pinned: `pyelan==0.4.x`, `lhotse==1.30.x` as of 2026-04-23.

```python
# eaf_to_lhotse.py
# Phase 1 stub — converts ELAN EAF + linked audio to Lhotse CutSet.

from pathlib import Path
from lhotse import CutSet, Recording, SupervisionSegment, MonoCut
import xml.etree.ElementTree as ET

TARGET_LANG = "yor"
TIER_NAME_TRANSCRIPTION = "tx"  # standardize per project
PUA_MAPPING = {}  # populate per legacy SIL font; e.g., {"": "ɔ"}

def normalize_pua(text: str) -> str:
    """Convert SIL PUA characters to Unicode equivalents."""
    for pua_char, uni_char in PUA_MAPPING.items():
        text = text.replace(pua_char, uni_char)
    return text

def parse_eaf(eaf_path: Path) -> list[SupervisionSegment]:
    """Extract transcription tier intervals as Supervision Segments."""
    tree = ET.parse(eaf_path)
    root = tree.getroot()
    # ELAN EAF: TIER -> ANNOTATION -> ALIGNABLE_ANNOTATION -> ANNOTATION_VALUE
    time_slots = {ts.get("TIME_SLOT_ID"): int(ts.get("TIME_VALUE", 0)) / 1000.0
                  for ts in root.findall(".//TIME_SLOT")}
    sups = []
    for tier in root.findall(".//TIER"):
        if tier.get("TIER_ID") != TIER_NAME_TRANSCRIPTION:
            continue
        for ann in tier.findall(".//ALIGNABLE_ANNOTATION"):
            t1 = time_slots[ann.get("TIME_SLOT_REF1")]
            t2 = time_slots[ann.get("TIME_SLOT_REF2")]
            text_elem = ann.find("ANNOTATION_VALUE")
            text = normalize_pua(text_elem.text or "")
            sups.append(SupervisionSegment(
                id=f"{eaf_path.stem}-{ann.get('ANNOTATION_ID')}",
                recording_id=eaf_path.stem,
                start=t1, duration=t2 - t1, channel=0,
                text=text, language=TARGET_LANG,
            ))
    return sups

def build_cutset(corpus_dir: Path) -> CutSet:
    cuts = []
    for eaf_path in corpus_dir.glob("*.eaf"):
        wav_path = eaf_path.with_suffix(".wav")
        if not wav_path.exists():
            continue
        rec = Recording.from_file(wav_path)
        sups = parse_eaf(eaf_path)
        for sup in sups:
            cut = MonoCut(
                id=sup.id, start=sup.start, duration=sup.duration,
                channel=0, recording=rec, supervisions=[sup],
            )
            cuts.append(cut)
    return CutSet.from_cuts(cuts)

# Usage:
# cuts = build_cutset(Path("data/eaf-corpus/"))
# cuts.to_file("data/cuts.jsonl.gz")
```

**PUA mapping must be populated** per source font; SIL provides per-font mapping tables. Without PUA conversion, downstream tokenizer / IPA validator will see legacy bytes.

## Lhotse-native data manifests

Standard layout:

```
data/
├── recordings.jsonl.gz      # one recording (audio file) per line
├── supervisions.jsonl.gz    # one supervision (text + time) per line
├── cuts.jsonl.gz            # one cut (audio + supervisions) per line
└── feats/
    └── *.lca               # cached features (Mel-spec, etc.)
```

Tools that consume:
- ESPnet (k2/icefall integration).
- SpeechBrain (lhotse-data adapter).
- NeMo (lhotse plugin).
- Custom HuggingFace fine-tune (manual conversion as in stub 1).

## Refresh procedure

Pinned library versions per stub. Refresh:
1. Quarterly: re-pin to current `transformers` / `lhotse` / `torch`.
2. Test stub end-to-end on a sample.
3. Update version pin + test result.
4. Document any breaking-change adapters needed.

## See also

- Lhotse: https://github.com/lhotse-speech/lhotse
- Lhotse docs: https://lhotse.readthedocs.io/
- ESPnet egs2: https://github.com/espnet/espnet/tree/master/egs2
- icefall: https://github.com/k2-fsa/icefall
- SpeechBrain: https://github.com/speechbrain/speechbrain
