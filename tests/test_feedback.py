from harness.feedback.parser import TestResultParser, FeedbackResult


def test_parse_pytest_pass():
    parser = TestResultParser()
    output = "collected 3 items\n\n tests/test_a.py::test_ok PASSED\n tests/test_b.py::test_ok PASSED\n\n== 3 passed in 0.05s =="
    result = parser.parse(output)
    assert result.passed == 3
    assert result.failed == 0
    assert result.success is True


def test_parse_pytest_fail():
    parser = TestResultParser()
    output = "collected 2 items\n\n tests/test_a.py::test_ok PASSED\n tests/test_b.py::test_fail FAILED\n\n== 1 passed, 1 failed in 0.10s =="
    result = parser.parse(output)
    assert result.passed == 1
    assert result.failed == 1
    assert result.success is False


def test_parse_error():
    parser = TestResultParser()
    output = "ERROR: file not found"
    result = parser.parse(output)
    assert result.success is False
    assert result.error_type == "unknown"
