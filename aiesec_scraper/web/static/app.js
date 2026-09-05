/**
 * @fileoverview AIESEC in Tanta - B2C Event Radar & Command Center
 * Modern Frontend Controller integrating Three.js 3D WebGL, GSAP Motion Choreography,
 * Dynamic Telemetry, and World-Class SaaS Aesthetics.
 *
 * @typedef {Object} EventRecord
 * @property {string} event_id
 * @property {string} title
 * @property {string} date_display
 * @property {string} location
 * @property {string} city
 * @property {string} category
 * @property {string} source
 * @property {string} url
 * @property {number} b2c_score
 * @property {string} b2c_priority
 * @property {string} description
 * @property {string} recommended_action
 * @property {string} [parallel_org]
 * @property {boolean} [clash_warning]
 * @property {string} [ticket_type]
 */

/** @type {{ events: EventRecord[], sort: string, priority: string, category: string, city: string, source: string, search: string, partnersOnly: boolean, clashesOnly: boolean, activePitchEvent: EventRecord|null, activeView: 'cards'|'calendar' }} */
let state = {
  events: [],
  sort: "score_desc",
  priority: "all",
  category: "all",
  city: "all",
  source: "all",
  search: "",
  partnersOnly: false,
  clashesOnly: false,
  activePitchEvent: null,
  activeView: "cards"
};

// DOM Elements
const containerCards = document.getElementById("container-cards");
const containerCalendar = document.getElementById("container-calendar");
const calendarTimeline = document.getElementById("calendar-timeline");
const inputSearch = document.getElementById("input-search");
const selectSort = document.getElementById("select-sort");
const selectCategory = document.getElementById("select-category");
const selectCity = document.getElementById("select-city");
const selectSource = document.getElementById("select-source");
const checkPartnersOnly = document.getElementById("check-partners-only");
const checkClashesOnly = document.getElementById("check-clashes-only");
const btnViewCards = document.getElementById("btn-view-cards");
const btnViewCalendar = document.getElementById("btn-view-calendar");
const btnQuickFilterHigh = document.getElementById("btn-quick-filter-high");
const btnQuickFilterFlagship = document.getElementById("btn-quick-filter-flagship");

// Modal Elements
const pitchModal = document.getElementById("pitch-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnGeneratePitch = document.getElementById("btn-generate-pitch");
const pitchOutputBox = document.getElementById("pitch-output-box");
const pitchSubject = document.getElementById("pitch-subject");
const pitchBody = document.getElementById("pitch-body");
const btnCopyPitch = document.getElementById("btn-copy-pitch");
const btnOpenMail = document.getElementById("btn-open-mail");
const pitchEventSubtitle = document.getElementById("pitch-event-subtitle");

// Action Buttons
const btnSyncSheets = document.getElementById("btn-sync-sheets");
const btnSendEmail = document.getElementById("btn-send-email");
const btnScrapeNow = document.getElementById("btn-scrape-now");
const scrapeIcon = document.getElementById("scrape-icon");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  initThreeRadar();
  initSmoothMouseLighting();
  initLiveClock();
  setupEventListeners();
  fetchEvents();
  if (window.lucide) lucide.createIcons();
});

// ============================================================
// THREE.JS 3D HOLOGRAPHIC PARTICLE RADAR (WebGL Spatial Depth)
// ============================================================
// ============================================================
// THREE.JS 3D HOLOGRAPHIC PARTICLE RADAR GLOBE (Hero Centerpiece)
// ============================================================
function initThreeRadar() {
  const canvas = document.getElementById("hero-globe-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  try {
    const container = canvas.parentElement;
    const width = container.clientWidth || 400;
    const height = container.clientHeight || 250;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 175;

    const renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 1. Holographic Wireframe Sphere
    const globeRadius = 58;
    const wireframeGeo = new THREE.SphereGeometry(globeRadius, 20, 14);
    const wireframeMat = new THREE.MeshBasicMaterial({
      color: 0x037ef3,
      wireframe: true,
      transparent: true,
      opacity: 0.2,
      blending: THREE.AdditiveBlending
    });
    const wireframeGlobe = new THREE.Mesh(wireframeGeo, wireframeMat);
    scene.add(wireframeGlobe);

    // 2. High-Density Particle Constellation Globe
    const particleCount = 650;
    const partGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const cBlue = new THREE.Color(0x037ef3);
    const cCyan = new THREE.Color(0x00e5ff);

    for (let i = 0; i < particleCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / particleCount);
      const theta = Math.sqrt(particleCount * Math.PI) * phi;

      positions[i * 3] = globeRadius * Math.cos(theta) * Math.sin(phi);
      positions[i * 3 + 1] = globeRadius * Math.sin(theta) * Math.sin(phi);
      positions[i * 3 + 2] = globeRadius * Math.cos(phi);

      const mixed = cBlue.clone().lerp(cCyan, Math.random());
      colors[i * 3] = mixed.r;
      colors[i * 3 + 1] = mixed.g;
      colors[i * 3 + 2] = mixed.b;
    }
    partGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    partGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const partMat = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.88,
      blending: THREE.AdditiveBlending
    });
    const particleMesh = new THREE.Points(partGeo, partMat);
    scene.add(particleMesh);

    // 3. Orbiting Radar Sweep Rings
    const ringGroup = new THREE.Group();
    const ringRadii = [72, 84];
    ringRadii.forEach((r, idx) => {
      const rGeo = new THREE.RingGeometry(r, r + 1.2, 64);
      const rMat = new THREE.MeshBasicMaterial({
        color: idx === 0 ? 0x00e5ff : 0x037ef3,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.42 - idx * 0.15,
        blending: THREE.AdditiveBlending
      });
      const ringMesh = new THREE.Mesh(rGeo, rMat);
      ringMesh.rotation.x = Math.PI / 2.3 + (idx * 0.3);
      ringMesh.rotation.y = idx * 0.4;
      ringGroup.add(ringMesh);
    });
    scene.add(ringGroup);

    // 4. Egypt Hub Beacon Pins on the Globe
    const pinGroup = new THREE.Group();
    const hubs = [
      { name: "Cairo", lat: 30.0444, lon: 31.2357, color: 0x00e5ff },
      { name: "Alexandria", lat: 31.2001, lon: 29.9187, color: 0x38bdf8 },
      { name: "Tanta", lat: 30.7865, lon: 31.0004, color: 0x037ef3, primary: true },
      { name: "Giza", lat: 30.0131, lon: 31.2089, color: 0xff4d36 },
      { name: "Mansoura", lat: 31.0409, lon: 31.3785, color: 0xa855f7 },
      { name: "Assiut", lat: 27.1801, lon: 31.1837, color: 0xf59e0b }
    ];

    function latLonToVector3(lat, lon, radius) {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + 180) * (Math.PI / 180);
      return new THREE.Vector3(
        -(radius * Math.sin(phi) * Math.cos(theta)),
        radius * Math.cos(phi),
        radius * Math.sin(phi) * Math.sin(theta)
      );
    }

    hubs.forEach(hub => {
      const pos = latLonToVector3(hub.lat, hub.lon, globeRadius + 1);
      const pinGeo = new THREE.SphereGeometry(hub.primary ? 3.2 : 2.2, 16, 16);
      const pinMat = new THREE.MeshBasicMaterial({
        color: hub.color,
        blending: THREE.AdditiveBlending
      });
      const pin = new THREE.Mesh(pinGeo, pinMat);
      pin.position.copy(pos);
      pinGroup.add(pin);

      const bRingGeo = new THREE.RingGeometry(2.5, 3.8, 16);
      const bRingMat = new THREE.MeshBasicMaterial({
        color: hub.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.7,
        blending: THREE.AdditiveBlending
      });
      const bRing = new THREE.Mesh(bRingGeo, bRingMat);
      bRing.position.copy(pos);
      bRing.lookAt(0, 0, 0);
      pinGroup.add(bRing);
    });
    scene.add(pinGroup);

    // Mouse Tracking Parallax
    let targetRotX = 0.2;
    let targetRotY = 0;
    container.addEventListener("mousemove", (e) => {
      const rect = container.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      targetRotY = nx * 0.7;
      targetRotX = 0.2 + ny * 0.35;
    }, { passive: true });

    // Drag to rotate interactively
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };
    container.addEventListener("mousedown", (e) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    });
    window.addEventListener("mouseup", () => { isDragging = false; });
    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMousePos.x;
      const deltaY = e.clientY - prevMousePos.y;
      wireframeGlobe.rotation.y += deltaX * 0.01;
      particleMesh.rotation.y += deltaX * 0.01;
      pinGroup.rotation.y += deltaX * 0.01;
      wireframeGlobe.rotation.x += deltaY * 0.01;
      particleMesh.rotation.x += deltaY * 0.01;
      pinGroup.rotation.x += deltaY * 0.01;
      prevMousePos = { x: e.clientX, y: e.clientY };
    });

    // Render Animation Loop
    function animate() {
      requestAnimationFrame(animate);

      if (!isDragging) {
        wireframeGlobe.rotation.y += 0.003;
        particleMesh.rotation.y += 0.003;
        pinGroup.rotation.y += 0.003;

        ringGroup.rotation.z += 0.0035;
        ringGroup.rotation.y += 0.0018;

        scene.rotation.y += (targetRotY - scene.rotation.y) * 0.05;
        scene.rotation.x += (targetRotX - scene.rotation.x) * 0.05;
      }

      renderer.render(scene, camera);
    }
    animate();

    // Resize Observer for auto scaling
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        if (w && h) {
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
          renderer.setSize(w, h);
        }
      });
      ro.observe(container);
    }
  } catch (err) {
    console.warn("Three.js WebGL hero globe bypassed:", err);
  }
}

// ============================================================
// GSAP ANIMATIONS & MOTION CHOREOGRAPHY
// ============================================================

/**
 * Animate numerical counter using GSAP with smooth easing
 * @param {HTMLElement} el
 * @param {number} targetVal
 * @param {number} [duration=1.2]
 */
function animateCounter(el, targetVal, duration = 1.2) {
  if (!el) return;
  const endNum = parseInt(targetVal) || 0;
  if (window.gsap) {
    const currentNum = parseInt(el.innerText) || 0;
    const counterObj = { val: currentNum };
    gsap.to(counterObj, {
      val: endNum,
      duration: duration,
      ease: "power2.out",
      onUpdate: () => {
        el.innerText = Math.round(counterObj.val);
      }
    });
  } else {
    el.innerText = endNum;
  }
}

/**
 * Initialize Framer-style magnetic physics on interactive CTA buttons
 */
function initMagneticButtons() {
  if (typeof gsap === "undefined") return;
  const targets = document.querySelectorAll(".btn-pitch-event, #btn-scrape-now, #btn-filter-flagship-badge");
  targets.forEach((btn) => {
    btn.addEventListener("mousemove", (e) => {
      const rect = btn.getBoundingClientRect();
      const x = (e.clientX - rect.left - rect.width / 2) * 0.22;
      const y = (e.clientY - rect.top - rect.height / 2) * 0.22;
      gsap.to(btn, { x: x, y: y, duration: 0.25, ease: "power2.out" });
    });
    btn.addEventListener("mouseleave", () => {
      gsap.to(btn, { x: 0, y: 0, duration: 0.55, ease: "elastic.out(1, 0.4)" });
    });
  });
}

// Hardware-Accelerated Ambient Cursor Lighting with rAF
function initSmoothMouseLighting() {
  let targetX = 50;
  let targetY = 20;
  let currentX = 50;
  let currentY = 20;
  let ticking = false;

  window.addEventListener("mousemove", (e) => {
    targetX = Math.round((e.clientX / window.innerWidth) * 100);
    targetY = Math.round((e.clientY / window.innerHeight) * 100);

    if (!ticking) {
      window.requestAnimationFrame(() => {
        currentX += (targetX - currentX) * 0.18;
        currentY += (targetY - currentY) * 0.18;
        document.documentElement.style.setProperty("--mouse-x", `${currentX.toFixed(1)}%`);
        document.documentElement.style.setProperty("--mouse-y", `${currentY.toFixed(1)}%`);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

// Live Cairo Time Clock (Africa/Cairo timezone)
function initLiveClock() {
  const el = document.getElementById("live-clock");
  if (!el) return;
  function tick() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString("en-US", { 
      timeZone: "Africa/Cairo", 
      hour: "2-digit", 
      minute: "2-digit", 
      second: "2-digit",
      hour12: true 
    });
    el.innerText = `Cairo: ${timeStr}`;
  }
  tick();
  setInterval(tick, 1000);
}

function setupEventListeners() {
  // Search typing with smooth debounce
  let searchTimeout = null;
  inputSearch.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.search = e.target.value.trim();
      fetchEvents();
    }, 200);
  });

  // Sorting
  selectSort.addEventListener("change", (e) => {
    state.sort = e.target.value;
    fetchEvents();
  });

  // City selection
  selectCity.addEventListener("change", (e) => {
    state.city = e.target.value;
    fetchEvents();
  });

  // Platform Source stream selection
  if (selectSource) {
    selectSource.addEventListener("change", (e) => {
      state.source = e.target.value;
      fetchEvents();
    });
  }

  // Category selection
  if (selectCategory) {
    selectCategory.addEventListener("change", (e) => {
      state.category = e.target.value;
      fetchEvents();
    });
  }

  // Quick filter for flagship summits
  const handleFlagshipFilter = () => {
    state.category = "Flagship Summits";
    if (selectCategory) selectCategory.value = "Flagship Summits";
    fetchEvents();
  };

  if (btnQuickFilterFlagship) {
    btnQuickFilterFlagship.addEventListener("click", handleFlagshipFilter);
  }

  const btnFilterFlagshipBadge = document.getElementById("btn-filter-flagship-badge");
  if (btnFilterFlagshipBadge) {
    btnFilterFlagshipBadge.addEventListener("click", (e) => {
      e.stopPropagation();
      handleFlagshipFilter();
    });
  }

  const tileTotalRadar = document.getElementById("tile-total-radar");
  if (tileTotalRadar) {
    tileTotalRadar.addEventListener("click", () => {
      state.category = "all";
      if (selectCategory) selectCategory.value = "all";
      fetchEvents();
    });
  }

  // Priority buttons
  document.querySelectorAll(".filter-priority-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-priority-btn").forEach((b) => {
        b.className = "filter-priority-btn px-3 py-1 rounded-xl font-medium bg-[#080D1D] text-slate-300 hover:bg-[#111A30] border border-white/[0.08]";
      });
      btn.className = "filter-priority-btn px-3 py-1 rounded-xl font-bold bg-[#037EF3] text-white shadow-[0_0_12px_rgba(3,126,243,0.35)]";
      state.priority = btn.dataset.priority;
      fetchEvents();
    });
  });

  // Quick filter for high leads from telemetry tile
  if (btnQuickFilterHigh) {
    btnQuickFilterHigh.addEventListener("click", () => {
      state.priority = "HIGH";
      document.querySelectorAll(".filter-priority-btn").forEach((b) => {
        if (b.dataset.priority === "HIGH") {
          b.className = "filter-priority-btn px-3 py-1 rounded-xl font-bold bg-[#037EF3] text-white shadow-[0_0_12px_rgba(3,126,243,0.35)]";
        } else {
          b.className = "filter-priority-btn px-3 py-1 rounded-xl font-medium bg-[#080D1D] text-slate-300 hover:bg-[#111A30] border border-white/[0.08]";
        }
      });
      fetchEvents();
    });
  }

  // Hero Bento Widget Controls
  const btnHeroLaunchPitch = document.getElementById("btn-hero-launch-pitch");
  if (btnHeroLaunchPitch) {
    btnHeroLaunchPitch.addEventListener("click", () => {
      const targetEvent = state.events.find(e => e.b2c_priority === "HIGH") || state.events[0];
      if (targetEvent) openPitchModal(targetEvent);
    });
  }

  const heroCalTechne = document.getElementById("hero-cal-techne");
  if (heroCalTechne) {
    heroCalTechne.addEventListener("click", () => {
      state.search = "Techne";
      inputSearch.value = "Techne";
      fetchEvents();
    });
  }

  const heroCalClash = document.getElementById("hero-cal-clash");
  if (heroCalClash) {
    heroCalClash.addEventListener("click", () => {
      checkClashesOnly.checked = !checkClashesOnly.checked;
      state.clashesOnly = checkClashesOnly.checked;
      fetchEvents();
    });
  }

  // Checkboxes
  checkPartnersOnly.addEventListener("change", (e) => {
    state.partnersOnly = e.target.checked;
    fetchEvents();
  });

  checkClashesOnly.addEventListener("change", (e) => {
    state.clashesOnly = e.target.checked;
    fetchEvents();
  });

  // Global Keyboard Shortcuts
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== inputSearch && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault();
      inputSearch.focus();
      inputSearch.select();
    }
    if (e.key === "Escape" && !pitchModal.classList.contains("hidden")) {
      closePitchModal();
    }
  });

  // View Switcher
  btnViewCards.addEventListener("click", () => switchView("cards"));
  btnViewCalendar.addEventListener("click", () => switchView("calendar"));

  // Modal Controls
  btnCloseModal.addEventListener("click", closePitchModal);
  pitchModal.addEventListener("click", (e) => {
    if (e.target === pitchModal) closePitchModal();
  });
  btnGeneratePitch.addEventListener("click", handleGeneratePitch);
  btnCopyPitch.addEventListener("click", handleCopyPitch);

  // Action Buttons
  btnSyncSheets.addEventListener("click", handleSyncSheets);
  btnSendEmail.addEventListener("click", handleSendEmail);
  btnScrapeNow.addEventListener("click", handleScrapeNow);
}

function switchView(view) {
  state.activeView = view;
  if (view === "cards") {
    containerCards.classList.remove("hidden");
    containerCalendar.classList.add("hidden");
    btnViewCards.className = "px-3 py-1 text-xs font-bold rounded-lg bg-[#037EF3] text-white shadow-sm flex items-center gap-1.5 transition active:scale-95";
    btnViewCalendar.className = "px-3 py-1 text-xs font-bold rounded-lg text-slate-400 hover:text-white flex items-center gap-1.5 transition active:scale-95";
  } else {
    containerCards.classList.add("hidden");
    containerCalendar.classList.remove("hidden");
    btnViewCalendar.className = "px-3 py-1 text-xs font-bold rounded-lg bg-[#037EF3] text-white shadow-sm flex items-center gap-1.5 transition active:scale-95";
    btnViewCards.className = "px-3 py-1 text-xs font-bold rounded-lg text-slate-400 hover:text-white flex items-center gap-1.5 transition active:scale-95";
    renderCalendarView();
  }
  if (window.lucide) lucide.createIcons();
}

// --- Fetch API ---
async function fetchEvents() {
  const params = new URLSearchParams({
    sort: state.sort,
    priority: state.priority,
    category: state.category,
    city: state.city,
    source: state.source,
    search: state.search,
    partner_only: state.partnersOnly,
    clash_only: state.clashesOnly
  });

  try {
    const res = await fetch(`/api/events?${params}`);
    const data = await res.json();
    state.events = data.events;

    // Animate KPI Telemetry HUD with GSAP counter interpolation
    const elTotal = document.getElementById("stat-total");
    animateCounter(elTotal, data.metrics.total_events);

    const elHigh = document.getElementById("stat-high");
    animateCounter(elHigh, data.metrics.high_priority);

    const elFlagship = document.getElementById("stat-flagship-count");
    animateCounter(elFlagship, data.metrics.flagship_count || 10);

    renderCards();
    if (state.activeView === "calendar") {
      renderCalendarView();
    }
  } catch (err) {
    console.error("Failed to fetch events:", err);
    showToast("Failed to connect to radar server", "error");
  }
}

// Helper: Extract month & day for tear-off badge
function parseDateForTearoff(dateDisplay) {
  if (!dateDisplay) return { month: "TBA", day: "--" };
  const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
  const upper = dateDisplay.toUpperCase();
  for (const m of months) {
    if (upper.includes(m)) {
      const match = upper.match(new RegExp(`${m}\\s*(\\d{1,2})`)) || upper.match(new RegExp(`(\\d{1,2})\\s*${m}`));
      const day = match ? match[1].padStart(2, "0") : "15";
      return { month: m, day: day };
    }
  }
  return { month: "DATE", day: "TBA" };
}

// Helper: Source pill class and icon
function getSourcePill(source) {
  const s = source.toLowerCase();
  if (s.includes("ticketsmarche")) {
    return `<span class="source-pill-ticketsmarche px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="ticket" class="w-3 h-3"></i> TicketsMarche</span>`;
  }
  if (s.includes("summit") || s.includes("techne") || s.includes("flagship")) {
    return `<span class="source-pill-summit px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="crown" class="w-3 h-3"></i> Flagship Summit</span>`;
  }
  if (s.includes("linkedin")) {
    return `<span class="source-pill-linkedin px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="briefcase" class="w-3 h-3"></i> LinkedIn</span>`;
  }
  if (s.includes("instagram")) {
    return `<span class="source-pill-instagram px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="camera" class="w-3 h-3"></i> Instagram</span>`;
  }
  if (s.includes("telegram")) {
    return `<span class="source-pill-telegram px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="send" class="w-3 h-3"></i> Telegram</span>`;
  }
  if (s.includes("facebook")) {
    return `<span class="source-pill-facebook px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="share-2" class="w-3 h-3"></i> Facebook</span>`;
  }
  if (s.includes("eventbrite")) {
    return `<span class="source-pill-eventbrite px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1">Eventbrite</span>`;
  }
  return `<span class="source-pill-default px-2 py-0.5 rounded-full text-[10px] font-medium">${source}</span>`;
}

// --- Render Cards View with GSAP Stagger Entrance ---
function renderCards() {
  containerCards.innerHTML = "";

  if (state.events.length === 0) {
    containerCards.innerHTML = `
      <div class="col-span-full radar-surface p-12 text-center">
        <i data-lucide="inbox" class="w-12 h-12 text-slate-500 mx-auto mb-3"></i>
        <h3 class="text-sm font-bold text-slate-200 font-display">No matching campus events found</h3>
        <p class="text-xs text-slate-400 mt-1">Try broadening your search term, switching city to 'All Egypt', or resetting filters.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  state.events.forEach((ev) => {
    const card = document.createElement("div");
    const isHigh = ev.b2c_priority === "HIGH";
    const isFlagship = (ev.category && ev.category.toLowerCase().includes("flagship")) || ev.source.toLowerCase().includes("summit") || ev.title.toLowerCase().includes("techne") || ev.title.toLowerCase().includes("riseup");
    const hasPartner = !!ev.parallel_org;
    const hasClash = ev.clash_warning;

    let glowClass = "";
    if (isFlagship) {
      glowClass = "card-summit-glow";
    } else if (isHigh) {
      glowClass = "card-high-glow";
    } else if (hasPartner) {
      glowClass = "card-partner-glow";
    }

    card.className = `radar-card p-5 flex flex-col justify-between ${glowClass}`;

    // Priority badge class
    const badgeClass = isHigh ? "badge-neon-coral" : (ev.b2c_priority === "MEDIUM" ? "badge-neon-amber" : "badge-neon-slate");
    const dateBadge = parseDateForTearoff(ev.date_display);
    const sourcePill = getSourcePill(ev.source);

    card.innerHTML = `
      <div class="space-y-3.5">
        <!-- Top Tags & Meta Stream Bar -->
        <div class="flex items-center justify-between gap-2 flex-wrap">
          <div class="flex items-center gap-1.5">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold ${badgeClass}">
              ★ ${ev.b2c_score.toFixed(1)} ${ev.b2c_priority}
            </span>
            ${sourcePill}
          </div>
          <div class="flex items-center gap-1.5 flex-wrap justify-end">
            ${isFlagship ? `<span class="badge-flagship-gold px-2.5 py-0.5 rounded-full text-[10px] inline-flex items-center gap-1">👑 Flagship</span>` : ""}
            ${hasPartner ? `<span class="badge-neon-purple px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide">${ev.parallel_org}</span>` : ""}
            ${hasClash ? `<span class="badge-neon-amber px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide">⚠️ Weekend Clash</span>` : ""}
          </div>
        </div>

        <!-- Title Block with Physical Tear-Off Date Badge -->
        <div class="flex items-start gap-3 pt-1">
          <div class="date-tearoff-badge shrink-0" title="${ev.date_display || 'Date TBA'}">
            <span class="date-tearoff-month">${dateBadge.month}</span>
            <span class="date-tearoff-day">${dateBadge.day}</span>
          </div>

          <div class="flex-1 min-w-0">
            <h3 class="font-extrabold text-base text-white leading-snug line-clamp-2 hover:text-[#00E5FF] transition group font-display">
              <a href="${ev.url}" target="_blank" class="group-hover:underline underline-offset-2">${ev.title}</a>
            </h3>
            <div class="mt-1.5 space-y-1 text-xs text-slate-400">
              <div class="flex items-center gap-1.5 truncate">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-rose-400 shrink-0"></i>
                <span class="truncate">${ev.location} • <strong class="text-slate-200 font-semibold">${ev.city}</strong></span>
              </div>
              <div class="flex items-center gap-1.5 text-slate-400 truncate">
                <i data-lucide="calendar" class="w-3.5 h-3.5 text-sky-400 shrink-0"></i>
                <span class="truncate">${ev.date_display || "Date TBA"}</span>
                ${ev.ticket_type ? `<span class="text-slate-600">•</span><span class="text-slate-300 font-medium">${ev.ticket_type}</span>` : ""}
              </div>
            </div>
          </div>
        </div>

        <!-- Specific Event Intelligence Briefing Box -->
        <div class="event-desc-box p-3 text-xs space-y-1">
          <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span class="flex items-center gap-1.5 text-sky-400">
              <i data-lucide="file-text" class="w-3.5 h-3.5"></i> Event Intelligence Briefing
            </span>
            <span class="text-[9px] text-slate-500 font-mono-code font-medium">Granular Details</span>
          </div>
          <p class="text-slate-300 text-[11px] leading-relaxed line-clamp-3 hover:line-clamp-none transition-all duration-300 cursor-pointer" title="Hover to view full briefing">
            ${ev.description || "No specific briefing available."}
          </p>
        </div>

        <!-- AIESEC Strategic Recommendation Callout Box -->
        <div class="dark-action-box p-3 text-xs">
          <div class="text-[10px] font-bold text-[#00E5FF] uppercase tracking-wider mb-1 flex items-center gap-1.5 font-display">
            <i data-lucide="zap" class="w-3.5 h-3.5 text-[#00E5FF]"></i> Recommended B2C Action
          </div>
          <div class="font-medium text-slate-200 leading-relaxed text-[11px]">
            ${ev.recommended_action}
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="pt-3 mt-3 border-t border-white/[0.07] flex items-center justify-between gap-2">
        <button class="btn-pitch-event flex-1 py-2 px-3 bg-gradient-to-r from-[#037EF3]/20 to-[#0266C8]/20 hover:from-[#037EF3] hover:to-[#0266C8] text-[#38BDF8] hover:text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 border border-[#38BDF8]/30 hover:border-transparent shadow-[0_0_12px_rgba(3,126,243,0.15)] active:scale-95"
                data-event-id="${ev.event_id}">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Outreach Pitch
        </button>
        <a href="${ev.url}" target="_blank" class="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/[0.08] border border-white/[0.09] transition active:scale-95" title="Open Event Link">
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    `;

    // Attach click for pitch button
    const pitchBtn = card.querySelector(".btn-pitch-event");
    pitchBtn.addEventListener("click", () => openPitchModal(ev));

    containerCards.appendChild(card);
  });

  // Trigger GSAP Stagger Entrance for Cards
  if (typeof gsap !== "undefined") {
    gsap.from("#container-cards > .radar-card", {
      opacity: 0,
      y: 20,
      stagger: 0.035,
      duration: 0.45,
      ease: "power2.out",
      clearProps: "all"
    });
  }

  initMagneticButtons();

  if (window.lucide) lucide.createIcons();
}

// --- Render Calendar & Conflict Radar ---
function renderCalendarView() {
  calendarTimeline.innerHTML = "";

  // Group events by Month/Date
  const groups = {};
  state.events.forEach((ev) => {
    const key = ev.date_display ? ev.date_display.split("·")[0].trim() : "Date TBA";
    if (!groups[key]) groups[key] = [];
    groups[key].push(ev);
  });

  Object.entries(groups).slice(0, 15).forEach(([dateStr, eventList]) => {
    const isClashDate = eventList.length > 1;
    const groupBlock = document.createElement("div");
    groupBlock.className = `p-4 rounded-2xl border ${isClashDate ? "bg-amber-950/20 border-amber-500/35 shadow-[0_0_20px_rgba(245,158,11,0.12)]" : "bg-[#0A1020]/80 border-white/[0.08]"}`;

    let eventsHtml = eventList.map(e => `
      <div class="py-2.5 flex items-center justify-between border-b border-white/[0.06] last:border-0 gap-4">
        <div>
          <div class="font-bold text-xs text-white flex items-center gap-2 font-display">
            <span>${e.title}</span>
            <span class="text-[10px] ${e.b2c_priority === 'HIGH' ? 'badge-neon-coral' : 'badge-neon-blue'} px-2 py-0.5 rounded-full font-bold">★ ${e.b2c_score.toFixed(1)}</span>
            <span class="text-[10px] bg-white/[0.06] text-slate-400 px-2 py-0.5 rounded-md font-medium">${e.source}</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">${e.location} (<span class="text-slate-200 font-medium">${e.city}</span>) • <span class="text-[#00E5FF]">${e.recommended_action}</span></div>
        </div>
        <button class="text-xs bg-sky-500/15 hover:bg-sky-500 text-sky-300 hover:text-white border border-sky-500/30 px-3 py-1.5 rounded-xl font-bold shrink-0 transition active:scale-95" onclick="openPitchById('${e.event_id}')">
          Pitch
        </button>
      </div>
    `).join("");

    groupBlock.innerHTML = `
      <div class="flex items-center justify-between mb-2 pb-2 border-b border-white/[0.06]">
        <h4 class="text-xs font-bold text-slate-200 flex items-center gap-2 font-display">
          <i data-lucide="calendar" class="w-4 h-4 text-[#00E5FF]"></i>
          <span>${dateStr}</span>
        </h4>
        ${isClashDate ? `<span class="badge-neon-amber text-[10px] font-bold px-2.5 py-0.5 rounded-full">⚠️ Clash: ${eventList.length} Events Competing</span>` : ""}
      </div>
      <div class="divide-y divide-white/[0.06]">
        ${eventsHtml}
      </div>
    `;

    calendarTimeline.appendChild(groupBlock);
  });

  if (window.lucide) lucide.createIcons();
}

// Helper to open pitch from calendar
window.openPitchById = function(eventId) {
  const ev = state.events.find(e => e.event_id === eventId);
  if (ev) openPitchModal(ev);
};

// --- Modal Logic with GSAP Scale Physics ---
function openPitchModal(event) {
  state.activePitchEvent = event;
  pitchEventSubtitle.innerText = `Target Event: ${event.title} (${event.city})`;
  const briefingEl = document.getElementById("pitch-event-desc-text");
  if (briefingEl) {
    briefingEl.innerText = event.description || "No specific briefing available for this event.";
  }
  pitchOutputBox.classList.add("hidden");
  pitchModal.classList.remove("hidden");

  // GSAP Spring Pop Modal Entrance
  if (typeof gsap !== "undefined") {
    const dialog = pitchModal.querySelector(".modal-dialog-dark");
    if (dialog) {
      gsap.fromTo(dialog, 
        { scale: 0.92, opacity: 0, y: 15 },
        { scale: 1, opacity: 1, y: 0, duration: 0.35, ease: "back.out(1.4)" }
      );
    }
  }

  if (window.lucide) lucide.createIcons();
}

function closePitchModal() {
  if (typeof gsap !== "undefined") {
    const dialog = pitchModal.querySelector(".modal-dialog-dark");
    if (dialog) {
      gsap.to(dialog, {
        scale: 0.94,
        opacity: 0,
        duration: 0.2,
        ease: "power2.in",
        onComplete: () => {
          pitchModal.classList.add("hidden");
          state.activePitchEvent = null;
        }
      });
      return;
    }
  }
  pitchModal.classList.add("hidden");
  state.activePitchEvent = null;
}

async function handleGeneratePitch() {
  if (!state.activePitchEvent) return;

  const memberName = document.getElementById("pitch-name").value.trim() || "Abdelrahman Motazz";
  const memberEmail = document.getElementById("pitch-email").value.trim() || "abdelrahman.motazz@aiesec.net";
  const memberPhone = document.getElementById("pitch-phone").value.trim() || "+20 10 1234 5678";
  const purpose = document.getElementById("pitch-purpose").value;

  btnGeneratePitch.disabled = true;
  btnGeneratePitch.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating Proposal...`;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await fetch("/api/pitch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        event_id: state.activePitchEvent.event_id,
        member_name: memberName,
        member_email: memberEmail,
        member_phone: memberPhone,
        purpose: purpose
      })
    });

    const data = await res.json();
    pitchSubject.value = data.subject;
    pitchBody.value = data.body;

    // Mailto client link
    const mailto = `mailto:?subject=${encodeURIComponent(data.subject)}&body=${encodeURIComponent(data.body)}`;
    btnOpenMail.href = mailto;

    pitchOutputBox.classList.remove("hidden");

    if (typeof gsap !== "undefined") {
      gsap.from(pitchOutputBox, { opacity: 0, y: 12, duration: 0.35, ease: "power2.out" });
    }

    showToast("Partnership proposal generated successfully!", "success");
  } catch (err) {
    console.error("Failed to generate pitch:", err);
    showToast("Failed to generate pitch proposal", "error");
  } finally {
    btnGeneratePitch.disabled = false;
    btnGeneratePitch.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4 text-cyan-200"></i> Generate Outreach Proposal`;
    if (window.lucide) lucide.createIcons();
  }
}

function handleCopyPitch() {
  const fullText = `Subject: ${pitchSubject.value}\n\n${pitchBody.value}`;
  navigator.clipboard.writeText(fullText).then(() => {
    const copyText = document.getElementById("copy-text");
    copyText.innerText = "Copied to Clipboard!";
    showToast("Copied to clipboard!", "success");
    setTimeout(() => {
      copyText.innerText = "Copy to Clipboard";
    }, 2500);
  });
}

// --- Action Button Handlers ---
async function handleSyncSheets() {
  btnSyncSheets.disabled = true;
  showToast("Syncing records to Google Sheets...", "info");
  try {
    const res = await fetch("/api/sync-sheets", { method: "POST" });
    const data = await res.json();
    if (data.status === "synced") {
      showToast(`Synced ${data.rows_synced} events to Sheets!`, "success");
    } else {
      showToast("Sheets sync skipped (Credentials not configured)", "info");
    }
  } catch (err) {
    showToast("Error syncing to Sheets", "error");
  } finally {
    btnSyncSheets.disabled = false;
  }
}

async function handleSendEmail() {
  btnSendEmail.disabled = true;
  showToast("Sending B2C email digest...", "info");
  try {
    const res = await fetch("/api/send-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (data.status === "sent") {
      showToast(`Digest sent to ${data.recipients.length} recipients!`, "success");
    } else {
      showToast(data.message || "Email digest processed", "info");
    }
  } catch (err) {
    showToast("Error sending email", "error");
  } finally {
    btnSendEmail.disabled = false;
  }
}

async function handleScrapeNow() {
  btnScrapeNow.disabled = true;
  scrapeIcon.classList.add("animate-spin");
  showToast("Triggering full multi-platform scrape across Egypt...", "info");

  try {
    const res = await fetch("/api/scrape-now", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city: state.city })
    });
    const data = await res.json();
    showToast(`Scrape complete! Discovered ${data.events_count} events.`, "success");
    await fetchEvents();
  } catch (err) {
    showToast("Error triggering scrape", "error");
  } finally {
    btnScrapeNow.disabled = false;
    scrapeIcon.classList.remove("animate-spin");
  }
}

// --- Toast Feedback with Smooth Physics ---
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toast-message");
  const icon = document.getElementById("toast-icon");

  msg.innerText = message;
  toast.classList.remove("translate-y-20", "opacity-0", "pointer-events-none");

  if (typeof gsap !== "undefined") {
    gsap.fromTo(toast,
      { y: 30, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.35, ease: "back.out(1.4)" }
    );
  }

  setTimeout(() => {
    if (typeof gsap !== "undefined") {
      gsap.to(toast, {
        y: 20,
        opacity: 0,
        duration: 0.25,
        ease: "power2.in",
        onComplete: () => {
          toast.classList.add("translate-y-20", "opacity-0", "pointer-events-none");
        }
      });
    } else {
      toast.classList.add("translate-y-20", "opacity-0", "pointer-events-none");
    }
  }, 3500);
}
