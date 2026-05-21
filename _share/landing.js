/* rkitect.ai landing â€” animations + interactions */
const prefersReduced = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

/* â€” Scroll progress hairline â€” */
(function () {
  const el = document.getElementById("prog");
  if (!el) return;
  const onScroll = () => {
    const h = document.documentElement;
    const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
    el.style.setProperty("--p", Math.min(100, Math.max(0, pct)) + "%");
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();

/* â€” Demo console state machine: route â†’ style â†’ add sofa â€” */
(function () {
  const demo = document.getElementById("demo");
  const wrap = document.getElementById("slider-wrap");
  if (!demo) return;

  const s1 = document.getElementById("s1");
  const s2 = document.getElementById("s2");
  const s3 = document.getElementById("s3");
  const btnRoute = document.getElementById("btn-route");
  const btnSofa = document.getElementById("btn-sofa");
  const btnLamp = document.getElementById("btn-lamp");
  const btnRug = document.getElementById("btn-rug");
  const styleChips = document.querySelectorAll("#console [data-style]");

  const state = { segmented: false, style: "japandi", sofa: false };

  // Initial active step
  s1.classList.add("active");

  const refresh = () => {
    s1.classList.toggle("done", state.segmented);
    s1.classList.toggle("active", !state.segmented);

    // Step 2 is Sofa placement. Active once routed, done once sofa is added.
    s2.classList.toggle("active", state.segmented && !state.sofa);
    s2.classList.toggle("done", state.segmented && state.sofa);

    // Step 3 is Style selection. Active once sofa is added.
    s3.classList.toggle("active", state.segmented && state.sofa);
    s3.classList.toggle("done", false);

    btnRoute.disabled = state.segmented;
    btnRoute.textContent = state.segmented
      ? "Routed \u2713"
      : "Analyze With Chief Architect";

    btnSofa.disabled = !state.segmented;
    btnSofa.textContent = state.sofa ? "Sofa added \u2713" : "+ Add sofa";
    btnSofa.classList.toggle("selected", state.sofa);

    btnLamp.disabled = !state.sofa;
    btnRug.disabled = !state.sofa;
    if (!state.sofa) {
      btnLamp.classList.remove("selected");
      btnRug.classList.remove("selected");
      btnLamp.textContent = "+ Lamp";
      btnRug.textContent = "+ Rug";
    }

    styleChips.forEach((c) => {
      c.disabled = !state.sofa;
      const isSelected = c.dataset.style === state.style;
      c.classList.toggle("selected", isSelected);
    });
  };
  refresh();

  // Step 1: routing
  btnRoute.addEventListener("click", (e) => {
    if (state.segmented) return;

    // Tactical ripple effect
    const ripple = document.createElement("span");
    ripple.classList.add("ripple-span");
    const rect = btnRoute.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    btnRoute.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);

    demo.classList.add("segmenting");
    setTimeout(() => {
      demo.classList.remove("segmenting");
      demo.classList.add("segmented");
      state.segmented = true;
      refresh();
    }, 1100);
  });

  // Step 2: style selection (live filter on after layer)
  styleChips.forEach((c) =>
    c.addEventListener("click", () => {
      state.style = c.dataset.style;
      demo.dataset.style = c.dataset.style;
      refresh();
      updateDemoImage();
    }),
  );

  const demoAfterImg = document.getElementById("demo-after-img");

  const updateDemoImage = () => {
    const style = state.style; // 'japandi', 'scandinavian', 'industrial', 'midcentury'
    const hasLamp = btnLamp.classList.contains("selected");
    const hasRug = btnRug.classList.contains("selected");

    if (style === "japandi") {
      // Japandi maps to the original names in landing.html/js to ensure absolute correctness and preloading
      if (hasLamp && hasRug) {
        demoAfterImg.src =
          "refs/generated/demo_sofa_lamp_rug_1778960621299.png";
      } else if (hasLamp) {
        demoAfterImg.src = "refs/generated/demo_sofa_lamp_1778960589420.png";
      } else if (hasRug) {
        demoAfterImg.src = "refs/generated/demo_sofa_rug_1778960830041.png";
      } else {
        demoAfterImg.src = "refs/generated/demo_sofa_1778960568439.png";
      }
    } else {
      // Other styles map to their respective clean-named files
      let imgName = "";
      if (hasLamp && hasRug) {
        imgName = `${style}_sofa_lamp_rug.png`;
      } else if (hasLamp) {
        imgName = `${style}_sofa_lamp.png`;
      } else if (hasRug) {
        imgName = `${style}_sofa_rug.png`;
      } else {
        imgName = `${style}_sofa.png`;
      }
      demoAfterImg.src = "refs/generated/" + imgName;
    }
  };

  // Step 3: add sofa â†’ ghost placement â†’ render crossfade
  btnSofa.addEventListener("click", () => {
    if (!state.segmented) return;

    if (state.sofa) {
      // Toggle off
      state.sofa = false;
      demo.classList.remove("rendered", "placing");
      refresh();
      updateDemoImage();
    } else {
      // Toggle on
      state.sofa = true;
      demo.classList.add("placing");
      updateDemoImage(); // Load the correct styled image immediately as it begins placing!
      refresh();
      setTimeout(() => {
        demo.classList.add("rendered");
        setTimeout(() => demo.classList.remove("placing"), 300);
      }, 700);
    }
  });

  // Lamp / rug real image swaps
  [btnLamp, btnRug].forEach((b) =>
    b.addEventListener("click", () => {
      if (b.classList.contains("selected")) {
        b.classList.remove("selected");
        b.textContent = "+ " + (b.id === "btn-lamp" ? "Lamp" : "Rug");
      } else {
        b.classList.add("selected");
        b.textContent = (b.id === "btn-lamp" ? "Lamp" : "Rug") + " \u2713";
      }
      updateDemoImage();
    }),
  );

  // Parallax + entrance untouched
  if (!prefersReduced && wrap) {
    let ticking = false;
    const update = () => {
      const r = wrap.getBoundingClientRect();
      const y = Math.max(
        -40,
        Math.min(40, (r.top + r.height / 2 - window.innerHeight / 2) * -0.06),
      );
      wrap.style.transform = `translateY(${y}px)`;
      ticking = false;
    };
    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          requestAnimationFrame(update);
          ticking = true;
        }
      },
      { passive: true },
    );
  }
})();

/* â€” IntersectionObserver fade-in â€” */
(function () {
  const els = document.querySelectorAll(
    ".fade-in, .stagger, .grid, .compare, .steps, .phases",
  );
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("show");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -80px 0px" },
  );
  els.forEach((e) => io.observe(e));
  document.querySelectorAll("section.s").forEach((s) => {
    const so = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("show");
            so.unobserve(e.target);
          }
        });
      },
      { threshold: 0.02 },
    );
    so.observe(s);
  });
})();

/* â€” Number counters â€” */
(function () {
  const els = document.querySelectorAll(".counter");
  const fmt = (v, dec, prefix, suffix) =>
    `${prefix || ""}${dec ? v.toFixed(dec) : Math.round(v)}${suffix || ""}`;
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
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          start(e.target);
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.6 },
  );
  els.forEach((e) => io.observe(e));
})();

/* â€” Waitlist submit + post-submit reveal â€” */
(function () {
  const form = document.getElementById("wl");
  if (!form) return;

  const btn = document.getElementById("wl-btn");
  const nameInp = document.getElementById("wl-name");
  const emailInp = document.getElementById("wl-email");
  const contactInp = document.getElementById("wl-contact");
  const roleInp = document.getElementById("wl-role");
  const allInputs = form.querySelectorAll("input, select");
  const post = document.getElementById("post-submit");
  const emailEcho = document.getElementById("ps-email");

  // Replace this with your Google Apps Script Web App URL or n8n/Zapier Webhook URL
  const WEBHOOK_URL =
    "https://script.google.com/macros/s/AKfycbyhn_nrc1Bb2rjiS5VXICGKlp6WLByQL2KjhrvHwtWdNQ9BEspfusHxpt6Y0zW3dT5b/exec";

  // Dynamic Validation UI Helpers
  const showError = (input, message) => {
    input.classList.add("invalid-input");
    let errEl = input.nextElementSibling;
    if (!errEl || !errEl.classList.contains("error-msg")) {
      errEl = document.createElement("span");
      errEl.className = "error-msg";
      input.parentNode.insertBefore(errEl, input.nextSibling);
    }
    errEl.textContent = message;
  };

  const clearError = (input) => {
    input.classList.remove("invalid-input");
    const errEl = input.nextElementSibling;
    if (errEl && errEl.classList.contains("error-msg")) {
      errEl.remove();
    }
  };

  // Wire up live clear-on-input listeners for fluid UX
  [nameInp, emailInp, contactInp, roleInp].forEach((inp) => {
    if (!inp) return;
    const eventName = inp.tagName === "SELECT" ? "change" : "input";
    inp.addEventListener(eventName, () => {
      clearError(inp);
    });
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    let isValid = true;

    // 1. Validate Name
    if (nameInp) {
      const val = nameInp.value.trim();
      if (val.length < 2) {
        showError(nameInp, "Please enter your name (at least 2 characters).");
        isValid = false;
      } else {
        clearError(nameInp);
      }
    }

    // 2. Validate Email
    if (emailInp) {
      const val = emailInp.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(val)) {
        showError(
          emailInp,
          "Please enter a valid email address (e.g. you@studio.com).",
        );
        isValid = false;
      } else {
        clearError(emailInp);
      }
    }

    // 3. Validate Contact (Allow digits, +, -, spaces, parentheses. Length 7-18)
    if (contactInp) {
      const val = contactInp.value.trim();
      const contactRegex = /^[0-9+\-\s()]{7,18}$/;
      if (val.length === 0) {
        showError(contactInp, "Please enter your phone number or contact ID.");
        isValid = false;
      } else if (!contactRegex.test(val)) {
        showError(
          contactInp,
          "Please enter a valid contact number (7-18 digits).",
        );
        isValid = false;
      } else {
        clearError(contactInp);
      }
    }

    // 4. Validate Role Select
    if (roleInp) {
      const val = roleInp.value;
      if (!val) {
        showError(roleInp, "Please select the option that describes you best.");
        isValid = false;
      } else {
        clearError(roleInp);
      }
    }

    // UX focus fallback
    if (!isValid) {
      const firstInvalid = form.querySelector(".invalid-input");
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    // Capture the data
    const formData = {
      name: nameInp ? nameInp.value : "",
      email: emailInp ? emailInp.value : "",
      contact: contactInp ? contactInp.value : "",
      role: roleInp ? roleInp.value : "",
      timestamp: new Date().toISOString(),
    };

    // UI Updates: Disable fields and show "sending" state
    const originalBtnText = btn.innerHTML;
    btn.querySelector(".lbl").textContent = "Sending...";
    btn.disabled = true;
    allInputs.forEach((el) => (el.disabled = true));

    try {
      // Send data to the webhook
      if (WEBHOOK_URL !== "YOUR_WEBHOOK_URL_HERE") {
        await fetch(WEBHOOK_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
          mode: "no-cors", // no-cors is often required for simple webhooks like Google Apps Script without OPTIONS handling
        });
      } else {
        console.warn(
          "Please replace YOUR_WEBHOOK_URL_HERE with a valid Webhook URL.",
        );
      }

      // Success UI updates
      if (emailEcho && formData.email) emailEcho.textContent = formData.email;
      btn.classList.add("done");
      btn.querySelector(".lbl").style.opacity = "0";

      if (emailInp) {
        emailInp.value = "";
        emailInp.placeholder = "Confirmation sent.";
      }

      if (post) {
        post.hidden = false;
        requestAnimationFrame(() => post.classList.add("show"));
      }
    } catch (error) {
      console.error("Error submitting form", error);
      // Re-enable form on error
      btn.disabled = false;
      btn.innerHTML = originalBtnText;
      allInputs.forEach((el) => (el.disabled = false));
      alert("Something went wrong. Please try again.");
    }
  });
})();

/* â€” Demo replay button â€” */
(function () {
  const replay = document.getElementById("demo-replay");
  const demo = document.getElementById("demo");
  if (!replay || !demo) return;
  replay.addEventListener("click", () => {
    demo.classList.remove("rendered", "placing", "segmented", "segmenting");
    demo.style.removeProperty("--cut");

    // reset image
    const afterImg = document.getElementById("demo-after-img");
    if (afterImg) afterImg.src = "refs/generated/demo_sofa_1778960568439.png";

    document.querySelectorAll(".console .chip").forEach((c) => {
      c.classList.remove("selected");
      if (c.id === "btn-route") {
        c.disabled = false;
        c.textContent = "Run route";
      }
      if (c.id === "btn-sofa") {
        c.disabled = true;
        c.textContent = "+ Add sofa";
      }
      if (c.id === "btn-lamp") {
        c.disabled = true;
        c.textContent = "+ Lamp";
      }
      if (c.id === "btn-rug") {
        c.disabled = true;
        c.textContent = "+ Rug";
      }
      if (c.dataset.style) {
        c.disabled = true;
      }
    });
    document.getElementById("s1").classList.remove("done");
    document.getElementById("s1").classList.add("active");
    document.getElementById("s2").classList.remove("done", "active");
    document.getElementById("s3").classList.remove("done", "active");
    demo.dataset.style = "japandi";
    document.querySelectorAll("#console [data-style]").forEach((c) => {
      c.classList.toggle("selected", c.dataset.style === "japandi");
    });
  });
})();

/* â€” Founder Easter egg in console â€” */
(function () {
  const styles = [
    "background: #0b0f17; color: #f3eedc; font-family: 'Spectral', serif; font-style: italic; font-size: 16px; padding: 12px 16px; border-left: 3px solid #ff2814;",
    "color: #5c6577; font-family: 'Geist Mono', monospace; font-size: 11px;",
  ];
  console.log(
    "%cBuilt by an architect after losing pitches to render queues.%c\n\nIf you are an architect or you build for them â€” we want to talk.\nDM the founder Â· /landing.html#cta",
    styles[0],
    styles[1],
  );
})();

/* â€” Live SSE feed simulator â€” */
(function () {
  const feed = document.getElementById("feed");
  if (!feed) return;

  const events = [
    {
      t: "0:00",
      e: "Comprehending",
      v: "Reading your brief â€” residential, 2BHK, Japandi",
    },
    { t: "0:02", e: "Interior Designer", v: "Drafting the design thesis" },
    {
      t: "0:04",
      e: "Palette proposed",
      v: "Clay, oak, linen â€” anchored to your two precedents",
    },
    {
      t: "0:06",
      e: "Rubric review",
      v: "Scored 87 / 100 â€” passes on the first round",
    },
    {
      t: "0:08",
      e: "Space Planner",
      v: "Drawing the floor plan, scaled to 1:50",
    },
    {
      t: "0:10",
      e: "Question raised",
      v: "Morning light from the left or right? Answered: left",
    },
    {
      t: "0:14",
      e: "3D Artist",
      v: "Setting the isometric, placing furniture at scale",
    },
    {
      t: "0:18",
      e: "Isometric ready",
      v: "Living room â€” ready for the renderer",
    },
    {
      t: "0:22",
      e: "Renderer",
      v: "Placing materials and lighting, time of day set",
    },
    {
      t: "0:31",
      e: "Photoreal output",
      v: "Variation 1 of 3 ready â€” $0.18 spent",
    },
    {
      t: "0:34",
      e: "Edit mode ready",
      v: "Move a lamp, swap a finish, change the time of day",
    },
    {
      t: "0:35",
      e: "Done",
      v: "Studio paused â€” waiting for your next instruction",
    },
  ];

  let idx = 0;
  const MAX_VISIBLE = 9;
  const appendOne = () => {
    const it = events[idx % events.length];
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `<span class="t">${it.t}</span><span class="e">${it.e}</span><span class="v">${it.v}</span>`;
    feed.appendChild(row);
    while (feed.children.length > MAX_VISIBLE)
      feed.removeChild(feed.firstElementChild);
    idx++;
  };

  let started = false;
  const startFeed = () => {
    if (started) return;
    started = true;
    appendOne();
    appendOne();
    appendOne();
    if (!prefersReduced) setInterval(appendOne, 1700);
  };
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          startFeed();
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.4 },
  );
  io.observe(feed);
})();

/* â€” 42-element rubric grid (mostly pass, 2 warns) â€” */
(function () {
  const grid = document.getElementById("grid42");
  if (!grid) return;
  const warnSet = new Set([7, 23]); // arbitrary 2 cells flagged
  for (let i = 0; i < 42; i++) {
    const cell = document.createElement("div");
    cell.className = "cell " + (warnSet.has(i) ? "warn" : "pass");
    cell.title = warnSet.has(i)
      ? `Element ${i + 1} â€” refining`
      : `Element ${i + 1} â€” pass`;
    grid.appendChild(cell);
  }

  /* Stagger reveal when the section enters */
  const cells = grid.querySelectorAll(".cell");
  cells.forEach((c, i) => {
    c.style.opacity = "0";
    c.style.transform = "scale(.7)";
    c.style.transition = `opacity .35s var(--ease-out-quint) ${i * 25}ms, transform .35s var(--ease-out-quint) ${i * 25}ms, background .25s var(--ease-out-quint), border-color .25s var(--ease-out-quint)`;
  });
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          cells.forEach((c) => {
            c.style.opacity = "1";
            c.style.transform = "scale(1)";
          });
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.4 },
  );
  io.observe(grid);
})();

/* — Multi-Agent Studio Orchestration Simulator (auto-loop) — */
(function () {
  const btn = document.getElementById("dispatchBtn");
  const netSvg =
    document.getElementById("netSvg") ||
    document.getElementById("netSvgMobile");
  if (!netSvg) return;

  let nodes = {};
  let lines = {};
  let pulses = {};
  let travelDots = [];

  function updateActiveElements() {
    const useMobile = window.innerWidth <= 768;
    nodes = {
      chief: document.getElementById(
        useMobile ? "node-chief-mobile" : "node-chief",
      ),
      planner: document.getElementById(
        useMobile ? "node-planner-mobile" : "node-planner",
      ),
      designer: document.getElementById(
        useMobile ? "node-designer-mobile" : "node-designer",
      ),
      modeler: document.getElementById(
        useMobile ? "node-modeler-mobile" : "node-modeler",
      ),
      renderer: document.getElementById(
        useMobile ? "node-renderer-mobile" : "node-renderer",
      ),
      compliance: document.getElementById(
        useMobile ? "node-compliance-mobile" : "node-compliance",
      ),
    };

    lines = {
      chiefPlanner: document.getElementById(
        useMobile ? "path-chief-planner-mobile" : "path-chief-planner",
      ),
      chiefDesigner: document.getElementById(
        useMobile ? "path-chief-designer-mobile" : "path-chief-designer",
      ),
      chiefModeler: document.getElementById(
        useMobile ? "path-chief-modeler-mobile" : "path-chief-modeler",
      ),
      chiefRenderer: document.getElementById(
        useMobile ? "path-chief-renderer-mobile" : "path-chief-renderer",
      ),
      chiefCompliance: document.getElementById(
        useMobile ? "path-chief-compliance-mobile" : "path-chief-compliance",
      ),
    };

    pulses = {
      chief: document.getElementById(
        useMobile ? "pulse-chief-mobile" : "pulse-chief",
      ),
      planner: document.getElementById(
        useMobile ? "pulse-planner-mobile" : "pulse-planner",
      ),
      designer: document.getElementById(
        useMobile ? "pulse-designer-mobile" : "pulse-designer",
      ),
      modeler: document.getElementById(
        useMobile ? "pulse-modeler-mobile" : "pulse-modeler",
      ),
      renderer: document.getElementById(
        useMobile ? "pulse-renderer-mobile" : "pulse-renderer",
      ),
      compliance: document.getElementById(
        useMobile ? "pulse-compliance-mobile" : "pulse-compliance",
      ),
    };

    travelDots = [
      document.getElementById(
        useMobile ? "travel-dot-1-mobile" : "travel-dot-1",
      ),
      document.getElementById(
        useMobile ? "travel-dot-2-mobile" : "travel-dot-2",
      ),
      document.getElementById(
        useMobile ? "travel-dot-3-mobile" : "travel-dot-3",
      ),
      document.getElementById(
        useMobile ? "travel-dot-4-mobile" : "travel-dot-4",
      ),
      document.getElementById(
        useMobile ? "travel-dot-5-mobile" : "travel-dot-5",
      ),
    ];
  }

  let isOrchestrating = false;

  function easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }

  function triggerPulse(nodeKey) {
    const pulseCircle = pulses[nodeKey];
    if (!pulseCircle) return;
    let start = null;
    const DUR = 650;
    function step(timestamp) {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / DUR, 1);
      pulseCircle.setAttribute("r", 10 + progress * 24);
      pulseCircle.setAttribute("opacity", (1 - progress) * 0.75);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        pulseCircle.setAttribute("opacity", "0");
      }
    }
    requestAnimationFrame(step);
  }

  function animateSignalDot(
    dotElement,
    pathElement,
    duration,
    reverse,
    onComplete,
  ) {
    if (typeof reverse === "function") {
      onComplete = reverse;
      reverse = false;
    }
    if (!pathElement) {
      if (onComplete) onComplete();
      return;
    }
    const pathLength = pathElement.getTotalLength();
    if (dotElement) dotElement.setAttribute("opacity", "1");
    pathElement.classList.add("processing");
    let start = null;
    function step(timestamp) {
      if (!start) start = timestamp;
      const elapsed = timestamp - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeInOutQuad(progress);
      const distance = reverse ? (1 - eased) * pathLength : eased * pathLength;
      const point = pathElement.getPointAtLength(distance);
      if (dotElement) {
        dotElement.setAttribute("cx", point.x);
        dotElement.setAttribute("cy", point.y);
      }
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        if (dotElement) dotElement.setAttribute("opacity", "0");
        pathElement.classList.remove("processing");
        if (onComplete) onComplete();
      }
    }
    requestAnimationFrame(step);
  }

  /* Run one full chief→agents→chief cycle, call onDone when finished */
  function runCycle(onDone) {
    if (isOrchestrating) return;
    isOrchestrating = true;
    if (btn) btn.disabled = true;

    updateActiveElements();

    Object.keys(nodes).forEach((k) => {
      if (nodes[k]) nodes[k].classList.remove("active");
    });
    Object.keys(lines).forEach((k) => {
      if (lines[k]) lines[k].classList.remove("active", "processing");
    });

    nodes.chief.classList.add("active");
    triggerPulse("chief");

    const specialists = [
      {
        key: "planner",
        line: lines.chiefPlanner,
        dot: travelDots[0],
        workMs: 800,
      },
      {
        key: "designer",
        line: lines.chiefDesigner,
        dot: travelDots[1],
        workMs: 1100,
      },
      {
        key: "modeler",
        line: lines.chiefModeler,
        dot: travelDots[2],
        workMs: 1400,
      },
      {
        key: "renderer",
        line: lines.chiefRenderer,
        dot: travelDots[3],
        workMs: 1700,
      },
      {
        key: "compliance",
        line: lines.chiefCompliance,
        dot: travelDots[4],
        workMs: 2000,
      },
    ];

    setTimeout(() => {
      let remaining = specialists.length;
      specialists.forEach((spec) => {
        animateSignalDot(spec.dot, spec.line, 700, () => {
          if (nodes[spec.key]) nodes[spec.key].classList.add("active");
          triggerPulse(spec.key);
          if (spec.line) spec.line.classList.add("active");
          setTimeout(() => {
            if (nodes[spec.key]) nodes[spec.key].classList.remove("active");
            animateSignalDot(spec.dot, spec.line, 700, true, () => {
              triggerPulse("chief");
              if (spec.line) spec.line.classList.remove("active");
              remaining--;
              if (remaining === 0) {
                triggerPulse("chief");
                setTimeout(() => {
                  if (nodes.chief) nodes.chief.classList.remove("active");
                  if (btn) btn.disabled = false;
                  isOrchestrating = false;
                  if (onDone) onDone();
                }, 700);
              }
            });
          }, spec.workMs);
        });
      });
    }, 800);
  }

  let loopTimer = null;
  let isVisible = false;

  function scheduleNext() {
    loopTimer = setTimeout(() => {
      if (isVisible) runCycle(scheduleNext);
    }, 2000);
  }

  function startLoop() {
    clearTimeout(loopTimer);
    isOrchestrating = false;
    if (isVisible) runCycle(scheduleNext);
  }

  /* Auto-start on scroll into view; pause when scrolled away */
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        isVisible = e.isIntersecting;
        if (isVisible) {
          if (!isOrchestrating) runCycle(scheduleNext);
        } else {
          clearTimeout(loopTimer);
        }
      });
    },
    { threshold: 0.25 },
  );

  const observerTarget =
    document.querySelector(".network-svg-container") || netSvg;
  io.observe(observerTarget);

  /* Button = manual restart / skip to next cycle */
  if (btn) btn.addEventListener("click", startLoop);

  window.runOrchestration = startLoop;
})();
