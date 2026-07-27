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
