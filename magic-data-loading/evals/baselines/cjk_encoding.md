# Baseline: CJK Encoding

## Minimum Acceptable Behavior

An agent WITHOUT the data-loading skill would typically:
- Try `pd.read_csv()` with default UTF-8 encoding
- Get mojibake or UnicodeDecodeError
- Maybe try `encoding="utf-8-sig"` or `encoding="latin-1"` (neither correct for Big5)
- Not know the Big5 → GB2312 fallback chain for CJK data
- Not validate that CJK characters rendered correctly after loading

## With-Skill Expected Improvements

An agent WITH the data-loading skill should:
1. **CJK encoding awareness** — know that Taiwanese data is likely Big5, not assume UTF-8
2. **Encoding fallback chain** — try UTF-8 → Big5 → GB2312 → Shift_JIS systematically
3. **Content-based detection** — use chardet with confidence threshold (< 0.5 = fall back to UTF-8)
4. **Post-load validation** — inspect CJK text columns to verify characters render correctly (not mojibake)
5. **Confidence reporting** — report detected encoding and confidence level

## Key Differentiators

The skill teaches the CJK encoding fallback chain — expert knowledge that Claude wouldn't reliably apply without guidance. The critical insight is that Big5 is the most likely encoding for Taiwanese data, not UTF-8, and that mojibake in CJK columns is a silent failure (no error raised, data looks "loaded" but is corrupted).
