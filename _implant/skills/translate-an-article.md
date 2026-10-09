---
type: skill
title: Translate an article into English
description: "Use when translating a converted Finnish ApoWiki article into English: a small local model does the prose, ApoWiki's own glossary (Sanasto) fixes the terminology, and deterministic checks (links, footnotes, glossary terms) decide whether a chunk is accepted. Frontier-model tokens are spent only on review."
timestamp: 2026-10-09T00:07:48Z
depends_on: [skills/convert-apowiki-to-articles.md]
tools:
  - skills/tools/apowiki_glossary.py
  - skills/tools/apowiki_translate.py
  - skills/tools/apowiki_land.py
---

# Translate an article into English

Tom dropped the gate on 2026-10-01 and dogfoods the implant in parallel
([the plan](../plans/mvp-then-iteration.md)). The Finnish pages are already
searchable in English because the embeddings are multilingual, so
translation improves reading, not finding.

## Why a small model is enough, and where it is not

The work splits in two:

* **Turning Finnish prose into English.** A small model does this
  acceptably. A trial on 2026-09-27 ([journal](../journals/archive/2026/09/2026-09-27.md))
  had a 4B and a 9B Qwen 3.5 translate the same two paragraphs of *Pahan
  ongelma*. Both produced fluent, faithful English for the argument itself.
* **Everything that must survive.** A small model does this badly, and
  silently. In the same trial both models dropped a link
  (to the C. S. Lewis article), and both invented an English title for
  a Finnish book (*Aberystwyth*, *Sorrowful Notes*). Nothing in their output
  hinted at either error.

A full run of the 9B model over the same article (1 250 words) took 20
minutes on the CPU-only host. Four of five chunks passed every check. The
fifth kept losing the Lewis link across three attempts, so it stayed in
Finnish, marked, exactly as designed.

So the model is never trusted to preserve anything.
`skills/tools/apowiki_translate.py` checks every chunk mechanically, retries
it with the failure spelled out, and if it still fails keeps the Finnish
original under a visible comment. Those checks are what make a cheap model
usable. A better model reduces retries but does not replace the checks.

## ApoWiki's vocabulary is the contract

ApoWiki keeps an official glossary, `ApoWiki:Sanasto`, which is converted to
[knowledge/glossary/sanasto.md](../knowledge/glossary/sanasto.md). Its own
rule is that articles use terms in the glossary's sense, and struck-through
senses are common usage that ApoWiki avoids. A translation that renders
*perususkomus* as "basic belief" in one article and "foundational belief" in
the next breaks the link between them. The same goes for rendering
*äärinaturalismi* as plain "naturalism", which drops the distinction the
wiki draws on purpose.

[knowledge/glossary/english.md](../knowledge/glossary/english.md) fixes one
English rendering per term. The translator puts the terms found in each
chunk into the prompt, and then checks that the English contains every one
of them. Finnish is matched by word stem, so inflected forms (*naturalismin*,
*naturalismia*) count as the term.

## Procedure

1. **Refresh the glossary** if ApoWiki has edited it:
   `python3 skills/tools/apowiki_glossary.py --fetch`. Without `--fetch` it
   regenerates from the committed raw copy. It reports how many terms still
   lack an English rendering.
2. **Pick the batch.** One themed slice, per the plan (for example the
   *suunnitteluteoria* topic), not alphabetical.
3. **Fix missing terms first.** For each glossary term the batch uses that
   has no row in `english.md`, add the row, following the rules at the top
   of that page. This is the only step that needs judgement about
   vocabulary. Doing it before translating means the checks enforce it.
   A dry run calls no model and writes nothing. It lists the glossary
   terms in the article that still have no English row:
   `python3 skills/tools/apowiki_translate.py --dry-run ARTICLE.md`.
   Not every listed term needs a row. A term that is everyday Finnish
   (*hyvä*, *käsite*, *halu*) or whose stem also catches unrelated words
   (*apologi* catches *apologia*, *agenda* catches *agentti*, *per se*
   catches *perusteella sen*) is better left free: a row would force a
   word where the model already writes the right one, or fail correct
   chunks. Such terms are listed at the end of `english.md`.
4. **Translate** with the local model. The endpoint is machine-local, so
   pass it in the environment, never in a committed file:
   `OLLAMA_HOST=http://<host>:11434 python3 skills/tools/apowiki_translate.py ARTICLE.md`.
   Output goes to `_temp/translations/`. The default model is the 9B Qwen
   3.5, the best of the models that were available in the trial. Change it
   with `--model`.
   A shared Ollama that holds one model at a time can leave the translator
   waiting behind someone else's work for hours. In that case, run
   llama.cpp's `llama-server` on the same GGUF file Ollama stores (the
   model blob named in Ollama's manifest), with `-c 8192`. Then point the
   translator at its OpenAI-compatible URL, which ends in `/v1`:
   `TRANSLATE_ENDPOINT=http://127.0.0.1:<port>/v1`. Thinking stays off on
   both backends.
   If the shared Ollama no longer has the model, fetch the same GGUF by
   digest from the Ollama registry: read the manifest at
   `https://registry.ollama.ai/v2/<namespace>/<model>/manifests/<tag>`, take
   the layer of type `application/vnd.ollama.image.model`, download
   `…/blobs/sha256:<digest>` to a machine-local cache and check its sha256
   ([journal 2026-10-09](../journals/2026-10-09.md)).
5. **Review** with a strong model or a human: read the English against the
   Finnish for meaning, especially negations and hedges (*melko varmasti*
   is "almost certainly", not "certainly"). Blocks marked
   `translation failed its checks` are translated by the reviewer. This is
   the only step that spends frontier tokens, and it reads rather than
   writes, which is cheaper.
   A translation is made from the Finnish page as it was when the run
   started. If the converter changed that page since (`git diff` the
   Finnish file from the run's start to now), carry the change over in
   review. Most such changes are formatting only, such as bullets that
   gained a space in [2026-10-02's converter
   fix](../journals/archive/2026/10/2026-10-02.md); the wording rarely changes.
   At batch scale the review fans out to subagents, one per long article
   or a few short ones together ([journal 2026-10-09](../journals/2026-10-09.md);
   batch 2's 13 articles took eight in parallel). Each reviewer edits only
   its `_temp/translations/X.md`, never runs git, and treats the *current*
   Finnish page as the source of truth, which also carries over link
   targets fixed since the run. It verifies by script that the English
   matches the Finnish exactly in five things: (a) the ordered list of link
   targets, (b) the footnote reference counts, (c) no `translation failed`
   comment remains, (d) the HTML comments as a multiset, (e) the footnote
   definition lines. The caller re-runs the same checks independently,
   spot-checks the biggest claimed fixes against the Finnish, then lands.
   The errors worth looking for, from batch 1: inverted meanings ("ei
   muodissa", out of fashion, became "not due to fashion"), swapped
   comparisons, wrong numbers (*sata triljoonaa* is 10^20), Finnish case
   endings left on names (*Dembskin*), and links the model added.
6. **Land it:** `python3 skills/tools/apowiki_land.py _temp/translations/X.md …`.
   It copies the pages to `knowledge/en/` under the Finnish file name. It
   points article links at English pages where they exist and at
   `../articles/` where they do not, and it regenerates `en/index.md`.
   It also re-points a bracketed red link at a page written later in
   `knowledge/pages/` that answers it, as the converter does for the Finnish
   page ([why](../journals/archive/2026/10/2026-10-02.md)).
   It is idempotent, so run it with no arguments to re-link after any change.
   The tool writes `lang: en`, `translated_from`, `translated_by` and
   `translation_status: machine` into the frontmatter, but leaves `title` and
   `description` in Finnish. The reviewer translates both and sets
   `translation_status: reviewed`. Commit through the contract like any
   other change. Why this layout: [the plan](../plans/mvp-then-iteration.md).

## What stays Finnish on purpose

HTML comments, including the red-link notes inside sentences: the model sees
those and must return them unchanged, which the checker enforces since the
9B model translated *Älykkään suunnitelman idea (kirja)* in one on its first
run. Book and article titles, footnote definitions (the receipts: author, title,
publisher, page, exactly as ApoWiki recorded them), and HTML comments. A
citation translated into English points at a book that does not exist.
