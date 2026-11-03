# Lab 5 — Filtering Results and Manipulating Data

**Module 5 · Filtering and Formatting Data**

## Task 1 — Daily traffic volume in megabytes

1. Over **Last 7 days**, search the online store and total the bytes per day.

   ```
   index=web sourcetype=access_combined
   | timechart span=1d sum(bytes) as bytes
   ```

2. Convert to megabytes with `eval`, rounded to two decimal places.

   ```
   | eval MB = round(bytes/1048576, 2)
   ```

3. Show it as a **Line Chart** and set the X axis label to `Day`. Notice the
   raw `bytes` series is still plotted.

4. Remove it.

   ```
   | fields - bytes
   ```

5. Why divide by 1048576 rather than 1000000? ______________________

6. Save as **L5S1**.

## Task 2 — GET to POST ratio per server

7. Over **Last 24 hours**, count requests by host and method.

   ```
   index=web sourcetype=access_combined
   | chart count over host by method
   ```

8. Add a ratio column, rounded to two places.

   ```
   | eval Ratio = round(GET/POST, 2)
   ```

9. One host could in principle produce a null ratio. Under what circumstance,
   and how would you guard against it? ______________________

10. Save as **L5S2**.

## Task 3 — Accounts with repeated failures

11. Over **Last 24 hours**, find failed logins and count them by account.

    ```
    index=security sourcetype=linux_secure "Failed password"
    | stats count by user
    ```

    > An hour is too short a window for this question: the generated failures
    > work out at roughly three an hour across all 125 accounts, so no single
    > account reaches four. Over 24 hours three accounts qualify; over 7 days,
    > twenty-six.

12. Keep only accounts with more than three, sorted descending.

    ```
    | search count > 3
    | sort - count
    ```

13. Swap `search` for `where` and confirm you get the same answer. Now change
    the field name's case in both. Which one still works, and why?
    ______________________

14. Save as **L5S3**.

## Task 4 — Classify event sizes

15. Over **Last 24 hours**, classify each store request by response size:
    under 2000 bytes *Small*, 2000 to under 2500 *Medium*, 2500 to under 3000
    *Large*, 3000 and over *Extra Large*.

    ```
    index=web sourcetype=access_combined
    | eval dataSize = case(bytes < 2000,  "Small",
                           bytes < 2500,  "Medium",
                           bytes < 3000,  "Large",
                           true(),        "Extra Large")
    ```

16. Count by `dataSize` and show it as a **Pie Chart**.

17. The conditions look like they overlap but do not. Why does `bytes < 2500`
    not also catch everything under 2000? ______________________

18. Save as **L5S4**.

## Challenge — Employee traffic by content type

19. Over **Last 7 days**, count proxy events by `http_content_type`.

    ```
    index=network sourcetype=web_proxy
    | stats count by http_content_type
    ```

20. Add a `type` column: anything beginning `image` is `graphic`, everything
    else is `other`.

    ```
    | eval type = if(like(http_content_type, "image%"), "graphic", "other")
    ```

    > `like()` is a function and works inside `eval`. The bare `LIKE` operator
    > only works in a `where` clause — a common source of confusion.

21. Sum the counts by `type`, renaming the result `total`, and show a pie chart.

22. Save as **L5C1**.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 5** — A megabyte here means 1024², which is what Splunk's own byte
fields and most storage tooling mean. Dividing by a million gives you
megabytes in the SI sense and a number about 5% too large.

**Step 9** — If a host served no POST requests in the window, `POST` is null
and the division yields null. Guard with
`| fillnull value=0 POST | eval Ratio = if(POST > 0, round(GET/POST, 2), null())`,
or decide that a null is the honest answer and leave it.

**Step 13** — `where` is case sensitive on field values but both commands are
case sensitive on field *names*, so `Count` fails in each. The difference
appears when you change a *value*: `search user=ACHO` matches, `where
user="ACHO"` does not.

**Step 16** — Over **Last 24 hours**, four slices:

```
index=web sourcetype=access_combined
| eval dataSize = case(bytes < 2000,  "Small",
                       bytes < 2500,  "Medium",
                       bytes < 3000,  "Large",
                       true(),        "Extra Large")
| stats count by dataSize
```

**Step 17** — `case` evaluates top to bottom and stops at the first true
condition. Anything under 2000 already matched and left the comparison, so by
the time the second condition runs it only sees values of 2000 and above.

**Step 21** — Over **Last 7 days**, the Challenge search in full:

```
index=network sourcetype=web_proxy
| stats count by http_content_type
| eval type = if(like(http_content_type, "image%"), "graphic", "other")
| stats sum(count) as total by type
```

`sum(count)`, not `count`. The first `stats` already counted the events; this
one totals those counts. Write `| stats count as total by type` and you get
the number of *content types* in each group — two small numbers that look
plausible and mean nothing.

</details>
