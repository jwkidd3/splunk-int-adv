# Lab 2 — Search Performance and the Job Inspector

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

## Task 3 — scanCount, resultCount, and the search optimizer

4. Run this over **Last 7 days**, then open **Job → Inspect Job**.

   ```
   index=web sourcetype=access_combined
   ```

   `scanCount` ________  `resultCount` ________

5. Put the filter in the base search and inspect again.

   ```
   index=web sourcetype=access_combined action=purchase status=200
   ```

   `scanCount` ________  `resultCount` ________

   Both numbers drop, and by a lot. Splunk narrowed at the index instead of
   reading everything and discarding most of it.

6. Now move the filter after the pipe. Predict the `scanCount` before you run
   it — most people expect this to be worse.

   ```
   index=web sourcetype=access_combined
   | search action=purchase status=200
   ```

   `scanCount` ________  Same as step 5? ________

7. Run it again with Splunk's search optimizer turned off.

   ```
   index=web sourcetype=access_combined
   | noop search_optimization=false
   | search action=purchase status=200
   ```

   `scanCount` ________

   What did the optimizer do for you in step 6? ______________________

8. Finally, put something between the base search and the filter that the
   optimizer cannot see through.

   ```
   index=web sourcetype=access_combined
   | eval a = lower(action)
   | where a = "purchase" AND status = 200
   ```

   `scanCount` ________  `resultCount` ________

   Why can Splunk no longer push the filter down, and what does that cost?
   ______________________

## Task 4 — Search modes

9. Run the following in **Verbose**, then **Fast**, then **Smart**, noting the
   time from the Job Inspector each time.

   ```
   index=web sourcetype=access_combined
   ```

   Verbose ________  Fast ________  Smart ________

10. Which phase dominates in Verbose? Look at `command.search.kv`.
    ______________________

11. Leave your search mode on **Smart**.

## Task 5 — What a leading wildcard costs

12. Run this deliberately inefficient search over **Last 7 days** and inspect it.

    ```
    index=security sourcetype=linux_secure user=*admin
    ```

13. Then run the efficient equivalent and compare.

    ```
    index=security sourcetype=linux_secure user=admin*
    ```

    `scanCount`, leading ________  trailing ________

    Compare the elapsed times too. Which of the two numbers actually tells you
    anything at this data volume? ______________________

14. Both searches answer *almost* the same question but not quite. What does
    the second one miss? ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 1** — 28, 0, 28. Figures below are from the reference dataset. Yours will match closely if the data was generated the morning of class.

| Search | Events |
| ------ | ------ |
| `productId=HV-TN-101` | 28 |
| `productid=HV-TN-101` | 0 |
| `productId=hv-tn-101` | 28 |

Field *names* are case sensitive, so `productid` is a field that does not
exist and nothing can match it. Field *values* are not, so `hv-tn-101` finds
the same 28 events as `HV-TN-101`.

The middle search is worth inspecting: `scanCount` 28, `resultCount` 0. All
three read the same 28 events, because `HV-TN-101` is an indexed term in the
raw text. The second one then discards every one of them.

**Step 2** — The first and third agree. Field *names* are case sensitive, so
`productid` matches nothing. Field *values* are not, so `hv-tn-101` works.

**Step 3** — (a) yes. (b) yes — `Sourcetype` is not a field name here, it is
treated as a bare search term, and Splunk finds the string anyway; check the
event count differs from (a). (c) yes — values are case insensitive.
(d) no — `%` is not a Splunk wildcard. Use `*`.

**Steps 4 and 5** — On the class dataset, roughly 4,650 scanned and returned
with no filter, against 413 and 413 with it. Both numbers fall together,
because the filter values are searchable terms and the index can narrow on
them directly.

**Step 4** — Over **Last 7 days**: `scanCount` 4,709 and `resultCount` 4,709.

With no filter beyond the sourcetype, every event read is an event returned.

**Step 5** — `scanCount` 416 and `resultCount` 416 — about eleven times less than step 4.

Both numbers fall together, and that is the tell. Splunk used the index to
find the 416 matching events rather than reading 4,709 and discarding most of
them.

**Step 6** — Identical. Around 413 either way. This surprises most people, and
the reason is step 7.

**Step 7** — With the optimizer disabled, `scanCount` jumps back to about
4,650 — eleven times the work for the same 413 rows. That is what the
optimizer was quietly saving you in step 6: it recognised a plain `search`
immediately after the base search and pushed the predicate back down into it.

**Step 8** — Around 4,650 scanned for 413 results. The `eval` creates a field
that does not exist in the index, so the filter now depends on a value Splunk
can only compute after reading each event. The optimizer cannot see through
the transformation and stops trying.

So the lesson is sharper than "filter early". Splunk will often fix a simple
late filter for you, and it cannot fix anything it cannot see through. Write
the filter into the base search and you never have to work out which case you
are in.

**Step 9** — `scanCount` is 4,709 in all three modes. The mode changes how much field
extraction Splunk does per event, not how much data it reads, so read
`runDuration` and ignore the scan.

Fast is quickest. Smart is the one worth understanding: it has no fixed cost
of its own, it picks a side. With no transforming command it discovers fields
like Verbose; add a `| stats` and it behaves like Fast. Measured over
**Last 7 days**:

| Search | Verbose | Fast | Smart |
| ------ | ------- | ---- | ----- |
| `index=web sourcetype=access_combined` | 0.335s | 0.064s | 0.134s |
| the same, plus `\| stats count by host` | 0.155s | 0.088s | 0.060s |

Absolute timings move from run to run; the pattern does not. Smart tracks
Verbose on the first row and Fast on the second.

**Step 10** — `command.search.kv`, field extraction. Verbose extracts every
field it can find whether you asked for it or not.

**Step 13** — `scanCount` is the number that matters: about 1,740 for the
leading wildcard against 97 for the trailing one, roughly eighteen times the
work. The elapsed times are near identical and tell you nothing — at this
volume both finish in well under a tenth of a second, and the difference is
lost in noise. On production data that same ratio is the difference between a
search that returns and one that does not.

**Step 14** — `user=admin*` misses `sysadmin`, `itmadmin` and `sapadmin`. This
is the real tension: the efficient search is not always the correct one.
Module 10 solves it properly with a tag.

</details>
