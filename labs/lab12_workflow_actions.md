# Lab 12 — Creating and Using Workflow Actions

**Module 12 · Creating and Using Workflow Actions**

**Scenario:** analysts are tracking repeated login attempts from outside
addresses and need to act on an address without leaving the event.

## Before you start

Two of the three actions target a web service. So the lab works with no
internet access, this repository ships a local one. Start it now and leave it
running:

```bash
python3 tools/ip_lookup_server.py
```

It serves on `http://127.0.0.1:8888` and needs nothing beyond the Python
standard library.

> Link actions open in *your own browser*, not inside Splunk. `127.0.0.1`
> therefore means your machine, even when Splunk runs in a container.

## Task 1 — A GET action

1. Go to **Settings > Fields > Workflow actions** and click
   **New Workflow Action**.

2. Configure it:

   | Field | Value |
   | ----- | ----- |
   | Destination app | `splunk_intadv` |
   | Name | `lookup_src_ip` |
   | Label | `Look up IP: $src_ip$` |
   | Apply only to the following fields | `src_ip` |
   | Show action in | Both |
   | Action type | link |
   | URI | `http://127.0.0.1:8888/whois?ip=$src_ip$` |
   | Open link in | New window |
   | Link method | get |

3. Save.

4. Return to the class app and search over **Last 24 hours**:

   ```
   index=security sourcetype=linux_secure src_ip=*
   ```

   Refresh the browser if the action does not appear.

5. Expand an event with an `src_ip`, click **Event Actions**, and choose
   **Look up IP: {address}**. A window opens with a registration record.

6. Notice the Label in the menu shows the actual address, not `$src_ip$`. What
   does that tell you about when substitution happens? ______________________

## Task 2 — A POST action

**Scenario:** having identified an address, analysts should submit it to the
abuse-reporting system rather than copying it by hand.

7. Create another workflow action:

   | Field | Value |
   | ----- | ----- |
   | Destination app | `splunk_intadv` |
   | Name | `report_abuse_ip` |
   | Label | `Report IP: $src_ip$` |
   | Apply only to the following fields | `src_ip` |
   | Show action in | Both |
   | Action type | link |
   | URI | `http://127.0.0.1:8888/report` |
   | Open link in | New window |
   | Link method | **post** |

8. A **Post arguments** section appears as soon as you choose `post`. Add four:

   | Key | Value |
   | --- | ----- |
   | `src_ip` | `$src_ip$` |
   | `user` | `$user$` |
   | `sourcetype` | `$sourcetype$` |
   | `reported_by` | `splunk_class` |

9. Why does the Post arguments section not appear for a GET action?
   ______________________

10. Save, return to the class app, re-run the step 4 search and fire the new
    action from an event.

11. The page echoes what it received. Confirm the first three carry values
    from the event and `reported_by` is the literal string.

12. One field is likely to come back empty. Which, and why?
    ______________________

13. Check the terminal running the server — each action logs a `POST /report`
    line. If nothing appears there, the action never fired; recheck the URI.

## Task 3 — A search action

14. Create a third workflow action:

    | Field | Value |
    | ----- | ----- |
    | Destination app | `splunk_intadv` |
    | Name | `search_failures_by_ip` |
    | Label | `Failed logins from $src_ip$` |
    | Apply only to the following fields | `src_ip` |
    | Action type | **search** |
    | Search string | `index=security sourcetype=linux_secure "Failed password" src_ip=$src_ip$` |
    | Run in app | `splunk_intadv` |
    | Run search in | New window |
    | Use the same time range | ticked |

15. Save, re-run the step 4 search, and fire it from an event.

16. Stop the local server with Ctrl-C and try all three actions again. Which
    still works, and why? ______________________

## Task 4 — Scoping

17. Edit `lookup_src_ip` and clear **Apply only to the following fields**.
    Save, and run a search against the web index instead:

    ```
    index=web sourcetype=access_combined
    ```

18. Open an event's Event Actions menu. What has gone wrong?
    ______________________

19. Put the field scope back.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 6** — Substitution happens when the menu is built, per event, not when
the action is saved. That is why the same object produces a different label on
every event.

**Step 9** — A GET request has no body to put arguments in. Its parameters
must be in the URL, which is why Task 1 builds `$src_ip$` into the URI string
itself.

**Step 12** — `user`. The `linux_secure` events carrying an `src_ip` do not
all resolve a user. An unmatched `$field$` posts as empty rather than failing,
which is worth knowing before you build an action on a sometimes-present field.

**Step 16** — Only the search action. It runs SPL in the same Splunk instance
and never leaves the machine, so it has no external dependency at all.

**Step 18** — The action now appears on every event in every search, including
events with no `src_ip` at all, where it produces a broken lookup. Scoping is
not cosmetic — an action offered everywhere is one people learn to ignore.

</details>
