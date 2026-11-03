# Lab 13 — Creating Data Models

**Module 13 · Creating Data Models**

**Scenario:** the VP of Sales wants to answer her own questions about store
activity and has no intention of learning SPL.

> Build this in **Search & Reporting**, not the class app. Power users have
> read-only permissions on data models in most app contexts.

## Task 1 — The root event dataset

1. Go to **Settings > Data models** and click **New Data Model**.

   > Two models are already listed, `Harborview_Web` and
   > `Harborview_Authentication`. Those ship with the course and are what
   > Module 14 demonstrates `datamodel` and `tstats` against. Leave them
   > alone; you are building your own.

2. Title: `Store Activity`. Leave the auto-filled ID alone — it cannot be
   blank. Set App to **Search & Reporting**. Click **Create**.

3. Click **Add Dataset > Root Event**.

4. Dataset Name: `Web requests`

5. Constraints:

   ```
   index=web sourcetype=access_combined
   ```

6. Click **Preview** to confirm events come back, then save.

## Task 2 — Auto-extracted fields

7. With `Web requests` selected, click **Add Field > Auto-Extracted**.

8. Tick these and rename them for people who do not know the data:

   | Field | Rename to |
   | ----- | --------- |
   | `action` | action taken |
   | `bytes` | size |
   | `categoryId` | product category |
   | `clientip` | client IP |
   | `date_mday` | *(leave as is)* |
   | `productId` | product ID |
   | `product_name` | product name |
   | `status` | *(leave as is)* |

   > `date_mday` uses an underscore. There is no `date-mday`.

9. Save.

10. `product_name` and `categoryId` are not in the raw log — they come from the
    `products.csv` automatic lookup. Why do they show up in the
    Auto-Extracted list anyway? ______________________

## Task 3 — Child datasets

11. Click **Add Dataset > Child**.

12. Name: `Successful requests`. Additional Constraints: `status<400`.
    Preview, then save.

13. With `Successful requests` selected, add a child named `Purchases` with
    constraints `action=purchase productId=*`. Preview and save.

14. Select `Web requests` again and add a child named `Failed requests` with
    constraints `status>=400`. Preview and save.

15. Under `Failed requests`, add a child named `Removals` with constraints
    `action=remove`. Preview and save.

16. Try giving `Purchases` a constraint of `status>=500`. Preview it. What
    happens, and what does that tell you about how children inherit?
    ______________________

17. Undo that change.

## Task 4 — Test with Pivot

18. Click **Pivot** in the top right, and select `Web requests`.

19. Set the filter to **Last 7 days**.

20. Split Rows by **action taken**, click Add To Table.

21. Split Columns by **date_mday**, click Add To Table.

22. Click the search icon to see the SPL Pivot generated for you. Read it —
    this is a good way to learn `tstats` syntax later.

## Task 5 — An eval field

23. Click **Edit Dataset** and make sure `Web requests` is selected.

24. From **Add Field**, choose **Eval Expression**.

25. Expression:

    ```
    strftime(_time, "%m-%d %A")
    ```

26. Field Name and Display Name: `day`. Preview, then save.

## Task 6 — Verify with a dashboard

27. Click **Pivot**, select `Web requests`, filter to **Last 7 days**.

28. Split Rows by **action taken**, Split Columns by **day**.

29. **Save As > Dashboard Panel**. Dashboard Title `Weekly Store Activity`,
    Panel Title `Shopping cart activity by day`. Save and view.

## Task 7 — A lookup field

30. Return to **Settings > Data models** and select `Store Activity`.

31. With `Web requests` selected, click **Add Field > Lookup**.

32. Choose `http_status_lookup` from the Lookup Table list.

33. Input: **Field in Lookup** = `code`, **Field in Dataset** = `status`.

34. Output: tick `description`. Display Name: `status description`.

35. Preview — you should see a description column. Save.

## Task 8 — Verify the lookup

36. Click **Pivot**, select `Web requests`, filter to **Last 7 days**.

37. Split Rows by **status description**, then click **+** and add **status**
    as a second row split. This is a double row split, not a column split.

38. Split Columns by **day**.

39. **Save As > Dashboard Panel**, add it to the existing
    `Weekly Store Activity` dashboard as `Status summary`.

40. View the dashboard.

41. You could have produced the same table with a `lookup` command in a saved
    search. What does putting it in the data model buy you?
    ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 10** — Automatic lookups are applied at search time, before the data
model sees the event. By the time the model inspects what fields exist, the
lookup has already contributed them. This is the search-time order of
operations from Module 9, visible from the other side.

**Step 16** — Preview returns nothing. `Purchases` inherits `status<400` from
its parent, and `status>=500` cannot be true at the same time. Children only
ever narrow. If a child needs events the parent excludes, the hierarchy is
wrong.

**Step 41** — Everyone gets it, through Pivot, without writing SPL or knowing
the lookup exists. Change the definition once and every pivot, report and
dashboard built on the model updates. That is the whole argument for data
models in one sentence.

</details>
