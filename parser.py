#!/usr/bin/env python3
"""
JobPulse — автоматический парсер вакансий с демо-сайта.
Запускается по расписанию, отправляет ТОЛЬКО новые вакансии.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# === КОНФИГУРАЦИЯ ===
from dotenv import load_dotenv

load_dotenv()  # ← загружаем .env ОДИН РАЗ здесь

JOBSITE_URL = os.environ.get(
    "JOBSITE_URL", "https://anastasiiaglushakova.github.io/jobboard-demo/"
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CACHE_FILE = Path(__file__).parent / "jobs_cache.json"


def load_cache():
    """Загружает кэш отправленных вакансий."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка чтения кэша: {e}", file=sys.stderr)
            return {}
    return {}


def save_cache(cache):
    """Сохраняет кэш на диск."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def parse_jobs():
    """
    Парсит вакансии с демо-сайта.
    Точные селекторы для твоего сайта:
    - .job-card — карточка вакансии
    - .job-title — заголовок (h4)
    - .job-company — компания
    - .job-tags — теги/стек
    - .job-description — описание
    - .job-location — локация
    - .job-date — дата публикации
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"🌐 Открываю {JOBSITE_URL}...")
        page.goto(JOBSITE_URL, wait_until="networkidle", timeout=30000)

        # Ждём появления карточек вакансий
        print("⏳ Ждём загрузки вакансий...")
        try:
            page.wait_for_selector(".job-card", timeout=15000)
        except PWTimeoutError:
            print("❌ Вакансии не загрузились вовремя", file=sys.stderr)
            browser.close()
            return []

        print("✅ Вакансии загружены, извлекаю данные...")

        # Извлекаем все карточки
        job_elements = page.query_selector_all(".job-card")

        jobs = []
        for el in job_elements:
            try:
                # Извлекаем данные по точным селекторам твоего сайта
                title_el = el.query_selector(".job-title")
                company_el = el.query_selector(".job-company")
                tags_el = el.query_selector(".job-tags")
                desc_el = el.query_selector(".job-description")
                location_el = el.query_selector(".job-location")
                date_el = el.query_selector(".job-date")

                title = title_el.text_content().strip() if title_el else "Без названия"
                company = company_el.text_content().strip() if company_el else ""
                tags = tags_el.text_content().strip() if tags_el else ""
                description = desc_el.text_content().strip() if desc_el else ""
                location = location_el.text_content().strip() if location_el else ""
                posted = (
                    date_el.text_content().replace("📅 ", "").strip() if date_el else ""
                )

                # Уникальный ID из атрибута data-id
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
                print(f"  ⚠️ Ошибка парсинга карточки: {e}", file=sys.stderr)

        browser.close()
        print(f"✅ Извлечено {len(jobs)} вакансий")
        return jobs


def send_telegram(text: str):
    """Отправляет сообщение в Telegram через прямой API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(
            "❌ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены", file=sys.stderr
        )
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
        print(f"❌ Ошибка отправки: {e}", file=sys.stderr)
        return False


def main():
    print(f"\n🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск парсинга...")

    # Загружаем кэш отправленных вакансий
    cache = load_cache()
    print(f"📦 Кэш: {len(cache)} известных вакансий")

    # Парсим новые вакансии
    try:
        jobs = parse_jobs()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    if not jobs:
        print("ℹ️ Вакансии не найдены")
        sys.exit(0)

    # Фильтруем только новые (которые ещё не в кэше)
    new_jobs = [j for j in jobs if j["id"] not in cache]
    print(f"🆕 Новых вакансий: {len(new_jobs)} из {len(jobs)}")

    # Отправляем новые вакансии
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
            print(f"📤 Отправлено: {job['title']}")
        else:
            print(f"❌ Не отправлено: {job['title']}")

    # Сохраняем кэш
    save_cache(cache)
    print(f"\n✅ Готово: {sent_count} новых вакансий отправлено\n")


if __name__ == "__main__":
    main()
