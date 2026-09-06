/**
 * Content Script: Extracts live rendered Facebook Events and Instagram posts.
 */

function extractFacebookEvents() {
  const events = [];
  const seenIds = new Set();
  const eventLinks = Array.from(document.querySelectorAll('a[href*="/events/"]'));

  eventLinks.forEach(link => {
    const href = link.href;
    const match = href.match(/\/events\/(\d+)/);
    if (!match) return;
    const eventId = match[1];
    if (seenIds.has(eventId)) return;
    seenIds.add(eventId);

    const container = link.closest('div[role="article"]') || link.closest('div[role="listitem"]') || link.closest('div[role="feed"] > div') || link.parentElement;
    const rawText = container ? container.innerText : link.innerText;
    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    let title = link.innerText.trim();
    let date = "Upcoming";
    let location = "Egypt";

    lines.forEach(line => {
      if (/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|mon|tue|wed|thu|fri|sat|sun|today|tomorrow|am|pm)\b/i.test(line)) {
        date = line;
      } else if (/\b(cairo|alexandria|tanta|mansoura|giza|assiut|hall|center|centre|hotel|campus|university)\b/i.test(line)) {
        location = line;
      } else if (line.length > 8 && line !== lines[0] && title === link.innerText.trim()) {
        title = line;
      }
    });

    // Check for image
    let img = "";
    if (container) {
      const imgEl = container.querySelector('img[src*="fbcdn"]');
      if (imgEl) img = imgEl.src;
    }

    events.push({
      event_id: "fb_ext_" + eventId,
      url: `https://www.facebook.com/events/${eventId}/`,
      title: title || "Facebook Event",
      date_display: date,
      location: location,
      source: "Facebook Events",
      image_url: img,
      description: rawText.slice(0, 400),
      is_social_first: true,
      proof_url: `https://www.facebook.com/events/${eventId}/`,
      proof_type: "Live Facebook Event Announcement"
    });
  });

  return events;
}

function extractInstagramEvents() {
  const events = [];
  const articles = Array.from(document.querySelectorAll('article, div[role="presentation"]'));
  articles.forEach((art, idx) => {
    const text = art.innerText || "";
    if (/\b(event|summit|conference|workshop|webinar|hackathon|مؤتمر|ورشة|معرض)\b/i.test(text)) {
      const linkEl = art.querySelector('a[href*="/p/"]');
      const postUrl = linkEl ? linkEl.href : window.location.href;
      events.push({
        event_id: "ig_ext_" + Math.random().toString(36).substr(2, 9),
        url: postUrl,
        title: text.split('\n')[0] || "Instagram Event",
        date_display: "Upcoming",
        location: "Egypt",
        source: "Instagram Feeds",
        description: text.slice(0, 400),
        is_social_first: true,
        proof_url: postUrl,
        proof_type: "Direct Social Announcement Post"
      });
    }
  });
  return events;
}

// Message Listener from Popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extract_events") {
    let extracted = [];
    if (window.location.hostname.includes("facebook")) {
      extracted = extractFacebookEvents();
    } else if (window.location.hostname.includes("instagram")) {
      extracted = extractInstagramEvents();
    }
    sendResponse({ count: extracted.length, events: extracted, url: window.location.href });
  }
  return true;
});
