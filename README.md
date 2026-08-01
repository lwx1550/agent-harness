# Agent Harness — 轻量级 Coding Agent 运行框架

一个轻量级、可编程的 CLI coding agent 运行框架，核心聚焦 **护栏安全机制**。通过声明式规则定义 agent 能做什么、不能做什么，在危险动作执行前由代码层面拦截。

## 安装

从 GitHub Release 安装：

```bash
pip install https://github.com/lwx1550/agent-harness/releases/download/v0.1.0/agent_harness-0.1.0-py3-none-any.whl
```

或从源码安装：

```bash
git clone https://github.com/lwx1550/agent-harness.git
cd agent-harness
pip install -e .
```

## 快速开始

```bash
# 安全录入 API key（通过系统钥匙串存储）
harness configure

# 运行 agent 任务
harness run "写一个打印 hello world 的 Python 脚本"

# 测试护栏规则
harness guardrail test
```

## 命令列表

| 命令 | 说明 |
|------|------|
| `harness init` | 创建默认 config.yaml |
| `harness configure` | 安全存储 API key |
| `harness run <task>` | 运行 agent 任务 |
| `harness guardrail test` | 测试护栏规则 |
| `harness config show` | 查看配置（key 脱敏显示） |
| `harness version` | 显示版本信息 |

## 护栏规则

规则在 `config.yaml` 中定义，每条规则包含：

- `pattern` — 用于匹配命令的 glob 模式
- `action_type` — 作用于哪个工具（如 `run_command`）
- `verdict` — `block`（拦截）、`approval`（需审批）、`warn`（警告）
- `reason` — 规则说明

默认规则会拦截 `rm -rf /` 等危险命令，并对数据库删除操作要求人工审批。

## 安全机制

- API key 通过操作系统钥匙串存储（Windows Credential Manager / macOS Keychain），不可用时降级为加密文件
- key 绝不进入源码、Git 历史或日志
- 护栏规则由代码强制执行，而非依赖 LLM 提示词自控
- 高风险动作触发 HITL（Human-in-the-Loop）人工审批

## 机制演示

```bash
python demo/mechanism_demo.py
```

在 mock LLM 下演示三种行为：
1. 护栏拦截危险动作
2. 反馈闭环驱动自我修正
3. 护栏引擎的确定性行为

## 目录结构

```
src/harness/
  cli.py              CLI 入口
  agent.py            Agent 主循环
  llm/                LLM 抽象层（OpenAI + Mock）
  tools/              工具系统（读写文件、执行命令）
  guardrails/         护栏引擎 + HITL + 审计日志
  feedback/           测试结果解析器
  memory/             上下文管理器
  config/             配置加载器
  credentials.py      凭据安全管理
tests/                单元测试（43 个，全部基于 mock LLM）
demo/                 机制演示脚本
```

## 已知限制

- 需要 Python 3.9+
- 仅支持 OpenAI 兼容 API 格式
- 暂不支持流式输出
- 护栏规则启动时加载，不支持热更新

## 在线发布

GitHub Release: https://github.com/lwx1550/agent-harness/releases/tag/v0.1.0

