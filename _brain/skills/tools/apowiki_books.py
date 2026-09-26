#!/usr/bin/env python3
"""Generate the book spine: one page per biblical book, bound to its testament
here and to the matching book page in the theology implant.

The spine is owned by the theology implant (its `skills/tools/bookcodes.py`
is the canonical list, and its chapters hang off its book pages). This brain
does not copy that spine; it mirrors only the rungs — 66 Finnish book pages
and two testament pages — so that Finnish articles have somewhere to land, and
each rung points across the federation boundary at the page that owns it.

The cross-brain pointer is written as an autolink,
`<brain://theology-<id>/knowledge/scripture/gen/gen.md>`. That form matters:
brainpick 0.8.6 finds it when it builds `brain_read` annotations (so reading a
theology book page surfaces this brain's page about it), while neither
brainpick's ghost detection nor the henxels link checks treat it as a local
file — a markdown `[x](brain://…)` link would be reported dead by henxels.

The OSIS codes and chapter counts below MUST match the theology implant's
bookcodes.py; a code is a permanent address there (it is the first component
of every verse token). The Finnish names follow the 1992 church translation.

Usage:
    python3 apowiki_books.py [--out _brain/knowledge/books]
                             [--articles _brain/knowledge/articles]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

THEOLOGY = "brain://theology-n4d79bfxkjv1ysobi5g7fu"
TIMESTAMP = "2026-09-26T00:30:00Z"
KR92 = "https://raamattu.fi/"

# code, Finnish name, testament, division (Finnish), chapters, extra aliases.
# The numbered-book convention "1. Mooseksen kirja" also appears spelled out
# ("Ensimmäinen Mooseksen kirja") in ApoWiki links; aliases are generated for
# that below, so only irregular aliases are listed here.
BOOKS = [
    ("gen", "1. Mooseksen kirja", "ot", "Toora", 50, ["Genesis"]),
    ("exo", "2. Mooseksen kirja", "ot", "Toora", 40, ["Exodus"]),
    ("lev", "3. Mooseksen kirja", "ot", "Toora", 27, ["Leviticus"]),
    ("num", "4. Mooseksen kirja", "ot", "Toora", 36, ["Numeri"]),
    ("deu", "5. Mooseksen kirja", "ot", "Toora", 34, ["Deuteronomium"]),
    ("jos", "Joosuan kirja", "ot", "Historialliset kirjat", 24, []),
    ("jdg", "Tuomarien kirja", "ot", "Historialliset kirjat", 21, []),
    ("rut", "Ruutin kirja", "ot", "Historialliset kirjat", 4, []),
    ("1sa", "1. Samuelin kirja", "ot", "Historialliset kirjat", 31, []),
    ("2sa", "2. Samuelin kirja", "ot", "Historialliset kirjat", 24, []),
    ("1ki", "1. Kuninkaiden kirja", "ot", "Historialliset kirjat", 22, []),
    ("2ki", "2. Kuninkaiden kirja", "ot", "Historialliset kirjat", 25, []),
    ("1ch", "1. aikakirja", "ot", "Historialliset kirjat", 29, []),
    ("2ch", "2. aikakirja", "ot", "Historialliset kirjat", 36, []),
    ("ezr", "Esran kirja", "ot", "Historialliset kirjat", 10, []),
    ("neh", "Nehemian kirja", "ot", "Historialliset kirjat", 13, []),
    ("est", "Esterin kirja", "ot", "Historialliset kirjat", 10, []),
    ("job", "Jobin kirja", "ot", "Viisauskirjallisuus", 42, []),
    ("psa", "Psalmit", "ot", "Viisauskirjallisuus", 150, ["Psalmien kirja"]),
    ("pro", "Sananlaskujen kirja", "ot", "Viisauskirjallisuus", 31, ["Sananlaskut"]),
    ("ecc", "Saarnaaja", "ot", "Viisauskirjallisuus", 12, ["Saarnaajan kirja"]),
    ("sng", "Laulujen laulu", "ot", "Viisauskirjallisuus", 8, []),
    ("isa", "Jesajan kirja", "ot", "Suuret profeetat", 66, ["Jesaja"]),
    ("jer", "Jeremian kirja", "ot", "Suuret profeetat", 52, ["Jeremia"]),
    ("lam", "Valitusvirret", "ot", "Suuret profeetat", 5, []),
    ("ezk", "Hesekielin kirja", "ot", "Suuret profeetat", 48, ["Hesekiel"]),
    ("dan", "Danielin kirja", "ot", "Suuret profeetat", 12, []),
    ("hos", "Hoosea", "ot", "Pienet profeetat", 14, ["Hoosean kirja"]),
    ("jol", "Joel", "ot", "Pienet profeetat", 3, ["Joelin kirja"]),
    ("amo", "Aamos", "ot", "Pienet profeetat", 9, ["Aamoksen kirja"]),
    ("oba", "Obadja", "ot", "Pienet profeetat", 1, ["Obadjan kirja"]),
    ("jon", "Joona", "ot", "Pienet profeetat", 4, ["Joonan kirja"]),
    ("mic", "Miika", "ot", "Pienet profeetat", 7, ["Miikan kirja"]),
    ("nam", "Nahum", "ot", "Pienet profeetat", 3, ["Nahumin kirja"]),
    ("hab", "Habakuk", "ot", "Pienet profeetat", 3, ["Habakukin kirja"]),
    ("zep", "Sefanja", "ot", "Pienet profeetat", 3, ["Sefanjan kirja"]),
    ("hag", "Haggai", "ot", "Pienet profeetat", 2, ["Haggain kirja"]),
    ("zec", "Sakarja", "ot", "Pienet profeetat", 14, ["Sakarjan kirja"]),
    ("mal", "Malakia", "ot", "Pienet profeetat", 4, ["Malakian kirja"]),
    ("mat", "Matteuksen evankeliumi", "nt", "Evankeliumit", 28,
     ["Evankeliumi Matteuksen mukaan"]),
    ("mrk", "Markuksen evankeliumi", "nt", "Evankeliumit", 16,
     ["Evankeliumi Markuksen mukaan"]),
    ("luk", "Luukkaan evankeliumi", "nt", "Evankeliumit", 24,
     ["Evankeliumi Luukkaan mukaan"]),
    ("jhn", "Johanneksen evankeliumi", "nt", "Evankeliumit", 21,
     ["Evankeliumi Johanneksen mukaan"]),
    ("act", "Apostolien teot", "nt", "Historia", 28, []),
    ("rom", "Kirje roomalaisille", "nt", "Paavalin kirjeet", 16, ["Roomalaiskirje"]),
    ("1co", "1. kirje korinttilaisille", "nt", "Paavalin kirjeet", 16, []),
    ("2co", "2. kirje korinttilaisille", "nt", "Paavalin kirjeet", 13, []),
    ("gal", "Kirje galatalaisille", "nt", "Paavalin kirjeet", 6, ["Galatalaiskirje"]),
    ("eph", "Kirje efesolaisille", "nt", "Paavalin kirjeet", 6, ["Efesolaiskirje"]),
    ("php", "Kirje filippiläisille", "nt", "Paavalin kirjeet", 4, ["Filippiläiskirje"]),
    ("col", "Kirje kolossalaisille", "nt", "Paavalin kirjeet", 4, ["Kolossalaiskirje"]),
    ("1th", "1. kirje tessalonikalaisille", "nt", "Paavalin kirjeet", 5, []),
    ("2th", "2. kirje tessalonikalaisille", "nt", "Paavalin kirjeet", 3, []),
    ("1ti", "1. kirje Timoteukselle", "nt", "Pastoraalikirjeet", 6, []),
    ("2ti", "2. kirje Timoteukselle", "nt", "Pastoraalikirjeet", 4, []),
    ("tit", "Kirje Titukselle", "nt", "Pastoraalikirjeet", 3, []),
    ("phm", "Kirje Filemonille", "nt", "Paavalin kirjeet", 1, []),
    ("heb", "Kirje heprealaisille", "nt", "Yleiset kirjeet", 13, ["Heprealaiskirje"]),
    ("jas", "Jaakobin kirje", "nt", "Yleiset kirjeet", 5, []),
    ("1pe", "1. Pietarin kirje", "nt", "Yleiset kirjeet", 5, []),
    ("2pe", "2. Pietarin kirje", "nt", "Yleiset kirjeet", 3, []),
    ("1jn", "1. Johanneksen kirje", "nt", "Yleiset kirjeet", 5, []),
    ("2jn", "2. Johanneksen kirje", "nt", "Yleiset kirjeet", 1, []),
    ("3jn", "3. Johanneksen kirje", "nt", "Yleiset kirjeet", 1, []),
    ("jud", "Juudaksen kirje", "nt", "Yleiset kirjeet", 1, []),
    ("rev", "Johanneksen ilmestys", "nt", "Apokalypsi", 22, ["Ilmestyskirja"]),
]

TESTAMENTS = {
    "ot": ("Vanha testamentti", ["Vanha testamentti (kirja)"],
           "Heprealaisen Raamatun 39 kirjaa luomiskertomuksesta profeettoihin."),
    "nt": ("Uusi testamentti", ["Uusi testamentti (kirja)"],
           "Apostolisen todistuksen 27 kirjaa: evankeliumit, Apostolien teot, "
           "kirjeet ja Johanneksen ilmestys."),
}

ORDINALS = {"1.": "Ensimmäinen", "2.": "Toinen", "3.": "Kolmas",
            "4.": "Neljäs", "5.": "Viides"}


def aliases_for(name: str, extra: list[str]) -> list[str]:
    out = [name, *extra]
    m = re.match(r"^([1-5]\.)\s+(.*)$", name)
    if m:
        spelled = f"{ORDINALS[m.group(1)]} {m.group(2)}"
        out.append(spelled)
        out.append(f"{m.group(1)[0]} {m.group(2)}")  # "1 Mooseksen kirja"
    return list(dict.fromkeys(out))


def alias_map() -> dict[str, str]:
    """Lower-cased title or alias -> page path relative to the bundle.

    The converter imports this to resolve wiki links that name a biblical book
    but had no ApoWiki article (e.g. `[[Matteuksen evankeliumi]]`), so they
    land on the spine instead of staying red.
    """
    out: dict[str, str] = {}
    for code, name, _, _, _, extra in BOOKS:
        for a in aliases_for(name, extra):
            out[a.lower()] = f"books/{code}.md"
    for code, (name, extra, _) in TESTAMENTS.items():
        for a in [name, *extra]:
            out[a.lower()] = f"books/{code}.md"
    return out


def _fm_title(text: str) -> str | None:
    m = re.search(r'^title:\s*(.+)$', text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    try:
        return json.loads(v) if v.startswith('"') else v
    except json.JSONDecodeError:
        return v.strip('"')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="_brain/knowledge/books")
    ap.add_argument("--articles", default="_brain/knowledge/articles")
    args = ap.parse_args()
    out, adir = Path(args.out), Path(args.articles)
    out.mkdir(parents=True, exist_ok=True)

    # ApoWiki's own article about a book, when it has one, is the richest
    # thing this brain knows about it: link it from the rung.
    article_by_title: dict[str, str] = {}
    for f in adir.glob("*.md"):
        t = _fm_title(f.read_text(encoding="utf-8"))
        if t:
            article_by_title[t.lower()] = f.stem

    for code, name, test, division, chapters, extra in BOOKS:
        tname = TESTAMENTS[test][0]
        own = next((article_by_title[a.lower()] for a in aliases_for(name, extra)
                    if a.lower() in article_by_title), None)
        desc = (f"{name}: {division.lower()}, {chapters} lukua — "
                f"{tname}n kirja raamatullisessa selkärangassa.")
        lines = [
            "---",
            "type: article",
            "about: scripture",
            f"title: {json.dumps(name, ensure_ascii=False)}",
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            f"book: {code}",
            f"testament: {test}",
            f"chapters: {chapters}",
            f"tags: [raamattu, kirja, {code}]",
            f"timestamp: {TIMESTAMP}",
            "half_life: 0",
            "---",
            "",
            f"# {name}",
            "",
            f"*{tname}* ([{tname}]({test}.md)) — {division}, {chapters} lukua. "
            f"Kirjan nimi on [vuoden 1992 kirkkoraamatun]({KR92}) mukainen.",
            "",
        ]
        if own:
            lines += [f"ApoWikin artikkeli kirjasta: [{name}](../articles/{own}.md).", ""]
            # And back: the article names its rung, so the spine is reachable
            # from the text as well as the text from the spine.
            af = adir / f"{own}.md"
            at = af.read_text(encoding="utf-8")
            if "Raamatullinen selkäranka:" not in at:
                m = re.search(r"^(# .+)$", at, re.M)
                crumb = (f"\n*Raamatullinen selkäranka: [{name}](../books/{code}.md), "
                         f"[{tname}](../books/{test}.md).*\n")
                if m:
                    af.write_text(at[:m.end()] + "\n" + crumb + at[m.end():],
                                  encoding="utf-8")
        lines += [
            "Luvut, jaetunnisteet ja kirjan teologinen käsittely ovat "
            "teologiaimplantissa, joka omistaa raamatullisen selkärangan "
            "(OSIS-koodi `" + code + "`):",
            "",
            f"<{THEOLOGY}/knowledge/scripture/{code}/{code}.md>",
            "",
            "Tämän implantin artikkelit, jotka viittaavat kirjaan, näkyvät "
            "sivun takaisinlinkeissä.",
            "",
        ]
        (out / f"{code}.md").write_text("\n".join(lines), encoding="utf-8")

    for test, (tname, _, blurb) in TESTAMENTS.items():
        members = [b for b in BOOKS if b[2] == test]
        body, last_div = [], None
        for code, name, _, division, chapters, _ in members:
            if division != last_div:
                body += ["", f"## {division}", ""]
                last_div = division
            body.append(f"* [{name}]({code}.md) — {chapters} lukua")
        desc = f"{tname}: {blurb}"
        doc = [
            "---",
            "type: article",
            "about: scripture",
            f"title: {json.dumps(tname, ensure_ascii=False)}",
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            f"testament: {test}",
            f"tags: [raamattu, testamentti, {test}]",
            f"timestamp: {TIMESTAMP}",
            "half_life: 0",
            "---",
            "",
            f"# {tname}",
            "",
            blurb + " Kirjojen järjestys ja jako noudattavat protestanttista "
            "kaanonia, kuten teologiaimplantin selkäranka:",
            "",
            f"<{THEOLOGY}/knowledge/scripture/{test}.md>",
            "",
            "Apokryfit eivät ole osa selkärankaa: ne ovat tavallisia "
            "artikkeleita, jotka linkittävät kanonisiin kirjoihin. "
            "Katso myös [kirjojen luettelo](index.md).",
            *body,
            "",
        ]
        (out / f"{test}.md").write_text("\n".join(doc), encoding="utf-8")

    index = [
        "# Raamatun kirjat",
        "",
        "Raamatullinen selkäranka tässä implantissa: jokainen kirja on oma "
        "sivunsa, ja kirjat kuuluvat testamentteihinsa. Selkärangan omistaa "
        "teologiaimplantti; nämä sivut ovat sen suomenkielisiä kiinnekohtia.",
        "",
        "* [Vanha testamentti](ot.md) — 39 kirjaa.",
        "* [Uusi testamentti](nt.md) — 27 kirjaa.",
        "",
    ]
    (out / "index.md").write_text("\n".join(index), encoding="utf-8")
    print(f"book pages: {len(BOOKS)}, testaments: {len(TESTAMENTS)}, "
          f"with an ApoWiki article: "
          f"{sum(1 for b in BOOKS if any(a.lower() in article_by_title for a in aliases_for(b[1], b[5])))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
