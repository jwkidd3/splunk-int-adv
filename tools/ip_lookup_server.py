#!/usr/bin/env python3
"""Offline stand-in for the external whois service used by Lab 11.

Lab 11 builds workflow actions that hand a src_ip to an outside web service.
That needs the internet, so in an air-gapped classroom the lab cannot be
completed as written. This serves the same shapes locally:

    GET  /whois?ip=10.0.0.1    an HTML "whois" page for that address
    POST /report               accepts a form post and echoes what it received
    GET  /                     usage

Python 3.8+, standard library only. Nothing is fetched and nothing is written
to disk; responses are derived from the address itself so they stay stable
across restarts and across students' machines.

    python3 tools/ip_lookup_server.py          # serves on 127.0.0.1:8888
    python3 tools/ip_lookup_server.py --port 9000 --host 0.0.0.0

Workflow actions open in the student's own browser, so 127.0.0.1 is correct
even when Splunk itself runs in Docker.
"""

import argparse
import hashlib
import html
import ipaddress
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ORGS = [
    ("Meridian Broadband", "US", "Ashburn, Virginia"),
    ("Kestrel Networks", "US", "San Jose, California"),
    ("Northwind Telecom", "GB", "Manchester, England"),
    ("Aurora Datacentre", "DE", "Frankfurt, Hesse"),
    ("Pacific Rim Hosting", "SG", "Singapore"),
    ("Cedar Point Communications", "CA", "Toronto, Ontario"),
    ("Sawgrass Cloud Services", "US", "Miami, Florida"),
    ("Blue Ridge Internet", "US", "Charlotte, North Carolina"),
]

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 15px/1.6 ui-sans-serif, system-ui, -apple-system, sans-serif;
         margin: 0; padding: 2.5rem 1rem; background: #f6f7f9; color: #1b1f24; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #14171a; color: #e6e8eb; }}
    .card {{ background: #1e2227 !important; border-color: #2d333b !important; }}
    th {{ color: #9aa4b2 !important; }}
    code {{ background: #2d333b !important; }}
  }}
  .card {{ max-width: 46rem; margin: 0 auto; background: #fff; border: 1px solid #dfe3e8;
          border-radius: 10px; padding: 1.75rem 2rem; }}
  h1 {{ font-size: 1.25rem; margin: 0 0 .25rem; }}
  .sub {{ color: #6b7684; font-size: .875rem; margin: 0 0 1.5rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #e9edf1; vertical-align: top; }}
  th {{ width: 12rem; font-weight: 600; color: #52606d; }}
  tr:last-child th, tr:last-child td {{ border-bottom: 0; }}
  code {{ background: #eef1f4; padding: .1rem .35rem; border-radius: 4px; font-size: .9em; }}
  .note {{ margin-top: 1.5rem; font-size: .8125rem; color: #6b7684; }}
</style></head>
<body><div class="card"><h1>{title}</h1><p class="sub">{sub}</p>{body}
<p class="note">Served locally by <code>tools/ip_lookup_server.py</code>. This is
classroom data, not a real registry lookup.</p></div></body></html>"""


def profile(addr):
    """Derive a stable fake registration record from the address itself."""
    digest = hashlib.sha256(addr.encode()).digest()
    org, country, city = ORGS[digest[0] % len(ORGS)]
    try:
        net = ipaddress.ip_network(f"{addr}/24", strict=False)
        netblock = str(net)
    except ValueError:
        netblock = "unknown"
    return {
        "Network": netblock,
        "Organization": org,
        "Country": country,
        "Location": city,
        "AS number": f"AS{10000 + int.from_bytes(digest[1:3], 'big') % 55000}",
        "Abuse contact": f"abuse@{org.split()[0].lower()}.example",
        "Registry": "CLASSROOM-RIR",
    }


def rows(pairs):
    return "<table>" + "".join(
        f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>"
        for k, v in pairs
    ) + "</table>"


class Handler(BaseHTTPRequestHandler):
    server_version = "SplunkClassIPLookup/1.0"

    def _send(self, status, title, sub, body):
        page = PAGE.format(title=html.escape(title), sub=html.escape(sub), body=body)
        raw = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path.rstrip("/") in ("", "/whois") and not query:
            self._send(200, "Classroom IP lookup", "Offline stand-in for Lab 11.", rows([
                ("Whois (GET)", "/whois?ip=ADDRESS"),
                ("Report (POST)", "/report  — any form fields"),
            ]))
            return

        if parsed.path.rstrip("/") == "/whois":
            addr = (query.get("ip") or query.get("src_ip") or [""])[0].strip()
            if not addr:
                self._send(400, "Missing address",
                           "Call this as /whois?ip=ADDRESS.", "")
                return
            try:
                ipaddress.ip_address(addr)
            except ValueError:
                self._send(404, f"No record for {addr}",
                           "That is not a valid IP address.", "")
                return
            self._send(200, f"Whois: {addr}", "Registration record.",
                       rows(profile(addr).items()))
            return

        self._send(404, "Not found", f"No handler for {parsed.path}.", "")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        fields = parse_qs(raw, keep_blank_values=True)
        flat = [(k, ", ".join(v)) for k, v in sorted(fields.items())]
        self._send(200, "Report received",
                   f"{len(flat)} field(s) posted to {urlparse(self.path).path}.",
                   rows(flat) if flat else "<p>No form fields were posted.</p>")

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()}  {fmt % args}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8888)
    args = ap.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Classroom IP lookup on http://{args.host}:{args.port}")
    print(f"  whois   http://{args.host}:{args.port}/whois?ip=198.51.100.7")
    print(f"  report  POST to http://{args.host}:{args.port}/report")
    print("Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()


if __name__ == "__main__":
    main()
