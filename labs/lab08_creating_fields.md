# Lab 8 — Creating and Managing Fields

**Module 8 · Creating and Managing Fields**

Two extraction methods against two different log shapes.

## Task 1 — Regular expression extraction

**Scenario:** access to the Linux hosts needs monitoring, and the source
address and port are buried in the message text.

1. Over **Last 24 hours**, find authentication events mentioning a port.

   ```
   index=security sourcetype=linux_secure port
   ```

2. Expand an event that contains an IP address. Click **Event Actions >
   Extract Fields**.

3. Choose **Regular Expression** and click **Next**.

4. Highlight the IP address in the sample. Name the field `src` and click
   **Add Extraction**.

5. Scroll to the Preview and check the values. Then highlight the port number,
   name it `port`, add that extraction too, and click **Next**.

   > If Splunk cannot generate one regex covering both fields, build them as
   > two separate extractions. This is common and not a failure on your part.

6. In **Validate**, review the `src` values. Filter out anything that is not
   an address by clicking the **x** beside a bad sample value.

7. Click **Next**, review the extraction name, and **Finish**.

8. Wait about a minute, then run:

   ```
   index=security sourcetype=linux_secure
   | top limit=10 port by src
   ```

   > Knowledge objects take a moment to become available. A brand-new field
   > returning nothing usually means you were too quick, not that you were wrong.

9. Compare your `src` against the `src_ip` the sourcetype already provides.
   Did you need to extract it at all? ______________________

## Task 2 — Delimiter extraction

**Scenario:** the TrailMate mobile app is in beta. Its telemetry has no
headers and nothing is extracted automatically.

10. Over **Last 30 days**, look at the beta data.

    ```
    index=apps sourcetype=trailmate_beta
    ```

    A record looks like this:

    ```
    2026-09-29T13:15:37+0000,201.79.135.199,2.0.0-beta2,route_saved,user:nils.yilmaz@example.test DeviceName:Pathfinder-55 action:completed role:Trial
    ```

11. In the Fields sidebar, under Interesting Fields, click **+ Extract New Fields**.

12. Click the first event to select it as the sample, then **Next**.

13. Choose **Delimiters**, then **Next**, then **Comma**.

14. Rename the fields in order:

    | Default | Rename to |
    | ------- | --------- |
    | field1 | `event_time` |
    | field2 | `src` |
    | field3 | `version` |
    | field4 | `event_kind` |

15. Leave `field5` alone — you will handle it with a regex. Click **Next**,
    name the extraction `trailmate_columns`, and **Finish**.

16. Why can the delimiter method not finish the job on this record?
    ______________________

## Task 3 — Regex over the remainder

17. Run the same search again and start a new **Regular Expression**
    extraction on the trailing segment, pulling out:

    - `user`
    - `DeviceName`
    - `action`
    - `role`

18. Before validating, click **Non-Matches**. Any events shown here are
    excluded by your regex.

19. Hover an excluded event and click **+ Add sample event**. Highlight the
    values, assign them to the existing field names, and add the extractions.

20. Repeat until Non-Matches is empty or the remainder is genuinely irrelevant.

21. Click **Next**, validate, **Next**, accept the name and **Finish**.

22. Wait a minute, then confirm all four fields appear:

    ```
    index=apps sourcetype=trailmate_beta
    | stats count by role, action
    ```

23. Which step would you have skipped if you were in a hurry, and what would
    it have cost you? ______________________

## Task 4 — Manage what you built

24. Go to **Settings > Fields > Field extractions** and find your three
    extractions.

25. Open **Settings > Fields > Field transformations**. What is stored here
    that is not in the extraction itself? ______________________

26. Set permissions on the beta extractions so the whole app can use them.

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 9** — No. `linux_secure` is a pretrained sourcetype and already
supplies `src_ip` and `src_port`. The exercise is worth doing to learn the
tool, but in production you would check the Fields sidebar first and save
yourself a knowledge object that duplicates a built-in one — and that someone
will later have to maintain.

**Step 16** — The fifth comma-separated value is itself a set of `key:value`
pairs. Delimiters can split the record into five columns, but cannot reach
inside one of them. Real log formats mix structures like this constantly.

**Step 23** — Non-Matches. Skipping it gives you an extraction built from one
event that silently covers a fraction of the data. The search returns results,
so nothing looks broken — the numbers are just quietly incomplete.

**Step 25** — The regular expression itself, as a reusable transform. The
extraction binds a transform to a sourcetype; the transform holds the pattern.
That separation lets one pattern serve several sourcetypes.

</details>
