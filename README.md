# brain-implant-apologetics

A **brainpick brain implant**: a knowledge repository written to be read by AI
agents, not just by people. The articles here are plain markdown in a git
repository — you can read them with any text editor — but they are also a
compiled knowledge graph with semantic search, typed memory, dependency-linked
skills, and grounding links on every claim. An agent with brainpick attached
navigates this the way a person navigates a wiki they already know by heart:
overview first, then search, then read, then follow the links out.

**Scope: apologetics.** Articles about subjects that help Christians defend
their faith against non-Christian views. Articles that defend one Christian
view against *other Christian views* are theology and belong to the sibling
implant, `brain-implant-theology`. The boundary is who the opponent is — see
[`_brain/conventions/apologetics-vs-theology-scope.md`](_brain/conventions/apologetics-vs-theology-scope.md).

**Neutral point of view.** Nothing here asserts that a contested claim is
true. It asserts that somebody *said* something — and that is what gets
proven, with a citation. Whether what they said is true is left to the
reader.

---

## Using this with an agent

### If brainpick is already installed

```bash
git clone <this-repo> && cd brain-implant-apologetics
brainpick compile --root .          # --root is where brainpick.toml lives
brainpick overview --root .         # start here
```

Then `brainpick search`, `brainpick read`, `brainpick neighbors`. To wire it
into an agent harness as an MCP server:

```bash
brainpick register "$PWD/_brain"    # register once, then harnesses see it
brainpick integrate                 # writes harness config (Claude Code, opencode, …)
```

Or serve the web UI, which renders the graph and per-article history:

```bash
brainpick serve --root . --open
```

### If brainpick is not installed

brainpick is a Python CLI published on PyPI. Any of these work; `uv` is the
lightest because it needs no virtualenv of your own:

```bash
uv tool install brainpick           # recommended
# or:
pipx install brainpick
# or:
pip install --user brainpick
```

If the `brainpick` command is not found afterwards, it is almost certainly in
`~/.local/bin` — add that to your `PATH`.

You can also run it without installing anything:

```bash
uvx brainpick overview --root .
```

Source, issues and full documentation: <https://github.com/benquemax/brainpick>

### Minimum version

**brainpick >= 0.7.0 is required.** Check with `brainpick --version`.

This is not arbitrary. This brain uses **brain format 3**, introduced in
0.7.0, which made `type: convention` a memory type the engine actually
recognises — compiled into `conventions.json`, listed first in the overview
and in the generated `AGENTS.md` report. On an older brainpick the conventions
in this repository are not *broken*, they are **invisible**: the engine will
not surface them, so an agent reads the articles without ever seeing the rules
that govern how they are written and what they may claim. That is the failure
mode worth avoiding, and it is silent.

For context on the versions below the floor: federation and implants
(`brainpick register`, one cortex plus implants) arrived in 0.5.0, and
`--root` pointing at a repo root above the bundle arrived in 0.4.5. Neither is
sufficient on its own — 0.7.0 is the floor for this repository.

**Install the `[vectors]` extra**, not plain `brainpick`. Without it the
vector tier is silently off and search degrades to keyword only — no warning
at install time, just worse results:

```bash
uv tool install "brainpick[vectors]"
```

**Use 0.8.1 or later if you will run `brainpick serve`.** Earlier versions
applied `[bundle] root` twice and served a path that does not exist, so the
web UI showed a single generated index and nothing else. 0.7.0 remains the
floor for reading this brain; 0.8.1 is the floor for serving it.

The latest release is otherwise recommended but not required.

---

## How this repository is organised

`_brain/` is the bundle. Its folders are memory types, one job each:

| Folder | Holds |
| --- | --- |
| `knowledge/` | Evergreen concepts — the articles |
| `skills/` | Procedures an agent follows, with the tools they drive |
| `conventions/` | Standing rules: scope, neutrality, citation, publication |
| `journals/` | What happened, one file per day |
| `vision/` | Where this implant is going, as a book |
| `plans/` | Decided work |
| `todo/` | The live work queue |
| `raw/` | Undistilled source material, excluded from search results |

Read `conventions/` first — a rule constrains what every other read is for —
then `skills/`, then `knowledge/`. Grep `raw/` only to ground a claim or to
distil it into an article.

`raw/apowiki-export/` holds the original ApoWiki wikitext exactly as it was
published, unconverted. It is source material and evidence, not output:
brainpick excludes it from search results so it never drowns the distilled
articles, and every claim distilled from it links back to the revision it came
from.

## Contract

This repository is governed by a [henxels](https://pypi.org/project/henxels/)
contract — machine-checked rules in `henxels.yaml`, digested for agents into
`AGENTS.md`. It runs on commit. Install it before contributing:

```bash
uv tool install henxels && henxels init
henxels check --all
```

## Provenance and licensing

Articles are imported from [ApoWiki](https://apowiki.fi), which has been
running since 2007. The import is a **faithful history transcription**: every
ApoWiki revision becomes a git commit authored by the real contributor on the
real date, citing the MediaWiki revision id. The edit history of each article
is therefore browsable with ordinary git tooling and in the brainpick web UI,
and the GFDL's authorship-attribution requirement is satisfied by
construction rather than by a blanket credits page.

Revisions authored by bare IP addresses are pseudonymised to
`ApoWiki-anonymous`; an IP is personal data under GDPR and this repository is
public. A machine-checked rule blocks any bare IP from entering the committed
history.

Content is **GFDL-1.3-or-later**; tooling and conventions authored here are
**MIT**. See [`LICENSE`](LICENSE).
