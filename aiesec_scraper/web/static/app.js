/**
 * AIESEC Egypt B2C Event Radar - Frontend Controller
 */

let state = {
  events: [],
  sort: "score_desc",
  priority: "all",
  city: "all",
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
const selectCity = document.getElementById("select-city");
const checkPartnersOnly = document.getElementById("check-partners-only");
const checkClashesOnly = document.getElementById("check-clashes-only");
const btnViewCards = document.getElementById("btn-view-cards");
const btnViewCalendar = document.getElementById("btn-view-calendar");

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
  setupEventListeners();
  fetchEvents();
});

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

  // Priority buttons
  document.querySelectorAll(".filter-priority-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-priority-btn").forEach((b) => {
        b.className = "filter-priority-btn px-2.5 py-1 rounded-lg font-medium bg-slate-100 text-slate-700 hover:bg-slate-200";
      });
      btn.className = "filter-priority-btn px-2.5 py-1 rounded-lg font-medium bg-[#037EF3] text-white";
      state.priority = btn.dataset.priority;
      fetchEvents();
    });
  });

  // Checkboxes
  checkPartnersOnly.addEventListener("change", (e) => {
    state.partnersOnly = e.target.checked;
    fetchEvents();
  });

  checkClashesOnly.addEventListener("change", (e) => {
    state.clashesOnly = e.target.checked;
    fetchEvents();
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

  // Top Action Buttons
  btnSyncSheets.addEventListener("click", handleSyncSheets);
  btnSendEmail.addEventListener("click", handleSendEmail);
  btnScrapeNow.addEventListener("click", handleScrapeNow);
}

function switchView(view) {
  state.activeView = view;
  if (view === "cards") {
    containerCards.classList.remove("hidden");
    containerCalendar.classList.add("hidden");
    btnViewCards.className = "px-3 py-1 text-xs font-semibold rounded-md bg-white text-[#037EF3] shadow-sm flex items-center gap-1";
    btnViewCalendar.className = "px-3 py-1 text-xs font-semibold rounded-md text-slate-600 hover:text-slate-900 flex items-center gap-1";
  } else {
    containerCards.classList.add("hidden");
    containerCalendar.classList.remove("hidden");
    btnViewCalendar.className = "px-3 py-1 text-xs font-semibold rounded-md bg-white text-[#037EF3] shadow-sm flex items-center gap-1";
    btnViewCards.className = "px-3 py-1 text-xs font-semibold rounded-md text-slate-600 hover:text-slate-900 flex items-center gap-1";
    renderCalendarView();
  }
  lucide.createIcons();
}

// --- Fetch API ---
async function fetchEvents() {
  const params = new URLSearchParams({
    sort: state.sort,
    priority: state.priority,
    city: state.city,
    search: state.search,
    partner_only: state.partnersOnly,
    clash_only: state.clashesOnly
  });

  try {
    const res = await fetch(`/api/events?${params}`);
    const data = await res.json();
    state.events = data.events;

    // Update KPI cards
    document.getElementById("stat-total").innerText = data.metrics.total_events;
    document.getElementById("stat-high").innerText = data.metrics.high_priority;
    document.getElementById("stat-partners").innerText = data.metrics.partner_orgs;
    document.getElementById("stat-clashes").innerText = data.metrics.clashes;

    renderCards();
    if (state.activeView === "calendar") {
      renderCalendarView();
    }
  } catch (err) {
    console.error("Failed to fetch events:", err);
    showToast("Failed to connect to API server", "error");
  }
}

// --- Render Cards View ---
function renderCards() {
  containerCards.innerHTML = "";

  if (state.events.length === 0) {
    containerCards.innerHTML = `
      <div class="col-span-full bg-white p-12 rounded-xl text-center border border-slate-200">
        <i data-lucide="inbox" class="w-10 h-10 text-slate-300 mx-auto mb-2"></i>
        <h3 class="text-sm font-bold text-slate-700">No matching events found</h3>
        <p class="text-xs text-slate-500 mt-1">Try broadening your search or switching filters.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  state.events.forEach((ev) => {
    const card = document.createElement("div");
    const isHigh = ev.b2c_priority === "HIGH";
    const hasPartner = !!ev.parallel_org;
    const hasClash = ev.clash_warning;

    card.className = `aiesec-card p-5 flex flex-col justify-between ${isHigh ? "card-high-priority" : (hasPartner ? "card-partner-org" : "")}`;

    // Priority badge class
    const badgeClass = isHigh ? "badge-score-high" : (ev.b2c_priority === "MEDIUM" ? "badge-score-med" : "badge-score-low");

    card.innerHTML = `
      <div class="space-y-3">
        <!-- Top Tags Bar -->
        <div class="flex items-center justify-between gap-2">
          <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold ${badgeClass}">
            ★ ${ev.b2c_score.toFixed(1)} ${ev.b2c_priority}
          </span>
          <div class="flex items-center gap-1.5 flex-wrap justify-end">
            ${hasPartner ? `<span class="badge-partner px-2 py-0.5 rounded-full text-[10px] font-bold">${ev.parallel_org}</span>` : ""}
            ${hasClash ? `<span class="badge-clash px-2 py-0.5 rounded-full text-[10px] font-bold">⚠️ Weekend Clash</span>` : ""}
            <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">${ev.source}</span>
          </div>
        </div>

        <!-- Title & Location -->
        <div>
          <h3 class="font-bold text-sm text-slate-900 leading-snug line-clamp-2 hover:text-[#037EF3] transition">
            <a href="${ev.url}" target="_blank">${ev.title}</a>
          </h3>
          <div class="mt-2 space-y-1 text-xs text-slate-500">
            <div class="flex items-center gap-1.5">
              <i data-lucide="calendar" class="w-3.5 h-3.5 text-slate-400 shrink-0"></i>
              <span class="truncate">${ev.date_display || "Date TBA"}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <i data-lucide="map-pin" class="w-3.5 h-3.5 text-slate-400 shrink-0"></i>
              <span class="truncate">${ev.location} • <strong class="text-slate-700">${ev.city}</strong></span>
            </div>
            ${ev.organizer && ev.organizer !== "Unknown" ? `
            <div class="flex items-center gap-1.5">
              <i data-lucide="building" class="w-3.5 h-3.5 text-slate-400 shrink-0"></i>
              <span class="truncate">${ev.organizer}</span>
            </div>` : ""}
          </div>
        </div>

        <!-- AIESEC Recommendation Box -->
        <div class="bg-slate-50 border border-slate-200/70 p-2.5 rounded-lg text-xs">
          <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Recommended B2C Action</div>
          <div class="font-semibold text-slate-800 flex items-start gap-1">
            <span class="text-[#037EF3]">→</span>
            <span>${ev.recommended_action}</span>
          </div>
        </div>
      </div>

      <!-- Action Footer -->
      <div class="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between gap-2">
        <button class="btn-pitch-event flex-1 py-1.5 px-3 bg-[#037EF3]/10 hover:bg-[#037EF3] text-[#037EF3] hover:text-white rounded-lg text-xs font-semibold transition flex items-center justify-center gap-1.5"
                data-event-id="${ev.event_id}">
          <i data-lucide="mail" class="w-3.5 h-3.5"></i> Pitch Event
        </button>
        <a href="${ev.url}" target="_blank" class="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition" title="View Source">
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    `;

    // Attach click for pitch button
    const pitchBtn = card.querySelector(".btn-pitch-event");
    pitchBtn.addEventListener("click", () => openPitchModal(ev));

    containerCards.appendChild(card);
  });

  lucide.createIcons();
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
    groupBlock.className = `p-4 rounded-xl border ${isClashDate ? "bg-amber-50/40 border-amber-200" : "bg-white border-slate-200"}`;

    let eventsHtml = eventList.map(e => `
      <div class="py-2 flex items-center justify-between border-b border-slate-100 last:border-0 gap-4">
        <div>
          <div class="font-bold text-xs text-slate-800 flex items-center gap-2">
            <span>${e.title}</span>
            <span class="text-[10px] bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-bold">${e.b2c_score.toFixed(1)}</span>
          </div>
          <div class="text-[11px] text-slate-500">${e.location} (${e.city}) • <em>${e.recommended_action}</em></div>
        </div>
        <button class="text-xs bg-[#037EF3] text-white px-2.5 py-1 rounded font-semibold shrink-0 hover:bg-blue-600 transition" onclick="openPitchById('${e.event_id}')">
          Pitch
        </button>
      </div>
    `).join("");

    groupBlock.innerHTML = `
      <div class="flex items-center justify-between mb-2">
        <h4 class="text-xs font-bold text-slate-900 flex items-center gap-2">
          <i data-lucide="calendar" class="w-4 h-4 text-slate-400"></i>
          <span>${dateStr}</span>
        </h4>
        ${isClashDate ? `<span class="badge-clash text-[10px] font-bold px-2 py-0.5 rounded-full">⚠️ Clash: ${eventList.length} Events Competing</span>` : ""}
      </div>
      <div class="divide-y divide-slate-100">
        ${eventsHtml}
      </div>
    `;

    calendarTimeline.appendChild(groupBlock);
  });

  lucide.createIcons();
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
  pitchOutputBox.classList.add("hidden");
  pitchModal.classList.remove("hidden");
  lucide.createIcons();
}

function closePitchModal() {
  pitchModal.classList.add("hidden");
  state.activePitchEvent = null;
}

async function handleGeneratePitch() {
  if (!state.activePitchEvent) return;

  const memberName = document.getElementById("pitch-name").value.trim() || "AIESEC Member";
  const memberEmail = document.getElementById("pitch-email").value.trim() || "b2c@aiesec.net";
  const memberPhone = document.getElementById("pitch-phone").value.trim() || "+20 1X XXXX XXXX";
  const purpose = document.getElementById("pitch-purpose").value;

  btnGeneratePitch.disabled = true;
  btnGeneratePitch.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating Pitch...`;
  lucide.createIcons();

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
    btnOpenMail.href = data.mailto_url;

    pitchOutputBox.classList.remove("hidden");
  } catch (err) {
    showToast("Failed to generate pitch proposal", "error");
  } finally {
    btnGeneratePitch.disabled = false;
    btnGeneratePitch.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4"></i> Generate Pitch Email`;
    lucide.createIcons();
  }
}

function handleCopyPitch() {
  const text = `Subject: ${pitchSubject.value}\n\n${pitchBody.value}`;
  navigator.clipboard.writeText(text).then(() => {
    document.getElementById("copy-text").innerText = "Copied!";
    setTimeout(() => {
      document.getElementById("copy-text").innerText = "Copy to Clipboard";
    }, 2000);
    showToast("Email proposal copied to clipboard!");
  });
}

// --- Top Actions ---
async function handleSyncSheets() {
  btnSyncSheets.disabled = true;
  showToast("Syncing with Google Sheets...", "info");

  try {
    const res = await fetch("/api/sync-sheets", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast("Google Sheet updated successfully!");
    } else {
      showToast(data.message || "Google Sheets sync requires service_account.json", "warning");
    }
  } catch (err) {
    showToast("Error syncing Google Sheets", "error");
  } finally {
    btnSyncSheets.disabled = false;
  }
}

async function handleSendEmail() {
  btnSendEmail.disabled = true;
  showToast("Dispatching AIESEC digest email...", "info");

  try {
    const res = await fetch("/api/send-email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Email digest sent to ${data.recipients.join(", ")}`);
    } else {
      showToast(`Saved preview to ${data.preview_file} (configure SMTP in .env)`, "warning");
    }
  } catch (err) {
    showToast("Error dispatching email", "error");
  } finally {
    btnSendEmail.disabled = false;
  }
}

async function handleScrapeNow() {
  btnScrapeNow.disabled = true;
  scrapeIcon.classList.add("animate-spin");
  showToast("Running nationwide scrape... This takes ~15 seconds", "info");

  try {
    const res = await fetch("/api/scrape", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ country: "egypt" })
    });
    const data = await res.json();
    showToast(data.message || "Scrape completed successfully!");
    await fetchEvents();
  } catch (err) {
    showToast("Error running scrape pipeline", "error");
  } finally {
    btnScrapeNow.disabled = false;
    scrapeIcon.classList.remove("animate-spin");
  }
}

// --- Toast Notification Helper ---
function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toast-message");
  toastMsg.innerText = message;

  toast.classList.remove("translate-y-20", "opacity-0");
  toast.classList.add("translate-y-0", "opacity-100");

  setTimeout(() => {
    toast.classList.add("translate-y-20", "opacity-0");
    toast.classList.remove("translate-y-0", "opacity-100");
  }, 4000);
}
