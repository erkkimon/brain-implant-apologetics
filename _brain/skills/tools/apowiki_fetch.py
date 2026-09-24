#!/usr/bin/env python3
"""Fetch every ApoWiki article revision, oldest first, into a local cache.

Separated from the importer on purpose: fetching hits someone else's server
and must be polite and resumable, while importing is pure local computation
that can be re-run freely. Cache once, replay as often as the import needs
fixing.

Writes one JSON file per article into the cache directory, each holding the
full revision list with wikitext. Already-cached articles are skipped, so an
interrupted run resumes by simply running it again.

The wikitext is stored UNCONVERTED. It is what ApoWiki actually published,
byte for byte, and that is what makes the provenance claim defensible — see
_brain/raw/index.md.

Usage:
    python3 apowiki_fetch.py --cache _temp/apowiki-cache [--limit 5]
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://apowiki.fi/api.php"
UA = "brain-implant-apologetics/0.1 (faithful GFDL history import; contact via repository)"
# ApoWiki is a small volunteer wiki on modest hosting. Crawl gently.
DELAY = 0.4


def api(**params) -> dict:
    params.setdefault("format", "json")
    params.setdefault("action", "query")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)  # back off; the wiki may be rate limiting
    raise RuntimeError("unreachable")


def list_articles() -> list[dict]:
    """Mainspace articles only. Excludes the Metasivu: pseudo-namespace (template
    and infrastructure pages that live in ns0 by naming convention) and the
    front page, which an index-driven brain does not need."""
    pages, cont = [], {}
    while True:
        d = api(list="allpages", apnamespace=0, aplimit=500, **cont)
        pages += d["query"]["allpages"]
        if "continue" not in d:
            break
        cont = d["continue"]
        time.sleep(DELAY)
    return [p for p in pages
            if not p["title"].startswith("Metasivu:") and p["title"] != "Etusivu"]


def fetch_revisions(title: str) -> list[dict]:
    """Every revision of one article, OLDEST FIRST, with content.

    rvdir=newer is what makes the git replay natural: commits are created in
    the order the edits actually happened.
    """
    revs, cont = [], {}
    while True:
        d = api(prop="revisions", titles=title, rvdir="newer", rvlimit=50,
                rvprop="ids|timestamp|user|userid|comment|size|content",
                rvslots="main", **cont)
        page = next(iter(d["query"]["pages"].values()))
        if "revisions" not in page:
            break
        revs += page["revisions"]
        if "continue" not in d:
            break
        cont = d["continue"]
        time.sleep(DELAY)
    return revs


def safe_name(title: str) -> str:
    """A filesystem-safe cache key that still shows which article it is."""
    return urllib.parse.quote(title, safe="") + ".json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--limit", type=int, default=None, help="fetch only N articles (smoke test)")
    args = ap.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)

    articles = list_articles()
    if args.limit:
        articles = articles[:args.limit]
    print(f"{len(articles)} articles to consider", flush=True)

    fetched = cached = 0
    total_revs = 0
    for i, page in enumerate(articles, 1):
        target = args.cache / safe_name(page["title"])
        if target.exists():
            cached += 1
            total_revs += len(json.loads(target.read_text(encoding="utf-8"))["revisions"])
            continue
        revs = fetch_revisions(page["title"])
        target.write_text(json.dumps(
            {"title": page["title"], "pageid": page["pageid"], "revisions": revs},
            ensure_ascii=False), encoding="utf-8")
        fetched += 1
        total_revs += len(revs)
        if i % 25 == 0:
            print(f"  {i}/{len(articles)} — {total_revs} revisions so far", flush=True)
        time.sleep(DELAY)

    print(f"done: {fetched} fetched, {cached} already cached, {total_revs} revisions total",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
