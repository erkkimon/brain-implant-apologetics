---
type: todo
title: Open
description: What is still to be done — the implant's live work queue.
timestamp: 2026-10-02T04:40:51Z
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

- [ ] Before each translation batch, fill `knowledge/glossary/english.md` rows for the glossary terms that batch uses (252 of 413 terms still lack one; `apowiki_translate.py --dry-run` lists them per chunk). Batch 1's, batch 2's (God and the arguments, 28 rows) and batch 3's (atheism, 25 rows) are in, the last two added 2026-10-02; batch 4's (evolution, 16 rows) followed the same day; 161 of 413 terms now have English.
- [ ] Batch 1 (design theory, 6 articles; william-dembski landed and reviewed 2026-10-01, teleologinen-argumentti, tarkoituksellisuuspäättelyn-logiikka and the-edge-of-evolution-kirja 2026-10-02; kosminen-hienosäätö and suunnitteluteoria remain). Since 2026-10-02 the rest run with batch 2 as `_temp/run-batches.sh` (two passes, log `_temp/batches.log`) on a private llama-server (`_temp/llama-server.log`; see the translate skill, step 4), because the shared Ollama sat on another job's embedding model. Restart: start llama-server again, then `setsid nohup _temp/run-batches.sh`. It skips finished articles. When an article lands in `_temp/translations/`: review it against the Finnish, `apowiki_land.py`, commit. Keep landed files in `_temp/translations/`: the runner reads them as done.
- [ ] Batch 2 (God and the arguments, 13 articles, about 15 500 words; *alvin-plantinga*, 12 000 words, gets a run of its own later): runs after batch 1 in `_temp/run-batches.sh`. Glossary rows done. Review and land as for batch 1.
- [ ] Batch 3 (atheism, 9 articles, about 21 800 words: ateismi, richard-dawkins, pascalin-peliteoria, jumalharha-kirja, ateismin-falsifioitavuus, ateismin-määritelmä, tapio-puolimatka-uusateismin-tunnekieli, uusateismi, projektiivinen-ateistinen-teoria; antony-flew is already in batch 2). Glossary rows done 2026-10-02 (25 rows; the terms left free are listed on the English glossary page). Queued in `_temp/run-batch3.sh`, which waits for `run-batches.sh` to finish and logs to `_temp/batch3.log`. Review and land as for batch 1.
- [ ] Batch 4 (evolution, 12 articles, about 18 000 words: evoluutioteoria, evoluution-määritelmä, polveutumisoppi, perinnöllisen-muuntelun-mekanismit, evoluutioteorian-historia, kambrikauden-räjähdys, monimutkaisten-järjestelmien-synty, evoluution-ehdot, konvergenssi, nailonbakteerit, darwins-black-box-kirja, icons-of-evolution-kirja; the long critiques and book reviews of the theme, such as evoluutioteorian-vastaiset-argumentit and eliömaailma-rappeutuu-kirja, get runs of their own later). Glossary rows done 2026-10-02. Queued in `_temp/run-batch4.sh` (2026-10-02), which waits for the batch 1–3 runners to finish and logs to `_temp/batch4.log`; restart it the same way as the others if the host reboots. Review and land as for batch 1.
- [ ] Per batch: machine-translate one themed slice to English → improve that slice (ground claims, close its red links, enrich links) → commit. Themed, not alphabetical.
- [ ] Create the pages the graph asks for, per the [wanted-page skill](../skills/write-a-wanted-page.md). Done on 2026-10-02 (knowledge/pages/): Paul Nelson, Michael Denton, Discovery Institute, *Älykkään suunnitelman idea*, Guillermo Gonzalez, Jay W. Richards, Stanley Jaki. Batch 2's: the three cosmological-argument subtypes (2026-10-02). Phillip Johnson and Jonathan Wells (2026-10-02). Red links with no Finnish Wikipedia page fall back to the English one (2026-10-02). Next: the most-linked bare targets of each theme as its batch comes up (`_temp/convert-report.json` lists them after a convert run). *Nasaretilaisen haaste*, *Myytti apinaihmisistä*, *Voimat vastakkain*, *Valokuva Jeesuksesta?*, *The Guards of the Tomb*, *Evoluution maailmankuva*, *The Resurrection of the Son of God*, *The Design Inference*, *Darwin on Trial*, *No Free Lunch*, *Evolution: A Theory in Crisis*, *Agents Under Fire*, *Dawkinsin jumala*, *Dawkins-harha?*, *Paholaisen kirjeopisto* and *Muistiinpanoja surun ajalta* written 2026-10-02 from ApoWiki's citations and a bookseller's record of the 2026 edition (Finna still behind a bot check); a library record of the 2000 edition would still improve it. Red links that map to Wikipedia by meaning were added by hand the same day (fallacies, people by surname, typos): 603 red links, 374 to Finnish and 166 to English Wikipedia. The 330 others link to Finnish Wikipedia but stay wanted. Do it with the translation batch that touches the theme, since a new page is token work

## Deferred (after the MVP, still open)

- [ ] Port the Bayesian appraisal tool from stem (via the federated common implant, once created)
- [ ] Establish the shared common implant (brain-implant-common) holding the appraisal tool + its governing convention
