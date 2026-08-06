---
name: transcription
description: Transcribe audio/video files (meetings, calls, interviews, voice notes) for Lawcal OS. Routes through the tenant's managed Lawcal AI transcription pass-through (Whisper). Handles Hebrew/English mixed-language legal/business recordings. Use for offline/batch transcription, meeting notes, and documentable transcripts.
license: Proprietary
metadata:
  author: Lawcal AI
  version: "1.0.0"
---

# Transcription

Use this whenever a user uploads or references an **audio or video** file and wants a transcript, meeting notes, action items, or "what was said".

This tenant has a working, pre-configured **managed transcription pass-through** on the Lawcal AI gateway (OpenAI-compatible Whisper). Do **not** install Whisper/faster-whisper, do **not** use Gemini, Google Cloud Speech, or any other STT SDK, and do **not** ask the user for API keys.

## Models

Two aliases on the gateway, both OpenAI `/audio/transcriptions`-compatible:

- `audio-fast` — Whisper large-v3-turbo. **Default.** Fast, cheap, great for most meetings/voice notes.
- `audio-pro` — Whisper large-v3. Use for hard audio: heavy accents, noisy recordings, or when `audio-fast` output looks unreliable.

## Exact method

Run this in `execute_code`. It sends the file straight to the gateway and returns the transcript text.

```python
import os, requests

def transcribe(path: str, model: str = "audio-fast", language: str | None = None) -> str:
    """Managed transcription pass-through (Whisper). Returns transcript text."""
    base = os.environ["AI_GATEWAY_BASE_URL"].rstrip("/")   # https://api.lawcal.ai/v1
    key  = os.environ["AI_GATEWAY_KEY"]
    data = {"model": model}
    if language:                      # ISO-639-1, e.g. "he" or "en"; omit to auto-detect
        data["language"] = language
    with open(path, "rb") as fh:
        r = requests.post(
            f"{base}/audio/transcriptions",
            headers={"Authorization": f"Bearer {key}", "User-Agent": "LawcalOS/1.0"},
            files={"file": (os.path.basename(path), fh)},
            data=data,
            timeout=600,
        )
    r.raise_for_status()
    return r.json()["text"]

print(transcribe("/absolute/path/to/recording.m4a"))
```

Notes:
- A normal `User-Agent` header is required (Cloudflare rejects the default agent with 403).
- For **mixed Hebrew/English**, omit `language` and let Whisper auto-detect; force `language="he"` only if auto-detect misfires.
- Supported inputs: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, aac.

## Video files

Extract the audio track first, then transcribe:

```bash
ffmpeg -i input.mp4 -ar 16000 -ac 1 -c:a pcm_s16le /tmp/audio.wav
```

Then call `transcribe("/tmp/audio.wav")`.

## Large / long recordings

Whisper handles long files, but if a recording is very large or the request times out, chunk it and transcribe each chunk, then concatenate:

```bash
mkdir -p /tmp/chunks
ffmpeg -i recording.m4a -f segment -segment_time 1800 -ac 1 -ar 16000 /tmp/chunks/chunk_%03d.wav
```

Transcribe each `chunk_*.wav` in order and join the texts with a blank line between them.

## After transcription

- For meeting/call recordings, produce a short Markdown summary + action items from the transcript (use `lawcal-pro`), keeping the raw transcript as an artifact.
- Preserve original Hebrew wording when legal nuance matters; add an English translation separately only if requested.
- Whisper does not diarize (no per-speaker labels). If the user needs "who said what", note that speaker attribution is best-effort from context, not forensic.

## Hebrew / RTL

- Hebrew transcripts and summaries should read as natural Hebrew.
- Preserve names, URLs, evidence IDs, and filenames in LTR.

## Safety

Never expose raw credentials, env vars, API keys, or provider setup details.
Ask before sending externally, filing, or making legal commitments.
