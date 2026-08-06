---
name: ocr-and-documents
description: Lawcal OS single/multi-file document intake — extract text from PDFs, Word, PowerPoint, Excel, HTML and scanned/image files, keep source refs, then answer/summarize/review. OCR routes through the Lawcal AI managed OCR pass-through. Use before any heavy case-mapping skill.
license: Proprietary
metadata:
  author: Lawcal AI
  version: "1.0.0"
---

# OCR and Documents

Use this silently whenever a user uploads or references files in a legal workspace.

This is the **default path** for ordinary uploads: one PDF, one Word file, a few attachments — quick extraction, Q&A, summary, deadline lookup, risk spotting. Do **not** invoke the case mapper just to read a file.

Escalate to `mapping-legal-cases` only when the user explicitly asks to map/build a case file, or when there is a real case folder / many heterogeneous documents that should produce `.casebase/` outputs.

## Default behavior

See `references/toolchain.md` for the exact baked library or CLI tool per file type.

1. Detect file type and language.
2. Extract text with local/native readers first for **text-bearing** files (PyMuPDF for PDFs, python-docx for Word, etc.). This is fast and free — always try it first.
3. Use the **managed OCR pass-through** for scans/images, or PDFs whose native text layer is missing or low quality.
4. Preserve source references: filename, page/slide/sheet where available.
5. Use the extracted text directly for Q&A, summaries, risk review, drafting, or deadline lookup.

## OCR (scans / images / scanned PDFs) — exact method

This tenant has a working, pre-configured **managed OCR pass-through** on the Lawcal AI gateway. It is Azure Document Intelligence (layout) behind the alias `ocr`, and it returns **Markdown per page**. Do **not** install Marker, marker-pdf, PyTorch, Tesseract, or any OCR SDK, and do **not** ask the user for API keys.

Send the file straight to `POST $AI_GATEWAY_BASE_URL/ocr` with `model=ocr`. It accepts PDFs directly (multi-page) and common image formats (PNG/JPG/TIFF). Run this in `execute_code`:

```python
import os, requests

def ocr_document(path: str) -> list[dict]:
    """Managed OCR pass-through. Returns [{index, markdown, dimensions}, ...] per page."""
    base = os.environ["AI_GATEWAY_BASE_URL"].rstrip("/")   # https://api.lawcal.ai/v1
    key  = os.environ["AI_GATEWAY_KEY"]
    with open(path, "rb") as fh:
        r = requests.post(
            f"{base}/ocr",
            headers={"Authorization": f"Bearer {key}", "User-Agent": "LawcalOS/1.0"},
            files={"file": (os.path.basename(path), fh)},
            data={"model": "ocr"},
            timeout=180,
        )
    r.raise_for_status()
    return r.json()["pages"]

pages = ocr_document("/absolute/path/to/scan.pdf")
text = "\n\n".join(p["markdown"] for p in pages)
print(text)
```

Notes:
- The pass-through takes the **whole PDF** — no need to split pages to images first. Each element of `pages` has `index`, `markdown`, and `dimensions`.
- A normal `User-Agent` header is required; the gateway sits behind Cloudflare and rejects the default `python-requests`/`urllib` agent with 403.
- Minimum image dimensions apply (Azure rejects tiny thumbnails with `InvalidContentDimensions`) — render scanned pages at a reasonable DPI if you ever pre-rasterize.

## Text-bearing files — extract natively first

For files that already have a text layer, skip OCR entirely and use the baked libraries (much faster, exact text):

- PDF: `pymupdf` / `pymupdf4llm`; tables via `pdfplumber`. Quick pre-check with `pdftotext input.pdf -` to decide if OCR is even needed.
- Word `.docx`: `python-docx`. PowerPoint `.pptx`: `python-pptx`. Excel `.xlsx`: `openpyxl`.
- HTML: `beautifulsoup4` + `lxml`. Conversion: `pandoc`.
- Email: `.eml` via the Python stdlib `email` module; **Outlook `.msg` via the baked `extract-msg` library** (`import extract_msg`) — reads sender, recipients, subject, date, body, and lists attachments.

Rule of thumb: if `pdftotext` returns real text, use the native path. If it returns little/nothing (scanned image PDF), use the OCR pass-through above.

## Managed providers

Everything routes through the Lawcal AI gateway (`$AI_GATEWAY_BASE_URL`, i.e. `https://api.lawcal.ai/v1`) using the tenant's existing `AI_GATEWAY_KEY` — no separate OCR service, no extra key, no per-tool provider setup.

- OCR: managed pass-through, alias `ocr` (`POST /ocr`, returns Markdown per page).
- Transcription (audio/video): see the `transcription` skill.
- Reasoning model aliases: `lawcal-flash`, `lawcal-pro`, `lawcal-max`; default `lawcal-pro`.

Do not ask users for API keys or provider configuration. Lawcal admins preconfigure env vars.

## Output contract

For every processed file, keep:

```text
source_path
file_type
language
extraction_method   # native | ocr-passthrough
confidence/status
page_or_sheet_refs
warnings
```

If extraction fails, mark the file as one of:

```text
[PENDING OCR]
[UNSUPPORTED]
[FAILED EXTRACTION]
```

Continue with the available files.

## Escalation rule

Stay lightweight unless at least one is true:

- User asks for "map the case", "build casebase", "full case intake", "timeline + parties + claims + evidence across the folder".
- Input is a folder or large document set, not a single uploaded file.
- Output needed is the full `.casebase/` package.

Otherwise: extract → answer.

## Hebrew / RTL

- Hebrew summaries and legal outputs should be natural Hebrew.
- Preserve URLs, commands, evidence IDs, statute references, and filenames in LTR.
- Keep page citations compact.

## Safety

Never expose raw credentials, env vars, API keys, or provider setup details.
Ask before sending externally, filing, deleting, or making legal commitments.
