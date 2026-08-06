# Prompt Examples Reference

This document provides plain text prompt examples for common data synthesis tasks. These are starting points that the coding agent can adapt — not final templates. They are not Jinja2 templates; they use simple Python string formatting conventions where shown.

Each task shows:
- System instruction (goes into the agent's `instruction` field in YAML or the system turn)
- User prompt (the per-row input sent to the agent)
- Expected output format

---

## fill_missing

**Purpose:** Generate a missing value for one column, using other columns in the same row as context.

### System Instruction

```
You are a data synthesis assistant. Your task is to generate a realistic, contextually
appropriate value for a missing field in a dataset row.

You will receive a JSON object representing one row of the dataset. One field will have
the value null or an empty string — that is the field you must generate a value for.

Rules:
- Respond with ONLY the value for the missing field. No explanation. No JSON wrapper.
- The value must be consistent with the other fields in the row.
- Match the style, format, and range of the column based on the context provided.
- If the column has a specific format (e.g., phone number, date, currency), use that format.
```

### User Prompt

```
Dataset column to fill: "email"
Column description: Work email address for the employee.

Row context:
{
  "first_name": "Maria",
  "last_name": "Santos",
  "department": "Engineering",
  "company": "Acme Corp",
  "email": null
}

Generate a realistic value for the "email" field.
```

### Expected Output Format

```
maria.santos@acmecorp.com
```

Plain value only. No quotes, no JSON, no explanation.

---

## translate

**Purpose:** Translate text from one language to another, preserving meaning and tone.

### System Instruction

```
You are a professional translator. Your task is to translate text accurately while
preserving the original meaning, tone, and formatting.

Rules:
- Translate to the target language specified in the request.
- Preserve paragraph structure and line breaks.
- Do not add explanations, notes, or translator comments.
- Respond with ONLY the translated text.
- If the source text contains untranslatable proper nouns (names, brand names), keep them as-is.
```

### User Prompt

```
Source language: English
Target language: Traditional Chinese

Text to translate:
"The quarterly report shows a 12% increase in customer satisfaction scores,
driven primarily by improvements in our support response time."
```

### Expected Output Format

```
季度報告顯示客戶滿意度得分提升了12%，主要原因是我們的支援回應時間有所改善。
```

Translated text only. No preamble, no language labels, no quotes.

---

## annotate

**Purpose:** Add a classification label or structured annotation to a piece of text.

### System Instruction

```
You are a data annotation assistant. Your task is to classify or label text according
to a provided taxonomy.

Rules:
- Respond with ONLY the label or labels requested. No explanation.
- Use exactly the label names provided in the taxonomy — do not paraphrase or invent new labels.
- If multiple labels apply and multi-label output is requested, return them as a comma-separated list.
- If no label fits, return "other".
```

### User Prompt

```
Task: Classify the sentiment of the following customer review.
Labels: positive, negative, neutral, mixed

Review text:
"The product quality is excellent but the shipping took three weeks and the packaging
was damaged when it arrived."
```

### Expected Output Format

```
mixed
```

Single label from the provided taxonomy. No explanation, no punctuation beyond what the format requires.

For multi-label annotation:

```
Task: Tag the following support ticket with all relevant categories.
Labels: billing, technical, account, shipping, product_defect, feature_request

Ticket:
"I was charged twice for my order and I still haven't received it. Also the item
description on your website says it includes a charger but mine didn't come with one."

Return all applicable labels as a comma-separated list.
```

Expected output:
```
billing, shipping, product_defect
```

---

## summarize

**Purpose:** Generate a concise summary of a longer text.

### System Instruction

```
You are a summarization assistant. Your task is to generate a concise, accurate summary
of the provided text.

Rules:
- Write the summary in the same language as the source text unless instructed otherwise.
- Use the length and format specified in the request.
- Do not add information that is not in the source text.
- Do not include phrases like "This article discusses..." or "The text says...".
- Write in third person unless the source is first person and the request asks to preserve voice.
```

### User Prompt

```
Summarize the following text in 1-2 sentences. Focus on the key finding and its implication.

Text:
"Researchers at the university conducted a three-year longitudinal study tracking 2,400
participants across five cities. The study found that individuals who walked at least
30 minutes per day had a 23% lower risk of developing cardiovascular disease compared
to sedentary individuals, even after controlling for diet, age, and pre-existing conditions.
The findings suggest that moderate daily walking is one of the most cost-effective
interventions for public health programs targeting heart disease prevention."
```

### Expected Output Format

```
A three-year study of 2,400 participants found that walking at least 30 minutes daily
reduces cardiovascular disease risk by 23%. Researchers conclude that moderate daily
walking is among the most cost-effective public health interventions for heart disease prevention.
```

Prose summary only. No bullet points unless the request specifies it. No meta-commentary.

---

## html_to_markdown

**Purpose:** Convert HTML content to clean, readable Markdown.

### System Instruction

```
You are an HTML-to-Markdown converter. Your task is to convert the provided HTML into
clean, well-structured Markdown.

Rules:
- Preserve heading hierarchy (h1 → #, h2 → ##, etc.).
- Convert <strong> and <b> to **bold**, <em> and <i> to *italic*.
- Convert <a href="...">text</a> to [text](url).
- Convert <ul>/<li> to Markdown unordered lists, <ol>/<li> to ordered lists.
- Convert <code> to backtick inline code, <pre><code> to fenced code blocks.
- Remove all HTML tags that have no Markdown equivalent (e.g., <div>, <span>, <class>).
- Do not include the HTML source in your response.
- Respond with ONLY the converted Markdown.
```

### User Prompt

```
Convert the following HTML to Markdown:

<h2>Getting Started</h2>
<p>Welcome to the <strong>Quick Start Guide</strong>. Follow these steps to set up your environment.</p>
<ol>
  <li>Install <a href="https://python.org">Python 3.11</a> or later.</li>
  <li>Run <code>pip install magic-agent</code> in your terminal.</li>
  <li>Copy the example config: <code>cp config.example.yaml config.yaml</code></li>
</ol>
<p>For more details, see the <a href="/docs/setup">full setup documentation</a>.</p>
```

### Expected Output Format

```markdown
## Getting Started

Welcome to the **Quick Start Guide**. Follow these steps to set up your environment.

1. Install [Python 3.11](https://python.org) or later.
2. Run `pip install magic-agent` in your terminal.
3. Copy the example config: `cp config.example.yaml config.yaml`

For more details, see the [full setup documentation](/docs/setup).
```

Clean Markdown only. No HTML remnants. No explanation of what was converted.

---

## extract_structured

**Purpose:** Extract specific structured fields from unstructured text and return them as JSON.

### System Instruction

```
You are a structured data extraction assistant. Your task is to extract specific fields
from unstructured text and return them as a JSON object.

Rules:
- Return ONLY a valid JSON object. No explanation, no preamble, no markdown code fences.
- Include all fields listed in the request, even if a field is not present in the text.
- Use null for fields that cannot be found in the text.
- Do not infer or hallucinate values — only extract what is explicitly stated.
- Match the exact field names specified in the request.
```

### User Prompt

```
Extract the following fields from the text below:
- company_name (string)
- founded_year (integer or null)
- headquarters_city (string or null)
- number_of_employees (integer or null)
- industry (string or null)

Text:
"Acme Manufacturing, established in 1987, is a Chicago-based industrial equipment supplier
serving clients across North America. With over 3,200 employees and three production
facilities, Acme is one of the region's largest privately held manufacturers."
```

### Expected Output Format

```json
{
  "company_name": "Acme Manufacturing",
  "founded_year": 1987,
  "headquarters_city": "Chicago",
  "number_of_employees": 3200,
  "industry": "industrial equipment"
}
```

Valid JSON object only. No code fences, no trailing commentary, no additional keys beyond those requested.

---

## Adapting These Examples

When adapting these prompts for a specific dataset:

1. Replace the generic column descriptions with actual column names and schema descriptions from the user's dataset.
2. Include 2-3 concrete example values from the dataset in the system instruction to anchor the style and format.
3. Specify units, formats, and ranges explicitly (e.g., "date in YYYY-MM-DD format", "currency in USD with 2 decimal places").
4. For `fill_missing`, always include all non-null fields from the row in the user prompt — more context produces more realistic values.
5. For `extract_structured`, list field types explicitly to reduce type coercion errors in the output.
