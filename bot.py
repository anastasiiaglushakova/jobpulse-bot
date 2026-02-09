"""
JobPulse Telegram Bot — запускает e2e тесты и присылает отчёт.
"""

import os
import sys
import subprocess
import time
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

# Настройка логирования — кастомный логгер
from utils.logger import logger

# Загружаем переменные окружения
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не найден в .env файле!")
    sys.exit(1)

JOBSITE_URL = os.getenv(
    "JOBSITE_URL", "https://anastasiiaglushakova.github.io/jobboard-demo/"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — JobPulse Bot, система мониторинга демо-сайта вакансий.\n\n"
        "Доступные команды:\n"
        "• /test_jobboard — запустить end-to-end тесты\n"
        "• /status — проверить статус демо-сайта\n"
        "• /help — справка"
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_text = (
        "ℹ️ *JobPulse Bot — справка*\n\n"
        "Этот бот автоматически тестирует демо-сайт вакансий:\n"
        "→ https://anastasiiaglushakova.github.io/jobboard-demo/\n\n"
        "*Команды:*\n"
        "• `/test_jobboard` — запустить полный набор e2e тестов\n"
        "• `/status` — проверить доступность сайта\n"
        "• `/start` или `/help` — эта справка\n\n"
        "*Технологии:*\n"
        "Playwright • PyTest • Python • GitHub Actions"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверить статус демо-сайта."""
    import requests

    try:
        response = requests.get(JOBSITE_URL, timeout=10)
        if response.status_code == 200:
            status_text = (
                "✅ Демо-сайт доступен\n\n"
                f"URL: {JOBSITE_URL}\n"
                f"Статус: {response.status_code}\n"
                f"Время ответа: {response.elapsed.total_seconds():.2f} сек"
            )
        else:
            status_text = (
                "⚠️ Сайт недоступен или вернул ошибку\n\n"
                f"URL: {JOBSITE_URL}\n"
                f"Статус: {response.status_code}"
            )
    except Exception as e:
        status_text = (
            "❌ Ошибка при проверке сайта\n\n"
            f"URL: {JOBSITE_URL}\n"
            f"Ошибка: {str(e)}"
        )

    await update.message.reply_text(status_text)


async def run_tests_and_get_report() -> str:
    """Запустить тесты и вернуть текст отчёта."""
    # Запускаем pytest с кастомным форматированием
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_jobboard.py",
            "-v",
            "--tb=short",
            "-o",
            "console_output_style=classic",
        ],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,  # Максимум 60 секунд на тесты
    )

    # Читаем сохранённый отчёт
    report_path = Path(__file__).parent / "test_report.txt"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()
    else:
        # Если отчёт не сохранился — формируем вручную
        passed = result.stdout.count("PASSED")
        failed = result.stdout.count("FAILED")
        total = passed + failed

        status_emoji = "✅" if failed == 0 else "❌"
        report_text = (
            f"{status_emoji} JobBoard Demo — Тестовый отчёт (упрощённый)\n"
            f"{'─' * 45}\n"
            f"Всего тестов:   {total}\n"
            f"Успешно:       {passed} ✅\n"
            f"Упало:         {failed} ❌\n"
            f"{'─' * 45}\n\n"
            f"Подробности в логах бота."
        )

    # Добавляем информацию о результате выполнения
    if result.returncode != 0:
        report_text += f"\n\n⚠️  Код возврата: {result.returncode}"

    return report_text


async def test_jobboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /test_jobboard — запуск тестов."""
    await update.message.reply_text(
        "🚀 Запускаю end-to-end тесты для JobBoard Demo...\n"
        "Ожидайте ~10-15 секунд..."
    )

    try:
        # Запускаем тесты
        report = await run_tests_and_get_report()

        # Отправляем отчёт
        # Telegram имеет лимит ~4096 символов на сообщение
        if len(report) > 4000:
            # Обрезаем до последнего переноса строки перед лимитом
            report = (
                report[:4000].rsplit("\n", 1)[0]
                + "\n\n[Отчёт обрезан из-за лимита Telegram]"
            )

        await update.message.reply_text(
            f"```\n{report}\n```", parse_mode="MarkdownV2", disable_notification=False
        )

        # Отправляем скриншоты, если есть
        screenshots_dir = Path(__file__).parent / "screenshots"
        if screenshots_dir.exists():
            screenshot_files = sorted(
                [f for f in screenshots_dir.glob("*.png") if f.is_file()],
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            if screenshot_files and "❌" in report:  # Есть падения
                # Отправляем самый свежий скриншот
                latest_screenshot = screenshot_files[0]
                await update.message.reply_photo(
                    photo=open(latest_screenshot, "rb"),
                    caption="📸 Скриншот состояния при падении теста",
                )

    except subprocess.TimeoutExpired:
        await update.message.reply_text(
            "❌ Тесты превысили лимит времени (60 сек)\n"
            "Возможно, проблема с сетью или сайтом."
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при запуске тестов:\n" f"```\n{str(e)[:300]}\n```",
            parse_mode="MarkdownV2",
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик неизвестных команд."""
    await update.message.reply_text(
        "❓ Неизвестная команда.\n" "Используйте /help для списка доступных команд."
    )


def main() -> None:
    """Запуск бота."""
    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("test_jobboard", test_jobboard))

    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запускаем бота
    logger.info("✅ JobPulse Bot запущен и ожидает команд...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
