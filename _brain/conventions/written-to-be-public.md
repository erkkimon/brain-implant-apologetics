---
type: convention
about: concept
title: Written to be public
description: This implant is written for release to the open internet — every page is addressed to a stranger with no access to the machine it was written on, so no host names, internal paths, personal details or credentials ever enter it; the repository is private only until it is published, which changes nothing about how it is written.
tags: [convention, publishing, privacy, scope]
timestamp: 2026-09-24T16:00:00Z
half_life: 0
---

# Written to be public

Decided by Tom on 2026-09-24, while founding the apologetics implant
([journal](../journals/2026-09-24.md)): *"this repository will be public […]
it's not public yet, I will publish it later, but make sure that you know it
and that you will know it also in the future."*

So it is recorded here — in the brain, where an agent reads before it writes
— rather than in a README that would announce a private repository's future
to nobody. It is also in `brainpick.toml` as `[brain] audience = "public"`,
the field brainpick reports in `brain_overview`.

## The rule

**Write every page as if a stranger is reading it today.** Not a colleague,
not a future teammate, not an agent running on our hardware: someone who
found this repository on the internet, knows nothing about how it was made,
and cannot reach anything it mentions.

That the repository is *private right now* is a fact about its git remote
and nothing else. It is not a grace period. A page written "we will clean it
up before publishing" is a page that gets published uncleaned, because the
person who knew what to clean is gone by then. There is no publication pass
in this project's plan, by design.

### Never in this repository

1. **No machine or network identity** — no internal host names, LAN
   addresses, private URLs, user accounts, or SSH remotes in any page.
   (`brainpick.toml` names the git origin because that is what the field is
   for, and it is a private address that becomes a public one on release;
   prose does not repeat it.)
2. **No filesystem paths outside the repository** — paths are
   repository-relative. A reader clones this and the paths work. `/home/…`,
   `~/Brain`, or a path on a specific machine do not appear.
3. **No personal data** — no names of people who did not choose to appear in
   a public document, no e-mail addresses, no schedules or locations. Tom is
   named as the author of decisions, which he has chosen; nobody else is
   named without the same choice.
4. **No credentials, tokens or keys** — the contract enforces this
   mechanically (`no_secrets` in `henxels.yaml`), but the rule is wider than
   what a scanner catches: not even an example key, not even a revoked one.
5. **No assumption of our fleet** — a skill says how to do the thing with
   ordinary, publicly available tools. Where a step needs a local model, an
   API token or a specific service, it says so as a *requirement the reader
   must supply*, with a documented free alternative where one exists, and
   degrades gracefully when it is absent. A tool that only runs here is a
   tool this implant does not have.
6. **No private reasoning about third parties** — assessments are about
   published claims and their evidence, never about the people who made
   them. Criticism lands on the argument, with a citation, as
   [Evidence before authority](evidence-before-authority.md) requires.
7. **No bare IP addresses** — ApoWiki revisions authored by bare IPs are
   pseudonymized to `ApoWiki-anonymous` at import; the real IP is kept only
   in a local gitignored provenance sidecar. An IP is personal data under
   GDPR, and this implant is written for public release.

### Always in this repository

- **Every external dependency is named and free to obtain**, or the page
  says plainly what it costs and what happens without it.
- **Every citation resolves for a stranger** — a public DOI, URL or
  identifier, never a file only we hold. This is the same requirement
  [Every claim carries its receipt](every-claim-carries-its-receipt.md)
  makes for a different reason; here it is also what makes the implant
  usable by someone who is not us.
- **Terms are defined before they are used**, because the reader did not sit
  in the conversation where they were coined.

## Why this is a convention and not a task

A one-time cleanup is a task; this is a property every future page must have,
including pages written by agents that never read this conversation. It is
`type: convention` with `half_life: 0` so it never fades out of
`brain_overview`, and it is the first thing
[Using the brain](../skills/using-the-brain.md) tells a writer to respect.

## When it is published

Publication itself is a small event — flipping the Gitea repository to
public, or pushing a mirror elsewhere. What makes it small is that this rule
held from the first commit. Before flipping the switch, the only checks
needed are mechanical: `henxels check --all` for the secret scan, and a grep
for host names and absolute paths. If those come back clean, the repository
was already public in everything but its permission bit.
