# Common Synthesis Workflows

## Workflow: Fill Sentinel Values Across Multiple Columns

**Goal:** Detect and replace sentinel values (any format) in several columns using contextual LLM generation.

**Steps:**
1. Run `synthesis_config.py` to validate config and confirm dependency order
2. Dry-run to inspect plan and estimated cost
3. Preview on 100 rows; inspect quality metadata and output
4. Scale to full dataset with cost guard

```bash
# 1. Validate config
python3 scripts/synthesis_config.py --config synthesis.json --check-yaml --output config_check.json

# 2. Dry-run
python3 scripts/batch_synthesize.py --input ckpt_03_cleaned.csv --config synthesis.json --dry-run

# 3. Preview
python3 scripts/batch_synthesize.py --input ckpt_03_cleaned.csv --config synthesis.json \
  --sample-size 100 --output preview_synthesized.csv

# 4. Inspect and scale
python3 scripts/batch_synthesize.py --input ckpt_03_cleaned.csv --config synthesis.json \
  --output ckpt_05_synthesized.csv --max-cost 15.00

# 5. Validate
python3 scripts/validate_synthetic.py --input ckpt_05_synthesized.csv \
  --original ckpt_03_cleaned.csv --criteria criteria.json --output synthesis_validation.json
```

---

## Workflow: HTML to Markdown Format Conversion

**Goal:** Convert a column of raw HTML content to clean markdown across all rows.

**Steps:**
1. Generate a YAML agent config for an HTML-to-markdown converter
2. Run `generate_column.py` with `--target-rows all` on a preview subset
3. Scale to full dataset after verifying conversion quality

```bash
# Preview conversion on 50 rows
python3 scripts/generate_column.py \
  --input ckpt_03_cleaned.csv \
  --column content_md \
  --agent-yaml agents/html_converter.yaml \
  --target-rows all \
  --context-columns content_html \
  --sample-size 50 \
  --output preview_converted.csv

# Scale
python3 scripts/generate_column.py \
  --input ckpt_03_cleaned.csv \
  --column content_md \
  --agent-yaml agents/html_converter.yaml \
  --target-rows all \
  --context-columns content_html \
  --output ckpt_05_synthesized.csv \
  --max-cost 5.00
```

---

## Workflow: Enrich with Reference Dataset Then Synthesize Remaining Gaps

**Goal:** Use a reference dataset for exact matches, then use LLM to synthesize values for rows with no match.

**Steps:**
1. Run `enrich_from_reference.py` to fill as many rows as possible via join
2. Inspect match rate in the enrichment summary
3. For unmatched rows (null enrichment values), run `generate_column.py` with `--target-rows null_only`

```bash
# Step 1: Enrich from reference
python3 scripts/enrich_from_reference.py \
  --input ckpt_03_cleaned.csv \
  --reference-paths etymology_db.csv \
  --join-key word \
  --enrich-columns origin,etymology_notes \
  --output enriched.csv

# Step 2: Synthesize remaining nulls
python3 scripts/generate_column.py \
  --input enriched.csv \
  --column origin \
  --agent-yaml agents/etymology_synthesizer.yaml \
  --target-rows null_only \
  --context-columns word \
  --output ckpt_05_synthesized.csv \
  --sample-size 50
```
