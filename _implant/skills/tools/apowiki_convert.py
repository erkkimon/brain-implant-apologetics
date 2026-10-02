#!/usr/bin/env python3
"""Convert the ApoWiki wikitext export into implant articles — deterministically.

This is the machine-time half of the MVP (see plans/mvp-then-iteration.md):
no model is involved, so it costs hours of CPU rather than tokens, and it is
idempotent — run it as often as you like and the output is the same.

What it guarantees, because each is a rule the implant's contract enforces:

* **Links land.** Every `[[wiki link]]` is resolved through the SAME slug map
  the importer used, including its `-v2` collision disambiguation. A target
  that does not exist becomes a visible red link and is reported, never a
  silently plausible path.
* **Receipts survive.** The corpus is heavily cited (5 590 `<ref>` tags,
  1 365 `{{Kirjaviite}}` book citations). Structured citation templates are
  rendered as real footnotes with author, title, publisher, year, page and
  ISBN intact, because a claim without its receipt is worth less here than no
  claim at all.
* **Degradation is visible.** An unknown template is emitted as a fenced
  `wikitext` block, not dropped. A converter that silently discards content
  looks successful while destroying the archive; this one looks noisy instead.
* **Redirects are resolved, not imported.** The 374 redirect pages become
  entries in a redirect map used for link resolution; they do not become 374
  stub articles.

Usage:
    python3 apowiki_convert.py --export _implant/raw/apowiki-export \\
        --cache _temp/apowiki-cache --out _implant/knowledge/articles \\
        [--report _temp/convert-report.json] [--limit N]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import unicodedata
from collections import Counter
from pathlib import Path

try:  # the book spine's alias table; the converter works without it too
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from apowiki_books import alias_map as _book_alias_map
    from apowiki_books import ref_book as _ref_book
    BOOK_ALIASES = _book_alias_map()
except ImportError:  # pragma: no cover
    BOOK_ALIASES = {}

    def _ref_book(ref: str) -> None:
        return None

# The glossary's anchors (apowiki_glossary.py), so AW:S#term links land.
from apowiki_glossary import anchor as glossary_anchor  # noqa: E402
from apowiki_glossary import entries as _glossary_entries  # noqa: E402
from apowiki_glossary import source as _glossary_source  # noqa: E402
try:
    GLOSSARY_TERMS = {glossary_anchor(t) for t, _ in
                      _glossary_entries(_glossary_source()[0])}
except FileNotFoundError:  # glossary not generated yet
    GLOSSARY_TERMS = set()

# Glossary links (AW:S#term) to terms ApoWiki's glossary does not define:
# 41 distinct in revision 11402. Each was decided by hand on 2026-10-01
# against three candidates, in this order: a near-variant the glossary does
# define ("glossary:<term>"), an ApoWiki article ("article:<stem>"), or a
# Finnish Wikipedia page that is about the term in the sense used
# ("wp:<title>", checked to exist and not to be a disambiguation page). A term
# mapped to None has no fitting target and becomes plain text, because a link
# to the top of a 400-term glossary tells the reader nothing.
GLOSSARY_FALLBACKS: dict[str, str | None] = {
    # Two more surfaced on 2026-10-02, once quotes stopped swallowing links:
    "eksistentaalinen": "glossary:eksistenssi",  # misspelt adjective
    "likvidoida": None,  # Stalin's purges; no glossary or wiki sense fits
    "usko": "wp:Usko",
    "looginen": "wp:Logiikka",
    "idealismi": "wp:Idealismi",
    "argumentoida": "glossary:argumentointi",
    "nollahypoteesi": "wp:Nollahypoteesi",
    "kanoniset evankeliumit": "article:evankeliumit",
    "monoteismi": "wp:Monoteismi",
    "aktuaalisesti": "glossary:aktuaalinen",
    "konservatiivinen": None,
    "leegio": None,
    "teologinen": "wp:Teologia",
    "traditio": "wp:Perinne",
    "kompromettoida": None,
    "potentiaali": "glossary:potentiaalinen",
    "visuaalinen": None,
    "kvantitatiivinen": None,
    "ontologinen": "glossary:ontologia",
    "skeptinen": "glossary:skeptisismi",
    "karikatyyri": "wp:Karikatyyri",
    "evolutionisti": "article:evoluutioteoria",
    "darvinisti": "wp:Darvinismi",
    "messias": "wp:Messias",
    "teoreettinen": None,
    "dimensio": "wp:Ulottuvuus",
    "luonnonlaki": "article:luonnonlaki",
    "attribuutti": None,
    "hermeneutiikka": "article:hermeneutiikka",
    "syklinen": None,
    "itseisarvo": "wp:Itseisarvo",
    "praktiikka": None,
    "riivaustila": "wp:Riivaus",
    "homologinen": "glossary:homologia",
    "teisti": "article:teismi",
    "morfologia": "wp:Morfologia (biologia)",
    "embryologia": "wp:Embryologia",
    "suunnittelija": "glossary:suunnittelu",
    "falsifioitavuus": "glossary:falsifikaatio",
    "identifioida": None,
    "väitelause": "glossary:propositio",
    "unitarismi": "wp:Unitarismi",
    "trinitarismi": "wp:Kolminaisuusoppi",
}


# Pages written for this implant (knowledge/pages/) answer red links: each
# lists the titles it stands for in `aliases:` frontmatter. ApoWiki never had
# these pages, so the converter links to them instead of leaving the red link.
_PAGES = Path(__file__).resolve().parents[2] / "knowledge" / "pages"


def _written_pages() -> dict[str, str]:
    out: dict[str, str] = {}
    for f in sorted(_PAGES.glob("*.md")) if _PAGES.exists() else []:
        if f.name == "index.md":
            continue
        head = f.read_text(encoding="utf-8").split("\n---", 1)[0]
        names = re.findall(r'^title:\s*"?([^"\n]+)"?\s*$', head, re.M)
        m = re.search(r"^aliases:\s*\[(.*)\]\s*$", head, re.M)
        if m:
            # Quoted items may themselves hold commas ("Dawkinsin jumala:
            # Geenit, meemit ja elämän tarkoitus"), so split on the quotes.
            names += re.findall(r'"([^"]*)"', m.group(1)) or [
                a.strip() for a in m.group(1).split(",")]
        for n in names:
            out[n.strip().lower()] = f.stem
    return out


WRITTEN_PAGES = _written_pages()


def wiki_url(lang: str, title: str) -> str:
    """A Wikipedia URL for a title. A literal "?" would start the query
    string ("Mihin uskot jos et usko?" opened the page without its question
    mark), and "#" or "%" would misparse too, so those three are encoded;
    the rest stays readable."""
    t = title.strip().replace(" ", "_")
    t = t.replace("%", "%25").replace("?", "%3F")
    page, _, frag = t.partition("#")
    return f"https://{lang}.wikipedia.org/wiki/{page}" + (f"#{frag}" if frag else "")

# Interwiki links whose Wikipedia page is a different concept that merely
# shares the name. ApoWiki's [[wp:perusryhmä]] means the creationist
# taxonomic unit (baramin), but Finnish Wikipedia's "Perusryhmä" is the
# fundamental group of algebraic topology. Each entry is listed by hand,
# verified against the article lead, and points at a page written here
# ("pages/x") or at the right Wikipedia title ("wp:Title").
WRONG_CONCEPT_INTERWIKI = {
    "perusryhmä": "pages/perusryhmä",
}

# Red links that are only misspellings of an article ApoWiki has. A typo is
# an editorial fix, so each one is listed here by hand rather than guessed
# by fuzzy matching (which would pair "homologia-argumentti" with
# "kosmologinen-argumentti"). Raw wikitext keeps the original spelling.
RED_LINK_TYPOS = {
    "kosminen hienösäätö": "kosminen hienosäätö",  # jumalharha-kirja
}

# A wikitext bullet, tagged before inline markup runs (see convert()).
BULLET = "\x02"
BULLET_RE = r"^(\x02+)[ \t]*(.*)$"

# Red-link targets with a reviewed Finnish Wikipedia page (apowiki_redlinks.py).
_RLW = Path(__file__).resolve().parent / "red-link-wikipedia.json"
RED_LINK_WIKIPEDIA: dict[str, str | None] = (
    json.loads(_RLW.read_text(encoding="utf-8")) if _RLW.exists() else {})
# Second choice: the English Wikipedia, for targets the Finnish one lacks
# (apowiki_redlinks.py --lang en). Many red links name English-language
# scholars and books, which only English Wikipedia covers.
_RLW_EN = Path(__file__).resolve().parent / "red-link-wikipedia-en.json"
RED_LINK_WIKIPEDIA_EN: dict[str, str | None] = (
    json.loads(_RLW_EN.read_text(encoding="utf-8")) if _RLW_EN.exists() else {})

# ---------------------------------------------------------------------------
# Slug — byte-identical to apowiki_import.slug(). Do not "improve" it here:
# the two must agree or the links this tool writes will not match the files
# the importer named.
# ---------------------------------------------------------------------------


def slug(title: str) -> str:
    out = []
    for ch in title.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " _-/":
            out.append("-")
    s = "".join(out)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-") or "untitled"


def resolve_filenames(titles: list[str]) -> dict[str, str]:
    """Title -> unique stem, with the importer's sorted `-vN` disambiguation."""
    groups: dict[str, list[str]] = {}
    for t in sorted(titles):
        groups.setdefault(slug(t), []).append(t)
    names: dict[str, str] = {}
    for base, group in groups.items():
        if len(group) == 1:
            names[group[0]] = base
        else:
            for i, t in enumerate(group):
                names[t] = base if i == 0 else f"{base}-v{i + 1}"
    return names


# ---------------------------------------------------------------------------
# Citation templates -> footnote text
# ---------------------------------------------------------------------------

def _split_top(body: str) -> list[str]:
    """Split a template body on the pipes that are not inside [[...]] or
    {{...}}: the pipe in [[target|label]] is the link's, not the template's."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            # max(): a stray "]" in the source must not hide every later
            # pipe (messias-ennustukset has "{{rp|Sak. 9:9}}]").
            depth = max(0, depth - 1)
        if ch == "|" and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def _fields(body: str) -> dict[str, str]:
    """Parse `| Key = Value` pairs, respecting nested braces and brackets."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        if ch == "|" and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    out: dict[str, str] = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k.strip().lower()] = v.strip()
        elif p.strip():
            out.setdefault("_positional", p.strip())
    return out


def _strip_comments(s: str) -> str:
    return re.sub(r"<!--.*?-->", "", s, flags=re.S).strip()


def fmt_kirjaviite(f: dict[str, str]) -> str:
    """A book citation. Fields are Finnish; the output is a plain reference."""
    bits = []
    if f.get("tekijä"):
        bits.append(f["tekijä"])
    if f.get("nimeke"):
        bits.append(f"*{f['nimeke']}*")
    if f.get("selite"):
        bits.append(f["selite"])
    if f.get("julkaisija"):
        bits.append(f["julkaisija"])
    if f.get("vuosi"):
        bits.append(f["vuosi"])
    if f.get("sivu"):
        bits.append(f"s. {f['sivu']}")
    if f.get("tunniste"):
        bits.append(f["tunniste"])
    return ", ".join(b for b in bits if b)


def fmt_verkkoviite(f: dict[str, str]) -> str:
    """A web citation. The URL is often commented out in the source; keep the
    reference readable either way rather than emitting a broken link."""
    url = _strip_comments(f.get("osoite", ""))
    label = f.get("nimeke") or url or "verkkolähde"
    bits = []
    if f.get("tekijä"):
        bits.append(f["tekijä"])
    bits.append(f"[{label}]({url})" if url.startswith("http") else f"*{label}*")
    for key in ("julkaisija", "ajankohta", "selite"):
        if f.get(key):
            bits.append(f[key])
    if f.get("viitattu"):
        bits.append(f"viitattu {f['viitattu']}")
    return ", ".join(bits)


def fmt_lehtiviite(f: dict[str, str]) -> str:
    bits = []
    for key in ("tekijä", "otsikko", "nimeke"):
        if f.get(key):
            bits.append(f["tekijä"] if key == "tekijä" else f"*{f[key]}*")
    for key in ("lehti", "julkaisu", "vuosi", "numero", "sivut", "sivu"):
        if f.get(key):
            bits.append(f[key])
    return ", ".join(bits)


CITATION_FORMATTERS = {
    "kirjaviite": fmt_kirjaviite,
    "cite book": fmt_kirjaviite,
    "verkkoviite": fmt_verkkoviite,
    "cite web": fmt_verkkoviite,
    "lehtiviite": fmt_lehtiviite,
    "cite journal": fmt_lehtiviite,
}

# Templates that carry no content worth keeping (layout and navigation cruft).
DROP_TEMPLATES = {"hl2", "viestipohja", "kirja-päivitys", ",", "clear", "-"}



def _close_open_quotes(text: str) -> str:
    """Close a {{sitaatti|… that never gets its "}}" at the end of its
    paragraph. Only an unclosed template is touched: a quote that spans
    blank lines and closes later (bayesin-teoreema) is left alone."""
    starts = list(re.finditer(
        r"\{\{\s*(sitaatti\d?|lainaus|quotation|cquote)\s*\|", text, re.I))
    for m in reversed(starts):
        depth, k = 0, m.start()
        while k < len(text) - 1:
            two = text[k:k + 2]
            if two == "{{":
                depth += 1
                k += 2
                continue
            if two == "}}":
                depth -= 1
                k += 2
                if depth == 0:
                    break
                continue
            k += 1
        if depth > 0:
            end = re.compile(r"\n\s*\n").search(text, m.start())
            cut = end.start() if end else len(text)
            text = text[:cut] + "}}" + text[cut:]
    return text

class Converter:
    def __init__(self, stems: dict[str, str], redirects: dict[str, str]):
        self.stems = stems           # title -> stem
        self.redirects = redirects   # title -> target title
        # Case-insensitive fallback lookup, since wiki links vary in case.
        # Where two titles differ only in case, the article wins over the
        # redirect, so the fallback never lands on a redirect loop.
        self.by_lower = {}
        for t in sorted(stems, key=lambda t: t in redirects):
            self.by_lower.setdefault(t.lower(), t)
        self.stats = Counter()
        self.red_links: Counter = Counter()
        self.unknown_templates: Counter = Counter()
        self.pending_keywords: list[str] = []
        self.missing_project_pages: Counter = Counter()
        self.missing_glossary_terms: Counter = Counter()

    # -- link resolution ---------------------------------------------------

    def resolve_title(self, target: str) -> str | None:
        """Follow redirects to a title that has an article, or None."""
        seen = set()
        # MediaWiki decodes character entities in a title, so
        # "Evoluutio &ndash; kriittinen analyysi (kirja)" (evoluution-
        # määritelmä) named the same page as the one with a literal dash.
        cur = html.unescape(target)
        for _ in range(10):
            # Strip the invisible marks that pasted titles carry (U+200E LRM
            # and friends), and treat underscores as spaces, as MediaWiki does.
            cur = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "",
                         cur).replace("_", " ").strip()
            # MediaWiki also collapses runs of whitespace in a title, so
            # "World Without Design  (kirja)" was a working link on ApoWiki.
            cur = re.sub(r"\s+", " ", cur)
            if cur.startswith(":"):
                cur = cur[1:].strip()
            cur = cur.split("#", 1)[0].strip()
            if not cur or cur in seen:
                return None
            seen.add(cur)
            # MediaWiki titles are case-sensitive except for the first letter,
            # so an exact match comes first. Lower-casing first lets a redirect
            # such as "Michael behe" -> "Michael Behe" shadow the article it
            # points at, and the article then reads as a red link (it did, for
            # 30 links, until 2026-10-01).
            real = cur if cur in self.stems else None
            if real is None:
                up = cur[0].upper() + cur[1:]
                real = up if up in self.stems else None
            if real is None:
                real = self.by_lower.get(cur.lower())
            if real is None:
                return None
            if real in self.redirects:
                cur = self.redirects[real]
                continue
            return real
        return None

    def link(self, target: str, label: str | None = None) -> str:
        target = target.strip()
        label = (label or target).strip()
        if not target:
            return label
        if "%" in target:
            # A percent-encoded title pasted from a URL
            # ("Matti_V%C3%A4is%C3%A4nen:_Mit%C3%A4_Suomeen_kuuluu%3F" in
            # kiila-strategia) names the same page as its decoded form.
            target = urllib.parse.unquote(target).replace("_", " ")

        # ApoWiki's glossary (ApoWiki:Sanasto, shortcut AW:S). There are 415
        # of these links, and they land on the glossary page that
        # apowiki_glossary.py generates, at the term's anchor. A term the
        # glossary does not define lands on the page itself, not on a dead
        # anchor.
        m = re.match(r"^(?:aw:s|apowiki:sanasto)\s*(?:#(.*))?$", target, re.I)
        if m:
            frag = (m.group(1) or "").strip()
            a = glossary_anchor(frag) if frag else ""
            self.stats["link_glossary"] += 1
            if a and a not in GLOSSARY_TERMS:
                self.stats["link_glossary_term_missing"] += 1
                key = frag.lower()
                if key not in GLOSSARY_FALLBACKS:
                    # Undecided: report it, and land on the page itself.
                    self.missing_glossary_terms[frag] += 1
                    a = ""
                else:
                    fb = GLOSSARY_FALLBACKS[key]
                    kind, _, val = (fb or "").partition(":")
                    if kind == "glossary":
                        a = glossary_anchor(val)
                    elif kind == "article":
                        self.stats["link_glossary_fallback"] += 1
                        return f"[{label}]({val}.md)"
                    elif kind == "wp":
                        self.stats["link_glossary_fallback"] += 1
                        url = wiki_url("fi", val)
                        return f"[{label}]({url})"
                    else:
                        self.stats["link_glossary_plain"] += 1
                        return label
            href = "../glossary/sanasto.md" + (f"#{a}" if a else "")
            return f"[{label}]({href})"

        # The rest of ApoWiki's project namespace (help, FAQ, talk pages) was
        # never fetched. Those pages are genuinely absent from this export, so
        # record the gap and keep the prose readable instead of emitting a
        # link that cannot land.
        if re.match(r"^(aw|apowiki|ohje|help|project|keskustelu|talk)\s*:",
                    target, re.I):
            self.stats["link_project_ns_missing"] += 1
            self.missing_project_pages[target.split("#", 1)[0].strip()] += 1
            return label

        # Interwiki: Finnish Wikipedia.
        if target.lower().startswith(("wp:", "w:")):
            page = target.split(":", 1)[1].strip()
            wrong = WRONG_CONCEPT_INTERWIKI.get(page.lower())
            if wrong:
                self.stats["link_wikipedia_wrong_concept"] += 1
                if wrong.startswith("wp:"):
                    return f"[{label}]({wiki_url('fi', wrong[3:])})"
                return f"[{label}](../{wrong}.md)"
            url = wiki_url("fi", page)
            self.stats["link_wikipedia"] += 1
            return f"[{label}]({url})"

        # Images and files: no media is exported, so name them in italics
        # rather than emit a link to a file that is not here.
        if target.split(":", 1)[0].strip().lower() in (
                "kuva", "tiedosto", "file", "image"):
            self.stats["link_media_dropped"] += 1
            return ""

        # Categories are handled separately (they become tags).
        if target.lower().startswith(("luokka:", "category:")):
            return ""

        real = self.resolve_title(target)
        if real is None and not target.strip().endswith("(kirja)"):
            # ApoWiki names its book articles "Title (kirja)" but often links
            # the bare title: "Sukupuoli muutoksessa" was red in Puolimatka's
            # bibliography while its article existed (until 2026-10-02).
            real = self.resolve_title(target.strip() + " (kirja)")
            if real is not None:
                self.stats["link_book_suffix"] += 1
        if real is None and target.strip() in RED_LINK_TYPOS:
            real = self.resolve_title(RED_LINK_TYPOS[target.strip()])
            if real is not None:
                self.stats["link_typo_fixed"] += 1
        if real is None:
            # A biblical book the wiki never wrote an article for still has a
            # page: the book spine (apowiki_books.py). Land the link there
            # rather than leave the most-cited texts in the corpus red.
            book = BOOK_ALIASES.get(target.replace("_", " ").strip().lower())
            if book:
                self.stats["link_book_spine"] += 1
                return f"[{label}](../{book})"
            page = WRITTEN_PAGES.get(
                target.replace("_", " ").strip().lower())
            if page:
                self.stats["link_written_page"] += 1
                return f"[{label}](../pages/{page}.md)"
            self.red_links[target] += 1
            self.stats["link_red"] += 1
            # A red link that still reads as prose, and is greppable. Where
            # the Finnish Wikipedia has a page on the subject (reviewed in
            # red-link-wikipedia.json, see apowiki_redlinks.py) the label links
            # there, and the comment stays: the page is still wanted here.
            # ApoWiki's own glossary comes before Wikipedia: it defines the
            # term in the sense the wiki uses it (perususkomus is Plantinga's
            # properly basic belief there, not the Wikipedia article's).
            g = glossary_anchor(target.replace("_", " ").strip())
            if g in GLOSSARY_TERMS:
                self.stats["link_red_to_glossary"] += 1
                return (f"[{label}](../glossary/sanasto.md#{g}) "
                        f"<!-- red link: {target} -->")
            wp = RED_LINK_WIKIPEDIA.get(target)
            if wp:
                self.stats["link_red_to_wikipedia"] += 1
                url = wiki_url("fi", wp)
                return f"[{label}]({url}) <!-- red link: {target} -->"
            wp = RED_LINK_WIKIPEDIA_EN.get(target)
            if wp:
                self.stats["link_red_to_wikipedia_en"] += 1
                url = wiki_url("en", wp)
                return f"[{label}]({url}) <!-- red link: {target} -->"
            return f"{label} <!-- red link: {target} -->"
        self.stats["link_internal"] += 1
        return f"[{label}]({self.stems[real]}.md)"

    # -- template expansion ------------------------------------------------

    def expand_templates(self, text: str) -> str:
        """Replace {{...}} innermost-first so nesting resolves correctly."""
        # TeX braces inside <math> are not template braces: "\\frac{1}{2}}"
        # kept a quote around a formula from ever matching (bayesin-teoreema
        # until 2026-10-02). Mask the formulas, restore them afterwards.
        maths: list[str] = []

        def _mask(m: re.Match) -> str:
            maths.append(m.group(0))
            return f"\x00MATH{len(maths) - 1}\x00"

        text = re.sub(r"<math>.*?</math>", _mask, text, flags=re.S)
        pattern = re.compile(r"\{\{([^{}]*)\}\}", re.S)
        for _ in range(12):
            new = pattern.sub(self._one_template, text)
            if new == text:
                break
            text = new
        return re.sub(r"\x00MATH(\d+)\x00", lambda m: maths[int(m.group(1))], text)

    def _one_template(self, m: re.Match) -> str:
        raw = m.group(1)
        name = raw.split("|", 1)[0].strip().lower()
        # "{{Malline:quotation|…}}" names the template with its namespace
        # (bayesin-teoreema); MediaWiki treats it as plain "quotation".
        name = re.sub(r"^(malline|template):\s*", "", name)
        f = _fields(raw)
        pos = f.get("_positional", "")

        if name in CITATION_FORMATTERS:
            self.stats[f"tmpl_{name}"] += 1
            return CITATION_FORMATTERS[name](f)
        if name in DROP_TEMPLATES:
            self.stats["tmpl_dropped"] += 1
            return ""
        if name.startswith("viitteet") or name == "reflist":
            self.stats["tmpl_reflist"] += 1
            # A placeholder, not the heading itself: blocks() runs later and
            # reads a line starting "## " as a numbered list item (wikitext
            # "#"), which turned this heading into "1. Viitteet" in 350
            # articles until 2026-10-01.
            return "\n\n<!-- footnotes render here -->\n"
        if name == "rp":
            # An inline scripture reference ("Matt. 5:32"). It links to the
            # book's page on the spine, which binds it to the theology
            # implant's chapters and makes every article that cites a book
            # a backlink of that book. Anything the resolver does not
            # recognise stays plain text.
            self.stats["tmpl_rp"] += 1
            if not pos:
                return ""
            book = _ref_book(pos.strip())
            if book:
                self.stats["rp_linked"] += 1
                return f" ([{pos.strip()}](../books/{book}.md))"
            return f" ({pos})"
        if name in ("sitaatti", "lainaus", "quotation", "sitaatti3",
                    "sitaatti2", "cquote", "blockquote"):
            self.stats["tmpl_quote"] += 1
            # Split on the template's own pipes only. A plain split also cut
            # [[target|label]] in two, so the label became the "attribution"
            # and the link swallowed the quote (aukkojen-jumala-v2,
            # usko-ja-tieto, teleologinen-argumentti; fixed 2026-10-02).
            segments = [p.strip() for p in _split_top(raw)[1:] if p.strip()]
            # Drop named parameters (lähde=, source=); keep positional text.
            body_parts, attribution = [], ""
            for seg in segments:
                head = seg.split("=", 1)[0]
                if re.fullmatch(r"\s*\d\s*", head) and "=" in seg:
                    # "1=text" is positional text named explicitly
                    # (rudolf-bultmann's quote), not a parameter to drop.
                    body_parts.append(seg.split("=", 1)[1].strip())
                    continue
                if "=" in seg and " " not in head.strip() and len(head) < 20:
                    continue
                if seg.lower() in ("center", "left", "right"):
                    # Sitaatti3's alignment ({{Sitaatti3|center|…}}), not
                    # text: it showed as "> center" in 11 articles until
                    # 2026-10-02.
                    continue
                body_parts.append(seg)
            if len(body_parts) > 1 and not body_parts[-1].startswith("#"):
                attribution = body_parts[-1]
                body_parts = body_parts[:-1]
            quoted = "\n".join(
                "> " + ln for part in body_parts
                for ln in part.split("\n") if ln.strip() or True)
            if attribution:
                quoted += f"\n>\n> — {attribution}"
            return "\n\n" + quoted + "\n\n"
        if name in ("pääartikkeli", "main"):
            self.stats["tmpl_mainarticle"] += 1
            inner = pos or raw.split("|", 1)[-1]
            return f"\n\n*Pääartikkeli: {inner.strip()}*\n\n"
        if name.startswith(("uskonnonfilosofia", "raamatuntutkimus", "navbox",
                            "evoluutio", "teologia", "filosofia")):
            # Navigation boxes: the implant's own link graph replaces them.
            self.stats["tmpl_navbox_dropped"] += 1
            return ""
        if name in ("tägit", "tagit", "avainsanat"):
            # Search keywords the editors chose by hand. They are retrieval
            # gold in an implant whose whole point is being findable, so they are
            # collected into the page's tags rather than thrown away.
            self.stats["tmpl_keywords"] += 1
            for kw in re.split(r"[,\n]", pos):
                kw = kw.strip()
                if 2 < len(kw) < 40:
                    self.pending_keywords.append(kw)
            return ""
        if name in ("lähde", "fact", "citation needed", "cn"):
            # ApoWiki's own "citation needed" marker. This implant requires a
            # receipt for every claim, so the marker is kept as a visible
            # admission rather than quietly deleted.
            self.stats["tmpl_citation_needed"] += 1
            return " *[lähde puuttuu]*"

        if name in ("ingressi", "lead", "johdanto"):
            # The article's lead paragraph, wrapped in a styling template.
            # This is prime content — the first thing a reader and the
            # description generator see — so it is unwrapped, not dropped.
            self.stats["tmpl_lead"] += 1
            return "\n\n" + pos.strip() + "\n\n"
        if name in ("en", "fi", "sv", "de", "la", "gr", "he"):
            # A language marker on a following title; the label is noise in
            # prose but the language is worth keeping inline.
            self.stats["tmpl_lang"] += 1
            return "" if not pos else f" ({pos.strip()})"
        if name in ("väite-alku", "väite-loppu", "vaite-alku", "vaite-loppu",
                    "kh", "!", "l", "prettytable", "sisällysluettelo",
                    "toc", "suojattu", "tekijänoikeuksien alainen",
                    "lähteetön", "tämä artikkeli", "malline:tieteenfilosofia",
                    "raamatun_kirjat", "kirja", "tieteilijä", "ajankohtainen 3"):
            # Layout, protection banners and table styling: presentation that
            # markdown and the implant's own structure already provide.
            self.stats["tmpl_layout_dropped"] += 1
            return ""
        if name.startswith("#css") or name.startswith("#"):
            self.stats["tmpl_parserfunc_dropped"] += 1
            return ""
        if name in ("raamatunpaikka", "elokuvaviite", "cathency",
                    "kainalojuttu", "kainalojuttuboksi", "multiple image",
                    "hakasuluissa", "=", "kenen mukaan"):
            # Small wrappers around their own content: keep the content, drop
            # the wrapper. A citation variant keeps its text; a sidebar keeps
            # its prose; "hakasuluissa" literally means "in square brackets".
            self.stats["tmpl_unwrapped"] += 1
            inner = pos.strip()
            if name == "hakasuluissa" and inner:
                return f"[{inner}]"
            return inner
        if re.match(r"^k-[a-z]{2,3}$", name) or name in ("k-grc", "k-en", "k-he"):
            # Language-tagged term ({{k-grc|logos}}): the term is the content.
            self.stats["tmpl_lang_term"] += 1
            return pos.strip()
        if name.startswith("malline:") or name.endswith(("-päivitys", "-navi")):
            # `malline:` is the Template: namespace spelled out, and every
            # *-päivitys is an update banner. Both are navigation furniture.
            self.stats["tmpl_navbox_dropped"] += 1
            return ""
        # A bare {{topic}} with no parameters, whose name matches an article
        # or category in this wiki, is a topic navbox: the implant's link graph
        # replaces it. Anything WITH parameters may carry content, so it still
        # falls through to the visible-degradation path below.
        if not pos and "|" not in raw and len(name) > 3:
            self.stats["tmpl_navbox_dropped"] += 1
            return ""

        # Unknown: keep it visible so the gap can be found and fixed.
        self.unknown_templates[name] += 1
        self.stats["tmpl_unknown"] += 1
        return "\n\n```wikitext\n{{" + raw.strip() + "}}\n```\n\n"

    # -- refs --------------------------------------------------------------

    def extract_refs(self, text: str) -> tuple[str, list[str]]:
        """Turn <ref> tags into markdown footnotes, preserving named reuse."""
        notes: list[str] = []
        named: dict[str, int] = {}

        def add(content: str) -> int:
            notes.append(content.strip())
            return len(notes)

        def repl(m: re.Match) -> str:
            attrs, content = m.group("attrs") or "", m.group("body")
            nm = re.search(r'name\s*=\s*"?([^"\s/>]+)', attrs)
            if content is None:  # self-closing reuse: <ref name="x" />
                if nm and nm.group(1) in named:
                    return f"[^{named[nm.group(1)]}]"
                return ""
            body = self.expand_templates(content)
            body = self.inline_markup(body).strip()
            body = re.sub(r"\s*\n\s*", " ", body)
            idx = add(body)
            if nm:
                named[nm.group(1)] = idx
            return f"[^{idx}]"

        pattern = re.compile(
            r"<ref(?P<attrs>[^>]*?)(?:/>|>(?P<body>.*?)</ref\s*>)",
            re.S | re.I)
        text = pattern.sub(repl, text)
        self.stats["refs"] += len(notes)
        return text, notes

    # -- inline markup -----------------------------------------------------

    def _media_embeds(self, text: str) -> str:
        """`[[Kuva:x.jpg|frame|caption]]` -> an italic caption line.

        Brace-counted rather than regex-matched, because a caption may itself
        contain `[[links]]` and `[^1]` footnote markers.
        """
        open_re = re.compile(
            r"\[\[\s*(?:Kuva|Tiedosto|File|Image)\s*:", re.I)
        out, pos = [], 0
        while True:
            m = open_re.search(text, pos)
            if not m:
                out.append(text[pos:])
                break
            out.append(text[pos:m.start()])
            depth, i = 1, m.end()
            while i < len(text) and depth:
                if text.startswith("[[", i):
                    depth += 1
                    i += 2
                    continue
                if text.startswith("]]", i):
                    depth -= 1
                    i += 2
                    continue
                i += 1
            inner = text[m.end():i - 2]
            # Top-level pipes only: a caption's own [[target|label]] link
            # was cut at its pipe, so the caption became the link's label
            # plus a stray "]]" (darwin-ja-natsit until 2026-10-02).
            parts = _split_top(inner)
            name = parts[0].strip()
            # The caption is the last part that is not a layout keyword.
            caption = ""
            for p in reversed(parts[1:]):
                q = p.strip()
                if not q:
                    continue
                if re.fullmatch(
                        r"(frame|framed|thumb|thumbnail|left|right|center|none"
                        r"|border|upright|\d+\s*px|upright=[\d.]+)", q, re.I):
                    continue
                caption = q
                break
            self.stats["media_caption"] += 1
            if caption:
                out.append(f"\n\n*Kuva: {caption}*\n\n")
            else:
                out.append(f"\n\n*Kuva: {name}*\n\n")
            pos = i
        return "".join(out)

    def inline_markup(self, text: str) -> str:
        # Media embeds first. Their captions are real prose — often several
        # sentences carrying their own citations — and may contain brackets,
        # so the wiki-link regex below (which forbids brackets to stay
        # non-greedy) cannot match them. No media file is exported, so the
        # caption survives as an italic caption and the image is named.
        text = self._media_embeds(text)

        # Wiki links next, so their labels are not mangled by the quote rules.
        def wl(m: re.Match) -> str:
            inner = m.group(1)
            ext = re.match(r"^\s*(https?://\S+)\s+(.+?)\s*$", inner, re.S)
            if ext:
                # [[http://url label]] is a typo for [url label]; MediaWiki
                # shows it as an external link in literal brackets. Render
                # the link, not a red link to a URL (the-edge-of-evolution-
                # kirja, 2026-10-02).
                self.stats["link_external_double_bracket"] += 1
                return f"[{ext.group(2)}]({ext.group(1)})" + (m.group(2) or "")
            if "|" in inner:
                tgt, lbl = inner.split("|", 1)
            else:
                tgt, lbl = inner, inner
            if not re.match(r"^\s*(?:aw:s|apowiki:sanasto)\s*#", tgt, re.I):
                tgt = tgt.split("#", 1)[0]  # the glossary keeps its term
            # MediaWiki's link trail: letters written straight after the
            # closing brackets belong to the label ([[aihetodiste]]et reads
            # "aihetodisteet"). Finnish inflects by suffix, so without this
            # every inflected link would render as a split word.
            return self.link(tgt, lbl + (m.group(2) or ""))

        text = re.sub(r"\[\[([^\[\]]+)\]\]([^\W\d_]+)?", wl, text)

        # External links: [url label] -> [label](url)
        text = re.sub(
            r"\[(https?://[^\s\]]+)(?:\s+([^\]]+))?\]",
            lambda m: f"[{(m.group(2) or m.group(1)).strip()}]({m.group(1)})",
            text)

        # Emphasis: five, then three, then two quotes. A table row whose
        # bold is never closed (alkuhistorianäkemykset) paired its opening
        # ''' with the next row's; MediaWiki ends bold at the end of the
        # line, so such a row is closed there first (2026-10-02).
        text = "\n".join(
            ln + "'''" if ln.startswith("|")
            and len(re.findall(r"(?<!')'''(?!')", ln)) % 2 else ln
            for ln in text.split("\n"))
        text = re.sub(r"'''''(.+?)'''''", r"***\1***", text, flags=re.S)
        text = re.sub(r"'''(.+?)'''", r"**\1**", text, flags=re.S)
        text = re.sub(r"''(.+?)''", r"*\1*", text, flags=re.S)

        # Inline HTML that markdown has no need for.
        text = re.sub(r"<br\s*/?>", "  \n", text, flags=re.I)
        text = re.sub(r"</?(small|big|center|font|span|div)[^>]*>", "",
                      text, flags=re.I)
        text = re.sub(r"<nowiki>(.*?)</nowiki>", r"`\1`", text, flags=re.S | re.I)
        # HTML entities: markdown is read as text, so &ndash; must become the
        # character it names or the prose shows its own markup.
        text = html.unescape(text)
        return text

    # -- block structure ---------------------------------------------------

    def blocks(self, text: str) -> str:
        out = []
        for line in text.split("\n"):
            s = line.rstrip()
            m = re.match(r"^(={1,6})\s*(.+?)\s*\1\s*$", s)
            if m:
                # A single '=' is an h1 in wikitext, but the article title
                # already owns h1 here, so shift every level down by one.
                level = min(len(m.group(1)) + 1, 6)
                out.append("#" * level + " " + m.group(2))
                continue
            m = re.match(BULLET_RE, s)
            if m:
                out.append("  " * (len(m.group(1)) - 1) + "* " + m.group(2))
                continue
            # A wikitext bullet is `* text`. This runs AFTER inline markup, so
            # `'''Foo'''` is already `**Foo**`; a greedy `^\*+` would turn a
            # bold lead sentence into a list item and eat one of its markers.
            m = re.match(r"^(\*+)[ \t]+(?!\*)(.*)$", s)
            if m:
                out.append("  " * (len(m.group(1)) - 1) + "* " + m.group(2))
                continue
            m = re.match(r"^(#+)[ \t]+(.*)$", s)
            if m:
                out.append("  " * (len(m.group(1)) - 1) + "1. " + m.group(2))
                continue
            # ApoWiki usually writes numbered items with no space ("#Jos
            # Jumala…") and nests bullets under them ("#*", "#**", "#:").
            # Left alone, markdown reads "#Jos" as a broken heading; 4 467
            # lines in 451 articles were affected. The last prefix
            # character decides the item type, and the prefix length sets
            # the depth.
            m = re.match(r"^(#[#*:]*)(?![#*:])[ \t]*(\S.*)$", s)
            if m:
                pre = m.group(1)
                indent = "   " * (len(pre) - 1)
                marker = {"#": "1. ", "*": "* ", ":": "   "}[pre[-1]]
                out.append(indent + marker + m.group(2))
                continue
            m = re.match(r"^:+\s*(.*)$", s)
            if m:
                out.append("> " + m.group(1))
                continue
            m = re.match(r"^;\s*(.*)$", s)
            if m:
                out.append("**" + m.group(1) + "**")
                continue
            if re.match(r"^-{4,}\s*$", s):
                out.append("---")
                continue
            out.append(s)
        text = "\n".join(out)
        # A bullet inside a quote template sits after its "> " prefix.
        text = re.sub(r"^((?:> )+)(\x02+)[ \t]*",
                      lambda m: m.group(1) + "  " * (len(m.group(2)) - 1)
                      + "* ", text, flags=re.M)
        text = text.replace(BULLET, "*")
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def tables(self, text: str) -> str:
        """Wiki tables are 41 occurrences in the whole corpus. Rather than
        half-convert them, keep them as visible wikitext so nothing is lost
        and the remaining work is findable."""
        def repl(m: re.Match) -> str:
            self.stats["table_preserved"] += 1
            return "\n\n```wikitext\n" + m.group(0).strip() + "\n```\n\n"
        return re.sub(r"^\{\|.*?^\|\}", repl, text, flags=re.S | re.M)

    # A cell's attribute prefix: `style="…" |`, `colspan=2|`, `align=left |`.
    _ATTR = re.compile(r"^\s*((?:[a-z-]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s|]+)\s*)+)\|(?!\|)(.*)$",
                       re.I | re.S)

    def gfm_tables(self, text: str) -> str:
        """Turn the fenced wiki tables into GitHub-flavoured markdown tables.

        tables() fences each table early so later passes cannot mangle it;
        those passes still convert the cells (links, footnotes, bold), so
        here only the table syntax is left. colspan pads with empty cells and
        a caption becomes an italic line above the table. A table markdown
        cannot express (rowspan above 1, a nested table) stays fenced, so its
        degradation stays visible and counted.
        """
        def repl(m: re.Match) -> str:
            md = self._wiki_table_to_gfm(m.group(1))
            if md is None:
                self.stats["table_kept_fenced"] += 1
                return m.group(0)
            self.stats["table_converted"] += 1
            return md
        return re.sub(r"```wikitext\n(\{\|.*?\n\|\})\n```", repl, text,
                      flags=re.S)

    def _wiki_table_to_gfm(self, src: str) -> str | None:
        lines = src.split("\n")[1:-1]          # drop `{| …` and `|}`
        if any(l.lstrip().startswith("{|") for l in lines):
            return None
        caption = ""
        rows: list[list[tuple[bool, str, int]]] = []
        cur: list[tuple[bool, str, int]] | None = None

        def cell(raw: str, head: bool) -> tuple[bool, str, int] | None:
            span = 1
            am = self._ATTR.match(raw)
            if am:
                attrs, raw = am.group(1), am.group(2)
                rs = re.search(r"rowspan\s*=\s*\"?(\d+)", attrs, re.I)
                if rs and int(rs.group(1)) > 1:
                    return None
                cs = re.search(r"colspan\s*=\s*\"?(\d+)", attrs, re.I)
                if cs:
                    span = max(1, int(cs.group(1)))
            elif re.match(r"^\s*\|(?!\|)", raw):
                # An attribute prefix that was only a dropped template
                # (`!{{hl2}} | text`): the pipe is a separator, not content
                # (kreationismi rendered "\| text" until 2026-10-02).
                raw = re.sub(r"^\s*\|", "", raw, count=1)
            return (head, raw.strip(), span)

        for line in lines:
            st = line.strip()
            if st.startswith("|+"):
                c = cell(st[2:], False)
                caption = c[1] if c else st[2:].strip()
                continue
            if st.startswith("|-"):
                cur = None
                continue
            if st.startswith("!") or (st.startswith("|") and not st.startswith("|}")):
                head = st.startswith("!")
                body = st[1:]
                parts = re.split(r"!!|\|\|", body) if head else body.split("||")
                if cur is None:
                    cur = []
                    rows.append(cur)
                for part in parts:
                    c = cell(part, head)
                    if c is None:
                        return None
                    cur.append(c)
                continue
            # A continuation line belongs to the last cell.
            if cur and st:
                h, t, sp = cur[-1]
                cur[-1] = (h, (t + "<br>" + st) if t else st, sp)
        rows = [r for r in rows if r]
        if not rows:
            return None

        def esc(t: str) -> str:
            t = re.sub(r"</?br\s*/?>", "<br>", t)
            return t.replace("|", "\\|").replace("\n", "<br>")

        grid = []
        for r in rows:
            out = []
            for _h, t, sp in r:
                out.append(esc(t))
                out.extend([""] * (sp - 1))
            grid.append(out)
        grid = [r for r in grid if any(c.strip() for c in r)] or grid
        width = max(len(r) for r in grid)
        grid = [r + [""] * (width - len(r)) for r in grid]
        header_row = all(h for h, _t, _s in rows[0])
        head = grid[0] if header_row else [""] * width
        body = grid[1:] if header_row else grid
        out = []
        if caption:
            out.append(f"*{caption.strip('*')}*\n")
        out.append("| " + " | ".join(head) + " |")
        out.append("|" + "---|" * width)
        out += ["| " + " | ".join(r) + " |" for r in body]
        return "\n\n" + "\n".join(out) + "\n\n"

    # -- whole document ----------------------------------------------------

    def categories(self, text: str) -> tuple[str, list[str]]:
        cats = []

        def repl(m: re.Match) -> str:
            cats.append(m.group(1).strip())
            return ""

        text = re.sub(r"\[\[(?:Luokka|Category):([^\]|]+)(?:\|[^\]]*)?\]\]",
                      repl, text, flags=re.I)
        return text, cats

    def convert(self, title: str, wikitext: str, revid: str | None) -> str:
        self.pending_keywords = []
        body = re.sub(r"^<!--.*?-->\s*", "", wikitext, flags=re.S)
        # Behaviour switches (__NOTOC__, __TOC__ …) steer MediaWiki's own
        # rendering and are not text; two descriptions began "__NOTOC__"
        # until 2026-10-02.
        body = re.sub(r"__[A-ZÄÖ]+__", "", body)
        # A quote template its author never closed ({{sitaatti|… in
        # muotokritiikki): MediaWiki shows it as text; close it at the end
        # of its paragraph so it renders as the quote that was meant.
        body = _close_open_quotes(body)
        body, cats = self.categories(body)
        body = self.tables(body)
        body, notes = self.extract_refs(body)
        # In wikitext a line-initial "*" is always a bullet, with or without
        # a space ("*[[Väärä kompositio]]"). Once inline markup has run it
        # cannot be told from markdown italics, so 1 627 such lines in 470
        # articles stayed "*text" and never became lists (until 2026-10-02).
        # Tag the bullet prefix now; blocks() turns it into "* ".
        body = re.sub(r"^\*+", lambda m: BULLET * len(m.group(0)), body,
                      flags=re.M)
        body = self.expand_templates(body)
        body = self.inline_markup(body)
        body = self.blocks(body)
        body = self.gfm_tables(body)
        body = re.sub(r"<!--\s*red link:", "<!-- red link:", body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip()
        if not notes:
            body = body.replace("<!-- footnotes render here -->", "").strip()

        # Footnote definitions go at the end, under the references heading the
        # {{viitteet}} template already produced (or one we add).
        mark = "<!-- footnotes render here -->"
        if notes:
            if re.search(r"^#{2,6} Viitteet\s*" + re.escape(mark), body, re.M):
                body = body.replace(mark, "")       # the wiki wrote the heading
            elif mark in body:
                body = body.replace(mark, "## Viitteet", 1).replace(mark, "")
            elif "## Viitteet" not in body:
                body += "\n\n## Viitteet\n"
            body = body.rstrip()
            body += "\n\n" + "\n".join(
                f"[^{i + 1}]: {n}" for i, n in enumerate(notes) if n)

        tags = ["apowiki"] + [slug(c) for c in cats if c]
        # Editor-chosen keywords, capped: tags are for retrieval, and a list
        # of forty dilutes rather than sharpens it.
        tags += [slug(k) for k in self.pending_keywords[:12] if k]
        desc = self.description(body, title)
        fm = [
            "---",
            "type: article",
            "about: apologetics",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"description: {json.dumps(desc, ensure_ascii=False)}",
            f"tags: [{', '.join(dict.fromkeys(tags))}]",
            "timestamp: 2026-09-25T23:00:00Z",
            "---",
            "",
        ]
        permalink = (f"https://apowiki.fi/index.php?oldid={revid}" if revid
                     else "https://apowiki.fi")
        notice = (
            "<!--\n"
            f'Converted from ApoWiki (https://apowiki.fi) article "{title}".\n'
            f"Permalink: {permalink}\n"
            "Licence: GNU Free Documentation License, version 1.3 or later "
            "(GFDL-1.3-or-later).\n"
            "Generated by skills/tools/apowiki_convert.py from "
            "raw/apowiki-export/ — the wikitext there is the source of truth.\n"
            "-->\n"
        )
        return "\n".join(fm) + notice + "\n" + f"# {title}\n\n" + body + "\n"

    def description(self, body: str, title: str) -> str:
        """First real sentence, trimmed — the description is what search and
        the index show, so an empty one makes a page effectively invisible."""
        text = re.sub(r"^#.*$", "", body, flags=re.M)
        # Tables (and their captions) are not prose.
        text = re.sub(r"^\*[^\n]*\*\n\n(?=\|)", "", text, flags=re.M)
        text = re.sub(r"^\|.*$", "", text, flags=re.M)
        text = re.sub(r"```wikitext.*?```", "", text, flags=re.S)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        # Markdown links: keep the label, drop the target, or the description
        # reads "Herman Dooyeweerd(herman-dooyeweerd.md)". Links go before
        # footnote markers: a link labelled "[1960]" is not a footnote.
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"\[\^\d+\]:?", "", text)
        text = re.sub(r"[*>#\[\]]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return f"ApoWiki-artikkeli: {title}."
        cut = text[:400]
        m = re.search(r"^(.{60,300}?[.!?])\s", cut)
        out = (m.group(1) if m else cut[:240].rsplit(" ", 1)[0] + "…").strip()
        return unicodedata.normalize("NFC", out)


# Category slugs that mark a page as vandalism (see the skip in main()).
VANDALISM_CATEGORIES = {"vandalismi", "vandalism"}


def _revision_text(rev: dict) -> str:
    """Wikitext out of a MediaWiki revision record.

    MediaWiki 1.43 returns content under `slots.main.*` (the multi-content
    revision shape); older shapes put it in `*` or `content`. Reading only
    the top-level keys yields the empty string for every page, which looks
    like a corpus of blank articles rather than like a bug — so try all three.
    """
    slots = rev.get("slots") or {}
    main = slots.get("main") or {}
    return main.get("*") or main.get("content") or rev.get("*") \
        or rev.get("content") or ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--export", default="_implant/raw/apowiki-export")
    ap.add_argument("--cache", default="_temp/apowiki-cache")
    ap.add_argument("--out", default="_implant/knowledge/articles")
    ap.add_argument("--report", default="_temp/convert-report.json")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    export, cache = Path(args.export), Path(args.cache)
    out = Path(args.out)

    # Titles, revisions and redirect targets all come from the cache, so the
    # wiki's server is never touched by a conversion run.
    titles, revid_of, redirects, wikitext_of = [], {}, {}, {}
    for jf in sorted(cache.glob("*.json")):
        d = json.loads(jf.read_text(encoding="utf-8"))
        revs = d.get("revisions") or []
        if not revs:
            continue
        title = d["title"]
        titles.append(title)
        last = revs[-1]
        revid_of[title] = str(last.get("revid", ""))
        content = _revision_text(last)
        wikitext_of[title] = content
        m = re.match(r"^\s*#(?:REDIRECT|OHJAUS)\s*\[\[([^\]|]+)",
                     content, re.I)
        if m:
            redirects[title] = m.group(1).strip()

    stems = resolve_filenames(titles)
    conv = Converter(stems, redirects)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped_vandalism = []
    for title in sorted(titles):
        if title in redirects:
            continue
        wikitext = wikitext_of[title]
        # Prefer the exported file when present: it is the committed source.
        ef = export / f"{stems[title]}.wiki"
        if ef.exists():
            wikitext = ef.read_text(encoding="utf-8", errors="replace")
        # Pages the wiki itself files under a vandalism category are joke or
        # defaced pages, not apologetics: the raw export keeps them (it is
        # the faithful record), the distilled implant does not.
        _, cats = conv.categories(wikitext)
        if any(slug(c) in VANDALISM_CATEGORIES for c in cats):
            skipped_vandalism.append(title)
            continue
        md = conv.convert(title, wikitext, revid_of.get(title))
        (out / f"{stems[title]}.md").write_text(md, encoding="utf-8")
        written += 1
        if args.limit and written >= args.limit:
            break

    report = {
        "articles_written": written,
        "skipped_vandalism": skipped_vandalism,
        "redirects_resolved": len(redirects),
        "stats": dict(conv.stats),
        "red_links_total": sum(conv.red_links.values()),
        "red_links_distinct": len(conv.red_links),
        "red_links_top": conv.red_links.most_common(60),
        "red_links_all": conv.red_links.most_common(),
        "unknown_templates": conv.unknown_templates.most_common(40),
        "missing_project_pages": conv.missing_project_pages.most_common(20),
        "missing_glossary_terms": conv.missing_glossary_terms.most_common(60),
    }
    rp = Path(args.report)
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                  encoding="utf-8")

    print(f"wrote {written} articles to {out}")
    print(f"redirects resolved: {len(redirects)}")
    print(f"skipped as vandalism: {len(skipped_vandalism)}")
    print(f"internal links: {conv.stats['link_internal']}, "
          f"wikipedia: {conv.stats['link_wikipedia']}, "
          f"red: {conv.stats['link_red']} "
          f"({len(conv.red_links)} distinct, "
          f"{conv.stats['link_red_to_wikipedia']} to Finnish and "
          f"{conv.stats['link_red_to_wikipedia_en']} to English Wikipedia, "
          f"{conv.stats['link_red_to_glossary']} to the glossary)")
    print(f"written pages answering red links: "
          f"{conv.stats['link_written_page']}")
    print(f"footnotes: {conv.stats['refs']}")
    if conv.unknown_templates:
        print(f"unknown templates (kept visible): "
              f"{sum(conv.unknown_templates.values())} in "
              f"{len(conv.unknown_templates)} kinds — "
              f"{', '.join(k for k, _ in conv.unknown_templates.most_common(8))}")
    print(f"report: {rp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
