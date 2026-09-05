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

/** @type {{ events: EventRecord[], sort: string, priority: string, category: string, city: string, source: string, search: string, partnersOnly: boolean, clashesOnly: boolean, activePitchEvent: EventRecord|null, activeDrawerEvent: EventRecord|null, activeTopic: string, currentTheme: string, activeView: 'cards'|'calendar' }} */
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
  activeDrawerEvent: null,
  activeTopic: "all",
  currentTheme: "blue",
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
  initThemeAccent();
  initTopicChips();
  initEventDrawer();
  initThreeRadar();
  initSmoothMouseLighting();
  initLiveClock();
  setupEventListeners();
  fetchEvents();
  if (window.lucide) lucide.createIcons();
});

// ============================================================
// THREE.JS 3D HOLOGRAPHIC PARTICLE RADAR GLOBE (Interactive Spatial Navigator)
// ============================================================
let globeController = {
  focusCity: null
};

function initThreeRadar() {
  const canvas = document.getElementById("hero-globe-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  try {
    const container = canvas.parentElement;
    const tooltip = document.getElementById("globe-tooltip");
    const statusPill = document.getElementById("globe-status-pill");
    const cityButtons = document.querySelectorAll(".globe-hub-btn");

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

    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

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
    globeGroup.add(wireframeGlobe);

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
    const basePositions = new Float32Array(positions);

    const partMat = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.88,
      blending: THREE.AdditiveBlending
    });
    const particleMesh = new THREE.Points(partGeo, partMat);
    globeGroup.add(particleMesh);

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
    globeGroup.add(ringGroup);

    // 4. Egypt Hub Beacon Pins on the Globe (Clickable Interactive Targets)
    const interactivePins = [];
    const hubs = [
      { name: "Cairo", cityKey: "cairo", lat: 30.0444, lon: 31.2357, color: 0x00e5ff },
      { name: "Alexandria", cityKey: "alexandria", lat: 31.2001, lon: 29.9187, color: 0x38bdf8 },
      { name: "Tanta", cityKey: "tanta", lat: 30.7865, lon: 31.0004, color: 0x037ef3, primary: true },
      { name: "Giza", cityKey: "giza", lat: 30.0131, lon: 31.2089, color: 0xff4d36 },
      { name: "Mansoura", cityKey: "mansoura", lat: 31.0409, lon: 31.3785, color: 0xa855f7 },
      { name: "Assiut", cityKey: "assiut", lat: 27.1801, lon: 31.1837, color: 0xf59e0b }
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
      const pos = latLonToVector3(hub.lat, hub.lon, globeRadius + 1.2);
      
      // Pin Sphere
      const pinGeo = new THREE.SphereGeometry(hub.primary ? 4.2 : 3.0, 16, 16);
      const pinMat = new THREE.MeshBasicMaterial({
        color: hub.color,
        blending: THREE.AdditiveBlending
      });
      const pin = new THREE.Mesh(pinGeo, pinMat);
      pin.position.copy(pos);

      // Beacon Ripple Ring
      const bRingGeo = new THREE.RingGeometry(2.5, 4.2, 24);
      const bRingMat = new THREE.MeshBasicMaterial({
        color: hub.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });
      const bRing = new THREE.Mesh(bRingGeo, bRingMat);
      bRing.position.copy(pos);
      bRing.lookAt(0, 0, 0);

      // Store Metadata for Raycasting
      pin.userData = { hub, beaconRing: bRing };
      interactivePins.push(pin);

      globeGroup.add(pin);
      globeGroup.add(bRing);
    });

    // 5. Raycasting Engine (Hover Intel & Click to Filter)
    const raycaster = new THREE.Raycaster();
    const mouseNorm = new THREE.Vector2();
    let hoveredPin = null;

    // Filter Radar by City Helper
    function filterByCity(cityKey, cityName) {
      if (selectCity) selectCity.value = cityKey;
      state.city = cityKey;
      fetchEvents();

      // Highlight active button in hub chips
      cityButtons.forEach(btn => {
        if (btn.dataset.city === cityKey) {
          btn.className = "globe-hub-btn px-2 py-0.5 rounded-md bg-[#037EF3] text-white font-bold transition active:scale-95 shrink-0 shadow-sm";
        } else {
          btn.className = "globe-hub-btn px-2 py-0.5 rounded-md bg-white/[0.07] hover:bg-sky-500/20 text-slate-200 hover:text-sky-300 font-medium transition active:scale-95 shrink-0";
        }
      });

      // Update status indicator
      if (statusPill) {
        statusPill.innerText = cityKey === "all" ? "6 Active Hubs" : `Selected: ${cityName}`;
      }

      showToast(`Radar focused on ${cityName} opportunities!`, "info");
    }

    // Function to rotate globe directly to a city
    function rotateToCity(cityKey) {
      if (cityKey === "all") {
        if (typeof gsap !== "undefined") {
          gsap.to(globeGroup.rotation, { x: 0.2, y: 0, duration: 1.2, ease: "power2.out" });
        } else {
          globeGroup.rotation.set(0.2, 0, 0);
        }
        return;
      }

      const targetHub = hubs.find(h => h.cityKey === cityKey);
      if (!targetHub) return;

      const phi = (90 - targetHub.lat) * (Math.PI / 180);
      const theta = (targetHub.lon + 180) * (Math.PI / 180);

      const targetY = -theta + Math.PI / 2;
      const targetX = phi - Math.PI / 2;

      if (typeof gsap !== "undefined") {
        gsap.to(globeGroup.rotation, {
          y: targetY,
          x: targetX,
          duration: 1.3,
          ease: "power2.out"
        });
      } else {
        globeGroup.rotation.set(targetX, targetY, 0);
      }
    }

    // Expose controller for external city selection synchronization & dynamic theme adaptation
    globeController.focusCity = rotateToCity;
    globeController.updateThemeColor = (hexColor) => {
      if (wireframeMat) wireframeMat.color.setHex(hexColor);
    };

    // Connect Hub Button Clicks
    cityButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const cKey = btn.dataset.city;
        const matchingHub = hubs.find(h => h.cityKey === cKey);
        const cName = matchingHub ? matchingHub.name : "All Egypt";
        rotateToCity(cKey);
        filterByCity(cKey, cName);
      });
    });

    // Mouse Tracking Parallax & Hover Raycasting
    let targetRotX = 0.2;
    let targetRotY = 0;

    container.addEventListener("mousemove", (e) => {
      const rect = container.getBoundingClientRect();
      const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const ny = -(((e.clientY - rect.top) / rect.height) * 2 - 1);

      mouseNorm.set(nx, ny);
      targetRotY = nx * 0.6;
      targetRotX = 0.2 + ny * 0.3;

      // Raycast against pins
      raycaster.setFromCamera(mouseNorm, camera);
      const hits = raycaster.intersectObjects(interactivePins, false);

      if (hits.length > 0) {
        const pin = hits[0].object;
        const hub = pin.userData.hub;

        if (hoveredPin !== pin) {
          if (hoveredPin) hoveredPin.scale.set(1, 1, 1);
          hoveredPin = pin;
          pin.scale.set(1.45, 1.45, 1.45);
        }

        canvas.style.cursor = "pointer";

        // Calculate dynamic stats
        const cityEvents = state.events.filter(ev => ev.city.toLowerCase().includes(hub.cityKey.toLowerCase()));
        const flagshipEvents = cityEvents.filter(ev => (ev.category && ev.category.toLowerCase().includes("flagship")) || ev.title.toLowerCase().includes("techne") || ev.title.toLowerCase().includes("riseup"));

        // Position & populate tooltip
        if (tooltip) {
          const tooltipCity = document.getElementById("globe-tooltip-city");
          const tooltipCount = document.getElementById("globe-tooltip-count");
          const tooltipFlagships = document.getElementById("globe-tooltip-flagships");

          if (tooltipCity) tooltipCity.innerText = `📍 ${hub.name}`;
          if (tooltipCount) tooltipCount.innerText = `${cityEvents.length} Events`;
          if (tooltipFlagships) {
            tooltipFlagships.innerText = flagshipEvents.length > 0 
              ? `👑 ${flagshipEvents.length} Flagship (${flagshipEvents[0].title.split(" 202")[0]})` 
              : "Campus Lead Pipeline";
          }

          const worldPos = new THREE.Vector3();
          pin.getWorldPosition(worldPos);
          worldPos.project(camera);

          const screenX = (worldPos.x * 0.5 + 0.5) * rect.width;
          const screenY = (-(worldPos.y * 0.5) + 0.5) * rect.height;

          tooltip.style.left = `${screenX}px`;
          tooltip.style.top = `${screenY - 12}px`;
          tooltip.classList.remove("opacity-0");
        }
      } else {
        if (hoveredPin) {
          hoveredPin.scale.set(1, 1, 1);
          hoveredPin = null;
        }
        canvas.style.cursor = isDragging ? "grabbing" : "grab";
        if (tooltip) tooltip.classList.add("opacity-0");
      }
    }, { passive: true });

    // Drag and Touch Orbit Controls (Desktop Mouse & Mobile Touchscreen)
    let isDragging = false;
    let dragMoved = false;
    let prevPos = { x: 0, y: 0 };

    container.addEventListener("mousedown", (e) => {
      isDragging = true;
      dragMoved = false;
      prevPos = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevPos.x;
      const deltaY = e.clientY - prevPos.y;
      if (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3) dragMoved = true;

      globeGroup.rotation.y += deltaX * 0.01;
      globeGroup.rotation.x += deltaY * 0.01;

      prevPos = { x: e.clientX, y: e.clientY };
    });

    // Touch Support for Mobile Viewports
    container.addEventListener("touchstart", (e) => {
      if (e.touches && e.touches.length === 1) {
        isDragging = true;
        dragMoved = false;
        prevPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      }
    }, { passive: true });

    window.addEventListener("touchend", () => {
      isDragging = false;
    });

    container.addEventListener("touchmove", (e) => {
      if (!isDragging || !e.touches || e.touches.length !== 1) return;
      const deltaX = e.touches[0].clientX - prevPos.x;
      const deltaY = e.touches[0].clientY - prevPos.y;
      if (Math.abs(deltaX) > 3 || Math.abs(deltaY) > 3) dragMoved = true;

      globeGroup.rotation.y += deltaX * 0.012;
      globeGroup.rotation.x += deltaY * 0.012;

      prevPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }, { passive: true });

    // Click on Canvas Pin Trigger
    container.addEventListener("click", () => {
      if (dragMoved) return; // Ignore drag end click
      raycaster.setFromCamera(mouseNorm, camera);
      const hits = raycaster.intersectObjects(interactivePins, false);

      if (hits.length > 0) {
        const pin = hits[0].object;
        const hub = pin.userData.hub;
        const bRing = pin.userData.beaconRing;

        // Animate beacon ring ripple
        if (typeof gsap !== "undefined" && bRing) {
          gsap.fromTo(bRing.scale, 
            { x: 1, y: 1 }, 
            { x: 3.2, y: 3.2, duration: 0.65, ease: "power2.out", onComplete: () => bRing.scale.set(1, 1, 1) }
          );
        }

        rotateToCity(hub.cityKey);
        filterByCity(hub.cityKey, hub.name);
      }
    });

    // Render Animation Loop with 3D Holographic Particle Wave Flow
    let waveClock = 0;
    function animate() {
      requestAnimationFrame(animate);
      waveClock += 0.022;

      // Subtle dynamic 3D undulating wave oscillation across particles
      if (partGeo && partGeo.attributes && partGeo.attributes.position) {
        const posArr = partGeo.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {
          const i3 = i * 3;
          const bx = basePositions[i3];
          const by = basePositions[i3 + 1];
          const bz = basePositions[i3 + 2];
          const wave = 1.0 + 0.038 * Math.sin(waveClock * 2.2 + (by * 0.09) + (bx * 0.07));
          posArr[i3] = bx * wave;
          posArr[i3 + 1] = by * wave;
          posArr[i3 + 2] = bz * wave;
        }
        partGeo.attributes.position.needsUpdate = true;
      }

      if (!isDragging) {
        wireframeGlobe.rotation.y += 0.002;
        particleMesh.rotation.y += 0.002;

        ringGroup.rotation.z += 0.0035;
        ringGroup.rotation.y += 0.0018;

        globeGroup.rotation.y += (targetRotY - globeGroup.rotation.y) * 0.035;
        globeGroup.rotation.x += (targetRotX - globeGroup.rotation.x) * 0.035;
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

// Hardware-Accelerated Ambient Cursor Lighting & Linear-Style Card Spotlight with rAF
function initSmoothMouseLighting() {
  let targetX = 50;
  let targetY = 20;
  let currentX = 50;
  let currentY = 20;
  let mouseClientX = -999;
  let mouseClientY = -999;
  let ticking = false;

  window.addEventListener("mousemove", (e) => {
    mouseClientX = e.clientX;
    mouseClientY = e.clientY;
    targetX = Math.round((e.clientX / window.innerWidth) * 100);
    targetY = Math.round((e.clientY / window.innerHeight) * 100);

    if (!ticking) {
      window.requestAnimationFrame(() => {
        currentX += (targetX - currentX) * 0.18;
        currentY += (targetY - currentY) * 0.18;
        document.documentElement.style.setProperty("--mouse-x", `${currentX.toFixed(1)}%`);
        document.documentElement.style.setProperty("--mouse-y", `${currentY.toFixed(1)}%`);

        // Update spotlight cards in viewport proximity
        const spotlightCards = document.querySelectorAll(".spotlight-card");
        spotlightCards.forEach((card) => {
          const rect = card.getBoundingClientRect();
          const cx = mouseClientX - rect.left;
          const cy = mouseClientY - rect.top;
          if (cx >= -60 && cx <= rect.width + 60 && cy >= -60 && cy <= rect.height + 60) {
            card.style.setProperty("--card-mouse-x", `${cx}px`);
            card.style.setProperty("--card-mouse-y", `${cy}px`);
          }
        });

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
  // Command Palette & Global Keyboard Shortcuts
  document.addEventListener("keydown", (e) => {
    // Ctrl+K / Cmd+K toggle palette
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      toggleCommandPalette();
      return;
    }

    const cmdModal = document.getElementById("command-palette-modal");
    if (cmdModal && !cmdModal.classList.contains("hidden")) {
      if (e.key === "Escape") {
        e.preventDefault();
        closeCommandPalette();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        if (cmdItems.length > 0) {
          cmdActiveIndex = (cmdActiveIndex + 1) % cmdItems.length;
          updateCommandPaletteActiveItem();
        }
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (cmdItems.length > 0) {
          cmdActiveIndex = (cmdActiveIndex - 1 + cmdItems.length) % cmdItems.length;
          updateCommandPaletteActiveItem();
        }
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (cmdItems[cmdActiveIndex]) {
          cmdItems[cmdActiveIndex].run();
          closeCommandPalette();
        }
      }
      return;
    }

    if (e.key === "/" && document.activeElement !== inputSearch && document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault();
      inputSearch.focus();
      inputSearch.select();
    }
    if (e.key === "Escape") {
      if (!pitchModal.classList.contains("hidden")) {
        closePitchModal();
      }
      closeEventDrawer();
    }
  });

  // Command Palette DOM triggers
  const btnOpenCmd = document.getElementById("btn-open-cmd-palette");
  const cmdModal = document.getElementById("command-palette-modal");
  const cmdInput = document.getElementById("command-palette-input");
  if (btnOpenCmd) btnOpenCmd.addEventListener("click", openCommandPalette);
  if (cmdInput) cmdInput.addEventListener("input", (e) => renderCommandPaletteResults(e.target.value));
  if (cmdModal) {
    cmdModal.addEventListener("click", (e) => {
      if (e.target === cmdModal) closeCommandPalette();
    });
  }

  // Mobile Bottom Bar Triggers
  const mobileBtnCmd = document.getElementById("mobile-btn-cmd");
  const mobileBtnFlagships = document.getElementById("mobile-btn-flagships");
  const mobileBtnTanta = document.getElementById("mobile-btn-tanta");
  const mobileBtnView = document.getElementById("mobile-btn-view");
  const mobileBtnTop = document.getElementById("mobile-btn-top");

  if (mobileBtnCmd) mobileBtnCmd.addEventListener("click", openCommandPalette);
  if (mobileBtnFlagships) mobileBtnFlagships.addEventListener("click", () => {
    selectCategory.value = "Flagship Summits";
    selectCategory.dispatchEvent(new Event("change"));
    showToast("Filtered by Flagships", "info");
  });
  if (mobileBtnTanta) mobileBtnTanta.addEventListener("click", () => {
    selectCity.value = "tanta";
    selectCity.dispatchEvent(new Event("change"));
    if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
      globeController.focusCity("tanta");
    }
    showToast("Focused Tanta Hub", "info");
  });
  if (mobileBtnView) mobileBtnView.addEventListener("click", () => {
    if (state.activeView === "cards") {
      switchView("calendar");
      showToast("Switched to Calendar", "info");
    } else {
      switchView("cards");
      showToast("Switched to Cards", "info");
    }
  });
  if (mobileBtnTop) mobileBtnTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
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

// ============================================================
// THEME ACCENT CONTROLLER
// ============================================================
const THEME_ACCENTS = {
  blue: { hex: 0x037ef3, css: "#037EF3" },
  gold: { hex: 0xf59e0b, css: "#F59E0B" },
  cyan: { hex: 0x00e5ff, css: "#00E5FF" },
  coral: { hex: 0xff4d36, css: "#FF4D36" },
  emerald: { hex: 0x10b981, css: "#10B981" }
};

function setTheme(themeName) {
  if (!THEME_ACCENTS[themeName]) themeName = "blue";
  state.currentTheme = themeName;
  if (themeName === "blue") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.setAttribute("data-theme", themeName);
  }
  try {
    localStorage.setItem("aiesec_theme", themeName);
  } catch (e) {
    console.warn("Could not save theme to localStorage:", e);
  }

  const indicator = document.getElementById("theme-accent-indicator");
  if (indicator) {
    indicator.style.backgroundColor = THEME_ACCENTS[themeName].css;
    indicator.style.boxShadow = `0 0 8px ${THEME_ACCENTS[themeName].css}`;
  }

  if (typeof globeController !== "undefined" && typeof globeController.updateThemeColor === "function") {
    globeController.updateThemeColor(THEME_ACCENTS[themeName].hex);
  }
}

function initThemeAccent() {
  let saved = "blue";
  try {
    saved = localStorage.getItem("aiesec_theme") || "blue";
  } catch (e) {
    saved = "blue";
  }
  setTheme(saved);

  const btnTheme = document.getElementById("btn-theme-accent");
  const menuTheme = document.getElementById("menu-theme-accent");
  if (btnTheme && menuTheme) {
    btnTheme.addEventListener("click", (e) => {
      e.stopPropagation();
      menuTheme.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!btnTheme.contains(e.target) && !menuTheme.contains(e.target)) {
        menuTheme.classList.add("hidden");
      }
    });

    document.querySelectorAll(".theme-accent-item").forEach((item) => {
      item.addEventListener("click", () => {
        const t = item.dataset.theme;
        setTheme(t);
        menuTheme.classList.add("hidden");
        showToast(`Theme accent updated: ${item.innerText.trim()}`, "info");
      });
    });
  }
}

// ============================================================
// TOPIC CHIPS HORIZONTAL CAROUSEL CONTROLLER
// ============================================================
function initTopicChips() {
  const chips = document.querySelectorAll(".topic-chip");
  if (!chips || chips.length === 0) return;

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");

      const topic = chip.dataset.topic;
      state.activeTopic = topic;

      if (topic === "all") {
        state.category = "all";
        state.priority = "all";
        state.city = "all";
        if (selectCategory) selectCategory.value = "all";
        if (selectCity) selectCity.value = "all";
      } else if (topic === "flagship") {
        state.category = "Flagship Summits";
        state.city = "all";
        if (selectCategory) selectCategory.value = "Flagship Summits";
      } else if (topic === "tech") {
        state.category = "Tech & Innovation";
        state.city = "all";
        if (selectCategory) selectCategory.value = "Tech & Innovation";
      } else if (topic === "career") {
        state.category = "Career & Employment";
        state.city = "all";
        if (selectCategory) selectCategory.value = "Career & Employment";
      } else if (topic === "leadership") {
        state.category = "Youth Leadership";
        state.city = "all";
        if (selectCategory) selectCategory.value = "Youth Leadership";
      } else if (topic === "competition") {
        state.category = "Startup Competition";
        state.city = "all";
        if (selectCategory) selectCategory.value = "Startup Competition";
      } else if (topic === "tanta") {
        state.city = "tanta";
        if (selectCity) selectCity.value = "tanta";
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("tanta");
        }
      } else if (topic === "alex") {
        state.city = "alexandria";
        if (selectCity) selectCity.value = "alexandria";
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("alexandria");
        }
      }

      fetchEvents();
      showToast(`Filter applied: ${chip.innerText.trim()}`, "info");
    });
  });
}

// ============================================================
// LINEAR-STYLE SLIDE-OVER EVENT INTEL DRAWER
// ============================================================
function openEventDrawer(ev) {
  if (!ev) return;
  state.activeDrawerEvent = ev;

  const drawer = document.getElementById("event-detail-drawer");
  const badgeEl = document.getElementById("drawer-badge");
  const titleEl = document.getElementById("drawer-title");
  const cityEl = document.getElementById("drawer-city");
  const dateEl = document.getElementById("drawer-date");
  const scoreEl = document.getElementById("drawer-score");
  const priorityEl = document.getElementById("drawer-priority");
  const sourceEl = document.getElementById("drawer-source");
  const descEl = document.getElementById("drawer-description");
  const actionEl = document.getElementById("drawer-action");
  const linkEl = document.getElementById("drawer-event-link");
  const outputEl = document.getElementById("drawer-pitch-output");

  if (badgeEl) badgeEl.innerText = ev.category || "Youth Summit";
  if (titleEl) titleEl.innerText = ev.title;
  if (cityEl) cityEl.innerHTML = `<i data-lucide="map-pin" class="w-3.5 h-3.5"></i> ${ev.city || "Egypt"}`;
  if (dateEl) dateEl.innerText = ev.date_display || "Upcoming";
  if (scoreEl) scoreEl.innerText = ev.b2c_score ? ev.b2c_score.toFixed(1) : "8.0";
  if (priorityEl) {
    priorityEl.innerText = ev.b2c_priority || "HIGH";
    priorityEl.className = ev.b2c_priority === "HIGH" ? "text-xl font-black text-[#FF4D36] font-display" : "text-xl font-black text-sky-400 font-display";
  }
  if (sourceEl) sourceEl.innerText = ev.source || "Flagship Radar";
  if (descEl) descEl.innerText = ev.description || "Intelligence briefing pending verification.";
  if (actionEl) actionEl.innerText = ev.recommended_action || "Deploy student activation booth & PR outreach.";
  if (linkEl) linkEl.href = ev.url || "#";
  if (outputEl) outputEl.classList.add("hidden");

  if (drawer) {
    drawer.classList.add("active");
  }
  if (window.lucide) lucide.createIcons();
}

function closeEventDrawer() {
  const drawer = document.getElementById("event-detail-drawer");
  if (drawer) drawer.classList.remove("active");
  state.activeDrawerEvent = null;
}

window.openEventDrawerById = function(eventId) {
  const ev = state.events.find((e) => e.event_id === eventId);
  if (ev) openEventDrawer(ev);
};

async function handleGenerateDrawerPitch() {
  if (!state.activeDrawerEvent) return;

  const btnGen = document.getElementById("drawer-btn-generate");
  const name = document.getElementById("drawer-pitch-name").value.trim() || "Abdelrahman Motazz";
  const email = document.getElementById("drawer-pitch-email").value.trim() || "abdelrahman.motazz@aiesec.net";
  const purpose = document.getElementById("drawer-pitch-purpose").value;

  btnGen.disabled = true;
  btnGen.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating Proposal...`;
  if (window.lucide) lucide.createIcons();

  try {
    let data;
    try {
      const res = await fetch("/api/pitch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event_id: state.activeDrawerEvent.event_id,
          member_name: name,
          member_email: email,
          member_phone: "+20 10 1234 5678",
          purpose: purpose
        })
      });
      if (!res.ok) throw new Error("API not available");
      data = await res.json();
    } catch (apiErr) {
      data = generateClientPitch(state.activeDrawerEvent, name, email, "+20 10 1234 5678", purpose);
    }

    const subInput = document.getElementById("drawer-pitch-subject");
    const bodyInput = document.getElementById("drawer-pitch-body");
    const outputBox = document.getElementById("drawer-pitch-output");
    const mailBtn = document.getElementById("drawer-btn-mail");

    if (subInput) subInput.value = data.subject;
    if (bodyInput) bodyInput.value = data.body;
    if (mailBtn) mailBtn.href = `mailto:?subject=${encodeURIComponent(data.subject)}&body=${encodeURIComponent(data.body)}`;
    if (outputBox) {
      outputBox.classList.remove("hidden");
      if (typeof gsap !== "undefined") {
        gsap.from(outputBox, { opacity: 0, y: 10, duration: 0.3, ease: "power2.out" });
      }
    }
    showToast("Outreach proposal ready!", "success");
  } catch (err) {
    showToast("Failed to generate proposal", "error");
  } finally {
    btnGen.disabled = false;
    btnGen.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4 text-cyan-200"></i> Generate Partnership Pitch`;
    if (window.lucide) lucide.createIcons();
  }
}

function handleCopyDrawerPitch() {
  const subInput = document.getElementById("drawer-pitch-subject");
  const bodyInput = document.getElementById("drawer-pitch-body");
  const copyBtn = document.getElementById("drawer-btn-copy");
  if (!subInput || !bodyInput) return;

  const fullText = `Subject: ${subInput.value}\n\n${bodyInput.value}`;
  navigator.clipboard.writeText(fullText).then(() => {
    if (copyBtn) copyBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> <span>Copied!</span>`;
    showToast("Drawer pitch copied to clipboard!", "success");
    setTimeout(() => {
      if (copyBtn) copyBtn.innerHTML = `<i data-lucide="copy" class="w-3.5 h-3.5"></i> <span>Copy Pitch</span>`;
      if (window.lucide) lucide.createIcons();
    }, 2500);
  });
}

function initEventDrawer() {
  const btnClose = document.getElementById("btn-close-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const btnDone = document.getElementById("drawer-btn-done");
  const btnGen = document.getElementById("drawer-btn-generate");
  const btnCopy = document.getElementById("drawer-btn-copy");

  if (btnClose) btnClose.addEventListener("click", closeEventDrawer);
  if (backdrop) backdrop.addEventListener("click", closeEventDrawer);
  if (btnDone) btnDone.addEventListener("click", closeEventDrawer);
  if (btnGen) btnGen.addEventListener("click", handleGenerateDrawerPitch);
  if (btnCopy) btnCopy.addEventListener("click", handleCopyDrawerPitch);
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
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (!data || !data.events) throw new Error("Static JSON payload returned");
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
    console.warn("Backend API not reachable; engaging static radar dataset...", err);
    await loadStaticEventsFallback();
  }
}

// In-memory cache of static events.json
let rawEventsCache = null;

async function loadStaticEventsFallback() {
  try {
    if (!rawEventsCache) {
      const res = await fetch("events.json");
      if (!res.ok) throw new Error("Could not load events.json");
      rawEventsCache = await res.json();
    }

    let filtered = [...rawEventsCache];

    // Priority filter
    if (state.priority && state.priority !== "all") {
      filtered = filtered.filter(e => (e.b2c_priority || "").toUpperCase() === state.priority.toUpperCase());
    }

    // Category filter
    if (state.category && state.category !== "all") {
      filtered = filtered.filter(e => (e.category || "").toLowerCase().includes(state.category.toLowerCase()));
    }

    // City filter
    if (state.city && state.city !== "all") {
      filtered = filtered.filter(e => (e.city || "").toLowerCase() === state.city.toLowerCase());
    }

    // Source filter
    if (state.source && state.source !== "all") {
      filtered = filtered.filter(e => (e.source || "").toLowerCase().includes(state.source.toLowerCase()));
    }

    // Search filter
    if (state.search && state.search.trim()) {
      const q = state.search.toLowerCase();
      filtered = filtered.filter(e =>
        (e.title || "").toLowerCase().includes(q) ||
        (e.description || "").toLowerCase().includes(q) ||
        (e.location || "").toLowerCase().includes(q) ||
        (e.organizer || "").toLowerCase().includes(q)
      );
    }

    // Partners only
    if (state.partnersOnly) {
      filtered = filtered.filter(e => e.parallel_org && e.parallel_org !== "Independent");
    }

    // Clashes only
    if (state.clashesOnly) {
      filtered = filtered.filter(e => e.clash_warning);
    }

    // Sorting
    if (state.sort === "score_desc") {
      filtered.sort((a, b) => (b.b2c_score || 0) - (a.b2c_score || 0));
    } else if (state.sort === "score_asc") {
      filtered.sort((a, b) => (a.b2c_score || 0) - (b.b2c_score || 0));
    }

    state.events = filtered;

    // Metrics HUD
    const totalEvents = filtered.length;
    const highPriority = filtered.filter(e => (e.b2c_score || 0) >= 8.5).length;
    const flagshipCount = filtered.filter(e => (e.category || "").includes("Flagship") || (e.b2c_score || 0) >= 9.8).length;

    const elTotal = document.getElementById("stat-total");
    animateCounter(elTotal, totalEvents);

    const elHigh = document.getElementById("stat-high");
    animateCounter(elHigh, highPriority);

    const elFlagship = document.getElementById("stat-flagship-count");
    animateCounter(elFlagship, flagshipCount || 10);

    renderCards();
    if (state.activeView === "calendar") {
      renderCalendarView();
    }
  } catch (err) {
    console.error("Critical: Failed to load fallback events.json:", err);
    showToast("Radar dataset offline", "error");
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

    card.className = `radar-card spotlight-card p-5 flex flex-col justify-between ${glowClass}`;

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

    // Clicking card opens the Linear-style Slide-Over Drawer
    card.addEventListener("click", (e) => {
      if (e.target.closest("a") || e.target.closest("button")) return;
      openEventDrawer(ev);
    });

    // Attach click for pitch button (opens drawer directly for integrated workflow)
    const pitchBtn = card.querySelector(".btn-pitch-event");
    pitchBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      openEventDrawer(ev);
    });

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
      <div class="py-2.5 flex items-center justify-between border-b border-white/[0.06] last:border-0 gap-4 cursor-pointer hover:bg-white/[0.03] px-2 rounded-xl transition" onclick="openEventDrawerById('${e.event_id}')">
        <div>
          <div class="font-bold text-xs text-white flex items-center gap-2 font-display">
            <span>${e.title}</span>
            <span class="text-[10px] ${e.b2c_priority === 'HIGH' ? 'badge-neon-coral' : 'badge-neon-blue'} px-2 py-0.5 rounded-full font-bold">★ ${e.b2c_score.toFixed(1)}</span>
            <span class="text-[10px] bg-white/[0.06] text-slate-400 px-2 py-0.5 rounded-md font-medium">${e.source}</span>
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">${e.location} (<span class="text-slate-200 font-medium">${e.city}</span>) • <span class="text-[#00E5FF]">${e.recommended_action}</span></div>
        </div>
        <button class="text-xs bg-sky-500/15 hover:bg-sky-500 text-sky-300 hover:text-white border border-sky-500/30 px-3 py-1.5 rounded-xl font-bold shrink-0 transition active:scale-95 flex items-center gap-1.5" onclick="event.stopPropagation(); openEventDrawerById('${e.event_id}')">
          <i data-lucide="sparkles" class="w-3 h-3 text-cyan-300"></i> Intel & Pitch
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

// Client-side partnership proposal generator for static deployments
function generateClientPitch(event, memberName, memberEmail, memberPhone, purpose) {
  const name = memberName || "Abdelrahman Motazz";
  const email = memberEmail || "tanta@aiesec.net";
  const phone = memberPhone || "+20 10 0000 0000";
  const title = event?.title || "Upcoming Youth Event";
  const org = event?.organizer || "Organizing Committee";

  if (purpose === "pr_media") {
    return {
      subject: `AIESEC in Egypt x ${title} - Official Youth Media & PR Partnership`,
      body: `Dear ${org} Organizing Committee,\n\nI hope this email finds you well.\n\nMy name is ${name}, representing AIESEC in Egypt (LC Tanta) — the world's largest youth-led leadership organization present in over 100+ countries and across Egyptian universities.\n\nWe have been following the preparations for "${title}" with great admiration for its impact on youth and students.\n\nWe would love to explore a formal PR & Media Collaboration with your team:\n- Amplifying ${title} across our campus network of 10,000+ university students in the Delta and Egypt.\n- Social media cross-promotional campaigns and student community blasts.\n- Co-branding opportunities to drive delegate registration.\n\nCould we schedule a brief 10-minute discovery call this week to coordinate?\n\nWarm regards,\n\n${name}\nBusiness Development & B2C Team\nAIESEC in Egypt\nEmail: ${email}\nPhone: ${phone}\nWebsite: https://aiesec.org.eg`
    };
  }

  return {
    subject: `AIESEC in Egypt - Partnership & Booth Activation Proposal for ${title}`,
    body: `Dear ${org} Organizing Committee,\n\nI hope this message finds you in high spirits.\n\nMy name is ${name}, representing AIESEC in Egypt (LC Tanta). We are reaching out regarding the upcoming "${title}".\n\nGiven the exceptional gathering of ambitious youth and university talent at ${title}, AIESEC would be thrilled to participate as an Official Youth Partner:\n\n1. Physical Engagement Booth: Interactive student activation space showcasing Global Volunteer & Global Talent leadership internships abroad.\n2. Interactive Youth Workshop / Speaking Slot: Practical session on global leadership and cross-cultural career skills.\n3. Delegate Perks: Tailored career and exchange opportunities exclusively for your attendees.\n\nWe would appreciate the opportunity to connect with your Partnerships Lead for a 10-minute briefing.\n\nBest regards,\n\n${name}\nB2C & Strategic Partnerships\nAIESEC in Egypt\nEmail: ${email}\nPhone: ${phone}\nWebsite: https://aiesec.org.eg`
  };
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
    let data;
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
      if (!res.ok) throw new Error("API not available");
      data = await res.json();
    } catch (apiErr) {
      console.warn("Backend pitch API offline, generating locally:", apiErr);
      data = generateClientPitch(state.activePitchEvent, memberName, memberEmail, memberPhone, purpose);
    }

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

// ============================================================
// COMMAND PALETTE (CTRL+K / CMD+K) CONTROLLER
// ============================================================
let cmdActiveIndex = 0;
let cmdItems = [];

function toggleCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  if (!modal) return;
  if (modal.classList.contains("hidden")) {
    openCommandPalette();
  } else {
    closeCommandPalette();
  }
}

function openCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  const input = document.getElementById("command-palette-input");
  if (!modal || !input) return;

  modal.classList.remove("hidden");
  input.value = "";
  cmdActiveIndex = 0;
  renderCommandPaletteResults("");
  input.focus();

  if (typeof gsap !== "undefined") {
    gsap.fromTo("#command-palette-container",
      { scale: 0.95, opacity: 0, y: -20 },
      { scale: 1, opacity: 1, y: 0, duration: 0.25, ease: "power2.out" }
    );
  }
}

function closeCommandPalette() {
  const modal = document.getElementById("command-palette-modal");
  if (!modal) return;
  modal.classList.add("hidden");
}

function updateCommandPaletteActiveItem() {
  const items = document.querySelectorAll(".cmd-palette-item");
  items.forEach((item, idx) => {
    if (idx === cmdActiveIndex) {
      item.classList.add("active");
      item.scrollIntoView({ block: "nearest", behavior: "smooth" });
    } else {
      item.classList.remove("active");
    }
  });
}

function renderCommandPaletteResults(query) {
  const resultsContainer = document.getElementById("command-palette-results");
  if (!resultsContainer) return;
  const q = (query || "").trim().toLowerCase();
  cmdItems = [];

  const actions = [
    {
      icon: "crown",
      iconColor: "text-amber-400",
      title: "Filter Flagship Summits",
      desc: "Techne Alexandria/Cairo, RiseUp, National Student Summits",
      run: () => {
        selectCategory.value = "Flagship Summits";
        selectCategory.dispatchEvent(new Event("change"));
        showToast("Filtered by Flagship Summits", "info");
      }
    },
    {
      icon: "flame",
      iconColor: "text-rose-400",
      title: "Show High-Priority Leads (Score ≥ 8.5)",
      desc: "Top conversion recruitment opportunities",
      run: () => {
        btnQuickFilterHigh.click();
      }
    },
    {
      icon: "map-pin",
      iconColor: "text-sky-400",
      title: "Focus Tanta / Delta Campus Hub",
      desc: "Primary LC recruitment operations",
      run: () => {
        selectCity.value = "tanta";
        selectCity.dispatchEvent(new Event("change"));
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("tanta");
        }
        showToast("Centered radar on Tanta Hub", "info");
      }
    },
    {
      icon: "map-pin",
      iconColor: "text-sky-400",
      title: "Focus Cairo University Hub",
      desc: "Capital student summits & tech events",
      run: () => {
        selectCity.value = "cairo";
        selectCity.dispatchEvent(new Event("change"));
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("cairo");
        }
        showToast("Centered radar on Cairo Hub", "info");
      }
    },
    {
      icon: "map-pin",
      iconColor: "text-sky-400",
      title: "Focus Alexandria Campus Hub",
      desc: "Mediterranean youth summits & Techne",
      run: () => {
        selectCity.value = "alexandria";
        selectCity.dispatchEvent(new Event("change"));
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("alexandria");
        }
        showToast("Centered radar on Alexandria Hub", "info");
      }
    },
    {
      icon: "calendar",
      iconColor: "text-purple-400",
      title: "Switch to Calendar Timeline View",
      desc: "Inspect upcoming peak clashes across weeks",
      run: () => {
        switchView("calendar");
      }
    },
    {
      icon: "layout-grid",
      iconColor: "text-blue-400",
      title: "Switch to Event Cards Grid",
      desc: "Browse cards with 1-click pitch generator",
      run: () => {
        switchView("cards");
      }
    },
    {
      icon: "sheet",
      iconColor: "text-emerald-400",
      title: "Download Excel Spreadsheet (.xlsx)",
      desc: "Export formatted intelligence spreadsheet",
      run: () => {
        window.location.href = "/api/export/excel";
        showToast("Downloading Excel spreadsheet...", "success");
      }
    }
  ];

  const matchedActions = actions.filter(a => !q || a.title.toLowerCase().includes(q) || a.desc.toLowerCase().includes(q));

  const eventsPool = (state.events && state.events.length > 0) ? state.events : (rawEventsCache || []);
  const matchedEvents = q ? eventsPool.filter(e => 
    (e.title && e.title.toLowerCase().includes(q)) || 
    (e.city && e.city.toLowerCase().includes(q)) || 
    (e.organizer && e.organizer.toLowerCase().includes(q))
  ).slice(0, 6) : [];

  let html = "";

  if (matchedActions.length > 0) {
    html += `<div class="px-2 py-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">Commands & Quick Actions</div>`;
    matchedActions.forEach((act) => {
      const idx = cmdItems.length;
      cmdItems.push(act);
      html += `
        <div class="cmd-palette-item flex items-center justify-between p-2.5 rounded-xl cursor-pointer border border-transparent ${idx === cmdActiveIndex ? 'active' : ''}" data-cmd-idx="${idx}">
          <div class="flex items-center gap-3">
            <div class="w-7 h-7 rounded-lg bg-white/[0.06] border border-white/10 flex items-center justify-center shrink-0">
              <i data-lucide="${act.icon}" class="w-4 h-4 ${act.iconColor}"></i>
            </div>
            <div>
              <div class="text-xs font-bold text-white">${act.title}</div>
              <div class="text-[11px] text-slate-400">${act.desc}</div>
            </div>
          </div>
          <span class="text-[10px] font-mono text-slate-500">Action</span>
        </div>
      `;
    });
  }

  if (matchedEvents.length > 0) {
    html += `<div class="px-2 pt-3 pb-1 text-[10px] font-bold tracking-wider text-slate-400 uppercase">Matching Campus Events</div>`;
    matchedEvents.forEach((ev) => {
      const idx = cmdItems.length;
      const act = {
        title: ev.title,
        run: () => {
          state.search = ev.title;
          inputSearch.value = ev.title;
          fetchEvents();
          showToast(`Filtered for: ${ev.title}`, "info");
        }
      };
      cmdItems.push(act);
      html += `
        <div class="cmd-palette-item flex items-center justify-between p-2.5 rounded-xl cursor-pointer border border-transparent ${idx === cmdActiveIndex ? 'active' : ''}" data-cmd-idx="${idx}">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center shrink-0">
              <i data-lucide="ticket" class="w-4 h-4 text-sky-400"></i>
            </div>
            <div class="min-w-0">
              <div class="text-xs font-bold text-white truncate">${ev.title}</div>
              <div class="text-[11px] text-slate-400 flex items-center gap-2">
                <span>📍 ${ev.city || 'Egypt'}</span>
                <span>•</span>
                <span>📅 ${ev.date_display || 'Upcoming'}</span>
              </div>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-500/20 text-sky-400 border border-sky-500/30 shrink-0">
            ★ ${ev.b2c_score?.toFixed(1) || '8.0'}
          </span>
        </div>
      `;
    });
  }

  if (cmdItems.length === 0) {
    html = `
      <div class="p-8 text-center text-slate-400 text-xs">
        <i data-lucide="compass" class="w-8 h-8 mx-auto mb-2 text-slate-500"></i>
        No commands or events matching "${query}"
      </div>
    `;
  }

  resultsContainer.innerHTML = html;
  if (window.lucide) lucide.createIcons();

  resultsContainer.querySelectorAll(".cmd-palette-item").forEach(el => {
    el.addEventListener("click", () => {
      const idx = parseInt(el.getAttribute("data-cmd-idx"));
      if (cmdItems[idx]) {
        cmdItems[idx].run();
        closeCommandPalette();
      }
    });
  });
}

