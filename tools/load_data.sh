#!/usr/bin/env bash
# Load the course dataset into a Splunk Docker container.
#
# Does what README sections 4-6 describe through the UI, for when you want it
# repeatable: creates the indexes, writes the props the JSON sourcetypes need,
# and one-shots every file with the right index, sourcetype and host.
#
#   tools/load_data.sh                  # container "splunk", data from data/
#   CONTAINER=mysplunk tools/load_data.sh
#   tools/load_data.sh --append         # add to what is there instead of replacing
#
# Lookups still have to be created in the UI: the labs depend on them being
# *automatic* lookups, and setting that up is part of what students see.

set -euo pipefail

CONTAINER="${CONTAINER:-splunk}"
AUTH="${AUTH:-admin:password}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="$(cd "$HERE/.." && pwd)/data"
# Idempotent by default: `add oneshot` happily indexes the same file twice, so
# re-running without clearing silently doubles every count.
CLEAN=1
[ "${1:-}" = "--append" ] && CLEAN=0

INDEXES=(web security sales network apps)
APP="${APP:-splunk_intadv}"
APPDIR="/opt/splunk/etc/apps/$APP"

splunk_cmd() { docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk "$@" 2>&1 | grep -v "WARNING: Server Certificate" || true; }

say() { printf '  %s\n' "$*"; }

docker inspect "$CONTAINER" >/dev/null 2>&1 || {
  echo "No container named '$CONTAINER'. Start Splunk first (see README)." >&2
  exit 1
}

echo "Loading the course dataset into container '$CONTAINER'"
echo

# --- indexes ---------------------------------------------------------------
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

# --- props -----------------------------------------------------------------
# The three JSON sources are newline-delimited, so Splunk breaks them into
# events on its own; KV_MODE is what turns each line's keys into fields.
# trailmate_beta is deliberately left raw - Lab 7 is where students extract it.
echo "Sourcetype properties"
# Kept in conf/props.conf rather than inline here, so a hand-built instance can
# use the same file. linux_secure in particular needs it: a stock Splunk ships
# no field extractions for that sourcetype.
CONF="$(cd "$HERE/.." && pwd)/conf"
# Install as an app rather than into etc/system/local. System-level config is
# shadowed by any app that defines the same object, and on a shared training
# instance that is a real collision, not a theoretical one.
docker exec -u splunk "$CONTAINER" mkdir -p \
  "$APPDIR/local" "$APPDIR/default" "$APPDIR/lookups" "$APPDIR/metadata"
docker cp "$CONF/app.conf"        "$CONTAINER:$APPDIR/default/app.conf"        >/dev/null
docker cp "$CONF/props.conf"      "$CONTAINER:$APPDIR/local/props.conf"        >/dev/null
docker cp "$CONF/transforms.conf" "$CONTAINER:$APPDIR/local/transforms.conf"   >/dev/null
say "conf/*.conf -> apps/$APP/"
for csv in products.csv vendors.csv http_status.csv; do
  [ -f "$DATA/$csv" ] && docker cp "$DATA/$csv" "$CONTAINER:$APPDIR/lookups/$csv" >/dev/null
done
say "lookup CSVs -> apps/$APP/lookups/"
# Module 14's datamodel and tstats demonstrations run against these rather
# than the Splunkbase CIM add-on, so nothing has to be downloaded.
if [ -d "$CONF/models" ]; then
  docker exec -u splunk "$CONTAINER" mkdir -p "$APPDIR/local/data/models"
  for m in "$CONF"/models/*.json; do
    docker cp "$m" "$CONTAINER:$APPDIR/local/data/models/$(basename "$m")" >/dev/null
  done
  say "data models -> apps/$APP/local/data/models/"
fi
# Share the objects app-wide, or only the app's owner sees them - which is the
# failure Lab 6 step 19 is about.
docker exec -u splunk "$CONTAINER" bash -c "cat > $APPDIR/metadata/local.meta <<'META'
[]
access = read : [ * ], write : [ admin, power ]
export = system
META"
say "objects shared app-wide"
docker exec -u root "$CONTAINER" chown -R splunk:splunk "$APPDIR" 2>/dev/null || true
echo

# --- stage the files -------------------------------------------------------
echo "Staging"
# Unpack on the host: the Splunk image has no unzip, and Python's zipfile is
# already a dependency of the generator.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp "$DATA"/*.log "$DATA"/*.json "$DATA"/*.csv "$STAGE"/ 2>/dev/null || true
for z in access secure; do
  [ -f "$DATA/$z.zip" ] && python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$DATA/$z.zip" "$STAGE"
done
# docker cp lands files as root, so the splunk user cannot clear them.
docker exec -u root "$CONTAINER" rm -rf /tmp/coursedata
docker exec -u splunk "$CONTAINER" mkdir -p /tmp/coursedata
docker cp "$STAGE/." "$CONTAINER:/tmp/coursedata/" >/dev/null
docker exec -u root "$CONTAINER" chown -R splunk:splunk /tmp/coursedata
say "unpacked on the host and copied to /tmp/coursedata"
echo

# --- restart so the props take effect --------------------------------------
echo "Restarting Splunk"
# `splunk clean eventdata` is refused while splunkd is running, and the CLI
# reports success anyway - which is how re-running this script silently
# tripled every index. Stop first, clean, then start: the start also picks up
# the configuration installed above.
docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk stop >/dev/null 2>&1 || true
if [ "$CLEAN" = 1 ]; then
  for idx in "${INDEXES[@]}"; do
    docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk \
      clean eventdata -index "$idx" -f >/dev/null 2>&1 || true
  done
  say "indexes emptied"
else
  say "keeping existing events (--append)"
fi
# `splunk restart` can return before splunkd is actually accepting commands,
# and sometimes leaves it down altogether. Ingesting into a dead instance
# fails silently, so wait for it rather than assuming.
ready=0
for _ in $(seq 1 60); do
  if docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk status 2>/dev/null | grep -q "splunkd is running"; then
    ready=1; break
  fi
  docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk start \
    --accept-license --answer-yes --no-prompt >/dev/null 2>&1 || true
  sleep 5
done
[ "$ready" = 1 ] || { echo "  splunkd did not come back up; aborting" >&2; exit 1; }
say "splunkd is running"
echo

# --- ingest ----------------------------------------------------------------
oneshot() { # path index sourcetype host
  local out
  if ! out=$(docker exec -u splunk "$CONTAINER" /opt/splunk/bin/splunk \
             add oneshot "$1" -index "$2" -sourcetype "$3" -host "$4" \
             -auth "$AUTH" 2>&1 | grep -v "WARNING: Server Certificate"); then
    echo "  FAILED $1: $out" >&2
    return 1
  fi
  case "$out" in
    *"not running"*|*rror*) echo "  FAILED $1: $out" >&2; return 1 ;;
  esac
  say "$(printf '%-30s -> index=%-9s sourcetype=%s' "$(basename "$(dirname "$1")")/$(basename "$1")" "$2" "$3")"
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
# Counts taken straight after a oneshot report mid-ingest totals. Two equal
# readings is not enough: early on the indexes report 0 for several seconds
# running, which looks stable and is wrong. Wait for three equal non-trivial
# readings in a row.
settled=0; last=""; same=0
for _ in $(seq 1 60); do
  n=$(splunk_cmd search '| metadata type=sourcetypes index=web index=security index=sales index=network index=apps | stats sum(totalCount) as n' -auth "$AUTH" -preview false | tail -1 | tr -dc '0-9')
  if [ -n "$n" ] && [ "$n" -gt 1000 ] && [ "$n" = "$last" ]; then
    same=$((same + 1))
    [ "$same" -ge 2 ] && { settled=1; break; }
  else
    same=0
  fi
  last="$n"
  sleep 3
done
[ "$settled" = 1 ] || say "(counts may still be settling)"
splunk_cmd search '| metadata type=sourcetypes index=web index=security index=sales index=network index=apps | table sourcetype totalCount' -auth "$AUTH" -preview false | sed 's/^/  /'

echo
echo "Done. Indexes, sourcetype properties and the automatic lookups are all in"
echo "place. Students still create everything the labs ask them to build."
