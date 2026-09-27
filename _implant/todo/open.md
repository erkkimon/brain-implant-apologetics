---
type: todo
title: Open
description: What is still to be done — the implant's live work queue.
timestamp: 2026-09-27T14:00:00Z
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

- [ ] Glossary links to terms the Sanasto page does not define (41 distinct, e.g. *usko*, *looginen*, *monoteismi*; listed under `missing_glossary_terms` in `_temp/convert-report.json`) land on the glossary page itself. Decide per term whether a Wikipedia link or a new glossary-style page serves better
- [ ] Filter vandalism categories (e.g. `vandalismi`) out of the tags and topics

## Phase 2 — The book spine (machine time)

Rungs generated 2026-09-26 by `skills/tools/apowiki_books.py`: 66 books + 2
testaments in `knowledge/books/`, each pointing at the theology spine.

- [ ] Register the theology implant on each other machine (`brainpick register <repo>/_implant --implant --alias theology`, plus `--read-only` where the user is not its author), then check that `brain_read` on a theology book page shows this brain's rung as an annotation

## Phase 3 — Make Finnish findable by English queries (machine time)


## Phase 4 — The MVP gate

- [ ] `henxels check --all` green, implant compiled, served with `brainpick init`
- [ ] Tom uses it for a real question and calls it lovable — **do not start spending translation tokens before this**

## Phase 5+ — Daily iteration (token work, one batch per cooldown burst)

- [ ] Before each translation batch, fill `knowledge/glossary/english.md` rows for the glossary terms that batch uses (358 of 413 terms still lack one; `apowiki_translate.py --dry-run` lists them per chunk)
- [ ] Decide where English pages live (a sibling `articles-en/` folder or `lang`-suffixed files) with the first batch, and record it in the plan
- [ ] Decide the theme order for translation batches (suggested: the highest-link hubs first — Plantinga, Puolimatka, suunnitteluteoria — so each batch strengthens the graph most)
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] First improvement pass on the red-link report from Phase 1: create the pages the graph asked for
- [ ] Fix conversion degradation where the visible raw markup shows it is worth fixing (tables, exotic templates)

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common implant, once created)
- [ ] Establish the shared common implant (brain-implant-common) holding the appraisal tool + its governing convention
