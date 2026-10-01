# Skills

Procedural memory — distilled, actionable procedures an agent follows. One
kebab-case page per skill (`type: skill`), declaring `depends_on` and `tools`.
The dependency tree is generated at `skilltree.md` — edit the skills, never
the tree.

## Tools

* `tools/apowiki_fetch.py` — fetch every ApoWiki article revision into a local
  cache. Polite (rate-limited, retrying) and resumable: it hits someone else's
  server, so it is kept separate from the import, which is pure local
  computation and can be re-run freely.
* `tools/apowiki_import.py` — replay cached revisions as git commits carrying
  the real contributor, the real timestamp and the MediaWiki revision id.
  Pseudonymises bare-IP authors and writes the real addresses only to the
  gitignored provenance sidecar.
* `tools/apowiki_convert.py` — convert the wikitext export into Finnish
  articles in `knowledge/articles/`: links resolved through the importer's
  slug map, citations as footnotes, redirects resolved, red links reported
  (or linked to a page written here in `knowledge/pages/`).
* `tools/apowiki_topics.py` — turn ApoWiki's categories into topic pages in
  `knowledge/topics/` and give every article a breadcrumb back to them.
* `tools/apowiki_glossary.py` — ApoWiki's official glossary
  (`ApoWiki:Sanasto`) into `raw/apowiki-project/` and
  `knowledge/glossary/sanasto.md`, one anchor per term, so the articles'
  `AW:S#term` links land.
* `tools/apowiki_redlinks.py` — look red-link targets up in the Finnish
  Wikipedia and record the hits in `tools/red-link-wikipedia.json` for
  review; the converter links reviewed hits there and keeps them red.
  `--lang en` fills `tools/red-link-wikipedia-en.json` from the English
  Wikipedia for the targets Finnish lacks.
* `tools/apowiki_stamp.py` — after regenerating, restore the committed
  timestamp on every page that did not change and bump the rest.
* `tools/apowiki_translate.py` — translate one article with a small local
  model, checking links, footnotes and glossary terms chunk by chunk.
* `tools/apowiki_land.py` — land translated pages in `knowledge/en/`,
  point their article links at English or Finnish pages, regenerate
  `en/index.md`.
* `tools/apowiki_books.py` — the book spine: 66 book pages and two testament
  pages in `knowledge/books/`, bound to the theology implant's spine.

## Procedures

* [Translate an article into English](translate-an-article.md) — a small
  local model writes the prose, ApoWiki's glossary fixes the terms, and
  deterministic checks decide what is accepted. Frontier tokens go only to review.
* [Convert ApoWiki wikitext into implant articles](convert-apowiki-to-articles.md)
  — the token-free conversion that produces the MVP.
