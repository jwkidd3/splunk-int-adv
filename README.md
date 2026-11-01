# Splunk Int/Adv

Instructor setup for the Splunk Intermediate/Advanced course. Work through
**Setup** in order — several labs fail if an earlier step is skipped.

---

## 1. Choose your Splunk implementation

Either request a free eval Splunk Cloud instance at
<https://www.splunk.com/en_us/download/splunk-cloud.html>, or run Splunk in a
Docker container:

```bash
docker run -d -p 8000:8000 --platform linux/amd64 -e SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=password --name splunk splunk/splunk:latest
```

`SPLUNK_GENERAL_TERMS` is required — current `splunk/splunk` images refuse to
start without it.

## 2. Create the class app

Labs 8, 10, 11 and 12 all reference this app by name. Create it before loading
data, so the knowledge objects students create land in the right place.

Settings > Apps > Create app:

| Field | Value |
| ----- | ----- |
| Name | `CLASS: Intermediate` |
| Folder name | `class_Fund2` |
| Visible | Yes |

The folder name is what the lab PDFs show in the **Destination app** dropdown;
the display name is what they mean by "return to the CLASS: Intermediate app."
Both have to match or the labs will not line up with what students see.

## 3. Load the data

Pull everything from <https://github.com/jwkidd3/splunk_int_adv_data>.

Five indexes are used in this class: `web`, `security`, `sales`, `network`
and `games`. Create them first (Settings > Indexes > New Index).

| Index | Type | Sourcetype | host(s) | Source (file) |
| ----- | ---- | ---------- | ------- | ------------- |
| web | Online Sales | `access_combined` | segment in path 2 | `access.zip` |
| security | Web Server | `linux_secure` | segment in path 2 | `secure.zip` |
| sales | sales_entries | `sales_entries` | appserver | `sample_sales_entries_data.json` |
| sales | retail_sales | `vendor_sales` | appserver | `vendor_sales.log` |
| network | Web Security Appliance | `cisco_wsa_squid` | webserver | `sample_cisco_wsa_squid_data.json` |
| network | firewall_data | `cisco_firewall` | firewall | `sample_cisco_firewall_data.json` |
| games | Game logs | `SimCubeBeta` | appserver | `sample_sim_cube_beta_data.txt` |

Notes on the table:

- **Segment in path 2** — both archives unzip to `<name>/<host>/<name>.log`, so
  segment 2 gives the host. `access.zip` yields `www1`, `www2`, `www3`;
  `secure.zip` yields `www1`, `www2`, `www3` **and** `mailsv`.
- **`games` / `SimCubeBeta` is required by Lab 7, Task 2.** It was missing from
  earlier versions of this table, which made that half of Lab 7 impossible.
  Load it as a comma-delimited file; students build the field extractions
  themselves, so do not pre-extract anything.
- The data repo also contains `sample_linux_secure_data.json`. It is an
  alternative to `secure.zip`, not an addition — load one or the other, not
  both, or `linux_secure` event counts will be doubled.

## 4. Create the auto lookups

Settings > Lookups. Upload each file, add a lookup definition, then add an
automatic lookup bound to the sourcetype.

| Sourcetype | Lookup file | Match field |
| ---------- | ----------- | ----------- |
| `access_combined` | `products.csv` | `productId` |
| `vendor_sales` | `products.csv` | `Code` |
| `vendor_sales` | `vendors.csv` | `VendorID` |

These are what supply `product_name`, `categoryId` and `price` to the web data,
and `VendorCountry` / `VendorStateProvince` to the retail data. Labs 2, 3, 4, 5,
10 and 12 all depend on them.

## 5. Create the HTTP status lookup

**Lab 12, Task 7 needs this and nothing else in the course creates it.** Use
[`http_status.csv`](http_status.csv) from this repo — Splunk's built-in
`http_status.csv` will not work, because its columns are named
`status`/`status_description` and Lab 12 asks students to pick `code` and
`description`.

1. Settings > Lookups > Lookup table files > New. Upload `http_status.csv` into
   the **Search & Reporting** app (Lab 12 builds its data model there, not in
   `class_Fund2` — see the note in the lab).
2. Settings > Lookups > Lookup definitions > New. Name it exactly
   **`http_status_lookup`**, type File-based, pointing at `http_status.csv`.
3. Set permissions so students can read it.

No automatic lookup is needed; Lab 12 wires it into the data model by hand.

---

## Lab-to-module map

The labs are numbered one behind the modules, and Lab 1 compounds this by
saying it reviews "Module 1." Use this mapping:

| Module | Lab |
| ------ | --- |
| 1 — Course Introduction | — |
| 2 — Beyond Search Fundamentals | Lab 1 |
| 3 — Commands for Visualizations | Lab 2 |
| 4 — Advanced Visualizations | Lab 3 |
| 5 — Filtering and Formatting Data | Lab 4 |
| 6 — Correlating Events | Lab 5 |
| 7 — Introduction to Knowledge Objects | Lab 6 — **missing, see below** |
| 8 — Creating and Managing Fields | Lab 7 |
| 9 — Field Aliases and Calculated Fields | Lab 8 |
| 10 — Creating Tags and Event Types | Lab 9 |
| 11 — Creating and Using Macros | Lab 10 |
| 12 — Creating and Using Workflow Actions | Lab 11 |
| 13 — Creating Data Models | Lab 12 |
| 14 — Using the CIM Add-On | — |

---

## Known issues

Check these before you teach; each one will otherwise surface mid-class.

**Missing material**

- **Lab 6 does not exist in this repo** (it would be pages 28–29 of the lab
  book). Module 7 has no lab — plan a discussion or demo instead.
- **Lab 11 is missing Task 2 and page 50.** The PDF runs Task 1 (steps 1–14),
  then jumps to Task 3 at step 32. The lab's description promises GET, POST and
  Search workflow actions; the POST action is gone. Demo it or skip it, and
  warn students about the step-number jump.

**Defects in the lab PDFs**

- **Lab 3 will not render the digit `2`.** It shows `Task  :` for Task 2,
  `1 .` for step 12, `L3S ` for the report name L3S2, and — the one that
  actually misleads — **"from status, 00"** in step 22, which should be
  **status, 200**. Walk students through Lab 3 rather than letting them read it.
- **Lab 1 says `sourcetype=access_combined_wcookie`.** Load the web data as
  `access_combined` (per the table above) and have students substitute, or use
  `access_combined*`. The data has no cookie field — `JSESSIONID` is a URL query
  parameter — so `access_combined` is the correct pretrained sourcetype, and it
  is what the slide deck, Labs 3/4/5/12 and `supplement.pdf` all use.
- **Lab 12, step 13 asks for `date-mday`** with a hyphen. The real
  auto-extracted field is **`date_mday`**, which is what step 28 uses.
- **Lab 3, step 6** shows `categoryId=”STRATEGY”` with curly quotes. Retype them
  as straight quotes.
- **Lab 1 goes Task 2 → Task 4.** There is no Task 3; the step numbering is
  continuous, so nothing is actually missing.
- **Lab 2, Task 1's heading** says "top ten completed events … last 24 hours …
  new security dashboard." The steps actually run a 7-day search, produce no
  top-ten, and name the dashboard **IT Ops**. Follow the steps.
- **Lab 10, step 21** says to run the search "for sales in the UK" but does not
  tell students to change `VendorCountry` off Germany/France/Italy.

**Defects in the slide deck**

- Slide 12: `| fields clientip bytes referrer` — the field is `referer`.
- Slide 70: the discount example uses `sum(sale_price)`. `products.csv` has no
  `sale_price` column, so this will not run against our data.
- Slide 71: `TotalLostRevenue = $ + tostring(...)` — the `$` must be quoted
  (`"$"`), as it correctly is in the first eval on the same slide.
- Slide ~79: `| sort –sales` uses an en-dash. Retype as `-`.
- Slide 83: `fillnull VALUE=“N/A”` — should be lowercase `value=` with straight
  quotes.
- Slide 142: `tostring('USD’,"commas")` mixes a straight and a curly quote.

**Supplementary files**

- `supplement.pdf` lists `winauthentication_security` and `history_access`
  sourcetypes under the `security` index. Neither is loaded by this course and
  neither exists in the data repo — ignore those two rows.
- `splunk_upskill.txt` targets a different dataset (`index=main`,
  `sourcetype=log4j`, `uri_path=/viewItem`, `threadId`) that this course does
  not load. Most of it will not run here; treat it as SPL reading material. It
  also has several queries run together on one line, and four that use an
  en-dash in `sort –`.
- `splunk_upskill2.txt` refers to a report named "Purchasing trends" and a
  dashboard "Buttercup Games - Purchases" that its own earlier steps save under
  different names. Its Docker command omits `SPLUNK_GENERAL_TERMS` — use the one
  in section 1 instead.
- `search_opt.pdf` is two Splunk .conf decks from 2014, bundled back to back.
  Its agenda on page 3 only covers pages 1–71. It references the SOS app, which
  Splunk replaced with the Monitoring Console in 6.5.

---

## Data currency

The bundled data is historical: `access.zip`, `secure.zip` and `vendor_sales.log`
are dated September 2023, and the generated JSON files are dated 2024. Labs ask
for "Last 24 hours," "Last 7 days" and "Last 30 days", so **expect to widen the
time range on nearly every exercise**, or regenerate the data first.

The JSON and SimCube files come from `data/splunk_sample_data_scripts/Splunk_INT_Sample_Data_Gen.ipynb`
in the data repo. Re-run that notebook before class to get current timestamps.
The two `.zip` archives and `vendor_sales.log` are static and cannot be
regenerated — those always need a widened time range.

> This is not a production environment. Splunk's UI changes on a semi-regular
> basis and screenshots do not always match the product. Lab data should be
> consistent, but there are circumstances where an exercise has to be adapted
> based on data availability.
