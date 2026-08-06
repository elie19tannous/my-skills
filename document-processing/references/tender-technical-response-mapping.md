# Tender technical-response mapping

Use when asked to inspect tender/RFP documents and identify the parts an AI system should draft or fill.

## Workflow

1. Locate the exact source thread/files first; do not rely on memory of filenames.
2. Extract text beside originals:
   - PDFs: `pdftotext -layout <file.pdf> <file.pdf.txt>` when digital text exists.
   - DOCX: unzip/read `word/document.xml` or use a DOCX parser; keep paragraph order.
   - Scans/layout-heavy PDFs: only then use OCR.
3. Search for supplier-facing response markers, not only fixed annex names.
4. Produce a file-by-file map with page/line references and classify each area.
5. Save derived analysis in the project workspace; do not build a demo unless asked.

## Hebrew tender markers

Technical/professional response areas may appear under varied labels:

- `מענה טכני`
- `אופן הגשת המענה הטכני`
- `מפרט טכני`
- `מפרט משלים`
- `תיאור המתודולוגיה`
- `הצגת מתודולוגיה`
- `איכות ההצעה`
- `אופן העמידה במדד האיכות`
- `פרק ג׳` / `מפרט השירותים`
- `תכנית עבודה`
- `מימוש הפרויקט`
- `בקרת איכות`
- `אבטחת מידע` / `סייבר`
- acceptance tests: `בדיקות קבלה`, `הוכחת יכולת`
- documentation: `תיעוד טכני`, `תוכניות עדות`, `As made`

## Classification

For each hit, classify into one of:

| Class | AI role |
|---|---|
| Methodology/work plan | Draft narrative answer from requirements |
| Technical compliance matrix | Extract requirements, match specs, flag gaps |
| Supplemental spec (`מפרט משלים`) | Draft missing product/spec details only when evidence supports it |
| Quality/evidence tables | Map company projects/CVs/certifications; avoid invented experience |
| Cyber/security response | Draft policy/compliance response from verified company security material |
| Acceptance/test plan | Draft test methodology and handover checklist |
| Admin/legal | Usually do not generate except checklist/status |

## Pitfalls

- Do not assume technical response is always `נספח ג`; examples often place it in quality scoring, methodology annexes, service specs, or cyber annexes.
- Do not summarize the whole tender. User usually needs “where should the AI generate text / fill gaps.”
- Distinguish free-text generation from evidence mapping. Experience tables and CV/license sections need verified source data, not creative prose.
- Page numbers from extracted text are estimates; say “verify visually” before production use.
