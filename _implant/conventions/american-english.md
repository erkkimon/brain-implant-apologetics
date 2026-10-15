---
type: convention
about: concept
title: American English
description: "English pages use American spelling (color, behavior, analyze, skeptic, defense, program, toward). Quotations of an author's own English keep their spelling, and so do titles; quotations we translate from Finnish follow the rule."
tags: [convention, translation, english, spelling]
timestamp: 2026-10-15T18:48:41Z
half_life: 0
---

# American English

Tom chose American spelling for the English pages on 2026-10-15
([journal](../journals/2026-10-15.md)). Before that the reviewed pages mixed
the two: *colour* and *color*, *sceptic* and *skeptic*.

The rule:

* **Our own English is American.** This covers every translated article in
  [knowledge/en/](../knowledge/en/index.md), including quotations that we
  translated from Finnish, and every page the implant writes in English.
  Examples: *color*, *behavior*, *favorable*, *analyze*, *criticize*,
  *skeptic*, *defense*, *judgment*, *program*, *toward*, *center*.
* **Other people's English keeps its spelling.** A quotation that is
  already in English in the Finnish source is the author's text, so it is
  left as written. The same goes for titles: *Philosophical Essays In
  Defence Of …* stays *Defence*.
* **Machine-checked, not remembered.**
  `skills/tools/apowiki_american.py` converts a
  page and leaves alone link targets, HTML comments, footnote definitions,
  italic titles and quotations found verbatim in the Finnish source.
  `skills/tools/apowiki_land.py` runs it on every page it
  lands, so reviewers need not do it by hand. `--check` lists what
  remains to convert.

The converter works from a word list, not a blanket rule, because a
blanket *-ise* → *-ize* rule would break *exercise*, *promise* and *otherwise*.
A British form it does not know stays as it is. When one turns up, add it
to the list.
