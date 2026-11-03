# Lab 15 — Users, Roles and Capabilities

**Module 17 · Users, Roles and Capabilities**

Everything you have built so far has run as `admin`, which can do anything.
This lab is about what happens when it cannot.

> Most of this lab is UI work in **Settings > Access controls**. Splunk moves
> these screens between releases, so follow the intent rather than the exact
> wording if your version differs.

## Task 1 — What is already there

1. Look at the roles this instance ships with:

   ```
   | rest /services/authorization/roles
   | fields title, srchIndexesAllowed, srchIndexesDefault, imported_capabilities
   | sort title
   ```

2. Note the three that matter: `admin`, `power`, `user`.

   Which one are you logged in as? ________

3. Open **Settings > Access controls > Roles** and click **power**. Compare
   what you see against the search output.

4. Find `srchIndexesAllowed` for `user`. What can that role search by
   default? ______________________

5. Count the capabilities each role carries:

   ```
   | rest /services/authorization/roles
   | eval n = mvcount(capabilities)
   | table title, n
   | sort - n
   ```

   admin ________  power ________  user ________

## Task 2 — A role that can only see the store

**Scenario:** the merchandising team should see store traffic and nothing
else. Not security, not the firewall, not the proxy.

6. Go to **Settings > Access controls > Roles** and click **New Role**.

7. Name it `harborview_merch`.

8. Under **Inheritance**, tick `user`. A new role starts with nothing, and
   inheriting `user` gives it the basics without you listing them.

9. Under **Indexes**, set **Indexes searched by default** and **Indexes the
   role can search** to `web` only.

10. Leave capabilities alone for now. Save.

11. Verify what you built:

    ```
    | rest /services/authorization/roles
    | search title=harborview_merch
    | fields title, srchIndexesAllowed, imported_roles
    ```

## Task 3 — A user to test it with

12. Go to **Settings > Access controls > Users** and click **New User**.

13. Username `merch1`, set a password you will remember, and assign **only**
    the `harborview_merch` role. Remove `user` from the assigned list if it
    is added automatically — the role already inherits it.

14. Save.

15. Open a private browser window and sign in as `merch1`.

16. Run each of these and record what happens:

    | Search | Result |
    | ------ | ------ |
    | `index=web sourcetype=access_combined \| stats count` | |
    | `index=security sourcetype=linux_secure \| stats count` | |
    | `index=* \| stats count by index` | |

17. The security search returned no error — just no results. Why is that
    worse than an error, and what would you tell a user who reported it?
    ______________________

## Task 4 — Capabilities

A role's **indexes** decide what data it sees. Its **capabilities** decide
what it can do.

18. Back as `admin`, open `harborview_merch` and look at the capability list.
    Find `schedule_search`.

19. As `merch1`, try to save a report and schedule it. What stops you?
    ______________________

20. As `admin`, grant `schedule_search` to `harborview_merch` and save.

21. As `merch1`, try again. Does it work now? ________

22. Two capabilities worth knowing, and worth being careful with:

    | Capability | What it allows |
    | ---------- | -------------- |
    | `delete_by_keyword` | Running `\| delete`, which hides events from all searches |
    | `edit_own_objects` | Changing the permissions of objects you own |

    Neither is in `user` by default. Why not? ______________________

## Task 5 — Tidy up

23. Delete the `merch1` user.

24. Keep the `harborview_merch` role — Lab 16 looks at it again.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 2** — `admin`, unless your instructor set the class up differently.
Everything in Labs 1 to 14 has therefore run with no restrictions at all,
which is not how anyone's production Splunk is configured.

**Step 4** — `user` has no indexes allowed beyond the defaults, which on a
stock instance means it can search almost nothing until a role grants it
something. Splunk ships restrictive and expects you to open it up.

**Step 5** — Roughly 250 for admin, 100 for power, 40 for user on a current
release. The exact numbers move between versions; the ratio is the point.

**Step 16** — The store search works. The security search returns zero
results. `index=*` returns only `web`, because `index=*` means "every index
you are allowed to search", not "every index".

**Step 17** — Because it is indistinguishable from "there is no data". The
user cannot tell a permissions problem from an empty result, and will file a
bug against the data rather than ask for access. Tell them to run `index=*`
and compare the index list against what they expect — that is the quickest
way to spot a permissions boundary from the user's side.

**Step 19** — The Schedule option is absent or greyed out in the Save As
dialog. Splunk hides what you cannot do rather than letting you try and fail,
which is friendlier but makes a missing capability look like a missing
feature.

**Step 22** — `delete_by_keyword` hides data from everyone, cannot be undone
from the UI, and does not actually reclaim disk. `edit_own_objects` lets
someone widen the audience for their own objects, which quietly turns a
private report into a shared one. Both are safe to grant deliberately and
dangerous to grant by inheritance.

</details>
