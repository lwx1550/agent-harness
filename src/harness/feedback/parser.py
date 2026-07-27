import re
from dataclasses import dataclass


@dataclass
class FeedbackResult:
    success: bool
    passed: int = 0
    failed: int = 0
    error_type: str = ""
    summary: str = ""


class TestResultParser:
    def parse(self, output: str) -> FeedbackResult:
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        if passed_match or failed_match:
            return FeedbackResult(success=failed == 0, passed=passed, failed=failed, summary=output[:200])
        if "ERROR" in output.upper():
            return FeedbackResult(success=False, error_type="unknown", summary=output[:200])
        return FeedbackResult(success=True, summary=output[:200])
