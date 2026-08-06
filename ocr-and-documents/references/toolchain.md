# Baked file-handling toolchain

| File / need | Reach for | Invocation |
|---|---|---|
| PDF text and layout extraction; fast native first path | `pymupdf` / `pymupdf4llm` | Python: `import pymupdf` / `import pymupdf4llm` |
| PDF tables or precise layout when PyMuPDF is insufficient | `pdfplumber` | Python: `import pdfplumber` |
| Word documents (`.docx`) | `python-docx` | Python: `from docx import Document` |
| PowerPoint presentations (`.pptx`) | `python-pptx` | Python: `from pptx import Presentation` |
| Excel workbooks (`.xlsx`) | `openpyxl` | Python: `import openpyxl` |
| Outlook email (`.msg`) | `extract-msg` | Python: `import extract_msg`; `m = extract_msg.Message(path)` → `m.sender`, `m.to`, `m.subject`, `m.date`, `m.body`, `m.attachments` |
| Standard email (`.eml`) | stdlib `email` | Python: `import email`; `email.message_from_binary_file(fh)` |
| Tabular manipulation after extraction | `pandas` | Python: `import pandas as pd` |
| HTML parsing; use `lxml` parser for speed and robust markup handling | `beautifulsoup4` + `lxml` | Python: `from bs4 import BeautifulSoup`; `BeautifulSoup(html, "lxml")` |
| Format-to-format conversion, including DOCX ↔ Markdown | `pandoc` | CLI: `pandoc input.docx -t gfm -o output.md`; `pandoc input.md -o output.docx` |
| Quick PDF text-layer and metadata/image pre-check before deciding OCR is needed | `poppler-utils` | CLI: `pdftotext input.pdf -`; `pdfinfo input.pdf`; `pdfimages -list input.pdf` |
| OCR for images and scanned PDFs (managed pass-through, already configured for this tenant, no extra credentials) | Lawcal AI managed OCR | `POST $AI_GATEWAY_BASE_URL/ocr` with `model=ocr` (multipart `file=@doc.pdf`). Returns Markdown per page. Send the whole PDF; do NOT install Marker/marker-pdf/Tesseract or use a separate OCR provider. Requires a normal `User-Agent` header (Cloudflare). |
| Audio/video transcription (managed, already configured for this tenant, no extra credentials) | Lawcal AI managed transcription | `POST $AI_GATEWAY_BASE_URL/audio/transcriptions` with `model=audio-fast` (Whisper turbo) or `audio-pro` (Whisper large). See the `transcription` skill. Do NOT install Whisper or use another speech SDK. |
| Text-to-speech; Hebrew voice already configured | `edge-tts` | CLI: `edge-tts --voice he-IL-HilaNeural --text "…" --write-media output.mp3`; Python: `import edge_tts` |

Python packages run under `/opt/hermes/.venv/bin/python3` in the tenant agent image.

Gateway base URL and key are in env: `AI_GATEWAY_BASE_URL` (`https://api.lawcal.ai/v1`) and `AI_GATEWAY_KEY`. Never print or expose them.
