#!/usr/bin/env python3
"""Render the course decks as self-contained Reveal.js HTML.

Each module becomes one HTML file with Reveal's CSS and JS inlined, so a deck
is a single file that opens from disk with no network and no build step. The
vendored Reveal assets live in tools/reveal/.

    python3 tools/build_presentations.py
    python3 tools/build_presentations.py --only 3 7

Slide content lives in tools/course_content.py; this file is only the
renderer. Editing content there and re-running keeps all fourteen decks
consistent, which hand-maintaining fourteen copies of the same CSS does not.
"""

import argparse
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Work when run from any directory, and under `python3 -I`, which drops the
# script's own directory from sys.path.
sys.path.insert(0, HERE)

from course_content import MODULES, COURSE_TITLE, COMPANY  # noqa: E402
ROOT = os.path.dirname(HERE)
REVEAL = os.path.join(HERE, "reveal")

# Splunk brand-adjacent palette, defined once and themed per module.
BASE_CSS = """
:root {
  --accent: %(accent)s;
  --accent-dark: %(accent_dark)s;
  --ink: #1f2933;
  --muted: #52606d;
  --rule: #e4e7eb;
  --ok: #178a52;
  --warn: #b7791f;
  --bad: #c53030;
  --code-bg: #1f2430;
  --code-fg: #e6e8eb;
}
.reveal {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, sans-serif;
  font-size: 30px; font-weight: 300; color: var(--ink);
}
.reveal h1, .reveal h2, .reveal h3, .reveal h4 {
  color: var(--accent); text-transform: none; font-weight: 600;
  letter-spacing: normal; margin-bottom: .4em;
}
.reveal h1 { font-size: 1.65em; }
.reveal h2 { font-size: 1.18em; }
.reveal h3 { font-size: .95em; color: var(--muted); }
.reveal .slides section {
  text-align: left; height: 100%%; padding: 14px 10px; box-sizing: border-box;
  overflow-y: auto; overflow-x: hidden;
}
.reveal .slides section.title-slide,
.reveal .slides section.lab-callout { text-align: center; }
.reveal ul, .reveal ol { display: block; margin-left: 1.1em; }
.reveal li { margin: .22em 0; line-height: 1.35; }
.reveal p { line-height: 1.4; }
.reveal strong { color: var(--accent-dark); font-weight: 600; }
.reveal .emoji { font-style: normal; }

.reveal .two-column { display: flex; gap: 26px; align-items: flex-start; }
.reveal .two-column > .column { flex: 1; min-width: 0; }

.reveal pre {
  width: 100%%; box-shadow: none; border-radius: 8px; margin: .5em 0;
  font-size: .5em; line-height: 1.45;
}
.reveal pre code {
  display: block; padding: 14px 16px; background: var(--code-bg);
  color: var(--code-fg); border-radius: 8px; max-height: none;
  overflow-x: auto; white-space: pre-wrap; word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.reveal code:not(pre code) {
  background: #eef1f4; color: var(--accent-dark); border-radius: 4px;
  padding: .08em .3em; font-size: .85em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
/* SPL highlighting, applied by the inline script below. */
.spl-cmd  { color: #7cc5ff; font-weight: 600; }
.spl-fn   { color: #f6a2d8; }
.spl-str  { color: #b5e8a0; }
.spl-num  { color: #ffd083; }
.spl-pipe { color: #ff9f6e; font-weight: 700; }
.spl-cmt  { color: #8b97a8; font-style: italic; }

.reveal .note, .reveal .warn, .reveal .good {
  border-left: 5px solid var(--accent); background: #f6f8fa;
  padding: 10px 16px; border-radius: 6px; margin: .5em 0; font-size: .82em;
}
.reveal .warn { border-left-color: var(--warn); background: #fffaf0; }
.reveal .good { border-left-color: var(--ok); background: #f2fbf6; }

.reveal table { font-size: .62em; border-collapse: collapse; width: 100%%; }
.reveal table th, .reveal table td {
  border: none; border-bottom: 1px solid var(--rule);
  padding: .32em .5em; text-align: left;
}
.reveal table th { color: var(--muted); font-weight: 600; }

.reveal .lab-callout { display: flex; align-items: center; justify-content: center; }
.reveal .lab-callout h1, .reveal .lab-callout h2,
.reveal .lab-callout h3, .reveal .lab-callout strong { color: #fff; }
.reveal .lab-callout code:not(pre code) {
  background: rgba(255,255,255,.2); color: #fff;
}
.reveal .lab-callout h1 { font-size: 1.35em; margin-bottom: .1em; }
.reveal .lab-callout h2 { font-size: 1.0em; margin-bottom: .6em; opacity: .92; }
.reveal .lab-callout .panel {
  background: rgba(255,255,255,.12); padding: 22px 28px; border-radius: 14px;
  margin: 14px auto; max-width: 80%%; text-align: left;
}
.reveal .lab-callout .panel ul { font-size: .9em; }
.reveal .lab-callout .kicker {
  background: rgba(255,255,255,.18); border-left: 5px solid rgba(255,255,255,.65);
  padding: 12px 20px; border-radius: 8px; margin: 10px auto; max-width: 80%%;
  font-size: .82em; text-align: left;
}
.reveal .title-slide .sub { color: var(--muted); font-size: .8em; }
.reveal .title-slide .modnum {
  display: inline-block; background: var(--accent); color: #fff;
  padding: .18em .7em; border-radius: 999px; font-size: .6em;
  letter-spacing: .08em; text-transform: uppercase; margin-bottom: .6em;
}
.progress-indicator {
  position: fixed; bottom: 10px; right: 14px; z-index: 40;
  font: 500 13px/1 -apple-system, system-ui, sans-serif;
  color: var(--muted); opacity: .75;
}
@media print { .progress-indicator { display: none; } }
"""

SPL_SCRIPT = r"""
// Minimal SPL highlighter. highlight.js has no SPL grammar and its bundle is
// 900 KB, which is not worth inlining fourteen times for a language it does
// not know. This covers what the decks actually show.
(function () {
  var COMMANDS = ('search|stats|eventstats|streamstats|chart|timechart|top|rare|'
    + 'table|fields|where|eval|rename|sort|dedup|head|tail|lookup|inputlookup|'
    + 'outputlookup|transaction|join|append|appendcols|union|makeresults|rex|'
    + 'erex|regex|replace|fillnull|filldown|addtotals|addcoltotals|untable|'
    + 'xyseries|bin|bucket|iplocation|geostats|geom|trendline|predict|'
    + 'anomalies|anomalousvalue|cluster|associate|concurrency|datamodel|'
    + 'pivot|tstats|metadata|eventcount|map|foreach|multisearch|'
    + 'collect|sendemail|convert|spath|mvexpand|mvcombine|nomv|'
    + 'reverse|delta|accum|outlier|rangemap|abstract|highlight|format').split('|');
  var FUNCS = ('count|dc|distinct_count|sum|avg|min|max|median|mode|stdev|var|'
    + 'values|list|first|last|earliest|latest|range|perc|per_minute|per_hour|'
    + 'per_day|sparkline|round|floor|ceiling|abs|sqrt|pow|exact|tostring|'
    + 'tonumber|strftime|strptime|if|case|coalesce|isnull|isnotnull|isnum|'
    + 'isstr|like|match|searchmatch|substr|len|lower|upper|trim|ltrim|rtrim|'
    + 'split|mvcount|mvindex|mvfilter|mvjoin|mvzip|nullif|validate|cidrmatch|'
    + 'relative_time|now|time|typeof|json_extract').split('|');
  var cmdRe = new RegExp('(^|\\|\\s*)(' + COMMANDS.join('|') + ')\\b', 'g');
  var fnRe = new RegExp('\\b(' + FUNCS.join('|') + ')(?=\\s*\\()', 'g');

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function paint(src) {
    var out = '', i = 0;
    // Pull strings and comments out first so keywords inside them are left alone.
    var re = /"(?:[^"\\]|\\.)*"|```[\s\S]*?```|^\s*#.*$/gm, m;
    while ((m = re.exec(src)) !== null) {
      out += body(src.slice(i, m.index));
      var cls = m[0][0] === '"' ? 'spl-str' : 'spl-cmt';
      out += '<span class="' + cls + '">' + esc(m[0]) + '</span>';
      i = m.index + m[0].length;
    }
    return out + body(src.slice(i));
  }

  function body(s) {
    return esc(s)
      .replace(cmdRe, function (_, lead, cmd) {
        return lead.replace('|', '<span class="spl-pipe">|</span>')
             + '<span class="spl-cmd">' + cmd + '</span>';
      })
      .replace(fnRe, '<span class="spl-fn">$1</span>')
      .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="spl-num">$1</span>')
      .replace(/\|/g, function (p) {
        return p === '|' ? '<span class="spl-pipe">|</span>' : p;
      });
  }

  document.querySelectorAll('pre > code.spl').forEach(function (el) {
    el.innerHTML = paint(el.textContent);
  });
})();
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Module {num}: {title}</title>
<style>{reveal_css}</style>
<style>{theme_css}</style>
<style>{base_css}</style>
</head>
<body>
<div class="reveal"><div class="slides">
{slides}
</div></div>
<script>{reveal_js}</script>
<script>{notes_js}</script>
<script>
Reveal.initialize({{
  width: 1280, height: 760, margin: 0.04,
  minScale: 0.2, maxScale: 1.5,
  hash: true, controls: true, progress: true, center: false,
  touch: true, keyboard: true, overview: true, fragments: true,
  transition: 'slide', transitionSpeed: 'default', backgroundTransition: 'fade',
  plugins: [ RevealNotes ]
}});
</script>
<script>{spl_js}</script>
<script>
var pi = document.createElement('div');
pi.className = 'progress-indicator';
pi.textContent = 'Module {num} / {total}';
document.body.appendChild(pi);
</script>
</body>
</html>
"""


def read(name):
    with open(os.path.join(REVEAL, name), encoding="utf-8") as fh:
        return fh.read()


def shade(hex_color, factor=0.78):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


def spl(code):
    return f'<pre><code class="spl">{html.escape(code.strip())}</code></pre>'


def render_slide(s, mod):
    kind = s.get("type", "content")

    if kind == "title":
        return f"""<section class="title-slide">
<span class="modnum">Module {mod['num']}</span>
<h1>{s['h']}</h1>
<p class="sub">{s.get('sub','')}</p>
</section>"""

    if kind == "lab":
        builds = "".join(f"<li>{b}</li>" for b in s["builds"])
        kicker = f'<div class="kicker">{s["kicker"]}</div>' if s.get("kicker") else ""
        return f"""<section class="lab-callout" data-background-color="{mod['color']}">
<div>
<h1><span class="emoji">&#128300;</span> Hands-On: {s['h']}</h1>
<h2><span class="emoji">&#128640;</span> {s['lab']}</h2>
<div class="panel"><h3>What you will build</h3><ul>{builds}</ul></div>
{kicker}
</div>
</section>"""

    head = f"<h2><span class=\"emoji\">{s['emoji']}</span> {s['h']}</h2>" if s.get("h") else ""
    if "cols" in s:
        cols = "".join(f'<div class="column">{block(c)}</div>' for c in s["cols"])
        body_html = f'<div class="two-column">{cols}</div>'
    else:
        body_html = block(s.get("body", []))
    notes = f"<aside class=\"notes\">{s['notes']}</aside>" if s.get("notes") else ""
    return f"<section>{head}{body_html}{notes}</section>"


def block(items):
    """Content blocks: raw html str, ('spl', code), ('ul', [...]), ('note', txt)."""
    if isinstance(items, str):
        return items
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(it)
        elif it[0] == "spl":
            out.append(spl(it[1]))
        elif it[0] == "ul":
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in it[1]) + "</ul>")
        elif it[0] == "ol":
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in it[1]) + "</ol>")
        elif it[0] in ("note", "warn", "good"):
            out.append(f'<div class="{it[0]}">{it[1]}</div>')
        elif it[0] == "h3":
            out.append(f"<h3>{it[1]}</h3>")
        elif it[0] == "table":
            head, rows = it[1], it[2]
            th = "".join(f"<th>{c}</th>" for c in head)
            tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                         for r in rows)
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>")
        else:
            raise ValueError(f"unknown block {it[0]}")
    return "".join(out)


def build(mod, total, assets):
    slides = [render_slide({"type": "title", "h": mod["title"],
                            "sub": mod.get("sub", COURSE_TITLE)}, mod)]
    slides += [render_slide(s, mod) for s in mod["slides"]]
    return PAGE.format(
        num=mod["num"], title=html.escape(mod["title"]), total=total,
        slides="\n".join(slides),
        base_css=BASE_CSS % {"accent": mod["color"],
                             "accent_dark": shade(mod["color"])},
        spl_js=SPL_SCRIPT, **assets)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(ROOT, "presentations"))
    ap.add_argument("--only", nargs="*", type=int, help="module numbers")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    assets = {
        "reveal_css": read("reveal.min.css"),
        "theme_css": read("white.min.css"),
        "reveal_js": read("reveal.min.js"),
        "notes_js": read("notes.min.js"),
    }

    print(f"{COMPANY} — {COURSE_TITLE}")
    print(f"  {len(MODULES)} modules -> {args.out}\n")
    written = 0
    for mod in MODULES:
        if args.only and mod["num"] not in args.only:
            continue
        name = f"module{mod['num']:02d}_{mod['slug']}.html"
        path = os.path.join(args.out, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build(mod, len(MODULES), assets))
        labs = sum(1 for s in mod["slides"] if s.get("type") == "lab")
        print(f"  {name:48s} {len(mod['slides'])+1:>3} slides, "
              f"{labs} lab{'' if labs == 1 else 's'}, "
              f"{os.path.getsize(path)/1024:>6.0f} KB")
        written += 1
    print(f"\n  {written} deck(s) written, fully self-contained")


if __name__ == "__main__":
    main()
