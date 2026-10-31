"""Tell Bing (and Yandex, Seznam, Naver) that pages changed, so they re-read them within minutes.

IndexNow works with a key: the file <key>.txt at the site root proves we own the site.
Run AFTER the push has deployed (the pages and the key file must be live first).

    python3 _site/indexnow.py --changed HEAD~1   # pages changed since that commit (normal use)
    python3 _site/indexnow.py --all              # every URL in sitemap.xml (first time, or after a big rebuild)
    python3 _site/indexnow.py URL [URL ...]      # just these
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "cleandataengineering.ai"
SITE = f"https://{HOST}"


def key():
    keys = [p.stem for p in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", p.stem)]
    if len(keys) != 1:
        sys.exit(f"expected one IndexNow key file at the site root, found {len(keys)}")
    return keys[0]


def url_of(rel):
    if rel == "index.html":
        return SITE + "/"
    return f"{SITE}/{rel[:-10]}" if rel.endswith("/index.html") else f"{SITE}/{rel}"


def changed(ref):
    out = subprocess.run(["git", "diff", "--name-only", f"{ref}..HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [url_of(f) for f in out.split() if f.endswith(".html") and not f.startswith(("_", "."))]


def submit(urls):
    k = key()
    for i in range(0, len(urls), 10000):
        body = json.dumps({"host": HOST, "key": k, "keyLocation": f"{SITE}/{k}.txt", "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                     headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"IndexNow: {r.status} for {len(urls[i:i + 10000])} urls")
        except urllib.error.HTTPError as e:
            print(f"IndexNow: {e.code} {e.reason}  (403 = key file not live yet; 422 = a URL is not on {HOST})")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--all":
        urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
    elif args[0] == "--changed":
        urls = changed(args[1] if len(args) > 1 else "HEAD~1")
    else:
        urls = args
    if not urls:
        print("nothing to submit")
        return
    submit(urls)


if __name__ == "__main__":
    main()
