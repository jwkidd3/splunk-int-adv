# Lab 16 — System Administration and Monitoring

**Module 18 · System Administration and Monitoring**

Splunk indexes its own operation. This lab is about reading that, which is
how you answer "why is it slow?" with evidence instead of a guess.

> Searches here target `_internal` and `_audit`, Splunk's own indexes rather
> than course data. They are present on every instance, so these searches
> work anywhere — but the numbers you see will be yours, not the ones quoted
> in the answers.

## Task 1 — The Monitoring Console

1. Go to **Settings > Monitoring Console**. On a single instance it opens in
   standalone mode, which is what the class container runs.

2. Open **Overview**. Note the three panels: indexing rate, search activity,
   and resource usage.

3. Open **Indexing > Indexing Performance > Indexing Performance: Instance**.

   What is the current indexing rate? ________

4. Open **Search > Search Activity > Search Activity: Instance**.

   How many searches have run in the last hour? ________

5. The Monitoring Console is built on the same searches you can write
   yourself. The rest of this lab writes them.

## Task 2 — Index sizes and what they cost

6. List the course indexes with their size and event count:

   ```
   | rest /services/data/indexes
   | search title IN (web, security, sales, network, apps)
   | fields title, currentDBSizeMB, totalEventCount, maxTotalDataSizeMB, frozenTimePeriodInSecs
   | sort - currentDBSizeMB
   ```

   Largest index ________  its size ________

7. `frozenTimePeriodInSecs` is the retention setting — how long before data
   is removed. Convert it to something readable:

   ```
   | rest /services/data/indexes
   | search title IN (web, security, sales, network, apps)
   | eval retention_days = round(frozenTimePeriodInSecs/86400)
   | table title, currentDBSizeMB, retention_days
   ```

   What is the default retention, in years? ________

8. Look at how an index is physically laid out:

   ```
   | dbinspect index=web
   | stats count as buckets, sum(sizeOnDiskMB) as mb, min(startEpoch) as oldest
   ```

9. Why does Splunk split an index into buckets rather than one large file?
   ______________________

## Task 3 — Licence usage

10. Licence consumption is measured on raw bytes indexed per day:

    ```
    index=_internal source=*license_usage.log type=Usage
    | stats sum(b) as bytes by idx
    | eval MB = round(bytes/1048576, 2)
    | fields idx, MB
    | sort - MB
    ```

11. Total it, and compare against a notional 500 MB/day developer licence:

    ```
    index=_internal source=*license_usage.log type=Usage
    | stats sum(b) as bytes
    | eval MB = round(bytes/1048576, 2),
           pct_of_500MB = round(MB/500*100, 1)
    ```

12. Which index would you look at first if you needed to cut licence usage,
    and what would you check before deleting anything?
    ______________________

## Task 4 — Finding slow searches

13. Splunk audits every search that runs:

    ```
    index=_audit action=search info=completed
    | stats count as searches,
            avg(total_run_time) as avg_seconds,
            max(total_run_time) as slowest
    | eval avg_seconds = round(avg_seconds, 3)
    ```

14. Break it down by who ran them:

    ```
    index=_audit action=search info=completed total_run_time>0
    | stats count as searches, max(total_run_time) as slowest by user
    | sort - slowest
    ```

15. Most of those are yours, from Labs 1 to 15. Find your own worst one and
    look at what it was:

    ```
    index=_audit action=search info=completed total_run_time>1
    | table _time, user, total_run_time, search
    | sort - total_run_time
    | head 5
    ```

16. Does the slowest search match what you would have predicted from Lab 1?
    ______________________

## Task 5 — Troubleshooting with _internal

17. Splunk's own log is an index like any other:

    ```
    index=_internal log_level=ERROR
    | stats count by component
    | sort - count
    ```

18. Pick the busiest component and read the actual messages:

    ```
    index=_internal log_level=ERROR
    | stats count, values(message) as messages by component
    | sort - count
    | head 3
    ```

19. Check indexing throughput over time, which is the first thing to look at
    when ingestion seems stalled:

    ```
    index=_internal source=*metrics.log group=per_index_thruput
    | timechart span=1h sum(kb) as kb by series
    ```

20. You have now answered "is it slow, and where?" three different ways —
    the Monitoring Console, `_audit`, and `_internal`. Which would you reach
    for first, and why? ______________________

21. Save your favourite of these as **L16S1**.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 7** — About 6 years. `frozenTimePeriodInSecs` defaults to 188697600,
which is 2,184 days. Nothing in the class container will ever reach it, but
on a production index it is the setting that decides how much disk you need.

**Step 9** — Buckets let Splunk answer a time-bounded search by opening only
the buckets whose time range overlaps it, and they let old data age out by
deleting whole directories rather than rewriting a file. It is also why
`scanCount` in Lab 1 responded so strongly to narrowing the time range.

**Step 12** — Whichever has the most MB, which on the class data is `network`
or `sales`. Before deleting anything: check who searches it and how often
(`_audit` will tell you), check whether retention is already doing the job,
and check whether the volume is one noisy sourcetype rather than the index as
a whole. Licence pressure is almost always one source, not everything.

**Step 16** — Probably not. The searches you *expected* to be slow — the
leading wildcard in Lab 1, `transaction` in Lab 5 — are fractions of a second
on this data. The slowest will more likely be something touching `_internal`,
which is far larger than the course indexes. That is the lesson: measure on
the data you have, not the data you imagine.

**Step 20** — The Monitoring Console first, because it is already built and
shows all three dimensions at once. Drop to `_audit` when the question is
about a specific search or user, and `_internal` when the question is about
Splunk itself rather than the work it was asked to do.

</details>
