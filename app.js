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

/** @type {{ events: EventRecord[], sort: string, priority: string, category: string, city: string, source: string, search: string, partnersOnly: boolean, clashesOnly: boolean, activePitchEvent: EventRecord|null, activeDrawerEvent: EventRecord|null, activeTopic: string, currentTheme: string, activeView: 'cards'|'table'|'calendar' }} */
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
  canvasMode: "nebula",
  activeSpatialMode: "globe",
  activeIntents: null,
  activeView: "cards"
};

// DOM Elements
const containerCards = document.getElementById("container-cards");
const containerTable = document.getElementById("container-table");
const containerCalendar = document.getElementById("container-calendar");
const calendarTimeline = document.getElementById("calendar-timeline");
const tableBody = document.getElementById("table-body");
const tableCountBadge = document.getElementById("table-count-badge");
const btnTableExportCsv = document.getElementById("btn-table-export-csv");
const inputSearch = document.getElementById("input-search");
const selectSort = document.getElementById("select-sort");
const selectCategory = document.getElementById("select-category");
const selectCity = document.getElementById("select-city");
const selectSource = document.getElementById("select-source");
const checkPartnersOnly = document.getElementById("check-partners-only");
const checkClashesOnly = document.getElementById("check-clashes-only");
const btnViewCards = document.getElementById("btn-view-cards");
const btnViewTable = document.getElementById("btn-view-table");
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
  initAmbientCosmicDust();
  initCardTiltPhysics();
  initSmoothMouseLighting();
  initSolarCycle();
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

    // ----------------------------------------------------
    // FEATURE A: 3D ENTITY NETWORK MESH (Knowledge Graph)
    // ----------------------------------------------------
    const networkMeshGroup = new THREE.Group();
    networkMeshGroup.visible = false;
    scene.add(networkMeshGroup);

    const interactiveMeshNodes = [];
    const entityNodes = [
      { id: "aiesec-core", name: "AIESEC in Egypt (Tanta)", type: "National Youth Hub", city: "tanta", x: 0, y: 0, z: 0, radius: 7.5, color: 0x00e5ff, isCore: true, desc: "Leadership Pipeline & Global Talent Dispatch" },
      { id: "univ-tanta", name: "Tanta University", type: "Delta Campus Hub", city: "tanta", x: -38, y: 18, z: 12, radius: 5.0, color: 0x037ef3, desc: "Gharbia Academic Anchor • 100k+ Undergrads" },
      { id: "univ-cairo", name: "Cairo University", type: "Capital Campus Hub", city: "cairo", x: 38, y: 20, z: -15, radius: 5.2, color: 0x00e5ff, desc: "Flagship Campus • Giza/Cairo Student Gateway" },
      { id: "univ-alex", name: "Alexandria University", type: "Coastal Campus Hub", city: "alexandria", x: -28, y: -28, z: 18, radius: 5.0, color: 0x38bdf8, desc: "Mediterranean Coast • Techne Summit Partner" },
      { id: "univ-mansoura", name: "Mansoura University", type: "Delta Campus Hub", city: "mansoura", x: 32, y: -24, z: 20, radius: 4.6, color: 0xa855f7, desc: "Eastern Delta Anchor • Medical & Engineering" },
      { id: "univ-ainshams", name: "Ain Shams University", type: "Capital Campus Hub", city: "cairo", x: 14, y: 38, z: -20, radius: 4.6, color: 0x10b981, desc: "Cairo Tech Hub • Engineering & Youth Talent" },
      { id: "univ-assiut", name: "Assiut University", type: "Upper Egypt Hub", city: "assiut", x: -14, y: 38, z: 24, radius: 4.4, color: 0xf59e0b, desc: "Upper Egypt Regional Academic Center" },
      { id: "summit-techne", name: "Techne Summit", type: "Flagship Partner", query: "Techne", x: -55, y: -8, z: -16, radius: 6.2, color: 0xf59e0b, isFlagship: true, desc: "Mediterranean's Premier Tech & Startup Summit" },
      { id: "summit-riseup", name: "RiseUp Summit", type: "Flagship Partner", query: "RiseUp", x: 52, y: -12, z: -24, radius: 6.2, color: 0xf43f5e, isFlagship: true, desc: "MENA Innovation & Entrepreneurship Flagship" },
      { id: "org-ieee", name: "IEEE Egypt Section", type: "Student Organization", query: "IEEE", x: -44, y: 34, z: -18, radius: 4.2, color: 0x037ef3, desc: "Engineering Student Branches Across Campuses" },
      { id: "org-enactus", name: "Enactus Egypt", type: "Student Organization", query: "Enactus", x: 44, y: 30, z: 18, radius: 4.2, color: 0xfbbf24, desc: "Social Entrepreneurship & Campus Projects" },
      { id: "org-gdg", name: "Google Dev Groups", type: "Tech Community", query: "GDG", x: 8, y: -46, z: -10, radius: 4.2, color: 0x06b6d4, desc: "Developer Student Clubs & Tech Summits" }
    ];

    const nodeMap = new Map();
    let coreNodeMesh = null;

    entityNodes.forEach(nData => {
      const pos = new THREE.Vector3(nData.x, nData.y, nData.z);
      const geo = new THREE.SphereGeometry(nData.radius, 16, 16);
      const mat = new THREE.MeshBasicMaterial({
        color: nData.color,
        blending: THREE.AdditiveBlending,
        transparent: true,
        opacity: nData.isCore ? 0.95 : 0.85
      });
      const nodeMesh = new THREE.Mesh(geo, mat);
      nodeMesh.position.copy(pos);
      nodeMesh.userData = { node: nData };

      // Halo ring around node
      const haloGeo = new THREE.RingGeometry(nData.radius * 1.25, nData.radius * 1.5, 24);
      const haloMat = new THREE.MeshBasicMaterial({
        color: nData.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: nData.isCore ? 0.65 : 0.35,
        blending: THREE.AdditiveBlending
      });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.position.copy(pos);
      halo.lookAt(0, 0, 100);
      networkMeshGroup.add(halo);
      nodeMesh.userData.halo = halo;

      if (nData.isCore) coreNodeMesh = nodeMesh;

      networkMeshGroup.add(nodeMesh);
      interactiveMeshNodes.push(nodeMesh);
      nodeMap.set(nData.id, nodeMesh);
    });

    // Edges
    const entityEdges = [
      ["aiesec-core", "univ-tanta"],
      ["aiesec-core", "univ-cairo"],
      ["aiesec-core", "univ-alex"],
      ["aiesec-core", "univ-mansoura"],
      ["aiesec-core", "univ-ainshams"],
      ["aiesec-core", "univ-assiut"],
      ["aiesec-core", "summit-techne"],
      ["aiesec-core", "summit-riseup"],
      ["aiesec-core", "org-ieee"],
      ["aiesec-core", "org-enactus"],
      ["univ-alex", "summit-techne"],
      ["univ-tanta", "summit-techne"],
      ["univ-mansoura", "summit-techne"],
      ["univ-cairo", "summit-riseup"],
      ["univ-ainshams", "summit-riseup"],
      ["univ-cairo", "org-ieee"],
      ["univ-ainshams", "org-ieee"],
      ["univ-tanta", "org-ieee"],
      ["univ-cairo", "org-enactus"],
      ["univ-tanta", "org-enactus"],
      ["univ-cairo", "org-gdg"],
      ["univ-alex", "org-gdg"]
    ];

    const edgePairs = [];
    entityEdges.forEach(([fromId, toId]) => {
      const nFrom = nodeMap.get(fromId);
      const nTo = nodeMap.get(toId);
      if (!nFrom || !nTo) return;

      const edgeGeo = new THREE.BufferGeometry().setFromPoints([nFrom.position, nTo.position]);
      const edgeMat = new THREE.LineBasicMaterial({
        color: fromId === "aiesec-core" ? 0x00e5ff : 0x037ef3,
        transparent: true,
        opacity: fromId === "aiesec-core" ? 0.35 : 0.18,
        blending: THREE.AdditiveBlending
      });
      const edgeLine = new THREE.Line(edgeGeo, edgeMat);
      networkMeshGroup.add(edgeLine);
      edgePairs.push({ from: nFrom.position, to: nTo.position });
    });

    // Flowing Data Signal Pulses on Edges
    const pulseCount = 14;
    const pulseGeo = new THREE.SphereGeometry(1.2, 8, 8);
    const pulseMat = new THREE.MeshBasicMaterial({
      color: 0x00e5ff,
      blending: THREE.AdditiveBlending,
      transparent: true,
      opacity: 0.9
    });
    const pulseMeshes = [];
    for (let p = 0; p < pulseCount; p++) {
      const pMesh = new THREE.Mesh(pulseGeo, pulseMat);
      const edgeIndex = p % edgePairs.length;
      pMesh.userData = {
        edgeIndex: edgeIndex,
        progress: Math.random(),
        speed: 0.005 + Math.random() * 0.007
      };
      networkMeshGroup.add(pMesh);
      pulseMeshes.push(pMesh);
    }

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

    // Spatial Mode Switcher (Globe vs Entity Network Mesh)
    const btnSpatialGlobe = document.getElementById("btn-spatial-globe");
    const btnSpatialMesh = document.getElementById("btn-spatial-mesh");
    const spatialTitle = document.getElementById("spatial-card-title");

    function setSpatialMode(mode) {
      state.activeSpatialMode = mode;
      if (mode === "mesh") {
        if (btnSpatialMesh) btnSpatialMesh.className = "px-2 py-0.5 rounded-md bg-[#037EF3] text-white shadow-sm transition active:scale-95 flex items-center gap-1";
        if (btnSpatialGlobe) btnSpatialGlobe.className = "px-2 py-0.5 rounded-md text-slate-400 hover:text-white transition active:scale-95 flex items-center gap-1";
        if (spatialTitle) spatialTitle.innerText = "AIESEC Knowledge Mesh (3D Entity Network)";
        if (statusPill) statusPill.innerText = "12 Entity Nodes Active";

        globeGroup.visible = false;
        networkMeshGroup.visible = true;
        if (typeof gsap !== "undefined") {
          gsap.fromTo(networkMeshGroup.scale, { x: 0.8, y: 0.8, z: 0.8 }, { x: 1, y: 1, z: 1, duration: 0.45, ease: "back.out(1.2)" });
        }
        showToast("Switched to 3D Entity Knowledge Mesh", "info");
      } else {
        if (btnSpatialGlobe) btnSpatialGlobe.className = "px-2 py-0.5 rounded-md bg-[#037EF3] text-white shadow-sm transition active:scale-95 flex items-center gap-1";
        if (btnSpatialMesh) btnSpatialMesh.className = "px-2 py-0.5 rounded-md text-slate-400 hover:text-white transition active:scale-95 flex items-center gap-1";
        if (spatialTitle) spatialTitle.innerText = "Egypt Campus Radar Grid (3D Spatial Feed)";
        if (statusPill) statusPill.innerText = state.city === "all" ? "6 Active Hubs" : `Selected: ${state.city}`;

        networkMeshGroup.visible = false;
        globeGroup.visible = true;
        if (typeof gsap !== "undefined") {
          gsap.fromTo(globeGroup.scale, { x: 0.8, y: 0.8, z: 0.8 }, { x: 1, y: 1, z: 1, duration: 0.45, ease: "back.out(1.2)" });
        }
        showToast("Switched to 3D Geospatial Globe", "info");
      }
    }

    if (btnSpatialGlobe) btnSpatialGlobe.addEventListener("click", () => setSpatialMode("globe"));
    if (btnSpatialMesh) btnSpatialMesh.addEventListener("click", () => setSpatialMode("mesh"));

    // Expose controller for external city selection synchronization & dynamic theme adaptation
    globeController.focusCity = rotateToCity;
    globeController.updateThemeColor = (hexColor) => {
      if (wireframeMat) wireframeMat.color.setHex(hexColor);
      if (coreNodeMesh && coreNodeMesh.material) coreNodeMesh.material.color.setHex(hexColor);
    };
    globeController.setSpatialMode = setSpatialMode;

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

      const isMeshMode = state.activeSpatialMode === "mesh";
      const targetObjects = isMeshMode ? interactiveMeshNodes : interactivePins;

      // Raycast against interactive objects
      raycaster.setFromCamera(mouseNorm, camera);
      const hits = raycaster.intersectObjects(targetObjects, false);

      if (hits.length > 0) {
        const hitObj = hits[0].object;

        if (hoveredPin !== hitObj) {
          if (hoveredPin) hoveredPin.scale.set(1, 1, 1);
          hoveredPin = hitObj;
          hitObj.scale.set(1.4, 1.4, 1.4);
        }

        canvas.style.cursor = "pointer";

        // Position & populate tooltip
        if (tooltip) {
          const tooltipCity = document.getElementById("globe-tooltip-city");
          const tooltipCount = document.getElementById("globe-tooltip-count");
          const tooltipFlagships = document.getElementById("globe-tooltip-flagships");

          if (isMeshMode) {
            const node = hitObj.userData.node;
            if (tooltipCity) tooltipCity.innerText = node.isCore ? "🌐 " + node.name : (node.isFlagship ? "👑 " + node.name : "🏛️ " + node.name);
            if (tooltipCount) tooltipCount.innerText = node.type;
            if (tooltipFlagships) tooltipFlagships.innerText = node.desc;
          } else {
            const hub = hitObj.userData.hub;
            const cityEvents = state.events.filter(ev => ev.city.toLowerCase().includes(hub.cityKey.toLowerCase()));
            const flagshipEvents = cityEvents.filter(ev => (ev.category && ev.category.toLowerCase().includes("flagship")) || ev.title.toLowerCase().includes("techne") || ev.title.toLowerCase().includes("riseup"));

            if (tooltipCity) tooltipCity.innerText = `📍 ${hub.name}`;
            if (tooltipCount) tooltipCount.innerText = `${cityEvents.length} Events`;
            if (tooltipFlagships) {
              tooltipFlagships.innerText = flagshipEvents.length > 0 
                ? `👑 ${flagshipEvents.length} Flagship (${flagshipEvents[0].title.split(" 202")[0]})` 
                : "Campus Lead Pipeline";
            }
          }

          const worldPos = new THREE.Vector3();
          hitObj.getWorldPosition(worldPos);
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

      if (state.activeSpatialMode === "mesh") {
        networkMeshGroup.rotation.y += deltaX * 0.01;
        networkMeshGroup.rotation.x += deltaY * 0.01;
      } else {
        globeGroup.rotation.y += deltaX * 0.01;
        globeGroup.rotation.x += deltaY * 0.01;
      }

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

      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 2) {
        dragMoved = true;
        if (state.activeSpatialMode === "mesh") {
          networkMeshGroup.rotation.y += deltaX * 0.012;
        } else {
          globeGroup.rotation.y += deltaX * 0.012;
        }
      }

      prevPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }, { passive: true });

    // Click on Canvas Pin Trigger
    container.addEventListener("click", () => {
      if (dragMoved) return; // Ignore drag end click
      const isMeshMode = state.activeSpatialMode === "mesh";
      const targetObjects = isMeshMode ? interactiveMeshNodes : interactivePins;

      raycaster.setFromCamera(mouseNorm, camera);
      const hits = raycaster.intersectObjects(targetObjects, false);

      if (hits.length > 0) {
        const hitObj = hits[0].object;

        if (isMeshMode) {
          const node = hitObj.userData.node;
          if (node.isCore) {
            if (selectCity) selectCity.value = "all";
            state.city = "all";
            if (selectCategory) selectCategory.value = "all";
            state.category = "all";
            if (inputSearch) inputSearch.value = "";
            state.search = "";
            fetchEvents();
            showToast("Radar reset to full national network", "info");
          } else if (node.city) {
            filterByCity(node.city, node.name);
          } else if (node.query) {
            if (inputSearch) inputSearch.value = node.query;
            state.search = node.query;
            fetchEvents();
            showToast(`Filtered radar for ${node.name}`, "info");
          }
        } else {
          const pin = hitObj;
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
      }
    });

    // High-Performance Visibility Observer:
    // Only render Three.js when hero canvas is actually visible on screen.
    // When scrolled down to view cards, Three.js is completely paused to save 100% CPU/GPU!
    let isHeroVisible = true;
    if ("IntersectionObserver" in window) {
      const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          isHeroVisible = entry.isIntersecting;
        });
      }, { threshold: 0.05 });
      heroObserver.observe(container);
    }

    // Render Animation Loop with 3D Holographic Particle Wave Flow
    let waveClock = 0;
    const isMobileViewport = window.innerWidth < 768 || ("ontouchstart" in window);
    function animate() {
      requestAnimationFrame(animate);

      // Skip render if off-screen, tab hidden, or drawer open
      if (!isHeroVisible || document.hidden || state.activeDrawerEvent) {
        return;
      }

      waveClock += 0.022;

      if (state.activeSpatialMode === "mesh") {
        if (!isDragging) {
          networkMeshGroup.rotation.y += 0.002;
          networkMeshGroup.rotation.x += 0.0006;
          networkMeshGroup.rotation.y += (targetRotY - networkMeshGroup.rotation.y) * 0.035;
          networkMeshGroup.rotation.x += (targetRotX - networkMeshGroup.rotation.x) * 0.035;
        }

        // Pulse data packets along edges
        pulseMeshes.forEach(pMesh => {
          pMesh.userData.progress += pMesh.userData.speed;
          if (pMesh.userData.progress > 1) pMesh.userData.progress = 0;
          const pair = edgePairs[pMesh.userData.edgeIndex];
          if (pair) {
            pMesh.position.lerpVectors(pair.from, pair.to, pMesh.userData.progress);
          }
        });

        // Core node pulsating breathing effect
        if (coreNodeMesh) {
          const pulseScale = 1.0 + 0.08 * Math.sin(waveClock * 2.5);
          coreNodeMesh.scale.set(pulseScale, pulseScale, pulseScale);
        }

        // Orient halos towards camera
        interactiveMeshNodes.forEach(n => {
          if (n.userData && n.userData.halo) {
            n.userData.halo.quaternion.copy(camera.quaternion);
          }
        });
      } else {
        // Subtle dynamic 3D undulating wave oscillation across particles (desktop only to prevent mobile stutter)
        if (!isMobileViewport && partGeo && partGeo.attributes && partGeo.attributes.position) {
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

  // Lightweight delegated card spotlight calculation ONLY for the single card currently hovered
  document.addEventListener("mousemove", (e) => {
    const card = e.target.closest(".spotlight-card");
    if (card) {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--card-mouse-x", `${(e.clientX - rect.left).toFixed(1)}px`);
      card.style.setProperty("--card-mouse-y", `${(e.clientY - rect.top).toFixed(1)}px`);
    }
  }, { passive: true });
}

// ============================================================
// DYNAMIC EGYPTIAN SOLAR CYCLE (Atmospheric Cairo Time-Engine)
// ============================================================
let solarCycleState = {
  mode: localStorage.getItem("aiesec_solar_mode") || "auto", // 'auto' | 'dawn' | 'meridian' | 'dusk' | 'midnight'
  activePhase: "midnight",
  cairoHour: 5,
  cairoMinute: 0,
  timeString: ""
};

const SOLAR_PHASES = {
  dawn: {
    icon: "🌅",
    label: "Dawn",
    fullLabel: "Golden Dawn (06:00 - 10:00)",
    accent: "#F59E0B",
    glow: "rgba(245, 158, 11, 0.5)",
    beam1: "#F59E0B",
    beam2: "#FDE047"
  },
  meridian: {
    icon: "⚡",
    label: "Meridian",
    fullLabel: "Cyber Noon (10:00 - 17:30)",
    accent: "#00E5FF",
    glow: "rgba(0, 229, 255, 0.5)",
    beam1: "#00E5FF",
    beam2: "#037EF3"
  },
  dusk: {
    icon: "🌆",
    label: "Dusk",
    fullLabel: "Twilight Dusk (17:30 - 20:30)",
    accent: "#A855F7",
    glow: "rgba(168, 85, 247, 0.45)",
    beam1: "#A855F7",
    beam2: "#FF4D36"
  },
  midnight: {
    icon: "🌌",
    label: "Midnight",
    fullLabel: "Obsidian Midnight (20:30 - 06:00)",
    accent: "#38BDF8",
    glow: "rgba(56, 189, 248, 0.45)",
    beam1: "#38BDF8",
    beam2: "#10B981"
  }
};

function getCairoSolarPhase(hour, minute) {
  const decimalHour = hour + minute / 60;
  if (decimalHour >= 6.0 && decimalHour < 10.0) {
    return "dawn";
  } else if (decimalHour >= 10.0 && decimalHour < 17.5) {
    return "meridian";
  } else if (decimalHour >= 17.5 && decimalHour < 20.5) {
    return "dusk";
  } else {
    return "midnight";
  }
}

function applySolarPhase(phase) {
  solarCycleState.activePhase = phase;
  document.documentElement.setAttribute("data-solar", phase);

  // Update Solar Dial UI elements
  const orb = document.getElementById("solar-orb-indicator");
  const icon = document.getElementById("solar-dial-icon");
  const phaseLabel = document.getElementById("solar-dial-phase");
  const info = SOLAR_PHASES[phase] || SOLAR_PHASES.midnight;

  if (orb) {
    orb.style.backgroundColor = info.accent;
    orb.style.boxShadow = `0 0 10px ${info.glow}`;
  }
  if (icon) icon.textContent = info.icon;
  if (phaseLabel) phaseLabel.textContent = `· ${info.label}`;

  // Update menu active checkmarks
  document.querySelectorAll(".solar-dial-item").forEach((btn) => {
    const mode = btn.getAttribute("data-solar-mode");
    const check = btn.querySelector(".solar-check");
    if (mode === solarCycleState.mode) {
      btn.classList.add("active-solar-mode");
      if (check) check.classList.remove("hidden");
    } else {
      btn.classList.remove("active-solar-mode");
      if (check) check.classList.add("hidden");
    }
  });

  // Keep Three.js globe ambient light aligned if initialized
  if (window.threeSceneAmbient && info.accent) {
    try {
      window.threeSceneAmbient.color.set(info.accent);
    } catch (e) {}
  }
}

function updateCairoClock() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString("en-US", { 
    timeZone: "Africa/Cairo", 
    hour: "2-digit", 
    minute: "2-digit", 
    second: "2-digit",
    hour12: true 
  });

  const shortTimeStr = now.toLocaleTimeString("en-US", {
    timeZone: "Africa/Cairo",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  });

  // Calculate Cairo Hour in 24h format
  let hour = now.getUTCHours() + 2; // Cairo default UTC+2
  let minute = now.getUTCMinutes();
  try {
    const hour24Str = new Intl.DateTimeFormat("en-US", {
      timeZone: "Africa/Cairo",
      hour: "numeric",
      hour12: false
    }).format(now);
    const minStr = new Intl.DateTimeFormat("en-US", {
      timeZone: "Africa/Cairo",
      minute: "numeric"
    }).format(now);
    hour = parseInt(hour24Str, 10);
    minute = parseInt(minStr, 10);
  } catch (e) {}

  solarCycleState.cairoHour = hour;
  solarCycleState.cairoMinute = minute;
  solarCycleState.timeString = timeStr;

  // Update header labels
  const liveClock = document.getElementById("live-clock");
  if (liveClock) liveClock.innerText = `Cairo: ${timeStr}`;

  const dialClock = document.getElementById("solar-dial-clock");
  if (dialClock) dialClock.innerText = shortTimeStr;

  const menuTime = document.getElementById("solar-menu-time");
  if (menuTime) menuTime.innerText = `Cairo: ${timeStr}`;

  // If in auto mode, auto-detect phase
  if (solarCycleState.mode === "auto") {
    const autoPhase = getCairoSolarPhase(hour, minute);
    if (solarCycleState.activePhase !== autoPhase) {
      applySolarPhase(autoPhase);
    }
  }
}

function initSolarCycle() {
  const btnDial = document.getElementById("btn-solar-dial");
  const menuDial = document.getElementById("menu-solar-dial");

  if (btnDial && menuDial) {
    btnDial.addEventListener("click", (e) => {
      e.stopPropagation();
      menuDial.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!btnDial.contains(e.target) && !menuDial.contains(e.target)) {
        menuDial.classList.add("hidden");
      }
    });
  }

  // Bind clicks for all solar options
  document.querySelectorAll(".solar-dial-item").forEach((item) => {
    item.addEventListener("click", () => {
      const mode = item.getAttribute("data-solar-mode");
      if (!mode) return;
      solarCycleState.mode = mode;
      localStorage.setItem("aiesec_solar_mode", mode);

      if (mode === "auto") {
        const autoPhase = getCairoSolarPhase(solarCycleState.cairoHour, solarCycleState.cairoMinute);
        applySolarPhase(autoPhase);
      } else {
        applySolarPhase(mode);
      }

      if (menuDial) menuDial.classList.add("hidden");
    });
  });

  // Initial update
  updateCairoClock();
  if (solarCycleState.mode !== "auto") {
    applySolarPhase(solarCycleState.mode);
  } else {
    const autoPhase = getCairoSolarPhase(solarCycleState.cairoHour, solarCycleState.cairoMinute);
    applySolarPhase(autoPhase);
  }

  setInterval(updateCairoClock, 1000);
}

// ============================================================
// FEATURE 6: INTERACTIVE MOUSE-REPELLENT COSMIC DUST MATRIX
// ============================================================
let cosmicDustController = {
  updateTheme: null
};

function initAmbientCosmicDust() {
  const canvas = document.getElementById("threejs-radar-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const isMobile = window.innerWidth < 768 || ("ontouchstart" in window) || (navigator.maxTouchPoints > 0);
  let width = 0;
  let height = 0;
  const dpr = isMobile ? 1.0 : Math.min(window.devicePixelRatio || 1, 1.5);

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  resize();

  // Optimized particle population (lower on mobile to preserve 60/120fps scrolling)
  const particleCount = isMobile ? 22 : 65;
  const particles = [];

  let isScrolling = false;
  let scrollTimeout = null;
  window.addEventListener("scroll", () => {
    isScrolling = true;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => { isScrolling = false; }, 100);
  }, { passive: true });

  const THEME_DUST_PALETTES = {
    blue: ["#00E5FF", "#037EF3", "#38BDF8", "#93C5FD"],
    gold: ["#F59E0B", "#FBBF24", "#FCD34D", "#D97706"],
    cyan: ["#00E5FF", "#06B6D4", "#22D3EE", "#67E8F9"],
    coral: ["#FF4D36", "#FB7185", "#F43F5E", "#FDA4AF"],
    emerald: ["#10B981", "#34D399", "#6EE7B7", "#059669"],
    purple: ["#A855F7", "#C084FC", "#E879F9", "#7E22CE"],
    crimson: ["#F43F5E", "#FB7185", "#E11D48", "#FDA4AF"]
  };

  let activeColors = THEME_DUST_PALETTES[state.currentTheme] || THEME_DUST_PALETTES.blue;

  cosmicDustController.updateTheme = (themeName) => {
    activeColors = THEME_DUST_PALETTES[themeName] || THEME_DUST_PALETTES.blue;
    particles.forEach(p => {
      p.color = activeColors[Math.floor(Math.random() * activeColors.length)];
    });
  };

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.2,
      vy: -(0.12 + Math.random() * 0.3),
      ambientVx: (Math.random() - 0.5) * 0.18,
      ambientVy: -(0.08 + Math.random() * 0.22),
      radius: 0.8 + Math.random() * 1.8,
      baseAlpha: 0.2 + Math.random() * 0.55,
      pulsePhase: Math.random() * Math.PI * 2,
      pulseSpeed: 0.015 + Math.random() * 0.025,
      color: activeColors[Math.floor(Math.random() * activeColors.length)]
    });
  }

  // Mouse & Touch Tracking for dynamic repulsion
  const mouse = { x: -2000, y: -2000, active: false };

  window.addEventListener("mousemove", (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.active = true;
  }, { passive: true });

  window.addEventListener("touchmove", (e) => {
    if (e.touches && e.touches.length > 0) {
      mouse.x = e.touches[0].clientX;
      mouse.y = e.touches[0].clientY;
      mouse.active = true;
    }
  }, { passive: true });

  window.addEventListener("touchend", () => {
    mouse.active = false;
  });

  window.addEventListener("mouseleave", () => {
    mouse.active = false;
  });

  let resizeTimer = null;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 200);
  });

  // Animation Loop with tab throttle
  let isRunning = true;
  document.addEventListener("visibilitychange", () => {
    isRunning = !document.hidden;
  });

  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function renderDust() {
    if (isRunning && !state.activeDrawerEvent && (!isMobile || !isScrolling)) {
      ctx.clearRect(0, 0, width, height);

      const isObsidian = state.canvasMode === "obsidian";
      const repelRadius = isMobile ? 80 : 145;
      const repelStrength = isMobile ? 1.4 : 2.2;

      // 1. Update and draw dust particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (!prefersReduced) {
          // Repulsion physics from cursor
          if (mouse.active) {
            const dx = p.x - mouse.x;
            const dy = p.y - mouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < repelRadius && dist > 1) {
              const force = (1 - dist / repelRadius) * repelStrength;
              const angle = Math.atan2(dy, dx);
              p.vx += Math.cos(angle) * force;
              p.vy += Math.sin(angle) * force;
            }
          }

          p.vx *= 0.94;
          p.vy *= 0.94;

          p.x += p.vx + p.ambientVx;
          p.y += p.vy + p.ambientVy;

          if (p.x < -20) p.x = width + 20;
          else if (p.x > width + 20) p.x = -20;
          if (p.y < -20) p.y = height + 20;
          else if (p.y > height + 20) p.y = -20;
        }

        p.pulsePhase += p.pulseSpeed;
        const alpha = Math.max(0.08, Math.min(0.85, p.baseAlpha + Math.sin(p.pulsePhase) * 0.2));
        const drawColor = isObsidian ? "#E2E8F0" : p.color;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = drawColor;
        ctx.globalAlpha = isObsidian ? alpha * 0.85 : alpha * 0.65;
        ctx.fill();

        if (p.radius > 1.5 && !isMobile) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius * 2.2, 0, Math.PI * 2);
          ctx.fillStyle = drawColor;
          ctx.globalAlpha = alpha * 0.15;
          ctx.fill();
        }
      }

      // 2. Interconnecting neural constellation lines (Desktop only to prevent mobile GPU fill-rate throttling)
      if (!isMobile && !prefersReduced) {
        const maxConnectDist = 80;
        for (let i = 0; i < particles.length; i++) {
          for (let j = i + 1; j < particles.length; j++) {
            const p1 = particles[i];
            const p2 = particles[j];
            const dx = p1.x - p2.x;
            const dy = p1.y - p2.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < maxConnectDist) {
              const lineAlpha = (1 - dist / maxConnectDist) * (isObsidian ? 0.08 : 0.12);
              ctx.beginPath();
              ctx.moveTo(p1.x, p1.y);
              ctx.lineTo(p2.x, p2.y);
              ctx.strokeStyle = activeColors[0];
              ctx.globalAlpha = lineAlpha;
              ctx.lineWidth = 0.55;
              ctx.stroke();
            }
          }
        }
      }

      ctx.globalAlpha = 1.0;
    }
    requestAnimationFrame(renderDust);
  }
  requestAnimationFrame(renderDust);
}

// ============================================================
// FEATURE 1: 3D HOLOGRAPHIC CARD TILT & IRIDESCENT SHEEN CONTROLLER
// ============================================================
function initCardTiltPhysics() {
  // STRICT DESKTOP-ONLY GUARD:
  // Touchscreens do not have a cursor and trigger synthetic mousemove events
  // that cause catastrophic 3D layer clipping, shear distortion, and lag on mobile WebKit.
  const hasFinePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (!hasFinePointer || "ontouchstart" in window || (navigator.maxTouchPoints && navigator.maxTouchPoints > 0)) {
    return;
  }

  const container = document.getElementById("container-cards");
  if (!container) return;

  let activeCard = null;

  container.addEventListener("mousemove", (e) => {
    const card = e.target.closest(".radar-card");
    if (!card) {
      if (activeCard) {
        resetCardTilt(activeCard);
        activeCard = null;
      }
      return;
    }

    if (activeCard && activeCard !== card) {
      resetCardTilt(activeCard);
    }
    activeCard = card;

    const rect = card.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    const nx = (cx / rect.width) * 2 - 1; // -1 to 1
    const ny = (cy / rect.height) * 2 - 1;

    const maxTilt = 5.5; // subtle, realistic tilt degrees
    const tiltX = (-ny * maxTilt).toFixed(2);
    const tiltY = (nx * maxTilt).toFixed(2);

    card.style.transition = "none";
    card.style.transform = `perspective(1100px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale3d(1.015, 1.015, 1.015)`;
    card.style.setProperty("--sheen-x", `${cx}px`);
    card.style.setProperty("--sheen-y", `${cy}px`);
  });

  container.addEventListener("mouseleave", () => {
    if (activeCard) {
      resetCardTilt(activeCard);
      activeCard = null;
    }
  });

  function resetCardTilt(card) {
    card.style.transition = "transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease";
    card.style.transform = "perspective(1100px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
  }
}

// ============================================================
// FEATURE E: NATURAL LANGUAGE "ASK RADAR" PARSING & BADGE CONTROLLER
// ============================================================
function parseNaturalLanguageQuery(rawQuery) {
  if (!rawQuery || typeof rawQuery !== "string") return null;
  const q = rawQuery.trim();
  if (q.length < 3) return null;

  const intents = {
    raw: rawQuery,
    city: null,
    category: null,
    priority: null,
    isFree: false,
    hasClash: false,
    month: null,
    residualQuery: ""
  };

  let recognizedCount = 0;
  let remaining = q.toLowerCase();

  // 1. City extraction
  if (/\b(tanta)\b/i.test(remaining)) {
    intents.city = "tanta";
    remaining = remaining.replace(/\b(in\s+)?tanta\b/gi, " ");
    recognizedCount++;
  } else if (/\b(cairo)\b/i.test(remaining)) {
    intents.city = "cairo";
    remaining = remaining.replace(/\b(in\s+)?cairo\b/gi, " ");
    recognizedCount++;
  } else if (/\b(alex|alexandria)\b/i.test(remaining)) {
    intents.city = "alexandria";
    remaining = remaining.replace(/\b(in\s+)?(alex|alexandria)\b/gi, " ");
    recognizedCount++;
  } else if (/\b(mansoura)\b/i.test(remaining)) {
    intents.city = "mansoura";
    remaining = remaining.replace(/\b(in\s+)?mansoura\b/gi, " ");
    recognizedCount++;
  } else if (/\b(assiut|asyut)\b/i.test(remaining)) {
    intents.city = "assiut";
    remaining = remaining.replace(/\b(in\s+)?(assiut|asyut)\b/gi, " ");
    recognizedCount++;
  } else if (/\b(giza)\b/i.test(remaining)) {
    intents.city = "giza";
    remaining = remaining.replace(/\b(in\s+)?giza\b/gi, " ");
    recognizedCount++;
  }

  // 2. Category extraction
  if (/\b(hackathon|hackathons|tech|stem|ai|coding|software|developer)\b/i.test(remaining)) {
    intents.category = "Technology & Hackathons";
    remaining = remaining.replace(/\b(hackathons?|tech|stem|ai|coding|software|developer)\b/gi, " ");
    recognizedCount++;
  } else if (/\b(career|job|jobs|employment|internship|internships|fair|fairs)\b/i.test(remaining)) {
    intents.category = "Career Fair & Employment";
    remaining = remaining.replace(/\b(career|jobs?|employment|internships?|fairs?)\b/gi, " ");
    recognizedCount++;
  } else if (/\b(summit|summits|flagship|flagships)\b/i.test(remaining)) {
    intents.category = "Flagship Summits";
    remaining = remaining.replace(/\b(summits?|flagships?)\b/gi, " ");
    recognizedCount++;
  } else if (/\b(youth|leadership|student\s*org)\b/i.test(remaining)) {
    intents.category = "Youth Leadership & Student Orgs";
    remaining = remaining.replace(/\b(youth|leadership|student\s*org)\b/gi, " ");
    recognizedCount++;
  }

  // 3. Free admission
  if (/\b(free|zero\s*cost|no\s*ticket|complimentary)\b/i.test(remaining)) {
    intents.isFree = true;
    remaining = remaining.replace(/\b(free|zero\s*cost|no\s*ticket|complimentary)\b/gi, " ");
    recognizedCount++;
  }

  // 4. High Priority
  if (/\b(high|urgent|top|best|priority|recommended)\b/i.test(remaining)) {
    intents.priority = "HIGH";
    remaining = remaining.replace(/\b(high|urgent|top|best|priority|recommended)\b/gi, " ");
    recognizedCount++;
  }

  // 5. Clashes / Conflicts
  if (/\b(clash|clashes|conflict|conflicts|overlap|competing)\b/i.test(remaining)) {
    intents.hasClash = true;
    remaining = remaining.replace(/\b(clash(es)?|conflicts?|overlap|competing)\b/gi, " ");
    recognizedCount++;
  }

  // 6. Month / Timeline
  const months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
  for (const m of months) {
    const rx = new RegExp(`\\b(in\\s+)?${m}\\b`, "i");
    if (rx.test(remaining)) {
      intents.month = m.slice(0, 3).toUpperCase();
      remaining = remaining.replace(rx, " ");
      recognizedCount++;
      break;
    }
  }

  // Clean remaining stop words
  remaining = remaining.replace(/\b(in|at|for|the|a|an|events?|opportunities|radar|show|me|find|all|any)\b/gi, " ").trim();
  intents.residualQuery = remaining.replace(/\s+/g, " ").trim();

  return recognizedCount > 0 ? intents : null;
}

function renderSearchIntentPills(intents) {
  const container = document.getElementById("search-intent-pills");
  if (!container) return;

  if (!intents) {
    container.innerHTML = "";
    container.classList.add("hidden");
    return;
  }

  const chips = [];

  if (intents.city) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#00E5FF]/15 text-[#38BDF8] border border-[#00E5FF]/30 font-semibold shadow-sm">
        <span>📍 ${intents.city.toUpperCase()}</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="city" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (intents.category) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#A855F7]/15 text-[#C084FC] border border-[#A855F7]/30 font-semibold shadow-sm">
        <span>🏷️ ${intents.category}</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="category" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (intents.isFree) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 font-semibold shadow-sm">
        <span>🎟️ Free Admission</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="isFree" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (intents.priority) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-500/15 text-rose-300 border border-rose-500/30 font-semibold shadow-sm">
        <span>★ High Priority</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="priority" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (intents.hasClash) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold shadow-sm">
        <span>⚠️ Clashes Only</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="hasClash" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (intents.month) {
    chips.push(`
      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-blue-500/15 text-blue-300 border border-blue-500/30 font-semibold shadow-sm">
        <span>📅 ${intents.month}</span>
        <button type="button" class="btn-clear-intent hover:text-white ml-1 font-bold" data-intent-key="month" title="Remove filter">✕</button>
      </span>
    `);
  }

  if (chips.length > 0) {
    chips.push(`
      <button type="button" id="btn-clear-all-intents" class="text-[10px] text-slate-400 hover:text-white underline font-medium ml-1">
        Clear All
      </button>
    `);
    container.innerHTML = `<span class="text-slate-400 text-[9px] uppercase tracking-wider font-bold">Ask Radar:</span> ` + chips.join("");
    container.classList.remove("hidden");

    // Clear individual intent button handlers
    container.querySelectorAll(".btn-clear-intent").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const key = btn.dataset.intentKey;
        if (state.activeIntents) {
          state.activeIntents[key] = key === "isFree" || key === "hasClash" ? false : null;
          const hasAny = Boolean(state.activeIntents.city || state.activeIntents.category || state.activeIntents.isFree || state.activeIntents.priority || state.activeIntents.hasClash || state.activeIntents.month);
          if (!hasAny) {
            state.activeIntents = null;
          }
          renderSearchIntentPills(state.activeIntents);
          fetchEvents();
        }
      });
    });

    const clearAll = document.getElementById("btn-clear-all-intents");
    if (clearAll) {
      clearAll.addEventListener("click", (e) => {
        e.stopPropagation();
        state.activeIntents = null;
        renderSearchIntentPills(null);
        inputSearch.value = "";
        state.search = "";
        fetchEvents();
      });
    }
  } else {
    container.innerHTML = "";
    container.classList.add("hidden");
  }
}

function setupEventListeners() {
  // Natural Language "Ask Radar" & Search typing with smooth debounce
  let searchTimeout = null;
  inputSearch.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    const rawVal = e.target.value;
    searchTimeout = setTimeout(() => {
      const intents = parseNaturalLanguageQuery(rawVal);
      state.activeIntents = intents;
      renderSearchIntentPills(intents);
      state.search = rawVal.trim();
      fetchEvents();
    }, 180);
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
    // Global Keyboard Shortcut 'T': Cycle theme accents instantly
    if (e.key.toLowerCase() === "t" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      e.preventDefault();
      cycleNextTheme();
      return;
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
      switchView("table");
      showToast("Switched to Executive Table", "info");
    } else if (state.activeView === "table") {
      switchView("calendar");
      showToast("Switched to Conflict Radar", "info");
    } else {
      switchView("cards");
      showToast("Switched to Cards Grid", "info");
    }
  });
  if (mobileBtnTop) mobileBtnTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // View Switcher (Cards | Table | Conflict Radar)
  if (btnViewCards) btnViewCards.addEventListener("click", () => switchView("cards"));
  if (btnViewTable) btnViewTable.addEventListener("click", () => switchView("table"));
  if (btnViewCalendar) btnViewCalendar.addEventListener("click", () => switchView("calendar"));

  // Executive Table Export Button
  if (btnTableExportCsv) {
    btnTableExportCsv.addEventListener("click", () => {
      exportEventsToCSV(state.events);
      showToast("Exported executive data grid!", "success");
    });
  }

  // Executive Table Column Sorting Headers
  document.querySelectorAll("#executive-radar-table th.sortable").forEach((th) => {
    th.addEventListener("click", () => {
      const col = th.dataset.sortCol;
      if (tableSortCol === col) {
        tableSortAsc = !tableSortAsc;
      } else {
        tableSortCol = col;
        tableSortAsc = (col === "title" || col === "city");
      }
      renderTableView();
      showToast(`Sorted table by ${col} (${tableSortAsc ? "Ascending" : "Descending"})`, "info");
    });
  });

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

  const btnExportCsv = document.getElementById("btn-export-csv");
  if (btnExportCsv) {
    btnExportCsv.addEventListener("click", () => {
      exportEventsToCSV(state.events);
      showToast("Downloaded events CSV!", "success");
    });
  }
}

function switchView(view) {
  state.activeView = view;
  const activeClass = "px-3 py-1.5 text-xs font-bold rounded-lg bg-[#037EF3] text-white shadow-sm flex items-center gap-1.5 transition active:scale-95";
  const inactiveClass = "px-3 py-1.5 text-xs font-bold rounded-lg text-slate-400 hover:text-white flex items-center gap-1.5 transition active:scale-95";

  if (btnViewCards) btnViewCards.className = view === "cards" ? activeClass : inactiveClass;
  if (btnViewTable) btnViewTable.className = view === "table" ? activeClass : inactiveClass;
  if (btnViewCalendar) btnViewCalendar.className = view === "calendar" ? activeClass : inactiveClass;

  if (view === "cards") {
    if (containerCards) containerCards.classList.remove("hidden");
    if (containerTable) containerTable.classList.add("hidden");
    if (containerCalendar) containerCalendar.classList.add("hidden");
    renderCards();
  } else if (view === "table") {
    if (containerCards) containerCards.classList.add("hidden");
    if (containerTable) containerTable.classList.remove("hidden");
    if (containerCalendar) containerCalendar.classList.add("hidden");
    renderTableView();
  } else if (view === "calendar") {
    if (containerCards) containerCards.classList.add("hidden");
    if (containerTable) containerTable.classList.add("hidden");
    if (containerCalendar) containerCalendar.classList.remove("hidden");
    renderCalendarView();
  }
  if (window.lucide) lucide.createIcons();
}

// ============================================================
// THEME ACCENT CONTROLLER
// ============================================================
const THEME_ACCENTS = {
  blue: { name: "Electric Blue", hex: 0x037ef3, css: "#037EF3", glow: "rgba(3, 126, 243, 0.45)", border: "rgba(3, 126, 243, 0.4)" },
  gold: { name: "Sunlight Gold", hex: 0xf59e0b, css: "#F59E0B", glow: "rgba(245, 158, 11, 0.45)", border: "rgba(245, 158, 11, 0.4)" },
  cyan: { name: "Neon Cyan", hex: 0x00e5ff, css: "#00E5FF", glow: "rgba(0, 229, 255, 0.45)", border: "rgba(0, 229, 255, 0.4)" },
  coral: { name: "Sunset Coral", hex: 0xff4d36, css: "#FF4D36", glow: "rgba(255, 77, 54, 0.45)", border: "rgba(255, 77, 54, 0.4)" },
  emerald: { name: "Emerald Green", hex: 0x10b981, css: "#10B981", glow: "rgba(16, 185, 129, 0.45)", border: "rgba(16, 185, 129, 0.4)" },
  purple: { name: "Synthwave Violet", hex: 0xa855f7, css: "#A855F7", glow: "rgba(168, 85, 247, 0.45)", border: "rgba(168, 85, 247, 0.4)" },
  crimson: { name: "Crimson Stealth", hex: 0xf43f5e, css: "#F43F5E", glow: "rgba(244, 63, 94, 0.45)", border: "rgba(244, 63, 94, 0.4)" }
};

const THEME_CYCLE_KEYS = Object.keys(THEME_ACCENTS);

function applyThemeTokens(themeName) {
  const tObj = THEME_ACCENTS[themeName] || THEME_ACCENTS.blue;
  document.documentElement.setAttribute("data-theme", themeName);

  const subtleGlow = tObj.glow.replace(/[\d\.]+\)$/, "0.15)");
  document.documentElement.style.setProperty("--theme-accent", tObj.css);
  document.documentElement.style.setProperty("--theme-accent-glow", tObj.glow);
  document.documentElement.style.setProperty("--theme-accent-subtle", subtleGlow);
  document.documentElement.style.setProperty("--theme-accent-border", tObj.border);
  document.documentElement.style.setProperty("--aiesec-blue", tObj.css);
  document.documentElement.style.setProperty("--aiesec-blue-glow", tObj.css);
  document.documentElement.style.setProperty("--solar-beam-1", tObj.css);
  document.documentElement.style.setProperty("--solar-beam-2", tObj.glow);
  document.documentElement.style.setProperty("--solar-spotlight", subtleGlow);

  const indicator = document.getElementById("theme-accent-indicator");
  if (indicator) {
    indicator.style.backgroundColor = tObj.css;
    indicator.style.boxShadow = `0 0 10px ${tObj.glow}`;
  }

  if (typeof globeController !== "undefined" && typeof globeController.updateThemeColor === "function") {
    globeController.updateThemeColor(tObj.hex);
  }

  if (typeof cosmicDustController !== "undefined" && typeof cosmicDustController.updateTheme === "function") {
    cosmicDustController.updateTheme(themeName);
  }
}

function setTheme(themeName) {
  if (!THEME_ACCENTS[themeName]) themeName = "blue";
  state.currentTheme = themeName;
  applyThemeTokens(themeName);

  try {
    localStorage.setItem("aiesec_theme", themeName);
  } catch (e) {
    console.warn("Could not save theme to localStorage:", e);
  }

  // Update checkmarks in dropdown
  document.querySelectorAll(".theme-accent-option, .theme-accent-item").forEach((item) => {
    const isThis = item.dataset.theme === themeName;
    const check = item.querySelector(".theme-check-icon");
    if (check) {
      if (isThis) check.classList.remove("hidden");
      else check.classList.add("hidden");
    }
  });
}

function previewTheme(themeName) {
  if (THEME_ACCENTS[themeName]) {
    applyThemeTokens(themeName);
  }
}

function revertThemePreview() {
  applyThemeTokens(state.currentTheme);
}

function cycleNextTheme() {
  const currentIdx = THEME_CYCLE_KEYS.indexOf(state.currentTheme);
  const nextIdx = (currentIdx + 1) % THEME_CYCLE_KEYS.length;
  const nextTheme = THEME_CYCLE_KEYS[nextIdx];
  setTheme(nextTheme);
  showToast(`Theme: ${THEME_ACCENTS[nextTheme].name} (Press T to cycle)`, "info");
}

function setCanvasContrast(mode) {
  state.canvasMode = mode;
  if (mode === "obsidian") {
    document.documentElement.setAttribute("data-canvas", "obsidian");
  } else {
    document.documentElement.removeAttribute("data-canvas");
  }
  try {
    localStorage.setItem("aiesec_canvas_mode", mode);
  } catch (e) {}

  const btnNebula = document.getElementById("btn-canvas-nebula");
  const btnObsidian = document.getElementById("btn-canvas-obsidian");
  if (btnNebula && btnObsidian) {
    if (mode === "obsidian") {
      btnObsidian.className = "px-2 py-1 rounded-lg text-[10px] font-bold bg-[#037EF3]/20 text-[#38BDF8] border border-[#037EF3]/30 transition active:scale-95 text-center";
      btnNebula.className = "px-2 py-1 rounded-lg text-[10px] font-bold bg-white/[0.05] text-slate-300 hover:text-white border border-white/10 transition active:scale-95 text-center";
    } else {
      btnNebula.className = "px-2 py-1 rounded-lg text-[10px] font-bold bg-[#037EF3]/20 text-[#38BDF8] border border-[#037EF3]/30 transition active:scale-95 text-center";
      btnObsidian.className = "px-2 py-1 rounded-lg text-[10px] font-bold bg-white/[0.05] text-slate-300 hover:text-white border border-white/10 transition active:scale-95 text-center";
    }
  }
}

function initThemeAccent() {
  let saved = "blue";
  let savedCanvas = "nebula";
  try {
    saved = localStorage.getItem("aiesec_theme") || "blue";
    savedCanvas = localStorage.getItem("aiesec_canvas_mode") || "nebula";
  } catch (e) {
    saved = "blue";
  }
  setTheme(saved);
  setCanvasContrast(savedCanvas);

  const btnTheme = document.getElementById("btn-theme-accent");
  const menuTheme = document.getElementById("menu-theme-accent");
  const btnNebula = document.getElementById("btn-canvas-nebula");
  const btnObsidian = document.getElementById("btn-canvas-obsidian");

  if (btnNebula) btnNebula.addEventListener("click", () => setCanvasContrast("nebula"));
  if (btnObsidian) btnObsidian.addEventListener("click", () => setCanvasContrast("obsidian"));

  if (btnTheme && menuTheme) {
    btnTheme.addEventListener("click", (e) => {
      e.stopPropagation();
      menuTheme.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!btnTheme.contains(e.target) && !menuTheme.contains(e.target)) {
        menuTheme.classList.add("hidden");
        revertThemePreview();
      }
    });

    document.querySelectorAll(".theme-accent-item, .theme-accent-option").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.stopPropagation();
        const t = item.dataset.theme;
        setTheme(t);
        menuTheme.classList.add("hidden");
        showToast(`Theme: ${THEME_ACCENTS[t]?.name || t}`, "info");
      });

      // Live hover preview
      item.addEventListener("mouseenter", () => {
        const t = item.dataset.theme;
        previewTheme(t);
      });
      item.addEventListener("mouseleave", () => {
        revertThemePreview();
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

      const raw = (chip.dataset.topic || "").trim();
      const lower = raw.toLowerCase();
      state.activeTopic = raw;

      if (lower === "all") {
        state.category = "all";
        state.priority = "all";
        state.city = "all";
        if (selectCategory) selectCategory.value = "all";
        if (selectCity) selectCity.value = "all";
      } else if (lower.includes("flagship")) {
        state.category = "Flagship Summits";
        if (selectCategory) selectCategory.value = "Flagship Summits";
      } else if (lower.includes("tech") || lower.includes("stem") || lower.includes("hack")) {
        state.category = "Technology & Hackathons";
        if (selectCategory) selectCategory.value = "Technology & Hackathons";
      } else if (lower.includes("career") || lower.includes("business") || lower.includes("job") || lower.includes("fair")) {
        state.category = "Career Fair & Employment";
        if (selectCategory) selectCategory.value = "Career Fair & Employment";
      } else if (lower.includes("youth") || lower.includes("leadership")) {
        state.category = "Youth Leadership & Student Orgs";
        if (selectCategory) selectCategory.value = "Youth Leadership & Student Orgs";
      } else if (lower.includes("startup") || lower.includes("entrepreneur") || lower.includes("summit")) {
        state.category = "Startup";
        if (selectCategory) selectCategory.value = "all";
      } else if (lower.includes("culture") || lower.includes("art") || lower.includes("exchange")) {
        state.category = "Arts & Entertainment";
        if (selectCategory) selectCategory.value = "Arts & Entertainment";
      } else if (lower.includes("tanta")) {
        state.city = "tanta";
        if (selectCity) selectCity.value = "tanta";
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("tanta");
        }
      } else if (lower.includes("alex")) {
        state.city = "alexandria";
        if (selectCity) selectCity.value = "alexandria";
        if (typeof globeController !== "undefined" && typeof globeController.focusCity === "function") {
          globeController.focusCity("alexandria");
        }
      } else {
        state.category = raw;
      }

      fetchEvents();
      showToast(`Filter: ${chip.innerText.trim()}`, "info");
    });
  });
}

// ============================================================
// AUTOMATED ORGANIZER CONTACT & SOCIAL MEDIA SCOUT REGISTRY (Idea 9)
// ============================================================
const KNOWN_ORGANIZER_CONTACTS = {
  techne: {
    name: "Techne Summit Committee",
    email: "info@technesummit.com",
    instagram: "technesummit",
    linkedin: "company/techne-summit",
    phone: "+201200008324"
  },
  riseup: {
    name: "RiseUp Summit Team",
    email: "info@riseupsummit.com",
    instagram: "riseupsummit",
    linkedin: "company/riseup-summit",
    phone: "+201000007473"
  },
  ticketsmarche: {
    name: "TicketsMarche Operations",
    email: "support@ticketsmarche.com",
    instagram: "ticketsmarche",
    linkedin: "company/ticketsmarche",
    phone: "16826"
  },
  ieee: {
    name: "IEEE Egypt Section",
    email: "info@ieee-egypt.org",
    instagram: "ieee_egypt",
    linkedin: "company/ieee-egypt-section",
    phone: null
  },
  enactus: {
    name: "Enactus Egypt Country Office",
    email: "egypt@enactus.org",
    instagram: "enactusegypt",
    linkedin: "company/enactus-egypt",
    phone: null
  },
  "maker faire": {
    name: "Maker Faire Cairo",
    email: "info@makerfairecairo.com",
    instagram: "makerfairecairo",
    linkedin: "company/maker-faire-cairo",
    phone: null
  },
  egycon: {
    name: "EGYCON Organizing Committee",
    email: "contact@egycon.net",
    instagram: "egycon_official",
    linkedin: "company/egycon",
    phone: null
  },
  seamless: {
    name: "Seamless North Africa / Terrapinn",
    email: "info@terrapinn.com",
    instagram: "seamlessafrica",
    linkedin: "company/seamless-north-africa",
    phone: null
  },
  "cairo university": {
    name: "Cairo University Student Activities",
    email: "events@cu.edu.eg",
    instagram: "cairo_university_official",
    linkedin: "school/cairo-university",
    phone: null
  },
  "ain shams": {
    name: "Ain Shams University Youth Hub",
    email: "info@asu.edu.eg",
    instagram: "ainshams_uni",
    linkedin: "school/ain-shams-university",
    phone: null
  },
  "alexandria university": {
    name: "Alexandria University Student Affairs",
    email: "info@alexu.edu.eg",
    instagram: "alex_university_official",
    linkedin: "school/alexandria-university",
    phone: null
  },
  tanta: {
    name: "Tanta University Youth & Campus Council",
    email: "president@tanta.edu.eg",
    instagram: "tanta_university_official",
    linkedin: "school/tanta-university",
    phone: null
  },
  mansoura: {
    name: "Mansoura University Student Union",
    email: "info@mans.edu.eg",
    instagram: "mansoura_university",
    linkedin: "school/mansoura-university",
    phone: null
  },
  aiesec: {
    name: "AIESEC in Egypt LC Network",
    email: "contact@aiesec.org.eg",
    instagram: "aiesecinegypt",
    linkedin: "company/aiesecinegypt",
    phone: null
  }
};

function enrichEventContacts(ev) {
  if (!ev) return { organizerName: "Organizing Committee", email: null, instagram: null, linkedin: null, phone: null };

  let organizerName = ev.organizer || "Organizing Committee";
  let email = ev.organizer_email || null;
  let instagram = ev.organizer_instagram || null;
  let linkedin = ev.organizer_linkedin || null;
  let phone = ev.organizer_phone || null;

  const fullText = `${ev.title || ""} ${ev.organizer || ""} ${ev.description || ""} ${ev.parallel_org || ""}`.toLowerCase();

  for (const [key, item] of Object.entries(KNOWN_ORGANIZER_CONTACTS)) {
    if (fullText.includes(key)) {
      if (organizerName === "Organizing Committee" || !organizerName) {
        organizerName = item.name;
      }
      if (!email && item.email) email = item.email;
      if (!instagram && item.instagram) instagram = item.instagram;
      if (!linkedin && item.linkedin) linkedin = item.linkedin;
      if (!phone && item.phone) phone = item.phone;
      break;
    }
  }

  // Regex fallback from description
  const desc = ev.description || "";
  if (!email) {
    const m = desc.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
    if (m && !m[0].endsWith(".png") && !m[0].endsWith(".jpg")) email = m[0];
  }
  if (!phone) {
    const p = desc.match(/(?:\+?20|0)?1[0125]\d{8}\b|\b1[5679]\d{3}\b/);
    if (p) phone = p[0];
  }
  if (!instagram) {
    const cleanForIg = desc.replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, " ");
    const ig = cleanForIg.match(/(?:instagram\.com\/|(?<![\w.-])@)([a-zA-Z0-9_.]{3,30})/);
    if (ig && !["gmail", "yahoo", "hotmail", "outlook"].includes(ig[1].toLowerCase()) && !/\.(com|org|net|edu|gov|eg)$/i.test(ig[1])) {
      instagram = ig[1];
    }
  }

  return {
    organizerName,
    email,
    instagram,
    linkedin,
    phone
  };
}

// ============================================================
// LINEAR-STYLE SLIDE-OVER EVENT INTEL DRAWER
// ============================================================
let drawerScrollLockY = 0;

function lockBodyForDrawer() {
  drawerScrollLockY = window.pageYOffset || document.documentElement.scrollTop || 0;
  document.documentElement.classList.add("drawer-open");
  document.body.classList.add("drawer-open");
  document.body.style.top = `-${drawerScrollLockY}px`;
}

function unlockBodyForDrawer() {
  document.documentElement.classList.remove("drawer-open");
  document.body.classList.remove("drawer-open");
  document.body.style.top = "";
  window.scrollTo(0, drawerScrollLockY);
}

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

  // Populate Organizer Scout Deck (Idea 9)
  const contacts = enrichEventContacts(ev);
  const orgNameEl = document.getElementById("drawer-organizer-name");
  const orgStatusEl = document.getElementById("drawer-organizer-status");
  const emailBtn = document.getElementById("drawer-contact-email");
  const emailVal = document.getElementById("drawer-contact-email-val");
  const liBtn = document.getElementById("drawer-contact-linkedin");
  const liVal = document.getElementById("drawer-contact-linkedin-val");
  const igBtn = document.getElementById("drawer-contact-instagram");
  const igVal = document.getElementById("drawer-contact-instagram-val");
  const waBtn = document.getElementById("drawer-contact-phone");
  const waVal = document.getElementById("drawer-contact-phone-val");

  if (orgNameEl) orgNameEl.innerText = contacts.organizerName;
  if (orgStatusEl) {
    if (contacts.email || contacts.instagram || contacts.linkedin) {
      orgStatusEl.innerText = "Verified Scout";
      orgStatusEl.className = "px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30";
    } else {
      orgStatusEl.innerText = "Live Scout";
      orgStatusEl.className = "px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-sky-500/15 text-sky-300 border border-sky-500/30";
    }
  }

  // Setup Email Action
  if (emailVal) emailVal.innerText = contacts.email || "Draft Email Pitch";
  if (emailBtn) {
    emailBtn.onclick = (e) => {
      e.preventDefault();
      const defaultPitch = generateClientPitch(ev, "Abdelrahman Motazz", "abdelrahman.motazz@aiesec.net", "+20 10 1234 5678", "booth");
      const toStr = contacts.email || "";
      const mailto = `mailto:${toStr}?subject=${encodeURIComponent(defaultPitch.subject)}&body=${encodeURIComponent(defaultPitch.body)}`;
      window.open(mailto, "_blank");
      showToast(contacts.email ? `Drafting email to ${contacts.email}` : "Opening email pitch draft", "success");
    };
  }

  // Setup LinkedIn Action
  if (liVal) liVal.innerText = contacts.linkedin ? contacts.linkedin.replace("company/", "").replace("school/", "") : "Scout LinkedIn";
  if (liBtn) {
    const liUrl = contacts.linkedin 
      ? `https://www.linkedin.com/${contacts.linkedin}`
      : `https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(contacts.organizerName + " Egypt")}`;
    liBtn.href = liUrl;
    liBtn.onclick = () => showToast(`Opening LinkedIn Scout for ${contacts.organizerName}...`, "info");
  }

  // Setup Instagram DM Action
  if (igVal) igVal.innerText = contacts.instagram ? `@${contacts.instagram}` : "Scout Instagram";
  if (igBtn) {
    igBtn.onclick = (e) => {
      e.preventDefault();
      const pitchMsg = `Hello ${contacts.organizerName}! Reaching out on behalf of AIESEC in Egypt (LC Tanta). We're excited about "${ev.title}" and would love to collaborate as an official Youth / Media Partner. Can we connect with your team?`;
      navigator.clipboard.writeText(pitchMsg).then(() => {
        showToast("Instagram DM pitch copied to clipboard! Opening Instagram...", "success");
      });
      const igUrl = contacts.instagram
        ? `https://instagram.com/${contacts.instagram}`
        : `https://www.instagram.com/explore/tags/${encodeURIComponent(contacts.organizerName.replace(/\s+/g, '').toLowerCase())}/`;
      window.open(igUrl, "_blank");
    };
  }

  // Setup WhatsApp / Call Action
  if (waVal) waVal.innerText = contacts.phone || "Search Hotline";
  if (waBtn) {
    waBtn.onclick = (e) => {
      e.preventDefault();
      if (contacts.phone) {
        const cleanPhone = contacts.phone.replace(/[^0-9]/g, '');
        const waMsg = `Hello! Reaching out from AIESEC in Egypt regarding partnership opportunities for "${ev.title}".`;
        window.open(`https://wa.me/${cleanPhone}?text=${encodeURIComponent(waMsg)}`, "_blank");
        showToast(`Opening WhatsApp chat with ${contacts.phone}...`, "success");
      } else {
        const query = encodeURIComponent(`${contacts.organizerName} Egypt contact phone number`);
        window.open(`https://www.google.com/search?q=${query}`, "_blank");
        showToast(`Searching directory for ${contacts.organizerName}...`, "info");
      }
    };
  }

  if (drawer) {
    drawer.classList.remove("hidden");
    lockBodyForDrawer();
    requestAnimationFrame(() => {
      drawer.classList.add("active");
      const scrollBody = document.getElementById("drawer-scroll-body");
      if (scrollBody) scrollBody.scrollTop = 0;
    });
  }
  if (window.lucide) lucide.createIcons();
}

function closeEventDrawer() {
  const drawer = document.getElementById("event-detail-drawer");
  if (drawer) {
    drawer.classList.remove("active");
    unlockBodyForDrawer();
    setTimeout(() => {
      if (!drawer.classList.contains("active")) {
        drawer.classList.add("hidden");
      }
    }, 360);
  }
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
  if (backdrop) {
    backdrop.addEventListener("click", closeEventDrawer);
    backdrop.addEventListener("touchmove", (e) => {
      e.preventDefault();
    }, { passive: false });
  }
  if (btnDone) btnDone.addEventListener("click", closeEventDrawer);
  if (btnGen) btnGen.addEventListener("click", handleGenerateDrawerPitch);
  if (btnCopy) btnCopy.addEventListener("click", handleCopyDrawerPitch);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.activeDrawerEvent) {
      closeEventDrawer();
    }
  });
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

  if (state.activeIntents) {
    if (state.activeIntents.city && state.city === "all") params.set("city", state.activeIntents.city);
    if (state.activeIntents.category && state.category === "all") params.set("category", state.activeIntents.category);
    if (state.activeIntents.priority && state.priority === "all") params.set("priority", state.activeIntents.priority);
  }

  try {
    const res = await fetch(`/api/events?${params}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (!data || !data.events) throw new Error("Static JSON payload returned");
    state.events = deduplicateClientEvents(data.events);

    // Animate KPI Telemetry HUD with GSAP counter interpolation
    const elTotal = document.getElementById("stat-total");
    animateCounter(elTotal, data.metrics.total_events);

    const elHigh = document.getElementById("stat-high");
    animateCounter(elHigh, data.metrics.high_priority);

    const elFlagship = document.getElementById("stat-flagship-count");
    animateCounter(elFlagship, data.metrics.flagship_count || 10);

    updateYieldGauge(87);
    if (state.activeView === "cards") {
      renderCards();
    } else if (state.activeView === "table") {
      renderTableView();
    } else if (state.activeView === "calendar") {
      renderCalendarView();
    }
  } catch (err) {
    console.warn("Backend API not reachable; engaging static radar dataset...", err);
    await loadStaticEventsFallback();
  }
}

/**
 * Client-Side Deduplication Safeguard:
 * Guarantees that no duplicate event ID, canonical URL, or duplicate title+date is ever rendered.
 */
function deduplicateClientEvents(eventsList) {
  if (!Array.isArray(eventsList)) return [];
  const unique = [];
  const seenIds = new Set();
  const seenUrls = new Set();
  const seenTitles = [];

  for (const ev of eventsList) {
    if (!ev || !ev.title || typeof ev.title !== "string") continue;
    const titleClean = ev.title.trim();
    if (titleClean.length < 3 || titleClean.toLowerCase() === "null" || titleClean.toLowerCase() === "none") continue;

    // Check ID
    if (ev.event_id && seenIds.has(ev.event_id)) continue;

    // Check Canonical URL
    let canonUrl = "";
    if (ev.url && typeof ev.url === "string") {
      canonUrl = ev.url.split("?")[0].split("#")[0].replace(/\/+$/, "").toLowerCase();
      if (canonUrl && seenUrls.has(canonUrl)) continue;
    }

    // Check Normalized Title Tokens
    const normTitle = titleClean.toLowerCase()
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter(w => !["the", "a", "an", "in", "at", "and", "of", "to", "for", "tickets", "ticket", "egypt", "live"].includes(w) && w.length > 1)
      .join(" ");

    let isDuplicate = false;
    if (normTitle.length >= 4) {
      for (const t of seenTitles) {
        if (t.normTitle === normTitle) {
          if (ev.start_date && t.startDate) {
            const d1 = new Date(ev.start_date).getTime();
            const d2 = new Date(t.startDate).getTime();
            if (Math.abs(d1 - d2) <= 4 * 86400000) {
              isDuplicate = true;
              break;
            }
          } else {
            isDuplicate = true;
            break;
          }
        }
      }
    }

    if (isDuplicate) continue;

    if (ev.event_id) seenIds.add(ev.event_id);
    if (canonUrl) seenUrls.add(canonUrl);
    seenTitles.push({ normTitle, startDate: ev.start_date });
    unique.push(ev);
  }

  return unique;
}

// In-memory cache of static events.json
let rawEventsCache = null;

async function loadStaticEventsFallback() {
  try {
    if (!rawEventsCache) {
      const res = await fetch("events.json");
      if (!res.ok) throw new Error("Could not load events.json");
      const loaded = await res.json();
      rawEventsCache = deduplicateClientEvents(loaded);
    }

    let filtered = [...rawEventsCache];

    // Priority filter
    if (state.priority && state.priority !== "all") {
      filtered = filtered.filter(e => (e.b2c_priority || "").toUpperCase() === state.priority.toUpperCase());
    }

    // Category filter with smart fuzzy keyword matching
    if (state.category && state.category !== "all") {
      const catLower = state.category.toLowerCase();
      filtered = filtered.filter(e => {
        const evCat = (e.category || "").toLowerCase();
        const evTitle = (e.title || "").toLowerCase();
        if (evCat.includes(catLower)) return true;
        if (catLower.includes("tech") && (evCat.includes("tech") || evTitle.includes("tech") || evTitle.includes("ai") || evTitle.includes("hackathon"))) return true;
        if (catLower.includes("flagship") && (evCat.includes("flagship") || (e.b2c_score && e.b2c_score >= 9.0) || evTitle.includes("techne") || evTitle.includes("riseup"))) return true;
        if (catLower.includes("career") && (evCat.includes("career") || evCat.includes("employment") || evTitle.includes("job") || evTitle.includes("career"))) return true;
        if (catLower.includes("youth") && (evCat.includes("youth") || evCat.includes("leadership") || evTitle.includes("youth") || evTitle.includes("leader"))) return true;
        if (catLower.includes("startup") && (evCat.includes("startup") || evCat.includes("entrepreneur") || evTitle.includes("summit") || evTitle.includes("pitch"))) return true;
        if (catLower.includes("art") && (evCat.includes("art") || evCat.includes("entertainment") || evCat.includes("culture"))) return true;
        return false;
      });
    }

    // City filter with case-insensitive substring matching
    if (state.city && state.city !== "all") {
      filtered = filtered.filter(e => (e.city || "").toLowerCase().includes(state.city.toLowerCase()));
    }

    // Source filter
    if (state.source && state.source !== "all") {
      filtered = filtered.filter(e => (e.source || "").toLowerCase().includes(state.source.toLowerCase()));
    }

    // Search filter & Natural Language Intent Filtering (Ask Radar)
    if (state.activeIntents) {
      const it = state.activeIntents;
      if (it.city) {
        filtered = filtered.filter(e => (e.city || "").toLowerCase().includes(it.city.toLowerCase()));
      }
      if (it.category) {
        const catTarget = it.category.toLowerCase();
        filtered = filtered.filter(e => {
          const evCat = (e.category || "").toLowerCase();
          const evTitle = (e.title || "").toLowerCase();
          if (evCat.includes(catTarget)) return true;
          if (catTarget.includes("tech") && (evCat.includes("tech") || evTitle.includes("tech") || evTitle.includes("ai") || evTitle.includes("hackathon"))) return true;
          if (catTarget.includes("flagship") && (evCat.includes("flagship") || (e.b2c_score && e.b2c_score >= 9.0) || evTitle.includes("techne") || evTitle.includes("riseup"))) return true;
          if (catTarget.includes("career") && (evCat.includes("career") || evCat.includes("employment") || evTitle.includes("job") || evTitle.includes("career"))) return true;
          if (catTarget.includes("youth") && (evCat.includes("youth") || evCat.includes("leadership") || evTitle.includes("youth") || evTitle.includes("leader"))) return true;
          return false;
        });
      }
      if (it.isFree) {
        filtered = filtered.filter(e => {
          const t = (e.ticket_type || "").toLowerCase();
          const desc = (e.description || "").toLowerCase();
          return t.includes("free") || desc.includes("free") || !t || t.includes("zero");
        });
      }
      if (it.priority) {
        filtered = filtered.filter(e => (e.b2c_priority || "").toUpperCase() === it.priority.toUpperCase());
      }
      if (it.hasClash) {
        filtered = filtered.filter(e => Boolean(e.clash_warning));
      }
      if (it.month) {
        filtered = filtered.filter(e => {
          const dateStr = (e.date_display || "").toUpperCase();
          return dateStr.includes(it.month);
        });
      }
      if (it.residualQuery) {
        const rq = it.residualQuery.toLowerCase();
        filtered = filtered.filter(e =>
          (e.title || "").toLowerCase().includes(rq) ||
          (e.description || "").toLowerCase().includes(rq) ||
          (e.location || "").toLowerCase().includes(rq)
        );
      }
    } else if (state.search && state.search.trim()) {
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

    updateYieldGauge(87);
    if (state.activeView === "cards") {
      renderCards();
    } else if (state.activeView === "table") {
      renderTableView();
    } else if (state.activeView === "calendar") {
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
    let beamClass = "beam-default";
    if (isFlagship) {
      glowClass = "card-summit-glow";
      beamClass = "beam-summit";
    } else if (isHigh) {
      glowClass = "card-high-glow";
      beamClass = "beam-high";
    } else if (hasPartner) {
      glowClass = "card-partner-glow";
      beamClass = "beam-partner";
    }

    card.className = `radar-card spotlight-card p-5 sm:p-6 flex flex-col justify-between h-full ${glowClass}`;

    // Priority badge class
    const contacts = enrichEventContacts(ev);
    const badgeClass = isHigh ? "badge-neon-coral" : (ev.b2c_priority === "MEDIUM" ? "badge-neon-amber" : "badge-neon-slate");
    const dateBadge = parseDateForTearoff(ev.date_display);
    const sourcePill = getSourcePill(ev.source);

    card.innerHTML = `
      <!-- Linear Conic Laser Border Beam (GPU-Accelerated) -->
      <div class="laser-border-beam ${beamClass}" aria-hidden="true"></div>

      <!-- Prismatic Holographic Iridescent Sheen (Feature 1) -->
      <div class="holographic-sheen"></div>

      <!-- Tactical Target Lock-On HUD Reticles (Feature B) -->
      <div class="hud-reticle-bracket hud-reticle-tl"></div>
      <div class="hud-reticle-bracket hud-reticle-tr"></div>
      <div class="hud-reticle-bracket hud-reticle-bl"></div>
      <div class="hud-reticle-bracket hud-reticle-br"></div>
      <div class="hud-scan-line"></div>
      <div class="hud-target-pill">LOCK ${ev.event_id ? ev.event_id.slice(-4).toUpperCase() : 'B2C'}</div>

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
        <div class="event-desc-box p-3.5 text-xs space-y-1.5 my-1">
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
        <div class="dark-action-box p-3.5 text-xs mt-1">
          <div class="text-[10px] font-bold text-[#00E5FF] uppercase tracking-wider mb-1 flex items-center gap-1.5 font-display">
            <i data-lucide="zap" class="w-3.5 h-3.5 text-[#00E5FF]"></i> Recommended B2C Action
          </div>
          <div class="font-medium text-slate-200 leading-relaxed text-[11px]">
            ${ev.recommended_action}
          </div>
        </div>

        <!-- Organizer Scout Intelligence Strip (Idea 9) -->
        <div class="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between gap-2 text-xs mt-1">
          <div class="flex items-center gap-1.5 min-w-0">
            <i data-lucide="user-check" class="w-3.5 h-3.5 text-emerald-400 shrink-0"></i>
            <span class="text-[11px] font-semibold text-slate-300 truncate" title="${contacts.organizerName}">${contacts.organizerName}</span>
          </div>
          <div class="flex items-center gap-1.5 shrink-0 text-slate-400">
            ${contacts.email ? `<span class="w-5 h-5 rounded-md bg-sky-500/15 text-sky-300 flex items-center justify-center text-[10px]" title="Email: ${contacts.email}"><i data-lucide="mail" class="w-3 h-3"></i></span>` : ""}
            ${contacts.linkedin ? `<span class="w-5 h-5 rounded-md bg-blue-600/15 text-blue-300 flex items-center justify-center text-[10px]" title="LinkedIn Verified"><i data-lucide="linkedin" class="w-3 h-3"></i></span>` : ""}
            ${contacts.instagram ? `<span class="w-5 h-5 rounded-md bg-pink-500/15 text-pink-300 flex items-center justify-center text-[10px]" title="Instagram: @${contacts.instagram}"><i data-lucide="instagram" class="w-3 h-3"></i></span>` : ""}
            ${contacts.phone ? `<span class="w-5 h-5 rounded-md bg-emerald-500/15 text-emerald-300 flex items-center justify-center text-[10px]" title="Phone: ${contacts.phone}"><i data-lucide="phone" class="w-3 h-3"></i></span>` : ""}
            <span class="text-[10px] text-sky-400 font-bold ml-1 hover:underline">Outreach →</span>
          </div>
        </div>
      </div>

      <!-- Action Footer (mt-auto guarantees aligned bottom across grid cards) -->
      <div class="pt-3.5 mt-auto border-t border-white/[0.08] flex items-center justify-between gap-2.5">
        <button class="btn-pitch-event flex-1 py-2.5 px-3.5 bg-gradient-to-r from-[#037EF3]/20 to-[#0266C8]/20 hover:from-[#037EF3] hover:to-[#0266C8] text-[#38BDF8] hover:text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 border border-[#38BDF8]/30 hover:border-transparent shadow-[0_0_12px_rgba(3,126,243,0.15)] active:scale-95"
                data-event-id="${ev.event_id}">
          <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Outreach Pitch
        </button>
        <a href="${ev.url}" target="_blank" class="p-2.5 text-slate-400 hover:text-white rounded-xl hover:bg-white/[0.08] border border-white/[0.09] transition active:scale-95 flex items-center justify-center shrink-0" title="Open Event Link">
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

// ============================================================
// MICRO-VISUAL TELEMETRY: RADIAL ARC SPEEDOMETER CONTROLLER
// ============================================================
function updateYieldGauge(percentage = 87) {
  const arc = document.getElementById("radial-yield-arc");
  const textEl = document.getElementById("stat-yield-pct");
  if (!arc) return;
  const pct = Math.max(0, Math.min(100, percentage));
  const circumference = 238.76;
  const offset = circumference * (1 - pct / 100);
  arc.style.strokeDashoffset = offset.toFixed(2);

  if (textEl) {
    if (window.gsap) {
      const current = parseInt(textEl.innerText) || 0;
      const obj = { val: current };
      gsap.to(obj, {
        val: pct,
        duration: 1.2,
        ease: "power2.out",
        onUpdate: () => {
          textEl.innerText = `${Math.round(obj.val)}%`;
        }
      });
    } else {
      textEl.innerText = `${pct}%`;
    }
  }
}

// ============================================================
// HIGH-DENSITY EXECUTIVE TABLE VIEW
// ============================================================
let tableSortCol = "priority";
let tableSortAsc = false;

function renderTableView(eventsToRender = state.events) {
  if (!tableBody) return;
  tableBody.innerHTML = "";

  const events = [...eventsToRender];

  // Apply sorting to table rows
  events.sort((a, b) => {
    let valA, valB;
    if (tableSortCol === "priority") {
      valA = a.b2c_score || 0;
      valB = b.b2c_score || 0;
    } else if (tableSortCol === "title") {
      valA = (a.title || "").toLowerCase();
      valB = (b.title || "").toLowerCase();
    } else if (tableSortCol === "date") {
      valA = a.start_date || a.date_display || "";
      valB = b.start_date || b.date_display || "";
    } else if (tableSortCol === "city") {
      valA = (a.city || "").toLowerCase();
      valB = (b.city || "").toLowerCase();
    } else {
      valA = a.b2c_score || 0;
      valB = b.b2c_score || 0;
    }

    if (valA < valB) return tableSortAsc ? -1 : 1;
    if (valA > valB) return tableSortAsc ? 1 : -1;
    return 0;
  });

  if (tableCountBadge) {
    tableCountBadge.innerText = `${events.length} Events Visible`;
  }

  if (events.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-12 text-slate-400">
          <i data-lucide="inbox" class="w-8 h-8 mx-auto text-slate-500 mb-2"></i>
          <p class="font-semibold text-sm text-slate-300 font-display">No events match your active filters</p>
          <p class="text-xs text-slate-500 mt-1">Try resetting filters or adjusting search queries</p>
        </td>
      </tr>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  events.forEach((ev) => {
    const contacts = enrichEventContacts(ev);
    const row = document.createElement("tr");
    const isHigh = (ev.b2c_priority || "").toUpperCase() === "HIGH";
    const isFlagship = (ev.category || "").includes("Flagship") || (ev.b2c_score && ev.b2c_score >= 9.5);
    row.className = `radar-table-row ${isHigh ? "row-priority-high" : ""}`;

    // Score pill
    let scoreBadge = "";
    if (isHigh) {
      scoreBadge = `<span class="px-2.5 py-1 rounded-lg font-bold text-[11px] bg-red-500/15 text-red-300 border border-red-500/30 inline-flex items-center gap-1 shadow-[0_0_10px_rgba(255,77,54,0.25)]"><i data-lucide="flame" class="w-3.5 h-3.5 text-[#FF4D36]"></i> ${(ev.b2c_score || 8.5).toFixed(1)}</span>`;
    } else if ((ev.b2c_priority || "").toUpperCase() === "MEDIUM") {
      scoreBadge = `<span class="px-2.5 py-1 rounded-lg font-bold text-[11px] bg-amber-500/15 text-amber-300 border border-amber-500/30 inline-flex items-center gap-1">${(ev.b2c_score || 7.0).toFixed(1)}</span>`;
    } else {
      scoreBadge = `<span class="px-2.5 py-1 rounded-lg font-semibold text-[11px] bg-white/[0.05] text-slate-400 border border-white/10 inline-flex items-center gap-1">${(ev.b2c_score || 5.0).toFixed(1)}</span>`;
    }

    // City tag
    const isTanta = (ev.city || "").toLowerCase().includes("tanta");
    const cityPill = isTanta 
      ? `<span class="font-bold text-sky-300 bg-sky-500/15 px-2 py-0.5 rounded-md border border-sky-500/30 text-[11px]">📍 Tanta</span>`
      : `<span class="font-semibold text-slate-200 text-xs">${ev.city || "Egypt"}</span>`;

    // Admission
    const isFree = (ev.ticket_type || "").toLowerCase().includes("free") || !ev.ticket_type;
    const admissionPill = isFree
      ? `<span class="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">Free Admission</span>`
      : `<span class="text-[10px] font-bold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20 truncate max-w-[120px] inline-block" title="${ev.ticket_type}">${ev.ticket_type}</span>`;

    row.innerHTML = `
      <td class="font-mono-code font-bold whitespace-nowrap">
        ${scoreBadge}
      </td>
      <td class="max-w-xs sm:max-w-md">
        <div class="flex items-center gap-1.5 flex-wrap">
          ${isFlagship ? `<span class="text-amber-400 font-bold text-[11px] shrink-0" title="Flagship Summit">👑</span>` : ""}
          <a href="${ev.url}" target="_blank" class="font-bold text-white hover:text-[#00E5FF] transition truncate max-w-[240px] sm:max-w-[340px] inline-block font-display" onclick="event.stopPropagation()">${ev.title}</a>
        </div>
        <div class="text-[10px] text-slate-400 mt-0.5 truncate flex items-center gap-2">
          <span class="text-slate-500">${ev.category || "Summit"}</span>
          ${ev.parallel_org && ev.parallel_org !== "Independent" ? `<span class="text-purple-300 font-semibold">• ${ev.parallel_org}</span>` : ""}
          <span class="text-emerald-400/90 font-medium inline-flex items-center gap-1 shrink-0">• <i data-lucide="user-check" class="w-3 h-3"></i> ${contacts.organizerName}</span>
        </div>
      </td>
      <td class="whitespace-nowrap">
        <div class="font-semibold text-slate-200 text-xs">${ev.date_display || "TBA"}</div>
        ${ev.clash_warning ? `<span class="text-[9px] font-bold text-amber-400">⚠️ Peak Weekend</span>` : ""}
      </td>
      <td class="whitespace-nowrap">
        ${cityPill}
        <div class="text-[10px] text-slate-400 truncate max-w-[140px] mt-0.5" title="${ev.location}">${ev.location}</div>
      </td>
      <td class="whitespace-nowrap">
        <span class="text-[11px] font-medium text-slate-300 bg-white/[0.04] px-2 py-0.5 rounded-md border border-white/[0.08]">${ev.source}</span>
      </td>
      <td class="whitespace-nowrap">
        ${admissionPill}
      </td>
      <td class="text-right whitespace-nowrap" onclick="event.stopPropagation()">
        <div class="flex items-center justify-end gap-1.5">
          <button class="btn-table-pitch px-2.5 py-1 bg-sky-500/15 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30 rounded-lg text-xs font-bold transition active:scale-95 flex items-center gap-1" title="Generate Pitch Proposal" data-event-id="${ev.event_id}">
            <i data-lucide="sparkles" class="w-3 h-3 text-cyan-300"></i> Pitch
          </button>
          <button class="btn-table-drawer p-1.5 text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.1] border border-white/10 rounded-lg transition" title="View Full Intel Drawer" data-event-id="${ev.event_id}">
            <i data-lucide="eye" class="w-3.5 h-3.5"></i>
          </button>
          <a href="${ev.url}" target="_blank" class="p-1.5 text-slate-400 hover:text-white bg-white/[0.04] hover:bg-white/[0.1] border border-white/10 rounded-lg transition" title="Open Event URL">
            <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
          </a>
        </div>
      </td>
    `;

    // Row click opens drawer
    row.addEventListener("click", () => openEventDrawer(ev));

    // Pitch button
    const pitchBtn = row.querySelector(".btn-table-pitch");
    if (pitchBtn) {
      pitchBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        openPitchModal(ev);
      });
    }

    // Drawer button
    const drawerBtn = row.querySelector(".btn-table-drawer");
    if (drawerBtn) {
      drawerBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        openEventDrawer(ev);
      });
    }

    tableBody.appendChild(row);
  });

  // Stagger entrance animation for table rows if GSAP present
  if (typeof gsap !== "undefined") {
    gsap.from("#table-body > tr", {
      opacity: 0,
      y: 10,
      stagger: 0.02,
      duration: 0.3,
      ease: "power2.out",
      clearProps: "all"
    });
  }

  if (window.lucide) lucide.createIcons();
}

window.openEventDrawerById = function(eventId) {
  const ev = state.events.find(e => e.event_id === eventId);
  if (ev) openEventDrawer(ev);
};

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

// --- Action Button Handlers (Dual-Mode: Local Server + Static Vercel/GitHub Pages) ---
function exportEventsToCSV(events) {
  const list = events && events.length > 0 ? events : state.events;
  if (!list || list.length === 0) {
    showToast("No events available to export", "info");
    return;
  }
  const headers = ["Title", "Date", "City", "Location", "Category", "Source", "B2C Score", "Priority", "Action", "URL"];
  const rows = list.map((e) => [
    `"${(e.title || "").replace(/"/g, '""')}"`,
    `"${(e.date_display || "").replace(/"/g, '""')}"`,
    `"${(e.city || "").replace(/"/g, '""')}"`,
    `"${(e.location || "").replace(/"/g, '""')}"`,
    `"${(e.category || "").replace(/"/g, '""')}"`,
    `"${(e.source || "").replace(/"/g, '""')}"`,
    `"${e.b2c_score || 0}"`,
    `"${e.b2c_priority || ""}"`,
    `"${(e.recommended_action || "").replace(/"/g, '""')}"`,
    `"${e.url || ""}"`
  ]);

  const csvContent = "\uFEFF" + [headers.join(","), ...rows.map((r) => r.join(","))].join("\r\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `aiesec_tanta_events_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

async function handleSyncSheets() {
  btnSyncSheets.disabled = true;
  showToast("Preparing Google Sheets pipeline data...", "info");

  try {
    let syncedOnServer = false;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);
      const res = await fetch("/api/sync-sheets", { method: "POST", signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "synced") {
          syncedOnServer = true;
          showToast(`Synced ${data.rows_synced} events to Google Sheets!`, "success");
        }
      }
    } catch {
      // Backend not running (static deployment)
    }

    if (!syncedOnServer) {
      exportEventsToCSV(state.events);
      showToast(`Exported ${state.events.length} events as CSV for Google Sheets!`, "success");
    }
  } catch (err) {
    exportEventsToCSV(state.events);
    showToast("Downloaded pipeline CSV for Google Sheets", "info");
  } finally {
    btnSyncSheets.disabled = false;
  }
}

async function handleSendEmail() {
  btnSendEmail.disabled = true;
  showToast("Compiling weekly B2C briefing...", "info");

  try {
    let sentOnServer = false;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);
      const res = await fetch("/api/send-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "sent") {
          sentOnServer = true;
          showToast(`Digest sent to ${data.recipients?.length || 1} recipients!`, "success");
        }
      }
    } catch {
      // Backend not running (static deployment)
    }

    if (!sentOnServer) {
      const top5 = state.events.slice(0, 5);
      const subject = `AIESEC in Tanta - B2C Weekly Event Radar Briefing (${new Date().toLocaleDateString("en-GB")})`;
      let body = `Dear AIESEC in Tanta Executive Board & B2C Team,\n\nHere is your high-priority event intelligence briefing for this week:\n\n`;
      top5.forEach((e, idx) => {
        body += `${idx + 1}. ${e.title} (${e.city})\n   • Date: ${e.date_display || "TBA"}\n   • Score: ${e.b2c_score?.toFixed(1) || "8.0"} (${e.b2c_priority || "HIGH"})\n   • Strategic Action: ${e.recommended_action || "Deploy youth booth"}\n   • Link: ${e.url}\n\n`;
      });
      body += `Best regards,\nB2C Business Development Team\nAIESEC in Egypt (LC Tanta)\nhttps://aiesec.org.eg`;

      const mailto = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      window.open(mailto, "_blank");
      showToast("Opened mail client with LC Tanta weekly briefing draft!", "success");
    }
  } catch (err) {
    showToast("Email briefing compiled", "info");
  } finally {
    btnSendEmail.disabled = false;
  }
}

async function handleScrapeNow() {
  btnScrapeNow.disabled = true;
  if (scrapeIcon) scrapeIcon.classList.add("animate-spin");
  showToast("Checking live radar feed across Egypt...", "info");

  try {
    let triggeredBackend = false;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      const res = await fetch("/api/scrape-now", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city: state.city }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        triggeredBackend = true;
        showToast(`Scrape complete! Discovered ${data.events_count} events.`, "success");
        await fetchEvents();
      }
    } catch {
      // Backend offline or running statically on Vercel / GitHub Pages
    }

    if (!triggeredBackend) {
      // Resilient static data reload: invalidate cache and reload latest static dataset
      rawEventsCache = null;
      await fetchEvents();
      showToast("Radar dataset refreshed! (Automated bot scrapes daily at 5 AM Cairo)", "success");
    }
  } catch (err) {
    showToast("Radar feed refreshed with latest dataset", "info");
  } finally {
    setTimeout(() => {
      btnScrapeNow.disabled = false;
      if (scrapeIcon) scrapeIcon.classList.remove("animate-spin");
    }, 600);
  }
}

// --- Toast Feedback with Smooth Physics ---
let toastTimeout = null;
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toast-message");
  const icon = document.getElementById("toast-icon");
  if (!toast || !msg) return;

  msg.innerText = message;
  toast.classList.remove("opacity-0", "pointer-events-none");

  if (icon) {
    if (type === "success") icon.className = "w-4 h-4 text-emerald-400 shrink-0";
    else if (type === "error") icon.className = "w-4 h-4 text-[#FF4D36] shrink-0";
    else icon.className = "w-4 h-4 text-[#00E5FF] shrink-0";
  }

  if (typeof gsap !== "undefined") {
    gsap.fromTo(toast,
      { y: -12, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.3, ease: "power2.out" }
    );
  }

  if (toastTimeout) clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    if (typeof gsap !== "undefined") {
      gsap.to(toast, {
        y: -12,
        opacity: 0,
        duration: 0.25,
        ease: "power2.in",
        onComplete: () => {
          toast.classList.add("opacity-0", "pointer-events-none");
        }
      });
    } else {
      toast.classList.add("opacity-0", "pointer-events-none");
    }
  }, 3200);
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

