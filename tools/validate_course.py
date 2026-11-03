#!/usr/bin/env python3
"""Structural checks on the course: shape, coverage and house style.

Complements validate_labs.py, which runs the searches. This one never talks to
Splunk; it checks that the material hangs together.

    python3 tools/validate_course.py

Checks:
  1. Every module that should have a lab has one, and every lab maps to a
     module. Taken from the deck content, not from a hardcoded list, so the
     two cannot drift apart.
  2. Each lab has the house-style shape: an em-dash title, numbered Task
     headings, and an Answers section.
  3. Lab step numbering is contiguous and starts at 1.
  4. The commands a lab exercises are actually taught in its module's deck.
  5. House style: no timing promises, and "introductory" rather than
     "beginner".
  6. README links to every lab, and every lab is linked from the README.

Exit code is 1 if anything fails.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from course_content import MODULES  # noqa: E402

LABS = os.path.join(ROOT, "labs")
PRES = os.path.join(ROOT, "presentations")

# Phrases that promise a duration. A course runs at the pace of the room, and
# a printed "20 minutes" is a promise the instructor did not make.
#
# "Last 24 hours" and "Previous week" are Splunk time-range presets and appear
# constantly; so does "maxspan=30m". Those are the subject matter, not a
# schedule, so the qualifier is checked on both sides of the match.
TIMING = re.compile(
    r"\b\d+\s*(?:-\s*\d+\s*)?(?:minute|minutes|min|mins|hour|hours|hr|hrs)\b",
    re.I)
NOT_A_PROMISE = re.compile(
    r"(?:last|previous|past|over(?:\s+the)?|within|every|span=|maxspan=|maxpause=|"
    r"earliest|latest|range\s+to)\s*$", re.I)

# The commands each lab is really about, checked against its module's deck.
CONCEPTS = {
    "lab02": ["Job Inspector", "scanCount", "search mode"],
    "lab03": ["chart", "timechart", "top", "useother"],
    "lab04": ["trendline", "iplocation", "geostats", "geom", "addtotals"],
    "lab05": ["eval", "case", "where", "fields", "like"],
    "lab06": ["transaction", "startswith", "endswith", "duration"],
    "lab07": ["knowledge object", "naming", "permission"],
    "lab08": ["Field Extractor", "Regular Expression", "Delimiter"],
    "lab09": ["alias", "calculated field"],
    "lab10": ["tag", "event type"],
    "lab11": ["macro", "backtick", "argument", "Validation"],
    "lab12": ["workflow action", "GET", "POST", "search"],
    "lab13": ["data model", "root event", "child", "Pivot", "lookup"],
    "lab14": ["subsearch", "dedup", "NOT", "10,000"],
    "lab15": ["join", "append", "union", "stats"],
    "lab16": ["role", "capabilit", "user"],
    "lab17": ["Monitoring Console", "_internal", "_audit", "retention"],
}

fails, warns = [], []


def fail(what, detail):
    fails.append(f"{what}: {detail}")


def warn(what, detail):
    warns.append(f"{what}: {detail}")


def deck_text(num):
    for name in os.listdir(PRES):
        if name.startswith(f"module{num:02d}_"):
            return open(os.path.join(PRES, name), encoding="utf-8").read()
    return ""


def main():
    lab_files = sorted(f for f in os.listdir(LABS) if f.endswith(".md"))
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()

    # 1. module <-> lab mapping, derived from the decks
    deck_labs = {}
    for mod in MODULES:
        for slide in mod["slides"]:
            if slide.get("type") == "lab":
                n = int(re.search(r"\d+", slide["lab"]).group())
                deck_labs[n] = mod["num"]
    for n, modnum in sorted(deck_labs.items()):
        if not any(f.startswith(f"lab{n:02d}") for f in lab_files):
            fail("coverage", f"Module {modnum} calls out Lab {n}, no such file")
    for f in lab_files:
        n = int(re.match(r"lab(\d+)", f).group(1))
        if n not in deck_labs:
            fail("coverage", f"{f} exists but no deck calls out Lab {n}")

    # 2-5. per-lab checks
    for f in lab_files:
        path = os.path.join(LABS, f)
        text = open(path, encoding="utf-8").read()
        stem = f[:5]

        if not re.match(r"^# Lab \d+ — ", text):
            fail(f, "title is not '# Lab N — Title' with an em-dash")
        if not re.search(r"^## Task \d+ — ", text, re.M):
            fail(f, "no '## Task N — ...' headings")
        if "## Answers" not in text:
            fail(f, "no '## Answers' section")

        steps = [int(m.group(1)) for m in
                 re.finditer(r"^\s{0,3}(\d+)\. ", text, re.M)]
        if steps:
            if steps[0] != 1:
                fail(f, f"step numbering starts at {steps[0]}, not 1")
            gaps = [(a, b) for a, b in zip(steps, steps[1:]) if b not in (a, a + 1)]
            if gaps:
                fail(f, f"step numbering jumps: {gaps[:3]}")

        for m in TIMING.finditer(text):
            lead = text[max(0, m.start() - 24):m.start()]
            if NOT_A_PROMISE.search(lead):
                continue
            line = text[:m.start()].count("\n") + 1
            warn(f, f"timing promise '{m.group(0)}' at line {line}")
        if re.search(r"\bbeginner", text, re.I):
            fail(f, "uses 'beginner'; house style is 'introductory'")

        n = int(re.match(r"lab(\d+)", f).group(1))
        deck = deck_text(deck_labs.get(n, 0))
        for concept in CONCEPTS.get(stem, []):
            if concept.lower() not in deck.lower():
                warn(f, f"exercises '{concept}' but module "
                        f"{deck_labs.get(n)} deck never mentions it")

        if f not in readme:
            fail("README", f"does not link {f}")

    # 5b. house style across the decks too
    for name in sorted(os.listdir(PRES)):
        deck = open(os.path.join(PRES, name), encoding="utf-8").read()
        if re.search(r"\bbeginner", deck, re.I):
            fail(name, "uses 'beginner'; house style is 'introductory'")

    print(f"{len(lab_files)} labs, {len(MODULES)} modules, "
          f"{len(deck_labs)} lab callouts\n")
    for w in warns:
        print(f"  WARN  {w}")
    for x in fails:
        print(f"  FAIL  {x}")
    if not fails and not warns:
        print("  everything checks out")
    print(f"\n{len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
