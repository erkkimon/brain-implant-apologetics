---
type: convention
about: concept
title: Every claim carries its receipt
description: No statement of fact enters this implant without a resolvable, verifiable citation attached to that specific statement — a DOI, a mission dataset, a pinned document revision — because the value this implant adds over a model's own memory is not the fact but the source, and a fact whose source cannot be checked is indistinguishable from a fluent guess.
tags: [convention, grounding, citation, traceability, provenance]
timestamp: 2026-09-27T10:00:00Z
half_life: 0
---

# Every claim carries its receipt

Decided by Tom on 2026-09-24, founding the apologetics implant
([journal](../journals/archive/2026/09/2026-09-24.md)): *"the traceability of the information
is fucking important. It is possible that a model is right if it states
something, but even if it is right and knows already something that is in
this brain implant, it doesn't know the source which this brain implant
gives to any LLM agent."*

That sentence is this implant's entire economic case. A capable model
already knows that C.S. Lewis was an atheist before his conversion; it
cannot tell you which letter, diary entry, or published essay establishes
that, how precisely it is dated, or what to read next. The fact is cheap.
**The receipt is the product.**

## The rule

**A claim and its citation are one unit.** A citation at the bottom of a
page, or a "sources" section listing six papers for thirty claims, does not
satisfy this rule — a reader cannot tell which paper backs which sentence,
so no sentence is checkable. The link goes at the claim, inline, in the
sentence that makes it.

### What counts as a receipt

In descending order of preference:

1. **A DOI** — resolvable, permanent, and machine-verifiable by content
   negotiation against `doi.org`, which returns structured metadata for a
   DOI that exists and an error for one that does not. A DOI is the only
   citation form that can be *mechanically proven to exist* in one request.
2. **A stable repository identifier** — an arXiv id, a NASA NTRS document
   id, an OpenAlex work id, an ADS bibcode, a PDS dataset id.
3. **A pinned document revision** — for a page that changes, the citation
   names the version it was read at (a MediaWiki `oldid` permalink, a
   Wikipedia `oldid` permalink, a dated standards revision, a specific
   edition and page of a book). A link to a living page is a link to
   something that may no longer say what was claimed.
4. **A named dataset with the instrument and mission that produced it** —
   for measurements, the provenance is the instrument, not a summary of it.
5. **An explicit statement that there is no receipt** — see below.

### What does not count

- A bare URL to a news article, press release or blog reporting on a study,
  when the study itself is citable. Cite the study; the report may be cited
  *additionally* if what is being claimed is that the report exists.
- A textbook or encyclopedia for a specific quantitative result. They are
  fine for definitions and settled pedagogy, and they are the right source
  for the ladder's lower rungs; they are not the source for a number that
  came from a particular measurement.
- A model's own confidence. "It is well known that…" is not a receipt.
- A link to another page of this implant, *as the sole grounding of a
  factual claim*. Internal links carry the ladder and the argument; the
  chain has to terminate in an external source somewhere. A page whose only
  outbound links are internal has moved the problem, not solved it.

## Uncited statements, when they are allowed

They are allowed, and they are marked. Three kinds:

- **A derivation** — a result computed from cited inputs by stated
  mathematics. It cites the inputs and the formula, and says it is derived.
  Where a tool did the arithmetic, it names the tool, so the number can be
  recomputed rather than trusted.
- **An assumption** — a premise adopted to make an estimate possible. It
  says *in words* that it is an assumption, and says whose. The contract's
  grounding rule accepts "this is an assumption" as valid grounding
  precisely so that assumptions are declared rather than disguised.
- **A judgement** — this implant's own assessment, which is what the
  feasibility reviews consist of. It is labelled as this implant's judgement,
  and it shows its reasoning from cited premises so a reader can disagree
  with the step rather than the conclusion.

What is never allowed is the fourth kind: a confident sentence that is none
of the above and has no source. That is the failure mode this whole implant
exists to prevent.

## Verification is mechanical, not aspirational

A citation nobody ever checks decays into decoration. So citations in this
implant are stored in a machine-readable record alongside the prose, and
they are re-verified: a DOI that stops resolving, a URL that rots, a
document revision that moved — these are findable by a script, and a broken
receipt is a defect in the page that carries it.

The contract already enforces that links *inside* the bundle land
(`links_resolve` in `henxels.yaml`). External receipts need the same
treatment, which is why they live in a citation register rather than only in
prose.

## Why the strictest possible reading

Because the alternative degrades silently. An implant with 95 % of its
claims sourced is not 95 % as good as one with 100 %: a reader who finds one
unsourced confident sentence must now treat *every* sentence as possibly
unsourced, and the receipts stop being load-bearing. Traceability is a
property of the whole corpus or it is not a property at all.

This is also why the rule survives [audience = public](written-to-be-public.md):
a receipt that only resolves for us is not a receipt.
