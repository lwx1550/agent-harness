# SPEC · Agent Harness — 一个轻量级 Coding Agent 运行框架

> 项目 A：Coding Agent Harness · 基于 Superpowers 方法论开发

## 1. 问题陈述

### 1.1 要解决的问题

当前 LLM 编码智能体（如 Claude Code、Codex、Cursor 等）通常以"全功能 IDE 插件"或"云服务"形态交付，用户无法在本地按自己的规则精细控制 agent 的行为边界。当用户需要一个轻量级、可编程的 agent 运行环境时——例如在 CI 流水线中、在受限服务器上、或在需要自定义安全策略的场景——现有的工具要么太重（嵌入整个 IDE），要么安全控制过于粗放（全靠提示词约束）。

Agent Harness 解决的是这个问题：**提供一个可编程的、安全可控的 CLI agent 运行框架，让用户用声明式规则定义 agent 能做什么、不能做什么，并在危险动作前拦截。**

### 1.2 目标用户

- 在本地开发环境中使用 LLM 辅助编码的开发者
- 需要在 CI/CD 中运行自动化编码任务的工程师
- 对 agent 安全边界有严格要求的团队
- 想理解"agent 内部是如何工作的"的学习者

### 1.3 为什么值得做

当 LLM 能完成大部分编码工作时，工程师的真正价值从"写代码"转移到"定义 agent 的行为边界、验证其输出质量、处理安全风险"。Agent Harness 是对这一判断的实践：与其给 LLM 一句"注意安全"的提示词，不如写一个在代码层面拦截危险动作的护栏。

## 2. 用户故事

1. **作为开发者**，我想要在终端中直接输入任务描述，让 agent 自动完成代码编写和测试，这样我可以专注于更高层的设计决策。
2. **作为安全敏感的工程师**，我想要定义一组规则来阻止 agent 执行危险命令（如 
m -rf /），这样即使 agent 产生恶意意图也不会造成破坏。
3. **作为代码审查者**，我想要在 agent 执行可能危险的操作前得到通知并亲自确认，这样我可以在造成影响前拦截它。
4. **作为 CI 维护者**，我想要在流水线中运行 agent 完成自动化代码修复，并确信它不会越界访问敏感文件。
5. **作为 Harness 的测试者**，我想要在不连接真实 LLM 的情况下验证护栏和工具分发机制是否正常工作，这样可以快速迭代并确保可靠性。
6. **作为初学者**，我想要一个简单的初始化命令来快速启动一个 agent 项目，而不需要手动配置各种参数。

## 3. 功能规约

### 3.1 CLI 界面

| 命令 | 描述 | 输入 | 输出 | 边界条件 | 错误处理 |
|------|------|------|------|----------|----------|
| harness init | 初始化项目配置 | 无 | 创建默认 config.yaml | 已存在配置文件时询问是否覆盖 | 写入失败时报错 |
| harness configure | 安全录入 API key | 隐藏输入 | 成功/失败提示 | 已存在 key 时询问是否更新 | 系统钥匙串不可用时降级到加密文件 |
| harness run <task> | 运行 agent 执行任务 | 任务描述字符串 | 执行过程输出 + 最终结果 | 无 API key 时提示先配置；空任务描述时报错 | LLM 调用失败时重试 3 次后退出 |
| harness guardrail test | 测试护栏规则 | 无 | 规则测试报告 | 无规则时提示"无规则" | 规则文件解析失败时报错 |
| harness config show | 查看配置 | 无 | 配置内容（key 脱敏） | 无配置文件时提示"未配置" | 读取失败时报错 |
| harness version | 版本信息 | 无 | 版本号 + 许可证信息 | — | — |

### 3.2 Agent Loop（主循环）

**输入：** 任务描述字符串
**行为：**
1. 从消息历史和工具定义构建上下文
2. 调用 LLM，获取结构化响应
3. 解析响应为 Action（tool_call 或 finish）
4. 若为 finish，输出摘要并停止
5. 若为 tool_call，经护栏检查后执行
6. 将执行结果回灌给 LLM
7. 重复直到 finish 或达到最大轮数
**输出：** 执行日志 + 最终摘要
**边界条件：** 最大轮数（默认 50）、超时（默认 300s）、LLM 连续返回无效格式时的降级策略
**错误处理：** LLM 调用失败重试（指数退避）、格式解析失败最多重试 3 次后报错退出

### 3.3 工具系统

| 工具 | 参数 | 描述 | 边界条件 | 错误处理 |
|------|------|------|----------|----------|
| 
ead_file | path: str | 读取文件内容 | 文件不存在、过大（>1MB 截断） | 返回错误信息 |
| write_file | path: str, content: str | 写入文件 | 目录不存在时创建、只读文件 | 权限错误时返回错误 |
| edit_file | path: str, old: str, new: str | 替换文件中的内容 | 匹配不到 old 文本时提示 | 返回未匹配错误 |
| 
un_command | command: str, timeout: int | 执行 shell 命令 | 超时（默认 30s）、工作目录 | 返回 stdout/stderr/exit code |
| 
un_test | command: str | 运行测试（默认 pytest） | 无测试文件时提示 | 返回测试输出 |

### 3.4 护栏引擎（重点）

**输入：** Action（待执行的动作）
**行为：**
1. 遍历已注册的守卫规则
2. 按 pattern 匹配动作类型和参数
3. 返回判决：PASS / BLOCK / NEEDS_APPROVAL / WARN
4. BLOCK → 拦截，记录审计日志，返回给 LLM
5. NEEDS_APPROVAL → 进入 HITL 状态机，等待用户确认
6. WARN → 放行但记录警告
**输出：** Verdict 枚举值
**边界条件：** 空规则集时全部放行；规则优先级按定义顺序匹配
**错误处理：** 规则解析失败时跳过该规则并记录

**HITL 状态机：**
`
NEEDS_APPROVAL → 显示动作详情 [y/n/s]
  y → 放行，记审计日志
  n → 拦截，反馈给 LLM
  s → 跳过（当前会话不再询问此模式）
`

### 3.5 反馈系统

将工具执行结果转为 LLM 可读的结构化反馈文本，包含：
- 执行状态（成功/失败）
- 关键输出摘要
- 错误分类（编译错误/测试失败/超时/权限错误）

### 3.6 记忆/上下文管理

- 消息历史维护：list[dict] 形式，按 token 预算截断
- 系统提示注入：将项目约定、护栏规则、可用工具定义注入
- 工作目录上下文：当前项目结构信息

### 3.7 配置系统

配置文件 config.yaml，支持：
- LLM 供应商配置（provider / model / base_url）
- 护栏规则列表
- 启用/禁用工具
- Agent 运行参数（max_turns / timeout）

## 4. 非功能性需求

### 4.1 性能
- 工具执行超时机制：默认 30s（命令）、300s（agent 总运行）
- 上下文 token 预算硬限制，超出时按策略截断

### 4.2 安全（含凭据威胁模型）
- **凭据存储：** API key 通过系统钥匙串（Windows Credential Manager / macOS Keychain）存储，不可用时降级到加密文件
- **绝不硬编码：** key 不进入源码、Git 历史、日志、终端 history
- **命令行输入：** configure 命令使用隐藏输入，避免 shell history 泄露
- **护栏机制：** 危险动作在代码层面拦截，不依赖 LLM 自控
- **威胁模型：**
  - 威胁 T1：凭据泄露（通过共享屏幕、日志、备份）→ 对策：不存储明文、不写日志
  - 威胁 T2：agent 越权执行危险命令 → 对策：护栏规则引擎 + HITL
  - 威胁 T3：配置文件泄露 → 对策：key 不存于 config.yaml
- **审计日志：** 所有被拦截和需审批的动作记录到审计日志

### 4.3 可用性
- 单命令安装：pip install agent-harness
- 首次运行引导：harness configure 引导用户录入 key
- 清晰的错误信息和帮助文本

### 4.4 可观测性
- 详细执行日志（含时间戳、动作、结果、耗时）
- 审计日志（所有被拦截/需审批的动作）

## 5. 系统架构

### 5.1 组件图

`
+---------------------------------------------------+
|                     CLI (typer)                    |
|   init  configure  run  guardrail-test  config-show|
+--------------------------+------------------------+
                           |
+--------------------------v------------------------+
|                    Agent Loop                      |
|  (context -> call LLM -> parse -> guardrail -> exec)|
+--+-----------+-----------+-----------+------------+
   |           |           |           |
   v           v           v           v
+------+ +----------+ +----------+ +----------+
| Tools | |Guardrails| | Feedback | | Memory   |
|registry| | engine   | | parser   | | manager  |
+--+---+ +----------+ +----------+ +----------+
   |
   v
+-----------------------------------------------+
|              LLM Abstraction Layer             |
|  (OpenAIClient / MockLLMClient / CustomLLMClient)|
+-----------------------------------------------+
`

### 5.2 数据流

`
用户输入任务 -> Agent Loop 开始
  -> LLM 返回 JSON 动作
  -> 解析为 Action
  -> Guardrail.evaluate(action)
    -> BLOCKED: 反馈给 LLM，继续
    -> NEEDS_APPROVAL: 用户确认/拒绝
    -> PASS: 执行
  -> Tool.execute(params)
  -> 结果回灌给 LLM
  -> LLM 返回 finish 或下一个动作
`

### 5.3 外部依赖

- OpenAI API（或兼容接口的 LLM 供应商）
- keyring（跨平台钥匙串访问）
- 可选：pytest（测试运行）

## 6. 数据模型

### 6.1 Action

`python
@dataclass
class Action:
    type: str          # "tool_call" | "finish"
    tool: str | None   # 工具名称
    params: dict       # 工具参数
    thought: str       # LLM 的推理过程
`

### 6.2 Verdict

`python
class Verdict(Enum):
    PASS = "pass"
    BLOCK = "block"
    NEEDS_APPROVAL = "approval"
    WARN = "warn"
`

### 6.3 GuardRule

`python
@dataclass
class GuardRule:
    pattern: str        # 匹配模式（glob/regex）
    action_type: str    # 匹配的动作类型
    verdict: str        # "block" | "approval" | "warn"
    reason: str         # 拦截理由
`

### 6.4 ToolResult

`python
@dataclass
class ToolResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration: float
`

## 7. 凭据与分发设计

### 7.1 凭据存储

- **主方案：** 通过 keyring 库使用操作系统钥匙串（Windows Credential Manager / macOS Keychain / Linux Secret Service）
- **降级方案：** 加密文件 ~/.config/agent-harness/credentials.enc（AES-GCM 加密，密钥由用户密码派生）
- **录入流程：** harness configure -> 隐藏输入 -> 写入钥匙串
- **查看：** harness config show -> 显示 pi_key: ****（不暴露明文）
- **更新：** 再次运行 harness configure -> 覆盖旧 key
- **清除：** harness configure --clear -> 删除钥匙串中的条目
- **加载方式：** 运行时从钥匙串读取，不写入环境变量或 .env（除非用户明确选择）

### 7.2 分发

- **形态：** PyPI 包（pip install agent-harness） + GitHub Releases（预构建二进制）
- **GitHub Releases：** 每个版本发布时附带预构建的 Python 包（wheel + source dist）
- **目标平台：** Windows / macOS / Linux（Python 3.9+）
- **安全配置：** 安装后运行 harness configure 按引导录入 key
- **已知限制：** 需要 Python 3.9+ 运行环境；Windows 下需要安装 Visual C++ Redistributable

## 8. 技术选型与理由

| 层面 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.9+ | 用户指定；生态丰富；跨平台；适合 CLI 工具 |
| CLI 框架 | typer | 基于 click，类型注解驱动，自动生成 help 文档 |
| LLM 调用 | httpx | 异步 HTTP 客户端，支持 OpenAI API 格式 |
| 钥匙串 | keyring | 跨平台统一接口，支持所有主流操作系统 |
| 测试 | pytest | 行业标准，清晰易用 |
| 打包 | hatchling + PyPI | 轻量、现代 Python 打包方案 |
| 配置格式 | YAML (ruamel.yaml) | 人类可读，支持注释 |
| LLM 供应商 | OpenAI API 兼容 | 可接入 OpenAI / DeepSeek / 本地模型等 |

## 9. 领域与机制设计

### 9.1 领域分析（Coding Agent）

| 机制维度 | 该领域的具体表现 | 实现方式 |
|----------|------------------|----------|
| 动作/工具 | 读写文件、执行 shell、运行测试 | ToolRegistry + 内置工具实现 |
| 客观反馈信号 | 测试结果、lint 输出、exit code | TestResultParser 结构化解析 |
| 危险动作 | 删除文件、危险 shell 命令、修改敏感配置 | Guardrail 规则引擎 + HITL |
| 记忆 | 项目约定、历史决策、代码库知识 | 会话内消息历史 + token 截断 |

### 9.2 重点深入维度：治理/护栏

选择护栏作为重点维度，理由：

1. **纯代码逻辑**：护栏的匹配->判决->拦截链路完全由代码控制，不依赖 LLM 能力
2. **确定性可测试**：guardrail.evaluate(Action("rm -rf /")) 永远返回 BLOCK，无需网络和 LLM
3. **工程价值最高**：代码级拦截 vs 提示词约束，是评审中最核心的区分点
4. **边界清晰**：规则定义->匹配引擎->HITL 状态机->审计日志，是一条完整的工程链路

### 9.3 机制代码化实现

护栏的每个环节都实现为可独立测试的代码：

- GuardRule 数据类：规则定义
- Guardrail.evaluate()：匹配引擎，遍历规则返回判决
- HITLStateMachine：交互式审批状态机
- AuditLogger：审计日志记录
- 以上全部可在 mock LLM 下用确定性单元测试验证

## 10. 验收标准

| 功能 | 验收标准 |
|------|----------|
| CLI 界面 | 全部命令可运行，输出符合预期格式 |
| Agent Loop | 能在 mock LLM 下跑通完整 cycle（context -> LLM -> parse -> execute -> feedback -> finish） |
| 工具系统 | 每个工具在 mock LLM 驱动下可执行并返回结果 |
| 护栏引擎 | 传入危险动作返回 BLOCK；传入安全动作返回 PASS；HITL 流程可交互 |
| 反馈系统 | 测试输出可被解析为结构化反馈，并回灌给 mock LLM |
| 凭据存储 | key 可安全录入、查看（脱敏）、更新、清除；不进入 Git |
| 分发 | pip install 可安装；harness run 可运行 |
| 测试覆盖率 | 核心机制（护栏、工具分发、agent loop 骨架）有 mock-LLM 驱动的单元测试 |
| 机制演示 | mock LLM 下可复现：护栏拦截危险动作、反馈闭环修正行为、护栏重点维度确定性行为 |

## 11. 风险与未决问题

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| R1: LLM 返回格式不稳定 | Agent Loop 解析失败 | 格式解析有多轮重试 + 降级策略 |
| R2: 钥匙串在某些 Linux 环境不可用 | 凭据无法安全存储 | 降级到加密文件方案 |
| R3: 护栏规则覆盖不全 | 危险动作漏过 | 默认规则集 + 可扩展性；HITL 作为兜底 |
| R4: 沙箱执行在 Windows 上行为差异 | 跨平台兼容性问题 | 平台适配层 + CI 多平台测试 |
| R5: 项目规模超出预期 | 无法按时完成 | 核心功能优先，扩展功能后置 |

**未决问题：**
- Q1: 是否要支持多 LLM 供应商切换（openai / deepseek / 本地 ollama）？-> 当前设计通过 base_url 配置支持兼容 OpenAI API 的供应商，暂不实现自定义协议。
- Q2: 是否要支持流式输出？-> 初期仅支持非流式，简化实现。后续可选。
- Q3: 护栏规则是否支持热加载？-> 初期仅启动时加载，需重启生效。
