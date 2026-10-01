---
type: skill
title: Write a wanted page
description: "Use when closing an ApoWiki red link by writing the page the wiki never had: Finnish first, every claim footnoted to a pinned source revision, NPOV, saved in knowledge/pages/ with aliases so the converter links the red links there."
timestamp: 2026-10-02T00:00:00Z
depends_on: [skills/convert-apowiki-to-articles.md]
tools:
  - skills/tools/apowiki_convert.py
---

# Write a wanted page

ApoWiki links to 584 titles it never wrote. 254 of them have no page
anywhere: not in the wiki, not in its glossary, not in the Finnish Wikipedia.
Those are the wanted pages, and `todo/open.md` lists them by inbound links.
The plan closes them theme by theme alongside each translation batch
([plan](../plans/mvp-then-iteration.md)); the first three were written on
2026-10-02 ([journal](../journals/2026-10-02.md)).

## Steps

1. **Pick the most-linked target in the current theme.** Read every
   sentence that links to it (`grep -o '.\{200\}<!-- red link: X -->'
   knowledge/articles/*.md`). The page has to answer what those sentences
   need, which is usually who the person is and why the article mentions
   them.
2. **Find a source with a pinned revision**
   ([every claim carries its receipt](../conventions/every-claim-carries-its-receipt.md)).
   A Wikipedia article is cited by its `oldid` permalink, which the
   MediaWiki API returns with
   `action=query&prop=revisions&rvprop=ids|timestamp`. Prefer the
   subject's own publications for what they hold, and a neutral or critical
   source for how others judge them.
3. **Write it in Finnish**, in the style of the converted articles: the
   same frontmatter (`type: article`, `about: apologetics`, `tags` including
   `written-here`), a comment naming the source revision, the topic line,
   then prose. Every sentence that makes a claim ends in a footnote.
   * **NPOV.** ApoWiki is an apologetics wiki, but this page is a reference
     page. State what the subject holds, then what critics and courts hold,
     each attributed. Don't adopt a judgment from the source's voice either:
     "pseudoscientific" stays the source's word, attributed, or is left out.
   * Link back to the ApoWiki articles that mention the subject, so a page
     written here is never an orphan.
4. **Save it in `knowledge/pages/<slug>.md`** and list it in
   `knowledge/pages/index.md`. Put every spelling the wiki used in
   `aliases:`, because the wiki wrote "Discovery instituutti", "Discovery-
   instituutti" and "Discovery Institute" for the same thing.
5. **Regenerate the corpus** (the order is in
   [the convert skill](convert-apowiki-to-articles.md)). The converter
   reads `title` and `aliases` and links those red links to the page; its
   summary line counts them. Check that the count went up by the number of
   links the page should answer.

Pages here are never overwritten by the converter. They get translated like
any article, when their theme's batch comes up.
