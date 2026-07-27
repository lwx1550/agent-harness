import pytest
from harness.tools.base import Tool, ToolResult
from harness.tools.registry import ToolRegistry
from harness.tools.builtins import ReadFileTool, WriteFileTool, RunCommandTool


def test_tool_registry_register():
    registry = ToolRegistry()
    tool = ReadFileTool()
    registry.register(tool)
    assert registry.get("read_file") is tool


def test_tool_registry_list():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    names = [t.name for t in registry.list_tools()]
    assert "read_file" in names
    assert "write_file" in names


def test_tool_not_found():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")


def test_tool_to_llm_format():
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    fmt = registry.to_llm_format()
    assert isinstance(fmt, list)
    assert fmt[0]["function"]["name"] == "read_file"


def test_read_file_not_found():
    tool = ReadFileTool()
    result = tool.execute({"path": "/nonexistent/path/file.txt"})
    assert result.success is False
    assert result.exit_code == 1


def test_run_command_echo():
    tool = RunCommandTool()
    result = tool.execute({"command": "echo hello"})
    assert result.success is True
    assert "hello" in result.stdout
