"""
Кастомные хуки pytest для интеграции с нашим репортёром.
"""

import pytest
import time
from utils.reporter import TestReport


# Глобальный экземпляр репортёра
_reporter = TestReport()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Перехватываем выполнение каждого теста для замера времени."""
    start = time.time()
    yield
    duration = time.time() - start

    # Определяем статус теста
    report = item.rep_call if hasattr(item, "rep_call") else None
    if report and report.failed:
        status = "FAILED"
        error = str(report.longrepr)
    elif report and report.skipped:
        status = "SKIPPED"
        error = None
    else:
        status = "PASSED"
        error = None

    _reporter.add_result(
        test_name=item.nodeid, status=status, duration=duration, error=error
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняем отчёт о вызове теста для определения статуса."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionfinish(session, exitstatus):
    """Выводим отчёт после завершения всех тестов."""
    _reporter.finish()
    print("\n\n" + "=" * 50)
    print(_reporter.get_summary())
    print("=" * 50 + "\n")

    # Сохраняем отчёт в файл
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write(_reporter.get_summary())

    print("📄 Отчёт сохранён: test_report.txt")
