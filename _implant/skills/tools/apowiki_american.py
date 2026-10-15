#!/usr/bin/env python3
"""Convert British spellings in English ApoWiki pages to American.

Usage: apowiki_american.py [--check] FILE.md ...

Protected, never changed: frontmatter keys other than title/description,
HTML comments, footnote definition lines ([^n]: ...), link targets (the
part in parentheses after ](...)), *italic* or **bold-italic** titles, the
generated "Licence:" footer, and any double-quoted or > block-quoted text
that also appears verbatim in the Finnish source page (an author's own
English, which keeps its spelling). Quotes that are our translation from
Finnish are converted like the rest.

--check prints what would change and exits 1 if anything would.
"""
import re
import sys
from pathlib import Path

WORDS = {
    # -our
    "behaviour": "behavior", "behaviours": "behaviors", "behavioural": "behavioral",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "favour": "favor", "favours": "favors", "favoured": "favored",
    "favourable": "favorable", "favourite": "favorite", "favouring": "favoring",
    "honour": "honor", "honours": "honors", "honoured": "honored",
    "labour": "labor", "neighbour": "neighbor", "neighbours": "neighbors",
    "humour": "humor", "rigour": "rigor", "vigour": "vigor",
    "endeavour": "endeavor", "harbour": "harbor", "rumour": "rumor",
    "rumours": "rumors", "flavour": "flavor", "fervour": "fervor",
    "splendour": "splendor", "odour": "odor", "armour": "armor",
    # -yse
    "analyse": "analyze", "analysed": "analyzed", "analyses_verb": "analyzes",
    "analysing": "analyzing", "paralyse": "paralyze", "paralysed": "paralyzed",
    "paralysing": "paralyzing",
    # -re
    "centre": "center", "centres": "centers", "centred": "centered",
    "theatre": "theater", "theatres": "theaters", "metre": "meter",
    "metres": "meters", "fibre": "fiber", "spectre": "specter",
    "calibre": "caliber", "sombre": "somber",
    # misc
    "sceptic": "skeptic", "sceptics": "skeptics", "sceptical": "skeptical",
    "scepticism": "skepticism", "defence": "defense", "offence": "offense",
    "pretence": "pretense", "judgement": "judgment", "judgements": "judgments",
    "towards": "toward", "programme": "program", "programmes": "programs",
    "grey": "gray", "whilst": "while", "amongst": "among",
    "practise": "practice", "practised": "practiced", "practising": "practicing",
    "labelled": "labeled", "labelling": "labeling", "modelled": "modeled",
    "modelling": "modeling", "travelled": "traveled", "travelling": "traveling",
    "cancelled": "canceled", "fulfil": "fulfill", "fulfilment": "fulfillment",
    "skilful": "skillful", "wilful": "willful", "aeon": "eon", "aeons": "eons",
    "mediaeval": "medieval", "encyclopaedia": "encyclopedia", "foetus": "fetus",
    "manoeuvre": "maneuver", "catalogue": "catalog", "catalogues": "catalogs",
}
# -ise/-isation verbs: an explicit stem list, because a blanket rule would
# break "exercise", "promise", "surprise", "otherwise", "precise", "wise" …
ISE_STEMS = """real recogn organ emphas critic character theor summar special apolog
minim maxim general popular legitim util civil secular rational hypothes harmon
symbol bapt scrutin jeopard ideal visual memor categor priorit standard mobil
neutral patron westerni author final penal local modern moral personal polar
public social stabil stigmat synthes systemat trivial capital central dramat
familiar global human individual internal liberal natural normal optim
pessim politic radical revolution sensit sympath terror urban vandal""".split()
ISE_RE = re.compile(r"\b(" + "|".join(ISE_STEMS) + r")is(e|es|ed|ing|ation|ations|er|ers)\b", re.I)
WORD_RE = re.compile(r"\b(" + "|".join(sorted((k for k in WORDS if not k.endswith("_verb")), key=len, reverse=True)) + r")\b", re.I)


def match_case(src: str, dst: str) -> str:
    if src.isupper():
        return dst.upper()
    if src[0].isupper():
        return dst[0].upper() + dst[1:]
    return dst


def convert_text(t: str) -> str:
    t = WORD_RE.sub(lambda m: match_case(m.group(0), WORDS[m.group(0).lower()]), t)
    t = ISE_RE.sub(lambda m: m.group(0)[: len(m.group(1))] + ("iz" if m.group(0)[len(m.group(1))].islower() else "IZ") + m.group(2), t)
    return t


PROTECT = re.compile(
    r"<!--.*?-->"            # HTML comments
    r"|\]\((?:[^()]|\([^()]*\))*\)"  # link targets
    r"|\*\*\*(?=\S)[^*\n]+?(?<=\S)\*\*\*|(?<!\*)\*(?=[^\s*])[^*\n]+?(?<=\S)\*(?!\*)"  # italic titles
    r"|\"[^\"\n]+\"|“[^”\n]+”",  # double quotes (checked against the Finnish below)
    re.S,
)


def convert_body(body: str, finnish: str) -> str:
    out = []
    for line in body.split("\n"):
        if line.startswith("[^") or line.startswith("Licence:") or "Licence: GNU" in line:
            out.append(line)
            continue
        if line.startswith(">"):
            core = line.lstrip("> ").strip()
            if core and core in finnish:
                out.append(line)
                continue
        pieces, last = [], 0
        for m in PROTECT.finditer(line):
            pieces.append(convert_text(line[last:m.start()]))
            seg = m.group(0)
            if seg[0] in "\"“" and seg[1:-1] not in finnish:
                seg = seg[0] + convert_text(seg[1:-1]) + seg[-1]
            pieces.append(seg)
            last = m.end()
        pieces.append(convert_text(line[last:]))
        out.append("".join(pieces))
    return "\n".join(out)


def convert_file(path: Path) -> tuple[str, str]:
    s = path.read_text()
    m = re.match(r"(---\n.*?\n---\n)(.*)", s, re.S)
    if not m:  # index.md and other frontmatter-free pages
        return s, s
    front, body = m.group(1), m.group(2)
    src = re.search(r"(?m)^translated_from: *(.+)$", front)
    finnish = ""
    if src:
        fp = (path.parent / src.group(1).strip().strip("\"'")).resolve()
        if fp.exists():
            finnish = fp.read_text()
    front2 = re.sub(r"(?m)^(title|description): (.*)$", lambda mm: f"{mm.group(1)}: {convert_text(mm.group(2))}", front)
    return s, front2 + convert_body(body, finnish)


def main() -> int:
    args = sys.argv[1:]
    check = "--check" in args
    files = [Path(a) for a in args if a != "--check"]
    changed = 0
    for f in files:
        old, new = convert_file(f)
        if old == new:
            continue
        changed += 1
        if check:
            for a, b in zip(old.split("\n"), new.split("\n")):
                if a != b:
                    print(f"{f}: {a[:100]!r}\n{' ' * len(str(f))}  {b[:100]!r}")
        else:
            f.write_text(new)
    print(f"{changed} of {len(files)} files {'would change' if check else 'changed'}")
    return 1 if check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
