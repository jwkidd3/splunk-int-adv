# Lab 1 — Search Performance and the Job Inspector

**Module 2 · Beyond Search Fundamentals**

By the end you can explain why one search is slower than another, using
evidence from the Job Inspector rather than intuition.

> If a search returns nothing, widen the time range before you debug the SPL.
> The data is generated relative to the day you ran `tools/generate_data.py`.

## Task 1 — Field names are case sensitive, values are not

1. Over **Last 24 hours**, run each of these and record the event count.

   ```
   index=web sourcetype=access_combined productId=HV-TN-101
   index=web sourcetype=access_combined productid=HV-TN-101
   index=web sourcetype=access_combined productId=hv-tn-101
   ```

   | Search | Events |
   | ------ | ------ |
   | `productId=HV-TN-101` | |
   | `productid=HV-TN-101` | |
   | `productId=hv-tn-101` | |

2. Which two agree, and what does that tell you about how Splunk treats field
   names versus field values? ______________________

## Task 2 — Which of these return nothing, and why?

3. Predict before running. Then run each over **Last 7 days**.

   | # | Search | Returns data? | Why |
   | - | ------ | ------------- | --- |
   | a | `index=security sourcetype=linux_secure` | | |
   | b | `index=web Sourcetype=access_combined` | | |
   | c | `index=web sourcetype=ACCESS_COMBINED` | | |
   | d | `index=security sourcetype=linux_se%` | | |

## Task 3 — scanCount against resultCount

4. Run this over **Last 7 days**, then open **Job > Inspect Job**.

   ```
   index=web sourcetype=access_combined
   ```

   `scanCount` ________  `resultCount` ________

5. Run the tighter version and inspect again.

   ```
   index=web sourcetype=access_combined action=purchase status=200
   ```

   `scanCount` ________  `resultCount` ________

6. The second search returns far fewer events. Did its `scanCount` drop by the
   same proportion? ______________________

7. Now move the filter after the pipe and inspect a third time.

   ```
   index=web sourcetype=access_combined
   | search action=purchase status=200
   ```

   `scanCount` ________  Same results as step 5? ________

   This is the central lesson of the module: both searches return the same
   rows, but only one of them let the index do the work.

## Task 4 — Search modes

8. Run the following in **Verbose**, then **Fast**, then **Smart**, noting the
   time from the Job Inspector each time.

   ```
   index=web sourcetype=access_combined
   ```

   Verbose ________  Fast ________  Smart ________

9. Which phase dominates in Verbose? Look at `command.search.kv`.
   ______________________

10. Leave your search mode on **Smart**.

## Task 5 — Find the expensive phase

11. Run this deliberately inefficient search over **Last 7 days** and inspect it.

    ```
    index=security sourcetype=linux_secure user=*admin
    ```

12. Then run the efficient equivalent and compare.

    ```
    index=security sourcetype=linux_secure user=admin*
    ```

    Which phase changed most, and by how much? ______________________

13. Both searches answer *almost* the same question but not quite. What does
    the second one miss? ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 2** — The first and third agree. Field *names* are case sensitive, so
`productid` matches nothing. Field *values* are not, so `hv-tn-101` works.

**Step 3** — (a) yes. (b) yes — `Sourcetype` is not a field name here, it is
treated as a bare search term, and Splunk finds the string anyway; check the
event count differs from (a). (c) yes — values are case insensitive.
(d) no — `%` is not a Splunk wildcard. Use `*`.

**Step 6** — No. `scanCount` stays high because the index still has to find
every `access_combined` event before the field filters narrow them. The gap
between the two numbers is the cost you are paying.

**Step 7** — Identical results, higher `scanCount` and a longer
`dispatch.evaluate`. Filtering after the pipe happens in memory, event by
event, instead of at the index.

**Step 9** — `command.search.kv`, field extraction. Verbose extracts every
field it can find whether you asked for it or not.

**Step 12** — `command.search.index`. A leading wildcard cannot use the index,
so Splunk reads every event in range and tests each one.

**Step 13** — `user=admin*` misses `sysadmin`, `itmadmin` and `sapadmin`. This
is the real tension: the efficient search is not always the correct one.
Module 10 solves it properly with a tag.

</details>
