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
