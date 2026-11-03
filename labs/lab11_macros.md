# Lab 11 — Creating and Using Macros

**Module 11 · Creating and Using Macros**

**Scenario:** the VP of Sales wants ad-hoc totals for European retail sales,
converted into local currency, without learning SPL.

## Task 1 — Build a basic macro

1. Over **Last 30 days**, total retail sales by product for the European
   vendors.

   ```
   index=sales sourcetype=vendor_sales
     VendorCountry IN ("Germany", "France", "Italy")
   | stats sum(price) as USD by product_name
   | sort - USD
   ```

2. Format the total as currency.

   ```
   | eval USD = "$" + tostring(USD, "commas")
   ```

   > The dollar sign must be quoted. An unquoted `$` is a syntax error, and
   > the message you get back will not say so clearly.

3. Copy the whole search somewhere safe — you need it twice.

4. Go to **Settings → Advanced search → Search macros** and click
   **New Search Macro**.

5. Set Destination app to `splunk_intadv`, Name to `europe_sales`, and paste the
   search into **Definition**. Save.

## Task 2 — Use it

6. Back in the **CLASS: Intermediate** app, over **Last 30 days**, run:

   ```
   `europe_sales`
   ```

   > Those are backticks, not apostrophes. This is the single most common
   > macro mistake and the error message does not point at it.

7. Now pipe the macro into something else:

   ```
   `europe_sales` | head 5
   ```

   Why does this work, given the macro already ends in a `sort`?
   ______________________

## Task 3 — A macro with arguments

8. Run the full version, which converts to a second currency:

   ```
   index=sales sourcetype=vendor_sales
     VendorCountry IN ("Germany", "France", "Italy")
   | stats sum(price) as USD by product_name
   | eval euro = "€" . tostring(round(USD*0.92, 2), "commas"),
          USD  = "$" + tostring(USD, "commas")
   ```

9. You are going to turn the second half into a macro taking the currency
   name, symbol and rate.

10. Create a new macro named **`to_currency(3)`** in `splunk_intadv`.

11. Definition:

    ```
    stats sum(price) as USD by product_name
    | eval $currency$ = "$symbol$" . tostring(round(USD*$rate$, 2), "commas"),
           USD = "$" + tostring(USD, "commas")
    ```

12. In **Arguments**, type: `currency,symbol,rate`

    The order must match the order the definition uses them.

13. Save.

## Task 4 — Call it

14. Over **Last 30 days**:

    ```
    index=sales sourcetype=vendor_sales
      VendorCountry IN ("Germany", "France", "Italy")
    | `to_currency(euro,€,0.92)`
    ```

    > Copy the € from this document if you cannot type it.

15. Run it again for the United Kingdom, converting to pounds. You will need
    to change *both* the country filter and the macro arguments:

    ```
    index=sales sourcetype=vendor_sales VendorCountry="United Kingdom"
    | `to_currency(GBP,£,0.79)`
    ```

16. Note that the macro definition begins with `stats`, but the call site
    supplies the leading pipe. Why is that a better design than putting the
    pipe inside the macro? ______________________

## Task 5 — Validate the arguments

17. Open `to_currency(3)` from **Settings → Advanced search → Search macros**.
    You may need to set **Owner** to your user name to see it.

18. In **Validation Expression** type:

    ```
    isnum($rate$)
    ```

19. In **Validation Error Message** type:

    ```
    to_currency expects a numeric rate, as in `to_currency(euro,€,0.92)`
    ```

20. Save, and deliberately call it badly:

    ```
    index=sales sourcetype=vendor_sales
    | `to_currency(euro,€,.xxx)`
    ```

21. Confirm your message appears.

22. Run it once more *without* the validation (remove it temporarily) and
    compare the error you get. Which would you rather hand a VP?
    ______________________

## Answers

<details>
<summary>Expand after attempting.</summary>

**Step 7** — A macro is plain text substitution. Splunk pastes the definition
in and parses the result, so the macro's last command and your `| head 5`
simply become adjacent commands in one pipeline.

**Step 16** — Keeping the pipe at the call site makes the macro composable.
It can follow any base search the caller likes. A macro that starts with its
own pipe can only ever be dropped in where the author anticipated.

**Step 22** — Without validation you get a parse error from somewhere inside
the expanded search, referring to text the user never typed. With it, you get
a sentence telling them exactly what to fix.

</details>
