# Agent Harness

A lightweight, programmable CLI coding agent harness with a focus on **guardrail safety mechanisms**. Lets you define declarative rules for what your agent can and cannot do, intercepting dangerous actions before they execute.

## Installation

```bash
pip install agent-harness
```

Or install from source:

```bash
git clone <repo-url>
cd agent-harness
pip install -e .
```

## Quick Start

```bash
# Configure your API key (stored securely via system keychain)
harness configure

# Run an agent task
harness run "write a Python script that prints hello world"

# Test guardrail rules
harness guardrail test
```

## Commands

| Command | Description |
|---------|-------------|
| `harness init` | Create default config.yaml |
| `harness configure` | Securely store API key |
| `harness run <task>` | Run an agent task |
| `harness guardrail test` | Test guardrail rules |
| `harness config show` | Show configuration (key masked) |
| `harness version` | Show version |

## Guardrail Rules

Rules are defined in `config.yaml`. Each rule has:

- `pattern` — glob pattern to match against commands
- `action_type` — which tool to apply to (e.g., `run_command`)
- `verdict` — `block`, `approval`, or `warn`
- `reason` — explanation for the rule

Default rules block dangerous commands like `rm -rf /` and require approval for database drops.

## Security

- API keys are stored via OS keychain (Windows Credential Manager / macOS Keychain), with encrypted file fallback
- Keys never enter source code, Git history, or logs
- Guardrail rules are enforced in code, not by LLM prompts
- HITL (Human-in-the-Loop) approval for high-risk actions

## Mechanism Demo

```bash
python demo/mechanism_demo.py
```

Demonstrates three behaviors using mock LLM:
1. Guardrail blocks dangerous action
2. Feedback loop for self-correction
3. Deterministic guardrail behavior

## Directory Structure

```
src/harness/
  cli.py              CLI entry point
  agent.py            Agent loop
  llm/                LLM abstraction (OpenAI + Mock)
  tools/              Tool system (read/write/run)
  guardrails/         Guardrail engine + HITL + audit
  feedback/           Test result parser
  memory/             Context manager
  config/             Config loader
  credentials.py      Secure credential manager
tests/                Unit tests
demo/                 Mechanism demo
```

## Known Limitations

- Python 3.9+ required
- Only OpenAI-compatible API format supported
- Non-streaming only
- Guardrail rules are loaded at startup (no hot-reload)

## License

MIT


