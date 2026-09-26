---
type: todo
title: Open
description: What is still to be done — the brain's live work queue.
timestamp: 2026-09-25T00:00:00Z
---

# Open

Tasks that surface mid-work land here instead of derailing the task at hand.
Check this list before planning new work. Tick an item as `- [x] … (done:
YYYY-MM-DD)` and move it to `archive/YYYY-MM-DD.md` the same or the next day.

Plan behind this list: [../plans/mvp-then-iteration.md](../plans/mvp-then-iteration.md).
Phases 1–3 are machine time (run them, spend no tokens). Phase 4 is the gate.
Everything after the gate is token work, one themed batch per cooldown burst.

## Phase 1 — Algorithmic conversion (machine time)

- [ ] Write `skills/tools/apowiki_convert.py`: wikitext → markdown + OKF frontmatter (`type: article`, `title`, quoted `description`, `timestamp`, `tags`), source permalink and the GFDL notice in a leading HTML comment
- [ ] Map markup deterministically: headings, `''italic''`, `'''bold'''`, lists, tables, `<ref>` → footnotes, `{{viitteet}}` → References heading; unknown templates stay as visible raw markup (never silently dropped)
- [ ] Resolve the 156 `#REDIRECT` files to their targets instead of importing them as pages
- [ ] Rewrite the 6 798 `[[links]]` across 845 files as brain links, reusing the importer's slug function **and its `-v2` collision map** so slugs have one source of truth
- [ ] Map namespaces: `Luokka:X` → a `knowledge/topics/` grouping page, `AW:S` → an internal article, `wp:X` → external Wikipedia URL
- [ ] Emit unresolvable targets as red links (visible, greppable) and write a report of how many there are — that report is the backlog for the improvement loop
- [ ] Land the converted Finnish articles in `knowledge/` and make every link land (`brainpick compile` reports zero ghosts)

## Phase 2 — The book spine (machine time)

- [ ] Copy or share the canonical book list (`bookcodes.py` in the theology implant) so both implants use one canon
- [ ] Generate one article per biblical book in `knowledge/books/`, each bound to its testament article
- [ ] Bind each book article across the federation boundary to the matching article in the theology implant (`{brain://theology}` suffix form)
- [ ] Hang the `Luokka:Kirjat` book-corpus articles off their biblical book articles
- [ ] Declare the theology implant under `[brains]` in `brainpick.toml` with a stable id, and keep apocrypha outside the spine (ordinary articles that link to canon, never a rung of it)

## Phase 3 — Make Finnish findable by English queries (machine time)

- [ ] `ollama pull bge-m3` and rerun `brainpick init` — the detected `nomic-embed-text` is English-only and this brain is Finnish
- [ ] Rebuild the tier-3 vectors and spot-check that English queries return Finnish articles

## Phase 4 — The MVP gate

- [ ] `henxels check --all` green, brain compiled, served with `brainpick init`
- [ ] Tom uses it for a real question and calls it lovable — **do not start spending translation tokens before this**

## Phase 5+ — Daily iteration (token work, one batch per cooldown burst)

- [ ] Decide the theme order for translation batches (suggested: the highest-link hubs first — Plantinga, Puolimatka, suunnitteluteoria — so each batch strengthens the graph most)
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] First improvement pass on the red-link report from Phase 1: create the pages the graph asked for
- [ ] Fix conversion degradation where the visible raw markup shows it is worth fixing (tables, exotic templates)

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common brain, once created)
- [ ] Establish the shared common brain (brain-implant-common) holding the appraisal tool + its governing convention
