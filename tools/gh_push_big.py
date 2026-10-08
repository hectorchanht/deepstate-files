#!/usr/bin/env python3
"""Push files (incl. big ones) via GitHub Git Data API without argv size limits.
Usage: python3 tools/gh_push_big.py "commit message" [file ...]
Files are repo-relative paths under ~/workspace/sites/deepstate.
Uses the same authd surrogate as the github-pat ghapi wrapper.
"""
import base64, json, os, sys, urllib.request, urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

REPO_ID = "1410011559"
BRANCH = "main"
BASE = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call(method, path, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(BASE + path, data=body, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "muse-github-pat-skill")
    if body:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.github-pat",
                             allowed_hosts=("api.github.com",))
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return read_json_response(resp) if resp.status != 204 else {}
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: "
                           f"{exc.read().decode('utf-8', 'replace')[:500]}")


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "update"
    files = sys.argv[2:]
    ref = call("GET", f"/repositories/{REPO_ID}/git/ref/heads/{BRANCH}")
    head_sha = ref["object"]["sha"]
    head_tree = call("GET", f"/repositories/{REPO_ID}/git/commits/{head_sha}")["tree"]["sha"]
    print(f"head {head_sha[:8]} tree {head_tree[:8]}", flush=True)
    tree = []
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            print(f"SKIP missing {f}")
            continue
        with open(p, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        blob = call("POST", f"/repositories/{REPO_ID}/git/blobs",
                    {"content": b64, "encoding": "base64"})
        sha = blob.get("sha", "")
        assert sha, f"EMPTY BLOB SHA for {f} — aborting (would delete file)"
        tree.append({"path": f, "mode": "100644", "type": "blob", "sha": sha})
        print(f"blob {f} {sha[:8]}", flush=True)
    if not tree:
        print("nothing to push")
        return
    new_tree = call("POST", f"/repositories/{REPO_ID}/git/trees",
                    {"base_tree": head_tree, "tree": tree})["sha"]
    commit = call("POST", f"/repositories/{REPO_ID}/git/commits",
                  {"message": msg, "tree": new_tree,
                   "parents": [head_sha]})["sha"]
    call("PATCH", f"/repositories/{REPO_ID}/git/refs/heads/{BRANCH}",
         {"sha": commit})
    print(f"pushed {commit[:8]} ({len(tree)} files)")


if __name__ == "__main__":
    main()
