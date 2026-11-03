# Lab 3 — Transforming Commands and Charts

**Module 3 · Commands for Visualizations**

You will build three visualizations and collect them on a dashboard that later
labs reuse.

## Task 1 — Authentication outcomes by source address

1. Search the security index over **Last 7 days** for events that are *not*
   session openings.

   ```
   index=security sourcetype=linux_secure NOT "session opened"
   ```

2. Count them by outcome and source address. `vendor_action` is supplied by
   the `linux_secure` sourcetype; check the Fields sidebar if you do not see it.

   ```
   index=security sourcetype=linux_secure NOT "session opened"
   | chart count over src_ip by vendor_action
   ```

3. Switch to the **Visualization** tab and choose **Column Chart**.

4. Ninety source addresses is more than a chart can show. Narrow it to the
   ten busiest.

   ```
   index=security sourcetype=linux_secure NOT "session opened"
   | chart count over src_ip by vendor_action
   | addtotals
   | sort - Total
   | head 10
   | fields - Total
   ```

   > `limit` and `useother` would be the obvious reach here and neither does
   > anything: both apply to the **`by`** field, and `vendor_action` has two
   > values. There is no OTHER column to remove. Task 2 uses them on a `by`
   > field with fourteen values, where they do exactly what you would expect.

5. Click **Format**, and under General set **Stack Mode** to *Stacked*.

6. Save as a report named **L3S1**.

7. From the confirmation screen click **Add to Dashboard**, and create a new
   dashboard:

   | Field | Value |
   | ----- | ----- |
   | Dashboard | New |
   | Title | `IT Ops` |
   | Panel title | `Accepted vs Failed by Source` |
   | Powered by | Report |

8. View the dashboard, click **Edit**, open the panel's **More actions** menu,
   choose **Edit Drilldown**, and set *On click* to **Link to search**. Apply
   and save.

9. Click a bar. Where does it take you? ______________________

## Task 2 — Five best sellers by country

VendorID ranges carry meaning:

| Range | Region |
| ----- | ------ |
| 1000–2999 | United States |
| 3000–3999 | Canada |
| 4000–4999 | Latin America |
| 5000–6999 | Europe & Middle East |
| 7000–8999 | Asia Pacific |
| 9000–9900 | Africa |
| 9901–9999 | Outliers |

10. Over **Last 7 days**, find retail sales from North America.

    ```
    index=sales sourcetype=vendor_sales VendorID<4000
    ```

11. Count the events over `VendorCountry`.

12. Split by product with a `by` clause on `product_name`.

13. Keep only the five best sellers with `limit=5`, and drop the OTHER column.

14. Show it as a **Column Chart**. In **Format**, label the X axis `Country`
    and the Y axis `Volume`, then change the Y axis scale from linear to **Log**.

15. Why does a log scale help here? ______________________

16. Save as **L3S2**.

## Task 3 — Employee web usage over time

17. Click **Search** to clear the formatting you set in Task 2.

18. Over **Last 24 hours**, time-chart proxy traffic by category.

    ```
    index=network sourcetype=web_proxy
    | timechart count by usage
    ```

19. Change the visualization to **Line Chart** and save as **L3S3**.

20. Add it to the `IT Ops` dashboard in a panel named
    `Internet Usage - Last 24 Hours`. Close the confirmation without viewing.

21. Open the **Trellis** tab, tick **Use Trellis Layout**, and set Scale to
    **Independent**.

22. Save as **L3S4** and add it to `IT Ops` as `Internet Usage by Category`.

23. Compare the two panels. What does Independent scaling reveal that the
    single line chart hid? ______________________

24. Edit the dashboard, arrange the panels sensibly, and save.

> Formatting choices persist between searches. If your next chart appears
> trellised for no reason, that is why — turn it off in the Trellis tab.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 9** — To the search that produced the clicked bar, with the series and
X-axis values added as filters. Use the browser's Back button to return.

**Step 11** — Over **Last 7 days**:

```
index=sales sourcetype=vendor_sales VendorID<4000
| chart count over VendorCountry
```

**Step 12** — ```
index=sales sourcetype=vendor_sales VendorID<4000
| chart count over VendorCountry by product_name
```

Two rows — the United States and Canada — and fourteen product columns, plus
an OTHER column.

**Step 13** — ```
index=sales sourcetype=vendor_sales VendorID<4000
| chart count over VendorCountry by product_name limit=5 useother=f
```

`limit=5` keeps the five largest `product_name` series and `useother=f` drops
the OTHER column that would otherwise collect the other nine.

Both options act on the **`by`** field. That is why they work here and did
nothing in Task 1, where the `by` field had only two values.

**Step 15** — The best seller outsells the fifth by a wide margin, so on a
linear axis the smaller series are flattened to near-zero. A log scale makes
their shape visible while keeping the ordering honest.

**Step 23** — Low-volume categories have their own shape and their own peaks.
On a shared axis they are a flat line along the bottom. The trade-off is that
you can no longer compare magnitudes across panels by eye.

</details>
