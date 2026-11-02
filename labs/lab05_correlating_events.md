# Lab 5 — Correlating Events

**Module 6 · Correlating Events**

## Task 1 — Group store traffic into sessions

1. Over **Last 24 hours**, list store events with the fields that matter.

   ```
   index=web sourcetype=access_combined
   | table _time, clientip, JSESSIONID, action
   ```

2. Keep only events that carry an action.

   ```
   index=web sourcetype=access_combined action=*
   ```

3. Remove the `table` command and group the events into sessions.

   ```
   | transaction JSESSIONID
   ```

4. Display the result as a table of `JSESSIONID`, `clientip` and `action`.

5. The `action` column lists each value once, alphabetically, rather than in
   the order they happened. Why? ______________________

6. Keep only sessions that contain a purchase.

   ```
   | search action=purchase
   ```

   > The `search` must come *after* `transaction`. Put it before and you
   > remove the view and cart events that make up the rest of the session.

7. Save as **L5S1**.

## Task 2 — Session length and event count

8. Re-run L5S1 in **Verbose** mode and open the **Events** tab. Note the two
   fields `transaction` added: `duration` and `eventcount`.

9. Back in **Smart** mode, add them to your table after `clientip`.

10. Convert duration to minutes, to one decimal place.

    ```
    | eval durationMinutes = round(duration/60, 1)
    ```

11. Keep only sessions longer than a minute, and display `JSESSIONID`,
    `clientip`, `action`, `durationMinutes` and `eventcount` in that order.

12. Save as **L5S2**.

## Task 3 — Cart to checkout

13. Over **Last 24 hours**, group store events by `clientip` this time, and
    keep only the journeys that begin with a cart addition and end with a
    purchase.

    ```
    index=web sourcetype=access_combined
    | transaction clientip
        startswith=(action="addtocart")
        endswith=(action="purchase")
        maxspan=30m maxpause=10m
    ```

14. Table `clientip`, `JSESSIONID`, `product_name`, `action`, `duration` and
    `eventcount`.

15. Remove `maxspan` and `maxpause` and re-run. What happens to the longest
    `duration`, and why is that answer wrong? ______________________

16. Save the constrained version as **L5S3**.

## Task 4 — The same answer with stats

17. Answer Task 1's question again without `transaction`.

    ```
    index=web sourcetype=access_combined action=*
    | stats range(_time) as duration,
            count as eventcount,
            values(action) as actions,
            dc(clientip) as ips
            by JSESSIONID
    | where isnotnull(mvfind(actions, "purchase"))
    ```

18. Compare the run time of this against L5S1 in the Job Inspector.

    | Search | Time |
    | ------ | ---- |
    | L5S1 (`transaction`) | |
    | Step 17 (`stats`) | |

19. Which is faster, and by roughly what factor? ______________________

20. Name one thing `transaction` gave you here that `stats` did not.
    ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 5** — `transaction` collapses multi-valued fields to their distinct
values and sorts them. If you need the order, keep `_time` and the raw events,
or use `list()` with `stats`, which preserves input order.

**Step 15** — Duration balloons, because one address that visited on Monday
and again on Friday becomes a single transaction lasting days. The constraints
are what make a "session" mean anything.

**Step 19** — `stats` is typically several times faster, and the gap widens
with data volume. `transaction` holds groups in memory and has a configured
cap; past it, groups are silently dropped.

**Step 20** — `transaction` gave you the member events themselves in order,
and the `startswith`/`endswith` framing. `stats` gives you aggregates about
each group but not the events, and cannot express "begins with X".

</details>
