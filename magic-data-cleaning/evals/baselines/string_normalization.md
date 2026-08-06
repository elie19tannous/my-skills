# Baseline: String Normalization

## Minimum Acceptable Behavior

An agent WITHOUT the data-cleaning skill would typically:
- Apply `.str.strip()` and maybe `.str.lower()` to all text columns
- Not fix mojibake/encoding issues
- Not apply unicode normalization (NFC)
- Not remove control characters specifically
- Not validate that normalization was effective

## With-Skill Expected Improvements

An agent WITH the data-cleaning skill should:
1. **Issue identification first** — detect specific text quality issues per column before cleaning
2. **Correct operation ordering** — trim before whitespace collapse (trimming first prevents edge-case misses)
3. **Encoding-aware fixes** — recognize and fix mojibake patterns (Latin-1 interpreted as UTF-8) using a known pattern map
4. **Unicode normalization** — apply NFC normalization to unify equivalent unicode representations
5. **Control character removal** — remove unicode control characters while preserving legitimate whitespace (newlines, tabs)
6. **Validation** — confirm issue counts drop to zero after normalization

## Key Differentiators

The skill prevents the agent from treating encoding issues as unsolvable. Without the skill, an agent seeing `"CafÃ© Machine"` would likely leave it as-is or apply generic `.encode().decode()` which may fail. The skill teaches the mojibake pattern map approach and the correct ordering of normalization operations.
