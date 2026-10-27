/* Renders plain-style practice questions (parts/plain/*.json shape) with answer reveal,
   "Explain simply" (eli5) and "Think it through" (deep). Options keep their order so [[i]] maps to a letter. */
(function () {
  const L = "ABCDEF";
  const sub = (s) => String(s || "").replace(/\[\[(\d)\]\]/g, (_, i) => L[+i]);
  const el = (tag, cls, html) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };

  function deepHtml(d) {
    let h = `<h3>1. The assumption to fix</h3><p>${sub(d.premise)}</p>`;
    if (d.diagram) h += `<pre>${d.diagram.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</pre>`;
    h += `<h3>2. Mind map: ${d.mapTitle}</h3><div class="tablewrap"><table><tr>${d.map.head.map((x) => `<th>${x}</th>`).join("")}</tr>`;
    h += d.map.rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("") + "</table></div>";
    h += `<h3>3. Apply it to the question</h3>`;
    h += d.evidence.map((e) => `<div class="ev"><q>${e.quote}</q><br>${sub(e.means)}</div>`).join("");
    h += `<h3>4. Rule to remember</h3><div class="box butter"><b>${d.rule}</b><br><span style="font-size:.9rem">Exam guide ${d.guide.obj}: “${d.guide.quote}”</span></div>`;
    return h;
  }

  function card(q, n, scen, before) {
    const c = el("div", "q");
    const s = scen[q.sid];
    c.appendChild(el("div", "meta", `<span class="chip peri">${q.domain}</span><span class="chip">Question ${n}</span>`));
    if (s) c.appendChild(el("details", "scen", `<summary>${s.title} (read the setting)</summary><p>${s.brief}</p>`));
    c.appendChild(el("div", "stem", q.question));
    const opts = [];
    q.options.forEach((o, i) => {
      const b = el("button", "opt", `<b class="l">${L[i]}</b>${o.t}<div class="why">${o.trap ? `<span class="chip rose">${o.trap}</span>` : `<span class="chip mint">best</span>`}${o.why}</div>`);
      b.onclick = () => {
        if (c.classList.contains("done")) return;
        c.classList.add("done");
        opts.forEach((x, j) => x.classList.add(q.answer.includes(j) ? "right" : j === i ? "wrong" : "x"));
      };
      opts.push(b);
      c.appendChild(b);
    });
    const after = el("div", "after");
    const eli = el("div", "layer box mint", `<p>${q.eli5.question}</p><p>${q.eli5.answer}</p>`);
    const deep = el("div", "layer", deepHtml(q.deep));
    const b1 = el("button", "btn", "Explain simply");
    const b2 = el("button", "btn", "Think it through");
    b1.onclick = () => { eli.classList.toggle("open"); b1.classList.toggle("on"); };
    b2.onclick = () => { deep.classList.toggle("open"); b2.classList.toggle("on"); };
    after.append(b1, b2, eli, deep);
    c.appendChild(after);
    if (before) {
      const ol = before.options.map((o, i) => `<li class="${before.answer.includes(i) ? "k" : ""}">${o.t}${before.answer.includes(i) ? " (key)" : ""}${i === before.runnerUp ? " (runner-up)" : ""}</li>`).join("");
      c.appendChild(el("details", "before", `<summary>Before: the Mock 7 version (${String(before.question).replace(/<[^>]+>/g, "").split(/\s+/).length} words)</summary><p>${before.question}</p><ol type="A">${ol}</ol>`));
    }
    return c;
  }

  window.renderPlain = function (target, data, ids, before) {
    const scen = Object.fromEntries(data.scenarios.map((s) => [s.id, s]));
    const byId = Object.fromEntries(data.questions.map((q) => [q.id, q]));
    const list = ids ? ids.map((i) => byId[i]).filter(Boolean) : data.questions;
    list.forEach((q, n) => target.appendChild(card(q, n + 1, scen, before && before[q.was])));
  };
})();
