#!/usr/bin/env python3
"""Checks every local link in the site.

  python3 scripts/check_links.py                 # files on disk
  python3 scripts/check_links.py http://localhost:8765/tich-tac-tien-site/
                                                 # also fetch each page and asset over HTTP (expects 200)

For every HTML page: each href/src/srcset (and CSS url()) that points inside the site must exist,
#fragments must match an id on the target page, and links must be relative (no "/..." or site URLs),
except in 404.html, which GitHub Pages serves at any path and so uses /tich-tac-tien-site/ root paths.
"""
import os, re, sys, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PREFIX = "/tich-tac-tien-site/"
SITE = "https://jarvis219.github.io" + PREFIX


class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.links.append((tag, k, a[k]))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                self.links.append((tag, "srcset", part.strip().split(" ")[0]))
        if tag == "meta" and a.get("content", "").startswith(SITE):
            self.links.append((tag, "content", a["content"]))


def parse(path):
    p = Collect()
    p.feed(open(path, encoding="utf-8").read())
    return p


def page_url(rel):
    """The URL path a file is served at on GitHub Pages."""
    rel = rel.replace(os.sep, "/")
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return PREFIX + rel


def to_file(url_path):
    rel = unquote(url_path[len(PREFIX):])
    path = os.path.join(ROOT, rel)
    if url_path.endswith("/") or os.path.isdir(path):
        path = os.path.join(path, "index.html")
    return path


def main():
    base_http = sys.argv[1] if len(sys.argv) > 1 else None
    pages = sorted(os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(ROOT) for f in fs
                   if f.endswith(".html") and "/." not in d)
    parsed = {p: parse(os.path.join(ROOT, p)) for p in pages}
    errors, checked, fetched = [], 0, set()
    for page in pages:
        info = parsed[page]
        here = page_url(page)
        for tag, attr, link in info.links:
            if link.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue
            if attr == "content":  # og:/twitter: absolute URLs must point at real files
                target = urlparse(link).path
            else:
                u = urlparse(link)
                if u.scheme in ("http", "https"):
                    if link.startswith(SITE) and tag != "link":
                        errors.append(f"{page}: absolute site URL in {attr}: {link}")
                    continue  # external (Google Fonts) or canonical/alternate
                if link.startswith("/") and page != "404.html":
                    errors.append(f"{page}: root-relative link (breaks under the sub-path): {link}")
                target = urlparse(urljoin(here, link)).path
            if not target.startswith(PREFIX):
                errors.append(f"{page}: {link} escapes the site")
                continue
            path = to_file(target)
            checked += 1
            if not os.path.isfile(path):
                errors.append(f"{page}: missing {link} -> {os.path.relpath(path, ROOT)}")
                continue
            frag = urlparse(link).fragment
            if frag and attr != "content":
                rel = os.path.relpath(path, ROOT)
                ids = parsed[rel].ids if rel in parsed else set()
                if frag not in ids:
                    errors.append(f"{page}: #{frag} not found in {rel}")
            fetched.add(target)
        # url(...) references inside the stylesheet
    css = os.path.join(ROOT, "assets", "style.css")
    for ref in re.findall(r"url\(['\"]?([^'\")]+)", open(css, encoding="utf-8").read()):
        if not ref.startswith(("data:", "http")):
            checked += 1
            if not os.path.isfile(os.path.join(ROOT, "assets", ref)):
                errors.append(f"assets/style.css: missing url({ref})")

    if base_http:
        for p in pages:
            fetched.add(page_url(p) if p != "404.html" else PREFIX + "404.html")
        for target in sorted(fetched):
            url = base_http.rstrip("/") + "/" + target[len(PREFIX):]
            try:
                code = urllib.request.urlopen(url, timeout=10).status
            except Exception as e:
                code = getattr(e, "code", str(e))
            if code != 200:
                errors.append(f"HTTP {code}: {url}")
        print(f"fetched {len(fetched)} URLs over HTTP")

    print(f"{len(pages)} pages, {checked} local links checked")
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
