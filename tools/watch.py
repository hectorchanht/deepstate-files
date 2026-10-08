#!/usr/bin/env python3
"""Source watcher: poll official release feeds, file new records as reviewed=false.
- DOJ press releases: JSON API (machine-readable)
- FBI Vault / NARA / House Oversight / CIA reading room: HTML scraping (best-effort)
New records go to src/records/watch-<slug>.json with reviewed=false and are
rendered with a 'NEW — PENDING REVIEW' badge until checked.
Idempotent: skips URLs already present in any record's sources.
"""
import json, os, re, sys, html as htmllib
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
REC = os.path.join(SRC, "records")

KEYWORDS = ["epstein", "declassif", "jfk", "rfk", "king assassination", "foia",
            "unredacted", "cointelpro", "mkultra", "vault", "transparency act",
            "maxwell", "assassination records"]

DOJ_API = ("https://www.justice.gov/api/v1/press_releases.json"
           "?pagesize=50&page=0")

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "DeepStateFiles-watcher/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def known_urls():
    urls = set()
    for fn in os.listdir(REC):
        if not fn.endswith(".json"):
            continue
        try:
            r = json.load(open(os.path.join(REC, fn)))
        except Exception:
            continue
        for s in r.get("sources", []):
            urls.add(s.get("url", "").rstrip("/").lower())
    return urls

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "untitled"

def matches(text):
    t = text.lower()
    return [k for k in KEYWORDS if k in t]

def check_doj(known):
    """DOJ press releases JSON API."""
    try:
        data = json.loads(fetch(DOJ_API))
    except Exception as e:
        print(f"DOJ API fetch failed: {e}", file=sys.stderr)
        return []
    items = data.get("results", data if isinstance(data, list) else [])
    out = []
    for it in items:
        title = it.get("title", "")
        url = it.get("url") or it.get("link") or ""
        if not url.startswith("http"):
            url = "https://www.justice.gov" + url
        date = (it.get("date") or it.get("created") or "")[:10]
        ks = matches(title)
        if ks and url.rstrip("/").lower() not in known:
            out.append({"title": htmllib.unescape(title), "url": url,
                        "date": date or "2026-01-01", "via": "DOJ press releases",
                        "keywords": ks})
    return out

def scrape_links(page_url, base, known):
    """Best-effort <a href> scraper for HTML-only sources."""
    try:
        page = fetch(page_url)
    except Exception as e:
        print(f"scrape {page_url} failed: {e}", file=sys.stderr)
        return []
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', page, re.S):
        href, text = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        href = htmllib.unescape(href)
        if href.startswith("/"):
            href = base.rstrip("/") + href
        if not href.startswith("http") or href in seen:
            continue
        seen.add(href)
        ks = matches(title := (text + " " + href))
        if ks and href.rstrip("/").lower() not in known and len(text) > 12:
            out.append({"title": htmllib.unescape(text[:140]), "url": href,
                        "date": "2026-01-01", "via": page_url, "keywords": ks})
    return out[:25]

def file_record(item, topic="epstein"):
    rid = "watch-" + slugify(item["title"])
    rec = {
        "id": rid,
        "topic": topic,
        "title": item["title"],
        "date": item["date"],
        "kind": "document",
        "status": "verified",
        "summary": f"New release spotted by the source watcher ({item['via']}). Matched keywords: {', '.join(item['keywords'])}. Awaiting editorial review — summary to be written from the primary source.",
        "sources": [{"label": "Primary source", "url": item["url"]}],
        "tags": ["watcher"] + item["keywords"][:3],
        "added": item["date"],
        "reviewed": False,
    }
    path = os.path.join(REC, rid + ".json")
    if os.path.exists(path):
        return None
    json.dump(rec, open(path, "w"), indent=2, ensure_ascii=False)
    return rid

def main():
    known = known_urls()
    found = []
    found += check_doj(known)
    # HTML-only sources (best effort; may be bot-walled from some networks)
    for page_url, base in [
        ("https://vault.fbi.gov/recently-added", "https://vault.fbi.gov"),
        ("https://www.archives.gov/news", "https://www.archives.gov"),
        ("https://oversight.house.gov/release", "https://oversight.house.gov"),
    ]:
        found += scrape_links(page_url, base, known)
    added = []
    for it in found:
        rid = file_record(it)
        if rid:
            added.append(rid)
            known.add(it["url"].rstrip("/").lower())
    print(f"watcher: {len(found)} candidates, {len(added)} new records")
    for rid in added:
        print(" +", rid)

if __name__ == "__main__":
    main()
