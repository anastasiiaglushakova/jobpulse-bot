"""
JobPulse Telegram Bot — runs e2e tests and sends reports via Telegram.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Custom logger setup
from utils.logger import logger

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
    sys.exit(1)

JOBSITE_URL = os.getenv(
    "JOBSITE_URL", "https://anastasiiaglushakova.github.io/jobboard-demo/"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start command — brief menu."""
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — JobPulse Bot, система автоматизированного тестирования.\n\n"
        "<b>Быстрый доступ:</b>\n"
        "• /test_jobboard — тесты демо-сайта вакансий\n"
        "• /test_internet — тесты учебной площадки\n"
        "• /status — проверить доступность сайтов\n"
        "• /help — подробная справка о проекте"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command — detailed project description."""
    help_text = (
        "ℹ️ <b>JobPulse Bot — подробная справка</b>\n\n"
        "<b>🎯 Назначение</b>\n"
        "Система автоматизированного тестирования демо-сайтов с доставкой отчётов через Telegram.\n\n"
        "<b>✅ Этичный подход</b>\n"
        "• Не тестирует коммерческие сайты без разрешения\n"
        "• Использует самохостящиеся демо-сайты (GitHub Pages)\n"
        "• Соблюдает ToS всех платформ\n\n"
        "<b>⚙️ Технологии</b>\n"
        "• Playwright — браузерная автоматизация\n"
        "• PyTest — фреймворк для тестов\n"
        "• Page Object Model — поддерживаемая архитектура\n"
        "• GitHub Actions — CI/CD\n"
        "• python-telegram-bot — интеграция с Telegram\n\n"
        "<b>🌐 Тестируемые площадки</b>\n"
        "• JobBoard Demo — демо-сайт вакансий\n"
        "  https://anastasiiaglushakova.github.io/jobboard-demo/\n"
        "• the-internet — учебная площадка\n"
        "  https://the-internet.herokuapp.com/\n\n"
        "<b>📚 Репозиторий</b>\n"
        "https://github.com/anastasiiaglushakova/jobpulse-bot\n\n"
        "<b>❓ Команды</b>\n"
        "• /test_jobboard — тесты демо-сайта вакансий\n"
        "• /test_internet — тесты учебной площадки\n"
        "• /status — проверить доступность сайтов\n"
        "• /start — краткое меню\n"
        "• /help — эта справка"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check status of demo sites."""
    # Site URLs
    sites = {
        "JobBoard Demo": JOBSITE_URL,
        "the-internet": "https://the-internet.herokuapp.com/",
    }

    status_text = "🔍 <b>Проверка статуса сайтов</b>\n\n"

    for site_name, site_url in sites.items():
        try:
            response = requests.get(site_url, timeout=10)
            if response.status_code == 200:
                status_text += (
                    f"✅ <b>{site_name}</b>\n"
                    f"   URL: {site_url}\n"
                    f"   Статус: {response.status_code}\n"
                    f"   Время ответа: {response.elapsed.total_seconds():.2f} сек\n\n"
                )
            else:
                status_text += (
                    f"⚠️ <b>{site_name}</b>\n"
                    f"   URL: {site_url}\n"
                    f"   Статус: {response.status_code}\n\n"
                )
        except Exception as e:
            status_text += (
                f"❌ <b>{site_name}</b>\n"
                f"   URL: {site_url}\n"
                f"   Ошибка: {str(e)[:50]}\n\n"
            )

    await update.message.reply_text(status_text, parse_mode="HTML")


async def run_tests_and_get_report(test_file: str, site_name: str) -> str:
    """Run tests and return report text."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            test_file,
            "-v",
            "--tb=short",
            "-o",
            "console_output_style=classic",
        ],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )

    # Read saved report
    report_path = Path(__file__).parent / "test_report.txt"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report = f.read()
        # Replace header with correct site name
        report = report.replace("JobBoard Demo", site_name)
    else:
        # Generate simplified report
        passed = result.stdout.count("PASSED")
        failed = result.stdout.count("FAILED")
        total = passed + failed

        status_emoji = "✅" if failed == 0 else "❌"
        report = (
            f"{status_emoji} {site_name} — Тестовый отчёт\n"
            f"{'─' * 45}\n"
            f"Всего тестов:   {total}\n"
            f"Успешно:       {passed} ✅\n"
            f"Упало:         {failed} ❌\n"
            f"{'─' * 45}\n"
        )

    return report


async def test_jobboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 Запускаю тесты для JobBoard Demo...\nОжидайте ~10 секунд..."
    )
    report = await run_tests_and_get_report("tests/test_jobboard.py", "JobBoard Demo")
    # Escape special characters for HTML
    report = report.replace("<", "&lt;").replace(">", "&gt;")
    await update.message.reply_text(f"<pre>{report}</pre>", parse_mode="HTML")


async def test_internet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🚀 Запускаю тесты для the-internet...\nОжидайте ~10 секунд..."
    )
    report = await run_tests_and_get_report(
        "tests/test_internet_login.py", "the-internet.herokuapp.com"
    )
    # Escape special characters for HTML
    report = report.replace("<", "&lt;").replace(">", "&gt;")
    await update.message.reply_text(f"<pre>{report}</pre>", parse_mode="HTML")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for unknown commands."""
    await update.message.reply_text(
        "❓ Неизвестная команда.\nИспользуйте /help для списка доступных команд."
    )


def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("test_jobboard", test_jobboard))
    application.add_handler(CommandHandler("test_internet", test_internet))

    # Unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start bot
    logger.info("✅ JobPulse Bot started and awaiting commands...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
