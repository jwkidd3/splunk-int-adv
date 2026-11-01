# Splunk Int/Adv

Instructor setup for the Splunk Intermediate/Advanced course.

**This repository is self-contained and runs offline.** The course data, the
lookup tables, the replacement labs and the local service Lab 11 needs are all
committed here. Nothing in the classroom reaches the internet.

Two things have to be staged **before** you travel, because they cannot be
redistributed here — see [Before class](#before-class-needs-internet-once).
Everything after that works air-gapped.

---

## Before class (needs internet, once)

### 1. Save the Splunk image

The classroom procedure uses Docker. Pull the image somewhere with internet and
save it to a file:

```bash
docker pull splunk/splunk:9.2.1
```

```bash
docker save splunk/splunk:9.2.1 -o splunk-image.tar
```

Copy `splunk-image.tar` to the classroom machines alongside this repository.

> Pin a version rather than using `latest`. `latest` moves, and a lab book with
> fixed screenshots does not. Any 9.x image works; 9.2.1 is what the steps below
> were checked against.

### 2. Download the CIM add-on — only if you are teaching Module 14

Module 14 covers the Common Information Model and the `datamodel` command.
Those slides need the **Splunk Common Information Model Add-on**, which is
distributed through Splunkbase and requires a Splunk account, so it cannot live
in this repository.

Download it from <https://splunkbase.splunk.com/app/1621/> and carry the `.tgz`
with you. Module 14 is lecture-only — there is no Lab for it — so if you are
not demonstrating `| datamodel`, you can skip this entirely.

**Nothing else needs the internet.** The dataset, the lookups and the Lab 11
endpoint are all in this repository.

---

## Classroom setup (no internet required)

Work through these in order. Several labs fail if an earlier step is skipped.

### 1. Start Splunk

```bash
docker load -i splunk-image.tar
```

```bash
docker run -d -p 8000:8000 --platform linux/amd64 -e SPLUNK_GENERAL_TERMS=--accept-sgt-current-at-splunk-com -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=password --name splunk splunk/splunk:9.2.1
```

`SPLUNK_GENERAL_TERMS` is required — current images refuse to start without it.
Splunk comes up on <http://localhost:8000>, user `admin`, password `password`.

> Splunk Cloud's free eval is the other way to run this course, but it is an
> online-only option. If you need an offline classroom, use Docker.

### 2. Create the class app

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

### 3. Create the indexes

Settings > Indexes > New Index. Five are used in this class:

`web` · `security` · `sales` · `network` · `games`

### 4. Load the data

Everything is in [`data/`](data/) in this repository — no download step.

| Index | Type | Sourcetype | host(s) | Source (file) |
| ----- | ---- | ---------- | ------- | ------------- |
| web | Online Sales | `access_combined` | segment in path 2 | `data/access.zip` |
| security | Web Server | `linux_secure` | segment in path 2 | `data/secure.zip` |
| sales | sales_entries | `sales_entries` | appserver | `data/sample_sales_entries_data.json` |
| sales | retail_sales | `vendor_sales` | appserver | `data/vendor_sales.log` |
| network | Web Security Appliance | `cisco_wsa_squid` | webserver | `data/sample_cisco_wsa_squid_data.json` |
| network | firewall_data | `cisco_firewall` | firewall | `data/sample_cisco_firewall_data.json` |
| games | Game logs | `SimCubeBeta` | appserver | `data/sample_sim_cube_beta_data.txt` |

Notes on the table:

- **Segment in path 2** — both archives unzip to `<name>/<host>/<name>.log`, so
  segment 2 gives the host. `access.zip` yields `www1`, `www2`, `www3`;
  `secure.zip` yields `www1`, `www2`, `www3` **and** `mailsv`.
- **`games` / `SimCubeBeta` is required by Lab 7, Task 2.** It was missing from
  earlier versions of this table, which made that half of Lab 7 impossible.
  Load it as a comma-delimited file; students build the field extractions
  themselves, so do not pre-extract anything.
- The sourcetype for the web data is **`access_combined`**, not
  `access_combined_wcookie`. The logs carry no cookie field — `JSESSIONID` is a
  URL query parameter — so `access_combined` is the correct pretrained
  sourcetype. See Known issues for the one lab that disagrees.

### 5. Create the auto lookups

Settings > Lookups. Upload each file from `data/`, add a lookup definition,
then add an automatic lookup bound to the sourcetype.

| Sourcetype | Lookup file | Match field |
| ---------- | ----------- | ----------- |
| `access_combined` | `data/products.csv` | `productId` |
| `vendor_sales` | `data/products.csv` | `Code` |
| `vendor_sales` | `data/vendors.csv` | `VendorID` |

These supply `product_name`, `categoryId` and `price` to the web data, and
`VendorCountry` / `VendorStateProvince` to the retail data. Labs 2, 3, 4, 5, 10
and 12 all depend on them.

### 6. Create the HTTP status lookup

**Lab 12, Task 7 needs this and nothing else in the course creates it.** Use
[`http_status.csv`](http_status.csv) from this repository — Splunk's built-in
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

### 7. Start the local endpoint for Lab 11

Lab 11's workflow actions point at a public whois site, which does not work
without internet. Start the bundled stand-in instead:

```bash
python3 tools/ip_lookup_server.py
```

It serves on `http://127.0.0.1:8888`, needs nothing beyond the Python 3
standard library, and should be left running for Lab 11.

Students then use `http://127.0.0.1:8888/whois?ip=$src_ip$` in place of the
`who.is` URI in step 8. Full instructions, including the restored Task 2, are
in [`labs/lab_11_task_2_post_workflow_action.md`](labs/lab_11_task_2_post_workflow_action.md).

---

## What is in this repository

| Path | What it is |
| ---- | ---------- |
| `Splunk_Intermediate.pdf` | The slide deck, 14 modules |
| `splunk_int_lab_*.pdf` | Lab book, Labs 1–12 (6 is missing — see below) |
| `supplement.pdf` | Index / sourcetype / field reference |
| `search_opt.pdf` | Two Splunk .conf decks on search optimisation, 2014 |
| `labs/` | Replacement and correction material for the broken labs |
| `data/` | The full course dataset |
| `tools/ip_lookup_server.py` | Offline stand-in for Lab 11's external whois |
| `http_status.csv` | Lookup table required by Lab 12 Task 7 |
| `splunk_upskill*.txt`, `splunk_rex_erex.txt` | Supplementary SPL, see Known issues |
| `commands` | One-liner to list populated indexes |

### Replacement labs

| File | Replaces |
| ---- | -------- |
| [`labs/lab_06_introduction_to_knowledge_objects.md`](labs/lab_06_introduction_to_knowledge_objects.md) | Lab 6, absent from the lab book |
| [`labs/lab_11_task_2_post_workflow_action.md`](labs/lab_11_task_2_post_workflow_action.md) | Lab 11 Task 2, lost with page 50; also the offline fix for Task 1 |
| [`labs/lab_03_corrections.md`](labs/lab_03_corrections.md) | Correction sheet for Lab 3's font defect |

---

## Lab-to-module map

The labs are numbered one behind the modules, and Lab 1 compounds this by
saying it reviews "Module 1." Use this mapping:

| Module | Lab |
| ------ | --- |
| 1 — Course Introduction | — |
| 2 — Beyond Search Fundamentals | Lab 1 |
| 3 — Commands for Visualizations | Lab 2 |
| 4 — Advanced Visualizations | Lab 3 *(+ corrections sheet)* |
| 5 — Filtering and Formatting Data | Lab 4 |
| 6 — Correlating Events | Lab 5 |
| 7 — Introduction to Knowledge Objects | `labs/lab_06_…md` |
| 8 — Creating and Managing Fields | Lab 7 |
| 9 — Field Aliases and Calculated Fields | Lab 8 |
| 10 — Creating Tags and Event Types | Lab 9 |
| 11 — Creating and Using Macros | Lab 10 |
| 12 — Creating and Using Workflow Actions | Lab 11 *(+ Task 2 file)* |
| 13 — Creating Data Models | Lab 12 |
| 14 — Using the CIM Add-On | — |

---

## Known issues

Check these before you teach; each one will otherwise surface mid-class.

**Defects in the lab PDFs**

- **Lab 3 will not render the digit `2`.** Step numbers, the Task 2 heading and
  the report name `L3S2` are all wrong, and step 22's hint reads "status, **00**"
  where it means **200**. Hand out
  [`labs/lab_03_corrections.md`](labs/lab_03_corrections.md).
- **Lab 1 says `sourcetype=access_combined_wcookie`** in all four of its
  searches. Load the web data as `access_combined` per the table above and have
  students substitute, or use `access_combined*`. The deck, Labs 3/4/5/12 and
  `supplement.pdf` all use `access_combined`.
- **Lab 11's PDF is missing page 50**, so it jumps from step 14 to step 32. The
  missing Task 2 is restored in
  [`labs/lab_11_task_2_post_workflow_action.md`](labs/lab_11_task_2_post_workflow_action.md).
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
  tell students to change `VendorCountry` off Germany/France/Italy. Step 20's
  link to `bit.ly` for the € symbol will not resolve offline — the lab already
  says to copy the symbol out of the document, which is the better route anyway.

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
- Module 14's slides link to `docs.splunk.com` and Splunkbase. Those pages are
  unreachable offline; the reference tables they point at are reproduced on
  slides 186–187.

**Supplementary files**

- `supplement.pdf` lists `winauthentication_security` and `history_access`
  sourcetypes under the `security` index. Neither is loaded by this course and
  neither exists in the dataset — ignore those two rows. Page 2 also prints
  `data_wday` and `data_year`, which should be `date_wday` and `date_year`.
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
are dated September 2023, and the JSON files are dated 2024. Labs ask for
"Last 24 hours," "Last 7 days" and "Last 30 days", so **expect to widen the
time range on nearly every exercise**.

The JSON and SimCube files were produced by `Splunk_INT_Sample_Data_Gen.ipynb`
in the companion data repository. Regenerating them needs that notebook and a
Python environment, not the internet, so it can be done ahead of class to get
current timestamps. The two `.zip` archives and `vendor_sales.log` are static
and cannot be regenerated — those always need a widened time range.

> This is not a production environment. Splunk's UI changes on a semi-regular
> basis and screenshots do not always match the product. Lab data should be
> consistent, but there are circumstances where an exercise has to be adapted
> based on data availability.
