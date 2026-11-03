# Lab 10 — Creating Tags and Event Types

**Module 10 · Creating Tags and Event Types**

## Task 1 — Tag the privileged accounts

**Scenario:** security wants to watch failed logins against any variation of
the admin account, without typing a five-way OR every time.

1. Over **Last 24 hours**, find failed logins for admin-like accounts.

   ```
   index=security sourcetype=linux_secure "Failed password" user=*admin*
   ```

   You should see five accounts: `admin`, `administrator`, `sysadmin`,
   `itmadmin`, `sapadmin`.

   > Note the leading wildcard. It works, and it is expensive — Lab 2 showed
   > why. Fixing that is the entire point of this task.

2. Expand an event, find the `user` row, click the Actions arrow and choose
   **Edit Tags**.

3. In **Tag(s)** type `privileged` and save.

4. Add the remaining four values. Quickest route: **Settings → Tags > List by
   tag name**, open `privileged`, and add them there rather than one event at
   a time.

5. Re-run the search and confirm the `tag` field appears. Add it to Selected
   Fields.

## Task 2 — Search by tag

6. Over **Last 7 days**, find failed logins by privileged accounts:

   ```
   index=security sourcetype=linux_secure "Failed password" tag=privileged
   ```

7. Compare this against the step 1 search in the Job Inspector.

   | Search | scanCount | Time |
   | ------ | --------- | ---- |
   | `user=*admin*` | | |
   | `tag=privileged` | | |

8. Is the tagged search faster, and does it return the same accounts?
   ______________________

9. A sixth admin account is created next month. What has to change for it to
   be included? ______________________

## Task 3 — An event type for server errors

**Scenario:** customers report checkout failures and employees report proxy
errors at the same time. IT Ops wants one name covering both.

10. Over **Last 7 days**, find server errors across the store and the proxy.

    ```
    (index=web sourcetype=access_combined status>=500)
    OR (index=network sourcetype=web_proxy sc_http_status>=500)
    ```

11. Choose **Save As** → **Event Type**. Name it `web_error`, leave Priority at
    **1**, and save.

12. Search for it:

    ```
    eventtype=web_error
    ```

13. Expand an event and add `eventtype` to Selected Fields.

14. How many sourcetypes does the event type reach? ________

15. Try adding `| stats count` to the event type's *definition* and saving.
    What happens, and why? ______________________

## Task 4 — Combining the two

16. Tag the event type itself. **Settings → Event types**, open `web_error`,
    and add the tag `error`.

17. Search `tag=error` and confirm it finds the same events.

18. You now have two ways to reach these events. When would tagging an event
    type be better than searching the event type by name?
    ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 7** — Run both over the same range first. Step 1 says Last 24 hours and step 6 says
Last 7 days, and comparing across two windows tells you nothing. Over
**Last 7 days** on the reference dataset:

| Search | scanCount | resultCount |
| ------ | --------- | ----------- |
| `user=*admin*` | 526 | 251 |
| `tag=privileged` | 251 | 251 |

Same five accounts, same 251 events. The wildcard makes Splunk read 526 events
and throw half of them away. The tag resolves to five exact `user` values it
can look up in the index, so every event it reads is one it keeps — which is
what `scanCount` equalling `resultCount` means.

**Step 8** — Yes, and the same five accounts. The tag resolves to an explicit
list of values the index can look up directly, so it reads only events it
will return; the leading wildcard has to read every candidate and filter
afterwards. On this data that is half the events rather than a tiny fraction —
the saving grows with how rare the tagged values are.

**Step 9** — Add the new value to the `privileged` tag. Nothing else — no
saved search, report or dashboard needs editing. That is the argument for
tags in one sentence.

**Step 14** — Two: `access_combined` and `web_proxy`. Depending on what apps
you have installed, Splunk may show additional built-in event types alongside
yours.

**Step 15** — It is rejected. An event type is a search *condition*, not a
search — no pipes, no subsearches. Aggregation belongs in the search that
uses the event type.

**Step 18** — When you want a family of conditions under one name. Tag
`web_error`, `db_error` and `auth_error` all as `error` and a single
`tag=error` covers all three, including ones added later. This is exactly how
the CIM composes its models.

</details>
