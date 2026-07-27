import os
import subprocess
import time
from .base import Tool, ToolResult


class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a file"
    parameters = {
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Path to file"}},
        "required": ["path"],
    }

    def execute(self, params: dict) -> ToolResult:
        path = params["path"]
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(1024 * 1024)
            return ToolResult(success=True, stdout=content)
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1)


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write content to a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }

    def execute(self, params: dict) -> ToolResult:
        path = params["path"]
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(params["content"])
            return ToolResult(success=True, stdout=f"Written {len(params['content'])} bytes to {path}")
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1)


class RunCommandTool(Tool):
    name = "run_command"
    description = "Run a shell command"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["command"],
    }

    def execute(self, params: dict) -> ToolResult:
        start = time.time()
        try:
            result = subprocess.run(
                params["command"], shell=True, capture_output=True, text=True,
                timeout=params.get("timeout", 30),
            )
            duration = time.time() - start
            return ToolResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, stderr="Command timed out", exit_code=124, duration=time.time() - start)
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1, duration=time.time() - start)


class RunTestTool(Tool):
    name = "run_test"
    description = "Run tests using pytest"
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Test command", "default": "pytest"},
            "path": {"type": "string", "description": "Test path", "default": "tests/"},
        },
        "required": [],
    }

    def execute(self, params: dict) -> ToolResult:
        cmd = f"{params.get('command', 'pytest')} {params.get('path', 'tests/')} -v"
        start = time.time()
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            duration = time.time() - start
            return ToolResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration=duration,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, stderr="Test timed out", exit_code=124, duration=time.time() - start)
        except Exception as e:
            return ToolResult(success=False, stderr=str(e), exit_code=1, duration=time.time() - start)
