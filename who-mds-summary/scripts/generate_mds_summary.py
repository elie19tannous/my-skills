#!/usr/bin/env python3
"""Generate a multi-day WHO EMT MDS summary Markdown file from daily CSV exports."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

NO_DATA = "No data available for the selected reporting period."
FIELD_MISSING = "Field not available in source data."


MDS_LABELS = {
    4: ("Trauma", "Major head / spine injury"),
    5: ("Trauma", "Major torso injury"),
    6: ("Trauma", "Major extremity injury"),
    7: ("Trauma", "Moderate injury"),
    8: ("Trauma", "Minor injury"),
    9: ("Infectious disease", "Acute respiratory infection"),
    10: ("Infectious disease", "Acute watery diarrhea"),
    11: ("Infectious disease", "Acute bloody diarrhea"),
    12: ("Infectious disease", "Acute jaundice syndrome"),
    13: ("Infectious disease", "Suspected measles"),
    14: ("Infectious disease", "Suspected meningitis"),
    15: ("Infectious disease", "Suspected tetanus"),
    16: ("Infectious disease", "Acute flaccid paralysis"),
    17: ("Infectious disease", "Tuberculous Bronchitis, suspected/confirmed"),
    18: ("Infectious disease", "Fever of unknown origin"),
    19: ("Additional diseases", "COVID-19, suspected/confirmed"),
    20: ("Additional diseases", "Hypertension"),
    21: ("Additional diseases", "Diabetes mellitus"),
    22: ("Additional diseases", "Musculoskeletal conditions"),
    23: ("Emergencies", "Surgical emergency, non-trauma"),
    24: ("Emergencies", "Medical emergency, non-infectious"),
    25: ("Other key diseases", "Skin disease"),
    26: ("Other key diseases", "Acute mental health problem"),
    27: ("Other key diseases", "Obstetric complications"),
    28: ("Other key diseases", "Severe Acute Malnutrition"),
    29: ("Other key diseases", "Other diagnosis, not specified above"),
    30: ("Procedure", "Major procedure excluding MDS31"),
    31: ("Procedure", "Limb amputation excluding digits"),
    32: ("Procedure", "Minor surgical procedure"),
    33: ("Procedure", "Normal Vaginal Delivery"),
    34: ("Procedure", "Caesarean section"),
    35: ("Procedure", "Obstetrics others"),
    36: ("Outcome", "Discharge without medical follow-up"),
    37: ("Outcome", "Discharge with medical follow-up"),
    38: ("Outcome", "Discharge against medical advice"),
    39: ("Outcome", "Referral"),
    40: ("Outcome", "Admission"),
    41: ("Outcome", "Dead on arrival"),
    42: ("Outcome", "Death within facility"),
    43: ("Outcome", "Requiring long-term rehabilitation"),
    44: ("Relation", "Directly related to event"),
    45: ("Relation", "Indirectly related to event"),
    46: ("Relation", "Not related to event"),
    47: ("Protection", "Vulnerable child"),
    48: ("Protection", "Vulnerable adult"),
    49: ("Protection", "Sexual Gender Based Violence"),
    50: ("Protection", "Violence non-SGBV"),
    51: ("Immediate report", "Unexpected death"),
    52: ("Immediate report", "Notifiable disease"),
    53: ("Immediate report", "Protection issues"),
    54: ("Immediate report", "Critical incident to EMT and/or community"),
    55: ("Immediate report", "Any other issue requiring immediate reporting"),
    56: ("Community risk", "WASH"),
    57: ("Community risk", "Community / suspected over infectious disease"),
    58: ("Community risk", "Environmental risk / exposure"),
    59: ("Community risk", "Shelter / Non-food items"),
    60: ("Community risk", "Food insecurity"),
    61: ("Operational constraint", "Logistics / operational support"),
    62: ("Operational constraint", "Supply"),
    63: ("Operational constraint", "Human resources"),
    64: ("Operational constraint", "Finance"),
    65: ("Operational constraint", "Others"),
}

HEALTH_GROUPS = {
    "Trauma": range(4, 9),
    "Infectious disease": range(9, 19),
    "Additional diseases": range(19, 23),
    "Emergencies": range(23, 25),
    "Other key diseases": range(25, 30),
}
RESTRICTED_ITEMS = {28, 31, 42, 43, 47, 48, 49, 50}
TRUE_VALUES = {"1", "true", "yes", "y", "x", "checked"}


@dataclass
class SourceFile:
    path: Path
    rows_loaded: int
    rows_included: int
    detected_start: str
    detected_end: str
    tool_version: str
    form_version: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a WHO EMT MDS summary Markdown file.")
    parser.add_argument("inputs", nargs="+", help="CSV files or directories containing CSV files.")
    parser.add_argument("--start-date", help="Inclusive report start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", help="Inclusive report end date, YYYY-MM-DD.")
    parser.add_argument("--organization", help="Organization name override.")
    parser.add_argument("--team-name", help="Team name override.")
    parser.add_argument("--emt-type", default=FIELD_MISSING, help="EMT type or capability package.")
    parser.add_argument("--output", default="who-emt-mds-summary.md", help="Generated summary Markdown path.")
    return parser.parse_args()


def collect_csv_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*.csv")))
        elif path.is_file():
            paths.append(path)
    if not paths:
        raise SystemExit("error: no CSV files found")
    return paths


def read_csv(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "latin-1"):
        try:
            with path.open(newline="", encoding=encoding) as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"error: could not decode {path}")


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y", "%d.%m.%y", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def date_range(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def is_selected(value: Any) -> bool:
    return str(value or "").strip().lower() in TRUE_VALUES


def first_present(rows: list[dict[str, str]], field: str) -> str:
    values = sorted({str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip()})
    if not values:
        return FIELD_MISSING
    if len(values) == 1:
        return values[0]
    return "Multiple"


def pct(count: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{(count / denominator) * 100:.1f}%"


def num_rate(count: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{(count / denominator) * 100:.1f}%"


def age_group(row: dict[str, str]) -> str | None:
    mds_age = str(row.get("MDSa", "")).strip()
    mapping = {"1": "<1", "2": "1-4", "3": "5-17", "4": "18-64", "5": "65+"}
    if mds_age in mapping:
        return mapping[mds_age]
    try:
        age = float(str(row.get("Age", "")).strip())
    except ValueError:
        return None
    unit = str(row.get("M/Y", "Y")).strip().upper()
    years = age / 12 if unit == "M" else age
    if years < 1:
        return "<1"
    if years < 5:
        return "1-4"
    if years < 18:
        return "5-17"
    if years < 65:
        return "18-64"
    return "65+"


def sex_category(row: dict[str, str]) -> str | None:
    value = str(row.get("MDS1-3", "")).strip()
    return {"1": "Male", "2": "Female non-pregnant", "3": "Female pregnant"}.get(value)


def selected_mds(row: dict[str, str], item: int) -> bool:
    return is_selected(row.get(f"MDS{item}"))


def get_dates(rows: list[dict[str, str]]) -> list[date]:
    return [d for d in (parse_date(row.get("h")) for row in rows) if d]


def load_data(paths: list[Path], start: date | None, end: date | None) -> tuple[list[dict[str, str]], list[SourceFile], date, date]:
    all_rows: list[dict[str, str]] = []
    sources: list[SourceFile] = []
    for path in paths:
        rows = read_csv(path)
        dates = get_dates(rows)
        included = []
        for row in rows:
            row["_source_file"] = path.name
            row["_date"] = parse_date(row.get("h")).isoformat() if parse_date(row.get("h")) else ""
            row["_facility"] = str(row.get("m", "")).strip() or FIELD_MISSING
            included.append(row)
        all_rows.extend(included)
        sources.append(
            SourceFile(
                path=path,
                rows_loaded=len(rows),
                rows_included=len(included),
                detected_start=min(dates).isoformat() if dates else FIELD_MISSING,
                detected_end=max(dates).isoformat() if dates else FIELD_MISSING,
                tool_version=first_present(rows, "ToolVer"),
                form_version=first_present(rows, "Ver"),
            )
        )
    all_dates = get_dates(all_rows)
    if not all_dates and (not start or not end):
        raise SystemExit("error: no activity dates found; pass --start-date and --end-date")
    report_start = start or min(all_dates)
    report_end = end or max(all_dates)
    included_rows = [row for row in all_rows if row.get("_date") and report_start <= parse_date(row.get("_date")) <= report_end]
    return included_rows, sources, report_start, report_end


def count_mds(rows: list[dict[str, str]], item: int) -> int:
    return sum(1 for row in rows if selected_mds(row, item))


def unique_or_multiple(values: list[str]) -> str:
    cleaned = sorted({v for v in values if v and v != FIELD_MISSING})
    if not cleaned:
        return FIELD_MISSING
    if len(cleaned) == 1:
        return cleaned[0]
    return "Multiple"


def make_rows_by_day(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    by_day: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_day[row.get("_date", "")].append(row)
    return by_day


def build_context(rows: list[dict[str, str]], sources: list[SourceFile], start: date, end: date, args: argparse.Namespace) -> dict[str, Any]:
    total = len(rows)
    by_day = make_rows_by_day(rows)
    all_days = date_range(start, end)
    active_days = [day for day in all_days if by_day.get(day.isoformat())]
    day_counts = {day.isoformat(): len(by_day.get(day.isoformat(), [])) for day in all_days}
    peak_day = max(day_counts, key=day_counts.get) if day_counts else FIELD_MISSING
    org = args.organization or first_present(rows, "a")
    team = args.team_name or first_present(rows, "b")
    facility = unique_or_multiple([row.get("_facility", "") for row in rows])
    admin1 = unique_or_multiple([str(row.get("j", "")).strip() for row in rows])
    admin2 = unique_or_multiple([str(row.get("k", "")).strip() for row in rows])
    admin3 = unique_or_multiple([str(row.get("l", "")).strip() for row in rows])

    ctx: dict[str, Any] = {
        "report_title": "WHO EMT MDS Periodic Report",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "calendar_days": len(all_days),
        "active_reporting_days": len(active_days),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "organization_name": org,
        "team_name": team,
        "emt_type": args.emt_type,
        "facility_name": facility,
        "facility_name_or_location": facility if facility != "Multiple" else "Multiple facilities",
        "admin1": admin1,
        "admin2": admin2,
        "admin3": admin3,
        "lat_long": unique_or_multiple([str(row.get("n", "")).strip() for row in rows]),
        "source_file_count": len(sources),
        "total_consultations": total,
        "daily_average_consultations": f"{(total / max(len(active_days), 1)):.1f}",
        "peak_day": peak_day,
        "peak_day_consultations": day_counts.get(peak_day, 0),
        "included_record_count": total,
        "records_included": total,
        "records_loaded": sum(source.rows_loaded for source in sources),
        "records_excluded": 0,
        "excluded_record_count": 0,
        "facility_count": len({row.get("_facility") for row in rows if row.get("_facility")}),
        "missing_days_count": len([day for day in all_days if not by_day.get(day.isoformat())]),
        "page_number": "",
        "total_pages": "",
    }

    age_groups = Counter(age_group(row) or "Missing / unknown" for row in rows)
    sexes = Counter(sex_category(row) or "Missing / unknown" for row in rows)
    ctx.update(build_demographics(rows, age_groups, sexes, total))
    ctx.update(build_mds_totals(rows, total))
    ctx.update(build_report_rows(rows, sources, all_days, by_day, total))
    ctx.update(build_quality(rows, total))
    ctx.update(build_findings(ctx))
    ctx.update(build_assumptions())
    return ctx


def build_demographics(rows: list[dict[str, str]], age_groups: Counter[str], sexes: Counter[str], total: int) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "under1_total": age_groups["<1"],
        "age_1_4_total": age_groups["1-4"],
        "age_5_17_total": age_groups["5-17"],
        "age_18_64_total": age_groups["18-64"],
        "age_65plus_total": age_groups["65+"],
        "age_unknown_total": age_groups["Missing / unknown"],
        "under5_count": age_groups["<1"] + age_groups["1-4"],
        "age65plus_count": age_groups["65+"],
        "missing_age_count": age_groups["Missing / unknown"],
        "male_total": sexes["Male"],
        "female_non_preg_total": sexes["Female non-pregnant"],
        "female_preg_total": sexes["Female pregnant"],
        "pregnant_count": sexes["Female pregnant"],
        "sex_unknown_total": sexes["Missing / unknown"],
        "missing_sex_count": sexes["Missing / unknown"],
        "valid_age_sex_count": sum(1 for row in rows if age_group(row) and sex_category(row)),
        "demographic_total": total,
        "invalid_age_group_count": 0,
        "conflicting_age_count": 0,
    }
    for key in ("under1", "age_1_4", "age_5_17", "age_18_64", "age_65plus", "age_unknown", "male", "female_non_preg", "female_preg", "sex_unknown", "under5"):
        total_key = f"{key}_total" if key != "under5" else "under5_count"
        ctx[f"{key}_percentage"] = pct(int(ctx.get(total_key, 0)), total)
    matrix_keys = [
        ("male", "Male"),
        ("female_non_preg", "Female non-pregnant"),
        ("female_preg", "Female pregnant"),
    ]
    age_key_map = {"<1": "under1", "1-4": "1_4", "5-17": "5_17", "18-64": "18_64", "65+": "65plus"}
    for prefix, sex in matrix_keys:
        for label, key in age_key_map.items():
            ctx[f"{prefix}_{key}"] = sum(1 for row in rows if sex_category(row) == sex and age_group(row) == label)
    return ctx


def build_mds_totals(rows: list[dict[str, str]], total: int) -> dict[str, Any]:
    ctx: dict[str, Any] = {}
    for item in range(4, 66):
        item_total = count_mds(rows, item)
        ctx[f"mds{item}_total"] = item_total
        ctx[f"mds{item}_percentage"] = pct(item_total, total)
        if 4 <= item <= 35:
            under5 = sum(1 for row in rows if selected_mds(row, item) and age_group(row) in {"<1", "1-4"})
            ctx[f"mds{item}_under5"] = under5
            ctx[f"mds{item}_5plus"] = item_total - under5
        if 51 <= item <= 65:
            dates = sorted({row.get("_date", "") for row in rows if selected_mds(row, item) and row.get("_date")})
            ctx[f"mds{item}_dates"] = ", ".join(dates) if dates else NO_DATA
            ctx[f"mds{item}_latest_comment"] = FIELD_MISSING
    for group, items in HEALTH_GROUPS.items():
        key = group.lower().replace(" ", "_")
        group_total = sum(int(ctx[f"mds{item}_total"]) for item in items)
        ctx[f"{key}_total"] = group_total
        ctx[f"{key}_percentage"] = pct(group_total, total)
    ctx["infectious_total"] = ctx["infectious_disease_total"]
    ctx["infectious_percentage"] = ctx["infectious_disease_percentage"]
    ctx["additional_total"] = ctx["additional_diseases_total"]
    ctx["additional_percentage"] = ctx["additional_diseases_percentage"]
    ctx["emergency_total"] = ctx["emergencies_total"]
    ctx["emergency_percentage"] = ctx["emergencies_percentage"]
    ctx["procedure_total"] = sum(int(ctx[f"mds{item}_total"]) for item in range(30, 36))
    ctx["death_total"] = int(ctx["mds41_total"]) + int(ctx["mds42_total"])
    ctx["protection_trigger_total"] = sum(int(ctx[f"mds{item}_total"]) for item in range(47, 51))
    ctx["referral_rate"] = num_rate(int(ctx["mds39_total"]), total)
    ctx["admission_rate"] = num_rate(int(ctx["mds40_total"]), total)
    ctx["procedure_rate"] = num_rate(int(ctx["procedure_total"]), total)
    return ctx


def build_report_rows(rows: list[dict[str, str]], sources: list[SourceFile], all_days: list[date], by_day: dict[str, list[dict[str, str]]], total: int) -> dict[str, Any]:
    daily_coverage_rows = []
    daily_consultation_rows = []
    daily_group_trend_rows = []
    daily_breakdown_rows = []
    for day in all_days:
        key = day.isoformat()
        day_rows = by_day.get(key, [])
        facilities = unique_or_multiple([row.get("_facility", "") for row in day_rows])
        source_names = unique_or_multiple([row.get("_source_file", "") for row in day_rows])
        daily_coverage_rows.append({
            "date": key,
            "status": "Reported" if day_rows else "Missing",
            "facility_name": facilities if day_rows else NO_DATA,
            "working_hours": unique_or_multiple([str(row.get("i", "")).strip() for row in day_rows]) if day_rows else NO_DATA,
            "consultation_count": len(day_rows),
            "source_file_name": source_names if day_rows else NO_DATA,
        })
        daily_consultation_rows.append({"date": key, "consultation_count": len(day_rows)})
        group_counts = {name: sum(count_mds(day_rows, item) for item in items) for name, items in HEALTH_GROUPS.items()}
        daily_group_trend_rows.append({
            "date": key,
            "trauma_count": group_counts["Trauma"],
            "infectious_count": group_counts["Infectious disease"],
            "additional_count": group_counts["Additional diseases"],
            "emergency_count": group_counts["Emergencies"],
            "other_key_diseases_count": group_counts["Other key diseases"],
        })
        daily_breakdown_rows.append({
            "date": key,
            "facility": facilities if day_rows else NO_DATA,
            "consultations": len(day_rows),
            "under5": sum(1 for row in day_rows if age_group(row) in {"<1", "1-4"}),
            "age65plus": sum(1 for row in day_rows if age_group(row) == "65+"),
            "trauma": group_counts["Trauma"],
            "infectious": group_counts["Infectious disease"],
            "procedures": sum(count_mds(day_rows, item) for item in range(30, 36)),
            "referrals": count_mds(day_rows, 39),
            "admissions": count_mds(day_rows, 40),
            "deaths": count_mds(day_rows, 41) + count_mds(day_rows, 42),
            "protection": sum(count_mds(day_rows, item) for item in range(47, 51)),
            "direct": count_mds(day_rows, 44),
            "indirect": count_mds(day_rows, 45),
            "not_related": count_mds(day_rows, 46),
        })

    mds_rows = []
    for item in range(4, 51):
        group, label = MDS_LABELS[item]
        item_total = count_mds(rows, item)
        mds_rows.append({
            "category": group,
            "mds_no": item,
            "mds_label": label,
            "count": item_total,
            "percentage": pct(item_total, total),
            "restricted_trigger": "Yes" if item in RESTRICTED_ITEMS else "No",
            f"mds{item}_total": item_total,
        })
    top_health = sorted((row for row in mds_rows if 4 <= int(row["mds_no"]) <= 29), key=lambda row: row["count"], reverse=True)[:10]
    top_health_event_rows = [{**row, "rank": index + 1} for index, row in enumerate(top_health)]
    top_event_trend_rows = [
        {
            "mds_no": row["mds_no"],
            "mds_label": row["mds_label"],
            "date": day.isoformat(),
            "count": count_mds(by_day.get(day.isoformat(), []), int(row["mds_no"])),
        }
        for row in top_health[:5]
        for day in all_days
    ]
    restricted_rows = []
    for row in rows:
        for item in RESTRICTED_ITEMS:
            if selected_mds(row, item):
                restricted_rows.append({
                    "record_id": row.get("ID", FIELD_MISSING),
                    "date": row.get("_date", FIELD_MISSING),
                    "facility": row.get("_facility", FIELD_MISSING),
                    "mds_no": item,
                    "trigger_item": MDS_LABELS[item][1],
                    "age_group": age_group(row) or FIELD_MISSING,
                    "sex_category": sex_category(row) or FIELD_MISSING,
                    "action_taken": FIELD_MISSING,
                    "followup_status": FIELD_MISSING,
                })
    facility_rows = []
    for facility in sorted({row.get("_facility", FIELD_MISSING) for row in rows}):
        subset = [row for row in rows if row.get("_facility", FIELD_MISSING) == facility]
        dates = sorted({row.get("_date", "") for row in subset if row.get("_date")})
        facility_rows.append({
            "facility_name": facility,
            "admin1": unique_or_multiple([str(row.get("j", "")).strip() for row in subset]),
            "admin2": unique_or_multiple([str(row.get("k", "")).strip() for row in subset]),
            "admin3": unique_or_multiple([str(row.get("l", "")).strip() for row in subset]),
            "lat_long": unique_or_multiple([str(row.get("n", "")).strip() for row in subset]),
            "first_date": dates[0] if dates else FIELD_MISSING,
            "last_date": dates[-1] if dates else FIELD_MISSING,
            "record_count": len(subset),
        })
    return {
        "daily_coverage_rows": daily_coverage_rows,
        "daily_consultation_rows": daily_consultation_rows,
        "daily_group_trend_rows": daily_group_trend_rows,
        "daily_breakdown_rows": daily_breakdown_rows,
        "facility_location_rows": facility_rows,
        "source_data_rows": [
            {
                "source_file_name": source.path.name,
                "loaded_count": source.rows_loaded,
                "included_count": source.rows_included,
                "detected_start": source.detected_start,
                "detected_end": source.detected_end,
                "tool_version": source.tool_version,
                "form_version": source.form_version,
            }
            for source in sources
        ],
        "top_health_event_rows": top_health_event_rows,
        "top_event_trend_rows": top_event_trend_rows,
        "restricted_record_rows": restricted_rows,
        "review_record_rows": [],
        "missing_excluded_rows": [
            {"issue": "Missing day", "details": day.isoformat(), "impact": "Day not included in period totals"}
            for day in all_days if not by_day.get(day.isoformat())
        ],
        "daily_note_rows": [],
        "detailed_comment_rows": [],
        "action_required_rows": [],
    }


def build_quality(rows: list[dict[str, str]], total: int) -> dict[str, Any]:
    ids = [row.get("ID", "") for row in rows if row.get("ID")]
    duplicate_ids = sum(count - 1 for count in Counter(ids).values() if count > 1)
    missing_required = sum(1 for row in rows for field in ("h", "ID") if not row.get(field))
    missing_age = sum(1 for row in rows if not age_group(row))
    missing_sex = sum(1 for row in rows if not sex_category(row))
    checkbox_warnings = sum(
        1
        for row in rows
        for item in range(4, 66)
        if str(row.get(f"MDS{item}", "")).strip() and not is_selected(row.get(f"MDS{item}")) and str(row.get(f"MDS{item}", "")).strip() != "0"
    )
    relation_multiple = sum(1 for row in rows if sum(1 for item in (44, 45, 46) if selected_mds(row, item)) > 1)
    relation_missing = sum(1 for row in rows if sum(1 for item in (44, 45, 46) if selected_mds(row, item)) == 0)
    restricted = sum(1 for row in rows for item in RESTRICTED_ITEMS if selected_mds(row, item))
    return {
        "duplicate_id_count": duplicate_ids,
        "missing_required_field_count": missing_required,
        "warning_record_count": len({row.get("ID", index) for index, row in enumerate(rows) if not age_group(row) or not sex_category(row)}),
        "error_record_count": missing_required,
        "date_check_result": "Pass" if all(row.get("_date") for row in rows) else "Review",
        "date_check_count": sum(1 for row in rows if not row.get("_date")),
        "duplicate_id_result": "Pass" if duplicate_ids == 0 else "Review",
        "age_check_result": "Pass" if missing_age == 0 else "Review",
        "age_check_count": missing_age,
        "sex_check_result": "Pass" if missing_sex == 0 else "Review",
        "sex_check_count": missing_sex,
        "checkbox_check_result": "Pass" if checkbox_warnings == 0 else "Review",
        "checkbox_check_count": checkbox_warnings,
        "outcome_check_result": "Informational",
        "outcome_check_count": sum(1 for row in rows if sum(1 for item in range(36, 44) if selected_mds(row, item)) == 0),
        "relation_check_result": "Pass" if relation_multiple == 0 else "Review",
        "relation_check_count": relation_multiple,
        "restricted_check_result": "Restricted trigger detected" if restricted else "Pass",
        "restricted_check_count": restricted,
        "missing_relation_total": relation_missing,
        "missing_relation_percentage": pct(relation_missing, total),
        "multiple_relation_total": relation_multiple,
        "multiple_relation_percentage": pct(relation_multiple, total),
        "needs_risks_available": "Available" if any(count_mds(rows, item) for item in range(51, 66)) else "No data available",
        "needs_risks_source": "MDS51-MDS65 fields",
        "needs_risks_date_range": FIELD_MISSING,
        "comments_available": "No",
    }


def build_findings(ctx: dict[str, Any]) -> dict[str, Any]:
    health_groups = [
        ("Trauma", int(ctx["trauma_total"])),
        ("Infectious disease", int(ctx["infectious_total"])),
        ("Additional diseases", int(ctx["additional_diseases_total"])),
        ("Emergencies", int(ctx["emergencies_total"])),
        ("Other key diseases", int(ctx["other_key_diseases_total"])),
    ]
    top_groups = sorted(health_groups, key=lambda item: item[1], reverse=True)[:3]
    findings = [
        {"text": f"{ctx['total_consultations']} consultations were included across {ctx['active_reporting_days']} active reporting day(s)."},
        {"text": f"The peak day was {ctx['peak_day']} with {ctx['peak_day_consultations']} consultation(s)."},
        {"text": "Top health event groups: " + ", ".join(f"{name} ({count})" for name, count in top_groups) + "."},
        {"text": f"Referrals: {ctx['mds39_total']}; admissions: {ctx['mds40_total']}; deaths: {ctx['death_total']}."},
    ]
    if int(ctx["protection_trigger_total"]) > 0:
        findings.append({"text": f"{ctx['protection_trigger_total']} protection-related aggregate trigger(s) were detected; details require a confidential pathway."})
    return {
        "main_findings": findings,
        "trend_interpretation_notes": findings[:3],
        "data_availability_note": f"{ctx['active_reporting_days']} of {ctx['calendar_days']} calendar day(s) have source data. Restricted trigger total: {ctx['restricted_check_count']}.",
        "daily_consultation_chart_svg_or_canvas": "Chart placeholder. Use daily consultation table for source values.",
        "top_event_1": ctx.get("top_health_event_rows", [{}])[0].get("mds_label", NO_DATA) if ctx.get("top_health_event_rows") else NO_DATA,
        "top_event_1_count": ctx.get("top_health_event_rows", [{}])[0].get("count", 0) if ctx.get("top_health_event_rows") else 0,
        "top_event_2": ctx.get("top_health_event_rows", [{}, {}])[1].get("mds_label", NO_DATA) if len(ctx.get("top_health_event_rows", [])) > 1 else NO_DATA,
        "top_event_2_count": ctx.get("top_health_event_rows", [{}, {}])[1].get("count", 0) if len(ctx.get("top_health_event_rows", [])) > 1 else 0,
        "top_event_3": ctx.get("top_health_event_rows", [{}, {}, {}])[2].get("mds_label", NO_DATA) if len(ctx.get("top_health_event_rows", [])) > 2 else NO_DATA,
        "top_event_3_count": ctx.get("top_health_event_rows", [{}, {}, {}])[2].get("count", 0) if len(ctx.get("top_health_event_rows", [])) > 2 else 0,
        "top_event_4": ctx.get("top_health_event_rows", [{}, {}, {}, {}])[3].get("mds_label", NO_DATA) if len(ctx.get("top_health_event_rows", [])) > 3 else NO_DATA,
        "top_event_4_count": ctx.get("top_health_event_rows", [{}, {}, {}, {}])[3].get("count", 0) if len(ctx.get("top_health_event_rows", [])) > 3 else 0,
        "top_event_5": ctx.get("top_health_event_rows", [{}, {}, {}, {}, {}])[4].get("mds_label", NO_DATA) if len(ctx.get("top_health_event_rows", [])) > 4 else NO_DATA,
        "top_event_5_count": ctx.get("top_health_event_rows", [{}, {}, {}, {}, {}])[4].get("count", 0) if len(ctx.get("top_health_event_rows", [])) > 4 else 0,
    }


def build_assumptions() -> dict[str, str]:
    return {
        "consultation_total_calculation_method": "Each included CSV row is counted as one consultation.",
        "age_group_derivation_method": "MDSa is used first; Age and M/Y are used as fallback.",
        "missing_age_or_sex_handling": "Missing values are counted in missing or unknown categories.",
        "multiple_mds_items_handling": "Multiple selected MDS items on one record are counted in each selected item.",
        "multiple_facilities_handling": "Multiple facilities are aggregated in totals and listed in coverage tables.",
        "unavailable_needs_risks_handling": "Unavailable needs and risks fields are marked as field not available.",
        "restricted_line_list_trigger_handling": "Restricted trigger details are excluded from the public report and may be rendered separately.",
        "outcome_notes": "",
        "followup_total": 0,
    }


SUMMARY_TABLES = {
    "Main Findings": "main_findings",
    "Trend Interpretation Notes": "trend_interpretation_notes",
    "Daily Coverage": "daily_coverage_rows",
    "Daily Consultations": "daily_consultation_rows",
    "Daily Group Trends": "daily_group_trend_rows",
    "Daily Breakdown": "daily_breakdown_rows",
    "Facility Locations": "facility_location_rows",
    "Source Data": "source_data_rows",
    "Top Health Events": "top_health_event_rows",
    "Top Event Trends": "top_event_trend_rows",
    "Missing Or Excluded Rows": "missing_excluded_rows",
    "Review Records": "review_record_rows",
    "Daily Notes": "daily_note_rows",
    "Detailed Comments": "detailed_comment_rows",
    "Actions Required": "action_required_rows",
    "Restricted Trigger Records": "restricted_record_rows",
}


def scalar_context(context: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in context.items() if not isinstance(value, list)}


def markdown_cell(value: Any) -> str:
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").strip()


def write_markdown_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        lines.append(NO_DATA)
        lines.append("")
        return
    fieldnames = sorted({key for row in rows for key in row})
    lines.append("| " + " | ".join(fieldnames) + " |")
    lines.append("| " + " | ".join("---" for _ in fieldnames) + " |")
    for row in rows:
        lines.append("| " + " | ".join(markdown_cell(row.get(key, "")) for key in fieldnames) + " |")
    lines.append("")


def write_key_value_table(lines: list[str], values: dict[str, Any]) -> None:
    lines.append("| Field | Value |")
    lines.append("| --- | --- |")
    for key in sorted(values):
        lines.append(f"| {markdown_cell(key)} | {markdown_cell(values[key])} |")
    lines.append("")


def build_markdown_summary(context: dict[str, Any]) -> str:
    metadata = scalar_context(context)
    assumption_values = {
        key: value
        for key, value in metadata.items()
        if key.endswith("_method") or key.endswith("_handling") or key == "outcome_notes"
    }
    lines = [
        "# WHO EMT MDS Summary",
        "",
        "> Generated summary data for final WHO EMT MDS report preparation. Treat the restricted trigger section as confidential when it contains rows.",
        "",
        "## Metadata",
        "",
    ]
    write_key_value_table(lines, metadata)
    lines.extend(["## Assumptions", ""])
    write_key_value_table(lines, assumption_values)
    for title, context_key in SUMMARY_TABLES.items():
        rows = context.get(context_key, [])
        lines.extend([f"## {title}", ""])
        if context_key == "restricted_record_rows":
            lines.append("> Confidential section. Do not include line-list trigger details in the public report.")
            lines.append("")
        write_markdown_table(lines, rows)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    start = parse_date(args.start_date) if args.start_date else None
    end = parse_date(args.end_date) if args.end_date else None
    if args.start_date and not start:
        raise SystemExit("error: --start-date must be YYYY-MM-DD")
    if args.end_date and not end:
        raise SystemExit("error: --end-date must be YYYY-MM-DD")
    paths = collect_csv_paths(args.inputs)
    rows, sources, report_start, report_end = load_data(paths, start, end)
    context = build_context(rows, sources, report_start, report_end, args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_markdown_summary(context), encoding="utf-8")
    print(f"Wrote WHO MDS summary Markdown: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
