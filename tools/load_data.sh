#!/usr/bin/env bash
# Prepare a Splunk container for the course.
#
# By default this installs only what must exist *before* students arrive: the
# class app, carrying the parsing rules each sourcetype needs before its first
# event lands, the linux_secure field extractions, and the data models.
#
# It does NOT create the indexes, load the data, or create the lookups.
# Students do all three themselves in Lab 1.
#
#   tools/load_data.sh                 # instructor setup, run before class
#   tools/load_data.sh --with-data     # also do everything Lab 1 does
#   tools/load_data.sh --with-data --append   # add rather than replace
#   CONTAINER=mysplunk tools/load_data.sh
#
# --with-data reaches the state a student has at the end of Lab 1. Use it to
# validate the course (tools/validate_labs.py needs loaded data) or to rescue
# a student whose instance went wrong. Running it for the whole class would
# take Lab 1 away from them.

set -euo pipefail

CONTAINER="${CONTAINER:-splunk}"
AUTH="${AUTH:-admin:password}"
APP="${APP:-splunk_intadv}"
APPDIR="/opt/splunk/etc/apps/$APP"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
DATA="$ROOT/data"
CONF="$ROOT/conf"

INDEXES=(web security sales network apps)
WITH_DATA=0
CLEAN=1
for arg in "$@"; do
  case "$arg" in
    --with-data) WITH_DATA=1 ;;
    --append)    CLEAN=0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

splunk_cmd() { docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk "$@" 2>&1 | grep -v "WARNING: Server Certificate" || true; }
say() { printf '  %s\n' "$*"; }

wait_for_splunkd() {
  for _ in $(seq 1 60); do
    if docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk status 2>/dev/null \
         | grep -q "splunkd is running"; then
      return 0
    fi
    docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk start \
      --accept-license --answer-yes --no-prompt >/dev/null 2>&1 || true
    sleep 5
  done
  return 1
}

docker inspect "$CONTAINER" >/dev/null 2>&1 || {
  echo "No container named '$CONTAINER'. Start Splunk first (see README)." >&2
  exit 1
}

if [ "$WITH_DATA" = 1 ]; then
  echo "Preparing '$CONTAINER', and doing Lab 1 for you"
else
  echo "Preparing '$CONTAINER'. Students do the rest in Lab 1."
fi
echo

# --- the class app ---------------------------------------------------------
# Installed as an app, never into etc/system/local: system configuration is
# shadowed by any app defining the same object, and on a shared training
# instance that is a real collision rather than a theoretical one.
echo "Class app"
docker exec -u splunk "$CONTAINER" mkdir -p \
  "$APPDIR/local" "$APPDIR/default" "$APPDIR/lookups" \
  "$APPDIR/metadata" "$APPDIR/local/data/models"
docker cp "$CONF/app.conf"   "$CONTAINER:$APPDIR/default/app.conf" >/dev/null
docker cp "$CONF/props.conf" "$CONTAINER:$APPDIR/local/props.conf" >/dev/null
docker exec -u root "$CONTAINER" chown -R splunk:splunk "$APPDIR" 2>/dev/null || true
say "app.conf, props.conf -> apps/$APP/"

for m in "$CONF"/models/*.json; do
  docker cp "$m" "$CONTAINER:$APPDIR/local/data/models/$(basename "$m")" >/dev/null
done
say "data models -> apps/$APP/local/data/models/"

docker exec -u splunk "$CONTAINER" bash -c "cat > $APPDIR/metadata/local.meta <<'META'
[]
access = read : [ * ], write : [ admin, power ]
export = system
META"
say "objects shared app-wide"
echo

if [ "$WITH_DATA" = 0 ]; then
  echo "Restarting Splunk so the configuration loads"
  docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk restart >/dev/null 2>&1 || true
  wait_for_splunkd || { echo "  splunkd did not come back up" >&2; exit 1; }
  say "splunkd is running"
  echo
  cat <<'DONE'
Ready. The instance has the class app, the parsing rules, the linux_secure
field extractions and the data models — and no indexes, no data, no lookups.

Students build those in Lab 1:
  labs/lab01_loading_the_data.md

To reach that end state yourself, for validation or to rescue a student:
  tools/load_data.sh --with-data
DONE
  exit 0
fi

# ===========================================================================
# Everything below is what Lab 1 has students do.
# ===========================================================================

echo "Indexes"
for idx in "${INDEXES[@]}"; do
  if splunk_cmd list index -auth "$AUTH" | grep -qx "$idx"; then
    say "$idx exists"
  else
    splunk_cmd add index "$idx" -auth "$AUTH" >/dev/null
    say "$idx created"
  fi
done
echo

echo "Lookups"
# conf/instructor_lookups.conf holds both halves so there is one copy to
# maintain; split it into the two files Splunk expects.
awk '/^# ---- props.conf ----/{f=1;next} /^# ---- transforms.conf ----/{f=0;next} !f' \
  "$CONF/instructor_lookups.conf" > /tmp/ct.conf
awk '/^# ---- props.conf ----/{f=1;next} f' \
  "$CONF/instructor_lookups.conf" > /tmp/cp.conf
docker cp /tmp/ct.conf "$CONTAINER:$APPDIR/local/transforms.conf" >/dev/null
docker exec -u splunk "$CONTAINER" bash -c "cat >> $APPDIR/local/props.conf" < /tmp/cp.conf
rm -f /tmp/ct.conf /tmp/cp.conf
for csv in products.csv vendors.csv http_status.csv; do
  [ -f "$DATA/$csv" ] && docker cp "$DATA/$csv" "$CONTAINER:$APPDIR/lookups/$csv" >/dev/null
done
docker exec -u root "$CONTAINER" chown -R splunk:splunk "$APPDIR" 2>/dev/null || true
say "definitions and automatic lookups installed"
echo

echo "Restarting Splunk"
docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk stop >/dev/null 2>&1 || true
if [ "$CLEAN" = 1 ]; then
  # `splunk clean eventdata` is refused while splunkd runs and reports success
  # anyway, which silently multiplies every index on a re-run. Clean while it
  # is stopped.
  for idx in "${INDEXES[@]}"; do
    docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk \
      clean eventdata -index "$idx" -f >/dev/null 2>&1 || true
  done
  say "indexes emptied"
fi
wait_for_splunkd || { echo "  splunkd did not come back up" >&2; exit 1; }
say "splunkd is running"
echo

echo "Staging"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp "$DATA"/*.log "$DATA"/*.json "$DATA"/*.csv "$STAGE"/ 2>/dev/null || true
for z in access secure; do
  [ -f "$DATA/$z.zip" ] && python3 -c \
    "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" \
    "$DATA/$z.zip" "$STAGE"
done
# docker cp lands files as root, so the splunk user cannot clear them later.
docker exec -u root "$CONTAINER" rm -rf /tmp/coursedata
docker exec -u splunk "$CONTAINER" mkdir -p /tmp/coursedata
docker cp "$STAGE/." "$CONTAINER:/tmp/coursedata/" >/dev/null
docker exec -u root "$CONTAINER" chown -R splunk:splunk /tmp/coursedata
say "unpacked on the host and copied to /tmp/coursedata"
echo

oneshot() { # path index sourcetype host
  local out
  out=$(docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk \
        add oneshot "$1" -index "$2" -sourcetype "$3" -host "$4" \
        -auth "$AUTH" 2>&1 | grep -v "WARNING: Server Certificate") || true
  case "$out" in
    *"not running"*|*rror*) echo "  FAILED $1: $out" >&2; return 1 ;;
  esac
  say "$(printf '%-30s -> index=%-9s sourcetype=%s' \
        "$(basename "$(dirname "$1")")/$(basename "$1")" "$2" "$3")"
}

echo "Ingesting"
for h in www1 www2 www3; do
  oneshot "/tmp/coursedata/access/$h/access.log" web access_combined "$h"
done
for h in www1 www2 www3 mailsv; do
  oneshot "/tmp/coursedata/secure/$h/secure.log" security linux_secure "$h"
done
oneshot /tmp/coursedata/vendor_sales.log    sales   vendor_sales    appserver
oneshot /tmp/coursedata/sales_entries.json  sales   sales_entries   appserver
oneshot /tmp/coursedata/web_proxy.json      network web_proxy       proxy
oneshot /tmp/coursedata/firewall.json       network firewall        firewall
oneshot /tmp/coursedata/trailmate_beta.log  apps    trailmate_beta  appserver
echo

echo "Indexed event counts"
# Counts taken straight after a oneshot report mid-ingest totals, and early in
# a load the indexes report zero for several seconds running, which looks
# stable and is wrong. Wait for three equal non-trivial readings.
last=""; same=0
for _ in $(seq 1 60); do
  n=$(splunk_cmd search '| metadata type=sourcetypes index=web index=security index=sales index=network index=apps | stats sum(totalCount) as n' \
      -auth "$AUTH" -preview false | tail -1 | tr -dc '0-9')
  if [ -n "$n" ] && [ "$n" -gt 1000 ] && [ "$n" = "$last" ]; then
    same=$((same + 1)); [ "$same" -ge 2 ] && break
  else
    same=0
  fi
  last="$n"; sleep 3
done
splunk_cmd search '| metadata type=sourcetypes index=web index=security index=sales index=network index=apps | table sourcetype totalCount' \
  -auth "$AUTH" -preview false | sed 's/^/  /'
echo
echo "This is the state a student reaches at the end of Lab 1."
