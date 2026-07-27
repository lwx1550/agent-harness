from dataclasses import dataclass, field
from typing import List, Optional
import yaml


@dataclass
class GuardRuleConfig:
    pattern: str
    action_type: str
    verdict: str
    reason: str = ""


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4o"
    base_url: Optional[str] = None


@dataclass
class AgentConfig:
    max_turns: int = 50
    timeout: int = 300


@dataclass
class GuardrailsConfig:
    rules: List[GuardRuleConfig] = field(default_factory=lambda: [
        GuardRuleConfig(pattern="rm -rf /*", action_type="run_command", verdict="block", reason="Dangerous recursive deletion"),
        GuardRuleConfig(pattern="rm -rf /", action_type="run_command", verdict="block", reason="Dangerous root deletion"),
        GuardRuleConfig(pattern="DROP DATABASE*", action_type="run_command", verdict="approval", reason="Database drop requires confirmation"),
        GuardRuleConfig(pattern="format C:*", action_type="run_command", verdict="block", reason="Dangerous format command"),
        GuardRuleConfig(pattern="*del /f /s*", action_type="run_command", verdict="approval", reason="Force deletion requires confirmation"),
    ])


@dataclass
class HarnessConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    guardrails: GuardrailsConfig = field(default_factory=GuardrailsConfig)
    tools: List[str] = field(default_factory=lambda: ["read_file", "write_file", "edit_file", "run_command", "run_test"])


class ConfigLoader:
    def get_default(self) -> HarnessConfig:
        return HarnessConfig()

    def load(self, data: dict) -> HarnessConfig:
        llm_cfg = LLMConfig(**(data.get("llm", {})))
        agent_cfg = AgentConfig(**(data.get("agent", {})))
        guard_data = data.get("guardrails", {})
        rules = [GuardRuleConfig(**r) for r in guard_data.get("rules", [])]
        guard_cfg = GuardrailsConfig(rules=rules) if rules else GuardrailsConfig()
        tools = data.get("tools", [])
        return HarnessConfig(llm=llm_cfg, agent=agent_cfg, guardrails=guard_cfg, tools=tools)

    def load_from_file(self, path: str) -> HarnessConfig:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return self.load(data)
