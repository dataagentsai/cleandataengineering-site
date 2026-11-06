---
title: Source semantic understanding: a key to data program success
date: 2026-11-06
subject: data
audience: builders
kind: explainer
draft: false
summary: Most "the numbers don't match" problems after go-live are not pipeline bugs. They come from not knowing what the source data means and how the source system behaves. This post draws the six questions to ask about every source, who can answer them, where to write the answers down, and why "matches the trusted report" is the only real definition of done.
linkedin: The pipeline was green for three weeks. Then finance said the lake's revenue was 6% too high. Nothing was broken: cancelled orders, reversals and the wrong date column had all been loaded perfectly. Connecting to a source is plumbing. Knowing what it means is the job. Six questions to ask, drawn simply.
deeper: /learn/technical-anchor/discovery/
deeper_label: the discovery stage, where these questions belong
---

Ravi's team connects the new lakehouse to the sales system. Every table lands, every load is green, and the dashboard goes live on time.

Three weeks later, finance sends one line: "Your revenue for October is too high." The pipeline has no bug. It loaded exactly what the source holds, which includes orders that were later cancelled, invoices that were reversed with a minus entry, and dates the business doesn't report on.

Nobody asked what the data *means*. That is source semantics, and it decides whether a data program is trusted or quietly ignored.

## Plumbing is not meaning

Every source needs two kinds of understanding. The first is **plumbing**: where the source lives, how to connect, how to pick up changes. Architects and engineers are good at this, and tools make it easier every year.

The second is **meaning**: what one row stands for, which records count, which date matters, what a blank means. No connector can tell you this. It lives in people's heads and in the habits of the source system.

{{drawing: sem-two-halves}}

Plumbing problems shout. A failed connection stops the load and someone fixes it that night. Meaning problems whisper. The load succeeds, the numbers look plausible, and the mistake is found weeks later by the person whose trust you most needed.

## Six questions for every source

You don't need a 200-row questionnaire. Almost every meaning problem falls under one of six questions.

{{drawing: sem-six}}

1. **What is one row?** The grain: an order, an order line, a daily snapshot, an event. Which key identifies it, and can that key change, be reused or be merged (two customer records become one)? Is this system the master copy, or a copy of something else?
2. **What life does a record live?** The statuses it moves through, such as draft, approved, posted and cancelled, and which of them count for reporting. How mistakes are fixed: overwritten, reversed with a minus entry, or cancelled and re-entered. What "deleted" means: gone, flagged, or archived.
3. **What time is it?** Most records carry several dates: when it happened, when it was posted, when it takes effect, when it was last changed. Which one does the business report on? Which time zone? A calendar year or a financial year? Can a closed month still change?
4. **What do the values mean?** What code `03` or type `ZOR` stands for. Whether amounts are in one currency or many, which exchange rate applies, whether tax is included, and whether a credit is a negative number or a flag. What a blank, a zero or a date like `9999-12-31` means.
5. **How do records connect?** Header and lines that must arrive together. Hierarchies such as cost centres or product groups, and how they change over time. Company codes or regions that follow different rules.
6. **What can we trust?** Test and dummy records, and how to spot them. Fields used for something other than their name ("we keep the region in remark2"). And most important: **which existing report does the business already trust**, and what does it show for a closed month?

## Two orders, two totals

Here is why question 2 matters so much. Follow two orders of ₹10,000 each through the sales system.

{{drawing: sem-order-life}}

It is created as a draft, approved, and posted. A week later a return is booked as a separate minus entry of ₹2,000. The customer's second order, also ₹10,000, is cancelled before it ships.

Load all of that naively and sum the amounts, and the lake says ₹18,000. Finance says ₹8,000: one posted order, less the return. Both numbers come from the same correct data. Only one of them is the business's meaning of revenue.

The fix is not code you can write before you know the rule. It is one question asked early: "Which statuses count, and how are returns booked?"

## Who can answer

The people in the first architecture meeting usually can't answer these questions, and that's fine. Their job is to tell you who can.

{{drawing: sem-who}}

- The **architect** knows where the data lives and how to reach it.
- A **key user** or business analyst knows what it means: the one who runs month-end, raises the orders, or builds the report finance trusts.
- The **data engineer** brings evidence: a profile of the real data, such as every distinct status value with its row count, the range of each date column, how many rows have a blank amount, and whether the key has duplicates.

Bring the profile to a short session per important source. People are poor at recalling rules from memory and very good at reacting to real data. "What does status 07 mean? There are 4,000 of them" gets an answer in seconds.

## Write it down once, use it three times

The answers belong in the dataset's own record, next to its loading settings, not in a slide deck. If you already describe each table with [one row of settings](/writing/metadata-driven-ingestion/), add a short meaning section to the same record.

```
dataset: sales.orders
grain: one row per order line
key: order_id + line_no (unique per company_code)
report_date: posting_date (India time)
counts_when: status in (POSTED, CLOSED)
returns: separate rows, negative amount
amount: INR, excluding tax
blank_ship_date: not shipped yet
trusted_report: Finance monthly sales pack
```

{{drawing: sem-one-record}}

That one record pays off three times:

1. **Quality rules.** "Status is one of the known values" and "the key is unique per company code" become checks that run on every load.
2. **Catalog descriptions.** People using the table read what it means instead of guessing.
3. **Reconciliation.** A check compares the lake's total for a closed month with the trusted report and shows any gap.

This is the meaning part of a [data contract](/writing/data-contracts/). The contract says what the producer promises. The semantic record says what the data means when it arrives.

## The real definition of done

A source is not onboarded when its tables land. It is onboarded when **the lake's numbers match the trusted report for one closed period**, within a tolerance the business agreed.

Make that the exit test for every source. It forces the meaning questions early, because you cannot pass it without them. And it gives the business a reason to trust the new numbers that has nothing to do with how modern the platform is.

## What goes wrong

- **Asking only the architect.** You get perfect plumbing and no meaning.
- **Asking from memory, not from data.** People forget the odd status, the backdated postings and the test company. A profile reminds them.
- **Discovering semantics in user testing.** By then the model is built, and every fix moves a number someone already saw.
- **One date for everything.** Reporting on the created date when finance reports on the posted date shifts revenue between months.
- **Keeping the answers in a meeting note.** They never become checks, so the same mistake comes back after the next source change.
- **No trusted number agreed.** Without one, "the lake is right" is an opinion, and the old report wins every argument.

## Five questions to check your own program

1. For your most important dataset, can you say in one sentence what one row is?
2. Which statuses count for reporting, and is that rule written where a machine can check it?
3. Which date does your main metric use, and does finance use the same one?
4. Is there a named report the business trusts, and have you matched it for a closed month?
5. Who is the key user for each source, and have they seen a profile of their own data?

Connecting to a source takes a week. Understanding it is what makes the next three years of numbers believable.
