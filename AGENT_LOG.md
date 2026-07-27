# AGENT_LOG

## 2026-07-27

### Session 1: Project Setup

- **Skills used:** brainstorming, writing-plans, subagent-driven-development
- **Key decisions:** Selected Project A (Coding Agent Harness), Python tech stack, CLI-only distribution via GitHub Releases, guardrails as the deep-dive dimension
- **SPEC.md:** Written via brainstorming, committed at `332e88d`
- **PLAN.md:** Written via writing-plans with 17 tasks across 5 worktrees, committed at `8208828`

### Worktree 1: core-infrastructure (Tasks 1-4)

- **Task 1 (Scaffold):** Subagent Ohm created project structure. Fixed pyproject.toml BOM issue and hatchling build config. Committed at `c0a2e6c`
- **Task 2 (Config):** Subagent Helmholtz created test file but was slow on implementation. I completed the implementation. Tests passed. Committed at `a32086d`
- **Task 3 (LLM):** Subagent Dirac wrote all files. Fixed missing httpx dependency. Tests passed. Committed at `394e875`
- **Task 4 (Data Models):** Wrote directly. Tests passed. Committed at `e91bd45`
- **Merged to master**

### Worktree 2: guardrails (Tasks 5-7)

- **Task 5 (Engine):** Wrote engine with fnmatch pattern matching. Fixed test bugs (action_type mismatch). All 6 engine tests pass.
- **Task 6 (HITL):** Wrote state machine with skip-for-session support. 5 tests pass.
- **Task 7 (Audit):** Wrote JSONL audit logger. Fixed temp directory issue. 2 tests pass.
- **Committed at `98f6773`. Merged to master.**

### Worktree 3: tools-feedback (Tasks 8-10)

- **Task 8 (Tools):** Tool base, registry, builtins (read_file, write_file, run_command, run_test). 6 tests.
- **Task 9 (Feedback):** TestResultParser with regex-based parsing. 3 tests.
- **Task 10 (Memory):** ContextManager with token truncation. Fixed truncation edge case. 3 tests.
- **Committed at `c815bd7`. Merged to master.**

### Worktree 4: agent-cli (Tasks 11-13)

- **Task 11 (Agent Loop):** Full agent loop with guardrail integration, HITL, audit logging. 4 tests.
- **Task 12 (CLI):** Typer-based CLI with all 6 commands. 3 tests.
- **Task 13 (Credentials):** CredentialManager with keyring + encrypted file fallback. Fixed sandbox directory issue. 3 tests.
- **Committed at `46d3293`. Merged to master.**

### Worktree 5: finishing (Tasks 14-17)

- **Task 14 (Demo):** mechanism_demo.py with 3 demonstrations. All pass.
- **Task 15 (CI):** GitHub Actions workflow with unit-test job.
- **Task 16 (Docs):** README.md written.
- **Task 17 (Build):** Makefile created.
