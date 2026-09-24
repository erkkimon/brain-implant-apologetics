# Raw

Undistilled source material: transcripts, exports, clippings, data dumps —
what knowledge pages ground on and what future distillation reads. No
frontmatter, no links required, but orderly: kebab-case names that say what
a file is, listed here, pruned once distilled or proved worthless. brainpick
excludes this folder from search results; grep it.

## Folders

* `apowiki-export/` — the faithful export of ApoWiki's wikitext source and revision metadata, imported under GFDL-1.3-or-later. Each file carries the GFDL notice required by the license; the `gfdl-notice` henxel enforces this.

## ApoWiki wikitext is kept as wikitext

The export stores the original MediaWiki wikitext **unconverted** — no
markdown translation, no template expansion, no interwiki rewriting. Three
reasons, in order of weight:

1. **It is the most defensible form.** Raw wikitext is what ApoWiki actually
   published, byte for byte. A conversion is an editorial act, and mixing it
   into the import would blur the line between "what the contributors wrote"
   and "what we made of it". Keeping them separate means the provenance claim
   survives any later disagreement about the conversion.
2. **Nothing is lost by it.** brainpick excludes `raw/` from search results
   and does not render it, so a converted copy here would buy no capability —
   it would be formatted text either way, with no engine magic applied.
   Conversion pays off only where it lands: in `knowledge/`.
3. **It is simpler.** One fewer pipeline stage, one fewer thing to get wrong,
   one fewer thing to re-run when the conversion rules change.

Distillation into `knowledge/` reads this folder and cites the MediaWiki
revision id it worked from, so any article can be traced back to the exact
source text behind it.
