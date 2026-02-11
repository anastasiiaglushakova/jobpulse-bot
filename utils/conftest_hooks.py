"""
Custom pytest hooks for integration with our test reporter.
"""

import pytest
import time
from utils.reporter import TestReport


# Global reporter instance
_reporter = TestReport()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Intercept each test execution to measure duration."""
    start = time.time()
    yield
    duration = time.time() - start

    # Determine test status
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
    """Save test report for status determination."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionfinish(session, exitstatus):
    """Print report after all tests have finished."""
    _reporter.finish()
    print("\n\n" + "=" * 50)
    print(_reporter.get_summary())
    print("=" * 50 + "\n")

    # Save report to file
    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write(_reporter.get_summary())

    print("📄 Report saved: test_report.txt")
