---
type: skill
title: Convert ApoWiki wikitext into implant articles
description: Use when turning the ApoWiki export in raw/apowiki-export/ into searchable articles under knowledge/ — the deterministic, token-free conversion that produces the MVP, including wiki-link resolution, citation footnotes and the topic spine that grounds every page.
timestamp: 2026-10-02T03:00:00Z
depends_on: [skills/using-the-brain-implant.md]
tools:
  - skills/tools/apowiki_convert.py
  - skills/tools/apowiki_topics.py
  - skills/tools/apowiki_books.py
  - skills/tools/apowiki_glossary.py
  - skills/tools/apowiki_stamp.py
  - skills/tools/apowiki_redlinks.py
---

# Convert ApoWiki wikitext into implant articles

This is the machine-time half of the MVP described in
[plans/mvp-then-iteration.md](../plans/mvp-then-iteration.md): it costs CPU
hours and **no model tokens**, and it is what makes the implant usable before
any translation work starts. Both tools are idempotent — run them as often as
you like.

## The procedure

```bash
# 0. start clean, so a page that no longer exists does not linger
rm -rf _implant/knowledge/{articles,topics,books}

# 0b. the glossary first: the converter resolves AW:S#term links against it
python3 _implant/skills/tools/apowiki_glossary.py

# 1. wikitext -> markdown articles (reads raw/ and the fetch cache, writes knowledge/articles/)
python3 _implant/skills/tools/apowiki_convert.py

# 1b. only when red links changed: look new red-link targets up in the
#     Finnish Wikipedia, review the additions to red-link-wikipedia.json by
#     hand (null keeps a target red), then re-run step 1
# python3 _implant/skills/tools/apowiki_redlinks.py
#     then the English Wikipedia for what Finnish lacked
#     (red-link-wikipedia-en.json; review it: bare years resolve to the year)
# python3 _implant/skills/tools/apowiki_redlinks.py --lang en

# 2. categories -> topic pages, and a breadcrumb on every article
python3 _implant/skills/tools/apowiki_topics.py

# 3. the book spine: 66 books + 2 testaments, bound to the theology implant
python3 _implant/skills/tools/apowiki_books.py

# 4. timestamps: keep the committed one where a page did not change, bump
#    the rest (the generators write a fixed placeholder)
python3 _implant/skills/tools/apowiki_stamp.py _implant/knowledge/articles \
    _implant/knowledge/topics _implant/knowledge/books
find _implant -name __pycache__ -exec rm -rf {} +

# 5. compile, then verify the contract
brainpick compile --root .
henxels check --all
```

Expect, from the 848-page export: **471 articles** (377 redirects resolved
rather than imported), ~2 500 internal links, ~1 500 Wikipedia links,
**5 111 footnotes**, 44 topic pages, 401 glossary links, 1 297 scripture
references linked to their book pages, zero ghosts.

## What the conversion guarantees, and why each matters

* **Slugs come from one source of truth.** `apowiki_convert.slug()` is
  byte-identical to the importer's, including the sorted `-v2` disambiguation
  that fixed the collision described in
  [the import journal](../journals/archive/2026/09/2026-09-24.md). Two slug
  functions would mean links that point at files nobody wrote.
* **Receipts survive.** `{{Kirjaviite}}` (1 365 of them) becomes a real
  footnote with author, title, publisher, year, page and ISBN;
  `{{Verkkoviite}}` keeps its URL and access date. This is the corpus's main
  value under [every claim carries its receipt](../conventions/every-claim-carries-its-receipt.md).
* **Degradation is visible, never silent.** An unknown template is emitted as
  a fenced `wikitext` block and counted in the report (none are left in
  revision 11402). Wiki tables become markdown tables, with colspan padded
  and a caption as an italic line; a table markdown cannot express (rowspan
  above 1, a nested table) stays fenced and counts as `table_kept_fenced`.
  All 41 converted on 2026-10-01 ([journal](../journals/archive/2026/10/2026-10-01.md)). A
  converter that drops what it cannot parse looks successful while
  destroying the archive.
* **Red links are honest.** A wiki link whose target does not exist becomes
  plain text plus an HTML comment (`<!-- red link: Target -->`), so it is
  greppable and reported, never a path that merely looks plausible.
* **Titles resolve the way MediaWiki resolves them.** An exact match comes
  first, then a capitalised first letter, and only then a case-insensitive
  match that prefers an article over a redirect. Before 2026-10-01 the
  lower-cased lookup let the redirect *Michael behe* shadow the article
  *Michael Behe*, and the corpus's most-linked person read as a red link
  ([journal](../journals/archive/2026/10/2026-10-01.md)). Invisible marks (U+200E), a
  leading colon, underscores and `#section` are stripped first.
* **A red link to a glossary term lands on the glossary.** When ApoWiki
  never wrote an article on a term its own [Sanasto](../knowledge/glossary/sanasto.md)
  defines (*perususkomus*, *äskettäisluomisnäkemys*), the label links to that
  entry, in the wiki's own sense, and the red-link comment stays. This
  comes before the Wikipedia fallback. 28 links, added 2026-10-01
  ([journal](../journals/archive/2026/10/2026-10-01.md)).
* **A red link to a subject Wikipedia covers links there and stays red.**
  `red-link-wikipedia.json` (written by `apowiki_redlinks.py`, then reviewed
  by hand) maps a target such as *Immanuel Kant* to its Finnish Wikipedia
  page. The label links there and the `<!-- red link -->` comment stays, so
  the page still counts as wanted. Reviewing matters: *David Quinn* the
  debater is a hockey player in Wikipedia, and *perusryhmä* (a created kind)
  is a topology term there; such entries are null.
  What the Finnish Wikipedia lacks, the English one is tried for next
  (`red-link-wikipedia-en.json`, `--lang en`): many red links name
  English-language scholars and books. 117 targets, added 2026-10-02
  ([journal](../journals/2026-10-02.md)); bare years (*1623*) were rejected
  by hand.
* **Headings are inserted after the list pass, never before it.** `blocks()`
  reads a line starting with `#` as a wikitext numbered item. The
  `{{viitteet}}` template used to emit `## Viitteet` early, and 350 articles
  ended with a stray "1. Viitteet" list item. It now leaves a placeholder
  that becomes the heading at the end, or vanishes when the wiki already
  wrote a *Viitteet* heading right above it. Found while reviewing the first
  translation ([journal](../journals/archive/2026/10/2026-10-01.md)).
* **Glossary links land somewhere useful.** An `AW:S#term` link to a term
  the glossary defines lands on its anchor. The 41 terms it does not define
  were decided once, in `GLOSSARY_FALLBACKS` in the converter: a near-variant
  glossary term, an ApoWiki article, a Finnish Wikipedia page, or plain text
  when nothing fits ([journal](../journals/archive/2026/10/2026-10-01.md)). A new undefined
  term shows up in the report under `missing_glossary_terms` and lands on the
  glossary page until it is added to the table.
* **Vandalism stays raw.** A page filed under `Luokka:Vandalismi` (one joke
  page in revision 11402's corpus) is kept in `raw/apowiki-export/` as the
  faithful record but is not converted, so it never reaches search or a topic
  page. The report lists it under `skipped_vandalism`
  ([journal](../journals/archive/2026/10/2026-10-01.md)).

## Gotchas that cost time once

* **The cache stores wikitext under `slots.main.*`** (MediaWiki 1.43's
  multi-content revisions), not under `content` or `*`. Reading only the
  top-level keys yields empty strings for all 848 pages, which looks like a
  corpus of blank articles rather than a bug. `_revision_text()` tries all
  three shapes.
* **Block conversion runs after inline conversion**, so by then `'''bold'''`
  is already `**bold**`. A `^\*+` bullet rule therefore eats a bold lead
  sentence; the rule requires whitespace after the asterisks for that reason.
* **Image captions are prose and may contain brackets and refs**, so they are
  extracted by brace counting, not by the bracket-free wiki-link regex.
  There are 194 of them, several sentences long, with their own citations.
* **`AW:S` is not a broken link, it is a missing namespace.** 415 links point
  into ApoWiki's project namespace (the glossary at `ApoWiki:Sanasto`), which
  the fetch never captured because it took only the main namespace. Following
  the redirect lands on a cycle. They are recorded in the report as
  `missing_project_pages`; re-fetching that namespace is an open task.

## Why the topic pages exist

54 converted articles carried no internal link at all, and 23 carried no
citation either — they would fail the grounding henxel and, worse, be
invisible to the graph. ApoWiki's editors had already solved this by hand:
every article carries categories. `apowiki_topics.py` turns each category with
at least three members into a topic page, adds an *Aihepiirit* breadcrumb to
every article, and sweeps anything left over (uncategorised, admin-only, or
vandalism categories) into a `Muut` page — because "uncategorised in the
source wiki" is a true statement and a findable page beats a dangling file.

The result is navigable in both directions and is the same move the theology
implant makes when it hangs chapters on books and books on testaments.

## The book spine

The theology implant owns the spine (its `bookcodes.py` is the canon; its
chapters hang on its book pages). `apowiki_books.py` mirrors only the rungs
here: one Finnish page per book in `knowledge/books/`, bound to its testament
page, each pointing across the federation boundary with an autolink such as
`<brain://theology-…/knowledge/scripture/gen/gen.md>`. Use that autolink
form. A markdown link whose target is a `brain://` URI is reported dead by henxels'
`links_resolve`, while brainpick 0.8.6 reads either form when it builds
`brain_read` annotations. The converter imports the tool's alias table, so a
wiki link naming a book with no ApoWiki article (`[[Matteuksen evankeliumi]]`)
lands on its rung instead of staying red. Run the books tool after the topics
tool: it adds a spine breadcrumb to the ten articles ApoWiki wrote about
individual books.

## After this

Semantic search needs a multilingual embedding model, or English queries will
not find this Finnish corpus — `bge-m3` in `brainpick.local.toml`, and
brainpick installed with its vector extra (`uv tool install 'brainpick[vectors]'`),
or tier 2 stays off and search silently degrades to keyword matching. Only
then does translation begin, one themed batch per cooldown burst.
