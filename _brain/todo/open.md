---
type: todo
title: Open
description: What is still to be done — the brain's live work queue.
timestamp: 2026-09-26T10:20:00Z
---

# Open

Tasks that surface mid-work land here instead of derailing the task at hand.
Check this list before planning new work. Tick an item as `- [x] … (done:
YYYY-MM-DD)` and move it to `archive/YYYY-MM-DD.md` the same or the next day.

Plan behind this list: [../plans/mvp-then-iteration.md](../plans/mvp-then-iteration.md).
Phases 1–3 are machine time (run them, spend no tokens). Phase 4 is the gate.
Everything after the gate is token work, one themed batch per cooldown burst.

## Phase 1 — Algorithmic conversion (machine time)

Done 2026-09-25 — see [archive/2026-09-25.md](archive/2026-09-25.md). Left over:

- [ ] Re-fetch ApoWiki's project namespace (`ApoWiki:Sanasto`, the glossary): 414 `AW:S#term` links point into it, and the fetch took only the main namespace, so they currently render as plain text
- [ ] Filter vandalism categories (e.g. `vandalismi`) out of the tags and topics

## Phase 2 — The book spine (machine time)

Rungs generated 2026-09-26 by `skills/tools/apowiki_books.py`: 66 books + 2
testaments in `knowledge/books/`, each pointing at the theology spine.

- [ ] Declare the theology implant as a read-only mount (`access = "read-only"`, alias `theology`) in the brain registry on each machine, then check that `brain_read` on a theology book page shows this brain's rung as an annotation
- [ ] Hang the `Luokka:Kirjat` book-corpus articles (the *kirja* reviews) off the biblical books they discuss, where they discuss one
- [ ] Mirror the binding from the theology side: each theology book page links to its Finnish rung here (theology's own todo)

## Phase 3 — Make Finnish findable by English queries (machine time)

- [ ] Confirm tier-2 vectors built with `bge-m3` (`brainpick compile` no longer reports search `degraded from semantic`) and spot-check that English queries return Finnish articles

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
