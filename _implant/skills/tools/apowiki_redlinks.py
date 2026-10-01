#!/usr/bin/env python3
"""Propose Finnish Wikipedia fallbacks for ApoWiki's red links.

A red link is a page ApoWiki's editors wanted but never wrote (Immanuel Kant,
Pyhä Henki, tieteenfilosofia …). The converter keeps it as plain text plus a
greppable `<!-- red link: … -->` comment. For a reader, and for an agent
following links, a page on the same subject in the Finnish Wikipedia is far
better than nothing, so this tool looks each red-link target up there and
writes the hits to `red-link-wikipedia.json` beside it. The converter then
links the label to Wikipedia **and keeps the red-link comment**, so the page
still counts as wanted in the report and in any grep.

The JSON is committed and reviewed by hand, not trusted blindly: a title can
exist in Wikipedia with another meaning (a person of the same name, a film).
Set an entry to null to keep a target red, and it stays null on re-runs.
Disambiguation pages are never proposed.

    python3 _implant/skills/tools/apowiki_redlinks.py            # update
    python3 _implant/skills/tools/apowiki_redlinks.py --report r.json

It reads the red links from the converter's report (run the converter first),
asks the Wikipedia API in batches of 50 with a pause between them, and leaves
existing decisions untouched.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = HERE / "red-link-wikipedia.json"
API = "https://fi.wikipedia.org/w/api.php"
UA = "brain-implant-apologetics/1.0 (red-link fallback lookup)"

# Targets that are not subjects at all: they stay red without asking.
NOT_A_SUBJECT = re.compile(r"^(?:user|käyttäjä|template|malline|special|toiminnot)\s*:",
                           re.I)


def clean(target: str) -> str:
    t = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", target)
    t = t.replace("_", " ").split("#", 1)[0].strip().lstrip(":").strip()
    return t[:1].upper() + t[1:]


def lookup(titles: list[str]) -> dict[str, str | None]:
    """Title -> Wikipedia page title (after redirects), or None."""
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": 1,
        "prop": "pageprops", "ppprop": "disambiguation",
        "titles": "|".join(titles)})
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 4:
                raise
            time.sleep(10 * (attempt + 1))
    query = d["query"]
    norm = {n["from"]: n["to"] for n in query.get("normalized", [])}
    redir = {n["from"]: n["to"] for n in query.get("redirects", [])}
    pages = {p["title"]: p for p in query["pages"].values()}
    out: dict[str, str | None] = {}
    for t in titles:
        x = norm.get(t, t)
        x = redir.get(x, x)
        p = pages.get(x)
        ok = (p is not None and "missing" not in p and "invalid" not in p
              and "disambiguation" not in p.get("pageprops", {}))
        out[t] = x if ok else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", default="_temp/convert-report.json")
    args = ap.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    wanted = [t for t, _ in report["red_links_all"]]
    current: dict[str, str | None] = (
        json.loads(MAP.read_text(encoding="utf-8")) if MAP.exists() else {})

    todo = sorted({t for t in wanted if t not in current
                   and not NOT_A_SUBJECT.match(t) and clean(t)})
    by_clean: dict[str, list[str]] = {}
    for t in todo:
        by_clean.setdefault(clean(t), []).append(t)
    keys = list(by_clean)
    for i in range(0, len(keys), 50):
        found = lookup(keys[i:i + 50])
        for k, v in found.items():
            for t in by_clean[k]:
                current[t] = v
        time.sleep(2)

    MAP.write_text(json.dumps(dict(sorted(current.items())), ensure_ascii=False,
                              indent=1) + "\n", encoding="utf-8")
    hits = sum(1 for t in wanted if current.get(t))
    print(f"red-link targets: {len(wanted)}, looked up now: {len(todo)}, "
          f"with a Wikipedia fallback: {hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
