#!/usr/bin/env python3
"""Generate the Harborview Outfitters course dataset.

All course data is synthesised here. Nothing is downloaded and nothing is
derived from a vendor's sample data, so the output is original to this course.

Timestamps are relative to the moment you run it, which is the point: the labs
ask for "Last 24 hours" and "Last 7 days", so regenerate before class rather
than widening every time range.

The default window is 35 days against a longest lab preset of "Last 30 days".
That five-day margin is deliberate: a window equal to the preset starts
clipping its oldest events the moment the clock moves past generation time,
so a dataset built on Wednesday morning is already losing events by the
Thursday session.

    python3 tools/generate_data.py                 # writes into data/
    python3 tools/generate_data.py --days 45 --seed 7
    python3 tools/generate_data.py --out /tmp/x

Output (see README for the index/sourcetype each one loads into):

    data/access.zip                     web      access_combined
    data/secure.zip                     security linux_secure
    data/vendor_sales.log               sales    vendor_sales
    data/sales_entries.json             sales    sales_entries
    data/web_proxy.json                 network  web_proxy
    data/firewall.json                  network  firewall
    data/trailmate_beta.log             apps     trailmate_beta
    data/products.csv                   lookup
    data/vendors.csv                    lookup

Deterministic for a given --seed, so every student gets identical data.
Standard library only.
"""

import argparse
import datetime as dt
import ipaddress
import json
import os
import random
import uuid
import zipfile

# --------------------------------------------------------------------------
# The fiction
# --------------------------------------------------------------------------

COMPANY = "Harborview Outfitters"
DOMAIN = "harborviewoutfitters.example"

# productId, product_name, categoryId, price, Code
PRODUCTS = [
    ("HV-TN-101", "Cirrus 2P Tent", "TENTS", 329.00, "A"),
    ("HV-TN-102", "Basecamp 4P Tent", "TENTS", 489.00, "B"),
    ("HV-TN-103", "Tarn Ultralight Shelter", "TENTS", 265.50, "C"),
    ("HV-PK-201", "Ridgeline 65L Pack", "PACKS", 219.99, "D"),
    ("HV-PK-202", "Daybreak 28L Pack", "PACKS", 94.50, "E"),
    ("HV-PK-203", "Portage Haul Duffel", "PACKS", 139.00, "F"),
    ("HV-FW-301", "Scree Approach Shoe", "FOOTWEAR", 148.00, "G"),
    ("HV-FW-302", "Kettle Ridge Boot", "FOOTWEAR", 232.00, "H"),
    ("HV-FW-303", "Shoal River Sandal", "FOOTWEAR", 72.00, "I"),
    ("HV-NV-401", "Meridian GPS Handheld", "NAVIGATION", 399.00, "J"),
    ("HV-NV-402", "Lodestone Compass", "NAVIGATION", 46.00, "K"),
    ("HV-AP-501", "Stormwall Shell", "APPAREL", 288.00, "L"),
    ("HV-AP-502", "Thermal Grid Midlayer", "APPAREL", 124.00, "M"),
    ("HV-AP-503", "Headland Sun Hoody", "APPAREL", 79.00, "N"),
]

# VendorID ranges carry meaning; the labs rely on this.
#   1000-2999 United States      3000-3999 Canada
#   4000-4999 Latin America      5000-6999 Europe & Middle East
#   7000-8999 Asia Pacific       9000-9900 Africa
#   9901-9999 Outliers
VENDOR_REGIONS = [
    (1000, 2999, "United States", [
        ("Anchorage", "Alaska"), ("Bozeman", "Montana"), ("Asheville", "North Carolina"),
        ("Bend", "Oregon"), ("Flagstaff", "Arizona"), ("Burlington", "Vermont"),
        ("Duluth", "Minnesota"), ("Boulder", "Colorado"), ("Tacoma", "Washington"),
        ("Santa Fe", "New Mexico"), ("Portland", "Maine"), ("Chattanooga", "Tennessee"),
    ]),
    (3000, 3999, "Canada", [
        ("Canmore", "Alberta"), ("Squamish", "British Columbia"),
        ("Thunder Bay", "Ontario"), ("Chicoutimi", "Quebec"),
    ]),
    (4000, 4999, "Chile", [("Puerto Varas", "Los Lagos"), ("Pucon", "Araucania")]),
    (5000, 6999, "Germany", [("Garmisch", "Bavaria"), ("Freiburg", "Baden-Wurttemberg")]),
    (5000, 6999, "France", [("Chamonix", "Haute-Savoie"), ("Annecy", "Haute-Savoie")]),
    (5000, 6999, "Italy", [("Bolzano", "South Tyrol"), ("Courmayeur", "Aosta Valley")]),
    (5000, 6999, "United Kingdom", [("Fort William", "Scotland"), ("Keswick", "England")]),
    (7000, 8999, "Japan", [("Hakuba", "Nagano"), ("Sapporo", "Hokkaido")]),
    (7000, 8999, "New Zealand", [("Wanaka", "Otago"), ("Nelson", "Tasman")]),
    (9000, 9900, "South Africa", [("Hermanus", "Western Cape")]),
    (9901, 9999, "Antarctica", [("Rothera", "Adelaide Island")]),
]

VENDOR_PREFIX = ["Summit", "Harbor", "Granite", "Northline", "Trailhead", "Cedar",
                 "Lantern", "Anvil", "Meridian", "Driftwood", "Foxglove", "Bastion"]
VENDOR_SUFFIX = ["Outfitters", "Supply", "Gear Co", "Provisions", "Trading Post",
                 "Equipment", "Mercantile"]

USER_FIRST = ["ana", "ben", "cara", "dev", "elin", "femi", "gus", "hana", "ivo",
              "jun", "kara", "liam", "mira", "nils", "omar", "priya", "quinn",
              "rosa", "sam", "tev", "uma", "vik", "wren", "yara", "zane"]
USER_LAST = ["abbott", "benali", "cho", "dumas", "eriksen", "fontaine", "gupta",
             "hassan", "ibarra", "jansen", "kowal", "lindqvist", "moreau",
             "nakamura", "okafor", "petrov", "quintero", "ramirez", "silva",
             "tanaka", "ueda", "varga", "whitfield", "yilmaz", "zadeh"]

PRIV_USERS = ["admin", "administrator", "sysadmin", "itmadmin", "sapadmin"]

WEB_HOSTS = ["www1", "www2", "www3"]
SECURE_HOSTS = ["www1", "www2", "www3", "mailsv"]

AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

REFERERS = [
    "https://www.example-search.test/",
    f"https://www.{DOMAIN}/home",
    f"https://www.{DOMAIN}/category",
    "https://news.example.test/gear-roundup",
    "-",
]

CONTENT_TYPES = [
    "image/png", "image/jpeg", "image/webp", "text/html", "text/css",
    "application/javascript", "application/json", "application/pdf",
    "video/mp4", "font/woff2",
]

PROXY_CATEGORIES = ["Shopping", "News", "Social Networking", "Streaming Media",
                    "Business", "Search Engines", "Technology", "Travel"]

DEPARTMENTS = ["Engineering", "Sales", "Finance", "Support", "Marketing",
               "Operations", "Legal", "People"]

FIREWALL_ACTIONS = ["allowed", "blocked", "teardown", "built"]

BETA_EVENTS = ["launch", "route_saved", "waypoint_added", "sync", "offline_cache",
               "share", "crash_report"]
BETA_ROLES = ["Guide", "Member", "Trial", "Admin"]
BETA_VERSIONS = ["1.4.0", "1.4.1", "1.5.0", "2.0.0-beta1", "2.0.0-beta2"]

ACTIONS = ["view", "addtocart", "remove", "purchase"]


def accounts(n):
    """Deterministic spread of first-initial + surname logins.

    Iterating the raw cross product and slicing only ever reached the first
    few first names, so every account looked like a variation of one person.
    Striding the surname list keeps both halves varied.
    """
    out = []
    for i in range(n):
        # Treat i as a two-digit number in base len(USER_FIRST): varying the
        # low digit against the high one gives every pair exactly once. A
        # stride instead collides, because both name lists are the same
        # length, and yields only len(USER_FIRST) distinct accounts.
        first = USER_FIRST[i % len(USER_FIRST)]
        last = USER_LAST[(i // len(USER_FIRST)) % len(USER_LAST)]
        out.append(f"{first[0]}{last}")
    return out


def write_ndjson(path, records):
    """One JSON object per line.

    A pretty-printed array is a single blob as far as Splunk is concerned, and
    breaking it into events needs hand-written LINE_BREAKER and
    SHOULD_LINEMERGE props. Newline-delimited JSON is split on newlines like
    any other log and `KV_MODE = json` picks the fields up directly.
    """
    with open(path, "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")


def ts(d):
    return d.strftime("%d/%b/%Y:%H:%M:%S")


def client_ips(rng, n):
    pool = []
    while len(pool) < n:
        a = rng.choice([23, 46, 67, 91, 103, 128, 172, 194, 201, 209, 217])
        ip = ipaddress.IPv4Address((a << 24) + rng.randrange(1 << 24))
        if ip.is_global:
            pool.append(str(ip))
    return pool


# --------------------------------------------------------------------------
# Lookups
# --------------------------------------------------------------------------

def write_products(out):
    path = os.path.join(out, "products.csv")
    with open(path, "w", newline="") as fh:
        fh.write("productId,product_name,categoryId,price,Code\n")
        for pid, name, cat, price, code in PRODUCTS:
            fh.write(f"{pid},{name},{cat},{price:.2f},{code}\n")
    return path


def build_vendors(rng):
    rows, used = [], set()
    for lo, hi, country, places in VENDOR_REGIONS:
        for city, region in places:
            while True:
                vid = rng.randrange(lo, hi + 1)
                if vid not in used:
                    used.add(vid)
                    break
            name = f"{rng.choice(VENDOR_PREFIX)} {rng.choice(VENDOR_SUFFIX)}"
            rows.append({
                "Vendor": name,
                "VendorCity": city,
                "VendorID": vid,
                "VendorStateProvince": region,
                "VendorCountry": country,
                "Weight": rng.randrange(1, 9),
            })
    rows.sort(key=lambda r: r["VendorID"])
    return rows


def write_vendors(out, vendors):
    path = os.path.join(out, "vendors.csv")
    cols = ["Vendor", "VendorCity", "VendorID", "VendorStateProvince",
            "VendorCountry", "Weight"]
    with open(path, "w", newline="") as fh:
        fh.write(",".join(cols) + "\n")
        for v in vendors:
            fh.write(",".join(str(v[c]) for c in cols) + "\n")
    return path


# --------------------------------------------------------------------------
# Web access logs
# --------------------------------------------------------------------------

def write_access(out, rng, now, days, sessions):
    """Combined log format plus a trailing response time, one dir per host."""
    ips = client_ips(rng, 220)
    lines = {h: [] for h in WEB_HOSTS}

    for _ in range(sessions):
        host = rng.choice(WEB_HOSTS)
        ip = rng.choice(ips)
        agent = rng.choice(AGENTS)
        jsession = "SD" + uuid.UUID(int=rng.getrandbits(128)).hex[:14].upper()
        start = now - dt.timedelta(
            seconds=rng.randrange(days * 86400),
        )
        clock = start
        # A session browses, maybe adds to cart, maybe buys.
        views = rng.randrange(1, 7)
        basket = []
        for _ in range(views):
            prod = rng.choice(PRODUCTS)
            clock += dt.timedelta(seconds=rng.randrange(3, 180))
            lines[host].append((clock, _access_line(
                ip, clock, "GET", "/viewItem", prod[0], "view", jsession,
                200, rng.randrange(1200, 4200), rng, agent)))
            if rng.random() < 0.38:
                clock += dt.timedelta(seconds=rng.randrange(2, 90))
                basket.append(prod)
                lines[host].append((clock, _access_line(
                    ip, clock, "POST", "/addItem", prod[0], "addtocart", jsession,
                    200, rng.randrange(400, 1400), rng, agent)))
                if rng.random() < 0.18:
                    clock += dt.timedelta(seconds=rng.randrange(5, 120))
                    basket.pop()
                    lines[host].append((clock, _access_line(
                        ip, clock, "POST", "/cart", prod[0], "remove", jsession,
                        200, rng.randrange(300, 900), rng, agent)))
        if basket and rng.random() < 0.55:
            clock += dt.timedelta(seconds=rng.randrange(10, 240))
            # Checkouts fail sometimes; the labs look for 4xx/5xx.
            roll = rng.random()
            status = 200 if roll < 0.9 else (503 if roll < 0.96 else 404)
            for prod in basket:
                lines[host].append((clock, _access_line(
                    ip, clock, "POST", "/checkout", prod[0], "purchase", jsession,
                    status, rng.randrange(900, 3600), rng, agent)))
                clock += dt.timedelta(seconds=rng.randrange(1, 10))

    path = os.path.join(out, "access.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for host, rows in lines.items():
            rows.sort(key=lambda r: r[0])
            z.writestr(f"access/{host}/access.log",
                       "\n".join(line for _, line in rows) + "\n")
    return path, sum(len(v) for v in lines.values())


def _access_line(ip, when, method, path, pid, action, jsession, status, size,
                 rng, agent):
    uri = (f"{path}?productId={pid}&action={action}"
           f"&JSESSIONID={jsession}")
    return (f'{ip} - - [{ts(when)}] "{method} {uri} HTTP/1.1" '
            f'{status} {size} "{rng.choice(REFERERS)}" "{agent}" '
            f'{rng.randrange(40, 2400)}')


# --------------------------------------------------------------------------
# Linux secure logs
# --------------------------------------------------------------------------

def write_secure(out, rng, now, days, count):
    ips = client_ips(rng, 90)
    people = accounts(120)
    lines = {h: [] for h in SECURE_HOSTS}

    for _ in range(count):
        host = rng.choice(SECURE_HOSTS)
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        stamp = when.strftime("%b %d %H:%M:%S")
        pid = rng.randrange(1000, 32000)
        roll = rng.random()
        if roll < 0.30:
            user = rng.choice(PRIV_USERS) if rng.random() < 0.45 else rng.choice(people)
            lines[host].append((when,
                f"{stamp} {host} sshd[{pid}]: Failed password for {user} "
                f"from {rng.choice(ips)} port {rng.randrange(1024, 65535)} ssh2"))
        elif roll < 0.60:
            user = rng.choice(people)
            lines[host].append((when,
                f"{stamp} {host} sshd[{pid}]: Accepted password for {user} "
                f"from {rng.choice(ips)} port {rng.randrange(1024, 65535)} ssh2"))
        elif roll < 0.85:
            lines[host].append((when,
                f"{stamp} {host} sshd[{pid}]: pam_unix(sshd:session): "
                f"session opened for user {rng.choice(people)} by (uid=0)"))
        else:
            lines[host].append((when,
                f"{stamp} {host} sudo: {rng.choice(people)} : TTY=pts/{rng.randrange(0,6)} ; "
                f"PWD=/home ; USER=root ; COMMAND=/usr/bin/{rng.choice(['systemctl','tail','vi','less'])}"))

    path = os.path.join(out, "secure.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for host, rows in lines.items():
            rows.sort(key=lambda r: r[0])
            z.writestr(f"secure/{host}/secure.log",
                       "\n".join(line for _, line in rows) + "\n")
    return path, sum(len(v) for v in lines.values())


# --------------------------------------------------------------------------
# Retail / sales
# --------------------------------------------------------------------------

def write_vendor_sales(out, rng, now, days, vendors, count):
    path = os.path.join(out, "vendor_sales.log")
    rows = []
    for _ in range(count):
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        v = rng.choice(vendors)
        code = rng.choice(PRODUCTS)[4]
        acct = "".join(str(rng.randrange(10)) for _ in range(16))
        rows.append((when, f"[{ts(when)}] VendorID={v['VendorID']} "
                           f"Code={code} AcctID={acct}"))
    rows.sort(key=lambda r: r[0])
    with open(path, "w") as fh:
        fh.write("\n".join(line for _, line in rows) + "\n")
    return path, len(rows)


def write_sales_entries(out, rng, now, days, count):
    path = os.path.join(out, "sales_entries.json")
    recs = []
    for _ in range(count):
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        prod = rng.choice(PRODUCTS)
        qty = rng.randrange(1, 5)
        recs.append({
            "timestamp": when.replace(microsecond=0).isoformat(),
            "TransactionID": str(uuid.UUID(int=rng.getrandbits(128))),
            "CustomerID": f"C{rng.randrange(100000, 999999)}",
            "AcctCode": f"AC-{rng.randrange(1000, 9999)}",
            "productId": prod[0],
            "quantity": qty,
            "unit_price": prod[3],
            "total": round(prod[3] * qty, 2),
            "channel": rng.choice(["online", "retail", "phone", "partner"]),
        })
    recs.sort(key=lambda r: r["timestamp"])
    write_ndjson(path, recs)
    return path, len(recs)


# --------------------------------------------------------------------------
# Network
# --------------------------------------------------------------------------

def write_web_proxy(out, rng, now, days, count):
    """Proxy/content-filter records. Lab 8 aliases cs_username to user and
    derives megabytes from sc_bytes; Lab 4 groups by http_content_type."""
    path = os.path.join(out, "web_proxy.json")
    people = [f"{USER_FIRST[i % len(USER_FIRST)]}."
              f"{USER_LAST[(i // len(USER_FIRST)) % len(USER_LAST)]}"
              for i in range(150)]
    recs = []
    for _ in range(count):
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        recs.append({
            "timestamp": when.replace(microsecond=0).isoformat(),
            "cs_username": rng.choice(people),
            "s_hostname": f"proxy{rng.randrange(1,4)}.{DOMAIN}",
            "cs_method": rng.choice(["GET", "POST", "CONNECT", "HEAD"]),
            "cs_url": f"https://{rng.choice(['store','docs','news','video','cdn'])}.example.test/"
                      f"{rng.choice(['index','asset','stream','api','img'])}",
            "sc_http_status": rng.choice([200, 200, 200, 204, 301, 403, 404, 502]),
            "sc_bytes": rng.randrange(800, 9_500_000),
            "http_content_type": rng.choice(CONTENT_TYPES),
            "x_category": rng.choice(PROXY_CATEGORIES),
            "usage": rng.choice(PROXY_CATEGORIES),
            "duration": rng.randrange(5, 9000),
        })
    recs.sort(key=lambda r: r["timestamp"])
    write_ndjson(path, recs)
    return path, len(recs)


def write_firewall(out, rng, now, days, count):
    path = os.path.join(out, "firewall.json")
    people = accounts(150)
    recs = []
    for _ in range(count):
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        recs.append({
            "timestamp": when.replace(microsecond=0).isoformat(),
            "Username": rng.choice(people),
            "Department": rng.choice(DEPARTMENTS),
            "src_ip": str(ipaddress.IPv4Address(rng.randrange(1 << 24) + (10 << 24))),
            "dest_ip": str(ipaddress.IPv4Address(rng.randrange(1 << 24) + (172 << 24))),
            "dest_port": rng.choice([22, 80, 443, 445, 3389, 8080, 8443]),
            "action": rng.choice(FIREWALL_ACTIONS),
            "protocol": rng.choice(["tcp", "udp"]),
            "bytes_out": rng.randrange(60, 2_000_000),
            "Duration": rng.randrange(1, 600),
        })
    recs.sort(key=lambda r: r["timestamp"])
    write_ndjson(path, recs)
    return path, len(recs)


# --------------------------------------------------------------------------
# App beta logs - deliberately headerless and delimited, for the field
# extraction lab.
# --------------------------------------------------------------------------

def write_beta(out, rng, now, days, count):
    path = os.path.join(out, "trailmate_beta.log")
    ips = client_ips(rng, 140)
    rows = []
    for _ in range(count):
        when = now - dt.timedelta(seconds=rng.randrange(days * 86400))
        first, last = rng.choice(USER_FIRST), rng.choice(USER_LAST)
        rows.append((when,
            f"{when.replace(microsecond=0).isoformat()},"
            f"{rng.choice(ips)},"
            f"{rng.choice(BETA_VERSIONS)},"
            f"{rng.choice(BETA_EVENTS)},"
            f"user:{first}.{last}@example.test "
            f"DeviceName:{rng.choice(['Pathfinder','Wayfarer','Compass','Beacon'])}-{rng.randrange(10,99)} "
            f"action:{rng.choice(['completed','failed','retried','queued'])} "
            f"role:{rng.choice(BETA_ROLES)}"))
    rows.sort(key=lambda r: r[0])
    with open(path, "w") as fh:
        fh.write("\n".join(line for _, line in rows) + "\n")
    return path, len(rows)


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=f"Generate the {COMPANY} dataset.")
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default=os.path.join(here, "data"))
    ap.add_argument("--days", type=int, default=35,
                    help="how far back events should reach (default 35)")
    ap.add_argument("--seed", type=int, default=1729,
                    help="change only if you want a different dataset")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rng = random.Random(args.seed)
    now = dt.datetime.now().replace(microsecond=0)

    print(f"{COMPANY} dataset -> {args.out}")
    print(f"  seed {args.seed}, {args.days} days back from {now:%Y-%m-%d %H:%M}\n")

    vendors = build_vendors(rng)
    results = [
        ("products.csv", write_products(args.out), len(PRODUCTS)),
        ("vendors.csv", write_vendors(args.out, vendors), len(vendors)),
    ]
    for label, (path, n) in [
        ("access.zip", write_access(args.out, rng, now, args.days, 4200)),
        ("secure.zip", write_secure(args.out, rng, now, args.days, 9000)),
        ("vendor_sales.log", write_vendor_sales(args.out, rng, now, args.days, vendors, 8000)),
        ("sales_entries.json", write_sales_entries(args.out, rng, now, args.days, 5000)),
        ("web_proxy.json", write_web_proxy(args.out, rng, now, args.days, 6000)),
        ("firewall.json", write_firewall(args.out, rng, now, args.days, 6000)),
        ("trailmate_beta.log", write_beta(args.out, rng, now, args.days, 4000)),
    ]:
        results.append((label, path, n))

    for label, path, n in results:
        size = os.path.getsize(path if isinstance(path, str) else path)
        print(f"  {label:22s} {n:>7,} records  {size/1024:>8.1f} KB")

    print(f"\n  {len(PRODUCTS)} products, {len(vendors)} vendors across "
          f"{len({v['VendorCountry'] for v in vendors})} countries")


if __name__ == "__main__":
    main()
