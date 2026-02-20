# 🔥 Playwright Recursive Lead Hunter v2.0

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0-blueviolet?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Language-Python-green?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/AI-Gemini-red?style=for-the-badge" alt="Gemini AI">
</p>

<p align="center">
  <strong>High-Performance Async Lead Generation Engine</strong><br>
  Powered by: Playwright + Gemini AI + DuckDuckGo
</p>

---

## 🚀 Overview

**Playwright Recursive Lead Hunter** is an enterprise-grade lead generation tool designed to automatically discover and enrich business leads from Google Maps. It combines web scraping, recursive crawling, and AI-powered analysis to extract valuable contact information including owner names, direct phone numbers, personal emails, LinkedIn profiles, and hiring status.

### Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Google Maps Scraping** | Extract business listings with phone numbers and websites |
| 🕷️ **Recursive Deep Crawling** | Intelligently explores contact, about, team, and staff pages |
| 🦆 **DuckDuckGo Integration** | Fallback email and LinkedIn search to stitch missing data |
| 🧠 **Gemini AI Classification** | Classify personal vs generic emails using AI |
| 📊 **Revenue Loss Analysis** | AI-powered analysis to identify why businesses are losing revenue |
| 🛡️ **Anti-Detection** | Stealth browser with persistent context and randomized delays |
| 💾 **RAM Management** | Auto browser recycling to keep memory usage under 1GB |
| 📈 **Real-time CSV Export** | Leads are appended instantly as they're discovered |

---

## 📋 Requirements

### System Requirements
- Python 3.8+
- Windows 10/11 or Linux
- Chrome/Chromium browser (automatically installed by Playwright)
- Internet connection

### Python Dependencies
```
playwright
```

### External Dependencies
- **gemini-cli** - Gemini AI CLI tool for AI synthesis (install separately via `npm install -g gemini-cli`)

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd leads-bot
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
```bash
playwright install chromium
```

### 4. Configure Gemini CLI
```bash
# Install Gemini CLI globally
npm install -g gemini-cli

# Or use "gemini" if you prefer
```

---

## ⚙️ Configuration

### Mission Configuration (Inside `playwright_hunter.py`)

```python
# Target cities and niches
CITIES = ["Casper", "Cheyenne", "Gillette", "Rock Springs", "Laramie"]

NICHES = {
    "Dental Clinic": 8000,
    "Dentist near me": 8000,
    "Emergency Dentist": 8000,
    # Add more niches here...
}

# Output file
OUTPUT_CSV = "unlimited_leads.csv"

# Engine tuning
BROWSER_RECYCLE_INTERVAL = 30      # Restart browser every N leads
SMART_DELAY_MIN = 5                # Min seconds between searches
SMART_DELAY_MAX = 12               # Max seconds between searches
MAX_CRAWL_DEPTH = 2                # How many sub-pages deep to crawl
MAX_SUBPAGES = 6                   # Max sub-pages per domain
```

---

## 🎯 Usage

### Basic Usage
```bash
python playwright_hunter.py
```

### Expected Output
```
╔══════════════════════════════════════════════════════════════╗
║       🔥 PLAYWRIGHT RECURSIVE LEAD HUNTER v2.0 🔥          ║
║  Targets: 5 cities × 7 niches                               ║
║  Output:  unlimited_leads.csv                               ║
╚══════════════════════════════════════════════════════════════╝

   📂 Existing leads in CSV: 0
   🟢 Browser launched with persistent context

   ================================
   🚀 MISSION: Dental Clinic in Casper
   ================================

   🗺️  Loading Maps: Dental Clinic in Casper
   📜 Scroll 1/60
   ...
```

---

## 📊 Output Data

The tool generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| Business Name | Name of the business |
| Owner Name | Owner's full name (extracted via AI) |
| Direct Mobile | Owner's personal mobile number |
| Personal Email | Owner's personal email address |
| LinkedIn Profile | Owner's LinkedIn profile URL |
| Hiring Status | Whether the business is hiring |
| Office Line | Business phone number |
| Estimated Revenue Loss | Estimated $ amount lost due to poor website |
| Loss Reason | AI-identified reason for revenue loss |
| Website | Business website URL |

---

## 🔧 How It Works

### 1. **Google Maps Discovery**
The bot searches Google Maps for businesses matching your niche + city combinations and extracts their basic info (name, phone, website).

### 2. **Recursive Website Crawling**
For each business, it deep-scans the website by following relevant links:
- `/contact` - Contact pages
- `/about` - About us pages
- `/team` - Team/staff pages
- `/meet` - Meet the team
- `/doctor` - Doctor profiles
- And more...

### 3. **Regex Extraction**
Extracts emails, phone numbers, and LinkedIn URLs from:
- Page source code
- Meta tags
- Hidden elements
- JavaScript variables

### 4. **DuckDuckGo Fallback**
If emails/LinkedIn aren't found on the website, it searches DuckDuckGo for:
- Business email addresses
- Owner LinkedIn profiles
- Hiring information

### 5. **AI Synthesis**
Gemini AI processes all collected data to:
- Classify emails as Personal vs Generic
- Identify the most likely revenue loss reason
- Synthesize all intel into structured data

---

## ⚠️ Legal Disclaimer

> **IMPORTANT**: This tool is provided for educational and research purposes only. Users are solely responsible for complying with:
> - Website Terms of Service
> - Applicable laws and regulations (CFAA, GDPR, etc.)
> - Robots.txt directives
> - Rate limiting and fair use policies

The maintainers assume no liability for any misuse of this tool.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) - Browser automation
- [Gemini AI](https://gemini.google.com/) - AI synthesis
- [DuckDuckGo](https://duckduckgo.com/) - Search API alternative

---

<p align="center">
  Made with ❤️ for lead generation automation
</p>
