---
type: plan
title: "MVP first, then daily iteration (apologetics)"
description: "The apologetics half of the shared plan: convert ApoWiki's wikitext to Finnish markdown pages with parsed implant links, hang the book corpus on the shared book spine, compile with multilingual embeddings, and only then start cooldown-batched translation and improvement."
tags: [plan, mvp, roadmap]
timestamp: 2026-09-27T10:00:00Z
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
   Namespace prefixes (`AW:S`, `Luokka:`) map to their own folders; `wp:`
   becomes an external Wikipedia URL.
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
   translation starts.

## The daily loop after the gate

One themed slice per cooldown burst: machine-translate it to English, then
improve that slice (ground claims, close red links, add links), commit. Themed
rather than alphabetical, so each burst finishes a coherent sub-domain instead
of leaving fifty half-touched ones. Expect days, not hours — the plan assumes
that and does not depend on the translation being fast, only on the gate being
early.
