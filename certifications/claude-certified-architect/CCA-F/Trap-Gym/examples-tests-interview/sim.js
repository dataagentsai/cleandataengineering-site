/* Examples, tests first or interview? simulator. Deterministic: every situation x technique pair plays the
   same fixed rounds, so a recording can be repeated. Minutes are illustrative, chosen to show the shape the
   exam guide describes (3.5: examples for transformations, tests first with shared failures, the interview
   pattern, one message for interacting problems and sequential messages for independent ones). */
(function () {
  const SITS = {
    transform: { label: "Turn messy address lines into structured fields", kind: "Prose explains it badly", tone: "peri", unit: "records",
                 cases: ["Unit 4/12", "PO box", "Leading-zero postcode", "Two-word suburb", "No street number", "Lot number", "Corner address", "Plain address"] },
    known:     { label: "Fix fare rounding: the right total for 8 currencies is known", kind: "Fixes keep breaking cases", tone: "butter", unit: "currencies",
                 cases: ["USD", "EUR", "JPY", "KWD", "CHF", "INR", "GBP", "SEK"] },
    vague:     { label: "Build “smart reminders”: nobody has said what's wanted", kind: "Requirements unclear", tone: "rose", unit: "decisions",
                 cases: ["Who gets them", "How early", "Which channel", "Opt-out", "Whose time zone", "Repeats"] },
    interact:  { label: "Two checkout bugs: discount order and rounding", kind: "The problems interact", tone: "mint", unit: "baskets",
                 cases: ["Basket 1", "Basket 2", "Basket 3", "Basket 4", "Basket 5", "Basket 6", "Basket 7", "Basket 8"] },
    indep:     { label: "Two unrelated bugs: a receipt typo and a slow search", kind: "The problems are independent", tone: "mint", unit: "checks",
                 cases: ["Email 1", "Email 2", "Email 3", "Email 4", "Search 1", "Search 2", "Search 3", "Search 4"] },
  };
  const TECHS = {
    prose:     { label: "Describe it in prose", where: ["box-prose"] },
    examples:  { label: "Show input/output examples", where: ["box-examples"] },
    tests:     { label: "Write tests first, share failures", where: ["box-tests"] },
    interview: { label: "Let Claude interview you first", where: ["box-interview"] },
    one:       { label: "Everything in one message", where: ["box-one"] },
    seq:       { label: "One message per issue", where: ["box-seq"] },
  };
  const SIT_BOX = { transform: "q-transform", known: "q-known", vague: "q-vague", interact: "q-many", indep: "q-many" };

  // Each round: [cases, note, minutes]. cases: "1" right, "0" wrong, null = a round before any code
  // (questions or setup). A case that was right last round and is wrong now is counted as a break.
  const OUT = {
    transform: {
      prose: { v: "Only usually works", c: "butter", note: "It got there after four rewrites. Each rewrite fixed one misreading, and the new words left room for another.",
        r: [["10110100", "Claude reads “4/12” as a street number, and postcodes lose their leading zero", 12],
            ["11110110", "You rewrite the prose. Units are fixed; now it splits a two-word suburb into suburb and street", 10],
            ["11111110", "Third rewrite: the PO box still lands in the street field", 10],
            ["11111111", "Fourth rewrite: all 8 right", 8]] },
      examples: { v: "Best fit (exam answer)", c: "mint", note: "Three before-and-after records said what pages of prose could not. One more pair settled the last case.",
        r: [["11111110", "You paste three before-and-after records. Claude follows the pattern; only the PO box is new to it", 8],
            ["11111111", "You add the PO box as a fourth pair: all 8 right", 4]] },
      tests: { v: "Also works", c: "mint", note: "Tests are input/output examples that run themselves. Correct, but slower to set up than pasting three pairs. Their real strength is catching breaks.",
        r: [[null, "You write 8 tests from the records you expect", 15],
            ["11011110", "Claude runs them; you share the 2 failures", 6],
            ["11111111", "All 8 pass", 4]] },
      interview: { v: "Different problem", c: "rose", note: "You already knew what you wanted; the trouble was getting it across. Answers in words are still prose. Show the records instead.",
        r: [[null, "Claude asks how units, PO boxes and postcodes should look; you answer in words", 10],
            ["11110110", "Your answers are read one way, you meant another: 2 records still wrong", 10],
            ["11111110", "Another round of answers", 8],
            ["11111111", "All 8 right", 6]] },
      one: { v: "Only usually works", c: "butter", note: "The size of the message was never the problem; the prose was. Three before-and-after pairs would have said it faster.",
        r: [["10111100", "One long message with every rule you can think of, in prose", 14],
            ["11111100", "You reply with corrections for the misread records", 8],
            ["11111111", "All 8 right", 6]] },
      seq: { v: "Delays the problem", c: "butter", note: "Five rounds of rules sent one by one, with a break along the way. The whole transformation was known; examples show it at once.",
        r: [["10110000", "You send the first rule: units only", 6],
            ["11110100", "Second rule: postcodes", 6],
            ["11010110", "Third rule: suburbs. It breaks a record that was right", 6],
            ["11111110", "Fourth rule, plus a fix for the break", 6],
            ["11111111", "All 8 right", 5]] },
    },
    known: {
      prose: { v: "Only usually works", c: "butter", note: "Words describe the rounding rules, but nothing re-checks every currency after each fix. You checked all 8 by hand, four times.",
        r: [["11001100", "You describe the rounding rules in words; yen and dinar come out wrong", 8],
            ["11101010", "You rephrase. Two fixed, but the rupee case breaks; you find it by hand", 10],
            ["11111110", "Another round, checked by hand", 10],
            ["11111111", "All 8 right, checked by hand", 10]] },
      examples: { v: "Only usually works", c: "butter", note: "The examples show what's right, but nothing re-runs every case after each fix. A break slipped in and you caught it by hand.",
        r: [["11101100", "You paste the expected total for each currency as examples", 6],
            ["11111001", "Claude fixes yen and dinar; the fix breaks the rupee case. You find it by checking all 8 by hand", 12],
            ["11111111", "Fixed, and checked by hand again", 12]] },
      tests: { v: "Best fit (exam answer)", c: "mint", note: "The expected totals became tests. Every fix was checked against all 8 within seconds, so the one break was caught at once.",
        r: [[null, "You write one test per currency with the known total", 10],
            ["11001100", "Claude runs the suite; you share all 4 failures at once", 3],
            ["11111011", "Next fix: the suite shows the rupee case broke, within seconds", 3],
            ["11111111", "All 8 pass, and every later change is checked against all 8 too", 3]] },
      interview: { v: "Different problem", c: "rose", note: "Nothing about the behaviour was unclear. The trouble was fixes breaking other cases, and questions don't catch that.",
        r: [[null, "Claude asks how each currency should round; you already knew, so you read out the answers", 8],
            ["11011100", "Claude fixes from your answers: 5 of 8", 10],
            ["11111001", "The next fix breaks the rupee case; you find it by hand", 10],
            ["11111111", "All 8 right", 10]] },
      one: { v: "Only usually works", c: "butter", note: "Sending all the failures together beats one at a time, but nothing re-runs every case after each fix. Tests do that for you.",
        r: [["11011100", "You list every wrong total in one message", 6],
            ["11111001", "Claude fixes them together; the rupee case breaks, found by hand", 12],
            ["11111111", "Fixed, checked by hand", 12]] },
      seq: { v: "Delays the problem", c: "butter", note: "Whack-a-mole: each fix broke another case, and you only saw it by checking by hand. Six rounds for something the tests settle in three.",
        r: [["11001100", "You report the first wrong total", 6],
            ["11101100", "Fixed. You report the next one", 6],
            ["11100110", "That fix breaks the Swiss franc case", 6],
            ["11110101", "Another fix, another break", 6],
            ["11111101", "One left", 6],
            ["11111111", "All 8 right, after six rounds", 6]] },
    },
    vague: {
      prose: { v: "Only usually works", c: "butter", note: "Your spec covered what you had thought of. Time zones and opt-out weren't in it, because nobody had asked.",
        r: [["101010", "You write a quick spec yourself; the owner sees the build: 3 of 6 decisions match", 20],
            ["111011", "You rewrite the parts the owner rejected", 15],
            ["111111", "Third build accepted", 12]] },
      examples: { v: "Different problem", c: "rose", note: "Examples show a format clearly, but here nobody had decided what was wanted. Your sample reminders were guesses.",
        r: [["100110", "You invent two sample reminders and ask Claude to match them", 15],
            ["110111", "The owner wants a different channel and timing; new samples", 15],
            ["111111", "Third build accepted", 12]] },
      tests: { v: "Wrong order", c: "rose", note: "The tests locked in your guesses. Claude passed them all, and both the tests and the code were redone.",
        r: [[null, "You write tests for the behaviour you guess at", 15],
            ["100100", "Claude passes every test, but the owner rejects 4 of 6 decisions", 15],
            ["101111", "You rewrite the tests and the code", 20],
            ["111111", "Accepted", 12]] },
      interview: { v: "Best fit (exam answer)", c: "mint", note: "Claude asked before building, so the gaps surfaced before any code. Built once, accepted once.",
        r: [[null, "Claude asks first: who gets reminders, how early, which channel, opt-out, whose time zone, repeats?", 6],
            [null, "You answer four; two go to the product owner, who decides", 8],
            ["111111", "Built once and accepted", 15]] },
      one: { v: "Different problem", c: "rose", note: "One message helps when problems interact. Here the gap was decisions nobody had made, and a longer message can't contain them.",
        r: [["101010", "You put everything you know in one long message; Claude fills the gaps with guesses", 18],
            ["111011", "The owner rejects two; you send corrections", 15],
            ["111111", "Accepted", 12]] },
      seq: { v: "Delays the problem", c: "butter", note: "Each demo surfaced one more decision, and one change undid another. Asking first finds them all before any code.",
        r: [["110001", "Claude builds a first version; demo to the owner", 15],
            ["111001", "Owner asks for SMS: rebuilt", 12],
            ["111101", "Owner asks for opt-out: rebuilt", 12],
            ["111011", "Time zones fixed for travellers; the change undid opt-out", 12],
            ["111111", "Accepted after five demos", 12]] },
    },
    interact: {
      prose: { v: "Only usually works", c: "butter", note: "Sending both bugs together was right, but words left the exact totals open. Add the failing baskets to the one message.",
        r: [["11011010", "You describe both bugs in words, in one message; the exact totals are left to Claude's reading", 10],
            ["11111011", "You correct the reading", 8],
            ["11111111", "All 8 right", 6]] },
      examples: { v: "Also works", c: "mint", note: "Examples make the totals exact, and both bugs went in one message. That single message is what stopped the collision.",
        r: [["11111110", "Both bugs in one message, with the expected totals for three baskets", 10],
            ["11111111", "All 8 right", 5]] },
      tests: { v: "Also works", c: "mint", note: "Tests catch a collision the moment it happens. Sharing both failures in one go is the single-message idea in test form.",
        r: [[null, "You write basket tests first", 12],
            ["11011001", "Both failures shared together", 3],
            ["11111111", "All pass", 4]] },
      interview: { v: "Different problem", c: "rose", note: "Nothing was unclear about what's wanted. The problems interacted, so they needed one message, not questions.",
        r: [[null, "Claude asks how discounts and rounding should work; the ticket already said", 6],
            ["11100110", "Then it fixes the discount alone; the totals move", 8],
            ["11011101", "The rounding fix collides with the discount fix", 8],
            ["11111111", "Consistent after a third round", 8]] },
      one: { v: "Best fit (exam answer)", c: "mint", note: "Both bugs in one message, so Claude fixed them as one change: the discount order and the rounding agree from the start.",
        r: [["11111110", "You send both bugs in one message, with the failing baskets. Claude fixes them as one change", 10],
            ["11111111", "One basket with a stacked coupon left; fixed", 5]] },
      seq: { v: "Fixes collide", c: "rose", note: "Each fix moved the totals the other fix was built on. Four messages of breaking and re-fixing what was right.",
        r: [["11100110", "Message 1: fix the discount order. Totals move, and rounding errors show in new places", 8],
            ["11011001", "Message 2: fix rounding. It rounds the old totals and breaks baskets the first fix had right", 8],
            ["11110110", "Message 3: re-fix the discount to fit the new rounding", 8],
            ["10111111", "Message 4: another collision", 8],
            ["11111111", "Finally consistent", 8]] },
    },
    indep: {
      prose: { v: "Also works", c: "mint", note: "Both bugs are easy to say in a sentence, and you sent them one at a time, which is what mattered here.",
        r: [["11110000", "You describe the typo in a sentence: fixed", 3],
            ["11111111", "Then the search, in a sentence: fixed", 12]] },
      examples: { v: "Overbuilt", c: "butter", note: "Before-and-after examples for a typo and a slow page. Nothing here was a transformation to explain.",
        r: [[null, "You prepare before-and-after examples for both bugs", 10],
            ["11110000", "Typo fixed", 3],
            ["11111111", "Search fixed", 12]] },
      tests: { v: "Also works", c: "mint", note: "A test per bug is good practice. The guide's point for this situation is the order: one issue at a time.",
        r: [[null, "A test for the email text and a timing test for the search", 10],
            ["11110000", "Typo fixed", 3],
            ["11111111", "Search fixed", 12]] },
      interview: { v: "Overbuilt", c: "butter", note: "Questions about two bugs that were already well defined. Nothing to ask.",
        r: [[null, "Claude asks questions about two well-defined bugs", 6],
            ["11110000", "Typo fixed", 3],
            ["11111111", "Search fixed", 12]] },
      one: { v: "Only usually works", c: "butter", note: "It worked, but two unrelated fixes arrived tangled in one change, and the typo waited for the search. Independent problems go one at a time.",
        r: [["11110110", "Both in one message. The change mixes the two, and the search fix misses a case", 12],
            ["11111111", "A second round; the typo fix waits in the same change", 8]] },
      seq: { v: "Best fit (exam answer)", c: "mint", note: "Each bug fixed and checked on its own. A clean history, and neither waits for the other.",
        r: [["11110000", "Message 1: the receipt typo. Fixed and checked", 3],
            ["11111111", "Message 2: the slow search. Fixed and checked", 12]] },
    },
  };
  const TECH_BOXES = ["box-prose", "box-examples", "box-tests", "box-interview", "box-one", "box-seq"];
  const SIT_BOXES = ["q-transform", "q-known", "q-vague", "q-many"];

  const $ = (id) => document.getElementById(id);
  let s = "transform", t = "prose", timers = [];

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
    TECH_BOXES.forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", TECHS[t].where.includes(id) ? "4" : "1.5"); });
    SIT_BOXES.forEach((id) => { const r = $(id); if (r) r.setAttribute("stroke-width", SIT_BOX[s] === id ? "4" : "1.5"); });
  }

  function draw() {
    buttons("sim-s", SITS, s, (k) => (s = k));
    buttons("sim-t", TECHS, t, (k) => (t = k));
    highlight();
    run();
  }

  function run() {
    timers.forEach(clearTimeout);
    timers = [];
    const o = OUT[s][t], S = SITS[s], list = $("sim-rounds");
    list.innerHTML = "";
    let prev = null, breaks = 0, rounds = 0, mins = 0, setup = 0;
    o.r.forEach(([cs, text, min], i) => {
      mins += min;
      const li = document.createElement("li");
      let dots = "";
      if (cs) {
        rounds += 1;
        dots = [...cs].map((ch, j) => {
          const broke = prev && prev[j] === "1" && ch === "0";
          if (broke) breaks += 1;
          const cls = ch === "1" ? "ok" : broke ? "broke" : "bad";
          return `<i class="${cls}" title="${S.cases[j]}: ${ch === "1" ? "right" : broke ? "was right, now broken" : "wrong"}"></i>`;
        }).join("");
        prev = cs;
        li.innerHTML = `<span class="rn">Round ${rounds}</span><span class="dots">${dots}</span><span class="tx">${text}</span><span class="mn">${min} min</span>`;
      } else {
        setup += 1;
        li.className = "pre";
        li.innerHTML = `<span class="rn">Before code</span><span class="dots"><span class="ask">asking or setting up</span></span><span class="tx">${text}</span><span class="mn">${min} min</span>`;
      }
      list.appendChild(li);
      timers.push(setTimeout(() => li.classList.add("show"), 140 * i));
    });
    $("sim-tally").innerHTML = `Rounds of code until all ${S.cases.length} ${S.unit} are right: <b>${rounds}</b> · Right cases that broke later: <b>${breaks || "none"}</b> · Your time: <b>${mins} min</b>`;
    $("sim-verdict").className = "box " + o.c;
    $("sim-verdict").innerHTML = `<span class="chip ${o.c}">${o.v}</span> ${o.note}`;
  }

  window.addEventListener("DOMContentLoaded", draw);
})();
