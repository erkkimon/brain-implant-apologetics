#!/usr/bin/env python3
"""Translate one converted article Finnish -> English with a small local model.

The model is treated as untrusted. It does the one thing a small model does
acceptably, which is turning a paragraph of Finnish prose into English. Every
property that must survive is checked mechanically afterwards, and a chunk
that fails a check is retried with the failure spelled out. If it still
fails, the Finnish original is kept and visibly marked, never replaced by a
plausible-looking translation that has lost something. The checks:

* **Links survive.** Every link target in the Finnish chunk appears in the
  English chunk. A trial on 2026-09-27 showed both a 4B and a 9B model
  silently dropping `[C. S. Lewis](c-s-lewis-v2.md)`.
* **Footnote markers survive.** The same `[^n]` markers, the same number of
  times, because the receipts are the product (see
  conventions/every-claim-carries-its-receipt.md).
* **The glossary is obeyed.** For every ApoWiki glossary term found in the
  Finnish chunk that has a fixed rendering in knowledge/glossary/english.md,
  that rendering appears in the English chunk.
* **Nothing is invented around it.** No preamble ("Here is the
  translation"), no code fences.

Passed through untranslated and unsent:

* the frontmatter, which is rewritten for the English page
* the GFDL source comment
* HTML comments that stand alone as a block. A comment inside prose (a
  red-link note) goes to the model and must come back unchanged.
* footnote definitions `[^n]: …`. A citation is a receipt: the Finnish book
  title, publisher and page stay exactly as ApoWiki recorded them.

The endpoint is machine-local, so it comes from `--endpoint` or `$OLLAMA_HOST`
and is never written into the repository.

Usage:
    python3 apowiki_translate.py ARTICLE.md [--model M] [--out DIR]
        [--endpoint URL] [--retries 2] [--dry-run]
    python3 apowiki_translate.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apowiki_glossary import anchor, entries, load_english, source  # noqa: E402

DEFAULT_MODEL = "jaahas/qwen3.5-uncensored:9b-q6_K"
MAX_WORDS = 350          # per chunk: small models degrade on long inputs
TODAY = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

PROMPT = """You translate Finnish Christian-apologetics articles into English.

Rules:
1. Translate the Finnish text below into natural, precise English.
2. Keep all markdown exactly: every [label](target) link keeps its target
   unchanged (translate only the label), every footnote marker like [^3]
   stays in place, headings keep their # level, lists stay lists.
3. Use these fixed English terms for these Finnish terms (inflect as English
   grammar needs, never substitute a synonym):
{glossary}
4. Do not translate the titles of books or articles; keep them as written.
   Copy every HTML comment <!-- ... --> unchanged, untranslated.
5. Output only the translation: no preamble, no notes, no code fences.
{feedback}
Finnish text:

{text}"""


# ---------------------------------------------------------------------------
# Glossary matching. Finnish inflects by suffix, so a term is found by the
# stem of each of its words: all but the last two letters of a longer word
# (naturalismi -> naturalism…, which matches naturalismin, naturalismia).
# Crude, but a false hit only adds a line to the prompt and to the check.
# ---------------------------------------------------------------------------

def _stem(word: str) -> str:
    return word[:-2] if len(word) > 5 else word


def glossary_rules() -> list[tuple[re.Pattern, str, str]]:
    english = load_english()
    rules = []
    try:
        ents = entries(source()[0])
    except FileNotFoundError:
        return rules
    seen = set()
    for term, _ in ents:
        a = anchor(term)
        if a not in english or a in seen:
            continue
        seen.add(a)
        words = term.strip("*").lower().split()
        pat = r"\b" + r"\w*\s+".join(re.escape(_stem(w)) for w in words) + r"\w*"
        rules.append((re.compile(pat, re.I), term.strip("*"), english[a]))
    return rules


def missing_terms(blocks) -> list[str]:
    """Glossary terms that occur in the visible text but have no English
    row yet: the rows to fill before this article's batch runs."""
    english = load_english()
    try:
        ents = entries(source()[0])
    except FileNotFoundError:
        return []
    seen = visible("\n".join(t for kind, t in blocks if kind != "keep"))
    out = []
    for term, _ in ents:
        a = anchor(term)
        if a in english or term in out:
            continue
        words = term.strip("*").lower().split()
        pat = r"\b" + r"\w*\s+".join(re.escape(_stem(w)) for w in words) + r"\w*"
        if re.search(pat, seen, re.I):
            out.append(term.strip("*"))
    return out


def visible(text: str) -> str:
    """The words a reader sees: link targets, comments and footnote markers
    removed. A term inside `(suunnitteluteoria.md)` is a file name, not a
    word to translate; matching it failed 3 of 5 chunks of the first
    batch's teleologinen-argumentti (2026-10-01)."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"\]\([^)\s]*\)", "]", text)
    return re.sub(r"\[\^[^\]]+\]", " ", text)


def terms_in(text: str, rules) -> list[tuple[str, str]]:
    # Longest term first: "metodologinen naturalismi" also contains
    # "naturalismi", and both are then required, which is correct.
    seen = visible(text)
    return [(fi, en) for pat, fi, en in rules if pat.search(seen)]


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

LINK = re.compile(r"\]\(([^)\s]+)\)")
NOTE = re.compile(r"\[\^[^\]]+\](?!:)")
# Red-link notes are data (the wanted-pages count reads them), not prose.
# The 9B model translated one on its first real run (2026-10-01).
COMMENT = re.compile(r"<!--.*?-->", re.S)


def check(fi: str, en: str, required: list[tuple[str, str]]) -> list[str]:
    problems = []
    missing = [t for t in LINK.findall(fi) if t not in LINK.findall(en)]
    if missing:
        problems.append("these link targets are missing, keep every "
                        "[label](target) link: " + ", ".join(missing))
    lost = [c for c in COMMENT.findall(fi) if c not in en]
    if lost:
        problems.append("these HTML comments must be copied unchanged, "
                        "character for character: " + " ".join(lost))
    if sorted(NOTE.findall(fi)) != sorted(NOTE.findall(en)):
        problems.append("footnote markers changed; keep exactly: "
                        + " ".join(NOTE.findall(fi)))
    low = visible(en).lower()
    for fi_t, en_t in required:
        # "extreme naturalism" is satisfied by "extreme naturalist" too.
        core = _stem(en_t.strip("*").lower()) if len(en_t) > 6 else en_t.lower()
        if core not in low:
            problems.append(f'the Finnish term "{fi_t}" must be translated '
                            f'as "{en_t}"')
    if re.match(r"\s*(here is|here's|translation:|```)", en, re.I) or "```" in en:
        problems.append("output only the translation, no preamble or fences")
    return problems


# ---------------------------------------------------------------------------
# Splitting the article
# ---------------------------------------------------------------------------

def split_article(md: str) -> tuple[str, str, list[tuple[str, str]]]:
    """(frontmatter, source comment, [(kind, block)]).

    kind is "prose" (translated) or "keep" (passed through verbatim).
    """
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    front = m.group(1) if m else ""
    rest = md[m.end():] if m else md
    c = re.match(r"^\s*<!--.*?-->\n", rest, re.S)
    comment = c.group(0) if c else ""
    rest = rest[c.end():] if c else rest
    blocks = []
    for b in re.split(r"\n{2,}", rest.strip("\n")):
        if not b.strip():
            continue
        keep = (re.match(r"^\[\^[^\]]+\]:", b)
                or re.fullmatch(r"\s*<!--.*?-->\s*", b, re.S)
                or b.startswith("```"))
        blocks.append(("keep" if keep else "prose", b))
    return front, comment, blocks


def chunks(blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Merge consecutive prose blocks into chunks of at most MAX_WORDS."""
    out: list[tuple[str, str]] = []
    for kind, b in blocks:
        if (kind == "prose" and out and out[-1][0] == "prose"
                and len((out[-1][1] + b).split()) <= MAX_WORDS):
            out[-1] = ("prose", out[-1][1] + "\n\n" + b)
        else:
            out.append((kind, b))
    return out


# ---------------------------------------------------------------------------

def generate(endpoint: str, model: str, prompt: str) -> str:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "think": False,
                       "options": {"temperature": 0.2, "num_ctx": 8192}})
    req = urllib.request.Request(f"{endpoint.rstrip('/')}/api/generate",
                                 data=body.encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3600) as r:
        return json.load(r).get("response", "").strip()


def translate_chunk(text, rules, endpoint, model, retries, dry):
    required = terms_in(text, rules)
    gl = "\n".join(f"   - {fi} = {en}" for fi, en in required) or "   (none)"
    feedback = ""
    problems: list[str] = []
    for _attempt in range(retries + 1):
        prompt = PROMPT.format(glossary=gl, feedback=feedback, text=text)
        if dry:
            return text, [], required
        try:
            en = generate(endpoint, model, prompt)
        except (OSError, ValueError) as e:
            # A shared CPU host can starve a request past the timeout. Lose
            # the chunk, not the article (2026-10-01: one timeout discarded
            # four finished chunks).
            problems = [f"the model call failed ({type(e).__name__})"]
            continue
        problems = check(text, en, required)
        if not problems:
            return en, [], required
        feedback = ("\nYour previous attempt was rejected: "
                    + "; ".join(problems) + ". Fix exactly that.\n")
    return None, problems, required


def english_front(front: str, model: str, stem: str) -> str:
    lines = []
    for line in front.splitlines():
        if line.startswith("timestamp:"):
            line = f"timestamp: {TODAY}"
        lines.append(line)
    lines += ["lang: en", f"translated_from: ../articles/{stem}.md",
              f"translated_by: {model}", "translation_status: machine"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article", nargs="?", type=Path)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", type=Path, default=Path("_temp/translations"))
    ap.add_argument("--endpoint",
                    default=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true",
                    help="split and match glossary terms, call no model")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.article:
        ap.error("an article path is required")
    if not args.endpoint.startswith("http"):
        args.endpoint = "http://" + args.endpoint

    rules = glossary_rules()
    front, comment, blocks = split_article(args.article.read_text(encoding="utf-8"))
    parts, failed, t0 = [], 0, time.time()
    for kind, text in chunks(blocks):
        if kind == "keep":
            parts.append(text)
            continue
        en, problems, req = translate_chunk(text, rules, args.endpoint,
                                            args.model, args.retries, args.dry_run)
        if en is None:
            failed += 1
            parts.append("<!-- translation failed its checks: "
                         + "; ".join(problems).replace("--", "—")
                         + ". Finnish original kept. -->\n\n" + text)
        else:
            parts.append(en)
        print(f"  chunk {len(parts)}: {len(text.split())} words, "
              f"{len(req)} glossary terms, "
              f"{'FAILED' if en is None else 'ok'}", flush=True)

    if args.dry_run:
        # A dry run writes nothing: a file in _temp/translations/ is a
        # finished translation to the batch runner and to apowiki_land.py
        # (2026-10-02, a dry run over batch 2 left 13 Finnish "translations").
        missing = missing_terms(blocks)
        print(f"{args.article.stem}: dry run, nothing written; "
              f"{len(missing)} glossary terms here have no English yet"
              + (": " + ", ".join(missing) if missing else ""))
        return 0
    stem = args.article.stem
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"{stem}.md"
    out.write_text("---\n" + english_front(front, args.model, stem)
                   + "\n---\n" + comment + "\n".join(p + "\n" for p in parts),
                   encoding="utf-8")
    print(f"{out}: {len(parts)} blocks, {failed} kept in Finnish, "
          f"{time.time() - t0:.0f}s")
    return 1 if failed else 0


def selftest() -> int:
    fi = "Ks. [C. S. Lewis](c-s-lewis-v2.md)in kirja.[^2]"
    assert check(fi, "See C. S. Lewis's book.[^2]", []) != []
    assert check(fi, "See [C. S. Lewis's](c-s-lewis-v2.md) book.[^2]", []) == []
    assert check(fi, "See [Lewis](c-s-lewis-v2.md).", []) != []
    req = [("naturalismi", "naturalism")]
    assert check("naturalismin", "of naturalism", req) == []
    assert check("naturalismin", "of materialism", req) != []
    assert check("x", "Here is the translation: x", []) != []
    assert check("a <!-- red link: Kirja -->", "a <!-- red link: Book -->", []) != []
    assert check("a <!-- red link: Kirja -->", "an <!-- red link: Kirja -->", []) == []
    f, c, b = split_article("---\ntype: article\n---\n<!--\nsrc\n-->\n\n# T\n\n"
                            "Teksti.[^1]\n\n[^1]: Kirja, s. 3.\n")
    assert [k for k, _ in b] == ["prose", "prose", "keep"], b
    assert [k for k, _ in chunks(b)] == ["prose", "keep"]
    rules = [(re.compile(r"\bnaturalism\w*", re.I), "naturalismi", "naturalism")]
    assert terms_in("naturalismia vastaan", rules) == [("naturalismi", "naturalism")]
    assert terms_in("[idea](naturalismi.md)", rules) == []
    print("apowiki_translate: selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
