/* rkitect.ai landing — animations + interactions */
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* — Scroll progress hairline — */
(function () {
  const el = document.getElementById("prog");
  if (!el) return;
  const onScroll = () => {
    const h = document.documentElement;
    const pct = (h.scrollTop) / (h.scrollHeight - h.clientHeight) * 100;
    el.style.setProperty("--p", Math.min(100, Math.max(0, pct)) + "%");
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();

/* — Demo console state machine: segment → style → add sofa — */
(function () {
  const demo = document.getElementById("demo");
  const wrap = document.getElementById("slider-wrap");
  if (!demo) return;

  const s1 = document.getElementById("s1");
  const s2 = document.getElementById("s2");
  const s3 = document.getElementById("s3");
  const btnSegment = document.getElementById("btn-segment");
  const btnSofa    = document.getElementById("btn-sofa");
  const btnLamp    = document.getElementById("btn-lamp");
  const btnRug     = document.getElementById("btn-rug");
  const styleChips = demo.querySelectorAll('[data-style]');

  const state = { segmented: false, style: "japandi", sofa: false };

  // Initial active step
  s1.classList.add("active");

  const refresh = () => {
    s1.classList.toggle("done", state.segmented);
    s1.classList.toggle("active", !state.segmented);
    s2.classList.toggle("active", state.segmented && !state.sofa);
    s2.classList.toggle("done", state.sofa);
    s3.classList.toggle("active", state.segmented && !state.sofa);
    s3.classList.toggle("done", state.sofa);
    btnSegment.disabled = state.segmented;
    btnSegment.textContent = state.segmented ? "Segmented ✓" : "Run segmentation";
    btnSofa.disabled = !state.segmented || state.sofa;
    btnSofa.textContent = state.sofa ? "Sofa added ✓" : "+ Add sofa";
    if (state.sofa) { btnLamp.disabled = false; btnRug.disabled = false; }
    styleChips.forEach(c => c.classList.toggle("selected", c.dataset.style === state.style));
  };
  refresh();

  // Step 1: segmentation
  btnSegment.addEventListener("click", () => {
    if (state.segmented) return;
    demo.classList.add("segmenting");
    setTimeout(() => { demo.classList.remove("segmenting"); demo.classList.add("segmented"); state.segmented = true; refresh(); }, 1100);
  });

  // Step 2: style selection (live filter on after layer; only swaps once sofa added)
  styleChips.forEach(c => c.addEventListener("click", () => {
    state.style = c.dataset.style;
    demo.dataset.style = c.dataset.style;
    refresh();
  }));

  // Step 3: add sofa → ghost placement → render crossfade
  btnSofa.addEventListener("click", () => {
    if (!state.segmented || state.sofa) return;
    state.sofa = true;
    demo.classList.add("placing");
    refresh();
    setTimeout(() => {
      demo.classList.add("rendered");
      setTimeout(() => demo.classList.remove("placing"), 300);
    }, 700);
  });

  // Lamp / rug placeholder (just toggles on)
  [btnLamp, btnRug].forEach(b => b.addEventListener("click", () => {
    b.classList.add("selected");
    b.disabled = true;
    b.textContent = b.textContent.replace("+ ", "") + " ✓";
  }));

  // Parallax + entrance untouched
  if (!prefersReduced && wrap) {
    let ticking = false;
    const update = () => {
      const r = wrap.getBoundingClientRect();
      const y = Math.max(-40, Math.min(40, (r.top + r.height/2 - window.innerHeight/2) * -0.06));
      wrap.style.transform = `translateY(${y}px)`;
      ticking = false;
    };
    window.addEventListener("scroll", () => {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
  }

  // Auto-demo: after preloader + entrance settles, run segmentation as a hint.
  if (!prefersReduced) {
    setTimeout(() => { if (!state.segmented) btnSegment.click(); }, 4400);
  }
})();

/* — IntersectionObserver fade-in — */
(function () {
  const els = document.querySelectorAll(".fade-in, .stagger, .grid, .compare, .steps, .phases");
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("show"); io.unobserve(e.target); } });
  }, { threshold: 0.12, rootMargin: "0px 0px -80px 0px" });
  els.forEach(e => io.observe(e));
  document.querySelectorAll("section.s").forEach(s => {
    const so = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("show"); so.unobserve(e.target); } });
    }, { threshold: 0.02 });
    so.observe(s);
  });
})();

/* — Number counters — */
(function () {
  const els = document.querySelectorAll(".counter");
  const fmt = (v, dec, prefix, suffix) => `${prefix||""}${(dec ? v.toFixed(dec) : Math.round(v))}${suffix||""}`;
  const start = (el) => {
    const to = parseFloat(el.dataset.to);
    const dec = parseInt(el.dataset.decimals || "0", 10);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";
    const dur = 1400;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      const eased = 1 - Math.pow(1 - p, 4);
      el.textContent = fmt(to * eased, dec, prefix, suffix);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { start(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.6 });
  els.forEach(e => io.observe(e));
})();

/* — Waitlist submit + post-submit reveal — */
(function () {
  const form = document.getElementById("wl");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const btn = document.getElementById("wl-btn");
    const inp = form.querySelector("input");
    const post = document.getElementById("post-submit");
    const emailEcho = document.getElementById("ps-email");
    if (emailEcho && inp.value) emailEcho.textContent = inp.value;
    btn.classList.add("done");
    btn.disabled = true;
    btn.querySelector(".lbl").style.opacity = "0";
    inp.value = "";
    inp.placeholder = "Confirmation sent.";
    inp.disabled = true;
    if (post) {
      post.hidden = false;
      requestAnimationFrame(() => post.classList.add("show"));
    }
  });
})();

/* — Demo replay button — */
(function () {
  const replay = document.getElementById("demo-replay");
  const demo = document.getElementById("demo");
  if (!replay || !demo) return;
  replay.addEventListener("click", () => {
    demo.classList.remove("rendered", "placing", "segmented", "segmenting");
    demo.style.removeProperty("--cut");
    document.querySelectorAll("#console .chip").forEach(c => {
      c.classList.remove("selected");
      if (c.id === "btn-segment") { c.disabled = false; c.textContent = "Run segmentation"; }
      if (c.id === "btn-sofa")    { c.disabled = true;  c.textContent = "+ Add sofa"; }
      if (c.id === "btn-lamp")    { c.disabled = true;  c.textContent = "+ Lamp"; }
      if (c.id === "btn-rug")     { c.disabled = true;  c.textContent = "+ Rug"; }
    });
    document.getElementById("s1").classList.remove("done");
    document.getElementById("s1").classList.add("active");
    document.getElementById("s2").classList.remove("done", "active");
    document.getElementById("s3").classList.remove("done", "active");
    demo.dataset.style = "japandi";
    document.querySelectorAll('#console [data-style]').forEach(c => c.classList.toggle("selected", c.dataset.style === "japandi"));
  });
})();

/* — Founder Easter egg in console — */
(function () {
  const styles = [
    "background: #0b0f17; color: #f3eedc; font-family: 'Spectral', serif; font-style: italic; font-size: 16px; padding: 12px 16px; border-left: 3px solid #ff2814;",
    "color: #5c6577; font-family: 'Geist Mono', monospace; font-size: 11px;",
  ];
  console.log("%cBuilt by an architect after losing pitches to render queues.%c\n\nIf you are an architect or you build for them — we want to talk.\nDM the founder · /landing.html#cta", styles[0], styles[1]);
})();

/* — Live SSE feed simulator — */
(function () {
  const feed = document.getElementById("feed");
  if (!feed) return;

  const events = [
    { t: "0:00", e: "Comprehending",      v: "Reading your brief — residential, 2BHK, Japandi" },
    { t: "0:02", e: "Interior Designer",  v: "Drafting the design thesis" },
    { t: "0:04", e: "Palette proposed",   v: "Clay, oak, linen — anchored to your two precedents" },
    { t: "0:06", e: "Rubric review",      v: "Scored 87 / 100 — passes on the first round" },
    { t: "0:08", e: "Space Planner",      v: "Drawing the floor plan, scaled to 1:50" },
    { t: "0:10", e: "Question raised",    v: "Morning light from the left or right? Answered: left" },
    { t: "0:14", e: "3D Artist",          v: "Setting the isometric, placing furniture at scale" },
    { t: "0:18", e: "Isometric ready",    v: "Living room — ready for the renderer" },
    { t: "0:22", e: "Renderer",           v: "Placing materials and lighting, time of day set" },
    { t: "0:31", e: "Photoreal output",   v: "Variation 1 of 3 ready — $0.18 spent" },
    { t: "0:34", e: "Edit mode ready",    v: "Move a lamp, swap a finish, change the time of day" },
    { t: "0:35", e: "Done",               v: "Studio paused — waiting for your next instruction" },
  ];

  let idx = 0;
  const MAX_VISIBLE = 9;
  const appendOne = () => {
    const it = events[idx % events.length];
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `<span class="t">${it.t}</span><span class="e">${it.e}</span><span class="v">${it.v}</span>`;
    feed.appendChild(row);
    while (feed.children.length > MAX_VISIBLE) feed.removeChild(feed.firstElementChild);
    idx++;
  };

  let started = false;
  const startFeed = () => {
    if (started) return;
    started = true;
    appendOne(); appendOne(); appendOne();
    if (!prefersReduced) setInterval(appendOne, 1700);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { startFeed(); io.unobserve(e.target); } });
  }, { threshold: 0.4 });
  io.observe(feed);
})();

/* — 42-element rubric grid (mostly pass, 2 warns) — */
(function () {
  const grid = document.getElementById("grid42");
  if (!grid) return;
  const warnSet = new Set([7, 23]); // arbitrary 2 cells flagged
  for (let i = 0; i < 42; i++) {
    const cell = document.createElement("div");
    cell.className = "cell " + (warnSet.has(i) ? "warn" : "pass");
    cell.title = warnSet.has(i) ? `Element ${i+1} — refining` : `Element ${i+1} — pass`;
    grid.appendChild(cell);
  }

  /* Stagger reveal when the section enters */
  const cells = grid.querySelectorAll(".cell");
  cells.forEach((c, i) => {
    c.style.opacity = "0";
    c.style.transform = "scale(.7)";
    c.style.transition = `opacity .35s var(--ease-out-quint) ${i * 25}ms, transform .35s var(--ease-out-quint) ${i * 25}ms, background .25s var(--ease-out-quint), border-color .25s var(--ease-out-quint)`;
  });
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        cells.forEach(c => { c.style.opacity = "1"; c.style.transform = "scale(1)"; });
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.4 });
  io.observe(grid);
})();
