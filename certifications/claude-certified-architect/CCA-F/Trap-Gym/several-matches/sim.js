/* Several customer matches simulator. Deterministic: the same eight chats play out for every
   search result x policy pair, so a recording can be repeated. The wait time for a person is
   illustrative. The exam guide's point (5.2): with several matches, ask for an identifier rather
   than pick one by a heuristic; a person is for the triggers (a request, a policy gap, no way forward). */
(function () {
  const SEARCH = {
    one:   { label: "One match", kind: "Unique name", tone: "mint" },
    three: { label: "Three customers called Priya Sharma", kind: "Same name", tone: "rose" },
    email: { label: "Two accounts share one email", kind: "Same email", tone: "butter" },
  };
  const POLICY = {
    recent: { label: "Pick the most recent account", where: ["box-guess"] },
    name:   { label: "Pick the best name match", where: ["box-guess"] },
    ask:    { label: "Ask for an identifier", where: ["box-ask"] },
    human:  { label: "Escalate to a human", where: ["box-human"] },
    list:   { label: "List the matches for the customer", where: ["box-list"] },
  };
  const WAIT = 15; // illustrative minutes in the queue for a person

  // Accounts that the search can return, per search result. last = date of the latest box.
  const ACC = {
    one: {},
    three: {
      A: { name: "Priya Sharma", where: "Leeds LS6", last: "24 Oct", order: "51120" },
      B: { name: "Priya Sharma", where: "Bristol BS3", last: "17 Oct", order: "50877" },
      C: { name: "Priya Sharma", where: "Leeds LS2", last: "3 Sep", order: "46302" },
    },
    email: {
      P: { name: "Priya Sharma", where: "Leeds LS6", last: "22 Oct", order: "51004" },
      R: { name: "Rahul Sharma", where: "Leeds LS6", last: "9 Oct", order: "49870" },
    },
  };
  // Unique customers for the one-match case.
  const ONE = [
    ["Meera Krishnan", "Hull HU5"], ["Tomasz Nowak", "York YO1"], ["Aisha Bello", "Derby DE1"], ["Callum Reid", "Perth PH1"],
    ["Grace Okafor", "Bath BA2"], ["Ravi Menon", "Leeds LS7"], ["Hannah Price", "Ely CB7"], ["Owen Lloyd", "Bangor LL57"],
  ];
  ONE.forEach(([n, w], i) => (ACC.one["U" + i] = { name: n, where: w, last: "20 Oct", order: String(52000 + i * 7) }));

  // Each chat: who really wrote it, what they ask, the account the best name match lands on,
  // and what they say when asked for an identifier (null: they can't or won't give one).
  const CHATS = {
    one: ONE.map((c, i) => ({ who: "U" + i, says: ["Please skip next week's box.", "My salmon was missing, can I get a refund?", "Change my delivery day to Friday.", "Pause my plan for July.", "Update my card details.", "Refund the cracked eggs, please.", "Cancel the extra box.", "Change my delivery address."][i], close: "U" + i, gives: null })),
    three: [
      { who: "A", says: "Please skip next week's box.", close: "A", gives: "Order 51120" },
      { who: "B", says: "My salmon was missing again, please refund it.", close: "A", gives: "Postcode BS3 4QT" },
      { who: "C", says: "I'm in Leeds. Change my delivery day to Friday.", close: "A", gives: "Order 46302" },
      { who: "B", says: "I'm in Bristol, please pause my plan for July.", close: "B", gives: "Postcode BS3 4QT" },
      { who: "A", says: "Update my card details, please.", close: "A", gives: "Postcode LS6 2AB" },
      { who: "C", says: "I used to live in Bristol. Cancel the extra box.", close: "B", gives: "Order 46302" },
      { who: "B", says: "Refund the cracked eggs. I'm in Bristol.", close: "B", gives: null },
      { who: "A", says: "Change my delivery address to my office.", close: "A", gives: "Order 51120" },
    ],
    email: [
      { who: "R", says: "Hi, it's Rahul. Pause my box for two weeks.", close: "R", gives: "Order 49870" },
      { who: "P", says: "The salmon was missing, please refund it.", close: "P", gives: "Order 51004" },
      { who: "R", says: "Change my delivery address, please.", close: "P", gives: "Order 49870" },
      { who: "P", says: "Priya here. Update my card details.", close: "P", gives: "Order 51004" },
      { who: "R", says: "Cancel the extra box we ordered.", close: "P", gives: "Order 49870" },
      { who: "R", says: "Rahul again: refund the cracked eggs.", close: "R", gives: "Order 49870" },
      { who: "P", says: "Skip next week, thanks.", close: "P", gives: "Order 51004" },
      { who: "P", says: "Priya: pause my plan for July.", close: "P", gives: "Order 51004" },
    ],
  };

  const VERDICT = {
    one: {
      recent: ["Fine here", "mint", "One account came back, so there was nothing to pick between. The rule only shows its flaw when several match."],
      name:   ["Fine here", "mint", "One account came back, so there was nothing to pick between. The rule only shows its flaw when several match."],
      ask:    ["Best fit (exam answer)", "mint", "With one match the policy never fires: the agent goes straight ahead, with no extra question."],
      human:  ["Fine here", "mint", "Nothing to escalate with one match. The cost only shows when several accounts come back."],
      list:   ["Fine here", "mint", "With one match there is no one else's account to show. Try it with three Priyas."],
    },
    three: {
      recent: ["Wrong person", "rose", "A heuristic guess. The newest box belongs to only one of three Priyas, so most changes landed on a stranger's account."],
      name:   ["Only usually works", "rose", "Closer, but still a guess. A town mentioned in passing, or a past address, sent changes to the wrong Priya."],
      ask:    ["Best fit (exam answer)", "mint", "One short question settled seven chats. The customer who would give nothing went to a person, because the agent could not make progress: a real trigger."],
      human:  ["Overbuilt", "butter", "Every change was right, but every chat waited for a person when one question would have settled it."],
      list:   ["Leaks data", "rose", "The customer chose correctly, but each chat showed two other customers' towns and order dates to someone unverified."],
    },
    email: {
      recent: ["Wrong person", "rose", "A heuristic guess. Half the chats were from Rahul, and every one of them changed Priya's account."],
      name:   ["Only usually works", "rose", "Signed messages went to the right account; unsigned ones were guessed, and two landed on the wrong person."],
      ask:    ["Best fit (exam answer)", "mint", "The order number settled it every time, for one extra message per chat."],
      human:  ["Overbuilt", "butter", "Right every time, but a household sharing an email is routine. A queue for it wastes people's time and the customer's."],
      list:   ["Leaks data", "rose", "Right every time, but it showed another person's account to whoever wrote from the shared inbox."],
    },
  };

  const BOXES = ["box-guess", "box-ask", "box-human", "box-list"];
  const $ = (id) => document.getElementById(id);
  let s = "three", p = "recent", timers = [];

  const acc = (k) => ACC[s][k];
  const label = (k) => `${acc(k).name}, ${acc(k).where}`;

  // Plays one chat: returns { steps: [text], changed: account key or null, human, exposed, extra }.
  function play(c) {
    const keys = Object.keys(ACC[s]);
    const matches = s === "one" ? [c.who] : keys;
    const r = { steps: [], changed: null, human: false, exposed: 0, extra: 0 };
    r.steps.push(matches.length === 1 ? "Search finds 1 account." : `Search finds ${matches.length} accounts.`);
    if (matches.length === 1) { r.steps.push("Agent goes ahead with that account."); r.changed = matches[0]; return r; }
    if (p === "recent") {
      const k = matches.slice().sort((a, b) => new Date(acc(b).last + " 2026") - new Date(acc(a).last + " 2026"))[0];
      r.steps.push(`Picks the latest box (${acc(k).last}): ${label(k)}.`); r.changed = k;
    } else if (p === "name") {
      r.steps.push(`Picks the closest match to the chat: ${label(c.close)}.`); r.changed = c.close;
    } else if (p === "ask") {
      r.extra = 1;
      r.steps.push("Asks: “What's your order number or postcode?”");
      if (c.gives) { r.steps.push(`Customer: “${c.gives}”. One account fits.`); r.changed = c.who; }
      else {
        r.extra = 2;
        r.steps.push("Customer: “I'd rather not say.” Agent asks once more, for a different detail; still nothing.");
        r.steps.push("Can't make progress, so it hands over to a person, who verifies the caller.");
        r.human = true; r.changed = c.who;
      }
    } else if (p === "human") {
      r.steps.push(`Hands the chat to a person (about ${WAIT} min wait), who verifies the caller.`);
      r.human = true; r.changed = c.who;
    } else {
      r.exposed = matches.length - 1;
      r.steps.push("Shows every match: " + matches.map((k) => `${acc(k).name} (${acc(k).where}, last box ${acc(k).last})`).join("; ") + ".");
      r.steps.push("Customer picks their own."); r.changed = c.who;
    }
    return r;
  }

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

  function highlight() {
    BOXES.forEach((id) => {
      const r = $(id);
      if (r) r.setAttribute("stroke-width", s !== "one" && POLICY[p].where.includes(id) ? "4" : "1.5");
    });
    const one = $("box-one");
    if (one) one.setAttribute("stroke-width", s === "one" ? "4" : "1.5");
  }

  function draw() {
    buttons("sim-s", SEARCH, s, (k) => (s = k));
    buttons("sim-p", POLICY, p, (k) => (p = k));
    highlight();
    run();
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    const list = $("sim-chats");
    list.innerHTML = "";
    let right = 0, wrong = 0, human = 0, exposed = 0, extra = 0;
    CHATS[s].forEach((c, i) => {
      const r = play(c);
      const ok = r.changed === c.who;
      ok ? right++ : wrong++;
      if (r.human) human++;
      exposed += r.exposed; extra += r.extra;
      const li = document.createElement("li");
      li.className = ok ? "" : "bad";
      const tag = ok ? `<span class="chip mint">right person</span>` : `<span class="chip rose">wrong person</span>`;
      li.innerHTML =
        `<div class="hd"><b>Chat ${i + 1}</b> <span class="who">really from ${label(c.who)}</span></div>` +
        `<div class="say">“${c.says}”</div>` +
        `<ol>${r.steps.map((t) => `<li>${t}</li>`).join("")}</ol>` +
        `<div class="res">Account changed: <b>${label(r.changed)}</b> ${tag}${r.human ? ` <span class="chip butter">via a person</span>` : ""}${r.exposed ? ` <span class="chip rose">${r.exposed} other ${r.exposed === 1 ? "customer" : "customers"} shown</span>` : ""}</div>`;
      list.appendChild(li);
      timers.push(setTimeout(() => li.classList.add("show"), 90 * i));
    });
    $("sim-tally").innerHTML =
      `Right account: <b>${right} of 8</b> · Wrong person's account changed: <b>${wrong}</b> · ` +
      `Handed to a person: <b>${human}</b>${human ? ` (about ${human * WAIT} min of waiting in all)` : ""} · ` +
      `Extra questions asked: <b>${extra}</b> · Other customers' details shown: <b>${exposed}</b>`;
    const v = VERDICT[s][p];
    $("sim-verdict").className = "box " + v[1];
    $("sim-verdict").innerHTML = `<span class="chip ${v[1]}">${v[0]}</span> ${v[2]}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
