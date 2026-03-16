"""
╔══════════════════════════════════════════════════════════════╗
║       🔥 PLAYWRIGHT RECURSIVE LEAD HUNTER v2.0 🔥            ║
║  High-Performance Async Lead Generation Engine               ║
║  Powered by: Playwright + Gemini AI + DuckDuckGo             ║
╚══════════════════════════════════════════════════════════════╝

Upgrade from selenium_scout.py:
  ✅ Async Playwright (RAM-efficient)
  ✅ Recursive deep-scan crawler (Contact, About, Team, etc.)
  ✅ Regex extraction for emails & LinkedIn URLs
  ✅ DuckDuckGo "stitching" fallback for missing emails
  ✅ Persistent browser context (cookies, anti-detection)
  ✅ Smart delay (15-30s randomized)
  ✅ Auto browser restart every 15 leads (RAM < 1GB)
  ✅ Gemini AI synthesis (email classification + loss reason)
"""

import os
import re
import csv
import json
import asyncio
import random
import subprocess
import traceback
from datetime import datetime
from urllib.parse import urljoin, urlparse

# ==========================================
# 🔥 MISSION CONFIGURATION
# ==========================================

GEMINI_CMD = "gemini-cli"  # Change to "gemini" if needed

CITIES = ["Casper", "Cheyenne", "Gillette", "Rock Springs", "Laramie"]

NICHES = {
    "Dental Clinic": 8000,
}

OUTPUT_CSV = "unlimited_leads.csv"

# ==========================================
# ⚙️  ENGINE TUNING
# ==========================================

BROWSER_RECYCLE_INTERVAL = 15      # Restart browser every N leads
SMART_DELAY_MIN = 15               # Min seconds between searches
SMART_DELAY_MAX = 30               # Max seconds between searches
PAGE_LOAD_TIMEOUT = 20_000         # ms — Playwright timeout
MAX_CRAWL_DEPTH = 2                # How many sub-pages deep to crawl
MAX_SUBPAGES = 6                   # Max sub-pages per domain
SCROLL_COUNT_MAPS = 15              # Scroll iterations in Google Maps
RESULTS_PER_NICHE = 35             # Max results per niche/city combo
PERSISTENT_PROFILE_DIR = os.path.join(os.path.dirname(__file__), ".browser_profile")
GEMINI_TIMEOUT = 60                # Seconds to wait for Gemini response

# ==========================================
# 📧 REGEX PATTERNS
# ==========================================

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE
)

LINKEDIN_REGEX = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?",
    re.IGNORECASE
)

LINKEDIN_COMPANY_REGEX = re.compile(
    r"https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9\-_%]+/?",
    re.IGNORECASE
)

PHONE_REGEX = re.compile(
    r"(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}"
)

# Sub-page link keywords to crawl
CRAWL_KEYWORDS = [
    "contact", "about", "team", "staff", "meet", "owner",
    "doctor", "dentist", "privacy", "legal", "our-team",
    "leadership", "management", "bio", "people", "founder"
]

# Junk email domains to ignore
JUNK_EMAIL_DOMAINS = {
    "example.com", "sentry.io", "wixpress.com", "googleapis.com",
    "w3.org", "schema.org", "gravatar.com", "wordpress.org",
    "jquery.com", "cloudflare.com", "google.com", "gstatic.com",
    "facebook.com", "twitter.com", "youtube.com", "instagram.com",
    "squarespace.com", "shopify.com", "wix.com", "godaddy.com",
}

CSV_COLUMNS = [
    "Business Name", "Owner Name", "Direct Mobile", "Personal Email",
    "LinkedIn Profile", "Hiring Status", "Office Line",
    "Estimated Revenue Loss", "Loss Reason", "Website"
]


# ==========================================
# 🛠️ UTILITY FUNCTIONS
# ==========================================

def smart_delay(min_s=SMART_DELAY_MIN, max_s=SMART_DELAY_MAX):
    """Randomized human-like delay."""
    delay = random.uniform(min_s, max_s)
    return delay


def short_delay(min_s=2, max_s=5):
    """Short delay for page transitions."""
    return random.uniform(min_s, max_s)


def filter_emails(emails: list[str]) -> list[str]:
    """Remove junk/system emails, return unique clean list."""
    cleaned = []
    seen = set()
    for email in emails:
        email = email.strip().lower().rstrip(".")
        domain = email.split("@")[-1] if "@" in email else ""
        if (
            domain not in JUNK_EMAIL_DOMAINS
            and email not in seen
            and not email.startswith("noreply")
            and not email.startswith("no-reply")
            and not email.startswith("support@")
            and not email.startswith("info@sentry")
            and len(email) < 80
            and ".png" not in email
            and ".jpg" not in email
            and ".gif" not in email
            and ".svg" not in email
        ):
            cleaned.append(email)
            seen.add(email)
    return cleaned


def extract_linkedin_name(url: str) -> str:
    """Attempt to extract a name from a LinkedIn /in/ URL."""
    try:
        path = urlparse(url).path.strip("/")
        slug = path.split("/")[-1]
        # Remove trailing numbers/hashes
        slug = re.sub(r"[-_]\w{5,}$", "", slug)
        parts = slug.replace("-", " ").replace("_", " ").title()
        if len(parts) > 3:
            return parts
    except Exception:
        pass
    return "N/A"


def load_existing_leads() -> set:
    """Load existing business names to avoid duplicates."""
    if not os.path.exists(OUTPUT_CSV):
        return set()
    try:
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["Business Name"] for row in reader if row.get("Business Name")}
    except Exception:
        return set()


def append_lead_to_csv(lead: dict):
    """Append a single lead row to the CSV in real-time."""
    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)


# ==========================================
# 🧠 GEMINI AI BRAIN
# ==========================================

def call_gemini_ai(prompt: str) -> str:
    """Synthesize data through Gemini CLI."""
    try:
        process = subprocess.Popen(
            [GEMINI_CMD, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        stdout, stderr = process.communicate(timeout=GEMINI_TIMEOUT)
        if process.returncode == 0 and stdout.strip():
            return stdout.strip()
        return "N/A|N/A|N/A|N/A|N/A|N/A"
    except Exception:
        return "N/A|N/A|N/A|N/A|N/A|N/A"


def gemini_classify_email(emails: list[str], business_name: str, website_text: str) -> tuple[str, str]:
    """
    Ask Gemini to classify which email is personal/owner vs generic.
    Returns (best_email, email_type).
    """
    if not emails:
        return "N/A", "N/A"

    prompt = f"""You are classifying emails for the business "{business_name}".
Here are the emails found: {', '.join(emails)}

Website context (truncated): {website_text[:3000]}

Rules:
1. A "Personal" email contains a real person's name (e.g., john@company.com, drsmith@gmail.com).
2. A "Generic" email is like info@, contact@, office@, admin@, hello@, support@.
3. Prefer personal emails. If none exist, return the best generic one.

OUTPUT FORMAT (pipe-separated, nothing else):
BestEmail|EmailType
Where EmailType is either "Personal" or "Generic".
If no valid email, return: N/A|N/A"""

    result = call_gemini_ai(prompt)
    parts = result.strip().split("|")
    if len(parts) >= 2:
        return parts[0].strip(), parts[1].strip()
    return emails[0] if emails else "N/A", "Unknown"


def gemini_revenue_loss_analysis(business_name: str, website: str, website_text: str) -> str:
    """Ask Gemini to guess a revenue loss reason from website quality."""
    prompt = f"""Analyze the website quality for "{business_name}" at {website}.

Website text (truncated): {website_text[:4000]}

Based on the website's quality, identify the SINGLE most likely reason this business
is losing revenue from their online presence. Consider:
- Slow loading / poor performance
- No mobile optimization
- No online booking system
- Poor SEO / no meta descriptions
- No social media links
- Outdated design
- No patient/customer reviews shown
- No clear call-to-action
- Missing contact information
- No SSL certificate

OUTPUT: Return ONLY a short reason (max 8 words), e.g. "No online booking system" or "Outdated design, no mobile optimization".
If you cannot determine, return "Needs website audit"."""

    result = call_gemini_ai(prompt)
    # Clean up: take first line, strip quotes
    reason = result.strip().split("\n")[0].strip('"').strip("'")
    return reason if len(reason) > 2 else "Needs website audit"


def gemini_final_synthesis(business_name: str, city: str, intel_blob: str, hiring_status: str) -> dict:
    """Final AI pass — extract structured intel from all raw data."""
    prompt = f"""Analyze all intelligence gathered for "{business_name}" in {city}.

RAW INTEL:
{intel_blob[:8000]}

Extract the following Decision Maker data.
Rules:
1. Direct Mobile must NOT be the general office number. Look for context like "cell", "mobile", "direct".
2. Personal Email should be a real person's email, not info@ or contact@.
3. LinkedIn Profile should be a full URL if found.
4. Owner Name should be a real person's name.
5. Hiring Status is: {hiring_status}

OUTPUT FORMAT (pipe-separated, one line, nothing else):
OwnerName|DirectMobile|PersonalEmail|LinkedInProfile|HiringStatus|RevenueLossReason

If a field is unknown, use N/A."""

    result = call_gemini_ai(prompt)
    parts = result.strip().split("|")
    if len(parts) >= 6:
        return {
            "owner_name": parts[0].strip(),
            "direct_mobile": parts[1].strip(),
            "personal_email": parts[2].strip(),
            "linkedin": parts[3].strip(),
            "hiring_status": parts[4].strip(),
            "loss_reason": parts[5].strip(),
        }
    return {
        "owner_name": "N/A", "direct_mobile": "N/A",
        "personal_email": "N/A", "linkedin": "N/A",
        "hiring_status": hiring_status, "loss_reason": "N/A",
    }


# ==========================================
# 🌐 BROWSER CONTEXT MANAGER
# ==========================================

class BrowserManager:
    """
    Manages a persistent Playwright browser context.
    Re-creates browser every N leads to keep RAM < 1GB.
    """

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.leads_since_restart = 0

    async def initialize(self):
        """Launch Playwright with persistent context."""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()

        # Ensure profile directory exists
        os.makedirs(PERSISTENT_PROFILE_DIR, exist_ok=True)

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=PERSISTENT_PROFILE_DIR,
            headless=False,
            viewport={"width": 1600, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/Denver",
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )

        # Stealth: override navigator.webdriver
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        self.leads_since_restart = 0
        print("   🟢 Browser launched with persistent context")

    async def get_page(self):
        """Get or create a new page in the context."""
        pages = self.context.pages
        if pages:
            return pages[0]
        return await self.context.new_page()

    async def new_page(self):
        """Create a fresh tab."""
        page = await self.context.new_page()
        page.set_default_timeout(PAGE_LOAD_TIMEOUT)
        return page

    async def recycle_if_needed(self):
        """Restart browser if we've processed enough leads (RAM management)."""
        self.leads_since_restart += 1
        if self.leads_since_restart >= BROWSER_RECYCLE_INTERVAL:
            print("\n   ♻️  RAM GUARD: Recycling browser to clear cache...")
            await self.shutdown()
            await asyncio.sleep(3)
            await self.initialize()
            print("   ♻️  Browser recycled successfully\n")

    async def shutdown(self):
        """Gracefully close everything."""
        try:
            if self.context:
                await self.context.close()
        except Exception:
            pass
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
        self.context = None
        self.playwright = None


# ==========================================
# 🕷️ RECURSIVE WEB CRAWLER
# ==========================================

async def recursive_web_crawler(page, start_url: str, max_depth: int = MAX_CRAWL_DEPTH) -> dict:
    """
    Deep-scan a website by following relevant links.
    Returns dict with all extracted intel.
    """
    results = {
        "emails": [],
        "linkedin_personal": [],
        "linkedin_company": [],
        "phones": [],
        "page_texts": [],
        "pages_visited": set(),
    }

    base_domain = urlparse(start_url).netloc

    async def _crawl(url: str, depth: int):
        if depth > max_depth:
            return
        if url in results["pages_visited"]:
            return
        if len(results["pages_visited"]) >= MAX_SUBPAGES:
            return

        # Only crawl same domain
        if urlparse(url).netloc != base_domain:
            return

        results["pages_visited"].add(url)

        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
            if not response or response.status >= 400:
                return
            await asyncio.sleep(short_delay(1, 3))

            # Get full page source (includes hidden scripts, meta tags, etc.)
            page_source = await page.content()
            body_text = await page.inner_text("body")

            # Regex extraction from FULL source
            found_emails = EMAIL_REGEX.findall(page_source)
            found_linkedin = LINKEDIN_REGEX.findall(page_source)
            found_linkedin_co = LINKEDIN_COMPANY_REGEX.findall(page_source)
            found_phones = PHONE_REGEX.findall(page_source)

            results["emails"].extend(found_emails)
            results["linkedin_personal"].extend(found_linkedin)
            results["linkedin_company"].extend(found_linkedin_co)
            results["phones"].extend(found_phones)
            results["page_texts"].append(body_text[:3000])

            print(f"      📄 Crawled: {url[:80]}... | Emails: {len(found_emails)} | LinkedIn: {len(found_linkedin)}")

            # Find sub-page links matching our keywords
            if depth < max_depth:
                links = await page.eval_on_selector_all(
                    "a[href]",
                    """(elements) => elements.map(e => ({
                        href: e.href,
                        text: (e.textContent || '').toLowerCase().trim()
                    }))"""
                )

                for link_info in links:
                    href = link_info.get("href", "")
                    text = link_info.get("text", "")

                    # Check if link text or href contains our keywords
                    should_follow = any(
                        kw in text or kw in href.lower()
                        for kw in CRAWL_KEYWORDS
                    )

                    if should_follow and href.startswith("http"):
                        await _crawl(href, depth + 1)

        except Exception as e:
            print(f"      ⚠️  Crawl error on {url[:60]}: {str(e)[:80]}")

    await _crawl(start_url, 0)

    # Deduplicate
    results["emails"] = filter_emails(results["emails"])
    results["linkedin_personal"] = list(set(results["linkedin_personal"]))
    results["linkedin_company"] = list(set(results["linkedin_company"]))
    results["phones"] = list(set(results["phones"]))

    return results


# ==========================================
# 🔍 DUCKDUCKGO EMAIL STITCHING
# ==========================================

async def duckduckgo_email_stitch(page, business_name: str, city: str) -> list[str]:
    """
    Fallback: Search DuckDuckGo for the business email if website didn't have one.
    DuckDuckGo has far fewer CAPTCHAs than Google.
    """
    query = f'"{business_name}" "{city}" email'
    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"

    try:
        print(f"      🦆 DuckDuckGo stitching: {business_name}...")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        await asyncio.sleep(short_delay(3, 6))

        page_source = await page.content()
        found_emails = EMAIL_REGEX.findall(page_source)
        found_emails = filter_emails(found_emails)

        if found_emails:
            print(f"      🦆 Stitched {len(found_emails)} email(s) from DuckDuckGo")

        return found_emails

    except Exception as e:
        print(f"      ⚠️  DuckDuckGo error: {str(e)[:60]}")
        return []


async def duckduckgo_linkedin_search(page, business_name: str, city: str) -> tuple[list[str], str]:
    """
    Search DuckDuckGo for LinkedIn profile of the business owner.
    Returns (linkedin_urls, extracted_owner_name).
    """
    query = f'site:linkedin.com/in "{business_name}" "{city}" owner OR founder OR CEO OR dentist'
    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"

    try:
        print(f"      🦆 DuckDuckGo LinkedIn hunt: {business_name}...")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        await asyncio.sleep(short_delay(3, 6))

        page_source = await page.content()
        body_text = await page.inner_text("body")
        linkedin_urls = LINKEDIN_REGEX.findall(page_source)

        owner_name = "N/A"
        if linkedin_urls:
            # Try to extract name from URL slug
            owner_name = extract_linkedin_name(linkedin_urls[0])

            # Also try to extract from page title snippets
            titles = await page.eval_on_selector_all(
                "a[href*='linkedin.com/in']",
                "(elements) => elements.map(e => e.textContent.trim())"
            )
            for title in titles:
                if title and len(title) > 3 and "linkedin" not in title.lower():
                    owner_name = title.split(" - ")[0].strip()
                    break

        return list(set(linkedin_urls)), owner_name

    except Exception as e:
        print(f"      ⚠️  DuckDuckGo LinkedIn error: {str(e)[:60]}")
        return [], "N/A"


# ==========================================
# 💼 HIRING STATUS CHECK
# ==========================================

async def check_hiring_status(page, business_name: str) -> str:
    """Check DuckDuckGo for job postings."""
    query = f'site:linkedin.com/jobs OR site:indeed.com "{business_name}"'
    search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"

    try:
        await page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
        await asyncio.sleep(short_delay(2, 4))

        # Check if any results exist
        results = await page.query_selector_all("article, .result, .nrn-react-div")
        return "Yes" if len(results) > 0 else "No"

    except Exception:
        return "Unknown"


# ==========================================
# 🕵️ DEEP INTELLIGENCE HUNT (Per Lead)
# ==========================================

async def recursive_intel_hunt(
    browser_mgr: BrowserManager,
    business_name: str,
    city: str,
    niche: str,
    website: str = "N/A",
    office_phone: str = "N/A"
) -> dict:
    """
    Full recursive intelligence pipeline for a single business.
    """
    print(f"\n   🕵️  INFILTRATING: {business_name}")

    page = await browser_mgr.new_page()
    intel_log = []
    all_emails = []
    all_linkedin = []
    owner_name = "N/A"
    website_text = ""

    try:
        # ─── STEP 1: Deep Website Crawl ───
        if website and website != "N/A" and "http" in website:
            print(f"      🌐 Deep-scanning website: {website[:60]}...")
            crawl_results = await recursive_web_crawler(page, website)

            all_emails.extend(crawl_results["emails"])
            all_linkedin.extend(crawl_results["linkedin_personal"])
            website_text = " ".join(crawl_results["page_texts"])
            intel_log.append(f"WEBSITE_CRAWL_EMAILS: {crawl_results['emails']}")
            intel_log.append(f"WEBSITE_CRAWL_LINKEDIN: {crawl_results['linkedin_personal']}")
            intel_log.append(f"WEBSITE_CRAWL_PHONES: {crawl_results['phones']}")
            intel_log.append(f"WEBSITE_TEXT: {website_text[:4000]}")

            # Extract owner name from LinkedIn if found
            if crawl_results["linkedin_personal"]:
                owner_name = extract_linkedin_name(crawl_results["linkedin_personal"][0])

        await asyncio.sleep(short_delay(2, 4))

        # ─── STEP 2: DuckDuckGo Email Stitching ───
        if not all_emails:
            stitched_emails = await duckduckgo_email_stitch(page, business_name, city)
            all_emails.extend(stitched_emails)
            intel_log.append(f"DDG_STITCHED_EMAILS: {stitched_emails}")

        await asyncio.sleep(short_delay(2, 4))

        # ─── STEP 3: DuckDuckGo LinkedIn Hunt ───
        if not all_linkedin or owner_name == "N/A":
            linkedin_urls, found_name = await duckduckgo_linkedin_search(page, business_name, city)
            all_linkedin.extend(linkedin_urls)
            if found_name != "N/A":
                owner_name = found_name
            intel_log.append(f"DDG_LINKEDIN: {linkedin_urls}")
            intel_log.append(f"DDG_OWNER_NAME: {found_name}")

        await asyncio.sleep(short_delay(2, 4))

        # ─── STEP 4: Hiring Status ───
        print(f"      💼 Checking hiring status...")
        hiring_status = await check_hiring_status(page, business_name)
        intel_log.append(f"HIRING_STATUS: {hiring_status}")

        await asyncio.sleep(short_delay(2, 4))

        # ─── STEP 5: Gemini Email Classification ───
        best_email = "N/A"
        email_type = "N/A"
        if all_emails:
            best_email, email_type = gemini_classify_email(all_emails, business_name, website_text)
            intel_log.append(f"GEMINI_EMAIL: {best_email} ({email_type})")

        # ─── STEP 6: Gemini Revenue Loss Analysis ───
        loss_reason = "N/A"
        if website_text:
            loss_reason = gemini_revenue_loss_analysis(business_name, website, website_text)

        # ─── STEP 7: Final Gemini Synthesis ───
        print(f"      🧠 Gemini AI synthesizing all intel...")
        synthesis = gemini_final_synthesis(
            business_name, city, "\n".join(intel_log), hiring_status
        )

        # ─── Merge all intel (prefer direct data over Gemini guesses) ───
        final_owner = owner_name if owner_name != "N/A" else synthesis.get("owner_name", "N/A")
        final_email = best_email if best_email != "N/A" else synthesis.get("personal_email", "N/A")
        final_linkedin = all_linkedin[0] if all_linkedin else synthesis.get("linkedin", "N/A")
        final_mobile = synthesis.get("direct_mobile", "N/A")
        final_hiring = hiring_status if hiring_status != "Unknown" else synthesis.get("hiring_status", "No")
        final_loss = loss_reason if loss_reason != "N/A" else synthesis.get("loss_reason", "N/A")

        return {
            "owner_name": final_owner,
            "direct_mobile": final_mobile,
            "personal_email": final_email,
            "linkedin": final_linkedin,
            "hiring_status": final_hiring,
            "loss_reason": final_loss,
        }

    except Exception as e:
        print(f"      ⚠️  Intelligence failure: {str(e)[:100]}")
        traceback.print_exc()
        return {
            "owner_name": owner_name, "direct_mobile": "N/A",
            "personal_email": "N/A", "linkedin": all_linkedin[0] if all_linkedin else "N/A",
            "hiring_status": "N/A", "loss_reason": "N/A",
        }

    finally:
        try:
            await page.close()
        except Exception:
            pass


# ==========================================
# 🗺️ GOOGLE MAPS SCRAPER
# ==========================================

async def scrape_google_maps(page, query: str) -> list[dict]:
    """
    Scrape Google Maps search results.
    Returns list of {name, phone, website} dicts.
    """
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    print(f"\n   🗺️  Loading Maps: {query}")

    await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)
    await asyncio.sleep(short_delay(4, 7))

    # Scroll the results feed to load more
    for i in range(SCROLL_COUNT_MAPS):
        try:
            feed = page.locator('div[role="feed"]')
            await feed.evaluate("el => el.scrollTop += 2000")
            await asyncio.sleep(short_delay(1.5, 3))
            print(f"      📜 Scroll {i + 1}/{SCROLL_COUNT_MAPS}")
        except Exception:
            break

    # Extract result links
    links = await page.locator("a.hfpxzc").all()
    businesses = []

    count = min(len(links), RESULTS_PER_NICHE)
    print(f"   📊 Found {len(links)} results, processing top {count}")

    for i in range(count):
        try:
            link = links[i]
            name = await link.get_attribute("aria-label")
            if not name:
                continue

            # Click to open the details panel
            await link.click()
            await asyncio.sleep(short_delay(2, 4))

            # Extract phone
            phone = "N/A"
            try:
                phone_btn = page.locator('button[aria-label^="Phone:"]')
                if await phone_btn.count() > 0:
                    phone_label = await phone_btn.first.get_attribute("aria-label")
                    phone = phone_label.replace("Phone: ", "").strip()
            except Exception:
                pass

            # Extract website
            website = "N/A"
            try:
                website_link = page.locator('a[aria-label^="Website:"], a[data-item-id="authority"]')
                if await website_link.count() > 0:
                    website = await website_link.first.get_attribute("href")
            except Exception:
                pass

            businesses.append({
                "name": name,
                "phone": phone,
                "website": website or "N/A",
            })

        except Exception as e:
            print(f"      ⚠️  Extraction error: {str(e)[:60]}")
            continue

    return businesses


# ==========================================
# 🚀 MAIN EXECUTION ENGINE
# ==========================================

async def main():
    """Async main loop — the heart of the Lead Hunter."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       🔥 PLAYWRIGHT RECURSIVE LEAD HUNTER v2.0 🔥          ║
║  Targets: {cities} cities × {niches} niches                ║
║  Output:  {output}                                         ║
╚══════════════════════════════════════════════════════════════╝
    """.format(
        cities=len(CITIES),
        niches=len(NICHES),
        output=OUTPUT_CSV,
    ))

    # Load existing leads
    existing_names = load_existing_leads()
    print(f"   📂 Existing leads in CSV: {len(existing_names)}")

    # Initialize browser
    browser = BrowserManager()
    await browser.initialize()

    total_new_leads = 0
    start_time = datetime.now()

    try:
        for city in CITIES:
            for niche, estimated_loss in NICHES.items():
                query = f"{niche} in {city}"
                print(f"\n{'='*60}")
                print(f"🚀 MISSION: {query}")
                print(f"{'='*60}")

                # Get the main page
                page = await browser.get_page()

                # Scrape Google Maps
                businesses = await scrape_google_maps(page, query)

                for biz in businesses:
                    name = biz["name"]

                    # Skip duplicates
                    if name in existing_names:
                        print(f"   ⏭️  Skipping (already exists): {name}")
                        continue

                    # ── Smart delay between leads ──
                    delay = smart_delay()
                    print(f"\n   ⏳ Smart delay: {delay:.1f}s...")
                    await asyncio.sleep(delay)

                    # ── Deep intel hunt ──
                    intel = await recursive_intel_hunt(
                        browser, name, city, niche,
                        website=biz["website"],
                        office_phone=biz["phone"],
                    )

                    # ── Build final lead row ──
                    lead = {
                        "Business Name": name,
                        "Owner Name": intel["owner_name"],
                        "Direct Mobile": intel["direct_mobile"],
                        "Personal Email": intel["personal_email"],
                        "LinkedIn Profile": intel["linkedin"],
                        "Hiring Status": intel["hiring_status"],
                        "Office Line": biz["phone"],
                        "Estimated Revenue Loss": f"${estimated_loss}",
                        "Loss Reason": intel["loss_reason"],
                        "Website": biz["website"],
                    }

                    # ── Append to CSV in real-time ──
                    append_lead_to_csv(lead)
                    existing_names.add(name)
                    total_new_leads += 1

                    print(f"\n   ✅ LEAD #{total_new_leads}: {name}")
                    print(f"      👤 Owner:    {intel['owner_name']}")
                    print(f"      📱 Mobile:   {intel['direct_mobile']}")
                    print(f"      📧 Email:    {intel['personal_email']}")
                    print(f"      🔗 LinkedIn: {intel['linkedin'][:60] if intel['linkedin'] != 'N/A' else 'N/A'}")
                    print(f"      💼 Hiring:   {intel['hiring_status']}")
                    print(f"      💸 Loss:     {intel['loss_reason']}")

                    # ── RAM Guard: Recycle browser ──
                    await browser.recycle_if_needed()

    except KeyboardInterrupt:
        print("\n\n   ⚡ Manual abort — saving progress...")

    except Exception as e:
        print(f"\n   ❌ Critical error: {e}")
        traceback.print_exc()

    finally:
        await browser.shutdown()

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚡ MISSION COMPLETE                                                         ║ 
║  New leads captured:  {total_new_leads:<37}                                  ║
║  Total time:          {elapsed:.0f}s{' ' * (34 - len(f'{elapsed:.0f}s'))}    ║
║  Output file:         {OUTPUT_CSV:<37}                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)


# ==========================================
# 🏁 ENTRY POINT
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())
