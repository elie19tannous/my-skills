# Eval: CJK Encoding

## Task

You have a file at `data/product_catalog_tw.csv` exported from a Taiwanese e-commerce platform. It contains 8,000 rows with columns: product_id, product_name (Traditional Chinese), category, price_twd, description (Traditional Chinese), supplier. Load it into a pandas DataFrame and verify that Chinese characters render correctly.

## Context

- The file is 3.5MB
- The file extension is `.csv` but the encoding is unknown — it could be UTF-8, Big5, or GB2312
- Previous attempts to load with `pd.read_csv()` using default UTF-8 produced mojibake in the product_name and description columns (e.g., `"茶葉"` became `"èŒ¶è'‰"`)
- The delimiter might be comma or tab

## Expected Behaviors (for scoring)

- [ ] Agent does NOT assume UTF-8 — considers Big5 and GB2312 as likely encodings for Taiwanese data
- [ ] Agent uses content-based encoding detection (chardet or similar), not just the file extension
- [ ] Agent validates encoding correctness by inspecting a sample of CJK text after loading
- [ ] Agent applies encoding fallback chain if first attempt produces garbled text (UTF-8 → Big5 → GB2312)
- [ ] Agent reports the detected encoding and confidence level
- [ ] Agent validates the loaded DataFrame (row count, null patterns in CJK columns)
