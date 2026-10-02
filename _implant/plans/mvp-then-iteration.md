---
type: plan
title: "MVP first, then daily iteration (apologetics)"
description: "The apologetics half of the shared plan: convert ApoWiki's wikitext to Finnish markdown pages with parsed implant links, hang the book corpus on the shared book spine, compile with multilingual embeddings, and only then start cooldown-batched translation and improvement."
tags: [plan, mvp, roadmap]
timestamp: 2026-10-02T21:00:00Z
---

# MVP first, then daily iteration (apologetics)

The canonical plan is in the theology implant —
[brain://theology/plans/mvp-then-iteration.md](/plans/mvp-then-iteration.md)
— because the book spine it builds on lives there. This page states the
apologetics side and keeps it searchable from this implant. Tom's instruction
(MVP first, then iterate) is recorded in
[journals/2026-09-25.md](../journals/archive/2026/09/2026-09-25.md).

## What "lovable" means here

Tom can ask in English and get the Finnish material back. That works because
the embedding model is multilingual, not because the text is translated. So a
page that is Finnish, mechanically converted, and *linked into the graph* is
already valuable; a perfect isolated page is not. Hence the order:
algorithmic first (costs machine time), LLM second (costs tokens, arrives in
cooldown-sized batches).

## MVP for this implant

1. **Converter** — `skills/tools/apowiki_convert.py`: wikitext → markdown with
   OKF frontmatter. Deterministic mapping: `== H ==` → `## H`, `''x''` →
   `*x*`, `'''x'''` → `**x**`, wiki links become implant links via the slug function, `<ref>` →
   footnote, `{{viitteet}}` → a References heading. Templates outside the
   known set stay as visible raw markup — degradation must be *seen*, never
   silent.
2. **Slugs from one source of truth** — reuse the importer's slug function and
   its collision map (the `-v2` disambiguation from the journal entry of
   2026-09-24), or conversion invents a second, conflicting naming scheme.
3. **Links that land** — 845 of 848 files carry wiki links, 6 798 of them.
   Resolvable targets become implant links; unresolvable ones become red links
   that grep can list. Redirects resolve to their target and are not imported.
   Namespace prefixes map to their own folders: `AW:S#term` (ApoWiki's
   glossary) lands on [knowledge/glossary/sanasto.md](../knowledge/glossary/sanasto.md),
   `Luokka:` on the topic pages; `wp:` becomes an external Wikipedia URL.
4. **The book spine** — one article per biblical book, generated from the same
   canonical list theology uses, each book bound to its testament and to the
   theology spine across the federation boundary; the `Luokka:Kirjat` corpus
   hangs off those books. Apocrypha sit outside the spine as ordinary
   articles that link to a canon book, never a load-bearing rung of it.

   brainpick 0.8.6 (released the day this plan was written) supplies the
   machinery for exactly this binding, so use it rather than improvise:
   a registry entry may carry `access = "read-only"`, which makes `brain_write`
   refuse with a redirect and turns `brain_sync` into a pure mirror — correct
   for mounting a spine owned by the sibling implant; `brain_read` returns
   *annotations*, the docs in the cortex and other mounted implants whose `brain://` links point
   at the page being read, so a book page here surfaces the theology pages that
   reference it without a second lookup; and `brain_contribute` + `brain_submit`
   propose fixes to the sibling through *its* contract instead of writing to its
   origin. Upgrade brainpick before the federation pass.
5. **Multilingual embeddings** — `ollama pull bge-m3` then `brainpick init`;
   without this the MVP does not exist, because cross-language retrieval is
   the entire reason Finnish-first is allowed.
6. **Gate** — contract green, implant compiled and served, Tom using it. Then
   translation starts. On 2026-10-01 Tom dropped the gate as a blocker
   ([journal](../journals/archive/2026/10/2026-10-01.md)): he dogfoods the implant in
   parallel, and what he finds lands in todo/open.md as bug fixes.

## The daily loop after the gate

One themed slice per cooldown burst: machine-translate it to English, then
improve that slice (ground claims, close red links, add links), commit. Themed
rather than alphabetical, so each burst finishes a coherent sub-domain instead
of leaving fifty half-touched ones. Expect days, not hours — the plan assumes
that and does not depend on the translation being fast, only on the gate being
early.

## Which models translate

Decided on 2026-09-27 ([journal](../journals/archive/2026/09/2026-09-27.md)): translation
runs on a small local model, and frontier tokens go only to review. The
procedure and its reasoning are in
[Translate an article](../skills/translate-an-article.md). In short:

* A local 9B model translates the prose. It is free to run, but slow
  (about 4 tokens a second on a CPU-only host), so a batch runs as an
  overnight background job, not inside a session.
* ApoWiki's official glossary fixes the vocabulary.
  [english.md](../knowledge/glossary/english.md) records the one English
  rendering of each term, and the translator checks that its output uses
  it.
* Links, footnote markers and glossary terms are checked mechanically. A
  chunk that fails keeps its Finnish original, visibly marked.
* The cooldown-limited frontier model reviews a batch against the Finnish
  instead of writing it. That changes what a cooldown burst is for: it
  covers several machine-translated slices instead of one.

## Where English pages live, and in what order

Decided on 2026-10-01 ([journal](../journals/archive/2026/10/2026-10-01.md)):

* **knowledge/en/, under the Finnish file name.** `articles/x.md` becomes
  `en/x.md`. The folder sits at the same depth as `articles/`, so links to
  topics, books and the glossary need no change. Article links point at the
  English page when there is one and at `../articles/x.md` until then;
  `skills/tools/apowiki_land.py` rewrites them after every batch and
  generates `en/index.md`. The Finnish page stays the source of truth, and
  the English page names it in `translated_from:`. Slugs stay Finnish because
  every inbound link, citation and theology annotation uses them.
* **Theme order: most-linked first.** A theme's weight is the number of
  inbound links to its member articles (measured 2026-10-01). Batches go:
  1. *suunnitteluteoria* (design theory): 39 articles, 217 inbound links,
     and the corpus's most-linked page
  2. *jumala* and *teismi* with the *argumentit*: God and the arguments
     for his existence
  3. *ateismi*
  4. *evoluutioteoria*, with abiogenesis and common descent
  5. *jeesus* and *raamattu*: the resurrection and the reliability of the
     New Testament
  6. *filosofia* and *maailmankatsomus*
  7. *seksuaalietiikka*
  8. the rest by the same measure

  *henkilöt* and *kirjat* are not batches of their own: a person or a book
  goes with the theme that links to it most. The first batch is the six
  most-linked design-theory articles (about 16 000 words), sized for one
  overnight run of the local model.

## Status and how to resume

Kept current so that work can pick up from the repository alone, without
the conversation that produced it. The work queue is
[todo/open.md](../todo/open.md), and the most recent journal says what
happened last.

**Done (as of 2026-09-27):**

* Phases 0–3 of the queue: history import, conversion (471 articles,
  5 111 footnotes), topics, the 66-book spine bound to theology, bge-m3
  vectors.
* ApoWiki's glossary is in: raw source in
  `raw/apowiki-project/sanasto.wiki`, converted to
  [sanasto.md](../knowledge/glossary/sanasto.md). The 401 `AW:S#term`
  links in articles now land there instead of being dropped.
* The translation tooling exists and has been tried on one article (see
  the journal of 2026-09-27).
* The corpus hangs off the book spine: 1 297 scripture references link to
  their book page, and each book page lists the articles citing it. The
  cross-implant annotations were verified live in both directions. Theology
  now carries Raamattu 1933/38 and the Textus Receptus beside the KJV.

**Next, in order:**

1. Machine-time polish is done (glossary terms, red links, tables;
   2026-10-01). So is the translation setup (above).
2. Translation batches one theme at a time, per the skill. As of
   2026-10-02: batch 1 (design theory) has four of six articles reviewed
   and landed in [knowledge/en/](../knowledge/en/index.md); batches 2–4
   (God and the arguments, atheism, evolution) have their glossary rows
   and run unattended behind it. The exact state is in todo/open.md.
3. Between batches, the pages the graph asks for, per the
   [wanted-page skill](../skills/write-a-wanted-page.md); the ones written
   so far are listed in [knowledge/pages/](../knowledge/pages/index.md).

Tom dogfoods in parallel and is not a gate (decided 2026-10-01). His bug
reports go to the top of todo/open.md and take priority over polish.

**To resume on any machine:**

1. `git pull`, then `brainpick compile --root .` from the repository root.
   Run `brainpick compile --root . --only t2` in the background if
   `brainpick doctor --root .` says the vectors are stale. It needs an
   embedding endpoint (bge-m3) in the gitignored `brainpick.local.toml`.
2. Register this implant beside its sibling so the book spine resolves:
   the theology implant must also be registered (`brainpick register`).
3. The conversion is regenerable. `_temp/apowiki-cache/` is not committed,
   so re-create it with `skills/tools/apowiki_fetch.py` before re-running
   `apowiki_convert.py`. The procedure is in
   [Convert ApoWiki wikitext](../skills/convert-apowiki-to-articles.md).
4. Work down todo/open.md top to bottom, record in today's journal, and
   commit through the contract.
5. The translation runs are machine-local and live only in `_temp/`: a
   private llama-server and one runner script per batch
   (`_temp/run-batches.sh`, `run-batch3.sh`, `run-batch4.sh`), each logging
   beside itself. On another machine, or after a reboot, start the server
   per the [translate skill](../skills/translate-an-article.md) and
   re-create a runner from the article lists in todo/open.md; a runner skips
   any article already in `_temp/translations/`.
