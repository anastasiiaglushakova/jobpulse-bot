"""
Utility for generating human-readable test reports.
"""

from datetime import datetime
from typing import List, Dict


class TestReport:
    """Generates human-readable test reports."""

    def __init__(self):
        self.start_time = datetime.now()
        self.results: List[Dict] = []
        self.end_time = None

    def add_result(
        self, test_name: str, status: str, duration: float, error: str = None
    ):
        """Add test result.

        Args:
            test_name: Test name (e.g., 'test_search_python_jobs')
            status: 'PASSED' | 'FAILED' | 'SKIPPED'
            duration: Execution time in seconds
            error: Error message (for failed tests)
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
        """Finish report collection."""
        self.end_time = datetime.now()

    def get_summary(self) -> str:
        """Get text report in format suitable for Telegram/console."""
        if not self.end_time:
            self.finish()

        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASSED"])
        failed = len([r for r in self.results if r["status"] == "FAILED"])
        skipped = len([r for r in self.results if r["status"] == "SKIPPED"])
        duration_total = sum(r["duration"] for r in self.results)

        # Status emoji
        status_emoji = "✅" if failed == 0 else "❌"

        # Header
        report = f"{status_emoji} JobBoard Demo — Test Report\n"
        report += f"{'─' * 45}\n"

        # Statistics
        report += f"Total tests:    {total}\n"
        report += f"Passed:         {passed} ✅\n"
        report += f"Failed:         {failed} ❌\n"
        report += f"Skipped:        {skipped} ⏭\n"
        report += f"Duration:       {duration_total:.2f}s\n"
        report += f"{'─' * 45}\n\n"

        # Test details
        for result in self.results:
            emoji = (
                "✅"
                if result["status"] == "PASSED"
                else "❌" if result["status"] == "FAILED" else "⏭"
            )
            duration = f"{result['duration']:.2f}s"

            # Trim test class prefix for readability
            test_name = result["name"].replace("TestJobBoardDemo.", "")
            report += f"{emoji} {test_name:<35} {duration:>6}\n"

            # Add error if present
            if result["error"] and result["status"] == "FAILED":
                # Trim long stack traces
                error_lines = result["error"].split("\n")
                first_line = error_lines[0] if error_lines else ""
                if len(first_line) > 70:
                    first_line = first_line[:67] + "..."
                report += f"   Error: {first_line}\n"

        report += f"\n{'─' * 45}\n"
        report += f"Generated: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}"

        return report

    def has_failures(self) -> bool:
        """Check if any tests failed."""
        return any(r["status"] == "FAILED" for r in self.results)
