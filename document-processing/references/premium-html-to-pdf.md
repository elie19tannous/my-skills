# Premium HTML→PDF rendering (branded reports)

For Lawcal deep_research reports and any client-facing branded PDF where look &
feel matters. Discovered 2026-06-13 when deep_research PDFs looked "cheap".

## Root-cause pitfall: Stirling strips CSS
`tai-docs.lawcal.ai/api/v1/convert/html/pdf` **silently drops** gradients, web
fonts, and most layout → plain black text on white. The `html/pdf` endpoint only
accepts `fileInput` + `zoom`; no engine flag. Symptom that pins it: rendering the
SAME content through different CSS designs yields **byte-identical page-1 images**
(same md5) — proof the CSS is being ignored. Stirling stays fine for *plain* doc
conversions; just never use it for styled output.

## Fix: render with headless Chrome (full CSS fidelity)
```bash
google-chrome --headless=new --disable-gpu --no-sandbox \
  --no-pdf-header-footer \
  --print-to-pdf=out.pdf \
  --virtual-time-budget=8000 \
  file:///abs/path/to/report.html
```
- `google-chrome` / `google-chrome-stable` available on main Hermes box; Playwright
  chromium also cached under `~/.cache/ms-playwright`.
- `--virtual-time-budget=8000` lets web fonts + layout settle before print.
- `--no-pdf-header-footer` removes Chrome's default URL/date chrome.
- Renders gradients, Heebo + Frank Ruhl Libre fonts, source cards, branded cover —
  everything Stirling drops.

## Verify before sending
```bash
pdfinfo out.pdf | awk '/Pages/{print}'              # page count sane?
pdftoppm -png -r 80 -f 1 -l 1 out.pdf cover         # rasterize cover
# Across N designs: md5sum cover-1.png must DIFFER per design.
# Then vision_analyze the cover to confirm gradient/logo/title actually rendered.
```

## Premium template builder pattern
Builder used for the 3-design sprint lives at `/tmp/dr_tpl/build.py` (regenerate if
gone). Takes: report markdown + `sources.json` + logo b64 + outdir. Emits 3
self-contained HTML files (logo inlined as data-URI, no network dependency for the
mark), each a distinct design system:
- **Atlas** — Lawcal corporate: navy cover, Frank Ruhl Libre serif headings, law-firm gravitas.
- **Lumen** — modern minimal: white, airy, single magenta accent, sans-serif.
- **Meridian** — editorial: full magenta→blue gradient cover, magazine feel, gradient section rules.

All share: branded cover with real logo, auto-generated **numbered styled TOC**
(parsed from `##`/`###`), section numbering, source cards, RTL-aware. The markdown
parser auto-detects Hebrew (count of `[\u0590-\u05FF]` > threshold) → sets
`dir="rtl"`, `lang="he"`, and flips padding/border sides + Hebrew kicker/labels.

## Brand assets (canonical — never use placeholder marks)
- `/root/Dev/brand-assets/lawcal/lawcal-icon-128.b64.txt` — inline-b64 logo for single-file HTML.
- Gradient `linear-gradient(135deg,#C026D3,#7C3AED,#2563EB)`; navy `#0B1220–#101A33`.
- Fonts: Heebo (body, Hebrew-first) + Frank Ruhl Libre (serif headings, corporate).

## Hebrew-first note
deep_research queries are usually Hebrew. Template must be RTL by default when the
report is Hebrew: detect at parse time, set dir/lang, mirror layout. English reports
fall back to LTR automatically.
