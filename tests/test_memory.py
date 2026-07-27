from harness.memory.manager import ContextManager


def test_add_and_get_messages():
    cm = ContextManager()
    cm.add("system", "You are a helpful assistant")
    cm.add("user", "Hello")
    msgs = cm.get_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["content"] == "Hello"


def test_token_truncation():
    cm = ContextManager(max_tokens=10)
    cm.add("system", "S" * 100)
    cm.add("user", "U" * 100)
    msgs = cm.get_messages()
    total = sum(len(m["content"]) for m in msgs)
    assert total <= 10


def test_clear():
    cm = ContextManager()
    cm.add("user", "Hello")
    cm.clear()
    assert len(cm.get_messages()) == 0
