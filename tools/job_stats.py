#!/usr/bin/env python3
"""Report what the Job Inspector shows for a search, from the command line.

The lab answer keys make claims about relative cost - that filtering early is
cheaper, that `stats` beats `transaction`. Wall-clock time from the CLI cannot
settle those: process startup dominates and every search looks like 2.4
seconds. This asks Splunk for the job's own numbers instead.

    python3 tools/job_stats.py 'index=web sourcetype=access_combined'
    python3 tools/job_stats.py --window -24h --compare cases.txt

`--compare` takes a file of `label<TAB>search` lines and prints them as a
table, which is how the answer keys' performance claims were checked.

SPL is passed to the container through the environment, never interpolated
into a shell command: a search is full of pipes and quotes.
"""

import argparse
import json
import os
import subprocess
import sys

REMOTE = r'''
import json, os, ssl, urllib.parse, urllib.request
spl, earliest, latest = os.environ["SPL"], os.environ["EARLIEST"], os.environ["LATEST"]
app, auth = os.environ["APP"], os.environ["AUTH"]
base = "https://localhost:8089"
ctx = ssl._create_unverified_context()
user, pwd = auth.split(":", 1)
mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
mgr.add_password(None, base, user, pwd)
op = urllib.request.build_opener(
    urllib.request.HTTPBasicAuthHandler(mgr),
    urllib.request.HTTPSHandler(context=ctx))

def call(path, data=None):
    url = f"{base}{path}"
    body = urllib.parse.urlencode(data).encode() if data else None
    with op.open(urllib.request.Request(url, data=body)) as r:
        return json.loads(r.read().decode())

job = call(f"/servicesNS/nobody/{app}/search/jobs", {
    "search": spl if spl.lstrip().startswith("|") else "search " + spl,
    "earliest_time": earliest, "latest_time": latest,
    "exec_mode": "blocking", "output_mode": "json"})
c = call(f"/servicesNS/nobody/{app}/search/jobs/{job['sid']}?output_mode=json")
c = c["entry"][0]["content"]
print(json.dumps({k: c.get(k) for k in
     ("runDuration", "scanCount", "eventCount", "resultCount")}))
'''


def stats(spl, container, app, auth, window, latest="now"):
    p = subprocess.run(
        ["docker", "exec",
         "-e", f"SPL={spl}", "-e", f"EARLIEST={window}", "-e", f"LATEST={latest}",
         "-e", f"APP={app}", "-e", f"AUTH={auth}",
         "-u", "splunk", container, "python3", "-c", REMOTE],
        capture_output=True, text=True, timeout=900)
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError((p.stderr or p.stdout).strip().splitlines()[-1][:200])
    return json.loads(p.stdout)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spl", nargs="?")
    ap.add_argument("--compare", help="file of label<TAB>search lines")
    ap.add_argument("--container", default=os.environ.get("CONTAINER", "splunk"))
    ap.add_argument("--app", default=os.environ.get("APP", "splunk_intadv"))
    ap.add_argument("--auth", default=os.environ.get("AUTH", "admin:password"))
    ap.add_argument("--window", default="-7d")
    args = ap.parse_args()

    cases = []
    if args.compare:
        for line in open(args.compare, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.strip() and not line.startswith("#"):
                label, _, spl = line.partition("\t")
                cases.append((label, spl))
    elif args.spl:
        cases = [("", args.spl)]
    else:
        ap.error("give a search or --compare")

    width = max((len(l) for l, _ in cases), default=0) or 1
    print(f"  {'search'.ljust(width)} {'seconds':>9} {'scanCount':>10} {'results':>9}")
    for label, spl in cases:
        try:
            s = stats(spl, args.container, args.app, args.auth, args.window)
        except Exception as exc:                     # noqa: BLE001
            print(f"  {label.ljust(width)}  ERROR {exc}")
            continue
        print(f"  {label.ljust(width)} {s['runDuration']:>9.3f} "
              f"{s['scanCount']:>10} {s['resultCount']:>9}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
