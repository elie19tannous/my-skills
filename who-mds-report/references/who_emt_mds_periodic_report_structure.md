# WHO EMT MDS Periodic Report — Page Structure Specification

## Purpose

This document describes the structural layout of a multi-page WHO EMT MDS periodic report. It is intended for an agent that will create an HTML report template.

The specification defines **what content appears on each page and where it should be placed**. It does not define colors, fonts, visual style, spacing, or branding.

The report is based on the WHO EMT Minimum Data Set structure used in the Daily Reporting Form and the MDS item definitions.

---

## 1. Global Report Rules

### 1.1 Page model

Each report page should be treated as a separate logical page.

Recommended HTML structure:

```html
<section class="report-page" data-page="{{page_id}}">
  <header>{{page_header}}</header>
  <main>{{page_body}}</main>
  <footer>{{page_footer}}</footer>
</section>
```

### 1.2 Repeated header on every page

Every page should contain the same compact report header.

Header content:

| Position | Content |
|---|---|
| Left | Report title: `WHO EMT MDS Periodic Report` |
| Center | Reporting period: `{{start_date}} – {{end_date}}` |
| Right | Facility or location: `{{facility_name_or_location}}` |

If the report covers multiple facilities, the right side should contain `Multiple facilities` and the details should be shown on Page 2.

### 1.3 Repeated footer on every page

Every page should contain the same compact footer.

Footer content:

| Position | Content |
|---|---|
| Left | Organization/team: `{{organization_name}} / {{team_name}}` |
| Center | Generated on: `{{generated_at}}` |
| Right | Page number: `Page {{page_number}} of {{total_pages}}` |

### 1.4 Page body structure

Each page body should be divided into named sections. A template agent may implement them as blocks, cards, tables, or containers, but the relative order should be preserved.

Recommended body model:

```html
<main>
  <section data-section="section-name">
    {{section_content}}
  </section>
</main>
```

### 1.5 Overflow rule

If a table does not fit on a page:

1. Continue it on a new page.
2. Repeat the table title.
3. Repeat the table header.
4. Add `continued` to the section title.
5. Preserve the same columns.

Example:

```text
Health Events Summary — continued
```

### 1.6 Empty data rule

If a section has no available data, the section should still appear if it is part of the standard report. The content area should contain:

```text
No data available for the selected reporting period.
```

If the data source does not contain a required field, use:

```text
Field not available in source data.
```

### 1.7 Confidentiality rule

The main report must contain aggregated counts only for protection-related and sensitive items. Patient identifiers, clinical narratives, and line-list details must not be shown in the main report.

Sensitive or restricted details should be placed in a separate restricted appendix or generated as a separate restricted report.

---

## 2. Input Data Mapping

### 2.1 Expected source fields

The report generator should support the following source fields when available.

| Field group | Source fields | Use |
|---|---|---|
| Team metadata | `a`, `b`, `d`, `e`, `f`, `g` | Organization, team, contact, phone, email, estimated departure |
| Activity metadata | `h`, `i` | Date of activity, working hours |
| Location metadata | `j`, `k`, `l`, `m`, `n` | Admin 1, Admin 2, Admin 3, facility name, geotag |
| Record identifier | `ID` | Consultation or patient record identifier |
| Age | `MDSa`, `Age`, `M/Y` | WHO MDS age group and derived age groups |
| Sex | `MDS1-3` | Male, female non-pregnant, female pregnant |
| Health events | `MDS4`–`MDS29` | Health event statistics |
| Procedures | `MDS30`–`MDS35` | Procedure statistics |
| Outcomes | `MDS36`–`MDS43` | Outcome statistics |
| Relation to event | `MDS44`–`MDS46` | Direct, indirect, not related |
| Protection | `MDS47`–`MDS50` | Protection indicators |
| Needs and risks | `MDS51`–`MDS65` or external daily comments | Immediate reports, community risks, operational constraints |
| Tool metadata | `ToolVer`, `Ver` | Tool and form version |

### 2.2 MDS item groups

| Group | Items |
|---|---|
| Sex and age | Age categories, `MDS1`–`MDS3` |
| Trauma | `MDS4`–`MDS8` |
| Infectious disease | `MDS9`–`MDS18` |
| Additional diseases | `MDS19`–`MDS22` |
| Emergencies | `MDS23`–`MDS24` |
| Other key diseases | `MDS25`–`MDS29` |
| Procedures | `MDS30`–`MDS35` |
| Outcomes | `MDS36`–`MDS43` |
| Relation | `MDS44`–`MDS46` |
| Protection | `MDS47`–`MDS50` |
| Needs and risks | `MDS51`–`MDS65` |

---

# Page 1 — Cover and Executive Summary

## Page objective

Provide a one-page overview of the reporting period, team, location, total activity, main findings, and critical indicators.

## Body layout

```text
[Section 1: Report metadata]
[Section 2: Key indicators]
[Section 3: Main findings]
[Section 4: Critical flags]
[Section 5: Data availability note]
```

## Section 1: Report metadata

Place at the top of the page.

Use a two-column metadata table.

| Left column | Right column |
|---|---|
| Reporting period | `{{start_date}} – {{end_date}}` |
| Number of calendar days | `{{calendar_days}}` |
| Number of active reporting days | `{{active_reporting_days}}` |
| Organization | `{{organization_name}}` |
| Team name | `{{team_name}}` |
| EMT type | `{{emt_type}}` |
| Facility | `{{facility_name}}` |
| Location | `{{admin1}}, {{admin2}}, {{admin3}}` |
| Source files | `{{source_file_count}}` |
| Generated on | `{{generated_at}}` |

If multiple values exist for organization, team, facility, or location, show the value `Multiple` and list the details on Page 2.

## Section 2: Key indicators

Place below report metadata.

Use a compact indicator table.

| Indicator | Value | Source / calculation |
|---|---:|---|
| Total consultations | `{{total_consultations}}` | Count records or sum daily new consultations |
| Daily average consultations | `{{daily_average_consultations}}` | Total consultations / active reporting days |
| Peak day | `{{peak_day}}` | Date with highest consultation count |
| Peak day consultations | `{{peak_day_consultations}}` | Count on peak day |
| Admissions | `{{mds40_total}}` | Sum `MDS40` |
| Referrals | `{{mds39_total}}` | Sum `MDS39` |
| Deaths total | `{{mds41_total + mds42_total}}` | Sum `MDS41` and `MDS42` |
| Protection-related cases | `{{mds47_total + mds48_total + mds49_total + mds50_total}}` | Sum `MDS47`–`MDS50` |

## Section 3: Main findings

Place below key indicators.

Use short generated text or bullet points.

Content requirements:

```text
- Main consultation trend over the period.
- Top health event groups.
- Most frequent individual MDS health events.
- Main outcome pattern.
- Notable relation-to-event pattern.
```

Do not include unsupported interpretation. Every statement should be based on calculated values.

## Section 4: Critical flags

Place below main findings.

Use a table.

| Flag | Count | Action |
|---|---:|---|
| Death within facility, `MDS42` | `{{mds42_total}}` | Review line list if count > 0 |
| Dead on arrival, `MDS41` | `{{mds41_total}}` | Review if count > 0 |
| Severe Acute Malnutrition, `MDS28` | `{{mds28_total}}` | Review line list if count > 0 |
| Limb amputation excluding digits, `MDS31` | `{{mds31_total}}` | Review line list if count > 0 |
| Long-term rehabilitation, `MDS43` | `{{mds43_total}}` | Review line list if count > 0 |
| Vulnerable child, `MDS47` | `{{mds47_total}}` | Confidential reporting pathway |
| Vulnerable adult, `MDS48` | `{{mds48_total}}` | Confidential reporting pathway |
| SGBV, `MDS49` | `{{mds49_total}}` | Confidential reporting pathway |
| Violence non-SGBV, `MDS50` | `{{mds50_total}}` | Confidential reporting pathway |

## Section 5: Data availability note

Place at the bottom of the page.

Content requirements:

```text
- State whether all days in the requested period are represented.
- State whether Needs and Risks data is available.
- State whether multiple facilities or locations are included.
- State whether restricted line-list items were detected.
```

---

# Page 2 — Reporting Coverage and Operational Context

## Page objective

Show which days, locations, facilities, and source files are included in the report.

## Body layout

```text
[Section 1: Reporting coverage summary]
[Section 2: Daily coverage table]
[Section 3: Facility and location table]
[Section 4: Source data table]
[Section 5: Missing or excluded data]
```

## Section 1: Reporting coverage summary

Place at the top.

Use a small table.

| Field | Value |
|---|---|
| Requested period | `{{start_date}} – {{end_date}}` |
| Calendar days in period | `{{calendar_days}}` |
| Active reporting days | `{{active_reporting_days}}` |
| Missing days | `{{missing_days_count}}` |
| Facilities included | `{{facility_count}}` |
| Records included | `{{included_record_count}}` |
| Records excluded | `{{excluded_record_count}}` |

## Section 2: Daily coverage table

Place below coverage summary.

One row per calendar day in the requested period.

| Date | Status | Facility / facilities | Working hours | Consultations | Source file |
|---|---|---|---|---:|---|
| `{{date}}` | `Reported / Missing / Excluded` | `{{facility_name}}` | `{{working_hours}}` | `{{consultation_count}}` | `{{source_file_name}}` |

## Section 3: Facility and location table

Place below the daily coverage table.

One row per unique facility/location combination.

| Facility | Admin 1 | Admin 2 | Admin 3 | Geotag | First reported date | Last reported date | Records |
|---|---|---|---|---|---|---|---:|
| `{{facility_name}}` | `{{admin1}}` | `{{admin2}}` | `{{admin3}}` | `{{lat_long}}` | `{{first_date}}` | `{{last_date}}` | `{{record_count}}` |

## Section 4: Source data table

Place below facility and location table.

One row per input file.

| Source file | Records loaded | Records included | Date range detected | Tool version | Form version |
|---|---:|---:|---|---|---|
| `{{source_file_name}}` | `{{loaded_count}}` | `{{included_count}}` | `{{detected_start}} – {{detected_end}}` | `{{tool_version}}` | `{{form_version}}` |

## Section 5: Missing or excluded data

Place at the bottom.

Use a short list or table.

| Issue | Details | Impact |
|---|---|---|
| Missing day | `{{date}}` | Day not included in period totals |
| Excluded record | `{{record_id}}` | Reason: `{{exclusion_reason}}` |
| Missing metadata | `{{field_name}}` | Report field unavailable |

---

# Page 3 — Demographic Statistics

## Page objective

Show the distribution of consultations by age and sex using WHO MDS demographic categories.

## Body layout

```text
[Section 1: Demographic summary]
[Section 2: Age and sex matrix]
[Section 3: Age group totals]
[Section 4: Sex category totals]
[Section 5: Demographic data quality]
```

## Section 1: Demographic summary

Place at the top.

Use a compact indicator table.

| Indicator | Value |
|---|---:|
| Total consultations with valid age and sex | `{{valid_age_sex_count}}` |
| Missing age | `{{missing_age_count}}` |
| Missing sex | `{{missing_sex_count}}` |
| Under 5 consultations | `{{under5_count}}` |
| Under 5 percentage | `{{under5_percentage}}` |
| Age 65+ consultations | `{{age65plus_count}}` |
| Pregnant patients | `{{pregnant_count}}` |

## Section 2: Age and sex matrix

Place below demographic summary.

Use the same logical categories as the MDS Daily Reporting Form.

| Sex / age category | `<1` | `1–4` | `5–17` | `18–64` | `65+` | Total |
|---|---:|---:|---:|---:|---:|---:|
| Male | `{{male_under1}}` | `{{male_1_4}}` | `{{male_5_17}}` | `{{male_18_64}}` | `{{male_65plus}}` | `{{male_total}}` |
| Female non-pregnant | `{{female_non_preg_under1}}` | `{{female_non_preg_1_4}}` | `{{female_non_preg_5_17}}` | `{{female_non_preg_18_64}}` | `{{female_non_preg_65plus}}` | `{{female_non_preg_total}}` |
| Female pregnant | `N/A` | `N/A` | `{{female_preg_5_17}}` | `{{female_preg_18_64}}` | `{{female_preg_65plus}}` | `{{female_preg_total}}` |
| Total | `{{under1_total}}` | `{{age_1_4_total}}` | `{{age_5_17_total}}` | `{{age_18_64_total}}` | `{{age_65plus_total}}` | `{{demographic_total}}` |

## Section 3: Age group totals

Place below or beside the matrix depending on available space.

| Age group | Count | Percentage of consultations |
|---|---:|---:|
| `<1` | `{{under1_total}}` | `{{under1_percentage}}` |
| `1–4` | `{{age_1_4_total}}` | `{{age_1_4_percentage}}` |
| `5–17` | `{{age_5_17_total}}` | `{{age_5_17_percentage}}` |
| `18–64` | `{{age_18_64_total}}` | `{{age_18_64_percentage}}` |
| `65+` | `{{age_65plus_total}}` | `{{age_65plus_percentage}}` |
| Missing / unknown | `{{age_unknown_total}}` | `{{age_unknown_percentage}}` |

## Section 4: Sex category totals

Place beside or below age group totals.

| Sex category | Count | Percentage of consultations |
|---|---:|---:|
| Male | `{{male_total}}` | `{{male_percentage}}` |
| Female non-pregnant | `{{female_non_preg_total}}` | `{{female_non_preg_percentage}}` |
| Female pregnant | `{{female_preg_total}}` | `{{female_preg_percentage}}` |
| Missing / unknown | `{{sex_unknown_total}}` | `{{sex_unknown_percentage}}` |

## Section 5: Demographic data quality

Place at the bottom.

| Check | Count | Notes |
|---|---:|---|
| Missing age | `{{missing_age_count}}` | Records without usable age |
| Missing sex | `{{missing_sex_count}}` | Records without usable sex category |
| Invalid age group | `{{invalid_age_group_count}}` | Records outside expected categories |
| Conflicting age fields | `{{conflicting_age_count}}` | Records where `MDSa`, `Age`, and `M/Y` do not align |

---

# Page 4 — Health Events Summary

## Page objective

Show period totals for all MDS health event items, grouped according to the WHO MDS structure.

## Body layout

```text
[Section 1: Health event group totals]
[Section 2: Top health events]
[Section 3: Full health event table]
```

## Section 1: Health event group totals

Place at the top.

| Health event group | MDS items | Count | Percentage of consultations |
|---|---|---:|---:|
| Trauma | `MDS4–MDS8` | `{{trauma_total}}` | `{{trauma_percentage}}` |
| Infectious disease | `MDS9–MDS18` | `{{infectious_total}}` | `{{infectious_percentage}}` |
| Additional diseases | `MDS19–MDS22` | `{{additional_total}}` | `{{additional_percentage}}` |
| Emergencies | `MDS23–MDS24` | `{{emergency_total}}` | `{{emergency_percentage}}` |
| Other key diseases | `MDS25–MDS29` | `{{other_key_diseases_total}}` | `{{other_key_diseases_percentage}}` |

## Section 2: Top health events

Place below group totals.

Show the top 10 individual MDS health events by count.

| Rank | MDS No. | Health event | Count | Percentage of consultations |
|---:|---:|---|---:|---:|
| `{{rank}}` | `{{mds_no}}` | `{{mds_label}}` | `{{count}}` | `{{percentage}}` |

## Section 3: Full health event table

Place below top health events.

Preserve this group order:

1. Trauma
2. Infectious disease
3. Additional diseases
4. Emergencies
5. Other key diseases

| Group | MDS No. | Health event | `<5` | `>=5` | Total | Percentage of consultations |
|---|---:|---|---:|---:|---:|---:|
| Trauma | 4 | Major head / spine injury | `{{mds4_under5}}` | `{{mds4_5plus}}` | `{{mds4_total}}` | `{{mds4_percentage}}` |
| Trauma | 5 | Major torso injury | `{{mds5_under5}}` | `{{mds5_5plus}}` | `{{mds5_total}}` | `{{mds5_percentage}}` |
| Trauma | 6 | Major extremity injury | `{{mds6_under5}}` | `{{mds6_5plus}}` | `{{mds6_total}}` | `{{mds6_percentage}}` |
| Trauma | 7 | Moderate injury | `{{mds7_under5}}` | `{{mds7_5plus}}` | `{{mds7_total}}` | `{{mds7_percentage}}` |
| Trauma | 8 | Minor injury | `{{mds8_under5}}` | `{{mds8_5plus}}` | `{{mds8_total}}` | `{{mds8_percentage}}` |
| Infectious disease | 9 | Acute respiratory infection | `{{mds9_under5}}` | `{{mds9_5plus}}` | `{{mds9_total}}` | `{{mds9_percentage}}` |
| Infectious disease | 10 | Acute watery diarrhea | `{{mds10_under5}}` | `{{mds10_5plus}}` | `{{mds10_total}}` | `{{mds10_percentage}}` |
| Infectious disease | 11 | Acute bloody diarrhea | `{{mds11_under5}}` | `{{mds11_5plus}}` | `{{mds11_total}}` | `{{mds11_percentage}}` |
| Infectious disease | 12 | Acute jaundice syndrome | `{{mds12_under5}}` | `{{mds12_5plus}}` | `{{mds12_total}}` | `{{mds12_percentage}}` |
| Infectious disease | 13 | Suspected measles | `{{mds13_under5}}` | `{{mds13_5plus}}` | `{{mds13_total}}` | `{{mds13_percentage}}` |
| Infectious disease | 14 | Suspected meningitis | `{{mds14_under5}}` | `{{mds14_5plus}}` | `{{mds14_total}}` | `{{mds14_percentage}}` |
| Infectious disease | 15 | Suspected tetanus | `{{mds15_under5}}` | `{{mds15_5plus}}` | `{{mds15_total}}` | `{{mds15_percentage}}` |
| Infectious disease | 16 | Acute flaccid paralysis | `{{mds16_under5}}` | `{{mds16_5plus}}` | `{{mds16_total}}` | `{{mds16_percentage}}` |
| Infectious disease | 17 | Tuberculous Bronchitis, suspected/confirmed | `{{mds17_under5}}` | `{{mds17_5plus}}` | `{{mds17_total}}` | `{{mds17_percentage}}` |
| Infectious disease | 18 | Fever of unknown origin | `{{mds18_under5}}` | `{{mds18_5plus}}` | `{{mds18_total}}` | `{{mds18_percentage}}` |
| Additional diseases | 19 | COVID-19, suspected/confirmed | `{{mds19_under5}}` | `{{mds19_5plus}}` | `{{mds19_total}}` | `{{mds19_percentage}}` |
| Additional diseases | 20 | Hypertension | `{{mds20_under5}}` | `{{mds20_5plus}}` | `{{mds20_total}}` | `{{mds20_percentage}}` |
| Additional diseases | 21 | Diabetes mellitus | `{{mds21_under5}}` | `{{mds21_5plus}}` | `{{mds21_total}}` | `{{mds21_percentage}}` |
| Additional diseases | 22 | Musculoskeletal conditions | `{{mds22_under5}}` | `{{mds22_5plus}}` | `{{mds22_total}}` | `{{mds22_percentage}}` |
| Emergencies | 23 | Surgical emergency, non-trauma | `{{mds23_under5}}` | `{{mds23_5plus}}` | `{{mds23_total}}` | `{{mds23_percentage}}` |
| Emergencies | 24 | Medical emergency, non-infectious | `{{mds24_under5}}` | `{{mds24_5plus}}` | `{{mds24_total}}` | `{{mds24_percentage}}` |
| Other key diseases | 25 | Skin disease | `{{mds25_under5}}` | `{{mds25_5plus}}` | `{{mds25_total}}` | `{{mds25_percentage}}` |
| Other key diseases | 26 | Acute mental health problem | `{{mds26_under5}}` | `{{mds26_5plus}}` | `{{mds26_total}}` | `{{mds26_percentage}}` |
| Other key diseases | 27 | Obstetric complications | `{{mds27_under5}}` | `{{mds27_5plus}}` | `{{mds27_total}}` | `{{mds27_percentage}}` |
| Other key diseases | 28 | Severe Acute Malnutrition | `{{mds28_under5}}` | `{{mds28_5plus}}` | `{{mds28_total}}` | `{{mds28_percentage}}` |
| Other key diseases | 29 | Other diagnosis, not specified above | `{{mds29_under5}}` | `{{mds29_5plus}}` | `{{mds29_total}}` | `{{mds29_percentage}}` |

---

# Page 5 — Health Events Trends

## Page objective

Show how consultations and health events changed over the selected reporting period.

## Body layout

```text
[Section 1: Daily consultation trend]
[Section 2: Daily health event group trend]
[Section 3: Top individual event trends]
[Section 4: Trend interpretation notes]
```

## Section 1: Daily consultation trend

Place at the top.

Use a chart placeholder and a backup table.

Required data series:

```text
Date → consultation count
```

Fallback table:

| Date | Consultations |
|---|---:|
| `{{date}}` | `{{consultation_count}}` |

## Section 2: Daily health event group trend

Place below the consultation trend.

Use either a chart placeholder or a table.

| Date | Trauma | Infectious disease | Additional diseases | Emergencies | Other key diseases |
|---|---:|---:|---:|---:|---:|
| `{{date}}` | `{{trauma_count}}` | `{{infectious_count}}` | `{{additional_count}}` | `{{emergency_count}}` | `{{other_key_diseases_count}}` |

## Section 3: Top individual event trends

Place below group trend.

Include only the top 5 individual MDS health events by total count.

| Date | `{{top_event_1}}` | `{{top_event_2}}` | `{{top_event_3}}` | `{{top_event_4}}` | `{{top_event_5}}` |
|---|---:|---:|---:|---:|---:|
| `{{date}}` | `{{count}}` | `{{count}}` | `{{count}}` | `{{count}}` | `{{count}}` |

## Section 4: Trend interpretation notes

Place at the bottom.

Use short generated statements.

Allowed statement patterns:

```text
- Highest consultation volume occurred on {{peak_day}}.
- {{event_name}} was the most frequently recorded health event.
- {{event_group}} increased from {{first_period_count}} to {{second_period_count}} between the first and second part of the period.
- Counts are low; interpret trend cautiously.
- No clear trend detected in the selected period.
```

Do not include clinical causation unless it is explicitly supported by external operational context.

---

# Page 6 — Procedures and Outcomes

## Page objective

Show all MDS procedures and outcomes for the reporting period.

## Body layout

```text
[Section 1: Procedure summary]
[Section 2: Outcome summary]
[Section 3: Derived operational indicators]
[Section 4: Outcome notes]
```

## Section 1: Procedure summary

Place in the upper half of the page.

| MDS No. | Procedure | `<5` | `>=5` | Total | Percentage of consultations |
|---:|---|---:|---:|---:|---:|
| 30 | Major procedure excluding MDS31 | `{{mds30_under5}}` | `{{mds30_5plus}}` | `{{mds30_total}}` | `{{mds30_percentage}}` |
| 31 | Limb amputation excluding digits | `{{mds31_under5}}` | `{{mds31_5plus}}` | `{{mds31_total}}` | `{{mds31_percentage}}` |
| 32 | Minor surgical procedure | `{{mds32_under5}}` | `{{mds32_5plus}}` | `{{mds32_total}}` | `{{mds32_percentage}}` |
| 33 | Normal Vaginal Delivery | `{{mds33_under5}}` | `{{mds33_5plus}}` | `{{mds33_total}}` | `{{mds33_percentage}}` |
| 34 | Caesarean section | `{{mds34_under5}}` | `{{mds34_5plus}}` | `{{mds34_total}}` | `{{mds34_percentage}}` |
| 35 | Obstetrics others | `{{mds35_under5}}` | `{{mds35_5plus}}` | `{{mds35_total}}` | `{{mds35_percentage}}` |

## Section 2: Outcome summary

Place below procedure summary.

| MDS No. | Outcome | Count | Percentage of consultations |
|---:|---|---:|---:|
| 36 | Discharge without medical follow-up | `{{mds36_total}}` | `{{mds36_percentage}}` |
| 37 | Discharge with medical follow-up | `{{mds37_total}}` | `{{mds37_percentage}}` |
| 38 | Discharge against medical advice | `{{mds38_total}}` | `{{mds38_percentage}}` |
| 39 | Referral | `{{mds39_total}}` | `{{mds39_percentage}}` |
| 40 | Admission | `{{mds40_total}}` | `{{mds40_percentage}}` |
| 41 | Dead on arrival | `{{mds41_total}}` | `{{mds41_percentage}}` |
| 42 | Death within facility | `{{mds42_total}}` | `{{mds42_percentage}}` |
| 43 | Requiring long-term rehabilitation | `{{mds43_total}}` | `{{mds43_percentage}}` |

## Section 3: Derived operational indicators

Place below outcome summary.

| Indicator | Formula | Value |
|---|---|---:|
| Procedure rate | `(MDS30 + MDS31 + MDS32 + MDS33 + MDS34 + MDS35) / total consultations` | `{{procedure_rate}}` |
| Referral rate | `MDS39 / total consultations` | `{{referral_rate}}` |
| Admission rate | `MDS40 / total consultations` | `{{admission_rate}}` |
| Death count | `MDS41 + MDS42` | `{{death_total}}` |
| Follow-up count | `MDS37 + MDS43` | `{{followup_total}}` |

## Section 4: Outcome notes

Place at the bottom.

Content requirements:

```text
- Mention whether MDS43 is treated as a subset of discharge with follow-up / discharge against medical advice.
- Mention whether any death or restricted procedure was detected.
- Mention whether outcome totals are incomplete or inconsistent.
```

---

# Page 7 — Relation to Event and Protection

## Page objective

Show whether consultations were directly, indirectly, or not related to the emergency event, and show aggregated protection indicators.

## Body layout

```text
[Section 1: Relation to event]
[Section 2: Protection indicators]
[Section 3: Confidentiality and reporting note]
[Section 4: Restricted appendix trigger summary]
```

## Section 1: Relation to event

Place at the top.

| MDS No. | Relation category | Count | Percentage of consultations |
|---:|---|---:|---:|
| 44 | Directly related to event | `{{mds44_total}}` | `{{mds44_percentage}}` |
| 45 | Indirectly related to event | `{{mds45_total}}` | `{{mds45_percentage}}` |
| 46 | Not related to event | `{{mds46_total}}` | `{{mds46_percentage}}` |
| Missing / unclear | No valid relation selected | `{{missing_relation_total}}` | `{{missing_relation_percentage}}` |
| Multiple selected | More than one relation selected | `{{multiple_relation_total}}` | `{{multiple_relation_percentage}}` |

## Section 2: Protection indicators

Place below relation table.

Only aggregated counts should appear here.

| MDS No. | Protection indicator | Count | Reporting note |
|---:|---|---:|---|
| 47 | Vulnerable child | `{{mds47_total}}` | Confidential pathway if count > 0 |
| 48 | Vulnerable adult | `{{mds48_total}}` | Confidential pathway if count > 0 |
| 49 | Sexual Gender Based Violence | `{{mds49_total}}` | Confidential pathway if count > 0 |
| 50 | Violence non-SGBV | `{{mds50_total}}` | Confidential pathway if count > 0 |

## Section 3: Confidentiality and reporting note

Place below protection table.

Required text:

```text
Protection-related details must not be included in the main report. Only aggregated counts are shown. Detailed line-list information, if generated, must be handled as a restricted appendix and shared only through the locally agreed confidential reporting pathway.
```

## Section 4: Restricted appendix trigger summary

Place at the bottom.

| Trigger group | Items included | Trigger count |
|---|---|---:|
| Protection | `MDS47–MDS50` | `{{protection_trigger_total}}` |
| Deaths | `MDS42` | `{{mds42_total}}` |
| Severe Acute Malnutrition | `MDS28` | `{{mds28_total}}` |
| Limb amputation | `MDS31` | `{{mds31_total}}` |
| Long-term rehabilitation | `MDS43` | `{{mds43_total}}` |

---

# Page 8 — Needs, Risks and Operational Constraints

## Page objective

Show immediate reports, community risks, operational constraints, and detailed comments reported during the period.

## Body layout

```text
[Section 1: Needs and risks availability]
[Section 2: Immediate reports]
[Section 3: Community risks]
[Section 4: Operational constraints]
[Section 5: Detailed comments]
[Section 6: Actions required]
```

## Section 1: Needs and risks availability

Place at the top.

| Field | Value |
|---|---|
| Needs and Risks data available | `{{needs_risks_available}}` |
| Data source | `{{needs_risks_source}}` |
| Dates covered | `{{needs_risks_date_range}}` |
| Comments available | `{{comments_available}}` |

## Section 2: Immediate reports

Place below availability table.

| MDS No. | Issue | Dates reported | Count | Latest comment |
|---:|---|---|---:|---|
| 51 | Unexpected death | `{{mds51_dates}}` | `{{mds51_total}}` | `{{mds51_latest_comment}}` |
| 52 | Notifiable disease | `{{mds52_dates}}` | `{{mds52_total}}` | `{{mds52_latest_comment}}` |
| 53 | Protection issues | `{{mds53_dates}}` | `{{mds53_total}}` | `{{mds53_latest_comment}}` |
| 54 | Critical incident to EMT and/or community | `{{mds54_dates}}` | `{{mds54_total}}` | `{{mds54_latest_comment}}` |
| 55 | Any other issue requiring immediate reporting | `{{mds55_dates}}` | `{{mds55_total}}` | `{{mds55_latest_comment}}` |

## Section 3: Community risks

Place below immediate reports.

| MDS No. | Risk | Dates reported | Count | Latest comment |
|---:|---|---|---:|---|
| 56 | WASH | `{{mds56_dates}}` | `{{mds56_total}}` | `{{mds56_latest_comment}}` |
| 57 | Community / suspected over infectious disease | `{{mds57_dates}}` | `{{mds57_total}}` | `{{mds57_latest_comment}}` |
| 58 | Environmental risk / exposure | `{{mds58_dates}}` | `{{mds58_total}}` | `{{mds58_latest_comment}}` |
| 59 | Shelter / Non-food items | `{{mds59_dates}}` | `{{mds59_total}}` | `{{mds59_latest_comment}}` |
| 60 | Food insecurity | `{{mds60_dates}}` | `{{mds60_total}}` | `{{mds60_latest_comment}}` |

## Section 4: Operational constraints

Place below community risks.

| MDS No. | Constraint | Dates reported | Count | Latest comment |
|---:|---|---|---:|---|
| 61 | Logistics / operational support | `{{mds61_dates}}` | `{{mds61_total}}` | `{{mds61_latest_comment}}` |
| 62 | Supply | `{{mds62_dates}}` | `{{mds62_total}}` | `{{mds62_latest_comment}}` |
| 63 | Human resources | `{{mds63_dates}}` | `{{mds63_total}}` | `{{mds63_latest_comment}}` |
| 64 | Finance | `{{mds64_dates}}` | `{{mds64_total}}` | `{{mds64_latest_comment}}` |
| 65 | Others | `{{mds65_dates}}` | `{{mds65_total}}` | `{{mds65_latest_comment}}` |

## Section 5: Detailed comments

Place below operational constraints. If comments are long, continue on the next page.

| Date | MDS No. | Category | Comment | Action / follow-up |
|---|---:|---|---|---|
| `{{date}}` | `{{mds_no}}` | `{{category}}` | `{{comment}}` | `{{action_required}}` |

## Section 6: Actions required

Place at the bottom.

| Priority | Action | Related MDS item | Responsible actor | Status |
|---|---|---:|---|---|
| `{{priority}}` | `{{action}}` | `{{mds_no}}` | `{{responsible_actor}}` | `{{status}}` |

---

# Page 9 — Data Quality and Validation

## Page objective

Show whether the report is reliable, complete, and internally consistent.

## Body layout

```text
[Section 1: Data quality summary]
[Section 2: Validation checks]
[Section 3: Records requiring review]
[Section 4: Calculation assumptions]
```

## Section 1: Data quality summary

Place at the top.

| Indicator | Value |
|---|---:|
| Records loaded | `{{records_loaded}}` |
| Records included | `{{records_included}}` |
| Records excluded | `{{records_excluded}}` |
| Duplicate IDs detected | `{{duplicate_id_count}}` |
| Missing required fields | `{{missing_required_field_count}}` |
| Records with validation warnings | `{{warning_record_count}}` |
| Records with validation errors | `{{error_record_count}}` |

## Section 2: Validation checks

Place below summary.

| Check | Rule | Result | Count | Severity |
|---|---|---|---:|---|
| Date present | Every included row should have an activity date | `{{date_check_result}}` | `{{date_check_count}}` | Critical |
| Unique record ID | Same `ID` should not repeat for same date and facility | `{{duplicate_id_result}}` | `{{duplicate_id_count}}` | High |
| Age valid | Age should map to one WHO MDS age group | `{{age_check_result}}` | `{{age_check_count}}` | High |
| Sex valid | Sex should map to one of MDS1–MDS3 | `{{sex_check_result}}` | `{{sex_check_count}}` | High |
| MDS checkbox valid | MDS values should be binary or blank | `{{checkbox_check_result}}` | `{{checkbox_check_count}}` | High |
| Outcome selected | Each clinical record should have a valid outcome where applicable | `{{outcome_check_result}}` | `{{outcome_check_count}}` | Medium |
| Relation selected | At most one of MDS44–MDS46 should be selected | `{{relation_check_result}}` | `{{relation_check_count}}` | Medium |
| Restricted items detected | Starred/sensitive items should trigger restricted appendix | `{{restricted_check_result}}` | `{{restricted_check_count}}` | Critical |

## Section 3: Records requiring review

Place below validation checks.

Do not include clinical details. Use internal IDs only.

| Record ID | Date | Facility | Issue | Severity |
|---|---|---|---|---|
| `{{record_id}}` | `{{date}}` | `{{facility}}` | `{{issue}}` | `{{severity}}` |

## Section 4: Calculation assumptions

Place at the bottom.

Include assumptions used by the generator.

Required assumptions:

```text
- Consultation total calculation method.
- Age group derivation method.
- Handling of missing age or sex.
- Handling of multiple MDS items selected for one record.
- Handling of multiple facilities in one period.
- Handling of unavailable Needs and Risks fields.
- Handling of restricted line-list triggers.
```

---

# Appendix A — Daily Breakdown

## Page objective

Provide a detailed day-by-day summary of all key report indicators.

## Placement

This appendix starts after the main report pages. It may continue across multiple pages.

## Body layout

```text
[Section 1: Daily breakdown table]
[Section 2: Daily notes]
```

## Section 1: Daily breakdown table

One row per date and facility.

| Date | Facility | Consultations | Under 5 | 65+ | Trauma | Infectious disease | Procedures | Referrals | Admissions | Deaths | Protection | Relation direct | Relation indirect | Relation not related |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `{{date}}` | `{{facility}}` | `{{consultations}}` | `{{under5}}` | `{{age65plus}}` | `{{trauma}}` | `{{infectious}}` | `{{procedures}}` | `{{referrals}}` | `{{admissions}}` | `{{deaths}}` | `{{protection}}` | `{{direct}}` | `{{indirect}}` | `{{not_related}}` |

## Section 2: Daily notes

Place below the table or on continuation pages.

| Date | Note type | Note |
|---|---|---|
| `{{date}}` | `{{note_type}}` | `{{note_text}}` |

---

# Appendix B — Full MDS Item Totals

## Page objective

Provide a complete table of all MDS items included in the report.

## Placement

This appendix starts after Appendix A. It may continue across multiple pages.

## Body layout

```text
[Section 1: Full MDS item totals]
```

## Section 1: Full MDS item totals

| MDS No. | Category | Item | `<5` | `>=5` | Total | Percentage of consultations | Restricted trigger |
|---:|---|---|---:|---:|---:|---:|---|
| 4 | Trauma | Major head / spine injury | `{{mds4_under5}}` | `{{mds4_5plus}}` | `{{mds4_total}}` | `{{mds4_percentage}}` | No |
| 5 | Trauma | Major torso injury | `{{mds5_under5}}` | `{{mds5_5plus}}` | `{{mds5_total}}` | `{{mds5_percentage}}` | No |
| 6 | Trauma | Major extremity injury | `{{mds6_under5}}` | `{{mds6_5plus}}` | `{{mds6_total}}` | `{{mds6_percentage}}` | No |
| 7 | Trauma | Moderate injury | `{{mds7_under5}}` | `{{mds7_5plus}}` | `{{mds7_total}}` | `{{mds7_percentage}}` | No |
| 8 | Trauma | Minor injury | `{{mds8_under5}}` | `{{mds8_5plus}}` | `{{mds8_total}}` | `{{mds8_percentage}}` | No |
| 9 | Infectious disease | Acute respiratory infection | `{{mds9_under5}}` | `{{mds9_5plus}}` | `{{mds9_total}}` | `{{mds9_percentage}}` | No |
| 10 | Infectious disease | Acute watery diarrhea | `{{mds10_under5}}` | `{{mds10_5plus}}` | `{{mds10_total}}` | `{{mds10_percentage}}` | No |
| 11 | Infectious disease | Acute bloody diarrhea | `{{mds11_under5}}` | `{{mds11_5plus}}` | `{{mds11_total}}` | `{{mds11_percentage}}` | No |
| 12 | Infectious disease | Acute jaundice syndrome | `{{mds12_under5}}` | `{{mds12_5plus}}` | `{{mds12_total}}` | `{{mds12_percentage}}` | No |
| 13 | Infectious disease | Suspected measles | `{{mds13_under5}}` | `{{mds13_5plus}}` | `{{mds13_total}}` | `{{mds13_percentage}}` | No |
| 14 | Infectious disease | Suspected meningitis | `{{mds14_under5}}` | `{{mds14_5plus}}` | `{{mds14_total}}` | `{{mds14_percentage}}` | No |
| 15 | Infectious disease | Suspected tetanus | `{{mds15_under5}}` | `{{mds15_5plus}}` | `{{mds15_total}}` | `{{mds15_percentage}}` | No |
| 16 | Infectious disease | Acute flaccid paralysis | `{{mds16_under5}}` | `{{mds16_5plus}}` | `{{mds16_total}}` | `{{mds16_percentage}}` | No |
| 17 | Infectious disease | Tuberculous Bronchitis, suspected/confirmed | `{{mds17_under5}}` | `{{mds17_5plus}}` | `{{mds17_total}}` | `{{mds17_percentage}}` | No |
| 18 | Infectious disease | Fever of unknown origin | `{{mds18_under5}}` | `{{mds18_5plus}}` | `{{mds18_total}}` | `{{mds18_percentage}}` | No |
| 19 | Additional diseases | COVID-19, suspected/confirmed | `{{mds19_under5}}` | `{{mds19_5plus}}` | `{{mds19_total}}` | `{{mds19_percentage}}` | No |
| 20 | Additional diseases | Hypertension | `{{mds20_under5}}` | `{{mds20_5plus}}` | `{{mds20_total}}` | `{{mds20_percentage}}` | No |
| 21 | Additional diseases | Diabetes mellitus | `{{mds21_under5}}` | `{{mds21_5plus}}` | `{{mds21_total}}` | `{{mds21_percentage}}` | No |
| 22 | Additional diseases | Musculoskeletal conditions | `{{mds22_under5}}` | `{{mds22_5plus}}` | `{{mds22_total}}` | `{{mds22_percentage}}` | No |
| 23 | Emergencies | Surgical emergency, non-trauma | `{{mds23_under5}}` | `{{mds23_5plus}}` | `{{mds23_total}}` | `{{mds23_percentage}}` | No |
| 24 | Emergencies | Medical emergency, non-infectious | `{{mds24_under5}}` | `{{mds24_5plus}}` | `{{mds24_total}}` | `{{mds24_percentage}}` | No |
| 25 | Other key diseases | Skin disease | `{{mds25_under5}}` | `{{mds25_5plus}}` | `{{mds25_total}}` | `{{mds25_percentage}}` | No |
| 26 | Other key diseases | Acute mental health problem | `{{mds26_under5}}` | `{{mds26_5plus}}` | `{{mds26_total}}` | `{{mds26_percentage}}` | No |
| 27 | Other key diseases | Obstetric complications | `{{mds27_under5}}` | `{{mds27_5plus}}` | `{{mds27_total}}` | `{{mds27_percentage}}` | No |
| 28 | Other key diseases | Severe Acute Malnutrition | `{{mds28_under5}}` | `{{mds28_5plus}}` | `{{mds28_total}}` | `{{mds28_percentage}}` | Yes |
| 29 | Other key diseases | Other diagnosis, not specified above | `{{mds29_under5}}` | `{{mds29_5plus}}` | `{{mds29_total}}` | `{{mds29_percentage}}` | No |
| 30 | Procedure | Major procedure excluding MDS31 | `{{mds30_under5}}` | `{{mds30_5plus}}` | `{{mds30_total}}` | `{{mds30_percentage}}` | No |
| 31 | Procedure | Limb amputation excluding digits | `{{mds31_under5}}` | `{{mds31_5plus}}` | `{{mds31_total}}` | `{{mds31_percentage}}` | Yes |
| 32 | Procedure | Minor surgical procedure | `{{mds32_under5}}` | `{{mds32_5plus}}` | `{{mds32_total}}` | `{{mds32_percentage}}` | No |
| 33 | Procedure | Normal Vaginal Delivery | `{{mds33_under5}}` | `{{mds33_5plus}}` | `{{mds33_total}}` | `{{mds33_percentage}}` | No |
| 34 | Procedure | Caesarean section | `{{mds34_under5}}` | `{{mds34_5plus}}` | `{{mds34_total}}` | `{{mds34_percentage}}` | No |
| 35 | Procedure | Obstetrics others | `{{mds35_under5}}` | `{{mds35_5plus}}` | `{{mds35_total}}` | `{{mds35_percentage}}` | No |
| 36 | Outcome | Discharge without medical follow-up | `N/A` | `N/A` | `{{mds36_total}}` | `{{mds36_percentage}}` | No |
| 37 | Outcome | Discharge with medical follow-up | `N/A` | `N/A` | `{{mds37_total}}` | `{{mds37_percentage}}` | No |
| 38 | Outcome | Discharge against medical advice | `N/A` | `N/A` | `{{mds38_total}}` | `{{mds38_percentage}}` | No |
| 39 | Outcome | Referral | `N/A` | `N/A` | `{{mds39_total}}` | `{{mds39_percentage}}` | No |
| 40 | Outcome | Admission | `N/A` | `N/A` | `{{mds40_total}}` | `{{mds40_percentage}}` | No |
| 41 | Outcome | Dead on arrival | `N/A` | `N/A` | `{{mds41_total}}` | `{{mds41_percentage}}` | No |
| 42 | Outcome | Death within facility | `N/A` | `N/A` | `{{mds42_total}}` | `{{mds42_percentage}}` | Yes |
| 43 | Outcome | Requiring long-term rehabilitation | `N/A` | `N/A` | `{{mds43_total}}` | `{{mds43_percentage}}` | Yes |
| 44 | Relation | Directly related to event | `N/A` | `N/A` | `{{mds44_total}}` | `{{mds44_percentage}}` | No |
| 45 | Relation | Indirectly related to event | `N/A` | `N/A` | `{{mds45_total}}` | `{{mds45_percentage}}` | No |
| 46 | Relation | Not related to event | `N/A` | `N/A` | `{{mds46_total}}` | `{{mds46_percentage}}` | No |
| 47 | Protection | Vulnerable child | `N/A` | `N/A` | `{{mds47_total}}` | `{{mds47_percentage}}` | Yes |
| 48 | Protection | Vulnerable adult | `N/A` | `N/A` | `{{mds48_total}}` | `{{mds48_percentage}}` | Yes |
| 49 | Protection | Sexual Gender Based Violence | `N/A` | `N/A` | `{{mds49_total}}` | `{{mds49_percentage}}` | Yes |
| 50 | Protection | Violence non-SGBV | `N/A` | `N/A` | `{{mds50_total}}` | `{{mds50_percentage}}` | Yes |

---

# Appendix C — Restricted Line-List Trigger Summary

## Page objective

Identify records that require restricted follow-up without exposing sensitive details in the main report.

## Placement

This appendix should be generated as a separate restricted report or placed after the public appendices with access control.

## Body layout

```text
[Section 1: Restricted trigger summary]
[Section 2: Restricted record list]
[Section 3: Handling notes]
```

## Section 1: Restricted trigger summary

| MDS No. | Trigger item | Count |
|---:|---|---:|
| 28 | Severe Acute Malnutrition | `{{mds28_total}}` |
| 31 | Limb amputation excluding digits | `{{mds31_total}}` |
| 42 | Death within facility | `{{mds42_total}}` |
| 43 | Requiring long-term rehabilitation | `{{mds43_total}}` |
| 47 | Vulnerable child | `{{mds47_total}}` |
| 48 | Vulnerable adult | `{{mds48_total}}` |
| 49 | Sexual Gender Based Violence | `{{mds49_total}}` |
| 50 | Violence non-SGBV | `{{mds50_total}}` |

## Section 2: Restricted record list

Use internal identifiers only unless the locally approved reporting pathway requires more detail.

| Record ID | Date | Facility | MDS No. | Trigger item | Age group | Sex category | Action taken | Follow-up status |
|---|---|---|---:|---|---|---|---|---|
| `{{record_id}}` | `{{date}}` | `{{facility}}` | `{{mds_no}}` | `{{trigger_item}}` | `{{age_group}}` | `{{sex_category}}` | `{{action_taken}}` | `{{followup_status}}` |

## Section 3: Handling notes

Required text:

```text
This appendix contains restricted information. It should be shared only with authorized recipients through the locally agreed confidential reporting pathway. Do not include patient-identifiable details unless explicitly required and authorized.
```

---

# Appendix D — Template Component Inventory

## Page objective

List reusable components that the HTML template agent should implement.

## Components

| Component ID | Purpose | Used on pages |
|---|---|---|
| `report-header` | Repeated page header | All pages |
| `report-footer` | Repeated page footer | All pages |
| `metadata-table` | Report/team/location metadata | Page 1, Page 2 |
| `indicator-table` | Key numeric metrics | Page 1, Page 3, Page 9 |
| `summary-bullets` | Generated short findings | Page 1, Page 5 |
| `coverage-table` | Date coverage and source completeness | Page 2 |
| `facility-location-table` | Facility and location details | Page 2 |
| `age-sex-matrix` | WHO demographic matrix | Page 3 |
| `group-total-table` | MDS group totals | Page 4 |
| `top-items-table` | Ranked MDS items | Page 4 |
| `mds-health-events-table` | Full health event totals | Page 4 |
| `trend-chart-placeholder` | Trend visualization placeholder | Page 5 |
| `trend-data-table` | Trend backup table | Page 5 |
| `procedure-table` | MDS30–MDS35 | Page 6 |
| `outcome-table` | MDS36–MDS43 | Page 6 |
| `relation-table` | MDS44–MDS46 | Page 7 |
| `protection-table` | MDS47–MDS50 aggregated counts | Page 7 |
| `needs-risks-table` | MDS51–MDS65 | Page 8 |
| `comments-table` | Detailed operational comments | Page 8 |
| `validation-table` | Data quality checks | Page 9 |
| `daily-breakdown-table` | Per-day values | Appendix A |
| `full-mds-table` | All MDS item totals | Appendix B |
| `restricted-trigger-table` | Restricted line-list trigger summary | Appendix C |

---

# Appendix E — Required Placeholder Variables

## Global placeholders

```text
{{report_title}}
{{start_date}}
{{end_date}}
{{calendar_days}}
{{active_reporting_days}}
{{generated_at}}
{{page_number}}
{{total_pages}}
{{organization_name}}
{{team_name}}
{{emt_type}}
{{facility_name}}
{{facility_name_or_location}}
{{admin1}}
{{admin2}}
{{admin3}}
{{lat_long}}
{{source_file_count}}
```

## Core calculated placeholders

```text
{{total_consultations}}
{{daily_average_consultations}}
{{peak_day}}
{{peak_day_consultations}}
{{under5_count}}
{{age65plus_count}}
{{pregnant_count}}
{{trauma_total}}
{{infectious_total}}
{{additional_total}}
{{emergency_total}}
{{other_key_diseases_total}}
{{procedure_total}}
{{referral_rate}}
{{admission_rate}}
{{death_total}}
{{protection_trigger_total}}
```

## MDS item placeholders

For every MDS item from 4 to 50, support:

```text
{{mdsN_total}}
{{mdsN_under5}}
{{mdsN_5plus}}
{{mdsN_percentage}}
```

Example:

```text
{{mds9_total}}
{{mds9_under5}}
{{mds9_5plus}}
{{mds9_percentage}}
```

For MDS51–MDS65, support:

```text
{{mdsN_total}}
{{mdsN_dates}}
{{mdsN_latest_comment}}
```

Example:

```text
{{mds56_total}}
{{mds56_dates}}
{{mds56_latest_comment}}
```
