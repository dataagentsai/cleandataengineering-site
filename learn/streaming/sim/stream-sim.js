/* Streaming simulator for /learn/streaming/sim/ (flow) and /learn/streaming/sim/lanes/ (three lanes).
   Illustrative: counts and delays are a model of the tyre-maker design on /learn/streaming/, not recordings.
   Numbers run on simulated time; dots move at viewing speed. Plain JS, no libraries. */
(function () {
  "use strict";
  var NS = "http://www.w3.org/2000/svg";
  var root = document.getElementById("ssim");
  if (!root) return;
  var MODE = root.getAttribute("data-mode") || "flow";

  /* ------------------------------------------------------------ bindings */
  var BINDINGS = {
    "aws-dbx": {
      name: "AWS + Databricks", rec: true,
      gw: "SiteWise Edge + IoT Core", api: "API Gateway, Firehose", cdc: "DMS + S3 file drops",
      log: "Kinesis Data Streams", land: "S3 landing, Auto Loader", fast: "Managed Flink", live: "DynamoDB",
      push: "API Gateway WebSocket", ui1: "Live board (web app)", ingest: "Lakeflow streaming table",
      bronze: "Bronze (Delta)", silver: "Silver (Delta, SCD)", gold: "Gold (Delta)",
      ui2: "Power BI on Databricks SQL", batch: "Lakeflow Jobs, nightly", ui3: "Power BI daily report",
      note: "Recommended. The live lane is AWS-native; the platform lane is Databricks. Power BI reads gold through Databricks SQL (DirectQuery with automatic page refresh)."
    },
    "aws": {
      name: "AWS only",
      gw: "SiteWise Edge + IoT Core", api: "API Gateway, Firehose", cdc: "DMS + S3 file drops",
      log: "Kinesis Data Streams", land: "S3 landing", fast: "Managed Flink", live: "DynamoDB",
      push: "API Gateway WebSocket", ui1: "Live board (web app)", ingest: "Firehose to S3 Tables",
      bronze: "Bronze (Iceberg)", silver: "Silver (Glue ETL)", gold: "Gold (Glue, Athena)",
      ui2: "Power BI via Athena, or QuickSight", batch: "Glue jobs, nightly", ui3: "Daily report (QuickSight)",
      note: "Fewest vendors. Silver and gold jobs, Iceberg upkeep and the semantic layer are yours to build."
    },
    "az-dbx": {
      name: "Azure + Databricks",
      gw: "IoT Edge + IoT Hub", api: "API Management, Event Hubs", cdc: "Lakeflow Connect + ADLS drops",
      log: "Event Hubs", land: "ADLS landing, Auto Loader", fast: "Fabric Eventstream", live: "Fabric Eventhouse",
      push: "Real-Time Dashboard refresh", ui1: "Power BI on Eventhouse (Real-Time Intelligence)", ingest: "Lakeflow streaming table",
      bronze: "Bronze (Delta)", silver: "Silver (Delta, SCD)", gold: "Gold (Delta)",
      ui2: "Power BI on Databricks SQL", batch: "Lakeflow Jobs, nightly", ui3: "Power BI daily report",
      note: "Power BI's old streaming datasets are being retired (no new ones after 31 Oct 2027); live Power BI goes through Fabric Real-Time Intelligence instead."
    },
    "dbx-only": {
      name: "Databricks only (not recommended)",
      gw: "Zerobus Ingest (straight to Delta)", api: "Zerobus Ingest", cdc: "Lakeflow Connect",
      log: "No shared event log", land: "Volumes, Auto Loader", fast: "Spark real-time mode", live: "Lakebase",
      push: "Databricks App (polls)", ui1: "Live board (Databricks App)", ingest: "Lakeflow streaming table",
      bronze: "Bronze (Delta)", silver: "Silver (Delta, SCD)", gold: "Gold (Delta)",
      ui2: "Power BI on Databricks SQL", batch: "Lakeflow Jobs, nightly", ui3: "Power BI daily report",
      note: "One vendor, but no shared event log: the live lane reads the bronze table, replay is from Delta only, and real-time mode needs an always-on fixed cluster."
    }
  };

  /* ------------------------------------------------------------ helpers */
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function $(id) { return document.getElementById(id); }
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function clock(t) { var d = Math.floor(t / 86400), s = t - d * 86400; return pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s / 60) % 60) + ":" + pad(Math.floor(s) % 60); }
  function hm(t) { var s = ((t % 86400) + 86400) % 86400; return pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s / 60) % 60); }
  function num(n) { n = Math.round(n); return n.toLocaleString("en-US"); }
  function dur(s) {
    if (s < 0) s = 0;
    if (s < 60) return s.toFixed(s < 10 ? 1 : 0) + " s";
    if (s < 3600) return (s / 60).toFixed(s < 600 ? 1 : 0) + " min";
    return (s / 3600).toFixed(1) + " h";
  }
  function wrapText(t, max) {
    var words = t.split(" "), lines = [], cur = "";
    words.forEach(function (w) { if ((cur + " " + w).trim().length > max && cur) { lines.push(cur); cur = w; } else cur = (cur + " " + w).trim(); });
    if (cur) lines.push(cur);
    return lines;
  }

  var state = { binding: "aws-dbx", route: "both", speed: 60, paused: false };
  var feedEl = $("ssim-feed");
  function feed(msg, kind) {
    if (!feedEl) return;
    var li = document.createElement("li");
    li.innerHTML = "<b>" + hm(SIM.t) + "</b> " + msg;
    if (kind) li.className = kind;
    feedEl.insertBefore(li, feedEl.firstChild);
    while (feedEl.children.length > 40) feedEl.removeChild(feedEl.lastChild);
  }

  /* ------------------------------------------------------------ drawing */
  var svg = $("ssim-svg");
  var boxes = {};
  function drawBox(id, x, y, w, h, role, title, lane) {
    var g = el("g", { "class": "bx " + (lane || ""), "data-id": id }, svg);
    el("rect", { x: x, y: y, width: w, height: h, rx: 10 }, g);
    var tt = el("text", { x: x + 8, y: y + 18, "class": "bt" }, g); tt.textContent = title;
    var pr = el("text", { x: x + 8, y: y + 35, "class": "bp" }, g);
    var small = h < 40;
    var c1 = el("text", { x: x + 8, y: y + h - 26, "class": "bc" }, g);
    var c2 = small ? el("text", { x: x + w - 8, y: y + 20, "class": "bc", "text-anchor": "end" }, g) : el("text", { x: x + 8, y: y + h - 10, "class": "bc" }, g);
    boxes[id] = { g: g, x: x, y: y, w: w, h: h, role: role, pr: pr, c1: c1, c2: c2, lane: lane };
    return boxes[id];
  }
  function setProduct(b) {
    var p = b.role ? BINDINGS[state.binding][b.role] : "";
    while (b.pr.firstChild) b.pr.removeChild(b.pr.firstChild);
    var lines = wrapText(p || "", Math.max(14, Math.floor(b.w / 7.2)));
    lines.slice(0, 2).forEach(function (ln, i) { var ts = el("tspan", { x: b.x + 8, dy: i ? 14 : 0 }, b.pr); ts.textContent = ln; });
  }
  function count(id, a, b) { if (!boxes[id]) return; boxes[id].c1.textContent = a || ""; boxes[id].c2.textContent = b || ""; }
  function line(pts, cls) {
    el("polyline", { points: pts.map(function (p) { return p.join(","); }).join(" "), "class": "wire " + (cls || "") }, svg);
  }
  function caption(x, y, t, cls) { var e = el("text", { x: x, y: y, "class": "cap " + (cls || "") }, svg); e.textContent = t; return e; }

  /* ------------------------------------------------------------ particles */
  var dots = [], dotLayer;
  var SHAPE = { press: "circle", tyre: "ring", app: "tri", cdc: "sq", lims: "dia", run: "circle", bad: "x" };
  function makeShape(kind) {
    var g = el("g", { "class": "dot " + kind }, dotLayer), s = SHAPE[kind] || "circle";
    if (s === "circle") el("circle", { r: 4.5 }, g);
    else if (s === "ring") el("circle", { r: 4.5, "class": "ring" }, g);
    else if (s === "sq") el("rect", { x: -4, y: -4, width: 8, height: 8 }, g);
    else if (s === "tri") el("path", { d: "M0,-5 L5,4 L-5,4 Z" }, g);
    else if (s === "dia") el("path", { d: "M0,-6 L5,0 L0,6 L-5,0 Z" }, g);
    else el("path", { d: "M-4,-4 L4,4 M4,-4 L-4,4", "class": "xs" }, g);
    return g;
  }
  function launch(kind, pts, speedPx, onDone) {
    if (dots.length > 260) return;
    var g = makeShape(kind);
    var d = { g: g, pts: pts, i: 0, f: 0, v: speedPx || 260, done: onDone };
    g.setAttribute("transform", "translate(" + pts[0][0] + "," + pts[0][1] + ")");
    dots.push(d);
  }
  function stepDots(dtReal) {
    for (var k = dots.length - 1; k >= 0; k--) {
      var d = dots[k], move = d.v * dtReal;
      while (move > 0 && d.i < d.pts.length - 1) {
        var a = d.pts[d.i], b = d.pts[d.i + 1], L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1, rem = (1 - d.f) * L;
        if (move >= rem) { move -= rem; d.i++; d.f = 0; } else { d.f += move / L; move = 0; }
      }
      if (d.i >= d.pts.length - 1) {
        dotLayer.removeChild(d.g); dots.splice(k, 1);
        if (d.done) d.done();
        continue;
      }
      var p = d.pts[d.i], q = d.pts[d.i + 1];
      d.g.setAttribute("transform", "translate(" + (p[0] + (q[0] - p[0]) * d.f) + "," + (p[1] + (q[1] - p[1]) * d.f) + ")");
    }
  }

  /* ------------------------------------------------------------ shared sim clock */
  var SIM = { t: 0 };
  var spawnAcc = {};
  function every(key, realMs, dtReal, fn) {
    spawnAcc[key] = (spawnAcc[key] || 0) + dtReal * 1000;
    while (spawnAcc[key] >= realMs) { spawnAcc[key] -= realMs; fn(); }
  }
  function routeHas(lane) { return state.route === "both" || (lane === "fast" ? state.route === "direct" : state.route === "medallion"); }

  /* =================================================================== FLOW MODE */
  function flow() {
    svg.setAttribute("viewBox", "0 0 1200 500");
    var defs = el("defs", {}, svg), mk = el("marker", { id: "ah", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": "ahp" }, mk);
    el("rect", { x: 548, y: 6, width: 646, height: 170, rx: 12, "class": "lane fast-lane" }, svg);
    el("rect", { x: 548, y: 222, width: 646, height: 270, rx: 12, "class": "lane nrt-lane" }, svg);
    caption(560, 24, "FAST LANE · seconds · acts now · never writes gold", "fast");
    caption(560, 240, "PLATFORM LANE · runs every 15 minutes · the number of record", "nrt");
    caption(12, 20, "SOURCES"); caption(182, 20, "FRONT DOOR"); caption(362, 20, "EVENT LOG / LANDING");

    drawBox("press", 10, 30, 150, 64, null, "Curing presses (IoT)");
    drawBox("tyre", 10, 104, 150, 64, null, "Connected tyres (IoT)");
    drawBox("app", 10, 250, 150, 64, null, "Dealer app events");
    drawBox("cdc", 10, 324, 150, 64, null, "SAP, MES changes (CDC)");
    drawBox("lims", 10, 398, 150, 64, null, "Lab result files (LIMS)");
    drawBox("gw", 180, 30, 160, 138, "gw", "Plant gateway, device entry");
    drawBox("api", 180, 250, 160, 64, "api", "App events entry");
    drawBox("cdcin", 180, 324, 160, 138, "cdc", "Change capture, file drops");
    drawBox("log", 360, 30, 165, 138, "log", "Event log (kept 7 days)");
    drawBox("land", 360, 250, 165, 212, "land", "File landing");
    drawBox("fast", 560, 36, 145, 100, "fast", "Live processor", "fastb");
    drawBox("live", 718, 36, 140, 100, "live", "Live store (48 h)", "fastb");
    drawBox("push", 871, 36, 140, 100, "push", "Push to screens", "fastb");
    drawBox("ui1", 1024, 36, 162, 100, "ui1", "LIVE SCREEN", "fastb ui");
    drawBox("dlq", 560, 140, 145, 30, null, "Dead letter", "fastb small");
    drawBox("ingest", 560, 252, 120, 110, "ingest", "Lake ingest", "nrtb");
    drawBox("bronze", 692, 252, 112, 110, "bronze", "Bronze", "nrtb");
    drawBox("silver", 816, 252, 112, 110, "silver", "Silver", "nrtb");
    drawBox("gold", 940, 252, 112, 110, "gold", "Gold", "nrtb");
    drawBox("ui2", 1064, 252, 122, 110, "ui2", "REPORT", "nrtb ui");
    drawBox("quar", 816, 368, 112, 30, null, "Quarantine", "nrtb small");
    var runBox = el("text", { x: 560, y: 424, "class": "bc runinfo", id: "ssim-runinfo" }, svg); runBox.textContent = "";
    var pile = el("text", { x: 560, y: 442, "class": "bc runinfo", id: "ssim-pile" }, svg); pile.textContent = "";
    var hourInfo = el("text", { x: 560, y: 460, "class": "bc runinfo", id: "ssim-hourinfo" }, svg); hourInfo.textContent = "";

    var P = {
      press: [[160, 62], [180, 62]], tyre: [[160, 136], [180, 136]],
      gwlog: [[340, 99], [360, 99]], app: [[160, 282], [180, 282], [340, 282], [360, 282]],
      cdc: [[160, 356], [180, 356], [340, 356], [360, 356]], lims: [[160, 430], [180, 430], [340, 430], [360, 430]],
      logfast: [[525, 86], [560, 86]], fastlane: [[705, 86], [718, 86], [858, 86], [871, 86], [1011, 86], [1024, 86]],
      logingest: [[525, 150], [540, 150], [540, 300], [560, 300]], landingest: [[525, 330], [545, 330], [560, 320]],
      todlq: [[632, 136], [632, 152]],
      run: [[680, 307], [692, 307], [804, 307], [816, 307]], toquar: [[872, 362], [872, 378]],
      hour: [[928, 307], [940, 307], [1052, 307], [1064, 307]]
    };
    line([[160, 62], [180, 62]]); line([[160, 136], [180, 136]]); line([[340, 99], [360, 99]], "arr");
    line([[160, 282], [180, 282]]); line([[340, 282], [360, 282]], "arr");
    line([[160, 356], [180, 356]]); line([[340, 356], [360, 356]], "arr");
    line([[160, 430], [180, 430]]); line([[340, 430], [360, 430]], "arr");
    line(P.logfast, "arr fastw"); line([[705, 86], [718, 86]], "arr fastw"); line([[858, 86], [871, 86]], "arr fastw"); line([[1011, 86], [1024, 86]], "arr fastw");
    line(P.logingest, "arr nrtw"); line(P.landingest, "arr nrtw");
    line([[680, 307], [692, 307]], "arr nrtw"); line([[804, 307], [816, 307]], "arr nrtw"); line([[928, 307], [940, 307]], "arr nrtw"); line([[1052, 307], [1064, 307]], "arr nrtw");
    dotLayer = el("g", {}, svg);
    Object.keys(boxes).forEach(function (k) { setProduct(boxes[k]); });

    /* model */
    var S = {
      on: { press: true, tyre: false, app: true, cdc: true, lims: true },
      rate: { press: 300, tyre: 3333, app: 2, cdc: 5, lims: 0 },
      gen: { press: 0, tyre: 0, app: 0, cdc: 0, lims: 0 },
      gwBuf: 0, gwOfflineUntil: -1, gwOfflineSince: 0, lateCount: 0,
      logIn: 0, fastOut: 0, fastLag: 0, fastDownUntil: -1, fastLat: 2.1, dlq: 0, liveWrites: 0, pushes: 0, liveAsOf: 0,
      dupUntil: -1, badUntil: -1, skipNext: false,
      pend: [], landPend: [], landFiles: 0,
      bronze: 0, silver: 0, gold: 0, dupRemoved: 0, quar: 0,
      running: false, runEnd: 0, runRows: 0, runOldest: 0, lastSilverLat: null, lastSilverAt: null,
      hourSum: {}, hourN: {}, lastGoldHour: null, lastGoldAt: null, lastGoldLat: null, goldVal: null,
      temp: 182, lastRunSlot: null, lastHourSlot: null, frac: {}
    };
    SIM.t = 9 * 3600 + 52 * 60; // 09:52
    S.lastRunSlot = Math.floor(SIM.t / 900); S.lastHourSlot = Math.floor((SIM.t - 900) / 3600);
    S.runOldest = SIM.t;

    function add(list, t, n) { if (n <= 0) return; var last = list[list.length - 1]; if (last && t - last.t < 60) last.n += n; else list.push({ t: t, n: n }); }
    function take(list) { var n = 0, w = 0; list.forEach(function (b) { n += b.n; w += b.n * b.t; }); list.length = 0; return { n: n, tAvg: n ? w / n : SIM.t }; }
    function emit(src, dt) {
      var x = S.rate[src] * dt + (S.frac[src] || 0), n = Math.floor(x); S.frac[src] = x - n; return n;
    }

    function tick(dt) {
      var t0 = SIM.t; SIM.t += dt; var t = SIM.t;
      S.temp += (Math.random() - 0.5) * 0.15 * Math.sqrt(dt); S.temp += (182 - S.temp) * 0.002 * dt;
      var hr = Math.floor(t / 3600);
      /* IoT */
      var iot = 0;
      ["press", "tyre"].forEach(function (s) { if (S.on[s]) { var n = emit(s, dt); S.gen[s] += n; iot += n; } });
      var offline = t < S.gwOfflineUntil;
      if (offline) { S.gwBuf += iot; iot = 0; }
      else if (S.gwBuf > 0) { var fl = Math.min(S.gwBuf, 3000 * dt); S.gwBuf -= fl; iot += fl; S.lateCount += fl; }
      S.hourSum[hr] = (S.hourSum[hr] || 0) + S.temp * dt; S.hourN[hr] = (S.hourN[hr] || 0) + dt;
      var dup = t < S.dupUntil ? iot * 0.05 : 0, bad = t < S.badUntil ? iot * 0.01 : 0;
      var inLog = iot + dup;
      S.logIn += inLog;
      /* fast lane */
      if (routeHas("fast")) {
        if (t < S.fastDownUntil) { S.fastLag += inLog; }
        else {
          var cap = (S.rate.press + (S.on.tyre ? S.rate.tyre : 0)) * 10 * dt + 1;
          var work = inLog + S.fastLag, done = Math.min(work, cap);
          S.fastLag = work - done;
          var good = Math.max(0, done - dup - bad);
          S.dlq += bad; S.fastOut += good;
          S.liveWrites += Math.min(good, 25 * dt);
          S.pushes += 50 * dt;
          if (good > 0 && !offline) S.liveAsOf = t - S.fastLat;
          var rate = (S.rate.press + (S.on.tyre ? S.rate.tyre : 0)) || 1;
          S.fastLat = 2.1 + S.fastLag / (rate * 9);
        }
      }
      /* platform lane */
      if (routeHas("nrt")) {
        add(S.pend, t, inLog);
        ["app", "cdc"].forEach(function (s) { if (S.on[s]) { var n = emit(s, dt); S.gen[s] += n; add(S.landPend, t, n); } });
        /* LIMS: one file per hour at :05, handled by a file arrival trigger */
        if (S.on.lims && Math.floor((t - 300) / 3600) !== Math.floor((t0 - 300) / 3600)) {
          S.gen.lims += 1200; S.landFiles++; S.bronze += 1200; S.silver += 1180; S.quar += 20;
          feed("A lab results file landed; the file arrival trigger loaded it into bronze and silver about 2 minutes later.");
          if (state.visible) launch("lims", P.lims.concat([[525, 430]]), 260);
        }
      } else { S.pend.length = 0; }
      /* 15-minute platform runs */
      var slot = Math.floor(t / 900);
      if (slot !== S.lastRunSlot) {
        S.lastRunSlot = slot;
        if (!routeHas("nrt")) { /* lane off */ }
        else if (S.skipNext) { S.skipNext = false; feed("The " + hm(slot * 900) + " platform run was skipped. Nothing is lost: the next run reads everything new.", "bad"); }
        else if (!S.running) {
          var a = take(S.pend), b = take(S.landPend), n = a.n + b.n;
          var oldest = Math.min(a.n ? a.tAvg : t, b.n ? b.tAvg : t);
          S.running = true; S.runRows = n; S.runA = a.n; S.runB = b.n; S.runOldest = oldest;
          S.runEnd = t + 180 + n / 1e6 * 30;
          feed("Platform run started: " + num(a.n) + " stream readings and " + num(b.n) + " rows from landed files.");
          burst("run", 10);
        }
      }
      if (S.running && t >= S.runEnd) {
        S.running = false;
        S.bronze += S.runRows;
        var dupsIn = S.pendingDups || 0, badIn = S.pendingBad || 0; S.pendingDups = 0; S.pendingBad = 0;
        S.dupRemoved += dupsIn; S.quar += badIn;
        S.silver += S.runRows - dupsIn - badIn;
        S.lastSilverLat = t - S.runOldest; S.lastSilverAt = t;
        feed("Run finished: bronze and silver are up to date. Silver is about " + dur(S.lastSilverLat) + " behind the average reading" + (dupsIn ? ", " + num(dupsIn) + " duplicates removed" : "") + (badIn ? ", " + num(badIn) + " bad rows quarantined" : "") + ".");
      }
      S.pendingDups = (S.pendingDups || 0) + dup; S.pendingBad = (S.pendingBad || 0) + bad;
      /* hourly gold job at :15 */
      var hslot = Math.floor((t - 900) / 3600);
      if (hslot !== S.lastHourSlot) {
        S.lastHourSlot = hslot;
        if (routeHas("nrt")) {
          var h = hslot - 1, avg = S.hourN[h] ? S.hourSum[h] / S.hourN[h] : S.temp;
          S.gold += 1500 + (S.on.tyre ? 200000 : 0);
          S.goldVal = avg; S.lastGoldHour = h; S.lastGoldAt = t + 240; S.lastGoldLat = t + 240 - (h * 3600 + 1800);
          S.goldComplete = !(S.gwBuf > 0 || (S.lastSilverAt || 0) < h * 3600 + 3600);
          feed("Gold hour " + hm(h * 3600) + " to " + hm(h * 3600 + 3600) + " built at :15 by window recompute" + (S.goldComplete ? " and marked complete." : ", marked provisional: some input has not arrived yet.") );
          setTimeout(function () { burst("hour", 6); }, 50);
        }
      }
    }

    function burst(kind, n) {
      if (!state.visible) return;
      for (var i = 0; i < n; i++) (function (i) {
        setTimeout(function () { launch("run", kind === "run" ? P.run : P.hour, 300); }, i * 90);
      })(i);
      if (kind === "run" && (S.pendingBad || 0) > 0) setTimeout(function () { launch("bad", P.run.slice(0, 3).concat(P.toquar), 260); }, 300);
    }

    /* visuals per source, real time */
    function visuals(dtReal) {
      var offline = SIM.t < S.gwOfflineUntil, fastDown = SIM.t < S.fastDownUntil;
      if (S.on.press) every("press", 260, dtReal, function () {
        var path = P.press.slice();
        if (offline) { launch("press", path, 240); return; }
        path = path.concat([[340, 62], [340, 99]]).concat(P.gwlog).concat([[525, 99]]);
        launch("press", path, 260, function () { split("press"); });
      });
      if (S.on.tyre) every("tyre", 200, dtReal, function () {
        var path = P.tyre.slice();
        if (offline) { launch("tyre", path, 240); return; }
        path = path.concat([[340, 136], [340, 99]]).concat(P.gwlog).concat([[525, 99]]);
        launch("tyre", path, 260, function () { split("tyre"); });
      });
      if (routeHas("nrt")) {
        if (S.on.app) every("app", 900, dtReal, function () { launch("app", P.app.concat([[525, 282]]), 220); });
        if (S.on.cdc) every("cdc", 1300, dtReal, function () { launch("cdc", P.cdc.concat([[525, 356]]), 220); });
      }
      function split(kind) {
        if (routeHas("fast") && !fastDown) launch(kind, P.logfast.concat(P.fastlane), 320);
        if (routeHas("nrt")) launch(kind, P.logingest, 260);
      }
      if (!fastDown && S.fastLag > 0 && routeHas("fast")) every("catch", 120, dtReal, function () { launch("press", P.logfast.concat(P.fastlane), 420); });
      if (SIM.t < S.badUntil && routeHas("fast")) every("bad", 700, dtReal, function () { launch("bad", P.logfast.concat(P.todlq), 260); });
    }

    function render() {
      var b = BINDINGS[state.binding];
      $("ssim-clock").textContent = clock(SIM.t);
      count("press", S.on.press ? "300 readings/s" : "off", "sent " + num(S.gen.press));
      count("tyre", S.on.tyre ? "3,333 readings/s" : "off (toggle below)", S.on.tyre ? "sent " + num(S.gen.tyre) : "");
      count("app", S.on.app ? "2 events/s" : "off", "sent " + num(S.gen.app));
      count("cdc", S.on.cdc ? "5 changes/s" : "off", "sent " + num(S.gen.cdc));
      count("lims", S.on.lims ? "one file an hour" : "off", "rows " + num(S.gen.lims));
      count("gw", SIM.t < S.gwOfflineUntil ? "OFFLINE, buffering" : (S.gwBuf > 0 ? "sending buffer" : "batches each second"), S.gwBuf > 0 ? "buffered " + num(S.gwBuf) : "late readings " + num(S.lateCount));
      count("api", "", "");
      count("cdcin", "", "files landed " + num(S.landFiles + Math.floor(S.gen.cdc / 1500)));
      count("log", b.log === "No shared event log" ? "events go straight to bronze" : "in " + num(S.logIn), "");
      count("land", "for next run", num(S.landPend.reduce(function (a, x) { return a + x.n; }, 0)) + " rows");
      var fastDown = SIM.t < S.fastDownUntil;
      count("fast", fastDown ? "RESTARTING from checkpoint" : (S.fastLag > 0 ? "catching up" : "windows, limits"), "lag " + num(S.fastLag));
      count("live", "latest per press", "writes " + num(S.liveWrites));
      count("push", "≤1/s per screen", "sent " + num(S.pushes));
      var stale = SIM.t - S.liveAsOf;
      count("ui1", "Press 17 " + S.temp.toFixed(1) + "°C", routeHas("fast") ? (stale > 30 ? "STALE: " + dur(stale) + " old" : "live, " + dur(Math.max(stale, S.fastLat)) + " behind") : "lane off");
      count("dlq", "", num(S.dlq));
      var pend = S.pend.reduce(function (a, x) { return a + x.n; }, 0);
      count("ingest", S.running ? "RUNNING" : "next run " + hm((S.lastRunSlot + 1) * 900), "waiting " + num(pend));
      count("bronze", "kept forever", num(S.bronze));
      count("silver", "deduplicated", num(S.silver));
      count("gold", "hour facts", num(S.gold));
      count("ui2", S.goldVal != null ? hm(S.lastGoldHour * 3600) + " hr " + S.goldVal.toFixed(1) + "°C" : "first hour at :15", S.goldVal != null ? (S.goldComplete ? "complete" : "provisional") : "");
      count("quar", "", num(S.quar));
      $("ssim-runinfo").textContent = S.lastSilverAt ? "Last run " + hm(S.lastSilverAt) + ": silver ≈ " + dur(S.lastSilverLat) + " behind" : "No platform run yet";
      $("ssim-pile").textContent = "Duplicates removed " + num(S.dupRemoved) + " · late readings " + num(S.lateCount);
      $("ssim-hourinfo").textContent = S.lastGoldAt ? "Gold hour ready ≈ " + dur(S.lastGoldLat) + " after the middle of that hour" : "Gold builds each hour at :15";
      $("ssim-lat-fast").textContent = routeHas("fast") ? (fastDown ? "paused" : dur(S.fastLat)) : "off";
      $("ssim-lat-silver").textContent = routeHas("nrt") ? (S.lastSilverLat != null ? dur(S.lastSilverLat) : "waiting for first run") : "off";
      $("ssim-lat-gold").textContent = routeHas("nrt") ? (S.lastGoldLat != null ? dur(S.lastGoldLat) : "at :15") : "off";
      svg.classList.toggle("no-fast", !routeHas("fast"));
      svg.classList.toggle("no-nrt", !routeHas("nrt"));
      ["app", "cdc", "lims"].forEach(function (k) { boxes[k].g.classList.toggle("off", !S.on[k] || !routeHas("nrt")); });
      ["press", "tyre"].forEach(function (k) { boxes[k].g.classList.toggle("off", !S.on[k]); });
    }

    /* controls */
    document.querySelectorAll("[data-src]").forEach(function (c) {
      c.checked = S.on[c.getAttribute("data-src")];
      c.addEventListener("change", function () { S.on[c.getAttribute("data-src")] = c.checked; feed((c.checked ? "Turned on: " : "Turned off: ") + c.parentNode.textContent.trim() + "."); });
    });
    var inc = {
      offline: function () { S.gwOfflineUntil = SIM.t + 600; feed("A plant gateway lost its network for 10 minutes. It buffers readings on its own disk and sends them when it is back; the live screen shows stale data meanwhile.", "bad"); },
      restart: function () { S.fastDownUntil = SIM.t + 120; feed("The live processor restarted. It resumes from its last checkpoint and catches up from the event log; nothing is lost.", "bad"); },
      dups: function () { S.dupUntil = SIM.t + 300; feed("Senders resend 5% of messages for 5 minutes. The live lane drops repeats within a short window; silver removes them by reading id.", "bad"); },
      bad: function () { S.badUntil = SIM.t + 300; feed("1% of messages are broken for 5 minutes. The live lane sends them to a dead-letter folder; silver puts them in quarantine with a reason. Nothing stops.", "bad"); },
      skip: function () { S.skipNext = true; feed("The next 15-minute platform run will be skipped (a failed run).", "bad"); }
    };
    document.querySelectorAll("[data-inc]").forEach(function (b) { b.addEventListener("click", function () { inc[b.getAttribute("data-inc")](); }); });
    feed("Simulation started at " + hm(SIM.t) + ". Presses send readings; the first platform run starts at 10:00.");
    return { tick: tick, visuals: visuals, render: render, maxStep: 2 };
  }

  /* =================================================================== LANES MODE */
  function lanes() {
    svg.setAttribute("viewBox", "0 0 1200 520");
    var defs = el("defs", {}, svg), mk = el("marker", { id: "ah", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 6, markerHeight: 6, orient: "auto" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", "class": "ahp" }, mk);
    el("rect", { x: 175, y: 28, width: 820, height: 120, rx: 12, "class": "lane fast-lane" }, svg);
    el("rect", { x: 355, y: 172, width: 640, height: 150, rx: 12, "class": "lane nrt-lane" }, svg);
    el("rect", { x: 355, y: 330, width: 640, height: 150, rx: 12, "class": "lane batch-lane" }, svg);
    caption(185, 44, "FAST · seconds · AWS or streaming service only, never calls the platform", "fast");
    caption(365, 188, "NEAR REAL TIME · streams every 15 min, gold hourly", "nrt");
    caption(365, 474, "BATCH · nightly masters and daily totals", "batch");
    caption(1010, 20, "SCREENS (4)");

    drawBox("iot", 10, 52, 150, 180, null, "Presses (IoT)");
    drawBox("ent", 10, 340, 150, 120, null, "SAP, MES, LIMS");
    drawBox("log", 190, 52, 150, 180, "log", "Event log (1)");
    drawBox("fast", 370, 56, 260, 84, "fast", "Live processor", "fastb");
    drawBox("live", 660, 56, 140, 84, "live", "Live store", "fastb");
    drawBox("ingest", 370, 200, 120, 100, "ingest", "Every 15 min", "nrtb");
    drawBox("extract", 370, 360, 120, 100, "batch", "Nightly 01:00", "batchb");
    drawBox("bronze", 505, 200, 110, 260, "bronze", "Bronze", "shared");
    drawBox("silver", 630, 200, 110, 260, "silver", "Silver", "shared");
    drawBox("gold", 755, 200, 230, 260, "gold", "Gold (3): streams meet batch", "shared");
    drawBox("ui1", 1010, 30, 180, 110, "ui1", "Live screen", "fastb ui");
    drawBox("ui2", 1010, 200, 180, 120, "ui2", "Hourly report", "nrtb ui");
    drawBox("ui3", 1010, 340, 180, 120, "ui3", "Daily report", "batchb ui");
    line([[160, 142], [190, 142]], "arr"); line([[340, 98], [370, 98]], "arr fastw"); line([[630, 98], [660, 98]], "arr fastw"); line([[800, 98], [1010, 85]], "arr fastw");
    line([[340, 200], [352, 200], [352, 250], [370, 250]], "arr nrtw"); line([[160, 410], [370, 410]], "arr batchw");
    line([[490, 250], [505, 250]], "arr nrtw"); line([[490, 410], [505, 410]], "arr batchw");
    line([[615, 330], [630, 330]], "arr"); line([[740, 330], [755, 330]], "arr");
    line([[985, 260], [1010, 260]], "arr nrtw"); line([[985, 400], [1010, 400]], "arr batchw");
    line([[160, 380], [175, 380], [175, 300], [370, 300]], "arr nrtw dotted"); // LIMS via file trigger
    line([[685, 200], [685, 168], [560, 168], [560, 140]], "arr ref"); // reference data up (2)
    caption(570, 163, "(2) reference data copied up: limits, press list", "ref");
    caption(178, 296, "LIMS files: file trigger", "small");
    dotLayer = el("g", {}, svg);
    /* hour chips inside gold */
    var chips = [];
    for (var i = 0; i < 6; i++) {
      var cx = 765 + (i % 2) * 108, cy = 262 + Math.floor(i / 2) * 46;
      var g = el("g", { "class": "chip" }, svg);
      var r = el("rect", { x: cx, y: cy, width: 102, height: 40, rx: 7 }, g);
      var t1 = el("text", { x: cx + 6, y: cy + 16, "class": "bc" }, g), t2 = el("text", { x: cx + 6, y: cy + 32, "class": "bc" }, g);
      chips.push({ g: g, r: r, t1: t1, t2: t2 });
    }
    Object.keys(boxes).forEach(function (k) { setProduct(boxes[k]); });

    var S = {
      hours: {}, dimsOK: true, dimsAt: null, refAt: null, newPress: false, newPressSeen: false,
      batchFail: false, limsDelay: 2 * 3600, gwOffline: null, lastRun: null, lastHourJob: null,
      daily: { day: null, at: null, late: false }, temp: 182, fastLat: 2.1, liveAsOf: 0, lastNight: null,
      silverAt: null
    };
    SIM.t = 0 * 86400 + 5 * 3600 + 40 * 60; // day 0, 05:40
    for (var h = -1; h < 5; h++) S.hours[h] = { st: "complete", lims: true, val: 181 + Math.random() * 2, at: 0 };
    S.hours[4] = { st: "provisional", lims: false, val: 182.3, at: 0, short: "lab" };
    S.dimsAt = 2 * 3600; S.refAt = 5 * 3600 + 30 * 60; S.silverAt = 5 * 3600 + 33 * 60;
    S.lastRun = Math.floor(SIM.t / 900); S.lastHourJob = Math.floor((SIM.t - 900) / 3600); S.lastNight = Math.floor((SIM.t - 3600) / 86400);
    S.daily = { day: -1, at: 6 * 3600, late: false };

    function hourLabel(h) { return hm(h * 3600) + "–" + hm(h * 3600 + 3600); }
    function tick(dt) {
      var t0 = SIM.t; SIM.t += dt; var t = SIM.t;
      S.temp += (Math.random() - 0.5) * 0.2 * Math.sqrt(dt / 10); S.temp += (182 - S.temp) * 0.0005 * dt;
      var offline = !!(S.gwOffline && t >= S.gwOffline.from && t < S.gwOffline.to);
      if (!offline) S.liveAsOf = t - S.fastLat;
      /* new press commissioned at 08:00 on day 0 */
      if (!S.newPress && t >= 8 * 3600) { S.newPress = true; feed("Press P-1501 was commissioned at 08:00. Its readings flow at once; it joins the press list in SAP today.", ""); }
      /* every 15 minutes: platform run */
      var slot = Math.floor(t / 900);
      if (slot !== S.lastRun) {
        S.lastRun = slot;
        if (routeHas("nrt")) {
          S.silverAt = t + 180; S.refAt = t + 180;
          if (state.visible) for (var i = 0; i < 6; i++) (function (i) { setTimeout(function () { launch("run", [[340, 200], [352, 200], [352, 250], [490, 250], [505, 250], [615, 250], [630, 250], [740, 250]], 340); }, i * 70); })(i);
          if (!offline && S.gwOffline && t >= S.gwOffline.to && !S.gwOffline.done) {
            S.gwOffline.done = true;
            var hh = Math.floor(S.gwOffline.from / 3600);
            if (S.hours[hh] && S.hours[hh].st !== "running") { S.hours[hh].st = "restated"; S.hours[hh].at = t; }
            feed("The buffered readings from the outage arrived; gold hour " + hourLabel(hh) + " was recomputed and marked restated.", "bad");
          }
        }
      }
      /* hourly gold at :15 */
      var hs = Math.floor((t - 900) / 3600);
      if (hs !== S.lastHourJob) {
        S.lastHourJob = hs;
        if (routeHas("nrt")) {
          hs = hs - 1;
          var hr = S.hours[hs] || (S.hours[hs] = { lims: false });
          hr.val = S.temp + (Math.random() - 0.5); hr.at = t;
          var gwHole = S.gwOffline && S.gwOffline.from < hs * 3600 + 3600 && S.gwOffline.to > hs * 3600 && !S.gwOffline.done;
          hr.st = (hr.lims && S.dimsOK && !gwHole) ? "complete" : "provisional";
          hr.why = !hr.lims ? "waiting for lab results" : (!S.dimsOK ? "press list is stale" : (gwHole ? "plant readings missing" : ""));
          hr.short = !hr.lims ? "lab" : (!S.dimsOK ? "dims" : (gwHole ? "gap" : ""));
          feed("Gold hour " + hourLabel(hs) + " built: " + hr.st + (hr.why ? " (" + hr.why + ")" : "") + ".");
          if (state.visible) for (var j = 0; j < 4; j++) (function (j) { setTimeout(function () { launch("run", [[740, 250], [755, 250], [985, 260], [1010, 260]], 340); }, j * 90); })(j);
        }
      }
      /* LIMS results for hour h arrive after limsDelay */
      Object.keys(S.hours).forEach(function (k) {
        var h = +k, hr = S.hours[k];
        if (!hr.lims && t >= h * 3600 + 3600 + S.limsDelay) {
          hr.lims = true;
          if (hr.st === "provisional" && S.dimsOK) { hr.st = "complete"; hr.at = t; feed("Lab results for " + hourLabel(h) + " arrived; the hour was recomputed and is now complete."); }
        }
      });
      /* nightly batch 01:00 */
      var night = Math.floor((t - 3600) / 86400);
      if (night !== S.lastNight) {
        S.lastNight = night;
        if (!routeHas("nrt")) { /* lane off */ }
        else if (S.batchFail) {
          S.batchFail = false; S.dimsOK = false; S.daily.late = true;
          feed("The nightly batch failed. Dimensions stay as of yesterday, so gold shows new press P-1501 as an unknown member (-1) and hours stay provisional. The daily report is late.", "bad");
        } else {
          S.dimsOK = true; S.dimsAt = t + 3600; S.daily = { day: Math.floor(t / 86400) - 1, at: t + 5 * 3600, late: false };
          if (S.newPress) S.newPressSeen = true;
          Object.keys(S.hours).forEach(function (k) { var hr = S.hours[k]; if (hr.st === "provisional" && hr.lims) { hr.st = "restated"; hr.at = t + 3600; } });
          feed("Nightly batch ran at 01:00: SAP and MES masters into bronze and silver (SCD type 2), gold dimensions rebuilt at 02:00, hours that waited on them recomputed, the daily report ready at 06:00. Reference data copied to the fast lane.");
          if (state.visible) for (var i2 = 0; i2 < 8; i2++) (function (i) { setTimeout(function () { launch("cdc", [[160, 410], [370, 410], [490, 410], [505, 410], [615, 410], [630, 410], [740, 410], [755, 410], [985, 400], [1010, 400]], 300); }, i * 90); })(i2);
        }
      }
      var h0 = Math.floor(t / 3600);
      if (!S.hours[h0]) S.hours[h0] = { st: "running", lims: false };
      else if (S.hours[h0].st == null) S.hours[h0].st = "running";
    }
    function visuals(dtReal) {
      var offline = S.gwOffline && SIM.t >= S.gwOffline.from && SIM.t < S.gwOffline.to;
      every("iot", 240, dtReal, function () {
        if (offline) { launch("press", [[100, 142], [160, 142]], 200); return; }
        launch("press", [[100, 142], [160, 142], [190, 142], [340, 142]], 280, function () {
          if (routeHas("fast")) launch("press", [[340, 98], [370, 98], [630, 98], [660, 98], [800, 98], [1010, 85]], 360);
        });
      });
      if (routeHas("nrt")) every("lims", 2600, dtReal, function () { launch("lims", [[160, 380], [175, 380], [175, 300], [370, 300]], 220); });
    }
    function render() {
      var b = BINDINGS[state.binding], t = SIM.t;
      $("ssim-clock").textContent = "Day " + (Math.floor(t / 86400) + 1) + " · " + clock(t);
      var offline = S.gwOffline && t >= S.gwOffline.from && t < S.gwOffline.to;
      count("iot", offline ? "PLANT OFFLINE, buffering" : "300 readings/s", "P-1501 " + (S.newPress ? "running" : "not yet"));
      count("ent", "masters nightly", "lab delay " + dur(S.limsDelay));
      count("log", b.log === "No shared event log" ? "events go straight to bronze" : "both lanes read it", "");
      var unknownLive = S.newPress && !S.newPressSeen;
      count("fast", "limits, press list as of " + (S.refAt ? hm(S.refAt) : "-"), unknownLive ? "P-1501 shown as 'unknown press'" : "light work only");
      count("live", "last 48 h", "");
      count("ingest", "streams + files", "silver " + (S.silverAt ? hm(S.silverAt) : "-"));
      count("extract", "SAP, MES masters", S.dimsOK ? "dims " + hm(S.dimsAt || 0) : "FAILED");
      count("bronze", "same tables", "both write");
      count("silver", "SCD2 masters", "+ readings");
      count("gold", unknownLive ? "P-1501 as unknown (-1)" : "", unknownLive ? "fixed by tonight's batch" : "");
      var stale = t - S.liveAsOf;
      count("ui1", routeHas("fast") ? "Press 17: " + S.temp.toFixed(1) + " °C" : "lane off", routeHas("fast") ? (stale > 60 ? "STALE " + dur(stale) : "live, ~2 s behind") : "");
      var hrs = Object.keys(S.hours).map(Number).sort(function (a, c) { return a - c; });
      var lastC = null, lastP = null;
      hrs.forEach(function (h) { var s = S.hours[h].st; if (s === "complete" || s === "restated") lastC = h; else if (s === "provisional") lastP = h; });
      count("ui2", routeHas("nrt") && lastC != null ? "Final to " + hm(lastC * 3600 + 3600) : "-", routeHas("nrt") && lastP != null ? "Provisional " + hourLabel(lastP) : "");
      var d = S.daily;
      count("ui3", routeHas("nrt") ? (d.late ? "Yesterday: LATE" : (t >= d.at ? "Yesterday: ready " + hm(d.at) : "Yesterday: due 06:00")) : "-", routeHas("nrt") ? "OEE, scrap, output" : "");
      var show = hrs.filter(function (h) { return h <= Math.floor(t / 3600); }).slice(-6);
      chips.forEach(function (c, i) {
        var h = show[i];
        if (h == null) { c.g.setAttribute("class", "chip empty"); c.t1.textContent = ""; c.t2.textContent = ""; return; }
        var hr = S.hours[h];
        c.g.setAttribute("class", "chip " + hr.st);
        c.t1.textContent = hourLabel(h);
        var label = hr.st === "running" ? (h < Math.floor(t / 3600) ? "builds at :15" : "hour open") : hr.st;
        c.t2.textContent = hr.st === "provisional" && hr.short ? "wait: " + hr.short : label;
      });
      svg.classList.toggle("no-fast", !routeHas("fast"));
      svg.classList.toggle("no-nrt", !routeHas("nrt"));
    }
    var inc = {
      offline: function () { S.gwOffline = { from: SIM.t, to: SIM.t + 3600, done: false }; feed("A plant goes offline for an hour. The live screen goes stale; the gateway buffers; that gold hour will be restated when the buffer arrives.", "bad"); },
      batchfail: function () { S.batchFail = true; feed("Tonight's nightly batch will fail.", "bad"); },
      limslate: function () { S.limsDelay = 6 * 3600; feed("Lab results now arrive 6 hours late. Gold hours stay provisional until they land.", "bad"); },
      reset: function () { S.limsDelay = 2 * 3600; feed("Lab results back to 2 hours."); }
    };
    document.querySelectorAll("[data-inc]").forEach(function (bt) { bt.addEventListener("click", function () { inc[bt.getAttribute("data-inc")](); }); });
    feed("Day 1 starts at 05:40. Yesterday's nightly batch already ran; the daily report is due at 06:00.");
    return { tick: tick, visuals: visuals, render: render, maxStep: 30 };
  }

  /* ------------------------------------------------------------ controls + loop */
  var sim = MODE === "lanes" ? lanes() : flow();
  function applyBinding() {
    Object.keys(boxes).forEach(function (k) { setProduct(boxes[k]); });
    var b = BINDINGS[state.binding];
    $("ssim-note").textContent = b.note;
    svg.classList.toggle("nolog", b.log === "No shared event log");
  }
  document.querySelectorAll("[name=ssim-binding]").forEach(function (r) {
    if (r.checked) state.binding = r.value;
    r.addEventListener("change", function () { if (r.checked) { state.binding = r.value; applyBinding(); feed("Binding: " + BINDINGS[state.binding].name + "."); } });
  });
  document.querySelectorAll("[name=ssim-route]").forEach(function (r) {
    if (r.checked) state.route = r.value;
    r.addEventListener("change", function () {
      if (!r.checked) return; state.route = r.value;
      feed(state.route === "direct" ? "Route: direct to the screen only. Fast and cheap, but there is no number of record, no history and nowhere for database and file sources to go." :
           state.route === "medallion" ? "Route: through the medallion only. Every number is governed and complete, but screens are 15 to 75 minutes behind." :
           "Route: both. The live screen acts now; reports come from gold.");
    });
  });
  var spd = $("ssim-speed");
  if (spd) { state.speed = +spd.value; spd.addEventListener("change", function () { state.speed = +spd.value; }); }
  var pauseBtn = $("ssim-pause");
  if (pauseBtn) pauseBtn.addEventListener("click", function () { state.paused = !state.paused; pauseBtn.textContent = state.paused ? "Play" : "Pause"; });
  applyBinding();

  state.visible = true;
  document.addEventListener("visibilitychange", function () { state.visible = !document.hidden; });
  var last = performance.now(), acc = 0;
  function loop(now) {
    var dtReal = Math.min(0.1, (now - last) / 1000); last = now;
    if (!state.paused && state.visible) {
      var dtSim = dtReal * state.speed, step = sim.maxStep;
      while (dtSim > 0) { var s = Math.min(step, dtSim); sim.tick(s); dtSim -= s; }
      sim.visuals(dtReal);
      stepDots(dtReal);
      acc += dtReal;
      if (acc > 0.1) { acc = 0; sim.render(); }
    }
    requestAnimationFrame(loop);
  }
  var jump = +(new URLSearchParams(location.search).get("run") || 0);
  if (jump > 0) { state.visible = false; var left = Math.min(jump, 3 * 86400); while (left > 0) { var st = Math.min(sim.maxStep, left); sim.tick(st); left -= st; } state.visible = !document.hidden; }
  sim.render();
  requestAnimationFrame(loop);
})();
