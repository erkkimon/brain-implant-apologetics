---
type: todo
title: Open
description: What is still to be done — the implant's live work queue.
timestamp: 2026-10-02T12:00:00Z
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

- [ ] Before each translation batch, fill `knowledge/glossary/english.md` rows for the glossary terms that batch uses (268 of 413 terms still lack one; `apowiki_translate.py --dry-run` lists them per chunk). Batch 1's, batch 2's (God and the arguments, 28 rows) and batch 3's (atheism, 25 rows) are in, the last two added 2026-10-02; 145 of 413 terms now have English.
- [ ] Batch 1 (design theory, 6 articles; william-dembski landed and reviewed 2026-10-01, teleologinen-argumentti and tarkoituksellisuuspäättelyn-logiikka 2026-10-02). Since 2026-10-02 the rest run with batch 2 as `_temp/run-batches.sh` (two passes, log `_temp/batches.log`) on a private llama-server (`_temp/llama-server.log`; see the translate skill, step 4), because the shared Ollama sat on another job's embedding model. Restart: start llama-server again, then `setsid nohup _temp/run-batches.sh`. It skips finished articles. When an article lands in `_temp/translations/`: review it against the Finnish, `apowiki_land.py`, commit.
- [ ] Batch 2 (God and the arguments, 13 articles, about 15 500 words; *alvin-plantinga*, 12 000 words, gets a run of its own later): runs after batch 1 in `_temp/run-batches.sh`. Glossary rows done. Review and land as for batch 1.
- [ ] Batch 3 (atheism, 9 articles, about 21 800 words: ateismi, richard-dawkins, pascalin-peliteoria, jumalharha-kirja, ateismin-falsifioitavuus, ateismin-määritelmä, tapio-puolimatka-uusateismin-tunnekieli, uusateismi, projektiivinen-ateistinen-teoria; antony-flew is already in batch 2). Glossary rows done 2026-10-02 (25 rows; the terms left free are listed on the English glossary page). Queued in `_temp/run-batch3.sh`, which waits for `run-batches.sh` to finish and logs to `_temp/batch3.log`. Review and land as for batch 1.
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] Create the pages the graph asks for, per the [wanted-page skill](../skills/write-a-wanted-page.md). Done on 2026-10-02 (knowledge/pages/): Paul Nelson, Michael Denton, Discovery Institute, *Älykkään suunnitelman idea*, Guillermo Gonzalez, Jay W. Richards, Stanley Jaki. Batch 2's: the three cosmological-argument subtypes (2026-10-02). Phillip Johnson and Jonathan Wells (2026-10-02). Red links with no Finnish Wikipedia page fall back to the English one (117 targets, 2026-10-02). Next: the most-linked bare targets of each theme as its batch comes up (`_temp/convert-report.json` lists them after a convert run). *Nasaretilaisen haaste* (5 links, Kankaanniemi 2000, ISBN 952-5374-00-9) belongs with the Jesus batch and needs a library record; Finna's API answered scripted requests with a Cloudflare challenge. The 330 others link to Finnish Wikipedia but stay wanted. Do it with the translation batch that touches the theme, since a new page is token work

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common implant, once created)
- [ ] Establish the shared common implant (brain-implant-common) holding the appraisal tool + its governing convention
