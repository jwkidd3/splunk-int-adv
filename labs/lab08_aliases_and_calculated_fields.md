# Lab 8 — Field Aliases and Calculated Fields

**Module 9 · Creating Field Aliases and Calculated Fields**

## Task 1 — Normalize three username fields

**Scenario:** IT Ops reports on employee access, but every source calls the
user something different.

1. Over **Last 7 days**, look at proxy traffic and note the `cs_username`
   values.

   ```
   index=network sourcetype=web_proxy
   ```

2. Look at firewall traffic and note the `Username` values.

   ```
   index=network sourcetype=firewall
   ```

3. Confirm the problem — this returns nothing useful:

   ```
   index=network user=* | stats count by sourcetype
   ```

4. Go to **Settings > Fields > Field aliases** and create:

   | Field | Value |
   | ----- | ----- |
   | Destination app | `splunk_intadv` |
   | Name | `web_proxy_aliases` |
   | Apply to | sourcetype |
   | Named | `web_proxy` |
   | Field aliases | `cs_username` = `user` |

5. Create a second alias for the firewall:

   | Field | Value |
   | ----- | ----- |
   | Name | `firewall_aliases` |
   | Apply to | sourcetype |
   | Named | `firewall` |
   | Field aliases | `Username` = `user` |

6. Return to the **CLASS: Intermediate** app, wait a moment, and re-run step 3.

   Do both sourcetypes now appear? ________

7. Check that `cs_username` still works as well. Did the alias rename the
   field or add to it? ______________________

## Task 2 — A calculated field

**Scenario:** bandwidth is reported in bytes; the team wants megabytes.

8. Over **Last 7 days**, note the `sc_bytes` field on proxy events.

9. Go to **Settings > Fields > Calculated fields** and create:

   | Field | Value |
   | ----- | ----- |
   | Destination app | `splunk_intadv` |
   | Apply to | sourcetype |
   | Named | `web_proxy` |
   | Name | `sc_megabytes` |
   | Eval expression | `sc_bytes/1024/1024` |

10. Back in the class app, report bandwidth by user:

    ```
    index=network sourcetype=web_proxy
    | stats sum(sc_megabytes) as MB by user
    | eval MB = round(MB, 2)
    | sort - MB
    ```

11. Note that this search uses *both* objects you just made — the alias for
    `user` and the calculated field for `sc_megabytes`.

12. Why can the calculated field reference `user` but the alias could not have
    referenced `sc_megabytes`? ______________________

## Task 3 — Order of operations

13. Try creating an alias on `web_proxy` mapping `sc_megabytes` to `mb`. Run a
    search for `mb=*`.

    What happens, and why? ______________________

14. Delete that alias.

## Supplemental

15. Create two aliases on `access_combined`: `action` to `http_action` and
    `method` to `http_method`.

16. Verify:

    ```
    index=web sourcetype=access_combined http_method=POST http_action=purchase
    | stats count by host
    ```

17. These two names are not arbitrary. Where have you seen them before, and
    where will you see them again? ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 6** — Yes. One search now spans both sourcetypes with no OR and no
knowledge of the original field names.

**Step 7** — It adds. An alias creates a second name; the original keeps
working, so existing searches do not break.

**Step 12** — Search-time order of operations. Aliases are applied at step 3,
calculated fields at step 4. A calculated field can see an alias because the
alias already ran; an alias cannot see a calculated field because it has not
run yet.

**Step 13** — `mb=*` returns nothing. The alias is evaluated before the
calculated field exists, so there is nothing to alias. This accounts for most
"my alias does not work" reports.

**Step 17** — They are CIM field names, from the Web data model. Module 14
covers making your data CIM-compliant, and this is the mechanism it uses —
aliases plus tags, nothing new.

</details>
