---
type: todo
title: Open
description: What is still to be done — the implant's live work queue.
timestamp: 2026-10-01T21:00:00Z
---

# Open

Tasks that surface mid-work land here instead of derailing the task at hand.
Check this list before planning new work. Tick an item as `- [x] … (done:
YYYY-MM-DD)` and move it to `archive/YYYY-MM-DD.md` the same or the next day.

Plan behind this list: [../plans/mvp-then-iteration.md](../plans/mvp-then-iteration.md).
Phases 1–3 are machine time (run them, spend no tokens). Phase 4 is no longer
a gate (Tom, 2026-10-01): he dogfoods in parallel, and his bug reports go under
"Bugs from dogfooding" and come first. Translation is one themed batch per
cooldown burst.

## Bugs from dogfooding

(none reported yet)

## Phase 1 — Algorithmic conversion (machine time)

Done 2026-09-25 — see [archive/2026-09-25.md](archive/2026-09-25.md). Nothing left over.

## Phase 2 — The book spine (machine time)

Rungs generated 2026-09-26 by `skills/tools/apowiki_books.py`: 66 books + 2
testaments in `knowledge/books/`, each pointing at the theology spine.

- [ ] Register the theology implant on each other machine (`brainpick register <repo>/_implant --implant --alias theology`, plus `--read-only` where the user is not its author), then check that `brain_read` on a theology book page shows this brain's rung as an annotation

## Phase 3 — Make Finnish findable by English queries (machine time)


## Phase 4 — Dogfooding (not a gate)

- [ ] Tom uses it on real questions; every rough edge becomes an item under "Bugs from dogfooding"

## Phase 5+ — Daily iteration (token work, one batch per cooldown burst)

- [ ] Before each translation batch, fill `knowledge/glossary/english.md` rows for the glossary terms that batch uses (321 of 413 terms still lack one; `apowiki_translate.py --dry-run` lists them per chunk). Batch 1's rows are in
- [ ] Batch 1 (design theory, 6 articles; william-dembski landed and reviewed 2026-10-01, the rest running as `_temp/run-batch1.sh`, log in `_temp/batch1.log`; re-run the script if it died, it skips finished ones: suunnitteluteoria, william-dembski, kosminen-hienosäätö, teleologinen-argumentti, the-edge-of-evolution-kirja, tarkoituksellisuuspäättelyn-logiikka): machine run → review against the Finnish (translate title and description, fix failed chunks, set `translation_status: reviewed`) → `apowiki_land.py` → commit
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] Create the pages the graph asks for. 254 red-link targets (273 links) still have no target at all; the most wanted are *Nasaretilaisen haaste* (5), *Paul Nelson* (3) and a run of ID-movement people and books (Denton, Jaki, Gonzalez, Richards, Discovery Institute). The 330 others link to Finnish Wikipedia but stay wanted. Do it with the translation batch that touches the theme, since a new page is token work

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common implant, once created)
- [ ] Establish the shared common implant (brain-implant-common) holding the appraisal tool + its governing convention
