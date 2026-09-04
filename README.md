# AIESEC Egypt B2C Event Radar & Command Center

An enterprise-grade, intelligent event scraping, outreach, and synchronization engine built specifically for **AIESEC B2C teams in Egypt**. It continuously tracks major event platforms and social media, filters events for the **next 6 months**, scores them for **student recruitment & partnership opportunities**, detects **campus calendar clashes**, and provides an **interactive web dashboard** with an **automated pitch generator** and **Google Sheets sync**.

---

## What's New in Version 2.0

1. **Interactive Web Dashboard & Command Center:**
   - Official **AIESEC Color Palette** (AIESEC Blue `#037EF3`, Navy `#0A2540`, Coral `#F85A40`).
   - Dynamic sorting from **Highest Score to Lowest**, Soonest Date, and Multi-Category filters.
   - 1-Click buttons: *Scrape Now*, *Sync Google Sheets*, *Send Email Digest*, *Export Excel/CSV*.
   - **Accessible to Anyone with the Link:** Shareable across your local network or via public instant URL with zero installation!
2. **Automated Partnership & PR Pitch Generator (Interactive Modal):**
   - Click *"Pitch Event"* on any card.
   - Enter your name, AIESEC email (`@aiesec.net`), phone number, and choose between:
     - **Event Collaboration:** Physical booth booking, flyer distribution, speaking slot, youth workshop co-hosting.
     - **PR & Media Collaboration:** Social media cross-promotion, student network blast, co-marketing.
   - Generates a customized, formal, high-converting outreach email ready to copy or open in your email client!
3. **Campus Calendar & Conflict Radar:**
   - Visual monthly/weekly calendar highlighting event density across Egyptian universities (AUC, GUC, Cairo Univ, Ain Shams, Alex Univ).
   - Flags **Weekend Clashes** when multiple major student events compete on the same date.
4. **Parallel Student Org & Partner Tracker:**
   - Auto-detects and tags events organized by parallel youth initiatives in Egypt: **IEEE, Enactus, Hult Prize, GDG, Toastmasters, TEDx, Rotaract**.
5. **Automated AIESEC Email Notifications:**
   - Sends beautiful HTML digest emails with score ranking and direct links for events with Score $\ge 8.5$.
6. **Social Media Scraper & Dual-Tier Caption Analyzer:**
   - Ingests public event announcement feeds on Instagram and Facebook.
   - Analyzes captions in **Arabic & English** using NLP patterns and optional **Gemini 2.5 Flash AI** multimodal intelligence.

---

## Quick Start

### 1. Launch the Web Dashboard
Open PowerShell or Command Prompt in the project folder:

```powershell
cd "C:\Users\User™\.gemini\antigravity\scratch\aiesec-event-scraper"
.\.venv\Scripts\activate

# Start the Web Dashboard
python -m aiesec_scraper.cli dashboard
```

Open your browser at **`http://localhost:8000`**.

#### How to Share with Anyone on Your Team:
* **Option A (Same Wi-Fi / Local Network):**  
  Look at the terminal output when the dashboard starts—it prints your network address (e.g. `http://192.168.1.X:8000`). Anyone connected to the same Wi-Fi can open that link on their phone or laptop!
* **Option B (Public Link Across the Internet):**  
  Open a second terminal window and run:
  ```powershell
  npx cloudflared tunnel --url http://localhost:8000
  ```
  *(This instantly gives you a free, secure `https://...trycloudflare.com` public URL that anyone in the world can open on their phone!)*

---

## Command-Line Usage

### 1. On-Demand Scrape
```powershell
# Scrape all of Egypt
python -m aiesec_scraper.cli run --country egypt

# Scrape a specific city dynamically
python -m aiesec_scraper.cli run --city alexandria
python -m aiesec_scraper.cli run --city cairo
```

### 2. Send Email Digest on Demand
```powershell
# Send digest to default configured recipients
python -m aiesec_scraper.cli notify

# Send to specific team member emails
python -m aiesec_scraper.cli notify --to "nour@aiesec.net,karim@aiesec.net"
```

### 3. Automated 3-Day Refreshes
```powershell
# Continuous background runner
python -m aiesec_scraper.cli schedule --interval-days 3

# Or install as a Windows Task Scheduler job (Set & Forget)
python -m aiesec_scraper.cli setup-task
```

---

## Configuration & Credentials

### 1. Google Sheets Integration
1. Place your Google Cloud Service Account JSON file as `service_account.json` in the project root.
2. Create a Google Sheet named `AIESEC Egypt B2C Event Radar`.
3. Share the Google Sheet with your service account email as **Editor**.

### 2. Email Notifications (SMTP)
Copy `.env.example` to `.env` and fill in your details:
```env
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
NOTIFICATION_RECIPIENTS=b2c.egypt@aiesec.net
```
*(For Gmail, generate a 16-character App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords))*

### 3. Optional AI Multimodal Caption & Flyer Extraction
In `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
```
When configured, complex social media flyer images and long post captions will be deeply understood using Gemini Flash.

---

## Project Structure

```
aiesec-event-scraper/
├── pyproject.toml              # Dependencies & entrypoints
├── config.yaml                 # Configurable keywords, cities, date window, SMTP settings
├── .env.example                # Environment variables template
├── README.md                   # Complete documentation
├── service_account.json        # Google Cloud Service Account key
├── run_scheduled_scrape.bat    # Windows Task Scheduler automation script
├── data/                       # Auto-exported files
│   ├── aiesec_egypt_events_latest.xlsx
│   ├── aiesec_egypt_events_latest.csv
│   └── latest_email_preview.html
└── aiesec_scraper/
    ├── models.py               # Standardized EventRecord dataclass
    ├── scorers.py              # B2C scoring & parallel student org detector
    ├── pipeline.py             # Deduplication, 6-month window, and clash detector
    ├── scrapers/
    │   ├── eventbrite.py       # Eventbrite scraper (JSON-LD + HTML)
    │   ├── allevents.py        # AllEvents.in scraper
    │   ├── meetup.py           # Meetup scraper
    │   ├── tentimes.py         # 10times scraper
    │   └── social.py           # Instagram & Facebook event announcements
    ├── analyzers/
    │   ├── caption_analyzer.py # Dual-tier Arabic/English NLP + Gemini AI
    │   └── pitch_generator.py  # AIESEC partnership & PR outreach email generator
    ├── notifications/
    │   ├── email_service.py    # SMTP email dispatcher
    │   └── templates/
    │       └── digest.html     # Responsive AIESEC HTML email template
    ├── web/
    │   ├── app.py              # FastAPI server (REST API)
    │   └── static/
    │       ├── index.html      # Responsive Single Page Dashboard
    │       ├── app.js          # Interactive frontend & pitch modal
    │       └── style.css       # Custom AIESEC branding styles
    ├── scheduler.py            # Recurring 3-day runner
    └── cli.py                  # Full-featured command-line interface
```
"# aiesec-event-radar" 
