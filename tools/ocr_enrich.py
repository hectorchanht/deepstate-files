#!/usr/bin/env python3
"""OCR enrichment for Deep State Files.

Downloads each target record's primary document. If it's a PDF with no
extractable text (scanned images), runs PaddleOCR on the first MAX_PAGES
pages. Saves extracted text to ocr_text/<id>.txt for human/AI review —
this script NEVER writes tldr/ai_summary itself; review happens separately.

Usage:
    python3 tools/ocr_enrich.py [record-id ...]   # specific records
    python3 tools/ocr_enrich.py all                # all records lacking tldr

Designed to run on GitHub Actions (ubuntu-latest) where PaddleOCR can be
pip-installed; PaddleOCR does not run on the dev VM.
"""
import json, os, sys, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
REC = os.path.join(SRC, "records")
OUT = os.path.join(HERE, "..", "ocr_text")
MAX_PAGES = 40
DPI = 150

UA = {"User-Agent": "DeepStateFiles-ocr/1.0 (+https://deepstate.hectorchan.com)"}


def load_records(ids):
    recs = []
    for fn in sorted(glob.glob(os.path.join(REC, "*.json"))):
        r = json.load(open(fn))
        if ids != "all" and r["id"] not in ids:
            continue
        if ids == "all" and r.get("tldr"):
            continue
        recs.append(r)
    return recs


def download(url, dest, timeout=90):
    import requests
    r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    open(dest, "wb").write(r.content)
    return r.headers.get("content-type", "")


def pdf_has_text(path):
    try:
        import fitz
        doc = fitz.open(path)
        words = sum(len(p.get_text().split()) for p in doc[:5])
        doc.close()
        return words > 50
    except Exception:
        return False


def extract_digital_text(path):
    import fitz
    doc = fitz.open(path)
    parts = []
    for p in doc:
        t = p.get_text().strip()
        if t:
            parts.append(t)
    doc.close()
    return "\n\n".join(parts)


def ocr_pdf(path):
    from paddleocr import PaddleOCR
    import fitz
    ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    doc = fitz.open(path)
    n = min(len(doc), MAX_PAGES)
    parts = []
    for i in range(n):
        pix = doc[i].get_pixmap(dpi=DPI)
        import numpy as np
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = img[:, :, :3]
        res = ocr.ocr(img, cls=True)
        lines = []
        for block in res or []:
            for line in block or []:
                try:
                    lines.append(line[1][0])
                except Exception:
                    pass
        parts.append(f"\n--- page {i+1} ---\n" + "\n".join(lines))
    doc.close()
    return "\n".join(parts), len(doc), n


def html_to_text(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    import html as h
    return re.sub(r"\s+", " ", h.unescape(raw)).strip()


def process(r):
    rid = r["id"]
    url = r["sources"][0]["url"] if r.get("sources") else None
    meta = {"id": rid, "source_url": url, "status": "pending"}
    if not url:
        meta["status"] = "no_source"
        return meta
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join("/tmp", f"ocr_{rid}")
    try:
        ctype = download(url, tmp)
    except Exception as e:
        meta["status"] = "fetch_failed"
        meta["error"] = f"{type(e).__name__}: {e}"[:200]
        return meta
    try:
        if "pdf" in ctype or tmp.lower().endswith(".pdf") or open(tmp, "rb").read(4) == b"%PDF":
            if pdf_has_text(tmp):
                text = extract_digital_text(tmp)
                meta.update(status="digital_text", pages=None,
                            chars=len(text))
            else:
                text, total, done = ocr_pdf(tmp)
                meta.update(status="ocrd", pages_total=total,
                            pages_ocrd=done, chars=len(text))
        else:
            text = html_to_text(tmp)
            meta.update(status="html_text", chars=len(text))
        open(os.path.join(OUT, rid + ".txt"), "w").write(text[:500000])
    except Exception as e:
        meta["status"] = "extract_failed"
        meta["error"] = f"{type(e).__name__}: {e}"[:200]
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    json.dump(meta, open(os.path.join(OUT, rid + ".meta.json"), "w"), indent=2)
    return meta


def main():
    args = sys.argv[1:] or ["all"]
    ids = "all" if args == ["all"] else set(args)
    recs = load_records(ids)
    print(f"ocr_enrich: {len(recs)} records to process")
    results = [process(r) for r in recs]
    ok = [m for m in results if m["status"] in ("digital_text", "html_text", "ocrd")]
    print(f"done: {len(ok)} extracted, {len(results)-len(ok)} failed")
    for m in results:
        if m["status"] not in ("digital_text", "html_text", "ocrd"):
            print(f"  FAIL {m['id']}: {m['status']} {m.get('error','')[:80]}")


if __name__ == "__main__":
    main()
