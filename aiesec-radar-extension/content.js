/**
 * Content Script: Extracts live rendered Facebook Events and Instagram posts.
 */

function isBadTitle(title) {
  if (!title || typeof title !== "string") return true;
  const t = title.trim();
  if (t.length < 4) return true;
  const lower = t.toLowerCase();
  if (/^(interested|going|share|invite|save|details|rsvp|view event|مهتم|يحضر|مشاركة|حفظ|تسجيل)$/i.test(lower)) return true;
  if (/\d+(\.\d+)?[KM]?\s*(interested|going|went|مهتم|يحضر)/i.test(lower)) return true;
  if (/(interested|going|مهتم|يحضر)\s*[·•|-]\s*\d+/i.test(lower)) return true;
  if (/^\d+\s*(interested|going|went)/i.test(lower)) return true;
  if (["facebook event", "null", "undefined", "none", "event", "events", "imported live event"].includes(lower)) return true;
  if (/^(happening now|upcoming|today|tomorrow)/i.test(lower)) return true;
  if (/^[a-z]{3},\s+[a-z]{3}\s+\d{1,2}/i.test(lower)) return true;
  return false;
}

function cleanEventTitleFromDesc(badTitle, desc = "", location = "", url = "") {
  if (!isBadTitle(badTitle)) return badTitle.trim();

  // 1. Check if Facebook URL contains a named event slug
  if (url && url.includes("facebook.com/events/")) {
    try {
      const parts = url.split("facebook.com/events/")[1].split(/[/?#]/).filter(Boolean);
      for (const part of parts) {
        if (isNaN(part) && part.length > 5 && !part.startsWith("explore") && !part.startsWith("search")) {
          const decoded = decodeURIComponent(part).replace(/[-_]+/g, " ").replace(/\b\w/g, l => l.toUpperCase()).trim();
          if (!isBadTitle(decoded)) return decoded;
        }
      }
    } catch (e) {}
  }

  if (!desc || typeof desc !== "string" || desc.trim().length < 4) {
    return "Facebook Community Event";
  }

  let text = desc.trim();
  text = text.replace(/\d+(\.\d+)?[KM]?\s*(interested|going|went|مهتم|يحضر)(\s*[·•|-]\s*\d+(\.\d+)?[KM]?\s*(going|interested)?)?/gi, "");
  text = text.replace(/\b(interested|going|share|invite|save|مهتم|يحضر|مشاركة|حفظ)\b/gi, "");
  text = text.replace(/\.{3,}$/, "").trim();
  text = text.replace(/^(happening now|upcoming|today|tomorrow)\s*/gi, "");
  text = text.replace(/^[a-z]{3},\s+[a-z]{3}\s+\d{1,2}(\s*-\s*([a-z]{3}\s+)?\d{1,2})?(\s+at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)?\s*/gi, "");
  text = text.replace(/^[a-z]{3},\s+\d{1,2}\s+[a-z]{3}(\s*-\s*\d{1,2}\s+[a-z]{3})?(\s+at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)?\s*/gi, "");

  if (location && location.toLowerCase().trim() !== "egypt" && location.toLowerCase().trim() !== "cairo") {
    const locClean = location.trim();
    const esc = locClean.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    text = text.replace(new RegExp("\\s*" + esc + ".*$", "i"), "");
  }

  const venueRegex = /\s+(The GrEEK Campus|Hilton\s+[A-Za-z\s]+|Intercontinental\s+[A-Za-z\s]+|EG Intercontinental\s+[A-Za-z\s]+|Four Seasons\s+[A-Za-z\s]+|Marriott\s+[A-Za-z\s]+|Soham Yoga\s+[A-Za-z0-9\s,]+).*$/i;
  text = text.replace(venueRegex, "");

  let cleaned = text.replace(/^[\s\-·•|,:\t\r\n]+|[\s\-·•|,:\t\r\n]+$/g, "");
  if (cleaned.length >= 4 && !isBadTitle(cleaned)) {
    return cleaned;
  }
  return "Facebook Community Event";
}

function extractFacebookEvents() {
  const events = [];
  const eventMap = new Map();
  const eventLinks = Array.from(document.querySelectorAll('a[href*="/events/"]'));

  eventLinks.forEach(link => {
    const href = link.href;
    const match = href.match(/\/events\/(\d+)/);
    if (!match) return;
    const eventId = match[1];
    if (!eventMap.has(eventId)) {
      eventMap.set(eventId, []);
    }
    eventMap.get(eventId).push(link);
  });

  eventMap.forEach((links, eventId) => {
    const primaryLink = links[0];
    const container = primaryLink.closest('div[role="article"]') ||
                      primaryLink.closest('div[role="listitem"]') ||
                      primaryLink.closest('div[role="feed"] > div') ||
                      primaryLink.parentElement;
    const rawText = container ? container.innerText : primaryLink.innerText;
    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l.length > 0);

    let date = "Upcoming";
    let location = "Egypt";
    let title = "";

    // 1. Find heading element inside container if exists
    if (container) {
      const headingEl = container.querySelector('[role="heading"], h1, h2, h3, h4');
      if (headingEl && !isBadTitle(headingEl.innerText)) {
        title = headingEl.innerText.trim();
      }
    }

    // 2. Look for best link text across all event links
    if (!title) {
      for (const l of links) {
        const txt = l.innerText.trim();
        if (!isBadTitle(txt)) {
          title = txt;
          break;
        }
      }
    }

    // 3. Parse lines for date, location, and potential title
    lines.forEach(line => {
      if (/\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|mon|tue|wed|thu|fri|sat|sun|today|tomorrow|am|pm)\b/i.test(line)) {
        if (date === "Upcoming") date = line;
      } else if (/\b(cairo|alexandria|tanta|mansoura|giza|assiut|hall|center|centre|hotel|campus|university)\b/i.test(line)) {
        if (location === "Egypt") location = line;
      } else if (!title && !isBadTitle(line)) {
        title = line;
      }
    });

    // 4. Sanitize title from description if still bad or missing
    if (isBadTitle(title)) {
      title = cleanEventTitleFromDesc(title, rawText, location, `https://www.facebook.com/events/${eventId}/`);
    }

    // Check for image
    let img = "";
    if (container) {
      const imgEl = container.querySelector('img[src*="fbcdn"]');
      if (imgEl) img = imgEl.src;
    }

    events.push({
      event_id: "fb_ext_" + eventId,
      url: `https://www.facebook.com/events/${eventId}/`,
      title: title || "Facebook Community Event",
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
      const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
      let title = "";
      for (const line of lines) {
        if (!isBadTitle(line)) {
          title = line;
          break;
        }
      }
      events.push({
        event_id: "ig_ext_" + Math.random().toString(36).substr(2, 9),
        url: postUrl,
        title: title || "Instagram Community Event",
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
