"""Drawings for 'Your Databricks bill has a leak: 10 cost mistakes we keep seeing'. Globals kit, figure, E, ROOT are injected."""


def drawing_dbx_leaky_bucket():
    t = kit.text
    d = t(500, 24, "nobody decided to spend it; it just leaks out", "sm", "middle")
    # the tap
    d += '<rect class="hz" x="420" y="40" width="120" height="26" rx="6"/><rect class="hz" x="500" y="66" width="24" height="22" rx="3"/>'
    d += t(560, 58, "your budget", "sm")
    d += '<path class="ln" d="M512,92 L512,120"/><path class="ln" d="M506,100 L506,118"/>'
    # the bucket
    d += '<path class="hz" d="M380,125 L640,125 L610,330 L410,330 Z"/>'
    d += '<path class="pf pf-bx" d="M390,165 L630,165 L610,325 L414,325 Z"/>'
    d += '<ellipse class="hz" cx="510" cy="125" rx="130" ry="12"/>'
    # holes and drips, left side
    left = [(392, 180, "idle clusters"), (398, 225, "the wrong kind of compute"), (404, 270, "warehouses left on"), (410, 312, "no cost tags")]
    for x, y, lbl in left:
        d += f'<ellipse class="hk" cx="{x}" cy="{y}" rx="5" ry="4"/>'
        d += f'<path class="ln" d="M{x - 6},{y} Q{x - 40},{y + 2} {x - 60},{y + 16}"/>'
        d += f'<path class="bxs" d="M{x - 66},{y + 18} q4,-8 8,0 a4,4 0 1,1 -8,0 Z"/>'
        d += t(x - 80, y + 6, lbl, "tx", "end")
    right = [(628, 180, "small files"), (622, 225, "one slow task (skew)"), (616, 270, "Python UDFs"), (610, 312, "collect() on big data")]
    for x, y, lbl in right:
        d += f'<ellipse class="hk" cx="{x}" cy="{y}" rx="5" ry="4"/>'
        d += f'<path class="ln" d="M{x + 6},{y} Q{x + 40},{y + 2} {x + 60},{y + 16}"/>'
        d += f'<path class="bxs" d="M{x + 58},{y + 18} q4,-8 8,0 a4,4 0 1,1 -8,0 Z"/>'
        d += t(x + 80, y + 6, lbl, "tx", "start")
    d += t(510, 360, "plus two more: oversized clusters and the wrong number of partitions", "sm", "middle")
    return figure(1000, 380, d, "A bucket filled from a tap labelled your budget. Water leaks out through holes labelled idle clusters, the wrong kind of compute, warehouses left on, no cost tags, small files, one slow task, Python UDFs and collect() on big data.",
                  "The bill doesn't jump. It leaks, through many small holes at once.")


def drawing_dbx_weekend_bill():
    t = kit.text
    x0, x1 = 170, 960
    hours = 63
    sc = (x1 - x0) / hours
    d = t(500, 24, "Friday 18:00 to Monday 09:00: 63 hours (illustrative, example prices)", "sm", "middle")
    # row 1: the forgotten cluster
    d += t(155, 88, ["Forgotten", "cluster"], "bd", "end")
    d += f'<rect class="pf pf-bxs" x="{x0}" y="70" width="{x1 - x0}" height="40" rx="4"/>'
    d += f'<rect class="hz" x="{x0}" y="70" width="{x1 - x0}" height="40" rx="4" style="fill:none"/>'
    d += t((x0 + x1) / 2, 96, "running the whole time, almost all of it idle: about $139", "tx", "middle")
    # row 2: job clusters
    d += t(155, 178, ["Job clusters,", "auto-stop"], "bd", "end")
    d += f'<line class="lnd" x1="{x0}" y1="180" x2="{x1}" y2="180"/>'
    for start in (6, 30, 54):
        x = x0 + start * sc
        d += f'<rect class="bx" x="{x:.0f}" y="160" width="{2.25 * sc:.0f}" height="40" rx="4"/>'
    d += t(x0 + 6 * sc + 30, 225, "three nights of real work, then the machines stop: about $5", "tx", "start")
    # day ticks
    for h, lbl in ((0, "Fri"), (6, "Sat"), (30, "Sun"), (54, "Mon"), (63, "09:00")):
        x = x0 + h * sc
        d += f'<line class="ln" x1="{x:.0f}" y1="250" x2="{x:.0f}" y2="258"/>' + t(x, 278, lbl, "sm", "middle")
    d += f'<line class="ln" x1="{x0}" y1="254" x2="{x1}" y2="254"/>'
    return figure(1000, 295, d, "Two timelines over 63 hours. The forgotten cluster runs the whole time and costs about $139. Job clusters run only for three short nightly windows and cost about $5.",
                  "Compute is most of the bill, and idle compute costs the same as busy compute. Example prices from the weekend-bill story in our performance stories.")


def drawing_dbx_small_files():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "same data, same answer; the table just stops being 3,000 pieces", "sm", "middle")
    # tiny files grid
    for r in range(9):
        for c in range(14):
            x, y = 30 + c * 22, 60 + r * 22
            d += f'<rect class="hz" x="{x}" y="{y}" width="14" height="14" rx="2"/>'
    d += t(180, 280, "3,000 files of about 7 KB", "bd", "middle")
    d += t(180, 302, "query: 1.4 s", "sm", "middle")
    d += a(360, 155, 545, 155)
    d += b(380, 95, 150, 46, "OPTIMIZE", "", "bxs")
    d += t(455, 185, "compacts them", "sm", "middle")
    d += t(455, 205, "in one commit", "sm", "middle")
    # one right-sized file
    d += '<rect class="hz" x="620" y="70" width="140" height="180" rx="8"/>'
    d += '<rect class="pf pf-solid" x="628" y="78" width="124" height="164" rx="6"/>'
    for i in range(5):
        d += f'<line class="ln" x1="645" y1="{110 + i * 25}" x2="735" y2="{110 + i * 25}"/>'
    d += t(690, 280, "1 file", "bd", "middle")
    d += t(690, 302, "query: 235 ms", "sm", "middle")
    d += t(800, 120, ["the rule we use:", "flag any table whose", "average file is under", "about 32 MB"], "sm", "start")
    return figure(1000, 320, d, "On the left, a grid of many tiny file boxes labelled 3,000 files of about 7 KB, query 1.4 seconds. An arrow through OPTIMIZE leads to one large file, query 235 milliseconds.",
                  "Small files, before and after OPTIMIZE. Timings are from our recorded laptop run, so compare before with after, not with a cluster.")


def drawing_dbx_skew_bars():
    t = kit.text
    d = t(500, 24, "the join stage, 16 tasks: everyone waits for the long one", "sm", "middle")
    times = [45, 41, 48, 44, 46, 43, 47, 45, 42, 49, 44, 46, 45, 43, 47, 246]
    sc = 2.9
    x0 = 140
    for i, ms in enumerate(times):
        y = 50 + i * 15
        cls = "solid" if ms > 100 else "bx"
        d += f'<rect class="{cls}" x="{x0}" y="{y}" width="{ms * sc:.0f}" height="10" rx="2"/>'
    d += t(125, 60, "task 1", "sm", "end") + t(125, 285, "task 16", "sm", "end")
    d += f'<line class="lnd" x1="{x0 + 45 * sc:.0f}" y1="42" x2="{x0 + 45 * sc:.0f}" y2="295"/>'
    d += t(x0 + 45 * sc + 10, 316, "median: 45 ms", "sm", "start")
    d += t(x0 + 246 * sc + 12, 290, "slowest: 246 ms", "bd", "start")
    d += t(870, 120, ["5.5 times the median.", "The rule we use:", "skew when the slowest", "task is over 5 times", "the median"], "sm", "middle")
    d += t(310, 150, ["the other 15 finish fast,", "then sit and wait"], "sm", "start")
    return figure(1000, 330, d, "Sixteen horizontal task bars. Fifteen are short, around 45 milliseconds. One bar is much longer, 246 milliseconds, more than 5 times the median.",
                  "Skew in our recorded join: one customer holds 40% of the orders, so one task does far more work than the rest.")


def drawing_dbx_weekly_check():
    b, a, t = kit.box, kit.arrow, kit.text
    d = t(500, 24, "every Monday, ten minutes", "sm", "middle")
    d += kit.num(150, 60, 1) + b(40, 80, 230, 110, "Billing tables", ["system.billing.usage", "last 7 days"], "bx")
    d += a(272, 135, 318, 135)
    d += kit.num(430, 60, 2) + b(320, 80, 230, 110, "Group by tag", ["team, project, job;", "flag what's untagged"], "bxs")
    d += a(552, 135, 598, 135)
    d += kit.num(710, 60, 3) + b(600, 80, 230, 110, "A dashboard", ["top five spenders,", "a budget alert"], "solid")
    # stick person with a cup
    d += ('<circle class="bx" cx="910" cy="105" r="13"/><line class="lnc" x1="910" y1="118" x2="910" y2="160"/>'
          '<line class="lnc" x1="910" y1="160" x2="898" y2="185"/><line class="lnc" x1="910" y1="160" x2="922" y2="185"/>'
          '<line class="lnc" x1="910" y1="132" x2="888" y2="140"/><line class="lnc" x1="910" y1="132" x2="932" y2="124"/>')
    d += '<path class="hz" d="M928,108 L944,108 L942,124 L930,124 Z"/><path class="ln" d="M944,112 q6,4 0,9"/>'
    d += t(910, 215, "one cup of chai", "sm", "middle")
    d += t(435, 230, "tags make step 2 possible, so they come first", "sm", "middle")
    return figure(1000, 250, d, "Three numbered boxes: query the billing system tables for the last 7 days, group by tag and flag what is untagged, put it on a dashboard with a budget alert. A stick person holds a cup of chai.",
                  "A ten-minute weekly cost check. No cost tool needed to start.")


DRAWINGS = {
    "dbx-leaky-bucket": drawing_dbx_leaky_bucket,
    "dbx-weekend-bill": drawing_dbx_weekend_bill,
    "dbx-small-files": drawing_dbx_small_files,
    "dbx-skew-bars": drawing_dbx_skew_bars,
    "dbx-weekly-check": drawing_dbx_weekly_check,
}
