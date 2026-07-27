import pytest
from harness.llm.client import LLMClient, LLMResponse
from harness.llm.mock_client import MockLLMClient


def test_mock_llm_returns_fixed_response():
    client = MockLLMClient(responses=[{"type": "finish", "summary": "done"}])
    resp = client.chat([{"role": "user", "content": "hello"}])
    assert resp.type == "finish"
    assert resp.summary == "done"


def test_mock_llm_returns_tool_call():
    client = MockLLMClient(responses=[{"type": "tool_call", "tool": "read_file", "params": {"path": "test.txt"}}])
    resp = client.chat([{"role": "user", "content": "read file"}])
    assert resp.type == "tool_call"
    assert resp.tool == "read_file"
    assert resp.params == {"path": "test.txt"}


def test_mock_llm_consumes_in_order():
    client = MockLLMClient(responses=[
        {"type": "tool_call", "tool": "read_file", "params": {"path": "a.txt"}},
        {"type": "finish", "summary": "done"},
    ])
    r1 = client.chat([])
    assert r1.tool == "read_file"
    r2 = client.chat([])
    assert r2.type == "finish"


def test_mock_llm_exhausted_raises():
    client = MockLLMClient(responses=[])
    with pytest.raises(StopIteration):
        client.chat([])
