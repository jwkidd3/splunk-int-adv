# Lab 7 — Working with Knowledge Objects

**Module 7 · Introduction to Knowledge Objects**

No new SPL. This lab is about the machinery every later lab depends on.

## Questions first

Answer before you start.

1. Which category does each object belong to — *data interpretation*,
   *data classification*, *data enrichment*, *normalization* or *datasets*?

   | Object | Category |
   | ------ | -------- |
   | A field alias | |
   | An event type | |
   | A lookup | |
   | A field extraction | |
   | A data model | |
   | A tag | |
   | A workflow action | |

2. You save a report and leave permissions alone. Who can see it? ________

3. Logged in with the **power** role, which sharing option is greyed out?
   ________

## Task 1 — Inventory what exists

4. Log in and switch to the **CLASS: Intermediate** app.

5. Open **Settings**. Everything under the **KNOWLEDGE** heading is an object
   manager.

   > Older material calls this "Settings > Knowledge". There is no menu item
   > with that name — it is the column heading above the group of links.

6. Click **All configurations**. Set **App context** to *CLASS: Intermediate*,
   then to *All*.

   Objects in the class app ________  In all apps ________

7. Set **Owner** to your own user name. These are the reports you saved in
   Labs 2 through 5.

## Task 2 — Naming conventions

8. Over **Last 7 days**, find server errors in the store.

   ```
   index=web sourcetype=access_combined status>=500
   | stats count by status, host
   ```

9. Save it twice: once as **`OPS_Report_WebServerErrors`**, once as **`L7S1`**.

10. In **Settings > Searches, reports, and alerts**, type `OPS_` in the filter.

    Which name tells a colleague what the object is without opening it?
    ______________________

11. Now imagine three hundred objects in this list. Which name is findable?
    ______________________

## Task 3 — Permissions

12. Find `OPS_Report_WebServerErrors` and click **Permissions**.

13. Note that **Display For** is **Owner** — the default for everything new.

14. Change it to **App**. The roles table activates.

    Roles with read ______________  Roles with write ______________

15. Try to click **All Apps**. What happens, and why? ______________________

16. Save.

## Task 4 — Why permissions matter in practice

17. In **All configurations**, set Owner and App context to *All*, and filter
    on `products`.

    You should find the lookup table file, the lookup definition, and the
    automatic lookup bound to `access_combined`.

18. Open **Permissions** on the automatic lookup.

    Shared to the app, or globally? ______________________

19. Suppose it had been left Private. Run this and predict what a *different*
    user would see:

    ```
    index=web sourcetype=access_combined action=purchase
    | stats count by product_name
    ```

    ______________________

## Task 5 — Clean up

20. Delete `L7S1`. Keep `OPS_Report_WebServerErrors`.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Question 1** — Field alias: normalization. Event type: data classification.
Lookup: data enrichment. Field extraction: data interpretation. Data model:
datasets. Tag: normalization. Workflow action: data enrichment.

**Question 2** — Only you. New objects default to Display For: Owner.

**Question 3** — All Apps. Only admin can promote an object to global scope.

**Step 14** — Every listed role gains read. Write stays with admin and the
owner until granted explicitly.

**Step 15** — The button is greyed out for the power role. If yours is not,
you are logged in as admin.

**Step 19** — The search runs without error and returns a single row with a
null `product_name` and the total count, because the enrichment never
happened. No error, no warning — just a quietly wrong answer. This is why a
privately scoped lookup is worse than a broken one.

</details>
