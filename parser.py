#!/usr/bin/env python3
"""
JobPulse — automatic job parser for demo site.
Runs on schedule, sends ONLY new job postings.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

from dotenv import load_dotenv

load_dotenv()

JOBSITE_URL = os.environ.get(
    "JOBSITE_URL", "https://anastasiiaglushakova.github.io/jobboard-demo/"
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CACHE_FILE = Path(__file__).parent / "jobs_cache.json"


def load_cache():
    """Load cache of sent job postings."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache read error: {e}", file=sys.stderr)
            return {}
    return {}


def save_cache(cache):
    """Save cache to disk."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def parse_jobs():
    """
    Parse job postings from demo site.
    Exact selectors for the site:
    - .job-card — job card
    - .job-title — title (h4)
    - .job-company — company
    - .job-tags — tags/stack
    - .job-description — description
    - .job-location — location
    - .job-date — publication date
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"🌐 Opening {JOBSITE_URL}...")
        page.goto(JOBSITE_URL, wait_until="networkidle", timeout=30000)

        # Wait for job cards to appear
        print("⏳ Waiting for job postings to load...")
        try:
            page.wait_for_selector(".job-card", timeout=15000)
        except PWTimeoutError:
            print("❌ Job postings did not load in time", file=sys.stderr)
            browser.close()
            return []

        print("✅ Job postings loaded, extracting data...")

        # Extract all job cards
        job_elements = page.query_selector_all(".job-card")

        jobs = []
        for el in job_elements:
            try:
                # Extract data using exact selectors
                title_el = el.query_selector(".job-title")
                company_el = el.query_selector(".job-company")
                tags_el = el.query_selector(".job-tags")
                desc_el = el.query_selector(".job-description")
                location_el = el.query_selector(".job-location")
                date_el = el.query_selector(".job-date")

                title = title_el.text_content().strip() if title_el else "Untitled"
                company = company_el.text_content().strip() if company_el else ""
                tags = tags_el.text_content().strip() if tags_el else ""
                description = desc_el.text_content().strip() if desc_el else ""
                location = location_el.text_content().strip() if location_el else ""
                posted = (
                    date_el.text_content().replace("📅 ", "").strip() if date_el else ""
                )

                # Unique ID from data-id attribute
                job_id = el.get_attribute("data-id") or title

                jobs.append(
                    {
                        "id": job_id,
                        "title": title,
                        "company": company,
                        "tags": tags,
                        "description": description,
                        "location": location,
                        "posted": posted,
                        "found_at": datetime.now().isoformat(),
                    }
                )
                print(f"  📌 {title} ({company})")

            except Exception as e:
                print(f"  ⚠️ Error parsing job card: {e}", file=sys.stderr)

        browser.close()
        print(f"✅ Extracted {len(jobs)} job postings")
        return jobs


def send_telegram(text: str):
    """Send message to Telegram via direct API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set", file=sys.stderr)
        return False

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"❌ Telegram API error: {resp.text}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"❌ Send error: {e}", file=sys.stderr)
        return False


def main():
    print(f"\n🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting parser...")

    # Load cache of sent job postings
    cache = load_cache()
    print(f"📦 Cache: {len(cache)} known job postings")

    # Parse new job postings
    try:
        jobs = parse_jobs()
    except Exception as e:
        print(f"❌ Critical error: {e}", file=sys.stderr)
        sys.exit(1)

    if not jobs:
        print("ℹ️ No job postings found")
        sys.exit(0)

    # Filter only new jobs (not in cache)
    new_jobs = [j for j in jobs if j["id"] not in cache]
    print(f"🆕 New job postings: {len(new_jobs)} out of {len(jobs)}")

    # Send new job postings
    sent_count = 0
    for job in new_jobs:
        msg = (
            f"💼 <b>{job['title']}</b>\n"
            f"🏢 {job['company']}\n"
            f"📍 {job['location']}\n"
            f"🛠 {job['tags']}\n"
        )
        if send_telegram(msg):
            sent_count += 1
            cache[job["id"]] = job["found_at"]
            print(f"📤 Sent: {job['title']}")
        else:
            print(f"❌ Not sent: {job['title']}")

    # Save cache
    save_cache(cache)
    print(f"\n✅ Done: {sent_count} new job postings sent\n")


if __name__ == "__main__":
    main()
