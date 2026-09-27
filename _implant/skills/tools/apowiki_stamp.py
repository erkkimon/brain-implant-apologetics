#!/usr/bin/env python3
"""Give regenerated pages an honest timestamp: bumped only when they changed.

The generators (apowiki_convert.py, apowiki_topics.py, apowiki_books.py) write
a fixed placeholder timestamp, so the same input always gives the same bytes.
The contract wants `timestamp` bumped whenever a page changes, and left alone
when it did not, because brainpick's half-life reads it as "last changed". This
pass reconciles the two. For each page it compares everything except the
timestamp line with the committed version (`git show HEAD:path`):

* unchanged, so the committed timestamp is put back;
* changed or new, so it gets the current time (or `--at`).

Run it last, after every generator:

    python3 apowiki_stamp.py _implant/knowledge/articles _implant/knowledge/topics \\
        _implant/knowledge/books [--at 2026-09-27T13:00:00Z]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

TS = re.compile(r"^timestamp:.*$", re.M)


def committed(path: Path) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{path.as_posix()}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", type=Path)
    ap.add_argument("--at", default=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    args = ap.parse_args()
    kept = bumped = 0
    for d in args.dirs:
        for f in sorted(d.rglob("*.md")):
            new = f.read_text(encoding="utf-8")
            if not TS.search(new):
                continue
            old = committed(f)
            if old is not None and TS.search(old) and \
                    TS.sub("", old) == TS.sub("", new):
                stamp = TS.search(old).group(0)
                kept += 1
            else:
                stamp = f"timestamp: {args.at}"
                bumped += 1
            out = TS.sub(stamp, new, count=1)
            if out != new:
                f.write_text(out, encoding="utf-8")
    print(f"timestamps: {kept} kept, {bumped} bumped to {args.at}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
