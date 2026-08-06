#!/usr/bin/env python3
"""
Harvey Specterbot — Legal Research Engine
Queries CourtListener API and USPTO for case law, court opinions, and patent data.
Used by Harvey's Legal Researcher agent during PHASE 1 research.

Usage:
    python3 legal_research.py search "non-compete enforceability" --type opinions --jurisdiction cal --limit 10
    python3 legal_research.py case <cluster_id>
    python3 legal_research.py docket <docket_id>
    python3 legal_research.py citation "410 U.S. 113"
    python3 legal_research.py patent-search "machine learning medical device"
    python3 legal_research.py patent <patent_number>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from urllib.parse import urlencode, quote
from datetime import datetime

# Load API tokens from .env file or environment variables
# Searches: project .env, skill .env, then home .env
ENV_FILE = None
for candidate in [
    Path.cwd() / ".env",
    Path(__file__).parent.parent / ".env",
    Path.home() / ".env",
]:
    if candidate.exists():
        ENV_FILE = candidate
        break
TOKENS = {}

def load_tokens():
    """Load API tokens from .env file."""
    global TOKENS
    if ENV_FILE and ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                TOKENS[key.strip()] = val.strip()
    # Environment variables override .env
    for key in ["COURTLISTENER_API_TOKEN", "USPTO_OPEN_DATA_API_KEY"]:
        if os.environ.get(key):
            TOKENS[key] = os.environ[key]

load_tokens()

CL_TOKEN = TOKENS.get("COURTLISTENER_API_TOKEN", "")
USPTO_KEY = TOKENS.get("USPTO_OPEN_DATA_API_KEY", "")
CL_BASE = "https://www.courtlistener.com/api/rest/v4"


def cl_headers():
    return {"Authorization": f"Token {CL_TOKEN}"}


def fetch_json(url, headers=None):
    """Fetch JSON from URL using urllib (no requests dependency)."""
    import urllib.request
    import urllib.error
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


# ─── COURTLISTENER OPERATIONS ─── #

def search_opinions(query, jurisdiction=None, after_date=None, before_date=None,
                    court=None, limit=10, order_by="score desc"):
    """
    Search CourtListener opinions (case law).

    Args:
        query: Search terms (supports boolean: AND, OR, NOT, quotes for exact)
        jurisdiction: Filter by jurisdiction code (e.g., 'cal', 'ny', 'scotus', 'ca9')
        after_date: Filter cases after this date (YYYY-MM-DD)
        before_date: Filter cases before this date (YYYY-MM-DD)
        court: Specific court ID (e.g., 'scotus', 'ca9', 'cacd')
        limit: Max results (1-20)
        order_by: Sort order ('score desc', 'dateFiled desc', 'dateFiled asc')
    """
    params = {
        "q": query,
        "type": "o",  # opinions
        "page_size": min(limit, 20),
        "order_by": order_by,
    }
    if jurisdiction:
        params["court"] = jurisdiction
    if court:
        params["court"] = court
    if after_date:
        params["filed_after"] = after_date
    if before_date:
        params["filed_before"] = before_date

    url = f"{CL_BASE}/search/?{urlencode(params)}"
    data = fetch_json(url, cl_headers())

    if "error" in data:
        return data

    results = []
    for r in data.get("results", []):
        results.append({
            "case_name": r.get("caseName", "Unknown"),
            "court": r.get("court", "Unknown"),
            "date_filed": r.get("dateFiled", "Unknown"),
            "citation": r.get("citation", []),
            "docket_number": r.get("docketNumber", ""),
            "status": r.get("status", ""),
            "snippet": r.get("snippet", "")[:500],
            "absolute_url": f"https://www.courtlistener.com{r.get('absolute_url', '')}",
            "cluster_id": r.get("cluster_id", ""),
            "id": r.get("id", ""),
        })

    return {
        "query": query,
        "total_results": data.get("count", 0),
        "returned": len(results),
        "results": results,
    }


def get_opinion(cluster_id):
    """Get full opinion text for a specific case by cluster ID."""
    url = f"{CL_BASE}/clusters/{cluster_id}/"
    cluster = fetch_json(url, cl_headers())

    if "error" in cluster:
        return cluster

    # Get the sub-opinions (the actual text)
    opinions = []
    for op_url in cluster.get("sub_opinions", []):
        if isinstance(op_url, str):
            op = fetch_json(op_url, cl_headers())
            if "error" not in op:
                opinions.append({
                    "type": op.get("type", ""),
                    "author": op.get("author_str", ""),
                    "text": (op.get("plain_text") or op.get("html_with_citations") or "")[:10000],
                })

    return {
        "case_name": cluster.get("case_name", ""),
        "date_filed": cluster.get("date_filed", ""),
        "court": cluster.get("court", ""),
        "citations": cluster.get("citations", []),
        "docket_number": cluster.get("docket", {}).get("docket_number", "") if isinstance(cluster.get("docket"), dict) else "",
        "precedential_status": cluster.get("precedential_status", ""),
        "syllabus": cluster.get("syllabus", ""),
        "judges": cluster.get("judges", ""),
        "opinions": opinions,
        "url": f"https://www.courtlistener.com{cluster.get('absolute_url', '')}",
    }


def get_docket(docket_id):
    """Get docket details including all entries."""
    url = f"{CL_BASE}/dockets/{docket_id}/"
    data = fetch_json(url, cl_headers())

    if "error" in data:
        return data

    return {
        "case_name": data.get("case_name", ""),
        "court": data.get("court", ""),
        "docket_number": data.get("docket_number", ""),
        "date_filed": data.get("date_filed", ""),
        "date_terminated": data.get("date_terminated", ""),
        "assigned_to_str": data.get("assigned_to_str", ""),
        "referred_to_str": data.get("referred_to_str", ""),
        "cause": data.get("cause", ""),
        "nature_of_suit": data.get("nature_of_suit", ""),
        "jury_demand": data.get("jury_demand", ""),
        "pacer_case_id": data.get("pacer_case_id", ""),
        "url": f"https://www.courtlistener.com{data.get('absolute_url', '')}",
    }


def search_by_citation(citation):
    """Search for a case by its citation (e.g., '410 U.S. 113')."""
    params = {
        "q": f'citation:("{citation}")',
        "type": "o",
        "page_size": 5,
    }
    url = f"{CL_BASE}/search/?{urlencode(params)}"
    data = fetch_json(url, cl_headers())

    if "error" in data:
        return data

    results = []
    for r in data.get("results", []):
        results.append({
            "case_name": r.get("caseName", ""),
            "court": r.get("court", ""),
            "date_filed": r.get("dateFiled", ""),
            "citation": r.get("citation", []),
            "cluster_id": r.get("cluster_id", ""),
            "absolute_url": f"https://www.courtlistener.com{r.get('absolute_url', '')}",
        })

    return {
        "citation_searched": citation,
        "total_results": data.get("count", 0),
        "results": results,
    }


def search_courts(query="", jurisdiction=None):
    """List available courts for filtering."""
    params = {}
    if query:
        params["q"] = query
    if jurisdiction:
        params["jurisdiction"] = jurisdiction

    url = f"{CL_BASE}/courts/?{urlencode(params)}&page_size=50"
    data = fetch_json(url, cl_headers())

    if "error" in data:
        return data

    courts = []
    for c in data.get("results", []):
        courts.append({
            "id": c.get("id", ""),
            "full_name": c.get("full_name", ""),
            "short_name": c.get("short_name", ""),
            "jurisdiction": c.get("jurisdiction", ""),
            "in_use": c.get("in_use", False),
        })

    return {"count": len(courts), "courts": courts}


# ─── PATENT OPERATIONS (Google Patents) ─── #

def search_patents(query, limit=10):
    """Search patents via Google Patents XHR endpoint."""
    import urllib.request
    import re

    search_query = quote(query)
    url = f"https://patents.google.com/xhr/query?url=q%3D{search_query}&num={limit}"

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; HarveyBot/2.0)",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        clusters = data.get("results", {}).get("cluster", [])
        patents = []
        for cluster in clusters:
            if isinstance(cluster, dict):
                # Single result per cluster
                result = cluster.get("result", {})
                if isinstance(result, list):
                    for item in result:
                        pat = item.get("patent", {}) if isinstance(item, dict) else {}
                        if pat:
                            patents.append(_parse_google_patent(pat))
                elif isinstance(result, dict):
                    pat = result.get("patent", {})
                    if pat:
                        patents.append(_parse_google_patent(pat))

        return {
            "query": query,
            "source": "Google Patents",
            "count": len(patents),
            "total_results": data.get("results", {}).get("total_num_results", len(patents)),
            "patents": patents[:limit],
        }
    except Exception as e:
        return {"error": f"Google Patents search failed: {str(e)}", "query": query}


def _parse_google_patent(pat):
    """Parse a patent entry from Google Patents XHR response."""
    pub_num = pat.get("publication_number", "")
    # Convert format: e.g., "US-11361846-B2" -> "US11361846B2"
    clean_num = pub_num.replace("-", "")

    title = pat.get("title", "")
    # Title can be localized — extract English
    if isinstance(title, dict):
        title = title.get("en", str(title))

    snippet = pat.get("snippet", "")
    if isinstance(snippet, dict):
        snippet = snippet.get("en", str(snippet))

    inventor = pat.get("inventor", [])
    if isinstance(inventor, list):
        inventor = [i.get("name", i) if isinstance(i, dict) else str(i) for i in inventor]

    assignee = pat.get("assignee", [])
    if isinstance(assignee, list):
        assignee = [a.get("name", a) if isinstance(a, dict) else str(a) for a in assignee]

    return {
        "patent_number": clean_num,
        "publication_number": pub_num,
        "title": title,
        "snippet": str(snippet)[:500],
        "filing_date": pat.get("filing_date", ""),
        "publication_date": pat.get("publication_date", ""),
        "inventor": inventor,
        "assignee": assignee,
        "url": f"https://patents.google.com/patent/{clean_num}/en",
    }


def get_patent(patent_number):
    """Get full patent details by scraping Google Patents page."""
    import urllib.request
    import re

    # Normalize patent number format
    clean = patent_number.replace("-", "").replace(" ", "").upper()
    # Add US prefix if just a number
    if clean.isdigit():
        clean = f"US{clean}"

    url = f"https://patents.google.com/patent/{clean}/en"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; HarveyBot/2.0)",
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Could not fetch patent {clean}: {str(e)}"}

    # Extract structured data using Dublin Core meta tags
    def extract_meta(name, text, scheme=None):
        if scheme:
            m = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"[^>]*scheme="{scheme}"', text)
            if not m:
                m = re.search(rf'<meta\s+name="{name}"[^>]*scheme="{scheme}"[^>]*content="([^"]*)"', text)
        else:
            m = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"', text)
        return m.group(1).strip() if m else ""

    def extract_all_meta(name, text, scheme=None):
        if scheme:
            return re.findall(rf'<meta\s+name="{name}"\s+content="([^"]*)"[^>]*scheme="{scheme}"', text) + \
                   re.findall(rf'<meta\s+name="{name}"[^>]*scheme="{scheme}"[^>]*content="([^"]*)"', text)
        return re.findall(rf'<meta\s+name="{name}"\s+content="([^"]*)"', text)

    # Title from DC.title or <title> tag
    title = extract_meta("DC.title", html)
    if not title:
        m = re.search(r"<title>([^<]+)</title>", html)
        title = m.group(1).strip() if m else "Unknown"
        title = re.sub(r"\s*-\s*Google Patents\s*$", "", title)
        title = re.sub(r"^US\S+\s*-\s*", "", title)
    title = title.strip()

    # Patent number
    patent_number = extract_meta("citation_patent_number", html) or clean

    # Dates: filing (dateSubmitted) and issue date
    filing_date = extract_meta("DC.date", html, scheme="dateSubmitted")
    issue_date = extract_meta("DC.date", html, scheme="issue")

    # Inventors and assignees via DC.contributor with scheme
    inventors = extract_all_meta("DC.contributor", html, scheme="inventor")
    assignees = extract_all_meta("DC.contributor", html, scheme="assignee")

    # Abstract from DC.description or meta description
    abstract = extract_meta("DC.description", html)
    if not abstract:
        abstract = extract_meta("description", html)
    # Clean whitespace
    abstract = re.sub(r'\s+', ' ', abstract).strip()

    # Application number
    app_number = extract_meta("citation_patent_application_number", html)

    # PDF URL
    pdf_url = extract_meta("citation_pdf_url", html)

    # Referenced patents (prior art cited)
    references = extract_all_meta("DC.relation", html, scheme="references")

    # Claims count from page structure
    claims_count = len(re.findall(r'<div class="claim"', html))

    return {
        "patent_number": patent_number,
        "title": title,
        "abstract": abstract[:2000],
        "filing_date": filing_date,
        "issue_date": issue_date,
        "assignee": assignees,
        "inventors": inventors,
        "application_number": app_number,
        "num_claims": claims_count or "unknown",
        "references_cited": references[:20],
        "pdf_url": pdf_url,
        "url": url,
        "source": "Google Patents",
    }


# ─── JURISDICTION QUICK REFERENCE ─── #

JURISDICTION_CODES = {
    # Federal
    "scotus": "Supreme Court of the United States",
    "ca1": "First Circuit", "ca2": "Second Circuit", "ca3": "Third Circuit",
    "ca4": "Fourth Circuit", "ca5": "Fifth Circuit", "ca6": "Sixth Circuit",
    "ca7": "Seventh Circuit", "ca8": "Eighth Circuit", "ca9": "Ninth Circuit",
    "ca10": "Tenth Circuit", "ca11": "Eleventh Circuit", "cadc": "D.C. Circuit",
    "cafc": "Federal Circuit",
    # State Supreme Courts
    "cal": "California Supreme Court", "calctapp": "California Court of Appeal",
    "ny": "New York Court of Appeals", "nyappdiv": "NY Appellate Division",
    "tex": "Texas Supreme Court", "texapp": "Texas Court of Appeals",
    "fla": "Florida Supreme Court", "fladistctapp": "Florida District Court of Appeal",
    "ill": "Illinois Supreme Court", "illappct": "Illinois Appellate Court",
    "pa": "Pennsylvania Supreme Court",
    "mass": "Massachusetts Supreme Judicial Court",
    "del": "Delaware Supreme Court", "delch": "Delaware Court of Chancery",
    # Federal District Courts (examples)
    "cacd": "C.D. California", "nysd": "S.D. New York", "txsd": "S.D. Texas",
    "dcd": "D. District of Columbia",
}


# ─── CLI ─── #

def main():
    parser = argparse.ArgumentParser(
        description="Harvey Specterbot Legal Research Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "non-compete enforceability" --jurisdiction cal --limit 5
  %(prog)s search "HIPAA breach notification" --after 2020-01-01 --order "dateFiled desc"
  %(prog)s case 12345                          # Get full opinion by cluster ID
  %(prog)s citation "410 U.S. 113"             # Find Roe v. Wade
  %(prog)s docket 67890                        # Get docket details
  %(prog)s courts --jurisdiction F              # List federal courts
  %(prog)s patent-search "machine learning"     # Search USPTO patents
  %(prog)s patent 11123456                      # Get specific patent
  %(prog)s jurisdictions                        # Show common jurisdiction codes
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # search
    sp = subparsers.add_parser("search", help="Search case law opinions")
    sp.add_argument("query", help="Search terms (supports AND, OR, NOT, quotes)")
    sp.add_argument("--jurisdiction", "-j", help="Court jurisdiction code")
    sp.add_argument("--court", "-c", help="Specific court ID")
    sp.add_argument("--after", help="Cases filed after date (YYYY-MM-DD)")
    sp.add_argument("--before", help="Cases filed before date (YYYY-MM-DD)")
    sp.add_argument("--limit", "-n", type=int, default=10, help="Max results")
    sp.add_argument("--order", default="score desc", help="Sort order")

    # case
    sp = subparsers.add_parser("case", help="Get full opinion by cluster ID")
    sp.add_argument("cluster_id", help="CourtListener cluster ID")

    # citation
    sp = subparsers.add_parser("citation", help="Find case by citation")
    sp.add_argument("cite", help='Citation string (e.g., "410 U.S. 113")')

    # docket
    sp = subparsers.add_parser("docket", help="Get docket details")
    sp.add_argument("docket_id", help="CourtListener docket ID")

    # courts
    sp = subparsers.add_parser("courts", help="List available courts")
    sp.add_argument("--jurisdiction", "-j", help="Filter: F=federal, S=state")
    sp.add_argument("--query", "-q", default="", help="Search court names")

    # patent-search
    sp = subparsers.add_parser("patent-search", help="Search USPTO patents")
    sp.add_argument("query", help="Search terms")
    sp.add_argument("--limit", "-n", type=int, default=10)

    # patent
    sp = subparsers.add_parser("patent", help="Get patent details")
    sp.add_argument("number", help="Patent number")

    # jurisdictions
    subparsers.add_parser("jurisdictions", help="Show common jurisdiction codes")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        result = search_opinions(args.query, jurisdiction=args.jurisdiction,
                                 after_date=args.after, before_date=args.before,
                                 court=args.court, limit=args.limit, order_by=args.order)
    elif args.command == "case":
        result = get_opinion(args.cluster_id)
    elif args.command == "citation":
        result = search_by_citation(args.cite)
    elif args.command == "docket":
        result = get_docket(args.docket_id)
    elif args.command == "courts":
        result = search_courts(args.query, args.jurisdiction)
    elif args.command == "patent-search":
        result = search_patents(args.query, args.limit)
    elif args.command == "patent":
        result = get_patent(args.number)
    elif args.command == "jurisdictions":
        result = JURISDICTION_CODES
    else:
        parser.print_help()
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
