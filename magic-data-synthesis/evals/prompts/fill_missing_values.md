# Eval: Fill Missing Values

## Task

You have a CSV file at `data/input/products.csv` with 500 rows and the following columns:
- `product_id` (integer, complete)
- `name` (string, complete)
- `category` (string, complete — values: "Electronics", "Clothing", "Home", "Food")
- `description` (string, 120 rows are null/empty)
- `price` (float, complete)

The `description` column has 120 missing values (NaN). You need to generate plausible product descriptions for these missing rows based on the product name, category, and price.

Use the MAGIC data synthesis skill to fill in the missing descriptions.

## Expected Behaviors (for scoring)

- [ ] Agent assesses feasibility: confirms that description generation requires contextual understanding (not a regex/code task), making LLM synthesis appropriate
- [ ] Agent creates a YAML agent config for the description generator with appropriate instruction text
- [ ] Agent uses `fill-missing` mode (not `fill-sentinels` or `transform`) since the values are NaN
- [ ] Agent declares `depends_on: ["name", "category", "price"]` or similar context columns
- [ ] Agent runs `--sample-size` preview (e.g., 20 rows) before full synthesis to validate prompt quality
- [ ] Agent presents preview results and cost estimate before proceeding to full dataset
- [ ] Agent runs `validate_synthetic.py` after synthesis to check output quality
- [ ] Agent produces output with `_synthesis_confidence`, `_synthesis_model`, `_synthesis_mode`, `_synthesis_timestamp` metadata columns
- [ ] Agent checkpoints output as `ckpt_05_synthesized.csv` or similar
