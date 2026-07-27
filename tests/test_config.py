import pytest
from pathlib import Path
from harness.config.loader import ConfigLoader, HarnessConfig

def test_load_default_config():
    loader = ConfigLoader()
    config = loader.get_default()
    assert isinstance(config, HarnessConfig)
    assert config.llm.model == "gpt-4o"
    assert config.agent.max_turns == 50
    assert len(config.guardrails.rules) > 0

def test_load_from_dict():
    loader = ConfigLoader()
    data = {"llm": {"model": "deepseek-chat"}, "agent": {"max_turns": 10}}
    config = loader.load(data)
    assert config.llm.model == "deepseek-chat"
    assert config.agent.max_turns == 10

def test_guard_rule_parsing():
    loader = ConfigLoader()
    data = {
        "guardrails": {
            "rules": [
                {"pattern": "rm -rf /*", "action_type": "command", "verdict": "block", "reason": "Dangerous deletion"}
            ]
        }
    }
    config = loader.load(data)
    assert len(config.guardrails.rules) == 1
    assert config.guardrails.rules[0].pattern == "rm -rf /*"
    assert config.guardrails.rules[0].verdict == "block"
