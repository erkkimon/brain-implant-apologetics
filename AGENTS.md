<!-- henxels:begin -->

## The contract (henxels)

_Auto-generated from `henxels.yaml` by `henxels sync`. Do not edit by hand._

Each bullet is a **henxel** (a rule). To disobey one, change `henxels.yaml` —
that is the only sanctioned escape. Run `henxels explain <path>` before creating
a file to see what governs that spot.

Only use `git commit --no-verify` in a genuine emergency: it bypasses the hooks that run this contract, the safety mechanism meant to protect the repository. Prefer `henxels bless <action>` or editing `henxels.yaml` — both keep the deviation visible.

> **Git etiquette — important.** Do **not** run `git add`, `git commit`, or `git push` yourself in this repo. When your work is ready, stop and ask the user to review the diff and stage it. Staging on the user's behalf is a mistake here, even if the change looks correct.
>
> _OpenCode agents:_ run `henxels integrate opencode` once to make this **enforced** (it hard-blocks `git add`/`git commit`), not just advisory.

### Rules

- Docs are kebab-case markdown (in ./docs)
- One implant, one bundle root — and it is compiled fresh before every commit (in .)
  ↳ Agents navigate the COMPILED implant (brainpick's index, link graph, vectors), not the raw files. Stale artifacts lie to agents, so the freshness gate runs before every commit. Serve it with `brainpick init`.
- Folders are memory types — knowledge, skills, journals, vision, plans, conventions — one job each; todo/ is the work queue, raw/ is source material (in ./_implant)
  ↳ knowledge/ is semantic memory (evergreen concepts), skills/ procedural (distilled, actionable procedures), journals/ episodic (one file per day, rolled into archive/YYYY/MM/), vision/ direction (a book), plans/ decided work, conventions/ decided rules and principles for HOW things get done (standing policy — naming, process, contracts — not a specific task like plans/, not a step-by-step procedure like skills/). todo/ is not a memory type: it is the implant's own work queue — open.md the live checklist, archive/YYYY-MM-DD.md what was closed that day — kept in the implant so it is searchable and counted. raw/ is not one either: undistilled source material (transcripts, exports, clippings) that knowledge grounds on — governed for order, exempt from OKF, and excluded from brainpick's results. Nothing is replicated across layers. A memory type that does not fit is a `type` value or a sub-folder, never a new sibling. Read conventions/ first — a rule constrains what any other read is for — then skills/, the most distilled, tested and pure layer, then knowledge/, then journals/; grep raw/ only to ground or to distil. Data flow architecture: https://github.com/benquemax/brainpick/blob/main/docs/data-flow-architecture.md
- Implant material is markdown plus small data and scripts; scratch is _temp/ (in ./_implant/*)
  ↳ Catalogues and tooling may live in the implant, but only these types count as implant material. brainpick indexes the markdown; the rest is allowed but invisible to the graph. Anything temporary goes to _temp/; raw/ has its own, wider list below.
- raw/ is orderly source material — kebab-case, indexed, greppable — never a dump (in ./_implant/raw/*)
  ↳ Raw data is undistilled but valuable: it is what knowledge grounds on and what future distillation reads. It needs no frontmatter and no links, but it is kept clean: kebab-case names that say what a file is, listed in raw/index.md, and pruned when it has been distilled or proved worthless. brainpick excludes raw/ from search results (see brainpick.toml) so it never drowns the distilled layers; grep it.
- ApoWiki-exported source files carry the GFDL notice (in ./_implant/raw/apowiki-export/*)
  ↳ ApoWiki content is GFDL-1.3-or-later. The license requires preserving authorship and license notices. Every file in raw/apowiki-export/ must carry the GFDL notice so the import is license-compliant — the faithful-history transcription preserves contributor attribution in git, and this notice preserves the license declaration in the source.
- Every concept doc is kebab-case markdown with OKF frontmatter (type is the one MUST) (in ./_implant/*)
  ↳ type, title and description keep a page findable and compilable; a description containing `: ` must be quoted. Follows the Open Knowledge Format: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Freshness is explicit — timestamp is a real ISO 8601 datetime bumped whenever a doc changes (in ./_implant/*)
- Every claim is grounded — knowledge, skills, plans and conventions link to where they came from (in ./_implant/knowledge/*, ./_implant/skills/*, ./_implant/plans/*, ./_implant/conventions/*)
  ↳ Wikipedia-style, inline, a plain link at the claim: a journal entry (a decision this implant made), an external page, another brain or implant (brain://slug-id/path), or say in words that it is an assumption. A page with no outbound links is ungrounded and fails, not warns. Journals are the primary sources and are exempt. https://github.com/benquemax/brainpick/blob/main/docs/grounding.md
- Skills are type: skill and form a dependency tree — declare depends_on, list tools that exist, never edit skilltree.md (in ./_implant/skills/*)
  ↳ A skill is a procedure an AGENT follows: `type: skill`, the one value brainpick recognises, lists first and boosts in search (a `playbook` is a how-to for humans and is not a skill). It lists the skills it assumes in `depends_on` frontmatter (bundle-relative .md paths; omit it or use `[]` when it assumes nothing) and the deterministic scripts it drives in `tools` (bundle-relative paths that must exist — brainpick indexes and points at them, never runs them). skilltree.md is generated from those edges by brainpick — edit the skills, never the tree. A skill with `export: agent-skill` is also written out as a harness-loaded SKILL.md pointer by `brainpick integrate`, so the implant's procedures reach the agent before it decides anything. Start one with `brainpick skill new <name>`.
- One journal file per day — journals/YYYY-MM-DD.md — entries newest first under any heading (in ./_implant/journals)
  ↳ Journals are episodic memory: what happened, when. A day per file caps the length forever and gives brainpick's half-life a file-level unit; the date is the file name, so headings inside are free (`## HH:MM` or a title). An entry links forward to the knowledge or skill it changed instead of restating it (DRY by pointer, in the direction of distillation); when you distil an entry, add the pointer to it. Journals are logs, not concept docs: no frontmatter.
- Only today stays in journals/ — every earlier day moves to journals/archive/YYYY/MM/ (in ./_implant/journals)
  ↳ History without the bulk: before the first entry of a new day, move yesterday's file to journals/archive/YYYY/MM/ (same name; mkdir -p it the first time). Two unarchived days block the commit, so the roll cannot be forgotten. Archived days are read-only history; brainpick indexes both, and a grounding link to a day is a link to its file, no anchor: ../journals/archive/2026/09/2026-09-07.md.
- Archived journals sit under archive/YYYY/MM/, one day per file, untouched otherwise (in ./_implant/journals/archive/*)
- Every link lands — bundle-absolute (/a/b.md) and relative alike (in ./_implant/*)
- OKF reserved files stay frontmatter-free; the root index is compile-managed (in ./_implant/**/index.md, ./_implant/**/log.md)
  ↳ _implant/index.md is regenerated by `brainpick compile` ([index] mode = "section") — edit the docs' descriptions, never the generated block.
- Update logs are date-sectioned, newest first (in ./_implant/**/log.md)
- vision/ is a book — index.md is the table of contents; an unlinked chapter is invisible (in ./_implant/vision)
- plans/ holds DECIDED work only, every plan listed in its index (in ./_implant/plans)
  ↳ Undecided ideas belong in todo/open.md (a task) or journals/ (an insight), not here.
- conventions/ holds decided rules and principles, one per page, every one listed in its index (in ./_implant/conventions)
  ↳ A convention is a standing answer to "how do we do this" — naming, process, a contract a team holds itself to — decided once and applied broadly, unlike plans/ (one specific piece of work) or skills/ (a procedure to execute). type: convention (brainpick brain format 3) is the standing RESULT of a decision, edited as practice evolves — not the decision record itself — and it is what brainpick lists first in brain_overview and the AGENTS.md report; ground each one the same way any other claim is grounded (the decision episode, an external source, or a stated assumption).
- todo/ is the implant's work queue — open.md the live type: todo checklist, done items archived by day (in ./_implant/todo/*)
  ↳ Open work is part of the implant, so it is searchable and counted: brainpick compiles every `- [ ]` / `- [x]` line of a `type: todo` doc into todos.json, the overview says how many are open, and a search hit on a list carries its counts. Tasks that surface mid-work go to todo/open.md instead of derailing the task at hand; check it before planning any new work — it may already flag a known imperfection or something overlapping the task. A ticked item ends in `(done: YYYY-MM-DD)` and moves to todo/archive/YYYY-MM-DD.md — the day it was closed — the next day at the latest, so open.md stays small and "done" is an episode with a date. The archive holds only done items.
- _temp stays gitignored (in .)
  ↳ _temp/ is free scratch space; nothing in it is ever committed, and brainpick always excludes it from the implant.
- Shared policy committed, machine-local config never — and no credentials anywhere
  ↳ brainpick.toml (index mode, [brain] audience, the bundle id) is shared and versioned. brainpick.local.toml (model endpoints, tokens) is gitignored. No secret ever enters the repo.
- brainpick.local.toml is never committed (in .)
- No bare IP addresses appear as git authors in committed history (in .)
  ↳ ApoWiki revisions authored by bare IP addresses are personal data under GDPR. This implant is public (see conventions/written-to-be-public.md), so no IP may enter the repository — not in prose, not in frontmatter, not as a git author. The faithful-history importer pseudonymizes bare IPs to 'ApoWiki-anonymous' and stores the real IP only in a local, gitignored provenance sidecar. This henxel checks committed history so no bare IP slips through.
- The ApoWiki provenance sidecar is never committed (in .)
  ↳ The .provenance/ directory and apowiki-provenance.json hold the real IP addresses behind pseudonymized commits. They are personal data and must never enter the public repository. The .gitignore excludes them; this henxel verifies the exclusion mechanically.

### Behaviours

- **never `git add` / `git commit` / `git push` yourself** — ask the user to review and stage
- push is blocked until `henxels bless push`
- deleting files / removing many lines is blocked until `henxels bless delete`
- warns when a new file looks like a near-copy of a committed one

### Custom henxels & contributing

**Before writing a custom check, run `henxels catalogue` and use the built-in that
matches your intent — don't reinvent one.** Never name a custom check after a built-in
or a setting (e.g. `warn_about_large_files` is a setting, not a check).

Need a check that genuinely doesn't exist? `henxels create-new-statement <name>` scaffolds a local check
(auto-loaded from `henxels_checks.py`). **If your check is reusable** — useful in
other repos, not tied to this one — contribute it upstream with `henxels contribute`.
We're in the agentic era: send a ready-to-merge PR instead of opening an issue.
<!-- henxels:end -->
