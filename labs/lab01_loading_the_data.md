# Lab 1 — Loading the Course Data

**Module 1 · Course Introduction**

Every other lab in this course searches the data you are about to load. Get
this one right and the rest work; get an index or a sourcetype name wrong and
you will spend Lab 2 debugging a typo.

> Your instructor has already installed the class app. Part of what it
> carries has to be there **before** a sourcetype's first event lands:
> Splunk works out the timestamp and where one event ends as it indexes, and
> writes the result into the index. Get those wrong and no later fix repairs
> them — you delete the data and load it again.
>
> The rest of the app is search-time and could have been added at any point:
> the authentication logs' field extractions, JSON field discovery, and the
> two data models.
>
> You are adding the indexes, the data and the lookups. The lookups are
> search-time too, so a mistake in Task 4 costs you a correction. A mistake
> in Task 2 or 3 costs you a reload, which is why Task 5 checks the
> timestamps and not just the counts.

## Task 1 — Create the indexes

1. Log in to Splunk at <http://localhost:8000> and switch to the
   **CLASS: Intermediate** app.

2. Go to **Settings → Indexes** and click **New Index**.

3. Create five, accepting every default except the name:

   | Index | Holds |
   | ----- | ----- |
   | `web` | Online store access logs |
   | `security` | Authentication logs |
   | `sales` | Retail transactions and order records |
   | `network` | Proxy and firewall traffic |
   | `apps` | Mobile app beta telemetry |

4. Confirm all five exist:

   ```
   | rest /services/data/indexes
   | search title IN (web, security, sales, network, apps)
   | table title, currentDBSizeMB, totalEventCount
   ```

   Five rows, all with zero events? ________

## Task 2 — Load the store logs, and pick the host from the path

The web data is an archive of three directories, one per server:

```
access/www1/access.log
access/www2/access.log
access/www3/access.log
```

You want each event's `host` to be the server it came from, not the name of
the file you uploaded.

5. Go to **Settings → Add Data** and choose **Upload**.

6. Click **Select File**, browse to `data/access.zip` in the course
   repository, and click **Open**. Splunk unpacks an archive for you. Click
   **Next**.

7. On **Set Source Type**, choose **Web > access_combined**.

   Check the preview. Are the timestamps being read correctly, and does
   `clientip` appear as a field? ________

8. Click **Next** to reach **Input Settings**.

9. For **Host**, choose **Segment in path** and enter **2**.

   The path is `access/www1/access.log`. Segment 1 is `access`, segment 2 is
   `www1`. That is the server name.

10. For **Index**, select `web`.

11. Click **Review**, check the summary, then **Submit**. You should see
    "File has been uploaded successfully".

12. Verify the host extraction worked — this is the step that catches a wrong
    segment number:

    ```
    index=web sourcetype=access_combined
    | stats count by host
    ```

    Three hosts, `www1` through `www3`? ________

    If you see one host called `access.zip`, the segment number was wrong.
    Delete the data and reload it:
    `| delete` is not the tool here — ask your instructor to clean the index.

## Task 3 — Load the rest

13. Click **Add More Data** and repeat the upload for each remaining source.
    The host for the second archive again comes from **Segment in path 2**;
    for the single files, type the host in directly.

    | File | Sourcetype | Index | Host |
    | ---- | ---------- | ----- | ---- |
    | `data/secure.zip` | `linux_secure` | `security` | Segment in path **2** |
    | `data/vendor_sales.log` | `vendor_sales` | `sales` | `appserver` |
    | `data/sales_entries.json` | `sales_entries` | `sales` | `appserver` |
    | `data/web_proxy.json` | `web_proxy` | `network` | `proxy` |
    | `data/firewall.json` | `firewall` | `network` | `firewall` |
    | `data/trailmate_beta.log` | `trailmate_beta` | `apps` | `appserver` |

14. **Select** each sourcetype on the **Set Source Type** screen — do not
    create it. All seven are already in the list: `access_combined` and
    `linux_secure` are Splunk's own, and the five course sourcetypes are
    under **Custom** because the class app defines them. Type the name into
    the dropdown's filter box to find it, check the preview updates, then
    **Next**.

    > **Do not use Save As here**, even though Fundamentals Lab 1 has you
    > create a sourcetype that way. There it is the only option. Here the
    > sourcetype already exists, and creating a second definition of the same
    > name does real damage to the three JSON sources: the UI bases a new
    > JSON sourcetype on `_json`, which carries `INDEXED_EXTRACTIONS = json`,
    > and index-time extraction then runs alongside the `KV_MODE = json` the
    > class app already sets. Every field ends up holding two identical
    > values. Nothing errors — `sc_http_status>=500` just matches nothing,
    > and `sum(total)` returns exactly twice the revenue. Task 5 checks for
    > this.

15. `secure.zip` unpacks to **four** directories, not three — there is a mail
    server as well as the three web servers. Confirm after loading:

    ```
    index=security sourcetype=linux_secure
    | stats count by host
    ```

    How many hosts? ________

16. Do **not** set a source type for `trailmate_beta.log` beyond the name. It
    is deliberately raw — Lab 8 is where you extract its fields.

## Task 4 — Create the lookups

Two CSVs turn identifiers into things a person recognises. Without them, half
the later labs return product codes instead of product names.

> **Why everything here starts `hv_`.** If you took Fundamentals on this same
> Splunk instance, you already have a `products.csv` and a `products_lookup`
> from its lookup lab — holding Buttercup Games data, not Harborview's. The
> two catalogues use the same column names and overlapping `Code` values, so
> a collision would not fail; it would quietly return *Mediocre Kingdoms*
> where you expect *Cirrus 2P Tent*. Prefixing this course's objects makes
> that impossible. It is also the naming convention Module 7 argues for,
> applied to a real problem.

17. Go to **Settings → Lookups → Lookup table files** and click **New Lookup
    Table File**.

18. Upload `data/hv_products.csv` into the **CLASS: Intermediate** app, with
    destination filename `hv_products.csv`. Repeat for `data/hv_vendors.csv`.

19. Go to **Lookup definitions** and click **New Lookup Definition**. Create
    two, both **File-based**:

    | Name | File |
    | ---- | ---- |
    | `hv_products_lookup` | `hv_products.csv` |
    | `hv_vendors_lookup` | `hv_vendors.csv` |

20. Go to **Automatic lookups** and click **New Automatic Lookup**. Create
    three:

    | Lookup table | Apply to sourcetype | Input | Output |
    | ------------ | ------------------- | ----- | ------ |
    | `hv_products_lookup` | `access_combined` | `productId` | `product_name`, `categoryId`, `price` |
    | `hv_products_lookup` | `vendor_sales` | `Code` | `product_name`, `categoryId`, `price` |
    | `hv_vendors_lookup` | `vendor_sales` | `VendorID` | `Vendor`, `VendorCity`, `VendorStateProvince`, `VendorCountry`, `Weight` |

21. Set the permissions on each to **This app only**, readable by everyone.

    Leave one of them Private and you will not notice for three labs. Lab 7
    comes back to why.

22. Verify the enrichment:

    ```
    index=web sourcetype=access_combined action=purchase
    | stats count by product_name
    ```

    Product names rather than codes like `HV-TN-101`? ________

    ```
    index=sales sourcetype=vendor_sales
    | stats count by VendorCountry
    ```

    Country names? ________

## Task 5 — Check the whole thing

23. Count everything you loaded:

    ```
    | metadata type=sourcetypes index=web index=security index=sales
                                index=network index=apps
    | table sourcetype, totalCount
    | sort sourcetype
    ```

24. Compare against what should be there:

    | Sourcetype | Events |
    | ---------- | ------ |
    | `access_combined` | 23,799 |
    | `firewall` | 6,000 |
    | `linux_secure` | 9,000 |
    | `sales_entries` | 5,000 |
    | `trailmate_beta` | 4,000 |
    | `vendor_sales` | 8,000 |
    | `web_proxy` | 6,000 |

    > Your numbers will match these exactly if your instructor generated the
    > data with the default seed. If they differ, that is fine — what matters
    > is that all seven sourcetypes are present and none is zero.

25. Check the timestamps landed in the right place. Every source should have
    events across roughly the last month, not all bunched at the moment you
    uploaded them:

    ```
    | metadata type=sourcetypes index=web index=security index=sales
                                index=network index=apps
    | eval oldest = strftime(firstTime, "%F"), newest = strftime(lastTime, "%F")
    | table sourcetype, oldest, newest
    ```

26. If one sourcetype shows today's date for both, its timestamp was not
    parsed and Splunk fell back to upload time. What would that break?
    ______________________

27. Confirm the three JSON sources extracted their fields once rather than
    twice:

    ```
    index=network sourcetype=web_proxy
    | head 1
    | eval copies = mvcount(sc_http_status)
    | table sc_http_status, copies
    ```

    `copies` has to be **1**. Repeat it for `sales_entries` with `total`, and
    for `firewall` with `bytes_out`.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 4** — Yes — five rows, every `totalEventCount` zero.

A missing row means a mistyped name. A row that already has events means you
are on an instance someone has loaded before; say so before you load this
course's data on top of it.

**Step 7** — Yes to both. `access_combined` is a built-in sourcetype, so
Splunk already knows the combined log format and extracts `clientip`,
`status`, `bytes` and the rest without being told.

**Step 12** — Three: `www1`, `www2` and `www3`. If the host shows as
`access.zip` or `access`, the segment number was 0 or 1. Segment counting
starts at 1 on the first directory in the path.

**Step 15** — Four: `www1`, `www2`, `www3` and `mailsv`. People running
`index=security` later and expecting three hosts have usually mis-set the
segment on this upload.

**Step 22** — Yes to both, and these are the two checks worth doing properly.
A missing automatic lookup does not error; it returns rows with an empty
column, which reads as "no data for that product" rather than "the lookup is
not applied".

**Step 26** — Everything time-based, which is most of the course. Every lab
specifies a time range, so a source stamped at upload time appears for a few
minutes and then falls outside every window. It is also nearly invisible:
the data is there, the searches are right, and the results are empty.

**Step 27** — 1 for all three.

A 2 means the sourcetype has a second definition performing index-time
extraction on top of the class app's search-time `KV_MODE = json`, which is
what **Save As** produces for a JSON source — see step 14. Every field then
holds two identical values, and nothing reports an error. `sc_http_status>=500`
matches nothing at all, and `sum(total)` returns exactly twice the revenue, so
Labs 9 and 15 would give confident wrong answers.

Fix it rather than working around it. Find the extra definition under
**Settings → Source types**, or in `etc/system/local/props.conf` and the
class app's `local/props.conf`. Delete it, then delete and reload that
file's events — index-time extraction cannot be undone by a search.

</details>
