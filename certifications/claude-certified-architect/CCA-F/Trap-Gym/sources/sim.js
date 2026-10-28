/* Sources simulator. Deterministic: every source set x synthesis approach pair writes the same fixed
   report, so a recording can be repeated. The town, sources and figures are made up for the lesson
   (illustrative), chosen to show the shape the exam guide describes (5.6: attribution is lost when
   summaries compress without claim-source mappings; conflicting figures are annotated with their
   sources, not settled by picking one; dates stop time differences reading as contradictions;
   figures render as tables, news as prose). */
(function () {
  // Source cards. fig = the figure it gives (null for a news story).
  const SRC = {
    nso:   { name: "National Statistics Office, Labour Force Survey", short: "NSO survey", pub: "Mar 2024", data: "2023", fig: "28%", how: "household survey, 12,000 people" },
    uni:   { name: "Riverton University study", short: "University study", pub: "Jun 2024", data: "2023", fig: "27%", how: "survey of 3,000 workers" },
    cham:  { name: "Riverton Chamber of Commerce poll", short: "Chamber poll", pub: "Feb 2024", data: "2023", fig: "41%", how: "poll of 220 firms: staff allowed to work from home" },
    nso19: { name: "National Statistics Office, Labour Force Survey", short: "NSO survey", pub: "Mar 2020", data: "2019", fig: "9%", how: "household survey, 11,500 people" },
    news:  { name: "Riverton Gazette article", short: "Riverton Gazette", pub: "Apr 2024", data: "", fig: null, how: "news story: cafés near the business park report quieter Mondays and Fridays" },
  };
  const SETS = {
    agree:  { label: "Sources agree", ids: ["nso", "uni", "news"], kind: "28% and 27%", tone: "mint" },
    clash:  { label: "Two sources give different figures", ids: ["nso", "cham", "news"], kind: "28% vs 41%", tone: "rose" },
    years:  { label: "Same statistic, different years", ids: ["nso", "nso19", "news"], kind: "2023 vs 2019", tone: "butter" },
  };
  const WAYS = {
    plain:  { label: "Plain summary", where: ["box-plain"] },
    mapped: { label: "Claim-source mapping kept through synthesis", where: ["box-map", "box-both"] },
    pick:   { label: "Keep the most recent or most authoritative figure", where: ["box-pick"] },
    both:   { label: "Show conflicting figures side by side, with source and date", where: ["box-plain", "box-both"] },
  };
  const COLS = ["Figure", "Value", "Source", "Dates"];
  const row = (id, figure) => [figure, SRC[id].fig, SRC[id].short, `data ${SRC[id].data}<br>published ${SRC[id].pub}`];
  const FIG = "Work from home";
  const CAFE = "Cafés near the business park report quieter Mondays and Fridays";
  // Report items: { p: text, src: citation or null, flag } or { table: rows, note }.
  // flag: "invented" | "time" | null. drop = figures dropped, the verdict comes last.
  const OUT = {
    agree: {
      plain:  { items: [{ p: "About 28% of Riverton's workers now work from home at least two days a week.", src: null },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Can't be checked", c: "rose",
                note: "The number happens to be right, but no reader can check it. The sources were compressed out of the summary, and nothing carried them through." },
      mapped: { items: [{ table: [row("nso", FIG), row("uni", FIG)] },
                        { p: "Two independent surveys put the share at about 28% for 2023.", src: "NSO survey, Mar 2024; University study, Jun 2024" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 0, v: "Best fit (exam answer)", c: "mint",
                note: "Every claim arrives with its source and date, because they travelled as data through each step. Figures sit in a table; the news stays prose." },
      pick:   { items: [{ p: "28% of Riverton's workers work from home at least two days a week.", src: "NSO survey, Mar 2024" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 1, v: "Also works", c: "mint",
                note: "When the sources agree, keeping one figure loses little: the dropped 27% said the same thing. The trap shows when they don't agree." },
      both:   { items: [{ table: [row("nso", FIG), row("uni", FIG)] },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Only half", c: "butter",
                note: "The figures are checkable, but the prose claim lost its source. Only the numbers carried attribution; nothing kept the claim-to-source links for the rest." },
    },
    clash: {
      plain:  { items: [{ p: "Roughly a third of Riverton's workers (about 35%) work from home at least two days a week.", src: null, flag: "invented" },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Breaks", c: "rose",
                note: "35% appears in neither source. The summary blended 28% and 41% into a number nobody measured, and the disagreement vanished with the sources." },
      mapped: { items: [{ table: [row("nso", FIG), row("cham", "Allowed to work from home")], note: "Sources disagree. They also measure different things: the survey asks workers what they do; the poll asks firms what they allow." },
                        { p: "The household survey gives 28%; the employer poll gives 41%. Both are for 2023.", src: "NSO survey, Mar 2024; Chamber poll, Feb 2024" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 0, v: "Best fit (exam answer)", c: "mint",
                note: "Both figures are shown, each with its source, date and method. The reader weighs them; the system didn't quietly pick one." },
      pick:   { items: [{ p: "28% of Riverton's workers work from home at least two days a week.", src: "NSO survey, Mar 2024" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 1, v: "Picks one", c: "rose",
                note: "Every line is checkable, but the 41% figure is gone. The reader can't see there was a disagreement to weigh." },
      both:   { items: [{ table: [row("nso", FIG), row("cham", "Allowed to work from home")], note: "Sources disagree." },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Also works", c: "mint",
                note: "The conflict is shown honestly, each figure with its source and date. Only the prose line lost its source, because no claim-to-source links came through the summary." },
    },
    years: {
      plain:  { items: [{ p: "Estimates of remote work in Riverton vary widely, from 9% to 28%.", src: null, flag: "time" },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Breaks", c: "rose",
                note: "A 2019 figure and a 2023 figure were read as a disagreement. Without dates, a change over time looks like a conflict, and nobody can check either number." },
      mapped: { items: [{ table: [row("nso19", FIG), row("nso", FIG)], note: "Same survey, two years: a change over time, not a conflict." },
                        { p: "The share rose from 9% in 2019 to 28% in 2023.", src: "NSO survey, Mar 2020 and Mar 2024 editions" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 0, v: "Best fit (exam answer)", c: "mint",
                note: "The dates came through with each figure, so synthesis compared them first. The report shows a trend, and the latest figure is the current one." },
      pick:   { items: [{ p: "28% of Riverton's workers work from home at least two days a week.", src: "NSO survey, Mar 2024" },
                        { p: CAFE + ".", src: "Riverton Gazette, Apr 2024" }],
                drop: 1, v: "Only half", c: "butter",
                note: "The latest figure is the current one, so the headline is right. But the rise from 9% is gone, and the reader can't see that an older figure was dropped." },
      both:   { items: [{ table: [row("nso", FIG), row("nso19", FIG)], note: "Sources disagree." },
                        { p: "Sources disagree on how many Riverton workers work from home.", src: null, flag: "time" },
                        { p: "Local businesses say the change is visible, with quieter Mondays and Fridays.", src: null }],
                drop: 0, v: "Misreads time", c: "rose",
                note: "The dates are printed in the table, yet the report calls a rise over four years a disagreement. Dates must be compared, not only shown." },
    },
  };
  const BOXES = ["box-plain", "box-map", "box-pick", "box-both"];

  const $ = (id) => document.getElementById(id);
  let s = "clash", w = "plain", timers = [];

  function buttons(boxId, items, current, set) {
    const box = $(boxId);
    box.innerHTML = "";
    Object.entries(items).forEach(([k, v]) => {
      const x = document.createElement("button");
      x.className = "btn" + (k === current ? " on" : "");
      x.innerHTML = v.label + (v.kind ? ` <span class="chip ${v.tone}">${v.kind}</span>` : "");
      x.onclick = () => { set(k); draw(); };
      box.appendChild(x);
    });
  }

  function draw() {
    buttons("sim-s", SETS, s, (k) => (s = k));
    buttons("sim-w", WAYS, w, (k) => (w = k));
    BOXES.forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", WAYS[w].where.includes(id) ? "4" : "1.5"); });
    run();
  }

  const mark = (ok, flag) =>
    flag === "invented" ? `<span class="chip rose">invented figure</span>` :
    flag === "time" ? `<span class="chip rose">time read as conflict</span>` :
    ok ? `<span class="chip mint">checkable</span>` : `<span class="chip rose">no source</span>`;

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    $("sim-src").innerHTML = SETS[s].ids.map((id) => {
      const x = SRC[id];
      return `<div class="src"><b>${x.name}</b><br>${x.fig ? `<span class="big">${x.fig}</span> ` : ""}<span class="mut">${x.how}</span><br><span class="mut">Published ${x.pub}${x.data ? ` · data from ${x.data}` : ""}</span></div>`;
    }).join("");
    const o = OUT[s][w];
    const rep = $("sim-report");
    rep.innerHTML = "";
    let lines = 0, ok = 0, invented = 0, misread = false;
    o.items.forEach((it, i) => {
      const d = document.createElement("div");
      d.className = "ri";
      if (it.table) {
        lines += it.table.length; ok += it.table.length;
        d.innerHTML = `<p class="tn">Share of Riverton's workers, at home at least two days a week</p><div class="tablewrap"><table><tr>${COLS.map((c) => `<th>${c}</th>`).join("")}</tr>${it.table.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</table></div>` +
          (it.note ? `<p class="tn">${it.note}</p>` : "") + `<div>${mark(true)} each row names its source and date</div>`;
      } else {
        lines++; if (it.src && !it.flag) ok++;
        if (it.flag === "invented") invented++;
        if (it.flag === "time") misread = true;
        d.innerHTML = `<p>${it.p}${it.src ? ` <span class="cite">[${it.src}]</span>` : ""}</p><div>${mark(!!it.src, it.flag)}</div>`;
      }
      rep.appendChild(d);
      timers.push(setTimeout(() => d.classList.add("show"), 160 * i));
    });
    const hasTable = o.items.some((it) => it.table);
    $("sim-tally").innerHTML =
      `Lines a reader can check: <b>${ok} of ${lines}</b> · Figures dropped: <b>${o.drop || "none"}</b> · Invented figures: <b>${invented || "none"}</b><br>` +
      `Change over time read as a conflict: <b>${misread ? "yes" : "no"}</b> · Figures shown as: <b>${hasTable ? "a table" : "prose"}</b>`;
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
