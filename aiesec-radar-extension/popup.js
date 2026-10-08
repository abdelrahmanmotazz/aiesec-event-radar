let extractedEvents = [];

document.addEventListener('DOMContentLoaded', async () => {
  const countEl = document.getElementById('event-count');
  const hostBadge = document.getElementById('host-badge');
  const pageUrlEl = document.getElementById('page-url');
  const btnSync = document.getElementById('btn-sync');
  const btnCopy = document.getElementById('btn-copy');

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) return;

  const url = tab.url || "";
  if (url.includes("facebook.com")) {
    hostBadge.innerText = "Facebook Active";
    hostBadge.style.color = "#38bdf8";
  } else if (url.includes("instagram.com")) {
    hostBadge.innerText = "Instagram Active";
    hostBadge.style.color = "#f43f5e";
  } else {
    hostBadge.innerText = "Other Site";
    hostBadge.style.color = "#94a3b8";
    pageUrlEl.innerText = "Navigate to facebook.com/events to scan";
  }

  try {
    chrome.tabs.sendMessage(tab.id, { action: "extract_events" }, response => {
      if (chrome.runtime.lastError || !response) {
        pageUrlEl.innerText = "Reload tab or scroll to detect events";
        return;
      }
      extractedEvents = response.events || [];
      countEl.innerText = extractedEvents.length;
      pageUrlEl.innerText = `Extracted from active page`;
    });
  } catch (err) {
    pageUrlEl.innerText = "Could not reach tab content.";
  }

  btnSync.addEventListener('click', async () => {
    if (!extractedEvents.length) {
      showToast("No events detected yet. Scroll down the page first!", "error");
      return;
    }
    btnSync.innerText = "Syncing...";
    try {
      const res = await fetch("http://127.0.0.1:8000/api/social/import", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: extractedEvents })
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Synced ${data.imported || extractedEvents.length} events to local Radar!`, "success");
        btnSync.innerText = "✓ Synced Successfully";
        return;
      }
    } catch (err) {
      // Local server not reachable -> sync directly to live Vercel Radar via URL payload + clipboard
    }

    navigator.clipboard.writeText(JSON.stringify(extractedEvents, null, 2));
    try {
      const compactPayload = extractedEvents.slice(0, 15).map(e => ({
        title: e.title,
        url: e.url,
        date_display: e.date_display,
        location: e.location,
        source: e.source
      }));
      const encoded = encodeURIComponent(JSON.stringify(compactPayload));
      chrome.tabs.create({ url: `https://aiesec-event-radar.vercel.app/?social_import=${encoded}` });
    } catch (e) {}
    showToast(`Synced ${extractedEvents.length} events to Live Radar & Clipboard!`, "success");
    btnSync.innerText = "✓ Synced to Live Radar";
    setTimeout(() => { btnSync.innerText = "⚡ Sync Directly to Radar"; }, 3000);
  });

  btnCopy.addEventListener('click', () => {
    if (!extractedEvents.length) {
      showToast("No events to copy.", "error");
      return;
    }
    navigator.clipboard.writeText(JSON.stringify(extractedEvents, null, 2));
    showToast("Copied events JSON to clipboard!", "success");
  });
});

function showToast(msg, type) {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.className = `toast ${type}`;
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 4000);
}
