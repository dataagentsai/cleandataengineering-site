/* Site search: Pagefind index in /pagefind/, custom UI. Loaded lazily by the header button. */
(function () {
  var SECTIONS = { learn: "Learn", certifications: "Certifications", paths: "Paths", platforms: "On your cloud", writing: "Blog",
    projects: "Projects", problems: "Hard problems", research: "Research", concepts: "Concepts", "how-we-work": "How we work",
    leaders: "For leaders", "data-engineering": "Data engineering", "ai-engineering": "AI engineering", "forward-deployed": "Forward deployed",
    "deep-tech": "Deep tech", "ai-for-cause": "AI for a cause", "road-safety": "Road safety", lab: "Lab", papers: "Papers", about: "About",
    mindset: "Mindset", simulators: "Simulators", business: "Business" };
  var pf = null, root = null, input, list, chips, state = { q: "", sec: "", res: [], sel: 0, token: 0 };

  function section(url) { var s = url.split("/")[1] || ""; return s; }
  function label(s) { return SECTIONS[s] || s; }
  function esc(t) { return t.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function load() {
    if (!pf) pf = import("/pagefind/pagefind.js").then(function (m) { return m.options({ excerptLength: 28 }).then(function () { return m; }); });
    return pf;
  }

  /* Pagefind ranks by body text. Add a boost for words in the title and URL, and for hub pages (short paths). */
  function rerank(d, q) {
    var toks = q.toLowerCase().split(/[^a-z0-9]+/).filter(function (t) { return t.length > 1 && ["the","a","an","of","to","in","on","for","and","vs","how","what","is","do"].indexOf(t) < 0; });
    if (!toks.length) return d;
    var phrase = toks.join(" ");
    return d.map(function (r, i) {
      var title = ((r.meta && r.meta.title) || "").toLowerCase().replace(/\s*·\s*clean data engineering$/, ""), url = r.url.toLowerCase().replace(/-/g, " ");
      var inT = toks.filter(function (t) { return title.indexOf(t) >= 0; }).length / toks.length, inU = toks.filter(function (t) { return url.indexOf(t) >= 0; }).length / toks.length;
      var depth = r.url.replace(/index\.html$/, "").split("/").filter(Boolean).length;
      var score = (1 - i / d.length) + 1.6 * inT + 0.8 * inU + (title.indexOf(phrase) >= 0 ? 1 : 0) + (inT > 0 ? Math.max(0, 4 - depth) * 0.12 : 0);
      return { r: r, s: score };
    }).sort(function (a, b) { return b.s - a.s; }).map(function (x) { return x.r; });
  }

  function build(container, inPage) {
    container.innerHTML =
      '<div class="sx-box"><input class="sx-in" type="search" placeholder="Search every page: e.g. delta vs iceberg, cost, skew" autocomplete="off" spellcheck="false" aria-label="Search the site">' +
      (inPage ? "" : '<button class="sx-x" aria-label="Close search">Esc</button>') + '</div>' +
      '<div class="sx-chips" role="group" aria-label="Filter by section"></div><div class="sx-list" role="listbox" aria-live="polite"></div>';
    input = container.querySelector(".sx-in"); list = container.querySelector(".sx-list"); chips = container.querySelector(".sx-chips");
    input.addEventListener("input", function () { state.sec = ""; run(input.value); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { move(1); e.preventDefault(); } else if (e.key === "ArrowUp") { move(-1); e.preventDefault(); }
      else if (e.key === "Enter") { var a = list.querySelectorAll("a.sx-r")[state.sel]; if (a) location.href = a.href; }
    });
    chips.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; state.sec = b.dataset.s; render(); });
    var x = container.querySelector(".sx-x"); if (x) x.onclick = close;
    load();
  }

  function move(d) {
    var as = list.querySelectorAll("a.sx-r"); if (!as.length) return;
    state.sel = (state.sel + d + as.length) % as.length;
    as.forEach(function (a, i) { a.classList.toggle("on", i === state.sel); });
    as[state.sel].scrollIntoView({ block: "nearest" });
  }

  function run(q) {
    state.q = q.trim(); var tok = ++state.token;
    if (!state.q) { state.res = []; render(); return; }
    load().then(function (m) { return m.debouncedSearch(state.q, {}, 120); }).then(function (r) {
      if (!r || tok !== state.token) return;
      return Promise.all(r.results.slice(0, 60).map(function (x) { return x.data(); })).then(function (d) {
        if (tok !== state.token) return;
        state.res = rerank(d, state.q); state.sel = 0; render();
        if (inPageMode) history.replaceState(null, "", "?q=" + encodeURIComponent(state.q));
      });
    });
  }

  function render() {
    var counts = {}; state.res.forEach(function (r) { var s = section(r.url); counts[s] = (counts[s] || 0) + 1; });
    var secs = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
    chips.innerHTML = secs.length > 1 ? '<button data-s=""' + (state.sec ? "" : ' class="on"') + ">All " + state.res.length + "</button>" +
      secs.map(function (s) { return '<button data-s="' + s + '"' + (state.sec === s ? ' class="on"' : "") + ">" + esc(label(s)) + " " + counts[s] + "</button>"; }).join("") : "";
    var rows = state.res.filter(function (r) { return !state.sec || section(r.url) === state.sec; });
    if (!state.q) { list.innerHTML = '<p class="sx-hint">Type to search all pages. Use ↑ ↓ and Enter to move, Esc to close.</p>'; return; }
    if (!rows.length) { list.innerHTML = '<p class="sx-hint">No pages match “' + esc(state.q) + '”. Try fewer or simpler words.</p>'; return; }
    list.innerHTML = rows.map(function (r, i) {
      var t = (r.meta && r.meta.title || r.url).replace(/\s*·\s*Clean Data Engineering$/, "");
      return '<a class="sx-r' + (i === state.sel ? " on" : "") + '" href="' + r.url + '"><span class="sx-t">' + esc(t) + '</span><span class="sx-s">' + esc(label(section(r.url))) +
        '</span><span class="sx-e">' + r.excerpt + "</span></a>";
    }).join("");
  }

  var inPageMode = false, modal;
  function open() {
    if (!modal) {
      modal = document.createElement("div"); modal.className = "sx-modal"; modal.innerHTML = '<div class="sx-bg"></div><div class="sx-panel" role="dialog" aria-label="Search"></div>';
      document.body.appendChild(modal); modal.querySelector(".sx-bg").onclick = close; build(modal.querySelector(".sx-panel"), false);
      list.innerHTML = '<p class="sx-hint">Type to search all pages. Use ↑ ↓ and Enter to move, Esc to close.</p>';
    }
    modal.classList.add("open"); input.focus(); input.select();
  }
  function close() { if (modal) modal.classList.remove("open"); }

  window.cdeSearch = { open: open, close: close };
  document.addEventListener("keydown", function (e) {
    var typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName) || (document.activeElement || {}).isContentEditable;
    if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing)) { e.preventDefault(); inPageMode ? input.focus() : open(); }
    else if (e.key === "Escape") close();
  });

  var page = document.getElementById("sx-page");
  if (page) {
    inPageMode = true; build(page, true);
    var q = new URLSearchParams(location.search).get("q") || ""; input.value = q; input.focus();
    list.innerHTML = '<p class="sx-hint">Type to search all pages.</p>'; if (q) run(q);
  }
  if (window.__sxOpen) { window.__sxOpen = false; if (!inPageMode) open(); }
})();
