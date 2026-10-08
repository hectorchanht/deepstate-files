#!/usr/bin/env python3
"""Deep State Files — static site generator. Reads src/topics.json + src/records/*.json → dist/."""
import json, os, shutil, html, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
DIST = os.path.join(HERE, "dist")
BASE = "https://deepstate.hectorchan.com"
TODAY = datetime.date.today().isoformat()

STATUS = {
    "verified": ("DOCUMENT", "st-verified", "Confirmed by primary sources — court records, government reports, declassified documents."),
    "disputed": ("CLAIM: DISPUTED", "st-disputed", "Actively contradicted by primary sources."),
    "unproven": ("CLAIM: UNPROVEN", "st-unproven", "No primary-source evidence either way."),
}

def esc(s): return html.escape(s or "")

def load():
    topics = json.load(open(os.path.join(SRC, "topics.json")))
    records = []
    for fn in sorted(os.listdir(os.path.join(SRC, "records"))):
        if fn.endswith(".json"):
            records.append(json.load(open(os.path.join(SRC, "records", fn))))
    return topics, records

CSS = """
:root{--bg:#0b0c0a;--panel:#141613;--panel2:#1a1d18;--ink:#e8e2d4;--dim:#9a9484;--amber:#d9a441;--red:#c0392b;--green:#7fb069;--yellow:#d9c441;--line:#2a2d26;--mono:"Courier New",ui-monospace,monospace;--serif:Georgia,"Times New Roman",serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--serif);line-height:1.65;font-size:17px}
a{color:var(--amber);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1060px;margin:0 auto;padding:0 20px}
header.site{border-bottom:3px double var(--line);padding:22px 0 16px;background:linear-gradient(180deg,#101210,#0b0c0a)}
.brand{font-family:var(--mono);font-weight:bold;font-size:22px;letter-spacing:3px;color:var(--ink)}
.brand .amber{color:var(--amber)}
.tagline{font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--dim);margin-top:4px}
nav.main{margin-top:14px;display:flex;gap:22px;font-family:var(--mono);font-size:13px;letter-spacing:1px}
nav.main a{color:var(--dim)}nav.main a:hover,nav.main a.on{color:var(--amber)}
.hero{padding:56px 0 40px;position:relative}
.stamp{display:inline-block;font-family:var(--mono);font-weight:bold;font-size:13px;letter-spacing:4px;color:var(--red);border:3px solid var(--red);padding:6px 14px;transform:rotate(-4deg);margin-bottom:22px;opacity:.92}
h1{font-size:clamp(34px,6vw,58px);line-height:1.1;font-weight:normal;letter-spacing:.5px}
h1 .thin{color:var(--dim)}
.lede{font-size:19px;color:var(--dim);max-width:640px;margin-top:14px}
.stats{display:flex;gap:0;margin-top:30px;border:1px solid var(--line);font-family:var(--mono)}
.stats div{flex:1;padding:14px 18px;border-right:1px solid var(--line)}
.stats div:last-child{border-right:0}
.stats b{font-size:26px;color:var(--amber);display:block}
.stats span{font-size:11px;letter-spacing:2px;color:var(--dim)}
h2.sec{font-family:var(--mono);font-size:14px;letter-spacing:3px;color:var(--dim);margin:44px 0 18px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);padding:20px;position:relative;transition:border-color .15s}
.card:hover{border-color:var(--amber)}
.card .code{font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--dim)}
.card h3{font-size:20px;margin:8px 0;font-weight:normal}
.card p{font-size:15px;color:var(--dim)}
.card .n{font-family:var(--mono);font-size:12px;color:var(--amber);margin-top:10px;display:block}
.badge{display:inline-block;font-family:var(--mono);font-size:11px;font-weight:bold;letter-spacing:1.5px;padding:3px 10px;border:1.5px solid;margin-bottom:10px}
.st-verified{color:var(--green);border-color:var(--green)}
.st-disputed{color:var(--red);border-color:var(--red)}
.st-unproven{color:var(--yellow);border-color:var(--yellow)}
.fileitem{background:var(--panel);border:1px solid var(--line);padding:18px 20px;margin-bottom:12px}
.fileitem h3{font-size:19px;font-weight:normal;margin:6px 0}
.fileitem .meta{font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:1px}
.fileitem p{font-size:15px;color:var(--dim);margin-top:6px}
.sources{margin-top:26px;border-top:1px solid var(--line);padding-top:18px}
.sources li{list-style:none;margin:8px 0;font-family:var(--mono);font-size:14px}
.sources li::before{content:"▸ ";color:var(--amber)}
.key{background:var(--panel);border:1px solid var(--line);padding:22px;margin-top:20px}
.key p{font-size:15px;color:var(--dim);margin:8px 0}
footer.site{border-top:3px double var(--line);margin-top:60px;padding:26px 0 40px;font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:1px}
footer.site .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}
.redact{background:var(--ink);color:transparent;user-select:none;padding:0 6px}
.searchbox{width:100%;background:var(--panel);border:1px solid var(--line);color:var(--ink);font-family:var(--serif);font-size:18px;padding:14px 18px;margin-top:20px}
#results .fileitem{cursor:pointer}
@media(max-width:640px){.stats{flex-direction:column}.stats div{border-right:0;border-bottom:1px solid var(--line)}nav.main{gap:14px;flex-wrap:wrap}}
"""

HEADER = """
<header class="site"><div class="wrap">
<div class="brand">DEEP STATE <span class="amber">FILES</span></div>
<div class="tagline">EVIDENCE-FIRST ARCHIVE · DOCUMENTS, NOT RUMORS</div>
<nav class="main"><a href="/" class="{h}">INDEX</a><a href="/topics/" class="{t}">TOPICS</a><a href="/search/" class="{s}">SEARCH</a><a href="/about/" class="{a}">ABOUT</a></nav>
</div></header>
"""

FOOTER = """
<footer class="site"><div class="wrap"><span>DEEP STATE FILES · {today}</span><span>EVERY FILE CITES ITS PRIMARY SOURCE</span></div></footer>
"""

def page(title, body, nav="h"):
    on = dict(h="", t="", s="", a="")
    on[nav] = "on"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Deep State Files</title>
<meta name="description" content="Evidence-first archive of declassified documents, court records and FOIA releases.">
<style>{CSS}</style></head><body>
{HEADER.format(**on)}
<main class="wrap">{body}</main>
{FOOTER.format(today=TODAY)}
</body></html>"""

def card_topic(t, n):
    return f"""<a class="card" href="/topics/{t['id']}/"><div class="code">{t['code']}</div><h3>{esc(t['title'])}</h3><p>{esc(t['lede'])}</p><span class="n">{n} FILES →</span></a>"""

def fileitem(r, topic_map):
    label, cls, _ = STATUS[r["status"]]
    t = topic_map[r["topic"]]
    return f"""<div class="fileitem"><span class="badge {cls}">{label}</span>
<div class="meta">{r['date']} · <a href="/topics/{t['id']}/">{esc(t['title']).upper()}</a></div>
<h3><a href="/files/{r['id']}/">{esc(r['title'])}</a></h3><p>{esc(r['summary'][:220])}…</p></div>"""

def build_index(topics, records):
    topic_map = {t["id"]: t for t in topics}
    counts = {t["id"]: 0 for t in topics}
    docs = sum(1 for r in records if r["kind"] == "document")
    for r in records: counts[r["topic"]] = counts.get(r["topic"], 0) + 1
    cards = "".join(card_topic(t, counts[t["id"]]) for t in topics)
    latest = sorted(records, key=lambda r: r["date"], reverse=True)[:6]
    items = "".join(fileitem(r, topic_map) for r in latest)
    key = "".join(f"<p><span class='badge {cls}'>{label}</span> — {esc(desc)}</p>" for label, cls, desc in STATUS.values())
    body = f"""
<div class="hero"><span class="stamp">DECLASSIFIED</span>
<h1>The paper trail<br><span class="thin">behind the legends.</span></h1>
<p class="lede">An archive of declassified documents, court records and FOIA releases on the deep state, Epstein, 9/11, banking dynasties and more. Every file cites its primary source. Every claim is labeled: confirmed by documents, contradicted by documents, or no evidence either way.</p>
<div class="stats"><div><b>{len(records)}</b><span>FILES</span></div><div><b>{docs}</b><span>DOCUMENTS</span></div><div><b>{len(topics)}</b><span>TOPICS</span></div><div><b>100%</b><span>SOURCED</span></div></div></div>
<h2 class="sec">TOPICS</h2><div class="cards">{cards}</div>
<h2 class="sec">HOW TO READ THIS ARCHIVE</h2><div class="key">{key}
<p style="margin-top:12px">A <span class="redact">redacted</span> claim is still a claim. This archive separates what the documents prove from what the internet believes.</p></div>
<h2 class="sec">LATEST FILES</h2>{items}
"""
    return page("Index", body, "h")

def build_topics_index(topics, records):
    counts = {}
    for r in records: counts[r["topic"]] = counts.get(r["topic"], 0) + 1
    cards = "".join(card_topic(t, counts.get(t["id"], 0)) for t in topics)
    return page("Topics", f'<h2 class="sec">ALL TOPICS</h2><div class="cards">{cards}</div>', "t")

def build_topic(t, records):
    docs = [r for r in records if r["topic"] == t["id"] and r["kind"] == "document"]
    claims = [r for r in records if r["topic"] == t["id"] and r["kind"] == "claim"]
    topic_map = {t["id"]: t}
    d = "".join(fileitem(r, topic_map) for r in sorted(docs, key=lambda r: r["date"], reverse=True))
    c = "".join(fileitem(r, topic_map) for r in sorted(claims, key=lambda r: r["date"], reverse=True))
    body = f"""<div class="hero" style="padding:36px 0 10px"><div class="code" style="font-family:var(--mono);font-size:11px;letter-spacing:2px;color:var(--dim)">{t['code']}</div>
<h1 style="font-size:clamp(28px,5vw,44px)">{esc(t['title'])}</h1><p class="lede">{esc(t['lede'])}</p></div>
<h2 class="sec">THE DOCUMENTS</h2>{d or '<p style="color:var(--dim)">No documents filed yet.</p>'}
<h2 class="sec">CLAIMS VS. EVIDENCE</h2>{c or '<p style="color:var(--dim)">No claims filed yet.</p>'}"""
    return page(t["title"], body, "t")

def build_record(r, topics):
    label, cls, desc = STATUS[r["status"]]
    t = next(x for x in topics if x["id"] == r["topic"])
    srcs = "".join(f'<li><a href="{esc(s["url"])}" rel="noopener" target="_blank">{esc(s["label"])}</a></li>' for s in r["sources"])
    review = "" if r.get("reviewed") else '<p style="margin-top:14px"><span class="badge st-unproven">NEW — PENDING REVIEW</span></p>'
    body = f"""<div class="hero" style="padding:36px 0 10px">
<span class="badge {cls}">{label}</span>
<div class="meta" style="font-family:var(--mono);font-size:12px;color:var(--dim);letter-spacing:1px;margin:10px 0">{r['date']} · <a href="/topics/{t['id']}/">{esc(t['title']).upper()}</a> · FILE {r['id'].upper()}</div>
<h1 style="font-size:clamp(26px,5vw,42px)">{esc(r['title'])}</h1></div>
<p style="font-size:19px;max-width:700px">{esc(r['summary'])}</p>
<p style="color:var(--dim);font-size:15px;margin-top:12px">Evidence status: {esc(desc)}</p>
{review}
<div class="sources"><h2 class="sec" style="margin-top:0">PRIMARY SOURCES</h2><ul>{srcs}</ul></div>"""
    return page(r["title"], body, "t")

def build_about():
    key = "".join(f"<p><span class='badge {cls}'>{label}</span> — {esc(desc)}</p>" for label, cls, desc in STATUS.values())
    body = f"""<div class="hero" style="padding:36px 0 10px"><h1 style="font-size:clamp(28px,5vw,44px)">About this archive</h1></div>
<p style="max-width:700px;font-size:19px">Deep State Files is an evidence-first archive. A <b>file</b> here is a real document — a declassified report, a court filing, an FBI Vault release, a FOIA tranche. Internet folklore is not filed as fact; popular claims are listed separately with their evidence status, so you can see exactly where the paper trail ends.</p>
<h2 class="sec">THE EVIDENCE KEY</h2><div class="key">{key}</div>
<h2 class="sec">HOW IT GROWS</h2><div class="key"><p>A watcher monitors the FBI Vault, NARA, the DOJ and House Oversight release feeds. New official releases are filed automatically and marked <span class="badge st-unproven">NEW — PENDING REVIEW</span> until checked.</p></div>
<h2 class="sec">CREDO</h2><div class="key"><p>Documents, not rumors. If a claim has no primary source, it is labeled as such — no matter how viral it is.</p></div>"""
    return page("About", body, "a")

def build_search(records, topics):
    tm = {t["id"]: t["title"] for t in topics}
    idx = [{"id": r["id"], "title": r["title"], "topic": tm[r["topic"]], "tid": r["topic"],
            "summary": r["summary"], "tags": " ".join(r.get("tags", [])), "status": r["status"],
            "date": r["date"]} for r in records]
    js = """<script>
const IDX=%s;
function go(q){q=q.toLowerCase().trim();const box=document.getElementById('results');
if(q.length<2){box.innerHTML='<p style="color:var(--dim)">Type at least 2 characters.</p>';return}
const hit=IDX.filter(r=>(r.title+' '+r.summary+' '+r.tags+' '+r.topic).toLowerCase().includes(q)).slice(0,40);
box.innerHTML=hit.length?hit.map(r=>`<div class="fileitem"><div class="meta">${r.date} · ${r.topic.toUpperCase()}</div><h3><a href="/files/${r.id}/">${r.title}</a></h3><p>${r.summary.slice(0,180)}…</p></div>`).join(''):'<p style="color:var(--dim)">No files match.</p>'}
document.getElementById('q').addEventListener('input',e=>go(e.target.value));
const p=new URLSearchParams(location.search);if(p.get('q')){document.getElementById('q').value=p.get('q');go(p.get('q'))}
</script>""" % json.dumps(idx, ensure_ascii=False).replace("</", "<\\/")
    body = '<h2 class="sec">SEARCH THE ARCHIVE</h2><input id="q" class="searchbox" placeholder="epstein, 9/11, cointelpro…" autocomplete="off"><div id="results" style="margin-top:18px"></div>' + js
    return page("Search", body, "s")

def build_llms(topics, records):
    lines = ["# Deep State Files", "> Evidence-first archive of declassified documents, court records and FOIA releases.",
             "", "## Topics"]
    for t in topics: lines.append(f"- [{t['title']}]({BASE}/topics/{t['id']}/): {t['lede']}")
    lines += ["", "## Files"]
    for r in sorted(records, key=lambda r: r["date"], reverse=True):
        label = STATUS[r["status"]][0]
        lines.append(f"- [{r['title']}]({BASE}/files/{r['id']}/) ({r['date']}) [{label}]")
    return "\n".join(lines) + "\n"

def build_sitemap(topics, records):
    urls = [f"<url><loc>{BASE}/</loc><lastmod>{TODAY}</lastmod></url>",
            f"<url><loc>{BASE}/topics/</loc><lastmod>{TODAY}</lastmod></url>",
            f"<url><loc>{BASE}/about/</loc><lastmod>{TODAY}</lastmod></url>"]
    for t in topics: urls.append(f"<url><loc>{BASE}/topics/{t['id']}/</loc><lastmod>{TODAY}</lastmod></url>")
    for r in records: urls.append(f"<url><loc>{BASE}/files/{r['id']}/</loc><lastmod>{TODAY}</lastmod></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>"

def build_feed(topics, records):
    tm = {t["id"]: t["title"] for t in topics}
    items = []
    for r in sorted(records, key=lambda r: r["date"], reverse=True)[:20]:
        items.append(f"""<item><title>{esc(r['title'])}</title><link>{BASE}/files/{r['id']}/</link>
<guid>{BASE}/files/{r['id']}/</guid><pubDate>{r['date']}T12:00:00Z</pubDate>
<description>{esc(r['summary'][:300])}</description><category>{esc(tm[r['topic']])}</category></item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Deep State Files</title><link>{BASE}/</link>
<description>Evidence-first archive: new files as they are added.</description>
{''.join(items)}</channel></rss>"""

def main():
    topics, records = load()
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    def w(path, content):
        p = os.path.join(DIST, path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(content)
    w("index.html", build_index(topics, records))
    w("topics/index.html", build_topics_index(topics, records))
    for t in topics: w(f"topics/{t['id']}/index.html", build_topic(t, records))
    for r in records: w(f"files/{r['id']}/index.html", build_record(r, topics))
    w("about/index.html", build_about())
    w("search/index.html", build_search(records, topics))
    w("llms.txt", build_llms(topics, records))
    w("sitemap.xml", build_sitemap(topics, records))
    w("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    w("feed.xml", build_feed(topics, records))
    print(f"built {len(records)} records, {len(topics)} topics → {DIST}")

if __name__ == "__main__":
    main()
