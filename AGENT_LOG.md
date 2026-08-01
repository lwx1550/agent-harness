# AGENT_LOG

## 2026-07-27

### Session 1: Project Setup

- **Skills used:** brainstorming, writing-plans, subagent-driven-development
- **Key decisions:** Selected Project A (Coding Agent Harness), Python tech stack, CLI-only distribution via GitHub Releases, guardrails as the deep-dive dimension
- **SPEC.md:** Written via brainstorming, committed at `332e88d`
- **PLAN.md:** Written via writing-plans with 17 tasks across 5 worktrees, committed at `8208828`

### Worktree 1: core-infrastructure (Tasks 1-4)

- **Task 1 (Scaffold):** Created project structure, pyproject.toml, __init__.py files. Fixed BOM issue and hatchling build config. Committed at `c0a2e6c`
- **Task 2 (Config):** ConfigLoader with default guardrail rules. 3 tests. Committed at `a32086d`
- **Task 3 (LLM):** LLMClient abstract base, MockLLMClient, OpenAIClient. 4 tests. Committed at `394e875`
- **Task 4 (Data Models):** Action, Verdict, GuardRule dataclasses. 4 tests. Committed at `e91bd45`
- **Merged to master**

### Worktree 2: guardrails (Tasks 5-7)

- **Task 5 (Engine):** Guardrail with fnmatch pattern matching. Fixed action_type matching bug. 6 tests.
- **Task 6 (HITL):** HITLStateMachine with skip-for-session. 5 tests.
- **Task 7 (Audit):** AuditLogger with JSONL format. Fixed sandbox directory issue. 2 tests.
- **Committed at `98f6773`. Merged to master.**

### Worktree 3: tools-feedback (Tasks 8-10)

- **Task 8 (Tools):** Tool base, ToolRegistry, built-in tools (read/write/run). 6 tests.
- **Task 9 (Feedback):** TestResultParser with regex parsing. 3 tests.
- **Task 10 (Memory):** ContextManager with token truncation. 3 tests.
- **Committed at `c815bd7`. Merged to master.**

### Worktree 4: agent-cli (Tasks 11-13)

- **Task 11 (Agent Loop):** Full agent loop with guardrail, HITL, audit integration. 4 tests.
- **Task 12 (CLI):** Typer CLI with 6 commands. 3 tests.
- **Task 13 (Credentials):** CredentialManager with keyring + encrypted fallback. 3 tests.
- **Committed at `46d3293`. Merged to master.**

### Worktree 5: finishing (Tasks 14-17)

- **Task 14 (Demo):** mechanism_demo.py with 3 demonstrations. All pass.
- **Task 15 (CI):** GitHub Actions workflow with unit-test job.
- **Task 16 (Docs):** README.md, AGENT_LOG.md written.
- **Task 17 (Build):** Makefile created.
- **Committed at `ab7f5ed`. Merged to master.**

### Post-Implementation

- Renamed project from codex-harness to agent-harness (all files updated)
- Pushed to GitHub: https://github.com/lwx1550/agent-harness
- Remaining: cold-start validation, GitHub Releases, PR workflow

## 2026-08-01

### Cold-Start Validation

- **验证对象：** GitHub Copilot（VS Code Chat），全新会话，无对话历史
- **验证范围：** Task 5（Guardrail Engine）+ Task 8（Tool System）
- **环境：** 新建空目录，仅提供 SPEC.md 和 PLAN.md，无口头解释

**Copilot 产出：**
- 实现了 `src/harness/guardrails/models.py` + `engine.py` 和 `src/harness/tools/`（base/registry/builtins）
- 14 个测试全部通过（10 guardrail + 4 tool）
- 核心逻辑正确，具备独立完成任务的能力

**发现的两处 SPEC/PLAN 缺陷：**
- `action_type` 语义歧义：PLAN.md 测试用例中混用了"语义标签"（`command`）和"工具名"（`run_command`），Copilot 按原文实现了一套 normalize 映射层，与主实现的"工具名直接匹配"不一致
- 工具数量不一致：PLAN.md Task 8 只列出 3 个工具，遗漏了 `RunTestTool`；SPEC.md §3.3 明确列出了 5 个工具

**修订：**
- PLAN.md 中所有 `action_type="command"` 统一为 `action_type="run_command"`（工具名语义）
- PLAN.md Task 8 工具列表与 SPEC.md §3.3 对齐
- 记录了完整的验证报告：`冷启动验证/SPEC_PROCESS_追加模板.md`

**关键洞察：** 主 agent 和开发者之间沉淀的隐性上下文（"action_type 就是工具名"）会让人高估 spec 的清晰度，只有冷启动验证才能暴露这类问题

- **Committed at `abdd262`**

### Handoff 准备

- 编写 STATUS.md 项目状态文档，记录当前进度、待办事项和手递说明
- **Committed at `49e4d49`**
