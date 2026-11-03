# Lab 4 — Trendlines, Maps and Single Values

**Module 4 · Advanced Visualizations**

Five visualizations, five saved reports: L4S1 through L4S5.

## Task 1 — Failed logins with a trendline

1. Over **Last 7 days**, find failed authentication attempts.

   ```
   index=security sourcetype=linux_secure "Failed password"
   ```

2. Count them per day and name the column `failures`.

   ```
   | timechart span=1d count as failures
   ```

3. Change the visualization to **Line Chart**.

4. Add a five-day simple moving average named `trend`.

   ```
   | trendline sma5(failures) as trend
   ```

5. The trend line does not start at the same point as the failures line. Why?
   ______________________

6. Save as **L4S1**.

## Task 2 — Single value with a trend indicator

7. Over **Last 7 days**, count daily tent sales through the retail channel.

   ```
   index=sales sourcetype=vendor_sales categoryId="TENTS"
   | timechart span=1d count
   ```

   > `categoryId` arrives from the `hv_products.csv` lookup, so the value is case
   > sensitive. Type `TENTS` in uppercase.

8. Change the visualization to **Single Value** and set:

   | Option | Value |
   | ------ | ----- |
   | Caption | `Tent Sales – Previous Day` |
   | Show trend indicator | Yes |
   | Show sparkline | Yes |
   | Use colours | Yes |
   | Colour by | Trend |
   | Colour mode | Background |

9. Save as **L4S2**.

10. Suppose this panel tracked failed logins instead of sales. What would you
    have to change about the colour settings, and why? ______________________

## Task 3 — Choropleth map of US retail sales

11. Over **Last 7 days**, find United States retail sales. US vendors have a
    `VendorID` below 3000.

12. Count the events over `VendorStateProvince`.

13. Map the results onto the bundled US states geometry.

    ```
    | geom geo_us_states featureIdField=VendorStateProvince
    ```

14. On the **Visualization** tab choose **Choropleth Map** and zoom to the
    United States.

15. Under **Format → Tiles**, click **Populate from preset configuration** and
    choose **Open Street Map**.

16. Save as **L4S3**.

## Task 4 — Cluster map of online purchases

17. Over **Last 7 days**, find successful online purchases.

    ```
    index=web sourcetype=access_combined action=purchase status=200
    ```

    > Hint: you can narrow this from the Fields sidebar — pick `purchase` from
    > `action` and `200` from `status`.

18. Resolve the client addresses to coordinates.

    ```
    | iplocation clientip
    ```

    Check the Fields sidebar for `lat` and `lon`.

19. Plot them.

    ```
    | geostats count by Country
    ```

    Change the visualization to **Cluster Map** if it does not appear
    automatically.

20. Some events produce no location at all. What kind of address does
    `iplocation` fail on, and what would you do about it in a real dashboard?
    ______________________

21. Save as **L4S4**.

## Task 5 — Units sold by country with a grand total

22. Over **Last 24 hours**, count retail purchases by country and rename the
    column `Units Sold`.

23. Add a labelled totals row, suppressing the per-row total.

    ```
    | addtotals col=t row=f labelfield=VendorCountry label="Total"
    ```

24. Scroll to the bottom of the last page of results to see it.

25. Save as **L4S5**.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 5** — A five-period moving average has nothing to average until the
fifth point, so the first four are null. The gap is correct.

**Step 10** — Colour by trend assumes an increase is good. For failures you
would invert the colours, or the panel will turn green exactly when things are
getting worse.

**Step 20** — Private, reserved and loopback addresses have no public
geolocation. In a real dashboard, either filter them out before mapping or
`fillnull` them into an explicit "Internal" bucket, so they are visibly
excluded rather than silently missing.

</details>
