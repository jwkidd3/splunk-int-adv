#!/usr/bin/env python3
"""Slide content for the Splunk Intermediate/Advanced course.

Original material written for this course. Rendered by build_presentations.py.

Block vocabulary inside a slide's ``body`` or ``cols``:
    "raw html"              passed through
    ("h3", text)            sub-heading
    ("ul", [...])           bullet list      ("ol", [...]) numbered
    ("spl", "search ...")   SPL code block, highlighted at runtime
    ("note"|"warn"|"good", text)
    ("table", [headers], [[row], ...])

Every module that has a lab ends with a ``{"type": "lab"}`` slide, and the
teaching content for that lab always precedes it.
"""

COMPANY = "Harborview Outfitters"
COURSE_TITLE = "Splunk Intermediate / Advanced"

WEB = "index=web sourcetype=access_combined"
SEC = "index=security sourcetype=linux_secure"
SALES = "index=sales sourcetype=vendor_sales"
PROXY = "index=network sourcetype=web_proxy"

MODULES = [

# ---------------------------------------------------------------- Module 1
{
 "num": 1, "slug": "course_introduction", "color": "#1b4f9c",
 "title": "Course Introduction",
 "sub": f"{COURSE_TITLE} &middot; {COMPANY}",
 "slides": [
  {"emoji": "&#128218;", "h": "Course Outline", "cols": [
    [("h3", "Searching"),
     ("ol", ["Course Introduction", "Beyond Search Fundamentals",
             "Commands for Visualizations", "Advanced Visualizations",
             "Filtering and Formatting Data", "Correlating Events"])],
    [("h3", "Knowledge objects"),
     "<ol start='7'>" + "".join(f"<li>{x}</li>" for x in [
        "Introduction to Knowledge Objects",
        "Creating and Managing Fields",
        "Field Aliases and Calculated Fields",
        "Creating Tags and Event Types",
        "Creating and Using Macros",
        "Creating and Using Workflow Actions"]) + "</ol>"],
    [("h3", "Modelling and advanced"),
     "<ol start='13'>" + "".join(f"<li>{x}</li>" for x in [
        "Creating Data Models",
        "Using the Common Information Model",
        "Subsearches",
        "Combining Datasets"]) + "</ol>"],
   ]},

  {"emoji": "&#127970;", "h": COMPANY, "cols": [
    [("ul", [f"Outdoor equipment retailer, founded 1998",
             "Sells through <strong>harborviewoutfitters.example</strong> and a "
             "worldwide network of third-party retail vendors",
             "Three web servers, a proxy, a firewall, and a mobile app in beta",
             "Offices in Portland, Vancouver and Munich"]),
     ("note", "Everything in this course &mdash; the company, the products, the "
              "vendors and the logs &mdash; is synthetic and original to the course. "
              "Regenerate it with <code>tools/generate_data.py</code>.")],
    [("h3", "Product catalogue"),
     ("table", ["Category", "Example"], [
        ["TENTS", "Cirrus 2P Tent"],
        ["PACKS", "Ridgeline 65L Pack"],
        ["FOOTWEAR", "Kettle Ridge Boot"],
        ["NAVIGATION", "Meridian GPS Handheld"],
        ["APPAREL", "Stormwall Shell"]])],
   ]},

  {"emoji": "&#128100;", "h": "Your Role", "body": [
    ("ul", ["You are a Splunk <strong>power user</strong> with a strong grasp of "
            "your company's data",
            "You answer questions for people across the business &mdash; security, "
            "IT operations, sales and the product team",
            "You build and maintain the knowledge objects everyone else searches "
            "through",
            "You apply naming conventions so those objects stay findable"]),
    ("good", "By the end of the course you will have built field extractions, "
             "aliases, calculated fields, tags, event types, macros, workflow "
             "actions and a data model &mdash; against real data, not screenshots.")]},

  {"emoji": "&#128451;", "h": "The Data", "body": [
    ("table", ["Index", "Sourcetype", "What it is"], [
      ["<code>web</code>", "<code>access_combined</code>", "Online store access logs, three hosts"],
      ["<code>security</code>", "<code>linux_secure</code>", "Authentication logs, four hosts"],
      ["<code>sales</code>", "<code>vendor_sales</code>", "Retail vendor transactions"],
      ["<code>sales</code>", "<code>sales_entries</code>", "Order records"],
      ["<code>network</code>", "<code>web_proxy</code>", "Employee web traffic"],
      ["<code>network</code>", "<code>firewall</code>", "Firewall sessions"],
      ["<code>apps</code>", "<code>trailmate_beta</code>", "Mobile app beta telemetry"]]),
    ("note", "Two lookups enrich this data: <code>hv_products.csv</code> supplies "
             "<code>product_name</code>, <code>categoryId</code> and <code>price</code>; "
             "<code>hv_vendors.csv</code> supplies <code>VendorCountry</code> and "
             "<code>VendorStateProvince</code>.")]},

  {"type": "lab", "lab": "Lab 1", "h": "Loading the Course Data",
   "builds": [
     "Create the five indexes",
     "Load seven sources, taking the host from the path",
     "Build the automatic lookups that turn codes into names",
     "Verify the counts and, more importantly, the timestamps"],
   "kicker": "Every other lab searches what you load here. A mistyped "
             "sourcetype costs you Lab 2 rather than this one."},

  {"emoji": "&#9881;&#65039;", "h": "Working Conventions", "cols": [
    [("h3", "Saving your work"),
     ("ul", ["Reports are named <code>L&lt;lab&gt;S&lt;step&gt;</code> &mdash; "
             "<code>L2S1</code> is Lab 3, first saved search",
             "Short names are fine here because they are disposable",
             "Module 7 covers what to do in production instead"]),
     ("h3", "Time ranges"),
     ("ul", ["The data is generated relative to today",
             "If a search returns nothing, widen the range before you debug the SPL"])],
    [("h3", "Your app"),
     ("ul", ["Work in the <strong>CLASS: Intermediate</strong> app",
             "Knowledge objects you create belong to that app unless you say otherwise",
             "Lab 13 is the exception and uses Search &amp; Reporting"]),
     ("warn", "This is not a production environment. Splunk's UI shifts between "
              "releases, so a menu may sit a little differently than the steps "
              "describe. The concepts do not move.")],
   ]},
 ]},

# ---------------------------------------------------------------- Module 2
{
 "num": 2, "slug": "beyond_search_fundamentals", "color": "#0a7d8c",
 "title": "Beyond Search Fundamentals",
 "slides": [
  {"emoji": "&#128269;", "h": "What Happens When You Search", "cols": [
    [("ol", ["Splunk parses your search into a pipeline",
             "The <strong>base search</strong> &mdash; everything before the first "
             "pipe &mdash; selects events from the index",
             "Each subsequent command transforms the results it is handed",
             "The final command's output is what you see"]),
     ("note", "Only the base search touches the index. Everything after the first "
              "pipe works on results already in memory, which is why the base "
              "search decides how fast the whole thing runs.")],
    [("spl", 'index=web sourcetype=access_combined action=purchase status=200\n'
             '| stats count by product_name\n'
             '| sort - count'),
     ("ul", ["Line 1 is the base search &mdash; it reads the index",
             "Lines 2 and 3 never touch disk"])],
   ]},

  {"emoji": "&#9889;", "h": "Writing an Efficient Base Search", "cols": [
    [("h3", "Narrow in this order"),
     ("ol", ["<strong>Time</strong> &mdash; the single biggest filter",
             "<strong>Index</strong> &mdash; stops Splunk searching everything",
             "<strong>Sourcetype</strong> / host / source",
             "Field values and keywords"]),
     ("good", "Adding more terms to the base search makes it faster, not slower. "
              "This is the opposite of most query languages.")],
    [("h3", "Case sensitivity"),
     ("table", ["Part of the search", "Case sensitive?"], [
        ["Field <em>names</em>", "Yes"],
        ["Field <em>values</em>", "No"],
        ["Commands and keywords", "No"],
        ["Values in <code>where</code>", "Yes"],
        ["Values matched by a lookup", "Yes"]]),
     ("warn", "<code>productId</code> and <code>productid</code> are different "
              "fields. The first returns results; the second returns nothing.")],
   ]},

  {"emoji": "&#10033;", "h": "Wildcards and Why Position Matters", "body": [
    ("ul", ["Splunk indexes whole terms, so <code>statu*</code> cannot match a "
            "term the indexer never split that way",
            "<strong>Trailing</strong> wildcards use the index: "
            "<code>sourcetype=access_*</code> is cheap",
            "<strong>Leading</strong> wildcards do not: <code>*combined</code> "
            "forces a scan of every event in the time range"]),
    ("spl", '# efficient - the index can answer this\n'
            'index=security sourcetype=linux_secure user=admin*\n\n'
            '# expensive - every event in range must be read and tested\n'
            'index=security sourcetype=linux_secure user=*admin'),
    ("note", "An occasional leading wildcard in an ad hoc search is fine. One "
             "inside a saved report, a dashboard panel or a dataset constraint "
             "runs on a schedule forever.")]},

  {"emoji": "&#128266;", "h": "Search Modes", "body": [
    ("table", ["Mode", "Field discovery", "Use it when"], [
      ["<strong>Fast</strong>", "Only fields the search needs",
       "You know exactly what you are looking for"],
      ["<strong>Smart</strong>", "Varies by command &mdash; the default",
       "Almost always"],
      ["<strong>Verbose</strong>", "Every field it can find",
       "You are exploring and want to see what exists"]]),
    ("ul", ["Smart behaves like Verbose for event-listing searches and like Fast "
            "for transforming ones",
            "Verbose can be dramatically slower on a wide time range",
            "Mode changes what is <em>discovered</em>, never what is "
            "<em>returned</em> by a transforming command"]),
    ("note", "Switching to Verbose is the quickest way to see fields a "
             "<code>transaction</code> or <code>stats</code> added &mdash; you will "
             "use this in Module 6.")]},

  {"emoji": "&#128270;", "h": "The Job Inspector", "cols": [
    [("ul", ["<strong>Job &gt; Inspect Job</strong> on any completed search",
             "Shows how long each phase took and where the time went",
             "Works on a finished job even after you navigate away"]),
     ("h3", "The two numbers that matter"),
     ("table", ["Field", "Meaning"], [
        ["<code>scanCount</code>", "Events read from the index"],
        ["<code>resultCount</code>", "Events returned to you"]])],
    [("h3", "Reading the ratio"),
     ("ul", ["<code>scanCount</code> &asymp; <code>resultCount</code> &mdash; a tight, "
             "well-filtered search",
             "<code>scanCount</code> &gg; <code>resultCount</code> &mdash; Splunk read "
             "a great deal to give you very little; tighten the base search"]),
     ("warn", "Measure throughput as <code>scanCount / time</code>, not "
              "<code>resultCount / time</code>. The first tells you how hard "
              "Splunk worked; the second only tells you how much it found.")],
   ]},

  {"emoji": "&#128202;", "h": "Where the Time Goes", "body": [
    ("ul", ["<code>command.search.index</code> &mdash; locating events. High values "
            "point at a weak base search or too wide a time range",
            "<code>command.search.rawdata</code> &mdash; decompressing and reading "
            "events. High values point at a rare-term search",
            "<code>command.search.kv</code> &mdash; field extraction. High values "
            "point at expensive regexes or Verbose mode",
            "<code>dispatch.evaluate</code> &mdash; the commands after your first pipe"]),
    ("good", "Start with the phase that dominates, change one thing, and re-run. "
             "Optimising a phase that takes 2% of the time is wasted effort.")]},

  {"type": "lab", "lab": "Lab 2", "h": "Search Performance and the Job Inspector",
   "builds": [
     "Prove that field names are case sensitive and values are not",
     "Compare <code>scanCount</code> against <code>resultCount</code> for a loose and a tight search",
     "Time the same search in Fast, Smart and Verbose mode",
     "Find which phase dominates a slow search"],
   "kicker": "You will leave with a repeatable method for answering "
             "&ldquo;why is this search slow?&rdquo;"},
 ]},

# ---------------------------------------------------------------- Module 3
{
 "num": 3, "slug": "commands_for_visualizations", "color": "#1f7a4d",
 "title": "Commands for Visualizations",
 "slides": [
  {"emoji": "&#128260;", "h": "Streaming vs Transforming", "cols": [
    [("h3", "Streaming"),
     ("ul", ["Act on one event at a time",
             "Results stay as a list of events",
             "<code>eval</code>, <code>where</code>, <code>rex</code>, "
             "<code>fields</code>, <code>rename</code>"])],
    [("h3", "Transforming"),
     ("ul", ["Turn events into a <em>statistics table</em>",
             "Required before any visualization",
             "<code>stats</code>, <code>chart</code>, <code>timechart</code>, "
             "<code>top</code>, <code>rare</code>"]),
     ("note", "If the Visualization tab is greyed out, your search has no "
              "transforming command in it.")],
   ]},

  {"emoji": "&#127942;", "h": "top and rare", "body": [
    ("spl", f'{WEB} action=purchase status=200\n| top limit=5 product_name'),
    ("ul", ["Returns <code>count</code> and <code>percent</code> automatically",
            "<code>limit=0</code> returns every value",
            "<code>showperc=f</code> drops the percentage column",
            "<code>countfield</code> / <code>percentfield</code> rename the outputs",
            "<code>by</code> gives a separate top-N per group"]),
    ("spl", f'{WEB} action=purchase status=200\n'
            '| top limit=3 product_name by categoryId showperc=f'),
    ("note", "<code>rare</code> takes exactly the same options and answers the "
             "opposite question &mdash; often the more interesting one in security work.")]},

  {"emoji": "&#128200;", "h": "stats", "cols": [
    [("ul", ["The general-purpose aggregator",
             "One row per distinct <code>by</code> combination",
             "Multiple aggregations in one command",
             "<code>as</code> renames the output column"]),
     ("h3", "Common functions"),
     ("ul", ["<code>count</code>, <code>dc</code>, <code>sum</code>, <code>avg</code>",
             "<code>min</code>, <code>max</code>, <code>median</code>, <code>stdev</code>",
             "<code>values</code>, <code>list</code>, <code>range</code>"])],
    [("spl", f'{WEB} action=purchase status=200\n'
             '| stats count as orders,\n'
             '        dc(clientip) as customers,\n'
             '        sum(price) as revenue\n'
             '        by product_name\n'
             '| sort - revenue'),
     ("warn", "<code>stats</code> with no aggregation function is a syntax error. "
              "<code>| stats by clientip</code> will not run &mdash; you need "
              "<code>| stats count by clientip</code>.")],
   ]},

  {"emoji": "&#128203;", "h": "chart", "body": [
    ("ul", ["Produces a table with two dimensions: rows and columns",
            "<code>over</code> sets the rows (the X axis)",
            "<code>by</code> splits into columns (the series)",
            "With only <code>by</code> and no <code>over</code>, the "
            "<code>by</code> field becomes the X axis"]),
    ("spl", f'{SALES}\n'
            '| chart count over VendorCountry by product_name limit=5 useother=f'),
    ("table", ["Option", "Effect"], [
      ["<code>limit=N</code>", "Keep the top N series by column total"],
      ["<code>useother=f</code>", "Drop the OTHER series rather than lumping the rest in"],
      ["<code>usenull=f</code>", "Drop the NULL series for events missing the field"]]),
    ("note", "An OTHER column frequently dwarfs everything else and flattens the "
             "chart. <code>useother=f</code> is usually what you want once you "
             "have set a <code>limit</code>.")]},

  {"emoji": "&#128336;", "h": "timechart", "cols": [
    [("ul", ["<code>chart</code> with <code>_time</code> permanently on the X axis",
             "Buckets events automatically; <code>span</code> overrides it",
             "A <code>by</code> clause creates one series per value",
             "Only one <code>by</code> field is allowed"]),
     ("h3", "Default spans"),
     ("table", ["Range", "Span"], [
        ["Last 60 minutes", "1 minute"],
        ["Last 24 hours", "30 minutes"],
        ["Last 7 days", "1 day"]])],
    [("spl", f'{WEB}\n'
             '| timechart span=1h count by status usenull=f'),
     ("spl", f'{PROXY}\n'
             '| timechart span=1d sum(sc_bytes) as bytes by usage limit=5'),
     ("warn", "Too fine a span over too long a range produces thousands of "
              "buckets and a chart nobody can read. Let Splunk pick first, then "
              "adjust.")],
   ]},

  {"emoji": "&#127912;", "h": "From Table to Chart", "body": [
    ("ol", ["Run a search with a transforming command",
            "Click the <strong>Visualization</strong> tab",
            "Pick a chart type from the dropdown",
            "Click <strong>Format</strong> for axes, legend, stacking and colour"]),
    ("ul", ["<strong>Column</strong> / <strong>Bar</strong> &mdash; comparing categories",
            "<strong>Line</strong> / <strong>Area</strong> &mdash; change over time",
            "<strong>Pie</strong> &mdash; parts of one whole, and only when there are few parts",
            "<strong>Scatter</strong> &mdash; relationship between two measures"]),
    ("warn", "Formatting choices persist into your next search. If a chart "
             "appears stacked or trellised for no apparent reason, it is because "
             "you set that previously &mdash; clear it in Format.")]},

  {"emoji": "&#129517;", "h": "Trellis Layout", "body": [
    ("ul", ["Splits one chart into a small multiple per value of a field",
            "Available from the <strong>Trellis</strong> tab of the Visualization panel",
            "<strong>Independent</strong> scale lets each panel use its own Y axis; "
            "<strong>Shared</strong> keeps them comparable"]),
    ("spl", f'{PROXY}\n| timechart span=1h count by usage'),
    ("good", "Independent scaling reveals the shape of small series that a shared "
             "axis would flatten to a line at zero. Shared scaling is honest about "
             "magnitude. Pick deliberately &mdash; they tell different stories.")]},

  {"type": "lab", "lab": "Lab 3", "h": "Transforming Commands and Charts",
   "builds": [
     "Chart authentication outcomes by source address, stacked",
     "Build a five-product-by-country chart with <code>useother=f</code>",
     "Time-chart employee web usage and apply a Trellis layout",
     "Collect all three onto an <strong>IT Ops</strong> dashboard"],
   "kicker": "Every panel you build here gets reused in later labs."},
 ]},

# ---------------------------------------------------------------- Module 4
{
 "num": 4, "slug": "advanced_visualizations", "color": "#8a5a1a",
 "title": "Advanced Visualizations",
 "slides": [
  {"emoji": "&#128201;", "h": "trendline", "body": [
    ("ul", ["Adds a moving average alongside a time series",
            "Three types: <code>sma</code> simple, <code>ema</code> exponential, "
            "<code>wma</code> weighted",
            "Syntax is <code>type(period)</code> over a field, with the period "
            "between 2 and 10000"]),
    ("spl", f'{SEC} "Failed password"\n'
            '| timechart span=1d count as failures\n'
            '| trendline sma5(failures) as trend'),
    ("note", "The first <em>period &minus; 1</em> points have no trend value, because "
             "there is not yet enough history to average. That gap at the start of "
             "the line is correct, not a bug.")]},

  {"emoji": "&#49;&#65039;&#8419;", "h": "Single Value with Trend", "cols": [
    [("ul", ["Any search returning one number can be a single-value visualization",
             "Give it a time series and it will show the change against the "
             "previous period",
             "Configured entirely in <strong>Format</strong>"]),
     ("h3", "Options worth setting"),
     ("ul", ["<strong>Caption</strong> &mdash; what the number means",
             "<strong>Trend indicator</strong> &mdash; arrow and delta",
             "<strong>Sparkline</strong> &mdash; recent shape",
             "<strong>Colour by trend</strong> &mdash; green up, red down"])],
    [("spl", f'{SALES} categoryId="TENTS"\n'
             '| timechart span=1d count'),
     ("warn", "Colour by trend assumes up is good. For failed logins or error "
              "rates, invert it or you will paint a worsening problem green.")],
   ]},

  {"emoji": "&#127758;", "h": "iplocation", "body": [
    ("spl", f'{WEB} action=purchase status=200\n'
            '| iplocation clientip\n'
            '| stats count by Country'),
    ("ul", ["Adds <code>City</code>, <code>Region</code>, <code>Country</code>, "
            "<code>lat</code> and <code>lon</code>",
            "Uses a database bundled with Splunk &mdash; no network lookup",
            "<code>allfields=true</code> adds every available field",
            "<code>prefix=</code> namespaces the new fields to avoid collisions"]),
    ("note", "Private and reserved addresses resolve to nothing. Fill them in "
             "with <code>fillnull</code> or filter them out before you map, or "
             "they become an unlabelled bucket.")]},

  {"emoji": "&#128506;&#65039;", "h": "geostats and geom", "cols": [
    [("h3", "geostats &rarr; cluster map"),
     ("ul", ["Aggregates by latitude and longitude",
             "Clusters points, splitting them as you zoom",
             "Needs <code>lat</code> and <code>lon</code> &mdash; usually from "
             "<code>iplocation</code>"]),
     ("spl", f'{WEB} action=purchase\n'
             '| iplocation clientip\n'
             '| geostats count by Country')],
    [("h3", "geom &rarr; choropleth"),
     ("ul", ["Shades predefined regions by value",
             "Ships with <code>geo_us_states</code> and <code>geo_countries</code>",
             "<code>featureIdField</code> names the field holding the region"]),
     ("spl", f'{SALES} VendorCountry="United States"\n'
             '| chart count over VendorStateProvince\n'
             '| geom geo_us_states featureIdField=VendorStateProvince')],
   ]},

  {"emoji": "&#10753;", "h": "addtotals and addcoltotals", "body": [
    ("table", ["Command", "Adds", "Default"], [
      ["<code>addtotals</code>", "A <strong>column</strong> of row totals", "on"],
      ["<code>addcoltotals</code>", "A <strong>row</strong> of column totals", "&mdash;"],
      ["<code>addtotals col=t row=f</code>", "A totals row only", "&mdash;"]]),
    ("spl", f'{SALES}\n'
            '| chart count as "Units Sold" over VendorCountry\n'
            '| addtotals col=t row=f labelfield=VendorCountry label="Total"'),
    ("ul", ["<code>labelfield</code> says which column holds the label",
            "<code>label</code> sets the text",
            "Without <code>labelfield</code>, the totals row has no label and is "
            "easy to mistake for data"]),
    ("warn", "The totals row lands at the bottom of the <em>last page</em> of "
             "results. On a long table you have to page to it.")]},

  {"type": "lab", "lab": "Lab 4", "h": "Trendlines, Maps and Single Values",
   "builds": [
     "Time-chart authentication failures with a five-day moving average",
     "Turn a daily sales count into a single value with a trend indicator",
     "Shade US states by retail volume with <code>geom</code>",
     "Map online purchases by country with <code>iplocation</code> and <code>geostats</code>",
     "Add a labelled grand-total row to a table"],
   "kicker": "Five visualizations, five saved reports: L3S1 through L3S5."},
 ]},

# ---------------------------------------------------------------- Module 5
{
 "num": 5, "slug": "filtering_and_formatting_data", "color": "#7a2f8f",
 "title": "Filtering and Formatting Data",
 "slides": [
  {"emoji": "&#129518;", "h": "eval", "body": [
    ("ul", ["Calculates a value and writes it into a field",
            "If the field exists it is overwritten; if not it is created",
            "The new field lives only for the duration of the search",
            "Several assignments in one <code>eval</code>, separated by commas"]),
    ("spl", f'{WEB}\n'
            '| eval kb = round(bytes/1024, 2),\n'
            '       size_class = if(bytes > 3000, "large", "normal")'),
    ("note", "An <code>eval</code> that references a field which does not exist "
             "produces null rather than an error. A column full of blanks almost "
             "always means a misspelled field name.")]},

  {"emoji": "&#128290;", "h": "eval Functions Worth Knowing", "cols": [
    [("h3", "Numbers"),
     ("ul", ["<code>round(x, n)</code>, <code>floor</code>, <code>ceiling</code>",
             "<code>abs</code>, <code>sqrt</code>, <code>pow</code>",
             "<code>tonumber(str)</code>"]),
     ("h3", "Text"),
     ("ul", ["<code>tostring(x, \"commas\"|\"duration\"|\"hex\")</code>",
             "<code>upper</code>, <code>lower</code>, <code>trim</code>",
             "<code>substr(s, start, len)</code>, <code>len(s)</code>",
             "Concatenate with <code>.</code> or <code>+</code>"])],
    [("h3", "Branching"),
     ("spl", 'eval tier = case(\n'
             '    price >= 300, "premium",\n'
             '    price >= 100, "standard",\n'
             '    true(), "entry")'),
     ("ul", ["<code>case</code> stops at the first true condition",
             "<code>true()</code> as the last pair is the default",
             "With no default, unmatched rows get null"]),
     ("warn", "Quote the dollar sign when you build currency strings: "
              "<code>\"$\" + tostring(total,\"commas\")</code>. An unquoted "
              "<code>$</code> is a syntax error.")],
   ]},

  {"emoji": "&#128269;", "h": "search vs where", "body": [
    ("table", ["", "<code>search</code>", "<code>where</code>"], [
      ["Syntax", "Like the base search", "Expression language"],
      ["Field values", "Case <strong>insensitive</strong>", "Case <strong>sensitive</strong>"],
      ["Wildcards", "<code>*</code>", "<code>like()</code> with <code>%</code>"],
      ["Compare two fields", "No", "Yes"],
      ["Functions", "No", "Yes"]]),
    ("spl", '| search status=200 product_name="Cirrus*"\n\n'
            '| where sc_bytes > avg_bytes\n'
            '| where like(http_content_type, "image%")'),
    ("note", "Comparing one field against another is the thing only "
             "<code>where</code> can do, and it is usually the reason to reach for it.")]},

  {"emoji": "&#128683;", "h": "Keeping Results Clean", "cols": [
    [("h3", "fields"),
     ("ul", ["<code>| fields a b c</code> keeps only those",
             "<code>| fields - a</code> removes them",
             "Placed early, it also speeds the search up"]),
     ("h3", "fillnull"),
     ("ul", ["<code>| fillnull</code> writes <code>0</code>",
             "<code>| fillnull value=\"N/A\"</code> writes a string",
             "List fields at the end to restrict it"]),
     ("spl", '| fillnull value="N/A" discount refund')],
    [("h3", "rename"),
     ("ul", ["<code>| rename clientip as \"Customer IP\"</code>",
             "Quote anything containing a space",
             "Rename last &mdash; downstream commands need the original name"]),
     ("warn", "Option names are lower case. <code>value=</code> works; "
              "<code>VALUE=</code> does not. Use straight quotes, never the "
              "curly ones a word processor produces.")],
   ]},

  {"emoji": "&#128257;", "h": "foreach", "body": [
    ("ul", ["Runs the same expression over several fields",
            "<code>&lt;&lt;FIELD&gt;&gt;</code> stands in for each field name",
            "Wildcards select which fields to loop over"]),
    ("spl", f'{PROXY}\n'
            '| timechart span=1d sum(sc_bytes) by usage\n'
            '| foreach * [ eval <<FIELD>> = round(<<FIELD>>/1048576, 2) ]'),
    ("good", "This converts every series from bytes to megabytes without you "
             "having to know in advance what the series are called &mdash; which "
             "you cannot know, because they come from the data.")]},

  {"type": "lab", "lab": "Lab 5", "h": "Filtering Results and Manipulating Data",
   "builds": [
     "Convert daily traffic volume from bytes to megabytes and drop the raw column",
     "Calculate a GET-to-POST ratio per web server",
     "Find accounts with more than three failed logins in an hour",
     "Classify event sizes with <code>case</code> and chart them",
     "Challenge: group proxy traffic into graphic vs other with <code>like()</code>"],
   "kicker": "<code>eval</code> is the command you will use most for the rest of "
             "your Splunk career."},
 ]},

# ---------------------------------------------------------------- Module 6
{
 "num": 6, "slug": "correlating_events", "color": "#b03a2e",
 "title": "Correlating Events",
 "slides": [
  {"emoji": "&#128279;", "h": "Why Correlate", "body": [
    ("ul", ["A single event rarely tells a story &mdash; a <em>sequence</em> does",
            "One customer's visit is dozens of events sharing a session ID",
            "One intrusion attempt is many failed logins from one address",
            "Correlation groups related events so you can ask about the group"]),
    ("good", "The question changes from &ldquo;how many requests?&rdquo; to "
             "&ldquo;how many visits, how long did they last, and how many ended "
             "in a purchase?&rdquo;")]},

  {"emoji": "&#129309;", "h": "The transaction Command", "cols": [
    [("ul", ["Groups events sharing one or more field values",
             "Produces one result per group",
             "Adds <code>duration</code> and <code>eventcount</code>",
             "<code>_raw</code> of the group is every member concatenated"]),
     ("spl", f'{WEB}\n'
             '| transaction JSESSIONID\n'
             '| table JSESSIONID, clientip, action,\n'
             '        duration, eventcount')],
    [("h3", "Constraining the group"),
     ("table", ["Option", "Meaning"], [
        ["<code>maxspan</code>", "Longest the whole group may last"],
        ["<code>maxpause</code>", "Longest gap allowed between events"],
        ["<code>maxevents</code>", "Most events in one group"],
        ["<code>startswith</code>", "Event that opens a group"],
        ["<code>endswith</code>", "Event that closes a group"]]),
     ("note", "Without constraints, two unrelated visits that reuse a session ID "
              "weeks apart become one transaction lasting a fortnight.")],
   ]},

  {"emoji": "&#9201;&#65039;", "h": "A Realistic Transaction", "body": [
    ("spl", f'{WEB}\n'
            '| transaction JSESSIONID\n'
            '    startswith=(action="addtocart")\n'
            '    endswith=(action="purchase")\n'
            '    maxspan=30m maxpause=5m\n'
            '| eval minutes = round(duration/60, 1)\n'
            '| table JSESSIONID, clientip, minutes, eventcount'),
    ("ul", ["Only sessions that got from cart to checkout survive",
            "<code>maxspan</code> rules out an abandoned cart revisited later",
            "<code>maxpause</code> rules out a session left open over lunch"]),
    ("warn", "<code>search</code> after <code>transaction</code> filters the "
             "<em>groups</em>. Before it, you filter the events that are available "
             "to be grouped &mdash; and may remove the ones that would have joined "
             "them up.")]},

  {"emoji": "&#9878;&#65039;", "h": "transaction vs stats", "cols": [
    [("h3", "Use stats"),
     ("ul", ["Almost always &mdash; it is far faster",
             "You need counts, sums or distinct counts per group",
             "The grouping field is a simple value",
             "The data set is large"]),
     ("spl", f'{WEB}\n'
             '| stats range(_time) as duration,\n'
             '        count as events,\n'
             '        values(action) as actions\n'
             '        by JSESSIONID')],
    [("h3", "Use transaction"),
     ("ul", ["You need the events themselves, in order",
             "The group is defined by a start or end marker",
             "You need time-based constraints between events",
             "The same ID is reused and must be split by time"]),
     ("warn", "<code>transaction</code> is memory-bound and has a configured "
              "limit on group size. On a wide time range it will silently drop "
              "groups rather than fail.")],
   ]},

  {"type": "lab", "lab": "Lab 6", "h": "Correlating Events",
   "builds": [
     "Group store traffic into sessions by <code>JSESSIONID</code>",
     "Keep only the sessions containing a purchase",
     "Add <code>duration</code> and <code>eventcount</code>, and filter on session length",
     "Rebuild one of the same answers with <code>stats</code> and compare the run times"],
   "kicker": "The last step is the point: you will see for yourself why "
             "<code>stats</code> is the default answer."},
 ]},

# ---------------------------------------------------------------- Module 7
{
 "num": 7, "slug": "introduction_to_knowledge_objects", "color": "#2b6cb0",
 "title": "Introduction to Knowledge Objects",
 "slides": [
  {"emoji": "&#129504;", "h": "What Is a Knowledge Object?", "body": [
    ("ul", ["A saved piece of understanding about your data",
            "Created once, then reused by anyone with permission",
            "Applied at <strong>search time</strong>, so it affects future and past "
            "events alike",
            "Managed centrally, independently of the data itself"]),
    ("good", "This is the dividing line between using Splunk and administering "
             "knowledge in Splunk. Everything in Modules 8 to 13 is one of these.")]},

  {"emoji": "&#128218;", "h": "The Five Categories", "body": [
    ("table", ["Category", "Purpose", "Objects"], [
      ["<strong>Data interpretation</strong>", "Give raw text structure",
       "Field extractions, calculated fields"],
      ["<strong>Data classification</strong>", "Group events by meaning", "Event types"],
      ["<strong>Data enrichment</strong>", "Add outside context",
       "Lookups, workflow actions"],
      ["<strong>Normalization</strong>", "Make different sources agree",
       "Field aliases, tags"],
      ["<strong>Datasets</strong>", "Model data for non-searchers",
       "Data models, table datasets"]]),
    ("note", "When you meet a new object, ask which column it belongs in. It "
             "tells you what the object is <em>for</em>, which is usually the part "
             "people get wrong.")]},

  {"emoji": "&#127991;&#65039;", "h": "Naming Conventions", "cols": [
    [("ul", ["Objects accumulate quickly and are searched by name",
             "A convention makes a whole group findable with one filter",
             "Agree it before you have three hundred objects, not after"]),
     ("h3", "A workable pattern"),
     ("spl", '<Group>_<Type>_<Description>\n\n'
             'OPS_Report_WebServerErrors\n'
             'SEC_Alert_PrivilegedLoginFailure\n'
             'SALES_Lookup_VendorRegions')],
    [("h3", "In this course"),
     ("ul", ["Labs use short throwaway names such as <code>L2S1</code>",
             "That is deliberate &mdash; they are disposable",
             "Anything that outlives the lab gets a real name"]),
     ("warn", "A name is the only thing most people will ever see. "
              "<code>L6S1</code> is findable only by someone who already knows it "
              "exists, which defeats the purpose of sharing it.")],
   ]},

  {"emoji": "&#128274;", "h": "Permissions", "body": [
    ("table", ["Scope", "Who can see it", "Who can change it"], [
      ["<strong>Private</strong>", "The owner only", "Owner, admin"],
      ["<strong>This app only</strong>", "Roles you grant, within one app",
       "Owner and admin, plus roles you grant"],
      ["<strong>All apps</strong>", "Roles you grant, everywhere",
       "Owner and admin, plus roles you grant"]]),
    ("ul", ["New objects are <strong>Private</strong> by default",
            "Sharing to an app grants read to every listed role",
            "Only <strong>admin</strong> can promote an object to All apps"]),
    ("warn", "A privately scoped automatic lookup silently enriches nobody but "
             "its owner. Searches still run &mdash; they just come back missing the "
             "fields, which is far harder to diagnose than an error.")]},

  {"emoji": "&#9881;&#65039;", "h": "Managing Objects", "body": [
    ("ul", ["Everything under the <strong>KNOWLEDGE</strong> heading of the "
            "Settings menu is an object manager",
            "<strong>All configurations</strong> lists every object you can see, "
            "whoever owns it",
            "Filter by app, by owner, or by name",
            "Your role decides what you can edit"]),
    ("note", "Older material calls this &ldquo;Settings &gt; Knowledge&rdquo;. "
             "There is no menu item with that name &mdash; it is the column heading "
             "above the group of links.")]},

  {"type": "lab", "lab": "Lab 7", "h": "Working with Knowledge Objects",
   "builds": [
     "Inventory the objects that already exist, by app and by owner",
     "Save the same report under a throwaway name and a conventional one",
     "Change a report's scope and watch which roles gain access",
     "Find out why a privately scoped lookup breaks everyone else's searches"],
   "kicker": "No new SPL here. This lab is about the machinery everything else "
             "in the course sits on."},
 ]},

# ---------------------------------------------------------------- Module 8
{
 "num": 8, "slug": "creating_and_managing_fields", "color": "#0f766e",
 "title": "Creating and Managing Fields",
 "slides": [
  {"emoji": "&#129349;", "h": "What Splunk Extracts For You", "body": [
    ("ul", ["<strong>Index time</strong>: <code>host</code>, <code>source</code>, "
            "<code>sourcetype</code>, <code>_time</code>, <code>_raw</code>",
            "<strong>Search time</strong>: obvious <code>key=value</code> pairs, "
            "JSON and XML structure",
            "Pretrained sourcetypes such as <code>access_combined</code> carry "
            "their own extractions"]),
    ("spl", '# productId, action and JSESSIONID come free - they are\n'
            '# key=value pairs in the query string\n'
            'index=web sourcetype=access_combined productId=HV-TN-101'),
    ("note", "Check what you already have before writing a regex. A surprising "
             "amount of the work is done for you, and a hand-written extraction "
             "that duplicates a built-in one is a maintenance problem.")]},

  {"emoji": "&#128295;", "h": "The Field Extractor", "cols": [
    [("ul", ["A guided UI for building search-time extractions",
             "Reached from Settings, the Fields sidebar, or Event Actions",
             "Produces a reusable knowledge object, not a one-off"]),
     ("h3", "Two methods"),
     ("table", ["Method", "Use when"], [
        ["<strong>Regular expression</strong>", "Unstructured text, like a syslog line"],
        ["<strong>Delimiters</strong>", "Structured rows with no header"]])],
    [("h3", "The workflow"),
     ("ol", ["Pick a representative sample event",
             "Highlight the value you want and name the field",
             "Check the preview, including <strong>non-matches</strong>",
             "Add more sample events until the non-matches are genuinely irrelevant",
             "Validate, name the extraction, save"]),
     ("warn", "Non-matches are the step people skip. An extraction built from one "
              "event often matches only events shaped exactly like it.")],
   ]},

  {"emoji": "&#128221;", "h": "Extraction by Regular Expression", "body": [
    ("spl", '# what the field extractor generates, roughly\n'
            'Failed password for (?<user>\\w+) from (?<src>\\d+\\.\\d+\\.\\d+\\.\\d+) '
            'port (?<port>\\d+)'),
    ("ul", ["<code>(?&lt;name&gt;...)</code> is a named capture group &mdash; the "
            "name becomes the field",
            "Splunk writes it for you from your highlighted examples",
            "You can edit the generated expression directly",
            "Two fields at once sometimes fails &mdash; build them separately"]),
    ("good", "Test with <code>rex</code> in a search before you save an "
             "extraction. It is the same engine, and the feedback loop is seconds "
             "instead of minutes.")]},

  {"emoji": "&#9986;", "h": "Extraction by Delimiter", "body": [
    ("spl", '2026-10-14T09:12:44,203.0.113.44,2.0.0-beta1,route_saved,'
            'user:ana.cho@example.test DeviceName:Wayfarer-21 action:completed role:Guide'),
    ("ul", ["Choose the delimiter &mdash; comma, tab, pipe, space or custom",
            "Splunk names the fields <code>field1</code>, <code>field2</code>, and so on",
            "Rename each one to something meaningful before saving",
            "Fields inside a segment still need a regex pass"]),
    ("note", "This record needs both methods: delimiters for the first four "
             "comma-separated values, then a regex for the "
             "<code>key:value</code> pairs in the last one. That is exactly what "
             "Lab 8 walks through.")]},

  {"emoji": "&#128736;&#65039;", "h": "Managing Extractions", "body": [
    ("ul", ["<strong>Settings &gt; Fields &gt; Field extractions</strong> lists them all",
            "<strong>Field transformations</strong> holds the underlying regex",
            "Permissions work exactly as in Module 7",
            "Delete an extraction and the field disappears from every search that "
            "used it"]),
    ("warn", "Knowledge objects can take a minute to become available after you "
             "save them, particularly in a clustered environment. If a brand-new "
             "field returns nothing, wait and re-run before you start debugging.")]},

  {"type": "lab", "lab": "Lab 8", "h": "Creating and Managing Fields",
   "builds": [
     "Extract source address and port from authentication logs with a regex",
     "Remove a bogus value during the validate step",
     "Extract the beta telemetry's leading columns with delimiters",
     "Extract <code>user</code>, <code>DeviceName</code>, <code>action</code> and "
     "<code>role</code> from the trailing segment with a regex",
     "Check non-matches and add sample events until coverage is right"],
   "kicker": "Two extraction methods against the same record, which is how real "
             "log formats usually arrive."},
 ]},

# ---------------------------------------------------------------- Module 9
{
 "num": 9, "slug": "field_aliases_and_calculated_fields", "color": "#9a3412",
 "title": "Creating Field Aliases and Calculated Fields",
 "slides": [
  {"emoji": "&#128279;", "h": "The Problem", "body": [
    ("table", ["Source", "The user field is called"], [
      ["<code>access_combined</code>", "<code>user</code>"],
      ["<code>web_proxy</code>", "<code>cs_username</code>"],
      ["<code>firewall</code>", "<code>Username</code>"],
      ["<code>linux_secure</code>", "<code>user</code>"]]),
    ("spl", '# this cannot work across all four sourcetypes\n'
            'index=* user=acho | stats count by sourcetype'),
    ("ul", ["Three different names for the same real-world thing",
            "Every cross-source search has to know all three",
            "Add a fourth data source and every search needs editing"])]},

  {"emoji": "&#127991;&#65039;", "h": "Field Aliases", "body": [
    ("ul", ["Give an existing field a second name",
            "The original keeps working &mdash; an alias adds, it does not rename",
            "Scoped to a sourcetype, source or host",
            "<strong>Settings &gt; Fields &gt; Field aliases</strong>"]),
    ("table", ["Setting", "Value"], [
      ["Apply to", "sourcetype"],
      ["Named", "<code>web_proxy</code>"],
      ["Field alias", "<code>cs_username</code> = <code>user</code>"]]),
    ("good", "Alias the three username fields to <code>user</code> and "
             "<code>index=* user=acho</code> starts working everywhere at once, "
             "with no change to any existing search.")]},

  {"emoji": "&#8505;&#65039;", "h": "When Aliases Are Applied", "body": [
    ("ol", ["Index-time fields and defaults",
            "Field extractions",
            "<strong>Field aliases</strong>",
            "Calculated fields",
            "Lookups",
            "Event types, then tags"]),
    ("ul", ["An alias can only point at something that already exists by step 3",
            "A calculated field <em>can</em> reference an alias &mdash; it runs later",
            "An alias <em>cannot</em> reference a calculated field"]),
    ("warn", "This ordering explains most &ldquo;my alias returns nothing&rdquo; "
             "problems. If the source field comes from a lookup, the alias has "
             "already run by the time it exists.")]},

  {"emoji": "&#129518;", "h": "Calculated Fields", "cols": [
    [("ul", ["A saved <code>eval</code> that runs automatically",
             "The field appears as though it were extracted",
             "Scoped to a sourcetype, source or host",
             "<strong>Settings &gt; Fields &gt; Calculated fields</strong>"]),
     ("table", ["Setting", "Value"], [
        ["Apply to", "sourcetype"],
        ["Named", "<code>web_proxy</code>"],
        ["Name", "<code>sc_megabytes</code>"],
        ["Eval expression", "<code>sc_bytes/1024/1024</code>"]])],
    [("h3", "Why bother"),
     ("ul", ["The conversion is written once, correctly",
             "Nobody divides by 1000 by mistake",
             "It is available in Pivot and data models",
             "Changing the definition fixes every search at once"]),
     ("spl", f'{PROXY}\n'
             '| stats sum(sc_megabytes) as MB by user\n'
             '| sort - MB')],
   ]},

  {"type": "lab", "lab": "Lab 9", "h": "Field Aliases and Calculated Fields",
   "builds": [
     "Alias <code>cs_username</code> and <code>Username</code> to <code>user</code>",
     "Prove a single search now spans both network sourcetypes",
     "Create a <code>sc_megabytes</code> calculated field from <code>sc_bytes</code>",
     "Report bandwidth by user in megabytes",
     "Supplemental: alias the store's <code>action</code> and <code>method</code> fields"],
   "kicker": "Normalization is unglamorous and it is what makes every later "
             "correlation possible."},
 ]},

# ---------------------------------------------------------------- Module 10
{
 "num": 10, "slug": "tags_and_event_types", "color": "#6b21a8",
 "title": "Creating Tags and Event Types",
 "slides": [
  {"emoji": "&#127991;&#65039;", "h": "Tags", "body": [
    ("ul", ["A label attached to a specific <code>field=value</code> pair",
            "One value can carry several tags; one tag can cover many values",
            "Searched with <code>tag=name</code> or <code>tag::field=name</code>"]),
    ("spl", '# instead of listing every privileged account by hand\n'
            'index=security (user=admin OR user=administrator OR user=sysadmin\n'
            '                OR user=itmadmin OR user=sapadmin)\n\n'
            '# tag each value once, then\n'
            'index=security tag=privileged'),
    ("note", "Create the first tag from an event's field Actions menu, then add "
             "the remaining values under Settings &gt; Tags &gt; List by tag name. "
             "It is far quicker than tagging one event at a time.")]},

  {"emoji": "&#128204;", "h": "Event Types", "body": [
    ("ul", ["A saved search condition, given a name",
            "Applied automatically to any event matching it",
            "Appears as the <code>eventtype</code> field",
            "Cannot contain a pipe or a subsearch &mdash; conditions only"]),
    ("spl", '# saved as the event type "web_error"\n'
            'index=web sourcetype=access_combined status>=500\n\n'
            '# then, anywhere\n'
            'eventtype=web_error | stats count by host, status'),
    ("warn", "Because an event type is only a condition, it cannot aggregate. "
             "<code>| stats count</code> belongs in the search that <em>uses</em> "
             "the event type, not in its definition.")]},

  {"emoji": "&#9878;&#65039;", "h": "Tags vs Event Types", "cols": [
    [("h3", "Tag"),
     ("ul", ["Labels a <strong>field value</strong>",
             "Normalization",
             "&ldquo;This account is privileged&rdquo;",
             "Many values &rarr; one label"])],
    [("h3", "Event type"),
     ("ul", ["Labels a <strong>whole event</strong>",
             "Classification",
             "&ldquo;This event is a web error&rdquo;",
             "One condition &rarr; many events"]),
     ("good", "They compose. Tag the event type itself and you can search a whole "
              "family of conditions by one name &mdash; which is exactly how the "
              "CIM works in Module 14.")],
   ]},

  {"emoji": "&#128290;", "h": "Priority and Scope", "body": [
    ("ul", ["Event types have a priority from 1 (highest) to 10",
            "When several match one event, priority decides the order they are "
            "listed in",
            "Priority does not exclude anything &mdash; every match still applies",
            "Permissions work as in Module 7"]),
    ("note", "An event can legitimately carry several event types at once. "
             "<code>eventtype</code> is multi-valued, so "
             "<code>| stats count by eventtype</code> counts each of them.")]},

  {"type": "lab", "lab": "Lab 10", "h": "Creating Tags and Event Types",
   "builds": [
     "Find every variation of the admin account in the security index",
     "Tag all five as <code>privileged</code>",
     "Search by tag instead of by a five-way OR",
     "Create a <code>web_error</code> event type for server errors",
     "Count how many sourcetypes the event type reaches"],
   "kicker": "Both objects exist to stop people retyping the same long search."},
 ]},

# ---------------------------------------------------------------- Module 11
{
 "num": 11, "slug": "macros", "color": "#065f46",
 "title": "Creating and Using Macros",
 "slides": [
  {"emoji": "&#128302;", "h": "Search Macros", "body": [
    ("ul", ["A named, reusable fragment of SPL",
            "Can be a whole search, or a single command in the middle of one",
            "Invoked between <strong>backticks</strong>",
            "<strong>Settings &gt; Advanced search &gt; Search macros</strong>"]),
    ("spl", "`europe_sales`\n\n"
            "index=sales sourcetype=vendor_sales `to_currency(euro,€,0.92)`"),
    ("warn", "A backtick <code>`</code> is not an apostrophe <code>'</code>. This "
             "is the single most common macro mistake, and the error message does "
             "not point at it.")]},

  {"emoji": "&#128221;", "h": "A Basic Macro", "cols": [
    [("h3", "The search"),
     ("spl", f'{SALES}\n'
             '  VendorCountry IN ("Germany","France","Italy")\n'
             '| stats sum(price) as USD by product_name\n'
             '| eval USD = "$" + tostring(USD, "commas")')],
    [("h3", "Saved as a macro"),
     ("ol", ["Name: <code>europe_sales</code>",
             "Definition: the search above",
             "Destination app: <code>splunk_intadv</code>",
             "Save, then call it as <code>`europe_sales`</code>"]),
     ("note", "A macro is pure text substitution. Splunk pastes the definition in "
              "and then parses the result, so a macro can end mid-pipeline and the "
              "caller can carry on piping.")],
   ]},

  {"emoji": "&#128256;", "h": "Macros with Arguments", "body": [
    ("ul", ["Declare the count in the name: <code>to_currency(3)</code>",
            "List argument names, comma separated, in the Arguments field",
            "Reference them in the definition as <code>$name$</code>",
            "Order of the call must match the order declared"]),
    ("spl", '# definition of to_currency(3), arguments: currency,symbol,rate\n'
            '| stats sum(price) as USD by product_name\n'
            '| eval $currency$ = "$symbol$" . tostring(round(USD*$rate$, 2), "commas"),\n'
            '       USD = "$" + tostring(USD, "commas")'),
    ("spl", '# the call\n'
            'index=sales sourcetype=vendor_sales `to_currency(euro,€,0.92)`')]},

  {"emoji": "&#9989;", "h": "Validating Arguments", "body": [
    ("ul", ["<strong>Validation expression</strong> &mdash; an eval returning "
            "true or false",
            "<strong>Validation error message</strong> &mdash; what the user sees "
            "when it fails",
            "Runs before the macro expands, so bad input fails clearly"]),
    ("spl", '# validation expression\n'
            'isnum($rate$)\n\n'
            '# error message\n'
            'to_currency expects a numeric rate, as in `to_currency(euro,€,0.92)`'),
    ("good", "Without validation, passing a non-numeric rate produces an "
             "incomprehensible parse error from somewhere deep inside the expanded "
             "search. With it, the user is told exactly what they did wrong.")]},

  {"type": "lab", "lab": "Lab 11", "h": "Creating and Using Macros",
   "builds": [
     "Build a basic macro for European retail sales",
     "Call it with backticks and confirm the output",
     "Build a three-argument currency conversion macro",
     "Call it for euros and again for pounds",
     "Add a validation expression and watch a bad argument fail cleanly"],
   "kicker": "Macros are how a useful search stops being something only you can "
             "write."},
 ]},

# ---------------------------------------------------------------- Module 12
{
 "num": 12, "slug": "workflow_actions", "color": "#1e40af",
 "title": "Creating and Using Workflow Actions",
 "slides": [
  {"emoji": "&#128279;", "h": "Workflow Actions", "body": [
    ("ul", ["Add a menu item to events and field values",
            "Carry field values from the event into a URL or another search",
            "Scoped to named fields, event types, or both",
            "<strong>Settings &gt; Fields &gt; Workflow actions</strong>"]),
    ("table", ["Type", "What it does"], [
      ["<strong>link (GET)</strong>", "Opens a URL with values in the query string"],
      ["<strong>link (POST)</strong>", "Submits values as a form post"],
      ["<strong>search</strong>", "Runs another SPL search"]]),
    ("note", "This is the bridge out of Splunk &mdash; to a ticketing system, an "
             "asset database, or a reputation service &mdash; without leaving the "
             "event you are looking at.")]},

  {"emoji": "&#127760;", "h": "GET Actions", "cols": [
    [("ol", ["Name: <code>lookup_src_ip</code>",
             "Label: <code>Look up IP: $src_ip$</code>",
             "Apply to field: <code>src_ip</code>",
             "Action type: <strong>link</strong>",
             "URI with <code>$src_ip$</code> embedded",
             "Link method: <strong>get</strong>"])],
    [("spl", 'http://127.0.0.1:8888/whois?ip=$src_ip$'),
     ("ul", ["<code>$field$</code> is substituted from the clicked event",
             "The Label uses the same syntax, so the menu item names the value",
             "Opens in a new window or the same one"]),
     ("note", "Link actions open in the <em>student's</em> browser, not inside "
              "Splunk. A <code>127.0.0.1</code> target therefore means the "
              "student's own machine, even when Splunk runs in a container.")],
   ]},

  {"emoji": "&#128228;", "h": "POST Actions", "body": [
    ("ul", ["Same object, with <strong>Link method: post</strong>",
            "A <strong>Post arguments</strong> section appears &mdash; it is hidden "
            "for GET, because a GET has no body",
            "Each argument is a key and a value; the value may be literal or "
            "<code>$field$</code>"]),
    ("table", ["Key", "Value", "Sends"], [
      ["<code>src_ip</code>", "<code>$src_ip$</code>", "the event's address"],
      ["<code>user</code>", "<code>$user$</code>", "the event's user, or empty"],
      ["<code>reported_by</code>", "<code>splunk_class</code>", "a constant"]]),
    ("warn", "An unmatched <code>$field$</code> posts as empty rather than "
             "failing. Build an action against a field that is only sometimes "
             "present and you will get silent blanks.")]},

  {"emoji": "&#128269;", "h": "Search Actions", "body": [
    ("ul", ["Runs SPL instead of opening a URL",
            "The search string may embed <code>$field$</code>",
            "Choose the app to run in and whether to reuse the time range"]),
    ("spl", 'index=security sourcetype=linux_secure "Failed password" src_ip=$src_ip$'),
    ("good", "A search action never leaves Splunk, so it is the one workflow "
             "action type that works with no network whatsoever.")]},

  {"emoji": "&#127919;", "h": "Scoping", "body": [
    ("ul", ["<strong>Apply only to the following fields</strong> &mdash; the action "
            "appears only where those fields exist",
            "<strong>Apply only to the following event types</strong> &mdash; narrower still",
            "Leave both blank and it appears on everything, which gets noisy fast",
            "<strong>Show action in</strong>: the event menu, the field menu, or both"]),
    ("note", "Scoping is a usability decision. An action offered on every event "
             "in every search is an action people learn to ignore.")]},

  {"type": "lab", "lab": "Lab 12", "h": "Creating and Using Workflow Actions",
   "builds": [
     "Build a GET action that looks up a source address",
     "Build a POST action that submits the address and user to a reporting endpoint",
     "Build a search action that finds every failed login from that address",
     "Scope each one so it appears only where it makes sense"],
   "kicker": "All three targets run locally, so the lab works with no internet "
             "access at all."},
 ]},

# ---------------------------------------------------------------- Module 13
{
 "num": 13, "slug": "data_models", "color": "#92400e",
 "title": "Creating Data Models",
 "slides": [
  {"emoji": "&#127959;&#65039;", "h": "What a Data Model Is", "body": [
    ("ul", ["A hierarchy of datasets describing your data in business terms",
            "Lets people answer questions through <strong>Pivot</strong>, without "
            "writing SPL",
            "Built by someone who knows the data; used by everyone else",
            "Can be <strong>accelerated</strong> for very fast reporting"]),
    ("good", "This is the payoff for Modules 8 to 12. A data model is where "
             "extractions, aliases, calculated fields and lookups are assembled "
             "into something a non-specialist can use.")]},

  {"emoji": "&#127795;", "h": "Datasets", "cols": [
    [("h3", "Root datasets"),
     ("table", ["Type", "Based on"], [
        ["<strong>Event</strong>", "A constraint &mdash; the common case"],
        ["<strong>Search</strong>", "An arbitrary search, transforming included"],
        ["<strong>Transaction</strong>", "A transaction over other datasets"]])],
    [("h3", "Child datasets"),
     ("ul", ["Inherit every field and constraint from the parent",
             "Add further constraints to narrow the set",
             "Nest as deeply as the data warrants"]),
     ("note", "Children narrow, never widen. If a child needs events the parent "
              "excludes, the hierarchy is wrong.")],
   ]},

  {"emoji": "&#128204;", "h": "Constraints", "body": [
    ("spl", '# root event: Web requests\n'
            'index=web sourcetype=access_combined\n\n'
            '# child: Successful requests\n'
            'status<400\n\n'
            '# grandchild: Purchases\n'
            'action=purchase productId=*'),
    ("ul", ["A child's constraint is <em>added</em> to its parent's",
            "Preview before saving &mdash; an over-narrow constraint returns nothing",
            "Constraints are plain search syntax, no pipes"])]},

  {"emoji": "&#129521;", "h": "Adding Fields", "body": [
    ("table", ["Type", "Source", "Use for"], [
      ["<strong>Auto-extracted</strong>", "Fields already present",
       "Renaming for Pivot users"],
      ["<strong>Eval expression</strong>", "A calculation", "Derived values"],
      ["<strong>Lookup</strong>", "A lookup table", "External enrichment"],
      ["<strong>Regular expression</strong>", "A regex on <code>_raw</code>",
       "Anything not yet extracted"],
      ["<strong>Geo IP</strong>", "<code>iplocation</code>", "Mapping"]]),
    ("spl", '# eval field: a readable day label\n'
            'strftime(_time, "%m-%d %A")'),
    ("warn", "Field names in a model are case sensitive and must match the data "
             "exactly. <code>date_mday</code> exists; <code>date-mday</code> does "
             "not.")]},

  {"emoji": "&#128202;", "h": "Pivot and Acceleration", "cols": [
    [("h3", "Pivot"),
     ("ul", ["Pick a dataset, then split rows and columns",
             "Generates the SPL for you &mdash; inspect it to learn",
             "Save the result as a report or dashboard panel"])],
    [("h3", "Acceleration"),
     ("ul", ["Builds a summary alongside the index",
             "Queries become dramatically faster",
             "Only root <em>event</em> and <em>search</em> datasets can be accelerated",
             "Costs disk, and the summary needs time to build"]),
     ("note", "Accelerate a model people use daily. Do not accelerate one you "
              "built to answer a single question.")],
   ]},

  {"type": "lab", "lab": "Lab 13", "h": "Creating Data Models",
   "builds": [
     "Create a model with a root event dataset for store traffic",
     "Add auto-extracted fields, renamed for people who do not know the data",
     "Add child datasets for successful and failed requests",
     "Add an eval field and a lookup-based field",
     "Verify the whole thing through Pivot and save a dashboard"],
   "kicker": "The longest lab in the course, and the one that ties the rest "
             "together."},
 ]},

# ---------------------------------------------------------------- Module 14
{
 "num": 14, "slug": "common_information_model", "color": "#374151",
 "title": "Using the Common Information Model",
 "slides": [
  {"emoji": "&#128207;", "h": "What the CIM Is", "body": [
    ("ul", ["A shared vocabulary of field names and event tags",
            "A <em>convention</em>, not a product that transforms your data",
            "Splunk publishes it as a Splunkbase add-on of ready-made data "
            "models; the convention is the part that matters, and you can "
            "follow it without installing anything",
            "The least common denominator for a domain, not an exhaustive schema"]),
    ("good", "Module 9 solved this problem for four of your own sourcetypes. The "
             "CIM solves it for the whole industry, so an app written by someone "
             "else can search your data without knowing your field names.")]},

  {"emoji": "&#128221;", "h": "Normalized Field Names", "cols": [
    [("h3", "Authentication"),
     ("table", ["Field", "Meaning"], [
        ["<code>action</code>", "success, failure"],
        ["<code>app</code>", "Application the auth ran against"],
        ["<code>src</code>", "Where it came from"],
        ["<code>dest</code>", "What it targeted"],
        ["<code>user</code>", "Account used"]])],
    [("h3", "Web"),
     ("table", ["Field", "Meaning"], [
        ["<code>action</code>", "What the server did"],
        ["<code>http_method</code>", "GET, POST, PUT"],
        ["<code>status</code>", "Response code"],
        ["<code>src</code>", "Requesting client"],
        ["<code>duration</code>", "Elapsed milliseconds"]]),
     ("note", "<code>src</code> may be aliased from <code>src_ip</code>, "
              "<code>src_host</code> or <code>src_name</code> &mdash; exactly the "
              "technique from Module 9.")],
   ]},

  {"emoji": "&#129513;", "h": "Making Your Data CIM-Compliant", "body": [
    ("ol", ["Pick the model that matches your source &mdash; Web, "
            "Authentication, Network Traffic",
            "Alias your field names to the model's names (Module 9)",
            "Tag your events with the model's required tags (Module 10)",
            "Confirm with the model's own validation search"]),
    ("spl", '# our store logs, mapped onto CIM Web field names\n'
            '#   clientip -> src     method -> http_method     uri_path -> url\n'
            '| datamodel Harborview_Web Web search\n'
            '| stats count by Web.src, Web.http_method, Web.status'),
    ("good", "This course ships two models already mapped this way, "
             "<code>Harborview_Web</code> and "
             "<code>Harborview_Authentication</code>, so every example here "
             "runs on the class instance with nothing to download."),
    ("note", "Compliance is just aliases, eval fields and tags. There is no "
             "separate mechanism to learn &mdash; which is why the CIM comes last.")]},

  {"emoji": "&#128269;", "h": "The datamodel Command", "body": [
    ("spl", '# describe every model available to you\n| datamodel\n\n'
            '# describe one\n| datamodel Harborview_Web\n\n'
            '# search a dataset\n'
            '| datamodel Harborview_Web Web search | fields Web.*'),
    ("ul", ["A <strong>generating</strong> command &mdash; it must come first",
            "Field names are prefixed with the dataset name",
            "<code>search</code> as the third argument returns the events"]),
    ("note", "<code>| datamodel</code> lists only models this Splunk instance "
             "actually has. On a production system with the CIM add-on you "
             "would see its twenty-odd models here too; the command is the "
             "same either way.")]},

  {"emoji": "&#9889;", "h": "tstats", "body": [
    ("spl", '| tstats count from datamodel=Harborview_Web\n'
            '  where Web.status>=400 by Web.src, Web.status'),
    ("ul", ["Reads the model's summary rather than raw events",
            "Orders of magnitude faster on large data",
            "Works on an unaccelerated model too &mdash; it simply falls back to "
            "the events, which is what happens on the class instance",
            "<code>prestats=t</code> chains it into <code>chart</code> or "
            "<code>timechart</code>"]),
    ("good", "An accelerated model plus <code>tstats</code> is how dashboards over "
             "months of data stay responsive. It is the single biggest performance "
             "lever in this course.")]},

  {"emoji": "&#127937;", "h": "End of the Intermediate Syllabus", "body": [
    ("good", "You can now build every search-time knowledge object Splunk "
             "offers, assemble them into a data model, normalise your data "
             "onto a shared vocabulary, and explain why one search is faster "
             "than another."),
    ("h3", "The advanced block, Modules 15 and 16"),
    ("table", ["Module", "Covers"], [
      ["15 &mdash; Subsearches", "Filtering by a list that is itself a search"],
      ["16 &mdash; Combining Datasets", "<code>join</code>, <code>append</code>, <code>union</code>, and why <code>stats</code> usually wins"]]),
    ("ul", ["Beyond this course: users and roles, system administration, "
            "alerting, Dashboard Studio, summary indexing, and clustering"])]},
 ]},


# ---------------------------------------------------------------- Module 15
{
 "num": 15, "slug": "subsearches", "color": "#0e7490",
 "title": "Subsearches",
 "slides": [
  {"emoji": "&#128269;", "h": "What a Subsearch Is", "body": [
    ("ul", ["A search inside square brackets that runs <strong>first</strong>",
            "Its results are turned into search terms and spliced into the "
            "outer search",
            "Use it when the filter you need is itself the answer to a search",
            "The inner search carries its own <code>search</code> keyword"]),
    ("spl", f'{WEB} action=purchase status=200\n'
            '    [search index=web sourcetype=access_combined status>=500\n'
            '     | fields clientip\n'
            '     | dedup clientip]'),
    ("good", "Read the rewritten search in the Job Inspector once and the "
             "whole command makes sense: the brackets are gone, replaced by a "
             "long <code>OR</code> expression of the values the inner search "
             "returned.")]},

  {"emoji": "&#9986;", "h": "Keeping the Generated Terms Small", "cols": [
    [("h3", "Always"),
     ("ul", ["<code>fields</code> &mdash; otherwise every field on the inner "
             "events becomes part of the expression",
             "<code>dedup</code> &mdash; otherwise a value repeats once per "
             "matching event",
             "<code>head</code> &mdash; a hard ceiling you chose, rather than "
             "the one Splunk imposes"])],
    [("h3", "The limits"),
     ("table", ["Limit", "Default"], [
        ["Results returned", "10,000"],
        ["Time to run", "60 seconds"],
        ["Nesting depth", "keep to 2"]]),
     ("warn", "Hit either limit and the subsearch does not fail. It returns "
              "what it has and the outer search runs against a truncated "
              "list, so the answer is quietly incomplete rather than wrong in "
              "any visible way.")],
   ]},

  {"emoji": "&#10060;", "h": "Exclusion with NOT", "body": [
    ("spl", f'{SEC} vendor_action=Failed\n'
            '    NOT [search index=security sourcetype=linux_secure\n'
            '                vendor_action=Accepted\n'
            '         | fields user\n'
            '         | dedup user]'),
    ("ul", ["&ldquo;Everything in A that is not also in B&rdquo;",
            "There is no other concise way to express it in SPL",
            "On this data it finds the accounts that have never once "
            "succeeded"]),
    ("note", "That result set is the five privileged accounts from Module 10, "
             "arrived at from the opposite direction. Discovering a pattern "
             "this way and then encoding it as a tag is a good habit.")]},

  {"emoji": "&#9878;&#65039;", "h": "Subsearch, Lookup or stats?", "body": [
    ("table", ["Need", "Reach for"], [
      ["Filter by a small, changing list", "<strong>Subsearch</strong>"],
      ["Add context to every event", "<strong>Lookup</strong>"],
      ["Correlate two sources field by field", "<strong>stats</strong> by the shared field"],
      ["Filter by tens of thousands of values", "<strong>Lookup</strong>, or <code>inputlookup</code> in the subsearch"]]),
    ("good", "A subsearch is for discovery &mdash; working out what the list "
             "even is. Once you know, encode it as a lookup or a tag so you "
             "are not re-deriving it on every run.")]},

  {"type": "lab", "lab": "Lab 14", "h": "Subsearches",
   "builds": [
     "Filter purchases by a client list you cannot write by hand",
     "Find accounts that have only ever failed, with <code>NOT</code>",
     "Compare <code>return</code> against <code>fields</code> in the generated terms",
     "Watch a subsearch hit its 10,000-row ceiling without telling you"],
   "kicker": "The last task is the one worth remembering: the failure mode is "
             "a plausible wrong answer."},
 ]},

# ---------------------------------------------------------------- Module 16
{
 "num": 16, "slug": "combining_datasets", "color": "#7c2d12",
 "title": "Combining Datasets",
 "slides": [
  {"emoji": "&#128279;", "h": "Four Ways to Bring Two Sources Together", "body": [
    ("table", ["Command", "What it does"], [
      ["<code>join</code>", "Matches rows side by side on a shared field"],
      ["<code>append</code>", "Puts one result set underneath another, in sequence"],
      ["<code>union</code>", "The same, run in parallel, as a generating command"],
      ["<code>stats</code>", "Aggregates both sources at once by the shared field"]]),
    ("good", "Three of these are the obvious answer and the fourth is usually "
             "the right one. Module 16 is mostly about why.")]},

  {"emoji": "&#129309;", "h": "join", "cols": [
    [("spl", f'{WEB} action=purchase\n'
             '| join productId\n'
             '    [search index=sales sourcetype=sales_entries\n'
             '     | stats sum(total) as revenue by productId]'),
     ("ul", ["The field must have the same name on both sides",
             "<code>rename</code> inside the subsearch when it does not"])],
    [("h3", "Join types"),
     ("table", ["Type", "Keeps"], [
        ["default (inner)", "Only rows matching on both sides"],
        ["<code>type=left</code>", "Every left-hand row, matched or not"]]),
     ("warn", "An inner join silently deletes the unmatched rows &mdash; which "
              "are often the interesting ones. On this data it removes exactly "
              "the privileged accounts security cares about.")],
   ]},

  {"emoji": "&#11015;&#65039;", "h": "append and union", "body": [
    ("spl", '# stack one result set under another\n'
            f'{WEB} status>=500\n'
            '| stats count as errors by host\n'
            '| append\n'
            '    [search index=network sourcetype=web_proxy sc_http_status>=500\n'
            '     | rename s_hostname as host\n'
            '     | stats count as errors by host]'),
    ("spl", '# the same, as a generating command, both sides in parallel\n'
            '| union\n'
            f'    [search {WEB} status>=500 | stats count by sourcetype]\n'
            '    [search index=network sourcetype=web_proxy sc_http_status>=500\n'
            '     | stats count by sourcetype]'),
    ("note", "Normalise the field names in the appended search, or you get two "
             "half-empty columns instead of one full one.")]},

  {"emoji": "&#9989;", "h": "Why stats Usually Wins", "cols": [
    [("spl", f'{WEB} action=purchase\n'
             '    OR index=sales sourcetype=sales_entries\n'
             '| stats count(eval(sourcetype=="access_combined"))\n'
             '          as checkouts,\n'
             '        sum(total) as revenue\n'
             '        by productId')],
    [("ul", ["Same answer as the <code>join</code>",
             "Streams, so no 10,000-row ceiling and no silent truncation",
             "One pass over the data instead of two",
             "Scales to data volumes where <code>join</code> stops being "
             "correct, not just slow"]),
     ("note", "<code>join</code> reads more naturally if you come from SQL, "
              "and that familiarity is most of why it gets used where "
              "<code>stats</code> would be safer.")],
   ]},

  {"type": "lab", "lab": "Lab 15", "h": "Combining Datasets",
   "builds": [
     "Join store checkouts to order revenue on <code>productId</code>",
     "Use <code>type=left</code>, and rename a field to make a join possible",
     "Stack two sources with <code>append</code>, then with <code>union</code>",
     "Answer the same question with <code>stats</code> and compare both"],
   "kicker": "You will see an inner join delete the rows that mattered."},
 ]},

]
