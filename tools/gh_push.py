#!/usr/bin/env python3
"""Targeted Git Data API push: blobs -> tree (base_tree=head) -> commit -> update ref.
Usage: python3 tools/gh_push.py "commit message" [file ...]
Files are repo-relative paths under ~/workspace/sites/deepstate.
Follows AGENTS.md lessons: numeric repo-ID path for writes, verify blob SHAs non-empty."""
import base64, json, os, subprocess, sys

REPO_ID = "1410011559"          # hectorchanht/deepstate-files
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GHAPI = os.path.expanduser("~/workspace/skills/github-pat/bin/ghapi")

def ghapi(method, path, data=None):
    cmd = [GHAPI, method, path]
    if data is not None:
        cmd += ["--data", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(f"ghapi {method} {path} failed: {out.stderr[:500]}")
    return json.loads(out.stdout) if out.stdout.strip() else {}

def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "update"
    files = sys.argv[2:]
    # current head
    ref = ghapi("GET", f"/repositories/{REPO_ID}/git/ref/heads/{BRANCH}")
    head_sha = ref["object"]["sha"]
    head_tree = ghapi("GET", f"/repositories/{REPO_ID}/git/commits/{head_sha}")["tree"]["sha"]
    print(f"head {head_sha[:8]} tree {head_tree[:8]}")
    tree = []
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            print(f"SKIP missing {f}"); continue
        with open(p, "rb") as fh: content = fh.read()
        b64 = base64.b64encode(content).decode()
        blob = ghapi("POST", f"/repositories/{REPO_ID}/git/blobs",
                     {"content": b64, "encoding": "base64"})
        sha = blob.get("sha", "")
        assert sha, f"EMPTY BLOB SHA for {f} — aborting (would delete file)"
        tree.append({"path": f, "mode": "100644", "type": "blob", "sha": sha})
        print(f"blob {f} {sha[:8]}")
    if not tree:
        print("nothing to push"); return
    new_tree = ghapi("POST", f"/repositories/{REPO_ID}/git/trees",
                     {"base_tree": head_tree, "tree": tree})["sha"]
    commit = ghapi("POST", f"/repositories/{REPO_ID}/git/commits",
                   {"message": msg, "tree": new_tree, "parents": [head_sha]})["sha"]
    ghapi("PATCH", f"/repositories/{REPO_ID}/git/refs/heads/{BRANCH}",
          {"sha": commit})
    print(f"pushed {commit[:8]} ({len(tree)} files)")

if __name__ == "__main__":
    main()
