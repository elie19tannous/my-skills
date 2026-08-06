---
name: document-processing
description: "Use when extracting, OCRing, editing, converting, or generating documents/PDFs/images/audio-video transcripts with tools such as Gemini OCR, Azure Document Intelligence, PyMuPDF, marker, nano-pdf, and workflow-specific document pipelines."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [documents, pdf, ocr, extraction, transcription, docx]
    related_skills: [google-workspace, tai-municipal-doc-tools]
---

# Document Processing

## Overview
Umbrella for document/media-to-text workflows: OCR, PDF extraction/editing, DOCX/Google Doc handling, transcript generation, and tool-specific pipelines.

## Lanes
- **OCR/extraction:** choose PyMuPDF for digital PDFs, marker for structured extraction, Gemini/Azure Document Intelligence for scans/images/layout-heavy docs.
- **PDF editing:** use nano-pdf for text/title/typo edits when preserving layout matters.
- **DOCX tracked changes:** to produce a Word doc with real Track Changes (Accept/Reject), inject `w:ins`/`w:del` OOXML directly — `python-docx` has no native API for it. Full pattern, helpers, verification, and pitfalls in `references/docx-tracked-changes-ooxml.md`. Common for Hebrew/RTL legal-contract review (mark up a lawyer's draft, attach back over email).
- **Workspace docs:** use Google Workspace for Drive/Docs/Sheets/Gmail source/destination operations.
- **Domain pipelines:** use TAI-specific document/protocol skills only when the task is that product/domain.
- **Premium HTML→PDF (branded reports):** render styled single-file HTML with **headless Chrome**, NOT Stirling. See `references/premium-html-to-pdf.md`.

## Rules
1. Inspect file type/quality first.
2. Prefer deterministic text extraction before OCR.
3. Keep original files; write outputs beside them.
4. Verify sample pages/fields manually before batch runs.
5. Report uncertainty/OCR confidence honestly.

## Pitfalls
- **Stirling silently strips CSS.** `tai-docs.lawcal.ai/api/v1/convert/html/pdf` drops gradients, web fonts, and most layout → output looks like plain black text on white (the classic "cheap-looking PDF"). Its `html/pdf` endpoint only takes `fileInput`+`zoom`; there's no flag to force a real engine. For any *branded/premium* report, render with headless Chrome instead (recipe in `references/premium-html-to-pdf.md`). Stirling is still fine for plain doc conversions where styling doesn't matter.
## References

- `references/tender-technical-response-mapping.md` — map Hebrew tender/RFP documents to supplier-facing technical/professional AI-draft areas (`מענה טכני`, `מתודולוגיה`, `איכות ההצעה`, compliance matrices, security annexes).

## Verification Checklist
- [ ] Input files located and backed up/not overwritten.
- [ ] Extraction/OCR lane justified.
- [ ] Output opened/read back.
- [ ] User gets output path or delivered file.
