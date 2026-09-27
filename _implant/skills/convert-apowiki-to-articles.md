---
type: skill
title: Convert ApoWiki wikitext into implant articles
description: Use when turning the ApoWiki export in raw/apowiki-export/ into searchable articles under knowledge/ — the deterministic, token-free conversion that produces the MVP, including wiki-link resolution, citation footnotes and the topic spine that grounds every page.
timestamp: 2026-09-27T10:00:00Z
depends_on: [skills/using-the-brain-implant.md]
tools:
  - skills/tools/apowiki_convert.py
  - skills/tools/apowiki_topics.py
  - skills/tools/apowiki_books.py
---

# Convert ApoWiki wikitext into implant articles

This is the machine-time half of the MVP described in
[plans/mvp-then-iteration.md](../plans/mvp-then-iteration.md): it costs CPU
hours and **no model tokens**, and it is what makes the implant usable before
any translation work starts. Both tools are idempotent — run them as often as
you like.

## The procedure

```bash
# 1. wikitext -> markdown articles (reads raw/ and the fetch cache, writes knowledge/articles/)
python3 _implant/skills/tools/apowiki_convert.py

# 2. categories -> topic pages, and a breadcrumb on every article
python3 _implant/skills/tools/apowiki_topics.py

# 3. the book spine: 66 books + 2 testaments, bound to the theology implant
python3 _implant/skills/tools/apowiki_books.py

# 4. compile, then verify the contract
brainpick compile --root .
henxels check --all
```

Expect, from the 848-page export: **471 articles** (377 redirects resolved
rather than imported), ~2 500 internal links, ~1 500 Wikipedia links,
**5 111 footnotes**, 44 topic pages, zero ghosts.

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
  a fenced `wikitext` block and counted in the report; the 41 wiki tables are
  preserved the same way rather than half-converted. A converter that drops
  what it cannot parse looks successful while destroying the archive.
* **Red links are honest.** A wiki link whose target does not exist becomes
  plain text plus an HTML comment (`<!-- red link: Target -->`), so it is
  greppable and reported, never a path that merely looks plausible.

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
