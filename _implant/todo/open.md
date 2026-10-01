---
type: todo
title: Open
description: What is still to be done — the implant's live work queue.
timestamp: 2026-10-02T00:30:00Z
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
- [ ] Batch 1 (design theory, 6 articles; william-dembski landed and reviewed 2026-10-01, the rest running as `_temp/run-batch1.sh`, then a retry pass `_temp/run-batch1b.sh`, log in `_temp/batch1.log`; re-run `run-batch1.sh` if both died, it skips finished ones. Throughput depends on how busy the shared CPU host is: on 2026-10-01/02 two articles timed out while the host was saturated: suunnitteluteoria, william-dembski, kosminen-hienosäätö, teleologinen-argumentti, the-edge-of-evolution-kirja, tarkoituksellisuuspäättelyn-logiikka): machine run → review against the Finnish (translate title and description, fix failed chunks, set `translation_status: reviewed`) → `apowiki_land.py` → commit
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] Create the pages the graph asks for, per the [wanted-page skill](../skills/write-a-wanted-page.md). Paul Nelson, Michael Denton and Discovery Institute are done (knowledge/pages/, 10 links, 2026-10-02). Next for design theory: Jaki, Gonzalez, Richards. *Nasaretilaisen haaste* (5 links, Kankaanniemi 2000, ISBN 952-5374-00-9) belongs with the Jesus batch and needs a library record; Finna's API answered scripted requests with a Cloudflare challenge. The 330 others link to Finnish Wikipedia but stay wanted. Do it with the translation batch that touches the theme, since a new page is token work

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common implant, once created)
- [ ] Establish the shared common implant (brain-implant-common) holding the appraisal tool + its governing convention
