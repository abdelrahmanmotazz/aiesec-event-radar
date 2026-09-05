/**
 * AIESEC in Tanta - B2C Event Radar & Command Center
 * Frontend Controller with Dynamic Telemetry & Non-AI Bespoke Aesthetics
 */

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
  activeView: "cards" // "cards" or "calendar"
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
  initMouseLighting();
  initLiveClock();
  setupEventListeners();
  fetchEvents();
  if (window.lucide) lucide.createIcons();
});

// Dynamic Ambient Cursor Lighting
function initMouseLighting() {
  window.addEventListener("mousemove", (e) => {
    const x = Math.round((e.clientX / window.innerWidth) * 100);
    const y = Math.round((e.clientY / window.innerHeight) * 100);
    document.documentElement.style.setProperty("--mouse-x", `${x}%`);
    document.documentElement.style.setProperty("--mouse-y", `${y}%`);
  });
}

// Live Cairo Time Clock
function initLiveClock() {
  const el = document.getElementById("live-clock");
  if (!el) return;
  function tick() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString("en-US", { timeZone: "Africa/Cairo", hour: "2-digit", minute: "2-digit", second: "2-digit" });
    el.innerText = `Cairo: ${timeStr}`;
  }
  tick();
  setInterval(tick, 1000);
}

function setupEventListeners() {
  // Search typing with debounce
  let searchTimeout = null;
  inputSearch.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      state.search = e.target.value.trim();
      fetchEvents();
    }, 250);
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

  const tileFlagshipRadar = document.getElementById("tile-flagship-radar");
  if (tileFlagshipRadar) {
    tileFlagshipRadar.addEventListener("click", handleFlagshipFilter);
  }

  // Priority buttons
  document.querySelectorAll(".filter-priority-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-priority-btn").forEach((b) => {
        b.className = "filter-priority-btn px-3 py-1 rounded-xl font-medium bg-[#0C1427] text-slate-300 hover:bg-[#13203C] border border-white/[0.08]";
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
          b.className = "filter-priority-btn px-3 py-1 rounded-xl font-medium bg-[#0C1427] text-slate-300 hover:bg-[#13203C] border border-white/[0.08]";
        }
      });
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

    // Update KPI Telemetry HUD
    const elTotal = document.getElementById("stat-total");
    if (elTotal) elTotal.innerText = data.metrics.total_events;
    const elHigh = document.getElementById("stat-high");
    if (elHigh) elHigh.innerText = data.metrics.high_priority;
    const elTm = document.getElementById("stat-tm-count");
    if (elTm) elTm.innerText = data.metrics.ticketsmarche_count || 49;
    const elFlagship = document.getElementById("stat-flagship-count");
    if (elFlagship) elFlagship.innerText = data.metrics.flagship_count || 10;
    const elSocial = document.getElementById("stat-social-count");
    if (elSocial) elSocial.innerText = data.metrics.social_count || 24;

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
    return `<span class="source-pill-summit px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide inline-flex items-center gap-1"><i data-lucide="sparkles" class="w-3 h-3"></i> Egypt Summit</span>`;
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

// --- Render Cards View ---
function renderCards() {
  containerCards.innerHTML = "";

  if (state.events.length === 0) {
    containerCards.innerHTML = `
      <div class="col-span-full radar-surface p-12 text-center">
        <i data-lucide="inbox" class="w-12 h-12 text-slate-500 mx-auto mb-3"></i>
        <h3 class="text-sm font-bold text-slate-200">No matching campus events found</h3>
        <p class="text-xs text-slate-400 mt-1">Try broadening your search term, switching city to 'All Egypt', or changing stream filters.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  state.events.forEach((ev) => {
    const card = document.createElement("div");
    const isHigh = ev.b2c_priority === "HIGH";
    const isFlagship = (ev.category && ev.category.toLowerCase().includes("flagship")) || ev.source.toLowerCase().includes("summit") || ev.title.toLowerCase().includes("techne") || ev.title.toLowerCase().includes("riseup");
    const isSummit = ev.source.toLowerCase().includes("summit");
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
          <div class="date-tearoff-badge shrink-0">
            <span class="date-tearoff-month">${dateBadge.month}</span>
            <span class="date-tearoff-day">${dateBadge.day}</span>
          </div>

          <div class="flex-1 min-w-0">
            <h3 class="font-extrabold text-base text-white leading-snug line-clamp-2 hover:text-[#00E5FF] transition group">
              <a href="${ev.url}" target="_blank" class="group-hover:underline underline-offset-2">${ev.title}</a>
            </h3>
            <div class="mt-1.5 space-y-1 text-xs text-slate-400">
              <div class="flex items-center gap-1.5 truncate">
                <i data-lucide="map-pin" class="w-3.5 h-3.5 text-rose-400 shrink-0"></i>
                <span class="truncate">${ev.location} • <strong class="text-slate-200">${ev.city}</strong></span>
              </div>
              <div class="flex items-center gap-1.5 text-slate-400 truncate">
                <i data-lucide="calendar" class="w-3.5 h-3.5 text-sky-400 shrink-0"></i>
                <span class="truncate">${ev.date_display || "Date TBA"}</span>
                ${ev.ticket_type ? `<span class="text-slate-500">•</span><span class="text-slate-300 font-medium">${ev.ticket_type}</span>` : ""}
              </div>
            </div>
          </div>
        </div>

        <!-- Specific Event Intelligence Briefing Box -->
        <div class="event-desc-box p-3 text-xs bg-[#080E1D]/90 border border-white/[0.08] rounded-2xl shadow-inner space-y-1">
          <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
            <span class="flex items-center gap-1.5 text-sky-400">
              <i data-lucide="file-text" class="w-3.5 h-3.5"></i> Event Intelligence Briefing
            </span>
            <span class="text-[9px] text-slate-500 font-mono font-medium tracking-tight">Granular Details</span>
          </div>
          <p class="text-slate-300 text-[11px] leading-relaxed line-clamp-3 hover:line-clamp-none transition-all duration-300 cursor-pointer" title="Click or hover to expand full briefing">
            ${ev.description || "No specific briefing available."}
          </p>
        </div>

        <!-- AIESEC Strategic Recommendation Callout Box -->
        <div class="dark-action-box p-3 text-xs">
          <div class="text-[10px] font-bold text-[#00E5FF] uppercase tracking-wider mb-1 flex items-center gap-1.5">
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
        <a href="${ev.url}" target="_blank" class="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/[0.08] border border-white/[0.09] transition active:scale-95" title="Open Event Source">
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    `;

    // Attach click for pitch button
    const pitchBtn = card.querySelector(".btn-pitch-event");
    pitchBtn.addEventListener("click", () => openPitchModal(ev));

    containerCards.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

// --- Render Calendar & Clash Heatmap ---
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
    groupBlock.className = `p-4 rounded-2xl border ${isClashDate ? "bg-amber-950/20 border-amber-500/35 shadow-[0_0_20px_rgba(245,158,11,0.12)]" : "bg-[#0A101F]/80 border-white/[0.08]"}`;

    let eventsHtml = eventList.map(e => `
      <div class="py-2.5 flex items-center justify-between border-b border-white/[0.06] last:border-0 gap-4">
        <div>
          <div class="font-bold text-xs text-white flex items-center gap-2">
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
        <h4 class="text-xs font-bold text-slate-200 flex items-center gap-2">
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

// --- Modal Logic ---
function openPitchModal(event) {
  state.activePitchEvent = event;
  pitchEventSubtitle.innerText = `Event: ${event.title} (${event.city})`;
  const briefingEl = document.getElementById("pitch-event-desc-text");
  if (briefingEl) {
    briefingEl.innerText = event.description || "No specific briefing available for this event.";
  }
  pitchOutputBox.classList.add("hidden");
  pitchModal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function closePitchModal() {
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
      showToast("Sheets sync skipped (Credentials not set)", "info");
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

// --- Toast Feedback ---
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const msg = document.getElementById("toast-message");
  const icon = document.getElementById("toast-icon");

  msg.innerText = message;
  toast.classList.remove("translate-y-20", "opacity-0", "pointer-events-none");

  setTimeout(() => {
    toast.classList.add("translate-y-20", "opacity-0", "pointer-events-none");
  }, 3500);
}
