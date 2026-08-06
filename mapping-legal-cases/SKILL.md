---
name: mapping-legal-cases
description: Heavy legal case-folder mapper. Use only for explicit case mapping / full case intake / `.casebase` generation across folders or many documents. Do NOT use for a single uploaded PDF, quick extraction, summary, Q&A, or ordinary file reading.
license: Apache-2.0
metadata:
  author: Chen Friedman / Lawcal AI
  version: "1.0.0"
  homepage: https://github.com/chen-friedman/legal-skills
---

# Mapping Legal Cases

Maps a folder of heterogeneous legal documents into a structured analysis brief in a `.casebase/` subfolder.

## Do NOT use for lightweight uploads

Do **not** invoke this skill for:

- a single PDF / Word / image / attachment;
- “summarize this file”;
- “what does this PDF say?”;
- quick deadline/risk extraction from one document;
- ordinary upload handling in chat.

Use `ocr-and-documents` first. Escalate here only when the user wants a durable case map across a folder/document set.

**Opening a brand-new matter (empty folder)?** Use `new-matter` instead — it runs an intake interview and scaffolds the matter workspace (folder tree, `MATTER.md` brief, `AGENTS.md`). Run *this* mapper afterwards, once source documents are in `documents/`. `MATTER.md` stays the human brief; `.casebase/` (produced here) holds the exhaustive analysis.

## What it does

Given a folder containing any mix of legal case documents, this skill produces **10 cross-referenced analysis documents** in a `.casebase/` subfolder:

1. **DOCUMENTS.md** — full inventory of every file with status
2. **GLOSSARY.md** — bilingual keyword index (Which terms appear where?)
3. **PRIVACY_FLAGS.md** — sensitive data locations (IDs, accounts, medical, etc.)
4. **PARTIES.md** — who's who (client, opposing, judges, experts, witnesses)
5. **TIMELINE.md** — chronological events with source citations
6. **CLAIMS.md** — legal claims, arguments, basis, status
7. **EVIDENCE.md** — evidence mapped to each claim
8. **GAPS.md** — missing documents, contradictions, unanswered questions
9. **RISKS.md** — case weaknesses, opposing-side-favorable material
10. **DEADLINES.md** — forward-looking dates with OVERDUE/URGENT flags

Plus **MAPPING_LOG.md** — audit trail listing processed files, pending OCR/transcription items, and environment diagnostics.

Finally, a **`case-portal.html`** is generated at the matter root — a single self-contained page that lets the lawyer browse the whole case map (all documents above) in the WebUI with one click. It is pure post-processing of the Markdown and adds no extraction time.

## When to use

- Case intake (first time touching a case folder)
- Building a case brief before drafting a motion
- Preparing for a hearing (verify every date is known)
- Onboarding a colleague to a case
- Identifying missing documents or contradictions
- Refreshing analysis after new documents arrive
- Auditing a case folder for sensitive data before sharing

## How it works

Two-wave architecture keeps token usage low:

**Wave 1 — Inventory (runs first, alone):**
1. Scans the folder via `scripts/extract.py --scan`
2. Extracts text from each file once using `scripts/extract.py --cache`
3. Caches all extractions to `.casebase/.cache/<hash>.json` (persistent across runs)
4. Loads the right keyword pack(s) based on detected source languages
5. Builds `DOCUMENTS.md`, `GLOSSARY.md`, `PRIVACY_FLAGS.md`

**Wave 2 — Analysis (4 parallel tasks, if platform supports; otherwise sequential):**
6. `parties-timeline` → `PARTIES.md` + `TIMELINE.md`
7. `claims-evidence` → `CLAIMS.md` + `EVIDENCE.md`
8. `risks-gaps` → `GAPS.md` + `RISKS.md`
9. `deadlines` → `DEADLINES.md`

Wave 2 tasks read from the cache and glossary — they never re-extract files.

## Step 1 — Pre-flight

Before doing anything else, run the pre-flight check to know what extraction tools are available in this environment:

```bash
python scripts/extract.py --preflight --pretty
```

Parse the JSON output. Key fields:
- `capabilities.pdf_text` — can we read PDFs?
- `capabilities.word` — can we read Word documents?
- `capabilities.excel` — can we read spreadsheets?
- `capabilities.ocr_images` — will scanned content auto-OCR?
- `capabilities.transcription` — will audio/video auto-transcribe?
- `install_hints` — what's missing

Lawcal OS managed file stack:
- OCR: managed pass-through on the Lawcal AI gateway — `POST $AI_GATEWAY_BASE_URL/ocr` with `model=ocr` (Azure Document Intelligence, returns Markdown per page). `scripts/extract.py` calls this automatically for images and scanned PDFs. No separate OCR service, no extra key, no Marker/Tesseract install.
- Transcription: managed pass-through — `POST $AI_GATEWAY_BASE_URL/audio/transcriptions` with `model=audio-fast` (Whisper large-v3-turbo) or `model=audio-pro` (Whisper large-v3). `scripts/extract.py` calls this automatically for audio/video. No Whisper install.
- Main reasoning provider: Lawcal AI router (`https://api.lawcal.ai/v1`), not user-managed provider keys.
- The extractor reads `AI_GATEWAY_BASE_URL` + `AI_GATEWAY_KEY` from the environment (preconfigured on the tenant). If they are absent (e.g. offline dev), it falls back to local tesseract/whisper, and otherwise flags files `[PENDING OCR]` / `[PENDING TRANSCRIPTION]`.

The skill **always works** for plain text, CSV, JSON, markdown. For PDF/Word/Excel, at least one backend must be available — the extractor falls back through multiple options.

If critical capabilities are missing, silently continue when possible: mark files as `[PENDING OCR]`, `[PENDING TRANSCRIPTION]`, or `[UNSUPPORTED]` in `DOCUMENTS.md` and list them in `MAPPING_LOG.md`. Do not ask ordinary users to install tools or configure API keys; Lawcal admins preconfigure those.

## Step 2 — Resolve target folder

If the user provided a path, use it. Otherwise use the current working directory.

Verify it is a directory and is not a system location (e.g., `C:\Windows`, `/etc`) — if so, ask the user to specify a folder.

## Step 3 — Check for existing map

If `.casebase/` already exists with documents, ask:

```
.casebase/ exists with {N} documents:
- DOCUMENTS.md ({X} lines)
- ...

What would you like?
1. Refresh — regenerate outputs (keep cache for speed)
2. Full refresh — also delete cache and re-extract every file
3. Update — regenerate only specific documents
4. Skip — use existing map as-is
```

Wait for user choice.

## Step 4 — Pre-scan and threshold

```bash
python scripts/extract.py --scan "<case_folder>" --pretty
```

Show the user:
```
Case folder: {path}
Found {total} files:
  - PDFs: {pdf}
  - Word documents: {word}
  - Spreadsheets: {spreadsheet}
  - Emails: {email}
  - CSVs: {csv}
  - Markdown: {markdown}
  - Text: {text}
  - Images: {image}       ← needs OCR (managed pass-through, auto)
  - Audio: {audio}         ← needs transcription (managed pass-through, auto)
  - Video: {video}         ← needs video analysis + transcription
  - Other: {other}
Total size: {size}
```

**If total > 150 files**, ask for confirmation:
```
Large case folder detected ({total} files). Estimated time: {estimate}.
Proceed?
1. Yes — map everything
2. Sample — most-recent 50 files only (preview)
3. Filter — skip audio/video/images, text-bearing only
4. Cancel
```

## Step 5 — Create structure

```bash
mkdir -p "<case_folder>/.casebase/.cache"
```

## Step 6 — Wave 1: Inventory + glossary + privacy

Do this work in order. If your platform supports subagents (e.g. Claude Code, OpenCode), this can be a dedicated task; otherwise do it inline in the current agent.

**6a. Extract every file (populate cache):**

For each file in the pre-scan file list:
```bash
python scripts/extract.py "<relative/path>" \
    --cache "<case_folder>/.casebase/.cache" \
    --case-root "<case_folder>" \
    --max-chars 200000
```

Track extraction results — note files with `needs_ocr`, `needs_transcription`, `needs_video_analysis`, or `success: false` for MAPPING_LOG.md.

**6b. Detect corpus language(s):**

Read the `language_detected` field from each cache JSON. Take the mode (most frequent) as the primary language. Possible values: `en`, `he`, `ar`, `ru`, `es`, `fr`, `de`, `pt`, `zh`.

**6c. Load ONLY the relevant keyword packs:**

Always load: `references/keywords/common-en.md` (baseline)

Also load based on detected languages:
- Primary language `he` → also load `references/keywords/he.md`
- Primary language `ar` → also load `references/keywords/ar.md`
- Primary language `ru` → also load `references/keywords/ru.md`
- Primary language `es` → also load `references/keywords/es.md` (if present)
- Primary language `fr` → also load `references/keywords/fr.md` (if present)
- Primary language `de` → also load `references/keywords/de.md` (if present)
- Primary language `pt` → also load `references/keywords/pt.md` (if present)

If a file is absent, skip it silently — that jurisdiction pack hasn't been contributed yet.

**6d. Build GLOSSARY.md** by scanning every cached extraction for terms in the loaded keyword packs. For each term, record the files where it appears. Include:
- Terms by category (dates, money, parties, procedures, etc.)
- Regex-matched patterns (date strings, currency amounts, case numbers)
- Auto-detected entities (capitalized names/orgs appearing 3+ times)
- File-name signals (dates, versions, case numbers in filenames)

**6e. Build PRIVACY_FLAGS.md** by scanning for privacy patterns defined in the keyword packs:
- National IDs, passports, credit cards, bank accounts, medical record numbers, phone numbers
- **Mask values in the output** (e.g., `123-45-****`) — do not echo full sensitive values

**6f. Build DOCUMENTS.md** with per-file rows: path, type, size, pages (if PDF), language, one-line summary, status tags (`[PENDING OCR]`, `[PENDING TRANSCRIPTION]`, etc.).

See `references/output-templates.md` for the exact template structures.

## Step 7 — Wave 2: Analysis (4 tasks, can run in parallel)

Each Wave 2 task reads from the cache + GLOSSARY.md. None of them re-extract files.

If your platform supports parallel subagents (Claude Code, OpenCode, OpenHands, etc.), spawn these 4 as parallel tasks. Otherwise run them sequentially.

**Task 2a — PARTIES.md + TIMELINE.md** — read GLOSSARY to find files with party names / dates, read those cached JSONs, build structured outputs.

**Task 2b — CLAIMS.md + EVIDENCE.md** — identify legal arguments (by party) and cross-reference evidence to each claim.

**Task 2c — GAPS.md + RISKS.md** — identify missing documents, contradictions, unfavorable facts. GAPS covers absence; RISKS covers present-but-problematic.

**Task 2d — DEADLINES.md** — extract every forward-looking date, sort ascending, flag OVERDUE / URGENT (<14 days).

See `references/output-templates.md` for templates.

## Step 8 — Write MAPPING_LOG.md

Orchestrator-level audit trail:
- Timestamp, case folder path
- Total files scanned / successfully extracted
- Pending OCR list (files with `needs_ocr: true`)
- Pending transcription list (files with `needs_transcription: true`)
- Pending video analysis list
- Failed / unsupported list
- Environment (tools available, from preflight)
- Documents generated (names + line counts)

## Step 9 — Build the case portal

Generate a single, self-contained HTML portal so the lawyer can browse the whole case map in the WebUI with one click. This is pure post-processing of the Markdown already on disk — it adds no extraction/LLM work.

```bash
python scripts/build_portal.py --casebase <matter-folder> --out <matter-folder>/case-portal.html
```

- `--casebase` accepts the matter folder (it auto-resolves the `.casebase/` inside) — pass the matter root.
- **Write the output to the matter ROOT (`<matter-folder>/case-portal.html`), NOT inside `.casebase/`.** `.casebase/` is a hidden dotfolder and will not appear in the WebUI workspace file tree; the matter root is visible, so the lawyer sees `case-portal.html` and clicks it — the WebUI renders it inline in its sandboxed HTML preview. One click, no extra steps.
- The portal never reads `.casebase/.cache/` (unmasked text). It digests only the analysis Markdown.
- Idempotent: re-run after every refresh so the portal reflects the latest map.

## Step 10 — Summarize

Show the user:
- `case-portal.html` created at the matter root — tell them they can click it in the file tree to browse the whole case
- All 10 documents generated with line counts
- **Privacy warning prominently** if `PRIVACY_FLAGS.md` has content
- **Pending extraction count** if any items need OCR / transcription / video analysis
- **Language-appropriate output** — write this summary in the corpus primary language (Hebrew, English, etc.)
- Next-step suggestions: review TIMELINE, DEADLINES, refresh after changes

## Critical rules

1. **Cite every finding** — every fact in every output document must reference a source file path like `file.pdf:p3` or `email.eml`.

2. **Match corpus language** — write output documents in the language of the source documents. Use the mode of `language_detected` values from cache JSONs. Default to Hebrew if mixed and Hebrew is present; otherwise English.

3. **Mask sensitive values** — in PRIVACY_FLAGS.md, never quote full ID numbers, credit cards, account numbers. Mask with asterisks.

4. **Extract once, analyze many times** — never re-run extract.py on a file already in cache. Wave 2 tasks read cache JSONs.

5. **Pending files are not ignored** — tag them `[PENDING OCR]`, `[PENDING TRANSCRIPTION]`, `[PENDING VIDEO ANALYSIS]` in relevant documents and log them in MAPPING_LOG.md.

6. **Forward slashes in paths** — use `/` not `\` in all documented file references (Unix-style, works everywhere).

7. **Lazy-load keyword packs** — load `common-en.md` always, but only load language-specific packs when the corpus language matches.

## Supporting files

- `scripts/extract.py` — universal extractor (PDF, Word, Excel, email, image, audio, video, text, CSV, JSON, markdown). See `references/document-handlers.md`.
- `references/document-handlers.md` — per-format extraction details and fallback chains.
- `references/output-templates.md` — exact templates for all 10 documents.
- `references/keywords/common-en.md` — base English legal terminology.
- `references/keywords/{lang}.md` — language-specific packs (loaded on demand).


## Platform notes

- **Claude Code / OpenCode / Cursor / OpenHands / similar** — this skill uses the Agent Skills standard and works in any agentskills.io-compatible platform.
- **Subagent support** — if available, Wave 2 tasks parallelize. If not, they run sequentially. Output is identical.
- **OCR / transcription** — handled automatically via the tenant's managed Lawcal AI pass-through (OCR + Whisper). Local tesseract/whisper are used only as an offline fallback; otherwise files are flagged `[PENDING...]`.
- **Network access** — extraction of local text-bearing files needs no internet. OCR and transcription call the managed gateway (`$AI_GATEWAY_BASE_URL`); if unreachable, they fall back or flag `[PENDING...]`.

## Output language override

The user may explicitly request an output language even if it differs from corpus language:
- "map this case in English" → force English output
- "in Hebrew" → force Hebrew
- "same as documents" → default behavior (auto-detect from corpus)
