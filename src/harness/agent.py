import time
from typing import List, Optional
from .llm.client import LLMClient
from .guardrails.models import Action, GuardRule
from .guardrails.engine import Guardrail
from .guardrails.hitl import HITLStateMachine
from .guardrails.audit import AuditLogger
from .tools.registry import ToolRegistry
from .memory.manager import ContextManager


class AgentLoop:
    def __init__(self, llm: LLMClient, tool_registry: ToolRegistry,
                 guardrails: List[GuardRule], max_turns: int = 50,
                 timeout: int = 300, audit_logger: Optional[AuditLogger] = None,
                 hitl: Optional[HITLStateMachine] = None):
        self.llm = llm
        self.tools = tool_registry
        self.guardrail = Guardrail(guardrails)
        self.max_turns = max_turns
        self.timeout = timeout
        self.audit = audit_logger or AuditLogger()
        self.hitl = hitl or HITLStateMachine()
        self.memory = ContextManager()

    def run(self, task: str) -> dict:
        start_time = time.time()
        self.memory.add("system", "You are a coding agent. You can use tools to accomplish tasks. "
                                   "Respond with a JSON action.")
        self.memory.add("user", task)
        steps = []
        turns = 0

        while turns < self.max_turns:
            if time.time() - start_time > self.timeout:
                return {"status": "timeout", "turns": turns, "steps": steps, "summary": "Timed out"}

            try:
                response = self.llm.chat(self.memory.get_messages(), self.tools.to_llm_format())
            except Exception as e:
                return {"status": "error", "error": str(e), "turns": turns, "steps": steps}

            if response.type == "finish":
                steps.append({"type": "finish", "summary": response.summary, "status": "completed"})
                return {"status": "completed", "turns": turns + 1, "steps": steps, "summary": response.summary}

            action = Action(type="tool_call", tool=response.tool, params=response.params, thought=response.thought)
            verdict = self.guardrail.evaluate(action)
            step = {"type": "tool_call", "tool": action.tool, "params": action.params,
                    "verdict": verdict, "status": "executed"}

            if verdict == "block":
                self.audit.log(action, verdict, "Blocked by guardrail")
                step["status"] = "blocked"
                self.memory.add("user", f"Action {action.tool}({action.params}) was BLOCKED by guardrail.")
                steps.append(step)
                turns += 1
                continue

            if verdict == "approval":
                action_detail = f"{action.tool} {action.params}"
                if not self.hitl.confirm(action_detail, verdict, "Requires approval"):
                    step["status"] = "blocked"
                    self.memory.add("user", f"Action {action.tool}({action.params}) was REJECTED by user.")
                    steps.append(step)
                    turns += 1
                    continue

            try:
                tool = self.tools.get(action.tool)
                result = tool.execute(action.params or {})
                step["result"] = {"success": result.success, "stdout": result.stdout[:500],
                                  "stderr": result.stderr[:500], "exit_code": result.exit_code}
                feedback = f"Tool {action.tool} {'succeeded' if result.success else 'failed'}. "
                self.memory.add("user", feedback)
            except KeyError as e:
                step["status"] = "error"
                self.memory.add("user", f"Tool '{action.tool}' not found: {e}")
            except Exception as e:
                step["status"] = "error"
                self.memory.add("user", f"Tool execution error: {e}")

            steps.append(step)
            turns += 1

        return {"status": "max_turns_reached", "turns": turns, "steps": steps, "summary": "Max turns reached"}
