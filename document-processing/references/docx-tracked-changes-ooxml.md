# DOCX tracked changes via direct OOXML

Use this when the user needs a Word document with real Track Changes (Accept/Reject in Word), especially for Hebrew/RTL legal/admin documents. `python-docx` can read/write DOCX but does not natively create Word revision markup, so inject `w:ins` / `w:del` directly into `word/document.xml` through the paragraph XML.

## Pattern

1. Preserve the original file; write a new output beside it.
2. Use `python-docx` to locate paragraphs and access `paragraph._p`.
3. For inserted text, create a new `w:p` with:
   - `w:pPr/w:bidi` for RTL paragraphs.
   - `w:ins w:id=... w:author=... w:date=...` wrapping `w:r/w:t`.
   - `w:rPr/w:rtl` for RTL runs.
4. For replacements, wrap the existing paragraph runs in `w:del`, convert child `w:t` tags to `w:delText`, then append a `w:ins` run with the replacement text.
5. Save the DOCX, then verify by inspecting the zipped XML for counts of `<w:ins`, `<w:del`, expected text, and author tags.
6. Render a PDF preview with LibreOffice and inspect a page visually if stakes are high.

## Minimal helpers

```python
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import datetime

AUTHOR = 'Chen @ Lawcal AI'
DATE = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
rid = 1000

def rpr(bold=False):
    rPr = OxmlElement('w:rPr')
    rPr.append(OxmlElement('w:rtl'))
    if bold:
        rPr.append(OxmlElement('w:b'))
    return rPr

def ins_para(text, bold=False):
    global rid
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr'); pPr.append(OxmlElement('w:bidi')); p.append(pPr)
    ins = OxmlElement('w:ins'); rid += 1
    ins.set(qn('w:id'), str(rid)); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
    r = OxmlElement('w:r'); r.append(rpr(bold))
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text
    r.append(t); ins.append(r); p.append(ins)
    return p

def insert_after(ref_para, text, bold=False):
    ref_para._p.addnext(ins_para(text, bold))

def replace_para_tracked(ref_para, new_text):
    global rid
    p = ref_para._p
    runs = [r for r in p.findall(qn('w:r'))]
    if runs:
        dw = OxmlElement('w:del'); rid += 1
        dw.set(qn('w:id'), str(rid)); dw.set(qn('w:author'), AUTHOR); dw.set(qn('w:date'), DATE)
        runs[0].addprevious(dw)
        for r in runs:
            for t in r.findall(qn('w:t')):
                t.tag = qn('w:delText')
            dw.append(r)
    ins = OxmlElement('w:ins'); rid += 1
    ins.set(qn('w:id'), str(rid)); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
    r = OxmlElement('w:r'); r.append(rpr(False))
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = new_text
    r.append(t); ins.append(r); p.append(ins)
```

## Verification snippets

```python
import zipfile, re
xml = zipfile.ZipFile('/tmp/out.docx').read('word/document.xml').decode('utf-8')
print('w:ins', xml.count('<w:ins '), 'w:del', xml.count('<w:del '))
for kw in ['expected phrase 1', 'expected phrase 2']:
    print(('OK ' if kw in xml else 'MISS ') + kw)
```

Render preview:

```bash
soffice --headless --convert-to pdf --outdir /tmp /tmp/out.docx
pdftoppm -png -r 95 -f 3 -l 4 /tmp/out.pdf /tmp/out_pg
```

Then use vision/image review for key pages: confirm insertions show colored/underlined, deletions show strikethrough, RTL text is readable.

## Pitfalls

- `python-docx` paragraph `.text` usually omits or mishandles text inside `w:ins` / `w:del`. For inspection, iterate raw `p._p` and collect `w:t` + `w:delText`.
- Existing legal DOCX files can split a single paragraph into many runs; seeing hundreds of `w:delText` in one replaced paragraph can be normal.
- LibreOffice renders tracked changes differently from Word but is good enough to verify that revision markup is visible.
- Keep proposed text short in tracked insertions; long Hebrew underlined colored insertions become visually dense.
