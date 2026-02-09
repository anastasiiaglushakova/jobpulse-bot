"""
Утилита для формирования текстовых отчётов о результатах тестов.
"""

from datetime import datetime
from typing import List, Dict
import textwrap


class TestReport:
    """Формирует человекочитаемый отчёт о результатах тестов."""

    def __init__(self):
        self.start_time = datetime.now()
        self.results: List[Dict] = []
        self.end_time = None

    def add_result(
        self, test_name: str, status: str, duration: float, error: str = None
    ):
        """Добавить результат теста.

        Args:
            test_name: Имя теста (например, 'test_search_python_jobs')
            status: 'PASSED' | 'FAILED' | 'SKIPPED'
            duration: Время выполнения в секундах
            error: Текст ошибки (для упавших тестов)
        """
        self.results.append(
            {
                "name": test_name,
                "status": status,
                "duration": duration,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def finish(self):
        """Завершить сбор отчёта."""
        self.end_time = datetime.now()

    def get_summary(self) -> str:
        """Получить текстовый отчёт в формате для Telegram/консоли."""
        if not self.end_time:
            self.finish()

        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASSED"])
        failed = len([r for r in self.results if r["status"] == "FAILED"])
        skipped = len([r for r in self.results if r["status"] == "SKIPPED"])
        duration_total = sum(r["duration"] for r in self.results)

        # Эмодзи статуса
        status_emoji = "✅" if failed == 0 else "❌"

        # Заголовок
        report = f"{status_emoji} JobBoard Demo — Тестовый отчёт\n"
        report += f"{'─' * 45}\n"

        # Статистика
        report += f"Всего тестов:   {total}\n"
        report += f"Успешно:       {passed} ✅\n"
        report += f"Упало:         {failed} ❌\n"
        report += f"Пропущено:     {skipped} ⏭\n"
        report += f"Время:         {duration_total:.2f} сек\n"
        report += f"{'─' * 45}\n\n"

        # Детали по тестам
        for result in self.results:
            emoji = (
                "✅"
                if result["status"] == "PASSED"
                else "❌" if result["status"] == "FAILED" else "⏭"
            )
            duration = f"{result['duration']:.2f}с"

            # Обрезаем имя теста для читаемости
            test_name = result["name"].replace("TestJobBoardDemo.", "")
            report += f"{emoji} {test_name:<35} {duration:>6}\n"

            # Добавляем ошибку, если есть
            if result["error"] and result["status"] == "FAILED":
                # Обрезаем длинные трейсы
                error_lines = result["error"].split("\n")
                first_line = error_lines[0] if error_lines else ""
                if len(first_line) > 70:
                    first_line = first_line[:67] + "..."
                report += f"   Ошибка: {first_line}\n"

        report += f"\n{'─' * 45}\n"
        report += f"Сформировано: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}"

        return report

    def has_failures(self) -> bool:
        """Есть ли упавшие тесты."""
        return any(r["status"] == "FAILED" for r in self.results)

    def get_screenshot_paths(self) -> List[str]:
        """Получить пути к скриншотам упавших тестов."""
        # В реальном проекте здесь будет логика поиска скриншотов
        # Пока возвращаем заглушку
        return ["screenshots/failure_*.png"] if self.has_failures() else []
