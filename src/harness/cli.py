import typer
from typing import Optional
from . import __version__

app = typer.Typer(name="harness")


@app.command()
def version():
    """Show version information"""
    typer.echo(f"Codex Harness v{__version__}")


@app.command()
def init():
    """Initialize project configuration"""
    from .config.loader import ConfigLoader
    import yaml
    import dataclasses

    def asdict(obj):
        if dataclasses.is_dataclass(obj):
            return {f.name: asdict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
        if isinstance(obj, list):
            return [asdict(v) for v in obj]
        return obj

    loader = ConfigLoader()
    config = loader.get_default()
    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(asdict(config), f, default_flow_style=False, allow_unicode=True)
    typer.echo("Created config.yaml. Run 'harness configure' to set up your API key.")


@app.command()
def configure(clear: bool = False, update: bool = False):
    """Configure API key securely"""
    if clear:
        try:
            import keyring
            keyring.delete_password("codex-harness", "api_key")
            typer.echo("API key cleared.")
        except Exception as e:
            typer.echo(f"Failed to clear key: {e}")
        return

    try:
        import keyring
        existing = keyring.get_password("codex-harness", "api_key")
        if existing and not update:
            typer.echo("API key already configured. Use --update to overwrite.")
            return
        key = typer.prompt("Enter your API key", hide_input=True)
        keyring.set_password("codex-harness", "api_key", key)
        typer.echo("API key stored securely.")
    except Exception as e:
        typer.echo(f"Keyring unavailable: {e}. Falling back to encrypted file.")
        key = typer.prompt("Enter your API key", hide_input=True)
        from .credentials import CredentialManager
        cm = CredentialManager()
        cm.store("api_key", key)
        typer.echo("API key stored in encrypted file.")


@app.command()
def run(task: str):
    """Run an agent task"""
    import os
    from .config.loader import ConfigLoader

    loader = ConfigLoader()
    config = loader.get_default()
    if os.path.exists("config.yaml"):
        config = loader.load_from_file("config.yaml")

    try:
        import keyring
        api_key = keyring.get_password("codex-harness", "api_key")
    except Exception:
        api_key = os.environ.get("CODEX_HARNESS_API_KEY")

    if not api_key:
        typer.echo("No API key configured. Run 'harness configure' first.", err=True)
        raise typer.Exit(1)

    from .llm.openai_client import OpenAIClient
    from .tools.registry import ToolRegistry
    from .tools.builtins import ReadFileTool, WriteFileTool, RunCommandTool
    from .agent import AgentLoop

    llm = OpenAIClient(api_key=api_key, model=config.llm.model, base_url=config.llm.base_url)
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(RunCommandTool())

    agent = AgentLoop(
        llm=llm, tool_registry=registry, guardrails=config.guardrails.rules,
        max_turns=config.agent.max_turns, timeout=config.agent.timeout,
    )
    result = agent.run(task)
    typer.echo(f"\nStatus: {result['status']}")
    typer.echo(f"Turns: {result['turns']}")
    typer.echo(f"Summary: {result['summary']}")


@app.command()
def guardrail_test():
    """Test guardrail rules against sample actions"""
    import os
    from .config.loader import ConfigLoader
    from .guardrails.models import Action
    from .guardrails.engine import Guardrail

    loader = ConfigLoader()
    config = loader.get_default()
    if os.path.exists("config.yaml"):
        config = loader.load_from_file("config.yaml")

    guard = Guardrail(config.guardrails.rules)
    test_actions = [
        Action(type="tool_call", tool="run_command", params={"command": "echo hello"}),
        Action(type="tool_call", tool="run_command", params={"command": "rm -rf /"}),
        Action(type="tool_call", tool="run_command", params={"command": "DROP DATABASE test"}),
        Action(type="finish", summary="done"),
    ]
    typer.echo(f"{'Action':<50} {'Verdict':<15}")
    typer.echo("-" * 65)
    for action in test_actions:
        v = guard.evaluate(action)
        desc = f"{action.tool} {action.params}" if action.params else action.summary
        typer.echo(f"{desc:<50} {v:<15}")


@app.command()
def config_show():
    """Show current configuration (key masked)"""
    import os
    import yaml
    import dataclasses
    from .config.loader import ConfigLoader

    loader = ConfigLoader()
    config = loader.get_default()
    if os.path.exists("config.yaml"):
        config = loader.load_from_file("config.yaml")

    def asdict(obj):
        if dataclasses.is_dataclass(obj):
            return {f.name: asdict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
        if isinstance(obj, list):
            return [asdict(v) for v in obj]
        return obj

    data = asdict(config)
    data["llm"]["api_key"] = "****"
    typer.echo(yaml.dump(data, default_flow_style=False, allow_unicode=True))


if __name__ == "__main__":
    app()
