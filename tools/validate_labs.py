#!/usr/bin/env python3
"""Run every runnable SPL block in labs/ against the live Splunk container.

A lab search that returns nothing looks exactly like a lab search that works,
right up until a student runs it in front of you. This runs them.

    python3 tools/validate_labs.py
    python3 tools/validate_labs.py --lab lab04 --window -7d

What it deliberately does NOT flag:

* Blocks that begin with a pipe, unless the pipe is followed by a generating
  command. `| rest`, `| dbinspect`, `| tstats`, `| union` and friends are
  complete searches; `| stats count by user` is a fragment quoted to show one
  step and cannot run on its own.
* Blocks with no `index=`. Those are config snippets - macro definitions,
  regexes, eval expressions, props - not searches.
* Blocks containing a backtick macro or a `$token$`. They depend on objects
  the student creates during the lab, so a zero result here means nothing.
Each search runs over the time range the lab tells the student to use, not
over one wide window. A search can pass at "-40d" and still return nothing at
"Last 24 hours", and the student only ever sees the latter.

* Searches the lab states are wrong on purpose. Mark those in the markdown by
  putting them in a table rather than a fenced block, as Lab 1 Task 2 does.
* Searches that depend on a knowledge object the lab itself has the student
  create - an alias, a tag, a calculated field, a field extraction. Those are
  empty until the student does the work, which is the point. They are listed
  in DEFERRED below, each with the lab step that creates what it needs.

Exit code is 1 if anything returned zero rows, so it can gate a commit.
"""

import argparse
import glob
import os
import re
import subprocess
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FENCE = re.compile(r"```\n(.*?)```", re.S)

# Commands that generate their own results, so a block starting with one is a
# complete search rather than a mid-pipeline fragment.
# "over **Last 24 hours**" and friends, as the labs phrase them. The window
# nearest above a code block is the one that applies to it.
WINDOW = re.compile(
    r"\b(?:over\s+(?:the\s+)?)?\*\*Last\s+(\d+)\s+"
    r"(minutes?|hours?|days?)\*\*", re.I)
UNIT = {"minute": "m", "hour": "h", "day": "d"}


def window_for(text, upto, default):
    """The last time range declared before this point in the lab."""
    hits = list(WINDOW.finditer(text, 0, upto))
    if not hits:
        return default, False
    n, unit = hits[-1].groups()
    return f"-{n}{UNIT[unit.rstrip('s').lower()]}", True


GENERATING = re.compile(
    r"\|\s*(?:rest|dbinspect|datamodel|tstats|union|metadata|inputlookup|"
    r"makeresults|eventcount|savedsearch|history|typeahead|from)\b")

# Searches that are correctly empty: either until a student completes the lab,
# or permanently because the lab is teaching why they fail. Keyed by lab
# filename stem; the value is a marker identifying the block and the reason.
DEFERRED = {
    "lab02": [("productid=HV-TN-101",
               "intentionally empty - Task 1 contrasts productId against "
               "productid to show field names are case sensitive")],
    "lab08": [("top limit=10 port by src",
               "src and port are extracted in Task 1"),
              ("stats count by role, action",
               "role and action are extracted in Task 3")],
    "lab09": [("index=network user=*",
               "deliberately empty - step 3 asks the student to confirm the "
               "problem the aliases then solve"),
              ("sc_megabytes",
               "calculated field created in Task 2"),
              ("http_method",
               "aliases created in the supplemental task")],
    "lab10": [("tag=privileged",
               "tag created in Task 1")],
    "lab14": [("| fields clientip] | stats count",
               "deliberately unbounded - Task 4 shows it hitting the "
               "10,000-row subsearch ceiling")],
}


def deferred_reason(lab, spl):
    for marker, reason in DEFERRED.get(lab[:5], []):
        if marker in spl:
            return reason
    return None


def search(spl, container, auth, window, app):
    cmd = ["docker", "exec", "-u", "splunk", container,
           "/opt/splunk/bin/splunk", "search", spl,
           "-app", app, "-auth", auth, "-preview", "false",
           "-earliest_time", window, "-latest_time", "now",
           "-maxout", "5"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    err = "\n".join(l for l in p.stderr.splitlines()
                    if l.strip() and "Server Certificate" not in l)
    rows = [l for l in p.stdout.splitlines()
            if l.strip() and "Server Certificate" not in l
            and not set(l.strip()) <= set("- ")]
    return len(rows), err


def split_searches(block):
    """A fenced block may hold several complete searches, one per line.

    Lab 1 shows three one-line variants together to contrast them. Joining
    them into a single search produces nonsense that reports as empty.
    """
    raw = [l for l in block.splitlines()
           if l.strip() and not l.strip().startswith("#")]
    if not raw:
        return []
    # Fenced blocks inside a numbered list carry the list's indent on every
    # line, so test continuation against the block's own left margin rather
    # than against column zero.
    lines = [textwrap.dedent("\n".join(raw))][0].splitlines()
    starts = [l for l in lines if l.startswith("index=")]
    if len(starts) > 1 and len(starts) == len(lines):
        return lines
    return ["\n".join(lines)]


def runnable(body):
    """Is this a complete search we can execute as-is?"""
    if not body.strip():
        return None, "empty"
    lead = body.lstrip()
    if lead.startswith("|") and not GENERATING.match(lead):
        return None, "fragment"
    if "index=" not in body and not GENERATING.match(body.lstrip()):
        return None, "not a search"
    if "`" in body:
        return None, "needs a macro"
    if re.search(r"\$\w+\$", body):
        return None, "needs a token"
    return " ".join(body.split()), None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--container", default=os.environ.get("CONTAINER", "splunk"))
    ap.add_argument("--auth", default=os.environ.get("AUTH", "admin:password"))
    ap.add_argument("--app", default=os.environ.get("APP", "splunk_intadv"),
                    help="Splunk app context; the course config lives in an "
                         "app, so searching from 'search' misses its lookups")
    ap.add_argument("--window", default="-40d",
                    help="fallback earliest_time for blocks where the lab "
                         "states no time range (default -40d)")
    ap.add_argument("--lab", help="only labs whose filename contains this")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(ROOT, "labs", "*.md")))
    if args.lab:
        files = [f for f in files if args.lab in os.path.basename(f)]
    if not files:
        print("no lab files matched", file=sys.stderr)
        return 2

    empty, ran, skipped, errors = [], 0, 0, []
    for path in files:
        name = os.path.basename(path)
        text = open(path, encoding="utf-8").read()
        blocks = FENCE.findall(text)
        print(f"\n{name}  ({len(blocks)} blocks)")
        units = []
        for i, b in enumerate(blocks, 1):
            at = text.index("```\n" + b)
            for u in split_searches(b):
                units.append((i, u, at))
        for i, unit, at in units:
            spl, why = runnable(unit)
            if spl is None:
                skipped += 1
                continue
            reason = deferred_reason(name, spl)
            win, declared = window_for(text, at, args.window)
            rows, err = search(spl, args.container, args.auth, win, args.app)
            ran += 1
            head = spl[:52] + ("..." if len(spl) > 52 else "")
            tag = win if declared else f"{win} (no window stated)"
            if err and reason:
                skipped += 1
                ran -= 1
                print(f"  {i:>2}. defer  {head}\n          ({reason})")
            elif err:
                errors.append((name, i, head, err.splitlines()[0][:90]))
                print(f"  {i:>2}. ERROR  {head}")
            elif rows <= 1:
                if reason:
                    skipped += 1
                    ran -= 1
                    print(f"  {i:>2}. defer  {head}\n          ({reason})")
                else:
                    empty.append((name, i, f"[{win}] {head}"))
                    print(f"  {i:>2}. EMPTY  {tag:<7} {head}")
            else:
                print(f"  {i:>2}. ok     {tag:<7} {head}")

    print(f"\n{'='*70}")
    print(f"ran {ran}, skipped {skipped} (fragments, config, deferred), "
          f"{len(empty)} empty, {len(errors)} errored")
    for name, i, head in empty:
        print(f"  EMPTY  {name} block {i}: {head}")
    for name, i, head, err in errors:
        print(f"  ERROR  {name} block {i}: {head}\n         {err}")
    return 1 if (empty or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
