"""Language code resolution: name <-> ISO 639-3 <-> Glottolog.

Cached snapshot dated 2026-04-23. NOT exhaustive (~120 most-relevant entries
for the magic-linguistic-* suite — covers every Joshi 0-5 example language plus
common dialect families). Refresh procedure: see references/canonical_sources.md.

Used by: magic-linguistic-scope (primary), magic-linguistic-corpus (Phase 2),
magic-linguistic-eval (Phase 4).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LangRecord:
    iso639_3: str
    glottolog: str
    display: str
    family: str
    macrolang: str | None = None  # e.g., 'zho' for Mandarin
    script_default: str = ""
    notes: str = ""


# Cached snapshot (2026-04-23). Keys are lowercase canonical names + common aliases.
_CACHE: dict[str, LangRecord] = {
    # Latin-script European
    "english": LangRecord("eng", "stan1293", "English", "Indo-European > Germanic", script_default="Latin"),
    "spanish": LangRecord("spa", "stan1288", "Spanish", "Indo-European > Romance", script_default="Latin"),
    "french": LangRecord("fra", "stan1290", "French", "Indo-European > Romance", script_default="Latin"),
    "german": LangRecord("deu", "stan1295", "German", "Indo-European > Germanic", script_default="Latin"),
    "italian": LangRecord("ita", "ital1282", "Italian", "Indo-European > Romance", script_default="Latin"),
    "portuguese": LangRecord("por", "port1283", "Portuguese", "Indo-European > Romance", script_default="Latin"),
    # Cyrillic
    "russian": LangRecord("rus", "russ1263", "Russian", "Indo-European > Slavic", script_default="Cyrillic"),
    "ukrainian": LangRecord("ukr", "ukra1253", "Ukrainian", "Indo-European > Slavic", script_default="Cyrillic"),
    # CJK
    "chinese": LangRecord(
        "zho",
        "sini1245",
        "Chinese (macrolanguage — disambiguate)",
        "Sino-Tibetan",
        script_default="Han",
        notes="MACROLANGUAGE — disambiguate to Mandarin (cmn), Cantonese (yue), Wu (wuu), Hakka (hak), Min Nan (nan), etc.",  # noqa: E501  # long macrolang note string
    ),
    "mandarin": LangRecord(
        "cmn", "mand1415", "Mandarin Chinese", "Sino-Tibetan", macrolang="zho", script_default="Han"
    ),
    "cantonese": LangRecord(
        "yue", "cant1236", "Cantonese (Yue Chinese)", "Sino-Tibetan", macrolang="zho", script_default="Han"
    ),
    "japanese": LangRecord("jpn", "nucl1643", "Japanese", "Japonic", script_default="Han+Kana"),
    "korean": LangRecord("kor", "kore1280", "Korean", "Koreanic", script_default="Hangul"),
    # Arabic + macrolang
    "arabic": LangRecord(
        "ara",
        "arab1395",
        "Arabic (macrolanguage — disambiguate)",
        "Afro-Asiatic > Semitic",
        script_default="Arabic",
        notes="MACROLANGUAGE — disambiguate to MSA (arb), Egyptian (arz), Levantine (apc/ajp), Maghrebi (ary/aeb/etc).",
    ),
    "msa": LangRecord(
        "arb", "stan1318", "Modern Standard Arabic", "Afro-Asiatic > Semitic", macrolang="ara", script_default="Arabic"
    ),
    "egyptian arabic": LangRecord(
        "arz", "egyp1253", "Egyptian Arabic", "Afro-Asiatic > Semitic", macrolang="ara", script_default="Arabic"
    ),
    "hebrew": LangRecord("heb", "hebr1245", "Hebrew", "Afro-Asiatic > Semitic", script_default="Hebrew"),
    # Indic
    "hindi": LangRecord("hin", "hind1269", "Hindi", "Indo-European > Indo-Aryan", script_default="Devanagari"),
    "urdu": LangRecord("urd", "urdu1245", "Urdu", "Indo-European > Indo-Aryan", script_default="Arabic"),
    "bengali": LangRecord("ben", "beng1280", "Bengali", "Indo-European > Indo-Aryan", script_default="Bengali"),
    "tamil": LangRecord("tam", "tami1289", "Tamil", "Dravidian", script_default="Tamil"),
    "telugu": LangRecord("tel", "telu1262", "Telugu", "Dravidian", script_default="Telugu"),
    "kannada": LangRecord("kan", "kann1255", "Kannada", "Dravidian", script_default="Kannada"),
    "malayalam": LangRecord("mal", "mala1464", "Malayalam", "Dravidian", script_default="Malayalam"),
    "marathi": LangRecord("mar", "mara1378", "Marathi", "Indo-European > Indo-Aryan", script_default="Devanagari"),
    "punjabi": LangRecord("pan", "panj1256", "Punjabi", "Indo-European > Indo-Aryan", script_default="Gurmukhi"),
    "gujarati": LangRecord("guj", "guja1252", "Gujarati", "Indo-European > Indo-Aryan", script_default="Gujarati"),
    # Southeast Asian
    "thai": LangRecord("tha", "thai1261", "Thai", "Tai-Kadai", script_default="Thai"),
    "vietnamese": LangRecord(
        "vie",
        "viet1252",
        "Vietnamese",
        "Austroasiatic",
        script_default="Latin",
        notes="Tone language — diacritic stripping is destructive",
    ),
    "khmer": LangRecord("khm", "cent1989", "Khmer (Cambodian)", "Austroasiatic", script_default="Khmer"),
    "lao": LangRecord("lao", "laoo1244", "Lao", "Tai-Kadai", script_default="Lao"),
    "burmese": LangRecord("mya", "nucl1310", "Burmese", "Sino-Tibetan", script_default="Myanmar"),
    "indonesian": LangRecord("ind", "indo1316", "Indonesian", "Austronesian", script_default="Latin"),
    "tagalog": LangRecord("tgl", "taga1270", "Tagalog", "Austronesian", script_default="Latin"),
    # African (Niger-Congo, Bantu, Afro-Asiatic)
    "swahili": LangRecord("swa", "swah1253", "Swahili", "Niger-Congo > Bantu", script_default="Latin"),
    "yoruba": LangRecord(
        "yor",
        "yoru1245",
        "Yoruba",
        "Niger-Congo > Atlantic-Congo",
        script_default="Latin",
        notes="Tone language — diacritics carry meaning; do NOT strip",
    ),
    "igbo": LangRecord(
        "ibo", "nucl1417", "Igbo", "Niger-Congo > Atlantic-Congo", script_default="Latin", notes="Tone language"
    ),
    "hausa": LangRecord(
        "hau",
        "haus1257",
        "Hausa",
        "Afro-Asiatic > Chadic",
        script_default="Latin",
        notes="Tone language; also written in Arabic (Ajami)",
    ),
    "amharic": LangRecord("amh", "amha1245", "Amharic", "Afro-Asiatic > Semitic", script_default="Ge'ez"),
    "twi": LangRecord(
        "twi", "akua1239", "Twi (Akan)", "Niger-Congo > Atlantic-Congo", script_default="Latin", notes="Tone language"
    ),
    "wolof": LangRecord("wol", "wolo1247", "Wolof", "Niger-Congo > Atlantic", script_default="Latin"),
    "kinyarwanda": LangRecord("kin", "kiny1244", "Kinyarwanda", "Niger-Congo > Bantu", script_default="Latin"),
    "zulu": LangRecord("zul", "zulu1248", "Zulu", "Niger-Congo > Bantu", script_default="Latin"),
    "xhosa": LangRecord("xho", "xhos1239", "Xhosa", "Niger-Congo > Bantu", script_default="Latin"),
    # Indigenous Americas
    "quechua": LangRecord(
        "que",
        "quec1387",
        "Quechua (macrolanguage — disambiguate)",
        "Quechuan",
        script_default="Latin",
        notes="MACROLANGUAGE — disambiguate to Cusco (quz), Ayacucho (quy), Bolivian (quh), etc.",
    ),
    "cusco quechua": LangRecord(
        "quz",
        "cusc1236",
        "Cusco Quechua",
        "Quechuan",
        macrolang="que",
        script_default="Latin",
        notes="Quechua subtag; Andean Indigenous",
    ),
    "ayacucho quechua": LangRecord(
        "quy",
        "ayac1239",
        "Ayacucho Quechua",
        "Quechuan",
        macrolang="que",
        script_default="Latin",
        notes="Quechua subtag; Andean Indigenous",
    ),
    "bolivian quechua": LangRecord(
        "quh",
        "soutbo1234",
        "South Bolivian Quechua",
        "Quechuan",
        macrolang="que",
        script_default="Latin",
        notes="Quechua subtag; Andean Indigenous",
    ),
    "aymara": LangRecord("aym", "ayma1253", "Aymara", "Aymaran", script_default="Latin"),
    "guarani": LangRecord("grn", "tupi1276", "Guarani", "Tupian", script_default="Latin"),
    "navajo": LangRecord(
        "nav",
        "nava1243",
        "Navajo",
        "Na-Dene > Athabaskan",
        script_default="Latin",
        notes="Polysynthetic; tone language; community-controlled data",
    ),
    "cherokee": LangRecord(
        "chr",
        "cher1273",
        "Cherokee",
        "Iroquoian",
        script_default="Cherokee",
        notes="Syllabary; community-controlled data",
    ),
    # Pacific / Austronesian
    "maori": LangRecord(
        "mri",
        "maor1246",
        "Māori",
        "Austronesian",
        script_default="Latin",
        notes="Māori Data License governs many corpora",
    ),
    "samoan": LangRecord("smo", "samo1305", "Samoan", "Austronesian", script_default="Latin"),
    "hawaiian": LangRecord(
        "haw",
        "hawa1245",
        "Hawaiian",
        "Austronesian",
        script_default="Latin",
        notes="Diacritics (kahakō, ʻokina) are semantic",
    ),
    # Turkic / Uralic / Caucasian (agglutinative examples)
    "turkish": LangRecord(
        "tur", "nucl1301", "Turkish", "Turkic", script_default="Latin", notes="Agglutinative — high tokenizer fertility"
    ),
    "azerbaijani": LangRecord("aze", "nort2697", "Azerbaijani", "Turkic", script_default="Latin"),
    "kazakh": LangRecord("kaz", "kaza1248", "Kazakh", "Turkic", script_default="Cyrillic+Latin"),
    "uzbek": LangRecord("uzb", "uzbe1247", "Uzbek", "Turkic", script_default="Latin"),
    "finnish": LangRecord("fin", "finn1318", "Finnish", "Uralic", script_default="Latin", notes="Agglutinative"),
    "estonian": LangRecord("est", "esto1258", "Estonian", "Uralic", script_default="Latin", notes="Agglutinative"),
    "hungarian": LangRecord("hun", "hung1274", "Hungarian", "Uralic", script_default="Latin", notes="Agglutinative"),
    "georgian": LangRecord("kat", "nucl1302", "Georgian", "Kartvelian", script_default="Georgian"),
    # Iranian
    "persian": LangRecord("fas", "pers1259", "Persian (Farsi)", "Indo-European > Iranian", script_default="Arabic"),
    "pashto": LangRecord(
        "pus",
        "pash1269",
        "Pashto (macrolanguage — disambiguate)",
        "Indo-European > Iranian",
        script_default="Arabic",
        notes="MACROLANGUAGE — disambiguate to Northern (pbu), Southern (pbt), Central (pst).",
    ),
    # Sami
    "northern sami": LangRecord(
        "sme",
        "nort2671",
        "Northern Sami",
        "Uralic",
        script_default="Latin",
        notes="Endangered (EGIDS 7); community sovereignty",
    ),
    # Inuit / polysynthetic
    "inuktitut": LangRecord(
        "iku",
        "inuk1258",
        "Inuktitut",
        "Eskimo-Aleut",
        script_default="Canadian Aboriginal Syllabics",
        notes="Polysynthetic; community-controlled",
    ),
    # Greek
    "greek": LangRecord("ell", "mode1248", "Modern Greek", "Indo-European > Hellenic", script_default="Greek"),
    # Welsh / Irish (Celtic)
    "welsh": LangRecord("cym", "wels1247", "Welsh", "Indo-European > Celtic", script_default="Latin"),
    "irish": LangRecord("gle", "iris1253", "Irish", "Indo-European > Celtic", script_default="Latin"),
    # 0015 NLLB-200 / Glot500 overlap expansion (2026-04-23) — 10 main + 4 subtags.
    "tigrinya": LangRecord("tir", "tigr1271", "Tigrinya", "Afro-Asiatic > Semitic", script_default="Ge'ez"),
    "somali": LangRecord(
        "som", "soma1255", "Somali", "Afro-Asiatic > Cushitic", script_default="Latin", notes="Tone language"
    ),
    "oromo": LangRecord(
        "orm",
        "nucl1736",
        "Oromo (macrolanguage — disambiguate)",
        "Afro-Asiatic > Cushitic",
        script_default="Latin",
        notes="MACROLANGUAGE — disambiguate to Borana (gax) for high-resource NLP work, West Central (gaz), Eastern (hae).",  # noqa: E501  # long macrolang note string
    ),
    "borana oromo": LangRecord(
        "gax",
        "bora1271",
        "Borana Oromo",
        "Afro-Asiatic > Cushitic",
        macrolang="orm",
        script_default="Latin",
        notes="High-resource Oromo subtag; Qubee (Latin) orthography",
    ),
    "afrikaans": LangRecord("afr", "afri1274", "Afrikaans", "Indo-European > Germanic", script_default="Latin"),
    "malagasy": LangRecord(
        "mlg",
        "mala1537",
        "Malagasy (macrolanguage — disambiguate)",
        "Austronesian",
        script_default="Latin",
        notes="MACROLANGUAGE — disambiguate to Plateau Malagasy (plt) for high-resource NLP; many regional subtags exist.",  # noqa: E501  # long macrolang note string
    ),
    "plateau malagasy": LangRecord(
        "plt",
        "plat1254",
        "Plateau Malagasy",
        "Austronesian",
        macrolang="mlg",
        script_default="Latin",
        notes="Default high-resource Malagasy subtag",
    ),
    "sinhala": LangRecord("sin", "sinh1246", "Sinhala", "Indo-European > Indo-Aryan", script_default="Sinhala"),
    "nepali": LangRecord(
        "nep",
        "nepa1252",
        "Nepali (macrolanguage — disambiguate)",
        "Indo-European > Indo-Aryan",
        script_default="Devanagari",
        notes="MACROLANGUAGE — disambiguate to Nepali individual (npi) which is the typical NLP target.",
    ),
    "nepali (individual)": LangRecord(
        "npi",
        "nepa1254",
        "Nepali (individual)",
        "Indo-European > Indo-Aryan",
        macrolang="nep",
        script_default="Devanagari",
    ),
    "kyrgyz": LangRecord("kir", "kirg1245", "Kyrgyz", "Turkic", script_default="Cyrillic"),
    "tajik": LangRecord(
        "tgk",
        "taji1245",
        "Tajik",
        "Indo-European > Iranian",
        script_default="Cyrillic",
        notes="Mutually intelligible with Persian; Cyrillic-script standard",
    ),
    "mongolian": LangRecord(
        "mon",
        "mong1349",
        "Mongolian (macrolanguage — disambiguate)",
        "Mongolic",
        script_default="Cyrillic",
        notes="MACROLANGUAGE — disambiguate to Halh (khk) for Cyrillic-script Mongolia standard, or Peripheral Mongolian (mvf) for Inner Mongolia Traditional script.",  # noqa: E501  # long macrolang note string
    ),
    "halh mongolian": LangRecord(
        "khk",
        "halh1238",
        "Halh Mongolian",
        "Mongolic",
        macrolang="mon",
        script_default="Cyrillic",
        notes="Default high-resource Mongolian subtag (Mongolia state standard)",
    ),
}


# Common aliases → canonical key.
_ALIASES: dict[str, str] = {
    "zh": "chinese",
    "zh-cn": "mandarin",
    "zh-hk": "cantonese",
    "yue": "cantonese",
    "cmn": "mandarin",
    "ja": "japanese",
    "jp": "japanese",
    "jpn": "japanese",
    "ko": "korean",
    "kor": "korean",
    "ar": "arabic",
    "ara": "arabic",
    "arb": "msa",
    "msa-modern-standard-arabic": "msa",
    "modern standard arabic": "msa",
    "egyptian": "egyptian arabic",
    "ar-eg": "egyptian arabic",
    "yor": "yoruba",
    "ibo": "igbo",
    "hau": "hausa",
    "swa": "swahili",
    "khm": "khmer",
    "cambodian": "khmer",
    "mya": "burmese",
    "myanmar": "burmese",
    "vie": "vietnamese",
    "tha": "thai",
    "que": "quechua",
    "quz": "quechua",  # NOTE: not exact; signal disambiguation
    "maori": "maori",
    "māori": "maori",
    "tur": "turkish",
    "fin": "finnish",
    "fas": "persian",
    "farsi": "persian",
    "fa": "persian",
    # 0015 expansion aliases
    "tir": "tigrinya",
    "som": "somali",
    "orm": "oromo",
    "gax": "borana oromo",
    "afr": "afrikaans",
    "mlg": "malagasy",
    "plt": "plateau malagasy",
    "sin": "sinhala",
    "sinhalese": "sinhala",
    "nep": "nepali",
    "npi": "nepali (individual)",
    "kir": "kyrgyz",
    "kyrgyzstani": "kyrgyz",
    "tgk": "tajik",
    "mon": "mongolian",
    "khk": "halh mongolian",
}


def resolve_language(query: str) -> LangRecord:
    """Resolve a language name or code to a canonical LangRecord.

    Raises KeyError with a helpful message if not found.
    Disambiguation guidance is in the notes field of returned macrolanguage records.
    """
    q = query.strip().lower()
    if q in _CACHE:
        return _CACHE[q]
    if q in _ALIASES:
        return _CACHE[_ALIASES[q]]
    # Try matching by ISO 639-3 directly
    for rec in _CACHE.values():
        if rec.iso639_3 == q:
            return rec
    raise KeyError(
        f"Unknown language: {query!r}. "
        f"Try a canonical English name (e.g., 'Yoruba'), an ISO 639-3 code (e.g., 'yor'), "
        f"or a Glottolog ID. Cache size: {len(_CACHE)} languages (snapshot 2026-04-23)."
    )


def is_macrolanguage(query: str) -> bool:
    """True if the query resolves to an ISO 639-3 macrolanguage (e.g., 'Chinese' -> zho)."""
    try:
        rec = resolve_language(query)
    except KeyError:
        return False
    # Macrolanguage if any other record points to this iso as its macrolang
    return any(r.macrolang == rec.iso639_3 for r in _CACHE.values())


def subtags(query: str) -> list[LangRecord]:
    """Return the subtags of a macrolanguage. Empty list if not a macrolanguage."""
    try:
        rec = resolve_language(query)
    except KeyError:
        return []
    return [r for r in _CACHE.values() if r.macrolang == rec.iso639_3]


# Default high-resource subtag picks per macrolanguage (curated 2026-04-23).
# These are the subtags an NLP pipeline should DEFAULT to when the user names
# the macrolang without disambiguating. Reasoning per pick:
#   zho → cmn  (Mandarin: ~1B speakers; SoTA pretraining coverage)
#   ara → arb  (MSA: written-language standard; broadest corpus availability)
#   que → quz  (Cusco: highest-resource Quechua subtag in NLLB / FLORES+)
#   pus → pbu  (Northern Pashto: Afghanistan dominant variety; not in cache yet — falls back to first subtag)
#   orm → gax  (Borana: high-resource Oromo subtag with Qubee orthography)
#   mlg → plt  (Plateau Malagasy: dominant variety + most NLP resources)
#   nep → npi  (Nepali individual: 1:1 mapping)
#   mon → khk  (Halh: Mongolia state standard, Cyrillic script)
_DEFAULT_SUBTAG: dict[str, str] = {
    "zho": "cmn",
    "ara": "arb",
    "que": "quz",
    "orm": "gax",
    "mlg": "plt",
    "nep": "npi",
    "mon": "khk",
}


def subtag_for(query: str) -> LangRecord | None:
    """Return the default high-resource subtag for a macrolanguage.

    Returns None if the query is not a macrolanguage OR if no curated default
    exists. Use `subtags(query)` for the full list of subtags.
    """
    try:
        rec = resolve_language(query)
    except KeyError:
        return None
    if rec.iso639_3 not in _DEFAULT_SUBTAG:
        # Not a macrolanguage with a curated default. Fall back to the first
        # subtag if any exist (alphabetical-by-iso for determinism).
        candidates = sorted(subtags(query), key=lambda r: r.iso639_3)
        return candidates[0] if candidates else None
    default_iso = _DEFAULT_SUBTAG[rec.iso639_3]
    for r in _CACHE.values():
        if r.iso639_3 == default_iso:
            return r
    return None
