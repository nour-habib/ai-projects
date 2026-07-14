import html
import re
import xml.etree.ElementTree as ET

import requests

MEDLINE_URL = "https://wsearch.nlm.nih.gov/ws/query"
REQUEST_TIMEOUT = 10


def _strip_html(text: str) -> str:
    """Remove the highlight spans / HTML tags MedlinePlus embeds in content."""
    cleaned = re.sub(r"<[^>]+>", "", html.unescape(text or ""))
    return re.sub(r"\s+", " ", cleaned).strip()


def search_medline(query: str, max_results: int = 5) -> list[dict]:
    """Query MedlinePlus health topics; return cleaned result documents."""
    params = {"db": "healthTopics", "term": query, "retmax": max_results}
    response = requests.get(MEDLINE_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    results = []
    for doc in root.findall(".//document"):
        fields = {c.get("name"): c.text for c in doc.findall("content")}
        results.append(
            {
                "title": _strip_html(fields.get("title", "")),
                "url": doc.get("url", ""),
                "summary": _strip_html(fields.get("FullSummary") or fields.get("snippet") or ""),
                "organization": _strip_html(fields.get("organizationName", "")),
            }
        )
    return results


def handle_query(query: str, max_results: int = 5) -> dict:
    """Entry point for a disease search. Returns {query, sources, error}."""
    query = (query or "").strip()
    if not query:
        return {"query": query, "sources": [], "error": "Empty query."}

    try:
        results = search_medline(query, max_results=max_results)
    except requests.exceptions.RequestException as exc:
        return {"query": query, "sources": [], "error": f"MedlinePlus request failed: {exc}"}

    return {"query": query, "sources": results, "error": None}
