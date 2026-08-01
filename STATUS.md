# STATUS · Agent Harness 项目状态

> 最后更新：2026-08-02
> GitHub：https://github.com/lwx1550/agent-harness

---

## 一、已完成的工作

### 设计文档
- SPEC.md（11 章节，含领域与机制设计）
- PLAN.md（17 个任务，全部 checkbox 已标记完成 + commit hash）
- SPEC_PROCESS.md（含 brainstorming 记录 + 冷启动验证记录）

### 源代码（src/harness/）
| 模块 | 文件 | 说明 |
|------|------|------|
| CLI | cli.py | typer CLI，6 个命令 |
| Agent Loop | agent.py | 主循环 + guardrail/HITL/audit 集成 |
| LLM 抽象 | llm/client.py, mock_client.py, openai_client.py | 抽象基类 + mock + OpenAI |
| 工具系统 | tools/base.py, registry.py, builtins.py | 4 个内置工具 |
| 护栏引擎 | guardrails/models.py, engine.py, hitl.py, audit.py | 核心深入维度 |
| 反馈 | feedback/parser.py | 测试结果解析 |
| 记忆 | memory/manager.py | 上下文管理器 |
| 配置 | config/loader.py | YAML 配置加载 |
| 凭据 | credentials.py | keyring + 加密文件降级 |

### 测试（tests/）
- 43 个单元测试全部通过：pytest tests/ -v
- 7 个测试文件：test_agent.py, test_audit.py, test_config.py, test_credentials.py, test_feedback.py, test_guardrails.py, test_hitl.py, test_llm.py, test_memory.py, test_tools.py

### 交付物
- README.md, AGENT_LOG.md, REFLECTION.md（~2000 字）, Makefile, pyproject.toml, .gitignore
- .github/workflows/ci.yml（unit-test job，Python 3.9/3.10/3.11 矩阵）
- demo/mechanism_demo.py（3 个机制演示，可跑通）

### Git
- 20 个 commit，推送到 GitHub
- 5 个 worktree 分支：core-infrastructure, guardrails, tools-feedback, agent-cli, finishing
- 全部已合并到 master 并推送到远程

### 冷启动验证（§4.5）
- 用 GitHub Copilot（全新会话）验证了 Task 5 + Task 8
- 发现 PLAN.md 中 action_type 字段语义歧义（已修正）
- 记录已追加到 SPEC_PROCESS.md

---

## 二、剩余待办（按优先级）

### 1. WebUI 接口（硬性要求）

**来源：** 通用要求 §五.9 "必须提供应用可访问的 WebUI 接口"

**要求：** 项目当前是纯 CLI，需要添加一个可通过浏览器访问的 Web 界面。最简单的方式是用 FastAPI + 简单 HTML 页面给 harness 内核包一层 Web 接口。

**建议实现方案：**
- 新建 src/harness/webui.py（FastAPI 应用）
- 提供 POST /api/run 接口接收任务描述，返回 agent 执行结果（SSE 流式或 JSON）
- 提供 GET / 返回一个简单的 HTML 页面（内嵌在 Python 中即可），包含：任务输入框、提交按钮、执行日志展示区
- 新增 CLI 命令 harness webui 启动 Web 服务器（默认 localhost:8080）
- 在 pyproject.toml 的 dependencies 中添加 astapi 和 uvicorn
- 在 pyproject.toml 的 [project.scripts] 中添加 harness-webui = "harness.webui:main" 入口

**验收标准：** harness webui 启动后浏览器打开能输入任务、看到 agent 执行过程

**注意：** WebUI 需要 mock LLM 才能在不配置真实 API key 的情况下演示。建议在 webui 中默认使用 MockLLMClient。

### 2. PR 创建

**要求：** 5 个 worktree 分支各对应一个 GitHub PR

**操作：**
在 GitHub 上为以下 5 个分支分别创建 PR（base: master）：
- core-infrastructure
- guardrails
- tools-feedback
- agent-cli
- finishing

每个 PR 描述中标注：
- 由哪个 subagent 完成（Codex）
- 包含哪些 task
- 人工修改了哪些部分（见 SPEC_PROCESS.md 的"三、AI 建议与人工修正"）

### 3. 分发

**要求：** 通用要求 §3.2，至少选一种分发形态

**当前状态：** README 写了 pip install agent-harness 但实际未发布到 PyPI

**建议操作：**
- 选项 A（推荐）：创建 GitHub Release（在 GitHub 页面操作），上传 dist/ 下的 .whl 和 .tar.gz
- 选项 B：发布到 PyPI（需要 PyPI 账号和 token）
- README 中写清获取方式：pip install agent-harness（如果发了 PyPI）或 pip install https://github.com/lwx1550/agent-harness/releases/download/v0.1.0/agent_harness-0.1.0-py3-none-any.whl（如果只发 GitHub Release）
- README 中写清 key 在目标机器上的安全配置方式（已有 harness configure 命令，补充说明即可）

**构建命令：**
`ash
pip install build
python -m build
# 产物在 dist/ 目录
`

### 4. CI 验证

**要求：** 通用要求 §五.7 "最后一次 CI/CD 执行必须是 pass 状态"

**操作：**
- 确认 GitHub Actions 已启用（在仓库 Settings > Actions > General）
- Push 当前 master 的最新 commit 触发 CI
- 在 GitHub Actions 页面确认 unit-test job 三个 Python 版本全部通过
- 如果 CI 没跑过，可能需要检查 CI 配置是否正确（当前配置看起来没问题）

### 5. 其他小项

- **.gitignore 补充：** 确认 冷启动验证/ 目录和 opencode-install/ 目录已加入 .gitignore（这些是工作产物，不需要提交）
- **AGENT_LOG.md 更新：** 补充冷启动验证的条目

---

## 三、项目技术细节

**Python 版本：** 3.9+
**入口：** harness CLI（typer），pyproject.toml 中 [project.scripts] 配置
**测试命令：** pytest tests/ -v
**安装命令：** pip install -e .
**Mock LLM：** MockLLMClient 接受预设响应列表，不依赖网络

**关键约束：**
- 所有测试必须能用 mock LLM 跑（不依赖真实 API）
- 凭据不硬编码，不进入 Git
- TDD 是硬性要求
