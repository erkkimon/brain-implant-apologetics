#!/usr/bin/env python3
"""Build topic pages from the ApoWiki categories, and bind every article to them.

ApoWiki's editors spent 18 years sorting 471 articles into categories
(`[[Luokka:Henkilöt]]`, `[[Luokka:Filosofia]]`, …). The converter keeps those
as tags, but a tag is not an edge: brainpick's graph — and the contract's
grounding rule — run on links. So this tool turns each category into a topic
page that lists its articles, and adds a "Aihepiirit" line to each article
pointing back at the topics it belongs to.

Why that is worth doing rather than relaxing the rule:

* **Grounding.** 54 converted articles carry no internal link at all, and 23
  carry no citation either. A topic edge makes the weakest of them reachable
  and reachable-from, which is what makes an implant searchable rather than a
  pile of files.
* **Navigation.** "Which people does this wiki cover?" is a question the
  original wiki answered with a category page and the implant could not answer
  at all.
* **It is the book spine's shape.** The plan binds books to testaments the
  same way; topics are the same move for the apologetics half.

Idempotent: run it after every conversion. It only appends the topic line to
an article that lacks one.

Usage:
    python3 apowiki_topics.py [--articles _implant/knowledge/articles]
                              [--out _implant/knowledge/topics]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

# Categories that describe the WIKI's own bookkeeping rather than a subject.
# A topic page for "stubs" or "copyright-encumbered articles" is maintenance
# metadata, not knowledge, and would pull unrelated pages into one heap.
ADMIN_CATEGORIES = {
    "tyngät", "lukusuositukset", "tekijänoikeuden-alaiset-artikkelit",
    "tekijanoikeuden-alaiset-artikkelit", "yleistä-tietoa", "yleista-tietoa",
    "apowiki", "keskeneräiset", "poistettavat", "kategoriat",
}

TITLES = {
    "henkilöt": "Henkilöt",
    "filosofia": "Filosofia",
    "kirjat": "Kirjat",
    "suunnitteluteoria": "Suunnitteluteoria",
    "historia": "Historia",
    "eksegetiikka": "Eksegetiikka",
    "raamattu": "Raamattu",
    "maailmankatsomus": "Maailmankatsomus",
    "evoluutioteoria": "Evoluutioteoria",
    "seksuaalietiikka": "Seksuaalietiikka",
    "jumala": "Jumala",
    "ateismi": "Ateismi",
    "tieteenfilosofia": "Tieteenfilosofia",
    "jeesus": "Jeesus",
    "apologetiikka": "Apologetiikka",
    "etiikka": "Etiikka",
    "teologia": "Teologia",
    "muut": "Muut",
}


def frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.group(2)


def parse_tags(raw: str) -> list[str]:
    raw = raw.strip()
    if raw.startswith("["):
        raw = raw[1:-1] if raw.endswith("]") else raw[1:]
    return [t.strip() for t in raw.split(",") if t.strip()]


def unquote(s: str) -> str:
    s = s.strip()
    if s.startswith(('"', "'")) and s.endswith(('"', "'")) and len(s) > 1:
        try:
            return json.loads(s) if s.startswith('"') else s[1:-1]
        except json.JSONDecodeError:
            return s[1:-1]
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--articles", default="_implant/knowledge/articles")
    ap.add_argument("--out", default="_implant/knowledge/topics")
    ap.add_argument("--min-size", type=int, default=3,
                    help="a topic needs this many articles to earn a page")
    args = ap.parse_args()

    adir, odir = Path(args.articles), Path(args.out)
    odir.mkdir(parents=True, exist_ok=True)

    members: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    docs: dict[str, tuple[dict, str, Path]] = {}

    for f in sorted(adir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        fm, body = frontmatter(text)
        title = unquote(fm.get("title", f.stem))
        desc = unquote(fm.get("description", ""))
        docs[f.stem] = (fm, text, f)
        for tag in parse_tags(fm.get("tags", "")):
            if tag in ("apowiki",) or tag in ADMIN_CATEGORIES:
                continue
            members[tag].append((f.stem, title, desc))

    topics = {t: ms for t, ms in members.items() if len(ms) >= args.min_size}

    # An article whose every category fell below the threshold — or that the
    # wiki never categorised, or categorised only as admin/vandalism — would
    # otherwise stay unreachable: no topic, no inbound edge, invisible to the
    # graph. It goes to a catch-all topic instead, because "uncategorised" is
    # a true statement about the source wiki and a findable page beats a
    # dangling file.
    placed = {stem for ms in topics.values() for stem, _, _ in ms}
    leftovers = [(s, unquote(fm.get("title", s)), unquote(fm.get("description", "")))
                 for s, (fm, _, _) in sorted(docs.items()) if s not in placed]
    if leftovers:
        topics["muut"] = leftovers

    # Every article gets an "Aihepiirit" line naming the topic pages it is on.
    # Prefer the biggest topics an article belongs to, so the line stays short.
    article_topics: dict[str, list[str]] = defaultdict(list)
    for t, ms in topics.items():
        for stem, _, _ in ms:
            article_topics[stem].append(t)
    for stem in article_topics:
        article_topics[stem].sort(key=lambda t: (-len(topics[t]), t))

    patched = 0
    for stem, ts in article_topics.items():
        fm, text, path = docs[stem]
        if "*Aihepiirit:" in text:
            continue
        links = ", ".join(
            f"[{TITLES.get(t, t.replace('-', ' ').capitalize())}]"
            f"(../topics/{t}.md)" for t in ts[:4])
        line = f"\n*Aihepiirit: {links}.*\n"
        # Insert right after the article's h1 so it reads as a breadcrumb.
        m = re.search(r"^(# .+)$", text, re.M)
        if m:
            text = text[:m.end()] + "\n" + line + text[m.end():]
        else:
            text = text.rstrip() + "\n" + line
        path.write_text(text, encoding="utf-8")
        patched += 1

    for t, ms in sorted(topics.items()):
        nice = TITLES.get(t, t.replace("-", " ").capitalize())
        ms_sorted = sorted(ms, key=lambda x: x[1].lower())
        lines = []
        for stem, title, desc in ms_sorted:
            short = desc.split(". ")[0].rstrip(".")
            if len(short) > 150:
                short = short[:150].rsplit(" ", 1)[0] + "…"
            lines.append(f"* [{title}](../articles/{stem}.md)"
                         + (f" — {short}." if short else ""))
        desc = (f"{len(ms_sorted)} ApoWiki-artikkelia aihepiiristä "
                f"{nice.lower()} — jokainen linkitetty tähän sivuun, "
                f"niin että aihepiiri on selattavissa kokonaisuutena.")
        doc = "\n".join([
            "---",
            "type: article",
            "about: apologetics",
            f"title: {json.dumps(nice, ensure_ascii=False)}",
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            f"tags: [apowiki, aihepiiri, {t}]",
            "timestamp: 2026-09-25T23:30:00Z",
            "---",
            "",
            f"# {nice}",
            "",
            f"Aihepiirin {nice.lower()} artikkelit, tuotu "
            "[ApoWikistä](https://apowiki.fi). Luettelo on koostettu "
            "artikkelien luokista, jotka ApoWikin toimittajat ovat "
            "valinneet; se on siis wikin oma jäsennys, ei tämän implantin "
            "tulkinta. Katso myös [aihepiirien luettelo](index.md).",
            "",
            f"## Artikkelit ({len(ms_sorted)})",
            "",
            *lines,
            "",
        ])
        (odir / f"{t}.md").write_text(doc, encoding="utf-8")

    index = "\n".join([
        "# Aihepiirit",
        "",
        "ApoWikin luokista koostetut aihepiirisivut. Kukin listaa oman "
        "alansa artikkelit, ja kukin artikkeli linkittää takaisin "
        "aihepiireihinsä, joten kokoelmaa voi selata kumpaankin suuntaan.",
        "",
        *[f"* [{TITLES.get(t, t.replace('-', ' ').capitalize())}]({t}.md) — "
          f"{len(ms)} artikkelia."
          for t, ms in sorted(topics.items(), key=lambda kv: -len(kv[1]))],
        "",
    ])
    (odir / "index.md").write_text(index, encoding="utf-8")

    print(f"topic pages: {len(topics)} (min {args.min_size} articles each)")
    print(f"articles given an Aihepiirit line: {patched}")
    skipped = sorted(set(members) - set(topics))
    if skipped:
        print(f"below threshold, no page: {len(skipped)} "
              f"({', '.join(skipped[:8])}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
