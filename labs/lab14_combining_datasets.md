# Lab 14 — Combining Datasets

**Module 16 · Combining Datasets**

Four ways to bring two sources together — `join`, `append`, `union` and the
one you should usually reach for instead.

## Task 1 — join on a shared field

**Scenario:** the store logs record which product was bought. The order
system records what it was worth. Nobody has both.

1. Look at each side separately, over **Last 30 days**.

   ```
   index=web sourcetype=access_combined action=purchase
   | stats count as checkouts by productId
   ```

   ```
   index=sales sourcetype=sales_entries
   | stats sum(total) as revenue by productId
   ```

2. Both carry `productId`. Join on it.

   ```
   index=web sourcetype=access_combined action=purchase
   | join productId
       [search index=sales sourcetype=sales_entries
        | stats sum(total) as revenue by productId]
   | stats count as checkouts, values(revenue) as revenue by productId
   ```

3. How many rows come back, and how many products does the catalogue have?
   ______________________

4. Save as **L14S1**.

## Task 2 — Join types, and joining fields with different names

**Scenario:** security wants failed logins annotated with the department the
account belongs to. The firewall data knows departments. It calls the account
`Username`, not `user`.

5. A join needs the field to have the same name on both sides. Rename inside
   the subsearch.

   ```
   index=security sourcetype=linux_secure vendor_action=Failed
   | join type=left user
       [search index=network sourcetype=firewall
        | rename Username as user
        | stats values(Department) as dept by user]
   | stats count by user, dept
   | sort - count
   ```

6. Some rows have no `dept`. What does `type=left` do that the default does
   not? ______________________

7. Change `type=left` to the default by removing it, and compare the row
   count. Which accounts disappeared, and is that what you want here?
   ______________________

8. Save as **L14S2**.

> **The limit that matters.** `join` has the same 10,000-row subsearch ceiling
> as Lab 13, and the same silent truncation. On anything large this is the
> reason to use `stats` instead, which Task 5 covers.

## Task 3 — append

`join` matches rows together side by side. `append` puts one result set
*underneath* another.

9. Count server errors on the store and on the proxy, and stack them.

   ```
   index=web sourcetype=access_combined status>=500
   | stats count as errors by host
   | append
       [search index=network sourcetype=web_proxy sc_http_status>=500
        | stats count as errors by s_hostname]
   ```

10. The result has two columns, `host` and `s_hostname`, each half empty. Fix
    it by normalising the field name in the appended search.

    ```
    | append
        [search index=network sourcetype=web_proxy sc_http_status>=500
         | rename s_hostname as host
         | stats count as errors by host]
    ```

11. Save as **L14S3**.

## Task 4 — union

12. `union` does the same job more cleanly, and runs both sides in parallel.

    ```
    | union
        [search index=web sourcetype=access_combined status>=500
         | stats count as errors by sourcetype]
        [search index=network sourcetype=web_proxy sc_http_status>=500
         | stats count as errors by sourcetype]
    ```

13. Note the leading pipe. `union` is a generating command, so it must come
    first. What happens if you drop it? ______________________

14. Save as **L14S4**.

## Task 5 — The one you should usually use

15. Answer Task 1's question again without `join`.

    ```
    (index=web sourcetype=access_combined action=purchase)
        OR (index=sales sourcetype=sales_entries)
    | stats count(eval(sourcetype=="access_combined")) as checkouts,
            sum(total) as revenue
            by productId
    ```

    > Those parentheses are load-bearing. `AND` binds tighter than `OR` in
    > SPL, so without them Splunk reads this as
    > `index=web AND sourcetype=access_combined AND (action=purchase OR
    > index=sales) AND sourcetype=sales_entries` — two sourcetypes at once,
    > which nothing satisfies. Drop them and run it: zero results, no error.

16. Compare the two in the Job Inspector.

    | Search | Elapsed | scanCount |
    | ------ | ------- | --------- |
    | L14S1 (`join`) | | |
    | Step 15 (`stats`) | | |

17. Which reads more clearly to you? Which would you trust on a year of data?
    ______________________

18. Save as **L14S5**.

## Task 6 — Choosing

19. Fill this in from what you have seen:

    | Situation | Reach for |
    | --------- | --------- |
    | Add a product name to every event | |
    | Two sources sharing a key, both large | |
    | Two sources sharing a key, one tiny | |
    | Stack two result sets into one table | |
    | Same question asked of several indexes | |

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 3** — Fourteen, matching the catalogue exactly, because every product
appears in both sources. Real joins rarely land that cleanly, which is what
Task 2 is about.

**Step 6** — The default is an inner join: a row survives only if the field
matches on both sides. `type=left` keeps every row from the left-hand search
whether or not the subsearch had a match, leaving the added fields empty when
it did not.

**Step 7** — Accounts with no firewall activity vanish — including the five
privileged accounts, which are exactly the ones security cares about. An
inner join here would quietly delete the most important rows. This is the
practical reason to think about join type rather than accept the default.

**Step 13** — Without the leading pipe Splunk treats `union` as a search term
and looks for events containing the word, which returns nothing. Generating
commands always come first.

**Step 17** — Both return the same answer. `stats` streams, has no 10,000-row
ceiling and no silent truncation; `join` holds the subsearch result in memory
and discards rows past the limit without telling you. The `join` reads more
naturally if you come from SQL, and that familiarity is most of why it gets
used where `stats` would be safer.

**Step 19** —

| Situation | Reach for |
| --------- | --------- |
| Add a product name to every event | A lookup |
| Two sources sharing a key, both large | `stats` by the shared field |
| Two sources sharing a key, one tiny | `join`, or a lookup |
| Stack two result sets into one table | `append` or `union` |
| Same question asked of several indexes | `union` |

</details>
