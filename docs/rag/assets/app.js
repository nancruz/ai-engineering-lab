/* Course page behaviour: navigation, progress, copy buttons and the interactive widgets.
   Widgets compute with RagLab (raglab.js) on RAG_DATA (course-data.js). Nothing calls a model. */
(function () {
  "use strict";
  const L = window.RagLab, D = window.RAG_DATA;
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const f2 = (x) => (x === null || x === undefined ? "–" : x.toFixed(2));
  const COLORS = ["--t1", "--t2", "--t3", "--t4", "--t5", "--t6", "--t7", "--t8"].map((v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim() || "#6960d6");
  const PASTEL = ["#e4e0ff", "#d5f0ea", "#fbe7c8", "#f8d9df", "#d9e7fa", "#eadcf7"];
  const docById = Object.fromEntries((D ? D.docs : []).map((d) => [d.id, d]));
  const store = {
    get() { try { return JSON.parse(localStorage.getItem("rag-course-v2") || "{}"); } catch (e) { return {}; } },
    set(v) { try { localStorage.setItem("rag-course-v2", JSON.stringify(v)); } catch (e) { /* storage unavailable */ } },
  };

  // ---------------------------------------------------------------- shared caches
  const chunkCache = {}, indexCache = {};
  function chunks(strategy = "headings", size = 800, overlap = 0) {
    const key = `${strategy}/${size}/${overlap}`;
    return chunkCache[key] || (chunkCache[key] = L.chunkDocuments(D.docs, strategy, size, overlap));
  }
  function index(strategy = "headings", size = 800, overlap = 0, k1 = 1.5, b = 0.75) {
    const key = `${strategy}/${size}/${overlap}/${k1}/${b}`;
    return indexCache[key] || (indexCache[key] = new L.BM25Index(chunks(strategy, size, overlap), k1, b));
  }
  const badges = (meta) => (meta.status === "archived" ? '<span class="badge warn">archived</span>' : "") +
    (meta.access === "sre" ? '<span class="badge no">SRE only</span>' : "") + (meta.source === "imported" ? '<span class="badge warn">imported</span>' : "");
  const snippet = (text, n = 150) => { const t = text.replace(/\s+/g, " ").trim(); return t.length > n ? t.slice(0, n - 1) + "…" : t; };
  function presets(container, label, items, onPick) {
    const row = document.createElement("div"); row.className = "presets";
    row.innerHTML = `<span>${esc(label)}</span>` + items.map((it, i) => `<button type="button" data-i="${i}">${esc(it.label)}</button>`).join("");
    row.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) onPick(items[+b.dataset.i]); });
    container.appendChild(row);
  }

  // ---------------------------------------------------------------- page chrome
  function chrome() {
    const btn = $(".menu-btn"), side = $(".sidebar");
    if (btn && side) btn.addEventListener("click", () => side.classList.toggle("open"));
    $$("pre.cmd").forEach((pre) => {
      const b = document.createElement("button"); b.className = "copy"; b.type = "button"; b.textContent = "COPY";
      b.addEventListener("click", () => {
        const text = [...pre.querySelector("code").childNodes].filter((n) => !(n.classList && n.classList.contains("p"))).map((n) => n.textContent).join("").trim();
        (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(() => { b.textContent = "COPIED"; b.classList.add("done"); setTimeout(() => { b.textContent = "COPY"; b.classList.remove("done"); }, 1400); }).catch(() => { b.textContent = "SELECT + COPY"; });
      });
      pre.appendChild(b);
    });
    progress();
    $$(".mark-done").forEach((b) => b.addEventListener("click", () => {
      const s = store.get(); s.labs = s.labs || {}; const lab = b.dataset.lab;
      s.labs[lab] = !s.labs[lab]; store.set(s); progress();
    }));
  }
  function progress() {
    const labs = (store.get().labs) || {};
    const total = $$(".nav a[data-lab]").length || 8, done = Object.values(labs).filter(Boolean).length;
    $$("[data-lab]").forEach((n) => n.classList.toggle("done", !!labs[n.dataset.lab]));
    $$(".mark-done").forEach((b) => { const on = !!labs[b.dataset.lab]; b.setAttribute("aria-pressed", on); b.textContent = on ? "✓ Lab done (undo)" : "Mark this lab as done"; });
    const bar = $(".side-foot .bar span"), label = $(".side-foot [data-count]");
    if (bar) bar.style.width = `${(100 * done) / total}%`;
    if (label) label.textContent = `${done} / ${total} labs done`;
  }

  // ---------------------------------------------------------------- widgets
  const widgets = {};

  // Module 1: inverted index on three tiny documents
  widgets.invindex = (body) => {
    const docs = [{ id: "d1", text: "Roll back the playback release" }, { id: "d2", text: "Playback errors and error codes" }, { id: "d3", text: "Catalog request timeout" }];
    body.innerHTML = `<div class="controls"><label class="control grow">Query<input type="search" value="playback rollback"></label></div><div class="grid2"><div><p class="small muted">Documents</p><div data-docs></div></div><div><p class="small muted">Inverted index: term → documents</p><table data-ix></table></div></div><p class="small" data-out></p>`;
    const input = $("input", body);
    const postings = {};
    docs.forEach((d) => L.tokenize(d.text).forEach((t) => { postings[t] = postings[t] || new Set(); postings[t].add(d.id); }));
    const terms = Object.keys(postings).sort();
    function render() {
      const q = new Set(L.tokenize(input.value)), hit = new Set();
      terms.forEach((t) => { if (q.has(t)) postings[t].forEach((d) => hit.add(d)); });
      $("[data-docs]", body).innerHTML = docs.map((d) => `<div class="result" style="${hit.has(d.id) ? "border-color:#a7d8c8;background:#f3fbf7" : ""}"><span class="rid">${d.id}</span> <span class="small">${esc(d.text)}</span></div>`).join("");
      $("[data-ix]", body).innerHTML = "<tr><th>term</th><th>documents</th></tr>" + terms.map((t) => `<tr style="${q.has(t) ? "background:#eeecff" : ""}"><td class="mono">${t}</td><td class="mono">${[...postings[t]].join(", ")}</td></tr>`).join("");
      $("[data-out]", body).innerHTML = q.size ? `Query terms <b class="mono">${[...q].join(", ")}</b> → look up their rows → candidates <b class="mono">${[...hit].sort().join(", ") || "none"}</b>. Only these are scored; the rest are never touched.` : "Type a query.";
    }
    input.addEventListener("input", render); render();
  };

  // Module 1: BM25 explorer
  widgets.bm25 = (body) => {
    body.innerHTML = `<div class="controls">
      <label class="control grow">Query<input type="search" data-q value="PLAY-4012 device clock"></label>
      <label class="control"><span>k1 <output data-k1o>1.5</output></span><input type="range" data-k1 min="0" max="3" step="0.1" value="1.5"></label>
      <label class="control"><span>b <output data-bo>0.75</output></span><input type="range" data-b min="0" max="1" step="0.05" value="0.75"></label>
      <label class="control">Search over<select data-unit><option value="document">whole documents</option><option value="headings">sections (Module 3)</option></select></label></div>`;
    presets(body, "Try:", [{ label: "PLAY-4012 device clock" }, { label: "PLAY-4012" }, { label: "kill switch flag naming" }, { label: "catalog timeout retries" }, { label: "how do I undo a bad playback release" }, { label: "my TV refuses to play a film I paid for" }], (p) => { $("[data-q]", body).value = p.label; render(); });
    const out = document.createElement("div"); body.appendChild(out);
    const chart = document.createElement("div"); body.appendChild(chart);
    $$("input,select", body).forEach((n) => n.addEventListener("input", render));
    function render() {
      const k1 = +$("[data-k1]", body).value, b = +$("[data-b]", body).value, unit = $("[data-unit]", body).value, q = $("[data-q]", body).value;
      $("[data-k1o]", body).textContent = k1.toFixed(1); $("[data-bo]", body).textContent = b.toFixed(2);
      const ix = index(unit, 800, 0, k1, b), terms = [...new Set(L.tokenize(q))], color = Object.fromEntries(terms.map((t, i) => [t, COLORS[i % COLORS.length]]));
      const hits = ix.search(q, 6), max = hits.length ? hits[0].score : 1;
      const legend = terms.map((t) => `<span><i style="background:${color[t]}"></i><b class="mono">${esc(t)}</b> <span class="muted mono">idf ${ix.idf(t).toFixed(2)} · in ${ix.df.get(t) || 0}/${ix.items.length}</span></span>`).join("");
      out.innerHTML = `<div class="legend">${legend || '<span class="muted">No search terms (everything was a stopword?)</span>'}</div>` + (hits.length ? `<div class="results">${hits.map((h, i) => {
        const c = h.item, parts = Object.entries(h.parts);
        return `<div class="result"><div class="result-top"><span class="rank">${i + 1}</span><span class="rid">${esc(c.id)}</span>${badges(c.meta)}<span class="rscore">${h.score.toFixed(2)}</span></div>
          <div class="snippet">${esc(c.heading ? c.title + " › " + c.heading : c.title)}</div>
          <div class="stack" title="${parts.map(([t, v]) => `${t}: ${v.toFixed(2)}`).join("  ")}">${parts.map(([t, v]) => `<span style="width:${(100 * v) / max}%;background:${color[t]}"></span>`).join("")}</div></div>`;
      }).join("")}</div>` : '<p class="empty">No document contains any of these terms.</p>');
      // saturation chart: contribution of one term vs tf, document of average length
      const W = 520, H = 150, P = 30, maxTf = 20, sat = (f) => (f * (k1 + 1)) / (f + k1 || 1), ymax = Math.max(sat(maxTf), 3.2);
      const x = (f) => P + ((W - P - 10) * f) / maxTf, y = (v) => H - 22 - ((H - 40) * v) / ymax;
      const pts = Array.from({ length: maxTf }, (_, i) => `${x(i + 1)},${y(sat(i + 1))}`).join(" ");
      chart.innerHTML = `<p class="small muted" style="margin:16px 0 4px">Term-frequency saturation at k1 = ${k1.toFixed(1)}: how much the 1st, 2nd … 20th occurrence of a term adds (average-length document, idf = 1).</p>
        <svg class="svgbox" viewBox="0 0 ${W} ${H}" role="img" aria-label="Saturation curve"><line x1="${P}" y1="${H - 22}" x2="${W - 10}" y2="${H - 22}" stroke="#ccd"/><line x1="${P}" y1="10" x2="${P}" y2="${H - 22}" stroke="#ccd"/>
        <polyline points="${pts}" fill="none" stroke="#6960d6" stroke-width="2.5"/><line x1="${x(0)}" y1="${y(k1 + 1)}" x2="${W - 10}" y2="${y(k1 + 1)}" stroke="#6960d6" stroke-dasharray="4 4" opacity=".5"/>
        <text x="${W - 12}" y="${y(k1 + 1) - 5}" text-anchor="end" font-size="10" fill="#6960d6">ceiling k1 + 1 = ${(k1 + 1).toFixed(1)}</text>
        ${[1, 5, 10, 15, 20].map((f) => `<text x="${x(f)}" y="${H - 6}" font-size="10" text-anchor="middle" fill="#888">${f}</text>`).join("")}<text x="${P + 4}" y="20" font-size="10" fill="#888">score</text><text x="${W - 12}" y="${H - 26}" font-size="10" text-anchor="end" fill="#888">occurrences (tf)</text></svg>`;
    }
    render();
  };

  // Module 1: IDF — how rare a term is decides how much it is worth
  widgets.idf = (body) => {
    const ix = index("document"), N = ix.items.length;
    const idfOf = (df) => Math.log(1 + (N - df + 0.5) / (df + 0.5));
    const real = ["play-4012", "drm", "play", "rollback", "catalog", "release", "error", "playback"].map((t) => ({ t, df: ix.df.get(t) || 0 })).filter((r) => r.df);
    body.innerHTML = `<div class="controls"><label class="control"><span>The term appears in <output data-o>2</output> of ${N} documents (df)</span><input type="range" data-df min="1" max="${N}" value="2" style="width:260px"></label></div>
      <div data-docs style="display:flex;flex-wrap:wrap;gap:4px;margin:0 0 12px"></div><div data-calc class="formula" style="white-space:normal;margin-bottom:12px"></div><svg class="svgbox" data-svg viewBox="0 0 560 190" role="img" aria-label="IDF curve"></svg>
      <p class="small muted">Dots are real terms from the Lumen knowledge base. Click one to load it.</p>`;
    const slider = $("[data-df]", body);
    slider.addEventListener("input", render);
    body.addEventListener("click", (e) => { const g = e.target.closest("[data-term]"); if (g) { slider.value = g.dataset.df; render(); } });
    function render() {
      const df = +slider.value, idf = idfOf(df), names = real.filter((r) => r.df === df).map((r) => r.t);
      $("[data-o]", body).textContent = df;
      $("[data-docs]", body).innerHTML = Array.from({ length: N }, (_, i) => `<span title="document ${i + 1}" style="width:18px;height:22px;border-radius:3px;background:${i < df ? "#6960d6" : "#ecebf6"}"></span>`).join("");
      $("[data-calc]", body).innerHTML = `idf = ln( 1 + (N − df + 0.5) / (df + 0.5) ) = ln( 1 + (${N} − ${df} + 0.5) / (${df} + 0.5) ) = ln( ${(1 + (N - df + 0.5) / (df + 0.5)).toFixed(2)} ) = <b>${idf.toFixed(2)}</b>` +
        `<br><span class="small muted">${names.length ? `Lumen terms with df = ${df}: <b class="mono">${names.join(", ")}</b>. ` : ""}${df <= 2 ? "Very rare: finding this word in a document is strong evidence the document is the one you want." : df >= N - 2 ? "In almost every document: it can't tell documents apart, so it's worth almost nothing." : df > N / 3 ? "Common: it narrows things down only a little." : "Fairly rare: a useful clue."}</span>`;
      const W = 560, H = 190, P = 34, ymax = idfOf(1) * 1.08, x = (d) => P + ((W - P - 14) * (d - 1)) / (N - 1), y = (v) => H - 26 - ((H - 44) * v) / ymax;
      const pts = Array.from({ length: N }, (_, i) => `${x(i + 1)},${y(idfOf(i + 1))}`).join(" ");
      $("[data-svg]", body).innerHTML = `<line x1="${P}" y1="${H - 26}" x2="${W - 10}" y2="${H - 26}" stroke="#ccd"/><line x1="${P}" y1="12" x2="${P}" y2="${H - 26}" stroke="#ccd"/>
        <polyline points="${pts}" fill="none" stroke="#c9c4f3" stroke-width="2.5"/>
        ${real.map((r, i) => `<g data-term="${r.t}" data-df="${r.df}" style="cursor:pointer"><circle cx="${x(r.df)}" cy="${y(idfOf(r.df))}" r="5" fill="#2f8f83"/><text x="${x(r.df) + (i % 2 ? -7 : 6)}" y="${y(idfOf(r.df)) + (i % 2 ? 15 : -8)}" text-anchor="${i % 2 ? "end" : "start"}" font-size="10" fill="#2f786d">${r.t}</text></g>`).join("")}
        <circle cx="${x(df)}" cy="${y(idf)}" r="7" fill="none" stroke="#6960d6" stroke-width="2.5"/><line x1="${x(df)}" y1="${y(idf)}" x2="${x(df)}" y2="${H - 26}" stroke="#6960d6" stroke-dasharray="3 3"/>
        ${[1, 6, 12, 18, N].map((d) => `<text x="${x(d)}" y="${H - 10}" font-size="10" text-anchor="middle" fill="#888">${d}</text>`).join("")}
        <text x="${P + 4}" y="22" font-size="10" fill="#888">idf (weight of the term)</text><text x="${W - 12}" y="${H - 30}" font-size="10" text-anchor="end" fill="#888">documents containing the term (df)</text></svg>`;
    }
    render();
  };

  // Module 1: term-frequency saturation — what k1 does
  widgets.tfsat = (body) => {
    body.innerHTML = `<div class="controls"><label class="control"><span>k1 <output data-o>1.5</output></span><input type="range" data-k1 min="0" max="5" step="0.1" value="1.5"></label></div>`;
    presets(body, "Try:", [{ label: "k1 = 0", k1: 0 }, { label: "k1 = 0.5", k1: 0.5 }, { label: "k1 = 1.5 (our default)", k1: 1.5 }, { label: "k1 = 5", k1: 5 }], (p) => { $("[data-k1]", body).value = p.k1; render(); });
    const grid = document.createElement("div"); grid.className = "grid2"; grid.style.alignItems = "start"; grid.innerHTML = `<svg class="svgbox" data-svg viewBox="0 0 380 220" role="img" aria-label="Saturation curves"></svg><div data-tab></div>`; body.appendChild(grid);
    const note = document.createElement("p"); note.className = "small muted"; body.appendChild(note);
    $("[data-k1]", body).addEventListener("input", render);
    const sat = (f, k1) => (k1 === 0 ? (f > 0 ? 1 : 0) : (f * (k1 + 1)) / (f + k1));
    function render() {
      const k1 = +$("[data-k1]", body).value, maxTf = 12, W = 380, H = 220, P = 30, ymax = 6.2;
      $("[data-o]", body).textContent = k1.toFixed(1);
      const x = (f) => P + ((W - P - 10) * f) / maxTf, y = (v) => H - 24 - ((H - 40) * Math.min(v, ymax)) / ymax;
      const curve = (k, color, w, dash = "") => `<polyline points="${Array.from({ length: maxTf + 1 }, (_, f) => `${x(f)},${y(sat(f, k))}`).join(" ")}" fill="none" stroke="${color}" stroke-width="${w}" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
      $("[data-svg]", body).innerHTML = `<line x1="${P}" y1="${H - 24}" x2="${W - 10}" y2="${H - 24}" stroke="#ccd"/><line x1="${P}" y1="10" x2="${P}" y2="${H - 24}" stroke="#ccd"/>
        <polyline points="${x(0)},${y(0)} ${x(ymax)},${y(ymax)}" stroke="#d08a1f" stroke-width="1.5" stroke-dasharray="5 4" fill="none"/><text x="${x(3.6) - 6}" y="${y(4.4)}" font-size="10" fill="#a86b12" text-anchor="end">raw count →</text>
        ${curve(k1, "#6960d6", 3)}<line x1="${P}" y1="${y(k1 + 1)}" x2="${W - 10}" y2="${y(k1 + 1)}" stroke="#6960d6" stroke-dasharray="3 4" opacity=".55"/>
        <text x="${W - 12}" y="${y(k1 + 1) - 5}" text-anchor="end" font-size="10" fill="#6960d6">${k1 === 0 ? "k1 = 0: present or not, that's all" : `ceiling = k1 + 1 = ${(k1 + 1).toFixed(1)}`}</text>
        ${Array.from({ length: maxTf }, (_, i) => i + 1).map((f) => `<circle cx="${x(f)}" cy="${y(sat(f, k1))}" r="3" fill="#6960d6"/>`).join("")}
        ${[0, 3, 6, 9, 12].map((f) => `<text x="${x(f)}" y="${H - 8}" font-size="10" text-anchor="middle" fill="#888">${f}</text>`).join("")}<text x="${P + 4}" y="20" font-size="10" fill="#888">tf part of the score</text><text x="${W - 12}" y="${H - 28}" font-size="10" text-anchor="end" fill="#888">times the term appears (tf)</text></svg>`;
      const rows = [1, 2, 3, 4, 5, 10, 20].map((f, i, a) => { const v = sat(f, k1), prev = i ? sat(a[i - 1], k1) : 0; return `<tr><td class="mono">${f}</td><td class="mono">${v.toFixed(2)}</td><td class="mono muted">${i ? "+" + (v - prev).toFixed(2) + (a[i] - a[i - 1] > 1 ? ` <span class="small">(${a[i] - a[i - 1]} more)</span>` : "") : "–"}</td></tr>`; }).join("");
      $("[data-tab]", body).innerHTML = `<table><tr><th>tf</th><th>tf part</th><th>added by the extra occurrences</th></tr>${rows}</table>`;
      note.innerHTML = k1 === 0 ? "With k1 = 0 the first occurrence is all that counts. Mentioning a word ten times is no better than once." :
        k1 >= 4 ? `With a large k1 the curve stays close to the raw count for a long time: repetition keeps paying off, so a document can win just by repeating a word.` :
        `The first occurrence gives 1.00. The second adds ${(sat(2, k1) - 1).toFixed(2)}, the third ${(sat(3, k1) - sat(2, k1)).toFixed(2)}… and no amount of repetition gets past ${(k1 + 1).toFixed(1)}. That's “diminishing returns”.`;
    }
    render();
  };

  // Module 1: one BM25 term, computed step by step
  widgets.termcalc = (body) => {
    const ix = index("document"), N = ix.items.length, avgdl = ix.avgdl;
    body.innerHTML = `<div class="controls">
      <label class="control"><span>df (docs with the term) <output data-o="df"></output></span><input type="range" data-v="df" min="1" max="${N}" value="4"></label>
      <label class="control"><span>tf (times in this doc) <output data-o="tf"></output></span><input type="range" data-v="tf" min="1" max="20" value="4"></label>
      <label class="control"><span>doc length |d| <output data-o="len"></output> terms</span><input type="range" data-v="len" min="20" max="400" step="1" value="140"></label>
      <label class="control"><span>k1 <output data-o="k1"></output></span><input type="range" data-v="k1" min="0" max="3" step="0.1" value="1.5"></label>
      <label class="control"><span>b <output data-o="b"></output></span><input type="range" data-v="b" min="0" max="1" step="0.05" value="0.75"></label></div>`;
    const set = (v) => { Object.entries(v).forEach(([k, val]) => { $(`[data-v="${k}"]`, body).value = val; }); render(); };
    const p = (id, t) => { const pos = ix.items.findIndex((i) => i.id === id); return { df: ix.df.get(t), tf: ix.tf[pos].get(t), len: ix.lengths[pos], k1: 1.5, b: 0.75 }; };
    presets(body, "Real cases:", [{ label: "“play” in drm-license-service", v: p("drm-license-service", "play") }, { label: "“play” in playback-error-codes", v: p("playback-error-codes", "play") }, { label: "“play-4012” in playback-error-codes", v: p("playback-error-codes", "play-4012") }], (x) => set(x.v));
    const out = document.createElement("div"); body.appendChild(out);
    $$("input", body).forEach((n) => n.addEventListener("input", render));
    function calc(df, tf, len, k1, b) {
      const idf = Math.log(1 + (N - df + 0.5) / (df + 0.5)), ratio = len / avgdl, factor = 1 - b + b * ratio, part = (tf * (k1 + 1)) / (tf + k1 * factor);
      return { idf, ratio, factor, part, score: idf * part };
    }
    function render() {
      const v = Object.fromEntries($$("[data-v]", body).map((n) => [n.dataset.v, +n.value]));
      Object.entries(v).forEach(([k, val]) => { $(`[data-o="${k}"]`, body).textContent = k === "k1" ? val.toFixed(1) : k === "b" ? val.toFixed(2) : val; });
      const c = calc(v.df, v.tf, v.len, v.k1, v.b);
      const lenWord = c.factor > 1.02 ? "longer than average, so each occurrence counts a bit <b>less</b>" : c.factor < 0.98 ? "shorter than average, so each occurrence counts a bit <b>more</b>" : "about average: no adjustment";
      const step = (n, label, math, why) => `<div class="result" style="padding:8px 12px"><div class="result-top"><span class="rank">${n}</span><b style="font-size:13.5px">${label}</b></div><div class="mono small" style="margin:4px 0 2px 30px">${math}</div><div class="snippet" style="margin-bottom:0">${why}</div></div>`;
      const sizes = [["short (½ avg)", avgdl / 2], ["average", avgdl], ["long (2× avg)", avgdl * 2]].map(([n, l]) => [n, calc(v.df, v.tf, l, v.k1, v.b).score]), smax = Math.max(...sizes.map((s) => s[1]), 0.01);
      out.innerHTML = `<div class="results">
        ${step(1, "How rare is the term?", `idf = ln(1 + (${N} − ${v.df} + 0.5) / (${v.df} + 0.5)) = <b>${c.idf.toFixed(2)}</b>`, `It's in ${v.df} of ${N} documents.`)}
        ${step(2, "How long is this document, compared with the average?", `|d| / avgdl = ${v.len} / ${avgdl.toFixed(0)} = <b>${c.ratio.toFixed(2)}</b>`, "avgdl is the average length of the Lumen documents, in terms.")}
        ${step(3, "Turn that into a length factor (this is where b acts)", `1 − b + b × ${c.ratio.toFixed(2)} = 1 − ${v.b.toFixed(2)} + ${v.b.toFixed(2)} × ${c.ratio.toFixed(2)} = <b>${c.factor.toFixed(2)}</b>`, `b = 0 would make this always 1 (length ignored); b = 1 uses the full ratio. Here: ${lenWord}.`)}
        ${step(4, "Saturate the count (this is where k1 acts)", `tf × (k1 + 1) / (tf + k1 × factor) = ${v.tf} × ${(v.k1 + 1).toFixed(1)} / (${v.tf} + ${v.k1.toFixed(1)} × ${c.factor.toFixed(2)}) = <b>${c.part.toFixed(2)}</b>`, `The length factor multiplies k1: a long document behaves as if k1 were bigger, so its occurrences fill up more slowly.`)}
        ${step(5, "Multiply", `score = idf × tf part = ${c.idf.toFixed(2)} × ${c.part.toFixed(2)} = <b>${c.score.toFixed(2)}</b>`, "Do this for every query term the document contains, then add the results up. That sum is the document's BM25 score.")}</div>
        <p class="small muted" style="margin:14px 0 6px">The same term, appearing ${v.tf}×, in three documents of different lengths (b = ${v.b.toFixed(2)}):</p>
        ${sizes.map(([n, s]) => `<div style="display:flex;align-items:center;gap:10px;margin:4px 0"><span class="small" style="width:110px">${n}</span><span style="height:14px;border-radius:4px;background:#6960d6;width:${(70 * s) / smax}%"></span><span class="mono small">${s.toFixed(2)}</span></div>`).join("")}`;
    }
    render();
  };

  // Module 2: vector angle playground
  widgets.vectors = (body) => {
    body.innerHTML = `<div class="grid2" style="align-items:center"><svg class="svgbox" viewBox="-1.6 -1.6 3.2 3.2" style="max-width:360px;touch-action:none;background:#fbfbfe;border:1px solid var(--line);border-radius:12px" data-svg></svg><div><div class="metric-grid" data-m style="grid-template-columns:1fr 1fr"></div><div class="presets" data-p></div><p class="small muted">Drag the two arrow heads. Cosine only cares about the angle between them; the dot product also grows with their lengths. Embedding models are trained so that texts with similar meaning point in similar directions.</p></div></div>`;
    const svg = $("[data-svg]", body); const v = { A: [1.1, 0.35], B: [0.55, 0.95] }; let drag = null;
    presets($("[data-p]", body).parentNode, "Try:", [
      { label: "same direction, longer", A: [0.6, 0.3], B: [1.3, 0.65] }, { label: "unrelated (90°)", A: [1, 0], B: [0, 1] },
      { label: "opposite", A: [0.9, 0.5], B: [-0.9, -0.5] }, { label: "normalize both", norm: true }], (p) => {
      if (p.norm) ["A", "B"].forEach((k) => { const n = Math.hypot(...v[k]) || 1; v[k] = [v[k][0] / n, v[k][1] / n]; });
      else { v.A = p.A.slice(); v.B = p.B.slice(); }
      render();
    });
    $("[data-p]", body).remove();
    const toLocal = (e) => { const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; const p = pt.matrixTransform(svg.getScreenCTM().inverse()); return [Math.max(-1.5, Math.min(1.5, p.x)), Math.max(-1.5, Math.min(1.5, -p.y))]; };
    svg.addEventListener("pointerdown", (e) => { const t = e.target.closest("[data-h]"); if (t) { drag = t.dataset.h; svg.setPointerCapture(e.pointerId); } });
    svg.addEventListener("pointermove", (e) => { if (drag) { v[drag] = toLocal(e); render(); } });
    svg.addEventListener("pointerup", () => { drag = null; });
    function render() {
      const [a, b] = [v.A, v.B], dot = a[0] * b[0] + a[1] * b[1], na = Math.hypot(...a), nb = Math.hypot(...b), cos = L.cosine(a, b), ang = (Math.acos(Math.max(-1, Math.min(1, cos))) * 180) / Math.PI;
      const arrow = (p, c, k) => `<line x1="0" y1="0" x2="${p[0]}" y2="${-p[1]}" stroke="${c}" stroke-width="0.035"/><circle data-h="${k}" cx="${p[0]}" cy="${-p[1]}" r="0.09" fill="${c}" style="cursor:grab"/><text x="${p[0] + 0.1}" y="${-p[1] - 0.1}" font-size="0.16" font-weight="700" fill="${c}">${k}</text>`;
      svg.innerHTML = `<circle cx="0" cy="0" r="1" fill="none" stroke="#dcdaf0" stroke-width="0.012" stroke-dasharray="0.04 0.04"/><line x1="-1.5" y1="0" x2="1.5" y2="0" stroke="#e6e6ef" stroke-width="0.01"/><line x1="0" y1="-1.5" x2="0" y2="1.5" stroke="#e6e6ef" stroke-width="0.01"/>${arrow(a, "#6960d6", "A")}${arrow(b, "#2f8f83", "B")}`;
      $("[data-m]", body).innerHTML = `<div class="metric"><b>${cos.toFixed(3)}</b><div>cosine similarity</div></div><div class="metric"><b>${ang.toFixed(0)}°</b><div>angle</div></div><div class="metric"><b>${dot.toFixed(3)}</b><div>dot product</div></div><div class="metric"><b class="small">${na.toFixed(2)} · ${nb.toFixed(2)}</b><div>lengths |A| · |B|</div></div>`;
    }
    render();
  };

  // Module 2: toy meaning map (illustrative 2-D positions)
  widgets.meaningmap = (body) => {
    const S = [
      ["Roll back production when the canary error ratio stays above 2%.", 20], ["In staging, any engineer may restore the previous release.", 32], ["`lumenctl release rollback playback --to previous`", 10],
      ["Catalog requests use an 800 ms total deadline.", 100], ["Writes are never retried automatically.", 115], ["The client opens its circuit breaker when 50% of requests fail.", 88],
      ["The account has no entitlement for this title or region.", 190], ["Streaming licenses last 2 hours.", 205], ["If a device clock is more than 5 minutes wrong, validation fails.", 220],
      ["Acknowledge SEV1 and SEV2 pages within 5 minutes.", 280], ["The page escalates to the secondary automatically.", 295], ["Handover happens every Monday at 10:00 UTC.", 268],
      ["Production diagnostic traces are kept for 7 days.", 345], ["Remove credentials and customer identifiers before indexing.", 330]];
    const Q = [["How do I undo a bad playback release?", 24], ["How long should a catalog call wait before giving up?", 104], ["A customer's TV refuses to play a film they paid for", 205], ["How quickly must I respond when I'm paged?", 286], ["How long do we keep debugging data?", 340]];
    const pt = (deg, r = 1) => [r * Math.cos((deg * Math.PI) / 180), r * Math.sin((deg * Math.PI) / 180)];
    const sents = S.map(([text, deg], i) => ({ text, v: pt(deg, 0.86 + ((i * 37) % 10) / 70) }));
    body.innerHTML = `<div class="grid2" style="align-items:start"><svg class="svgbox" viewBox="-1.25 -1.25 2.5 2.5" style="max-width:380px" data-svg></svg><div data-side></div></div>`;
    const side = $("[data-side]", body); let current = 0;
    presets(side, "Query:", Q.map(([label]) => ({ label })), (p) => { current = Q.findIndex((q) => q[0] === p.label); render(); });
    const list = document.createElement("div"); side.appendChild(list);
    function render() {
      const [qtext, qdeg] = Q[current], q = pt(qdeg, 0.6), qterms = new Set(L.tokenize(qtext));
      const ranked = sents.map((s, i) => ({ ...s, i, cos: L.cosine(q, s.v), shared: L.tokenize(s.text).filter((t) => qterms.has(t)).length })).sort((a, b) => b.cos - a.cos);
      const near = new Set(ranked.slice(0, 3).map((r) => r.i));
      $("[data-svg]", body).innerHTML = `<circle r="1.12" fill="#fbfbfe" stroke="#ecebf6" stroke-width="0.01"/>` + sents.map((s, i) => `${near.has(i) ? `<line x1="${q[0]}" y1="${-q[1]}" x2="${s.v[0]}" y2="${-s.v[1]}" stroke="#6960d6" stroke-width="0.012" stroke-dasharray="0.03 0.02"/>` : ""}<circle cx="${s.v[0]}" cy="${-s.v[1]}" r="${near.has(i) ? 0.055 : 0.04}" fill="${near.has(i) ? "#6960d6" : "#c5c2df"}"><title>${esc(s.text)}</title></circle>`).join("") +
        `<rect x="${q[0] - 0.06}" y="${-q[1] - 0.06}" width="0.12" height="0.12" fill="#2f8f83" transform="rotate(45 ${q[0]} ${-q[1]})"/><text x="0" y="1.22" font-size="0.075" text-anchor="middle" fill="#999">toy 2-D picture · hover the dots</text>`;
      list.innerHTML = `<p class="small" style="margin:6px 0 8px"><b>Nearest by cosine</b> to <span class="mono">"${esc(qtext)}"</span></p><div class="results">${ranked.slice(0, 3).map((r, i) => `<div class="result"><div class="result-top"><span class="rank">${i + 1}</span><span class="small">${esc(r.text)}</span></div><div class="snippet" style="margin-bottom:0">cosine ${r.cos.toFixed(2)} · shared words with the query: <b>${r.shared}</b></div></div>`).join("")}</div>`;
    }
    render();
  };

  // Module 2: a hand-made 4-number "embedding" to show how vectors are compared
  widgets.handembed = (body) => {
    const DIMS = ["releases & rollback", "video playback", "billing & rights", "time & speed"];
    const S = [
      ["Roll back production when the canary error ratio stays above 2%.", [0.9, 0.2, 0, 0.1]],
      ["`lumenctl release rollback playback --to previous`", [0.8, 0.5, 0, 0]],
      ["The account has no entitlement for this title or region.", [0, 0.3, 0.9, 0]],
      ["Streaming licenses last 2 hours.", [0, 0.5, 0.6, 0.4]],
      ["Catalog requests use an 800 ms total deadline.", [0.1, 0.1, 0, 0.9]],
      ["Acknowledge SEV1 pages within 5 minutes.", [0.2, 0, 0, 0.8]]];
    const Q = [{ label: "How do I undo a bad release?", v: [0.9, 0.3, 0, 0] }, { label: "Why can't this customer watch a film they paid for?", v: [0, 0.6, 0.8, 0] }, { label: "How long should a catalog call wait?", v: [0, 0.1, 0, 1] }];
    let qtext = Q[0].label;
    body.innerHTML = `<p class="small muted" style="margin-top:0">Pretend an embedding model gave every sentence just 4 numbers, one per topic, each between 0 and 1. (Real models use hundreds, and nobody labels them. This is to see the arithmetic.)</p>`;
    presets(body, "Query:", Q, (p) => { qtext = p.label; p.v.forEach((x, i) => { $(`[data-d="${i}"]`, body).value = x; }); render(); });
    const ctl = document.createElement("div"); ctl.className = "controls";
    ctl.innerHTML = DIMS.map((d, i) => `<label class="control"><span>${d} <output data-o="${i}"></output></span><input type="range" data-d="${i}" min="0" max="1" step="0.1" value="${Q[0].v[i]}"></label>`).join("");
    body.appendChild(ctl);
    const out = document.createElement("div"); body.appendChild(out);
    $$("[data-d]", body).forEach((n) => n.addEventListener("input", () => { qtext = "(your own query vector)"; render(); }));
    const f1 = (x) => x.toFixed(1), vec = (v) => `[${v.map(f1).join(", ")}]`;
    function render() {
      const q = $$("[data-d]", body).map((n) => +n.value);
      q.forEach((x, i) => { $(`[data-o="${i}"]`, body).textContent = f1(x); });
      const qterms = new Set(L.tokenize(qtext)), nq = Math.hypot(...q);
      const rows = S.map(([text, v]) => { const d = v.reduce((s, x, i) => s + x * q[i], 0), n = Math.hypot(...v); return { text, v, d, n, cos: L.cosine(q, v), shared: L.tokenize(text).filter((t) => qterms.has(t)).length }; }).sort((a, b) => b.cos - a.cos);
      const top = rows[0];
      out.innerHTML = `<p class="small" style="margin:0 0 6px">Query <span class="mono">"${esc(qtext)}"</span> → vector <b class="mono">${vec(q)}</b> · length ${nq.toFixed(2)}</p>
        <table><tr><th>#</th><th>Sentence</th><th>its vector</th><th>dot</th><th>length</th><th>cosine</th><th>shared words</th></tr>
        ${rows.map((r, i) => `<tr style="${i === 0 ? "background:#f3fbf7" : ""}"><td class="mono">${i + 1}</td><td class="small">${esc(r.text)}</td><td class="mono small">${vec(r.v)}</td><td class="mono small">${r.d.toFixed(2)}</td><td class="mono small">${r.n.toFixed(2)}</td><td class="mono"><b>${r.cos.toFixed(2)}</b></td><td class="mono small">${r.shared}</td></tr>`).join("")}</table>
        <div class="formula" style="white-space:normal;font-size:12.5px">
        <b>How #1 got its score</b><br>
        dot = ${q.map((x, i) => `${f1(x)}×${f1(top.v[i])}`).join(" + ")} = <b>${top.d.toFixed(2)}</b> <span class="muted">(multiply topic by topic, add up)</span><br>
        |query| = √(${q.map((x) => `${f1(x)}²`).join(" + ")}) = ${nq.toFixed(2)} · |sentence| = √(${top.v.map((x) => `${f1(x)}²`).join(" + ")}) = ${top.n.toFixed(2)}<br>
        cosine = dot / (|query| × |sentence|) = ${top.d.toFixed(2)} / (${nq.toFixed(2)} × ${top.n.toFixed(2)}) = <b>${top.cos.toFixed(2)}</b></div>
        <p class="small muted">${nq === 0 ? "An all-zero query has no direction, so every cosine is 0." : top.shared === 0 ? "The best match shares <b>no words</b> with the query. It wins because its numbers are high on the same topics: that's what “similar meaning” means to a vector search." : "Move the sliders: a sentence ranks high when it's strong on the same topics the query is strong on."}</p>`;
    }
    render();
  };

  // Module 2: the two phases of vector search, one stage at a time
  widgets.lifecycle = (body) => {
    const ex = "Roll back production when the canary error ratio stays above 2%.", hv = [0.031, -0.112, 0.087, 0.004, -0.056];
    const stages = [
      { lane: "INDEXING · once, ahead of time", id: "chunk", name: "Split", sub: "documents → chunks", text: `Each document is cut into passages small enough to be about one thing (Module 3). For now, think of one chunk per document section, e.g. <span class="mono">playback-rollback-runbook#when-to-roll-back</span>: <q>${ex}</q>` },
      { lane: "INDEXING · once, ahead of time", id: "embed", name: "Embed", sub: "text → 768 numbers", text: `Every chunk is sent to the embedding model, which returns one vector. For <code>nomic-embed-text</code> that's 768 numbers, e.g. <span class="mono">[${hv.join(", ")}, … 763 more]</span>. This is the slow, sometimes paid, step: 10,000 chunks means 10,000 embeddings (batched).` },
      { lane: "INDEXING · once, ahead of time", id: "norm", name: "Normalize", sub: "scale to length 1", text: `Each vector is divided by its own length so it has length 1. Afterwards, the dot product of two vectors <em>is</em> their cosine, which saves a square root and two divisions on every comparison at query time.` },
      { lane: "INDEXING · once, ahead of time", id: "store", name: "Store", sub: "vector + text + metadata", text: `Each record keeps the vector next to everything needed later: <span class="mono">{ id, vector, text, doc_id, heading, access: "all", status: "current" }</span>. The vector is only used to <em>find</em> the record; the text is what goes to the language model; the metadata is for filtering. This table of records, plus an index to search it fast, is what a vector database is.` },
      { lane: "QUERY · every question", id: "qembed", name: "Embed the question", sub: "same model!", text: `The question goes through the <em>same</em> model and is normalized the same way. A vector from a different model lives in a different space: comparing them is meaningless even if both have 768 numbers.` },
      { lane: "QUERY · every question", id: "compare", name: "Compare", sub: "dot with every record", text: `Exact search: compute the dot product of the question vector with every stored vector (skipping records the user may not see). 112 chunks × 768 numbers ≈ 86,000 multiply-adds: instant. 10 million chunks ≈ 7.7 billion per question: too slow, which is why vector databases build an approximate index (below).` },
      { lane: "QUERY · every question", id: "topk", name: "Top k", sub: "highest scores", text: `Sort by score and keep the k best (typically 3–10). The scores themselves have no absolute meaning (0.62 isn't “62% relevant”), only their order matters, and they aren't comparable across models.` },
      { lane: "QUERY · every question", id: "return", name: "Return text", sub: "→ the prompt", text: `Return the <em>text</em> and metadata of those k records, not the vectors. In Module 4 they become the sources in the prompt.` }];
    let cur = 0;
    body.innerHTML = `<div class="pipe" data-pipe></div><div class="stage-panel" data-panel></div>`;
    const lanes = [...new Set(stages.map((s) => s.lane))];
    $("[data-pipe]", body).innerHTML = lanes.map((ln) => `<div><p class="lane-label">${ln}</p><div class="lane">${stages.map((s, i) => s.lane === ln ? `<button type="button" class="stage" data-i="${i}"><span class="m">${i + 1}</span><b>${s.name}</b><small>${s.sub}</small></button>` : "").join("")}</div></div>`).join("");
    $("[data-pipe]", body).addEventListener("click", (e) => { const b = e.target.closest("[data-i]"); if (b) { cur = +b.dataset.i; render(); } });
    function render() {
      $$("[data-i]", body).forEach((b) => b.setAttribute("aria-pressed", +b.dataset.i === cur));
      const s = stages[cur];
      $("[data-panel]", body).innerHTML = `<h4>${cur + 1}. ${s.name}</h4><p class="small" style="margin:0">${s.text}</p>`;
    }
    render();
  };

  // Module 2: approximate nearest-neighbour search as a greedy walk on a neighbour graph (the idea behind HNSW)
  widgets.ann = (body) => {
    let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    const P = Array.from({ length: 90 }, () => [0.04 + 0.92 * rnd(), 0.04 + 0.92 * rnd()]);
    const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
    let q = [0.82, 0.22];
    body.innerHTML = `<div class="controls"><label class="control"><span>links per point (M) <output data-mo>3</output></span><input type="range" data-m min="1" max="10" value="3"></label><label class="control"><span>starting points <output data-eo>1</output></span><input type="range" data-e min="1" max="5" value="1"></label></div>
      <div class="grid2" style="align-items:start"><svg class="svgbox" data-svg viewBox="0 0 1 1" style="max-width:400px;background:#fbfbfe;border:1px solid var(--line);border-radius:12px;cursor:crosshair"></svg><div><div class="metric-grid" data-met style="grid-template-columns:1fr 1fr"></div><div data-verdict></div><p class="small muted">Click anywhere to move the query (◆). Each dot is a stored vector; lines link each one to its nearest neighbours. The search starts at a fixed entry point and keeps hopping to whichever neighbour is closer to the query, stopping when no neighbour is closer.</p></div></div>`;
    const svg = $("[data-svg]", body);
    svg.addEventListener("click", (e) => { const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; const p = pt.matrixTransform(svg.getScreenCTM().inverse()); q = [p.x, p.y]; render(); });
    $$("input", body).forEach((n) => n.addEventListener("input", render));
    function render() {
      const M = +$("[data-m]", body).value, E = +$("[data-e]", body).value;
      $("[data-mo]", body).textContent = M; $("[data-eo]", body).textContent = E;
      const nbr = P.map(() => new Set());
      P.forEach((p, i) => P.map((o, j) => [j, dist(p, o)]).filter(([j]) => j !== i).sort((a, b) => a[1] - b[1]).slice(0, M).forEach(([j]) => { nbr[i].add(j); nbr[j].add(i); }));
      const seen = new Set(), paths = [];
      let best = -1, bestD = Infinity;
      const entries = [0, 45, 17, 68, 30].slice(0, E);
      for (const start of entries) {
        let cur = start; seen.add(cur); const path = [cur];
        for (;;) {
          let next = cur, nd = dist(P[cur], q);
          for (const j of nbr[cur]) { seen.add(j); const d = dist(P[j], q); if (d < nd) { nd = d; next = j; } }
          if (next === cur) break;
          cur = next; path.push(cur);
        }
        paths.push(path);
        if (dist(P[cur], q) < bestD) { bestD = dist(P[cur], q); best = cur; }
      }
      const truth = P.map((p, i) => [i, dist(p, q)]).sort((a, b) => a[1] - b[1])[0][0];
      const edges = []; nbr.forEach((s, i) => s.forEach((j) => { if (i < j) edges.push(`<line x1="${P[i][0]}" y1="${P[i][1]}" x2="${P[j][0]}" y2="${P[j][1]}" stroke="#e1dff0" stroke-width="0.003"/>`); }));
      svg.innerHTML = edges.join("") +
        paths.map((path) => `<polyline points="${path.map((i) => P[i].join(",")).join(" ")}" fill="none" stroke="#6960d6" stroke-width="0.008" stroke-linejoin="round"/>`).join("") +
        P.map((p, i) => `<circle cx="${p[0]}" cy="${p[1]}" r="${i === truth || i === best ? 0.016 : 0.009}" fill="${i === truth ? "#2f8f83" : i === best ? "#b23b46" : seen.has(i) ? "#9e97e6" : "#c9c8d6"}"/>`).join("") +
        entries.map((i) => `<circle cx="${P[i][0]}" cy="${P[i][1]}" r="0.022" fill="none" stroke="#6960d6" stroke-width="0.005"/>`).join("") +
        `<rect x="${q[0] - 0.017}" y="${q[1] - 0.017}" width="0.034" height="0.034" fill="#d08a1f" transform="rotate(45 ${q[0]} ${q[1]})"/>`;
      $("[data-met]", body).innerHTML = `<div class="metric"><b>${seen.size}</b><div>distances computed (graph walk)</div></div><div class="metric"><b>${P.length}</b><div>distances computed (exact search)</div></div>`;
      $("[data-verdict]", body).innerHTML = best === truth ? `<div class="verdict ok">✓ <span>The walk found the true nearest point (green) after looking at ${Math.round((100 * seen.size) / P.length)}% of the points.</span></div>` :
        `<div class="verdict no">✗ <span>The walk stopped at a point (red) where no neighbour was closer, but it isn't the true nearest (green). That's the “approximate” in ANN. More links or more starting points make this rarer, at the cost of more distance computations.</span></div>`;
    }
    render();
  };

  // Module 3: chunking playground
  widgets.chunker = (body) => {
    body.innerHTML = `<div class="controls"><label class="control">Document<select data-doc>${D.docs.map((d) => `<option value="${d.id}"${d.id === "playback-rollback-runbook" ? " selected" : ""}>${esc(d.id)}</option>`).join("")}</select></label>
      <div class="control">Strategy<div class="seg" data-strat>${["fixed", "paragraph", "headings", "document"].map((s) => `<button type="button" data-s="${s}" aria-pressed="${s === "fixed"}">${s}</button>`).join("")}</div></div>
      <label class="control"><span>size <output data-so>300</output> chars</span><input type="range" data-size min="100" max="1500" step="50" value="300"></label>
      <label class="control"><span>overlap <output data-oo>0</output></span><input type="range" data-ov min="0" max="300" step="10" value="0"></label></div><div class="stat-row" data-stats></div><div data-verdict></div><div class="doc-view" data-view></div><p class="small muted" style="margin-top:8px">Coloured runs are chunks; dark markers show where each chunk starts. Darker runs are covered by two chunks (overlap). Faded text belongs to no chunk (blank space between paragraphs).</p>`;
    let strategy = "fixed";
    $("[data-strat]", body).addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; strategy = b.dataset.s; $$("[data-strat] button", body).forEach((x) => x.setAttribute("aria-pressed", x === b)); render(); });
    $$("select,input", body).forEach((n) => n.addEventListener("input", render));
    function render() {
      const doc = docById[$("[data-doc]", body).value], size = +$("[data-size]", body).value, ov = Math.min(+$("[data-ov]", body).value, size - 50);
      $("[data-so]", body).textContent = size; $("[data-oo]", body).textContent = strategy === "fixed" || strategy === "paragraph" ? ov : "–";
      $("[data-ov]", body).disabled = !(strategy === "fixed" || strategy === "paragraph");
      const cs = L.chunkDocument(doc, strategy, size, strategy === "fixed" || strategy === "paragraph" ? ov : 0), text = doc.body;
      const covered = cs.reduce((s, c) => s + c.end - c.start, 0), lens = cs.map((c) => c.end - c.start);
      $("[data-stats]", body).innerHTML = `<div class="stat"><b>${cs.length}</b><span>chunks</span></div><div class="stat"><b>${Math.round(covered / cs.length)}</b><span>avg chars</span></div><div class="stat"><b>${Math.max(...lens)}</b><span>largest</span></div><div class="stat"><b>~${Math.round(covered / 4)}</b><span>tokens to embed</span></div><div class="stat"><b>${Math.round((100 * covered) / text.trim().length - 100)}%</b><span>duplicated by overlap</span></div>`;
      const verdict = $("[data-verdict]", body);
      if (doc.id === "playback-rollback-runbook") {
        const rule = "If the check fails, do not roll back in the EU region.", whole = cs.find((c) => c.text.includes(rule));
        const first = cs.find((c) => c.text.includes("If the check fails")), rest = cs.find((c) => c.text.includes("in the EU region. Keep"));
        verdict.innerHTML = whole ? `<div class="verdict ok">✓ <span>The rule <b>“${rule}”</b> is whole, in chunk <b>#${cs.indexOf(whole)}</b>${whole.heading ? ` (section <b>${esc(whole.heading)}</b>)` : ""}. Retrieved alone, it still says what it means.</span></div>`
          : `<div class="verdict no">✗ <span>The rule <b>“${rule}”</b> is cut in half: chunk <b>#${cs.indexOf(first)}</b> ends with <b>“…${esc(first.text.slice(first.text.indexOf("If the check fails")).slice(-40))}”</b> and chunk <b>#${cs.indexOf(rest)}</b> holds the rest. Retrieved alone, the first half reads like “don't roll back”.</span></div>`;
      } else verdict.innerHTML = "";
      const cuts = [...new Set([0, text.length, ...cs.flatMap((c) => [c.start, c.end])])].sort((a, b) => a - b);
      let html = "";
      for (let i = 0; i + 1 < cuts.length; i++) {
        const [p, q] = [cuts[i], cuts[i + 1]], cover = cs.map((c, n) => [c, n]).filter(([c]) => c.start <= p && c.end >= q);
        const starts = cs.map((c, n) => [c, n]).filter(([c]) => c.start === p);
        html += starts.map(([, n]) => `<span class="cut" data-n="${n}"></span>`).join("");
        const seg = esc(text.slice(p, q));
        if (!cover.length) html += `<span class="gap">${seg}</span>`;
        else if (cover.length > 1) html += `<mark style="background:#c9c3ee" title="overlap: chunks ${cover.map(([, n]) => "#" + n).join(", ")}">${seg}</mark>`;
        else { const [c, n] = cover[0]; html += `<mark style="background:${PASTEL[n % PASTEL.length]}" title="${esc(c.id)}${c.heading ? " · " + esc(c.heading) : ""}">${seg}</mark>`; }
      }
      $("[data-view]", body).innerHTML = html;
    }
    render();
  };

  // Module 4: prompt assembler
  widgets.prompt = (body) => {
    const qs = D.questions.filter((q) => q.split === "dev");
    body.innerHTML = `<div class="controls"><label class="control grow">Question<select data-q>${qs.map((q) => `<option value="${q.id}">${q.id} · ${esc(q.question)}</option>`).join("")}</select></label>
      <div class="control">Asked by<div class="seg" data-role><button type="button" data-r="engineer" aria-pressed="true">engineer</button><button type="button" data-r="sre" aria-pressed="false">sre</button></div></div>
      <label class="control"><span>k <output data-ko>5</output></span><input type="range" data-k min="1" max="10" value="5"></label>
      <label class="control"><span>budget <output data-bo>1500</output> tokens</span><input type="range" data-budget min="200" max="3000" step="100" value="1500"></label></div>
      <div class="controls" style="margin-top:-4px"><label class="toggle"><input type="checkbox" data-filter checked> Apply access + freshness filter before ranking</label><label class="toggle"><input type="checkbox" data-arch> Include archived documents</label></div>
      <div data-verdict></div><div class="grid2"><div><p class="small muted" style="margin:0 0 6px">Retrieved (BM25 over sections, best first)</p><div class="results" data-hits></div></div><div><p class="small muted" style="margin:0 0 6px">Context budget</p><div class="budget" data-bar></div><p class="small muted" data-used></p><p class="small muted" style="margin:10px 0 6px">The prompt the model receives</p><div class="prompt-view" data-prompt></div></div></div>`;
    let role = "engineer";
    $("[data-role]", body).addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; role = b.dataset.r; $$("[data-role] button", body).forEach((x) => x.setAttribute("aria-pressed", x === b)); render(); });
    $$("select,input", body).forEach((n) => n.addEventListener("input", render));
    function render() {
      const q = qs.find((x) => x.id === $("[data-q]", body).value), k = +$("[data-k]", body).value, budget = +$("[data-budget]", body).value;
      const filter = $("[data-filter]", body).checked, arch = $("[data-arch]", body).checked;
      $("[data-ko]", body).textContent = k; $("[data-bo]", body).textContent = budget;
      const hits = L.retrieve(index(), q.question, k, role, arch, filter);
      const { selected, dropped } = L.packContext(hits, budget), sel = new Set(selected), drop = new Set(dropped);
      const leaks = selected.filter((h) => !L.allowed(h.item, role, true)), stale = selected.filter((h) => h.item.meta.status === "archived");
      $("[data-hits]", body).innerHTML = hits.length ? hits.map((h, i) => {
        const leak = !L.allowed(h.item, role, true), state = sel.has(h) ? '<span class="badge ok">in prompt</span>' : drop.has(h) ? '<span class="badge">over budget</span>' : '<span class="badge">duplicate</span>';
        return `<div class="result ${leak ? "blocked" : ""} ${drop.has(h) ? "dropped" : ""}"><div class="result-top"><span class="rank">S${sel.has(h) ? selected.indexOf(h) + 1 : "–"}</span><span class="rid">${esc(h.item.id)}</span>${badges(h.item.meta)}<span class="rscore">${L.countTokens(L.formatSource(1, h.item))} tok</span></div><div class="snippet">${esc(h.item.heading || h.item.title)} ${state}</div></div>`;
      }).join("") : '<p class="empty">Nothing retrieved: the pipeline abstains without calling the model.</p>';
      const p = L.buildPrompt(q.question, selected), sysT = L.countTokens(p.system), used = selected.reduce((s, h, i) => s + L.countTokens(L.formatSource(i + 1, h.item)), 0);
      const qT = L.countTokens(q.question), all = Math.max(budget + sysT + qT, used + sysT + qT);
      $("[data-bar]", body).innerHTML = `<span style="width:${(100 * sysT) / all}%;background:#8a84c9">rules</span>` + selected.map((h, i) => `<span style="width:${(100 * L.countTokens(L.formatSource(i + 1, h.item))) / all}%;background:${COLORS[i % COLORS.length]}" title="S${i + 1} ${esc(h.item.id)}">S${i + 1}</span>`).join("") + `<span style="width:${(100 * qT) / all}%;background:#2f8f83">Q</span>`;
      $("[data-used]", body).textContent = `${used} of ${budget} source tokens used · ${sysT + used + qT} tokens in total (estimate: characters ÷ 4)`;
      let user = esc(p.user);
      leaks.forEach((h) => { const t = esc(h.item.text); user = user.replace(t, `<span class="leak">${t}</span>`); });
      $("[data-prompt]", body).innerHTML = hits.length ? `<span class="sys">── system ──\n${esc(p.system)}</span>\n\n── user ──\n` + user.replace(/(\[S\d+\][^\n]*)/g, '<span class="src">$1</span>').replace(/(Question: .*)$/, '<span class="q">$1</span>') : "(no model call)";
      const v = $("[data-verdict]", body);
      if (leaks.length) v.innerHTML = `<div class="verdict no">✗ <span><b>${leaks.length} SRE-only chunk${leaks.length > 1 ? "s are" : " is"}</b> in an engineer's prompt. Whatever the system prompt says, the model can now repeat it. Access control has to happen before text reaches the model.</span></div>`;
      else if (stale.length) v.innerHTML = `<div class="verdict no">✗ <span><b>${stale.length} archived chunk${stale.length > 1 ? "s" : ""}</b> in the prompt: the model now sees two versions of the rules and has to guess which one is current.</span></div>`;
      else if (!hits.length) v.innerHTML = `<div class="verdict ok">✓ <span>No evidence retrieved, so the system answers “I don't know” and skips the model call.</span></div>`;
      else v.innerHTML = `<div class="verdict ok">✓ <span>Only chunks this ${role} may read, from current documents, are in the prompt.</span></div>`;
    }
    render();
  };

  // Module 5: ranking metrics workbench
  widgets.metrics = (body) => {
    const qs = D.questions.filter((q) => q.split === "dev" && q.relevant.length);
    body.innerHTML = `<div class="controls"><label class="control grow">Question<select data-q>${qs.map((q) => `<option value="${q.id}">${q.id} · ${esc(q.question)}</option>`).join("")}</select></label><label class="control"><span>k <output data-ko>3</output></span><input type="range" data-k min="1" max="8" value="3"></label><button type="button" class="seg" style="padding:6px 12px;background:#fff" data-reset>Reset to BM25 ranking</button></div>
      <div class="grid2"><div><p class="small muted" style="margin:0 0 6px">Ranked documents. Move them, or change which count as relevant.</p><ul class="rank-list" data-list></ul></div><div><div class="metric-grid" data-m style="grid-template-columns:1fr 1fr"></div><p class="small muted" data-why></p></div></div>`;
    let ranking = [], relevant = new Set();
    function reset() {
      const q = qs.find((x) => x.id === $("[data-q]", body).value);
      ranking = L.uniqueDocs(L.retrieve(index(), q.question, 30, q.role)).slice(0, 8);
      for (const r of q.relevant) if (!ranking.includes(r)) ranking.push(r);
      ranking = ranking.slice(0, 8 + q.relevant.length); relevant = new Set(q.relevant); render();
    }
    $("[data-q]", body).addEventListener("input", reset); $("[data-reset]", body).addEventListener("click", reset); $("[data-k]", body).addEventListener("input", render);
    $("[data-list]", body).addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return; const i = +b.dataset.i, j = i + (b.dataset.d === "up" ? -1 : 1);
      if (j < 0 || j >= ranking.length) return; [ranking[i], ranking[j]] = [ranking[j], ranking[i]]; render();
    });
    $("[data-list]", body).addEventListener("change", (e) => { const c = e.target.closest("input"); if (!c) return; c.checked ? relevant.add(c.dataset.id) : relevant.delete(c.dataset.id); render(); });
    function render() {
      const k = +$("[data-k]", body).value, rel = [...relevant]; $("[data-ko]", body).textContent = k;
      $("[data-list]", body).innerHTML = ranking.map((id, i) => `${i === k ? '<li class="kline"></li>' : ""}<li class="${relevant.has(id) ? "rel" : ""} ${i >= k ? "outk" : ""}"><span class="pos">${i + 1}</span><span class="name">${esc(id)}</span><label><input type="checkbox" data-id="${esc(id)}" ${relevant.has(id) ? "checked" : ""}>relevant</label><button type="button" data-i="${i}" data-d="up" aria-label="move up">↑</button><button type="button" data-i="${i}" data-d="down" aria-label="move down">↓</button></li>`).join("");
      const m = { hit: L.hitAtK(ranking, rel, k), recall: L.recallAtK(ranking, rel, k), rr: L.reciprocalRank(ranking, rel, k), ndcg: L.ndcgAtK(ranking, rel, k) };
      const topk = ranking.slice(0, k), found = topk.filter((x) => relevant.has(x)), first = topk.findIndex((x) => relevant.has(x));
      $("[data-m]", body).innerHTML = [["hit", `Hit@${k}`, "any relevant doc in the top k?"], ["recall", `Recall@${k}`, `${found.length} of ${rel.length} relevant found`], ["rr", "Reciprocal rank", first < 0 ? "none in the top k" : `first relevant at position ${first + 1} → 1/${first + 1}`], ["ndcg", `nDCG@${k}`, "1.0 = relevant docs all at the top"]].map(([key, name, why]) => `<div class="metric"><b>${f2(m[key])}</b><div>${name}</div><div class="small">${why}</div></div>`).join("");
      $("[data-why]", body).textContent = rel.length ? "Averaged over all questions, reciprocal rank becomes MRR. Hit is forgiving, recall checks completeness, MRR and nDCG reward putting the answer first." : "No document is marked relevant: these metrics are undefined (an abstention question).";
    }
    reset();
  };

  // Module 5: live evaluation board (BM25 over the dev set)
  widgets.evalboard = (body) => {
    body.innerHTML = `<div class="controls"><label class="control">Chunking<select data-s><option value="headings/800">headings, 800</option><option value="headings/400">headings, 400</option><option value="paragraph/600">paragraph, 600</option><option value="fixed/300">fixed, 300</option><option value="fixed/300/100">fixed, 300 + 100 overlap</option><option value="document/800">whole documents</option></select></label><label class="control"><span>k (chunks) <output data-ko>3</output></span><input type="range" data-k min="1" max="10" value="3"></label><label class="toggle"><input type="checkbox" data-split> include the 6 test questions</label></div><div class="stat-row" data-sum></div><table class="heat" data-types></table><details><summary>Every question</summary><table data-rows></table></details>`;
    $$("select,input", body).forEach((n) => n.addEventListener("input", render));
    function render() {
      const [strategy, size, ov] = $("[data-s]", body).value.split("/"), k = +$("[data-k]", body).value; $("[data-ko]", body).textContent = k;
      const ix = index(strategy, +size, +(ov || 0)), qs = D.questions.filter((q) => $("[data-split]", body).checked || q.split === "dev");
      const rows = qs.map((q) => { const hits = L.retrieve(ix, q.question, k, q.role), docs = L.uniqueDocs(hits);
        return { q, docs, hit: L.hitAtK(docs, q.relevant, k), recall: L.recallAtK(docs, q.relevant, k), mrr: L.reciprocalRank(docs, q.relevant, k), evidence: L.evidenceRecall(hits.map((h) => h.item.text), q.evidence), tokens: hits.reduce((s, h) => s + L.countTokens(h.item.text), 0) }; });
      const mean = (key, rs = rows) => { const v = rs.map((r) => r[key]).filter((x) => x !== null); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
      $("[data-sum]", body).innerHTML = [["hit", "hit@k"], ["recall", "doc recall"], ["mrr", "MRR"], ["evidence", "evidence found"], ["tokens", "tokens / question"]].map(([key, label]) => `<div class="stat"><b>${key === "tokens" ? Math.round(mean(key)) : f2(mean(key))}</b><span>${label}</span></div>`).join("");
      const types = [...new Set(rows.map((r) => r.q.type))].sort();
      const cell = (v) => v === null ? '<td class="v muted">–</td>' : `<td class="v" style="background:rgba(${v < 0.5 ? "178,59,70" : v < 0.9 ? "208,138,31" : "47,120,109"},${0.12 + 0.18 * (v < 0.5 ? 1 - v : v)})">${v.toFixed(2)}</td>`;
      $("[data-types]", body).innerHTML = `<tr><th>question type</th><th>n</th><th>evidence found</th><th>doc recall</th><th>MRR</th></tr>` + types.map((t) => { const rs = rows.filter((r) => r.q.type === t); return `<tr><td>${t}</td><td class="v">${rs.length}</td>${cell(mean("evidence", rs))}${cell(mean("recall", rs))}${cell(mean("mrr", rs))}</tr>`; }).join("");
      $("[data-rows]", body).innerHTML = `<tr><th>id</th><th>type</th><th>evidence</th><th>retrieved documents</th></tr>` + rows.map((r) => `<tr><td class="mono">${r.q.id}</td><td>${r.q.type}</td><td class="mono">${r.evidence === null ? "–" : r.evidence === 1 ? "✓" : r.evidence ? "½" : "✗"}</td><td class="mono small">${r.docs.map((d) => r.q.relevant.includes(d) ? `<b>${d}</b>` : d).join(", ") || "(none)"}</td></tr>`).join("");
    }
    render();
  };

  // Module 6: reciprocal rank fusion
  widgets.rrf = (body) => {
    const q = "How do I undo a bad playback release?";
    const lists = { A: L.uniqueDocs(L.retrieve(index("document"), q, 6, "engineer")),
      B: ["playback-rollback-runbook", "deploy-pipeline", "incident-commander-guide", "playback-architecture", "feature-flags-policy", "live-events-playbook"] };
    body.innerHTML = `<p class="small" style="margin-top:0">Query: <b class="mono">${esc(q)}</b></p><div class="controls"><label class="control"><span>c <output data-co>60</output></span><input type="range" data-c min="0" max="120" value="60"></label></div><div class="grid2" style="grid-template-columns:1fr 1fr 1.25fr"><div><p class="small muted">BM25 (real, from the knowledge base)</p><ul class="rank-list" data-l="A"></ul></div><div><p class="small muted">Vector search (example ranking)</p><ul class="rank-list" data-l="B"></ul></div><div><p class="small muted">Fused with RRF</p><div class="results" data-f></div></div></div>`;
    $$("[data-l]", body).forEach((ul) => ul.addEventListener("click", (e) => { const b = e.target.closest("button"); if (!b) return; const l = lists[ul.dataset.l], i = +b.dataset.i, j = i + (b.dataset.d === "up" ? -1 : 1); if (j < 0 || j >= l.length) return; [l[i], l[j]] = [l[j], l[i]]; render(); }));
    $("[data-c]", body).addEventListener("input", render);
    function render() {
      const c = +$("[data-c]", body).value; $("[data-co]", body).textContent = c;
      ["A", "B"].forEach((k) => { $(`[data-l="${k}"]`, body).innerHTML = lists[k].map((id, i) => `<li><span class="pos">${i + 1}</span><span class="name" style="font-size:11.5px">${esc(id)}</span><button type="button" data-i="${i}" data-d="up">↑</button><button type="button" data-i="${i}" data-d="down">↓</button></li>`).join(""); });
      const fused = L.rrf([lists.A, lists.B], c), max = fused.length ? fused[0].score : 1;
      $("[data-f]", body).innerHTML = fused.slice(0, 6).map((f, i) => { const ra = lists.A.indexOf(f.id), rb = lists.B.indexOf(f.id), ca = ra < 0 ? 0 : 1 / (c + ra + 1), cb = rb < 0 ? 0 : 1 / (c + rb + 1);
        return `<div class="result"><div class="result-top"><span class="rank">${i + 1}</span><span class="rid" style="font-size:11.5px">${esc(f.id)}</span><span class="rscore">${f.score.toFixed(4)}</span></div><div class="stack" style="margin:6px 0 2px"><span style="width:${(100 * ca) / max}%;background:#6960d6" title="BM25 rank ${ra + 1}"></span><span style="width:${(100 * cb) / max}%;background:#2f8f83" title="vector rank ${rb + 1}"></span></div><div class="snippet" style="margin:0">${ra < 0 ? "not in BM25" : `BM25 #${ra + 1}: 1/(${c}+${ra + 1})`} · ${rb < 0 ? "not in vectors" : `vector #${rb + 1}: 1/(${c}+${rb + 1})`}</div></div>`; }).join("");
    }
    render();
  };

  // Module 7: latency and cost calculator
  widgets.cost = (body) => {
    const fields = [["qpd", "Questions per day", 2000, 10, 200000], ["k", "Chunks in the prompt", 5, 1, 20], ["chunk", "Tokens per chunk", 200, 50, 1500], ["fixed", "System + question tokens", 250, 50, 2000], ["out", "Answer tokens", 200, 20, 2000], ["pin", "Input price, $ per 1M tokens", 1, 0, 30], ["pout", "Output price, $ per 1M tokens", 5, 0, 100], ["ttft", "Time to first token, ms", 400, 50, 5000], ["tps", "Output speed, tokens/s", 60, 5, 500], ["ret", "Retrieval, ms", 30, 1, 2000], ["rr", "Reranking, ms (0 = off)", 0, 0, 3000]];
    body.innerHTML = `<div class="grid2"><div class="controls" style="display:grid;grid-template-columns:1fr 1fr;gap:10px 14px">${fields.map(([id, label, v, min, max]) => `<label class="control">${label}<input type="text" inputmode="decimal" data-f="${id}" value="${v}" data-min="${min}" data-max="${max}"></label>`).join("")}</div><div><div class="metric-grid" data-m style="grid-template-columns:1fr 1fr"></div><p class="small muted" style="margin:12px 0 4px">Latency of one answer</p><div class="budget" data-lat style="height:26px"></div><p class="small muted" data-lt></p></div></div><p class="small muted">Prices here are placeholders: look up your provider's current pricing. Input tokens are a large share of RAG costs because every question carries its retrieved context.</p>`;
    $$("input", body).forEach((n) => n.addEventListener("input", render));
    function val(id) { const n = $(`[data-f="${id}"]`, body), x = parseFloat(n.value); return isNaN(x) ? 0 : Math.max(+n.dataset.min, Math.min(+n.dataset.max, x)); }
    function render() {
      const tin = val("k") * val("chunk") + val("fixed"), tout = val("out"), per = (tin * val("pin") + tout * val("pout")) / 1e6, month = per * val("qpd") * 30;
      const gen = (1000 * tout) / (val("tps") || 1), parts = [["retrieve", val("ret"), "#6960d6"], ["rerank", val("rr"), "#8a5cc9"], ["first token", val("ttft"), "#d08a1f"], ["writing the answer", gen, "#2f8f83"]], total = parts.reduce((s, p) => s + p[1], 0);
      $("[data-m]", body).innerHTML = `<div class="metric"><b>${Math.round(tin).toLocaleString()}</b><div>input tokens / question</div></div><div class="metric"><b>$${(per * 1000).toFixed(2)}</b><div>per 1,000 questions</div></div><div class="metric"><b>$${month < 100 ? month.toFixed(2) : Math.round(month).toLocaleString()}</b><div>per month (30 days)</div></div><div class="metric"><b>${(total / 1000).toFixed(1)} s</b><div>until the full answer</div></div>`;
      $("[data-lat]", body).innerHTML = parts.filter((p) => p[1] > 0).map(([n, ms, c]) => `<span style="width:${(100 * ms) / total}%;background:${c}" title="${n}: ${Math.round(ms)} ms">${n}</span>`).join("");
      $("[data-lt]", body).textContent = parts.filter((p) => p[1] > 0).map(([n, ms]) => `${n} ${Math.round(ms)} ms`).join(" · ") + ". Streaming shows text after retrieve + rerank + first token.";
    }
    render();
  };

  // Home: the pipeline, stage by stage, for one question
  widgets.pipeline = (body) => {
    const answers = JSON.parse(body.dataset.answers || "{}");
    const stages = [["docs", "Documents", "24 Markdown files", 3], ["chunk", "Chunk", "split into sections", 3], ["index", "Index", "BM25 + vectors", 1], ["question", "Question", "from a user + their role", 4], ["retrieve", "Retrieve", "best chunks, filtered", 1], ["pack", "Pack", "fit a token budget", 4], ["generate", "Generate", "model answers from sources", 4], ["cite", "Cite & check", "labels → documents", 4]];
    const qs = [["q02", "engineer"], ["q13", "engineer"], ["q14", "sre"], ["q03", "engineer"]];
    body.innerHTML = `<div class="presets" style="margin:0 0 12px"><span>Question:</span>${qs.map(([id, role], i) => `<button type="button" data-i="${i}">${esc(D.questions.find((q) => q.id === id).question)} <span class="muted">(${role})</span></button>`).join("")}</div>
      <div class="pipe"><div class="lane"><div class="lane-label">INDEXING · ONCE, AND WHEN DOCUMENTS CHANGE</div>${stages.slice(0, 3).map(stage).join("")}</div><div class="lane"><div class="lane-label">ANSWERING · EVERY QUESTION</div>${stages.slice(3).map(stage).join("")}</div></div><div class="stage-panel" data-panel aria-live="polite"></div>`;
    function stage([id, name, sub, m]) { return `<button type="button" class="stage" data-st="${id}" aria-pressed="false"><span class="m">MODULE ${m}</span><b>${name}</b><small>${sub}</small></button>`; }
    let qi = 0, st = "retrieve";
    body.addEventListener("click", (e) => { const s = e.target.closest("[data-st]"), p = e.target.closest("[data-i]"); if (s) st = s.dataset.st; if (p) qi = +p.dataset.i; render(); });
    function render() {
      $$("[data-st]", body).forEach((b) => b.setAttribute("aria-pressed", b.dataset.st === st));
      $$(".presets button", body).forEach((b) => b.style.background = +b.dataset.i === qi ? "#e4e0ff" : "");
      const [qid, role] = qs[qi], q = D.questions.find((x) => x.id === qid), cs = chunks(), ix = index();
      const all = L.retrieve(ix, q.question, 8, role, false, false), hits = L.retrieve(ix, q.question, 5, role), { selected } = L.packContext(hits, 1500);
      const panel = $("[data-panel]", body);
      const view = {
        docs: () => `<h4>The knowledge base</h4><p class="small">Runbooks, postmortems and policies of Lumen, a fictional streaming platform. Metadata decides who may read each document and whether it is still current.</p><div class="results">${D.docs.slice(0, 6).map((d) => `<div class="result"><span class="rid">${d.id}</span>${badges(d.meta)} <span class="small muted">updated ${d.meta.updated}</span></div>`).join("")}<p class="small muted">…and ${D.docs.length - 6} more.</p></div>`,
        chunk: () => `<h4>${cs.length} chunks</h4><p class="small">Each document is split at its Markdown headings, so a chunk is one section that makes sense on its own. Every chunk remembers its document, heading and exact character offsets.</p>${cs.filter((c) => c.doc_id === "playback-rollback-runbook").slice(0, 4).map((c) => `<div class="result"><span class="rid">${c.id}</span> <span class="small muted">${esc(c.heading || "(intro)")} · chars ${c.start}–${c.end}</span></div>`).join("")}`,
        index: () => `<h4>Searchable indexes</h4><p class="small">The keyword index maps ${ix.df.size.toLocaleString()} distinct terms to the chunks that contain them (Module 1). A vector index stores one embedding per chunk, so search can match meaning instead of words (Module 2).</p>`,
        question: () => `<h4>“${esc(q.question)}”</h4><p class="small">Asked by an <b>${role}</b>. Search terms after tokenizing: <span class="mono">${L.tokenize(q.question).join(" · ")}</span></p>`,
        retrieve: () => `<h4>Best chunks for this ${role}</h4><div class="results">${all.map((h) => { const ok = L.allowed(h.item, role); return `<div class="result ${ok ? "" : "blocked"}"><div class="result-top"><span class="rid">${esc(h.item.id)}</span>${badges(h.item.meta)}<span class="rscore">${ok ? "kept" : "filtered out"}</span></div><div class="snippet">${esc(snippet(h.item.text, 110))}</div></div>`; }).join("") || '<p class="empty">No chunk matches.</p>'}</div>`,
        pack: () => selected.length ? `<h4>${selected.length} sources in the prompt</h4><p class="small">Labelled <span class="mono">[S1]…[S${selected.length}]</span> so the model can cite them; ${selected.reduce((s, h, i) => s + L.countTokens(L.formatSource(i + 1, h.item)), 0)} of 1,500 budget tokens used.</p><div class="prompt-view" style="max-height:220px">${esc(L.buildPrompt(q.question, selected).user)}</div>` : `<h4>Nothing to pack</h4><p class="small">No allowed chunk matched, so the system abstains and never calls the model.</p>`,
        generate: () => `<h4>The model writes an answer from the sources only</h4><div class="prompt-view" style="max-height:140px"><span class="sys">${esc(L.SYSTEM_PROMPT)}</span></div><p class="small" style="margin-top:10px">Answer from the offline baseline you get in Module 4:</p><div class="note mono small">${esc(answers[qid] || "")}</div>`,
        cite: () => { const a = answers[qid] || "", labels = [...new Set([...a.matchAll(/\[S(\d+)\]/g)].map((m) => +m[1]))]; return `<h4>Every claim points at a source</h4>${labels.length ? labels.map((n) => `<div class="result"><span class="rid">[S${n}]</span> → ${selected[n - 1] ? `<span class="mono">${esc(selected[n - 1].item.doc_id)}</span> › ${esc(selected[n - 1].item.heading)}` : '<span class="badge no">no such source</span>'}</div>`).join("") : `<p class="small">The answer is an abstention: <span class="mono">${esc(a)}</span>. For this question that is the right result.</p>`}<p class="small muted" style="margin-top:10px">Module 5 measures how often the right passage was retrieved and whether answers contain the facts they should.</p>`; },
      };
      panel.innerHTML = view[st]();
    }
    render();
  };

  document.addEventListener("DOMContentLoaded", () => {
    chrome();
    if (!L || !D) return;
    $$("[data-widget]").forEach((w) => {
      const body = $(".widget-body", w) || w, fn = widgets[w.dataset.widget];
      if (fn) { body.innerHTML = ""; try { fn(body); } catch (err) { body.innerHTML = `<p class="empty">This widget failed to load: ${esc(err.message)}</p>`; console.error(err); } }
    });
  });
})();
