# Lab 13 — Subsearches

**Module 15 · Subsearches**

A subsearch runs first and hands its results to the search around it. That one
sentence explains both what makes them useful and every way they go wrong.

## Task 1 — Filtering by a list you do not know in advance

**Scenario:** support wants the successful purchases made by customers who
*also* hit a server error somewhere in the same period. You cannot write that
client list by hand — it changes every day.

1. First find the clients who saw a server error, over **Last 30 days**.

   ```
   index=web sourcetype=access_combined status>=500
   | fields clientip
   | dedup clientip
   ```

   How many addresses? ________

2. Now use that as a subsearch. Note the square brackets, and that the inner
   search carries its own `search` keyword.

   ```
   index=web sourcetype=access_combined action=purchase status=200
       [search index=web sourcetype=access_combined status>=500
        | fields clientip
        | dedup clientip]
   | stats count by clientip
   ```

3. Open **Job > Inspect Job** and read the `search` property near the top.
   Splunk shows you the search it actually ran.

   What has the subsearch been replaced by? ______________________

4. That is the whole mechanism: the subsearch runs, its results are turned
   into `field=value` terms joined by `OR`, and those are spliced into the
   outer search. Everything that follows is a consequence of it.

5. Why are `fields` and `dedup` in the subsearch rather than left out?
   ______________________

6. Save as **L13S1**.

## Task 2 — Exclusion with NOT

**Scenario:** security wants accounts that have *only ever* failed to log in —
no successes at all. That is not a filter you can express directly.

7. Over **Last 30 days**, find the failures.

   ```
   index=security sourcetype=linux_secure vendor_action=Failed
   | stats count by user
   ```

   Roughly how many accounts? ________

8. Now subtract every account that has ever succeeded.

   ```
   index=security sourcetype=linux_secure vendor_action=Failed
       NOT [search index=security sourcetype=linux_secure vendor_action=Accepted
            | fields user
            | dedup user]
   | stats count by user
   | sort - count
   ```

9. Look at what comes back. Do you recognise the accounts?
   ______________________

10. This is the same population you tagged in Lab 9, found a completely
    different way. Which method would you put in a scheduled alert, and why?
    ______________________

11. Save as **L13S2**.

## Task 3 — return and format

12. `return` gives you explicit control over what the subsearch emits.

    ```
    index=web sourcetype=access_combined
        [search index=web sourcetype=access_combined status=503
         | dedup productId
         | return 5 productId]
    | stats count by productId
    ```

13. Replace `return 5 productId` with `fields productId` and compare the
    result. Does anything change? ______________________

14. Now inspect the job for each version and compare the rewritten `search`
    property. `return` emits bare terms; `fields` emits `field=value` pairs.
    When would that difference matter? ______________________

15. Save as **L13S3**.

## Task 4 — The limits, and why they bite quietly

A subsearch stops at **10,000 results** and **60 seconds** by default. When it
hits either, it does not fail. It returns what it has, and the outer search
runs against a truncated list.

16. Run a deliberately broad subsearch.

    ```
    index=web sourcetype=access_combined
        [search index=web sourcetype=access_combined
         | fields clientip]
    | stats count
    ```

17. Check the Job Inspector for a message about the subsearch being
    finalised. Did Splunk warn you anywhere you would have noticed?
    ______________________

18. Fix it properly — narrow the subsearch and cap it.

    ```
    index=web sourcetype=access_combined
        [search index=web sourcetype=access_combined status>=500
         | fields clientip
         | dedup clientip
         | head 100]
    | stats count
    ```

19. Save as **L13S4**.

## Task 5 — When not to reach for one

20. For each of these, decide whether a subsearch is the right tool, and if
    not, what is:

    | Need | Subsearch? | If not, what |
    | ---- | ---------- | ------------ |
    | Filter by a small, changing list of IDs | | |
    | Enrich every event with a product name | | |
    | Correlate two sources field by field | | |
    | Filter by a list of 50,000 accounts | | |

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 3** — The bracketed subsearch is gone, replaced by a long
`( clientip="x" OR clientip="y" OR ... )` expression. Splunk runs the inner
search, converts the results to search terms, and rewrites the outer search
around them.

**Step 5** — Without `fields`, every field the inner events carry becomes part
of the generated expression, which is both enormous and wrong — you would be
matching on `status`, `bytes` and everything else as well. Without `dedup`,
the same address is repeated for every error it had. Both are about keeping
the generated expression small and correct, not about tidiness.

**Step 9** — The five privileged accounts: `administrator`, `sapadmin`,
`sysadmin`, `admin`, `itmadmin`. No real person's account appears, because
real accounts eventually succeed. An account with failures and no successes
is either an attack or a broken service, and both are worth knowing about.

**Step 10** — The tag, every time. The subsearch is the right tool for
*discovering* the pattern once; it re-derives the whole account list on every
run, and silently truncates at 10,000. A tag resolves to a fixed list the
index can look up directly. Discover with a subsearch, then encode what you
found.

**Step 13** — The results are the same here. The difference is in how the
terms are generated, which step 14 asks you to look at.

**Step 14** — `fields productId` produces `productId="HV-..." OR ...`, scoped
to that field. `return 5 productId` produces the same thing, but `return`
also offers `$field` syntax to emit bare values with no field name, which
matters when the outer search needs a raw term rather than a field match.

**Step 17** — Only if you go looking. The job log carries
`Subsearch produced 10000 results, truncating to maxout`, and the Job
Inspector shows it, but the search returns successfully and the results look
entirely plausible. This is the single most dangerous thing about subsearches: the
failure mode is a quietly incomplete answer, not an error.

**Step 20** —

| Need | Subsearch? | If not, what |
| ---- | ---------- | ------------ |
| Filter by a small, changing list of IDs | Yes | — |
| Enrich every event with a product name | No | A lookup |
| Correlate two sources field by field | No | `stats` by the shared field, or `join` |
| Filter by a list of 50,000 accounts | No | A lookup, or `inputlookup` in the subsearch |

</details>
