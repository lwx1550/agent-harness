# SPEC_PROCESS · 规约与计划生成过程

> 记录与 Superpowers 协作生成 SPEC 和 PLAN 的过程。

## 一、Brainstorming 关键节点

### 节点 1：选择项目方向

开始时我面临 A（Coding Agent Harness）和 B（应用类项目）的选择。在阅读完通用要求和两份项目文件后，我选择了 A，因为它更符合本课程"当 LLM 能完成大部分编码工作时，工程师的价值在哪里"的核心命题。

智能体追问的关键问题：
- "你心目中这个 Coding Agent Harness 的目标用户和使用场景是什么样的？"
- 我的回答明确了 CLI 工具、Python 技术栈、GitHub Releases 分发形态。

### 节点 2：确定深入维度

智能体提出了四个候选方向（治理/护栏、反馈闭环、工具分发、记忆/上下文），并推荐了治理/护栏方向，理由是：
1. 纯代码逻辑，不依赖 LLM
2. 最容易写确定性单元测试
3. 边界清晰，不容易做"过"
4. 这是 Harness 区别于"套壳提示词"的核心价值

我接受了这个建议。

### 节点 3：架构设计确认

智能体分块呈现了 9 个模块的设计（LLM 抽象层、Agent Loop、工具系统、护栏引擎、HITL 状态机、反馈系统、记忆/上下文、配置系统、CLI 界面），我逐块确认。没有需要调整的地方。

## 二、关键迭代节选

### 迭代 1：从"通用框架"到"CLI 工具"

**原始设想：** 做一个带 Web Dashboard 的通用 Agent 运行框架。
**AI 追问：** "目标用户和使用场景是什么样的？"
**我的修正：** 改为纯 CLI 工具 + GitHub Releases 分发，不开发 WebUI。这样更聚焦，工作量可控。

### 迭代 2：从"技术栈待定"到"Python"

**原始设想：** 技术栈未定，考虑 TypeScript/Go/Rust/Python。
**AI 追问：** "技术栈你有什么偏好吗？"
**我的决定：** Python。生态成熟，适合 CLI 工具，团队熟悉。

### 迭代 3：从"六个维度平均用力"到"护栏深入"

**原始设想：** 六个维度都做差不多的深度。
**AI 推荐：** 选择护栏作为重点维度，理由是它在"移除 LLM 后仍可用单测验证"的判据下表现最好。
**我的决定：** 接受这个建议。实际开发中这个决定被证明是正确的——护栏模块的 6 个测试全部可以在不依赖网络和 LLM 的情况下运行。

## 三、AI 建议与人工修正

### AI 提出而被我采纳的建议
1. 选择护栏作为深入维度（推荐理由充分）
2. 使用 fnmatch 做模式匹配（比正则简单，足够用）
3. HITL 状态机加入"跳过（skip for session）"功能

### 我推翻或修正的 AI 建议
1. **代码组织方式：** AI 倾向于将所有 guardrail 代码放在一个文件中，我坚持拆分为 models.py / engine.py / hitl.py / audit.py 四个独立文件，职责更清晰。
2. **测试方式：** AI 最初写的 guardrail 测试使用了模糊匹配，我改为精确的确定性断言，确保每次运行结果一致。
3. **默认配置：** AI 没有提供默认的护栏规则，我要求添加了 5 条内置规则（rm -rf /、DROP DATABASE、format C: 等）。

## 四、对 Brainstorming 技能的反思

### 做得好的地方
1. **追问有深度：** AI 没有停留在表面，而是追问了"为什么选这个方向"、"目标用户是谁"等关键问题，帮助我理清了思路。
2. **分块呈现：** 设计文档分 9 个模块逐块展示，每块确认后再继续，避免了一次性信息过载。
3. **推荐机制清晰：** 在推荐护栏方向时，AI 给出了四个维度的对比表格，有明确的比较标准。

### 不满意的地方
1. **缺少风险评估：** Brainstorming 阶段没有主动提示项目规模风险和可能遇到的困难，导致开发过程中才发现一些边界情况（如 Windows 钥匙串在沙箱中不可用）。
2. **技术细节不够深入：** 在护栏引擎的匹配算法上，AI 最初的实现使用了简单的字符串包含匹配，没有考虑到 glob 模式的优先级和边界情况，需要我在后续修正。

## 五、冷启动验证记录（§4.5）—— 实际记录

> 验证时间：2026-08-01
> 主开发 agent：OpenAI Codex
> 冷启动 agent：GitHub Copilot（VS Code Chat）
> 验证的 task：Task 5（Guardrail Engine）、Task 8（Tool System）

### 验证设置

- 新建空目录，仅包含 SPEC.md 和 PLAN.md
- Copilot 启动全新会话，无任何对话历史
- 未提供任何口头解释或补充信息

### Copilot 的提问（暂停点）

#### 提问 1：无显式提问，但遇到 action_type 不匹配后自行修复

**Copilot 做了什么：** 在实现 Guardrail.evaluate() 时，发现 PLAN.md 中测试用例使用 ction_type="command"，但 Action 的 tool 字段是 "run_command"，两者不匹配。Copilot 没有暂停提问，而是自行添加了 _normalize_action_type 方法，将 un_command 映射为 "command"。

**暴露了什么 spec 缺陷：** PLAN.md 中 GuardRule 的 action_type 字段语义不明确——它到底是"工具名"还是"动作类别标签"？PLAN.md 测试用例里混用了这两种语义。实际的 Codex 实现选择了"工具名"语义（ction_type="run_command"），并在测试中修正了 PLAN.md 的写法。但 PLAN.md 原文没有被同步更新，导致 Copilot 按原文实现了另一套语义。

**你的回答：** 无需回答——Copilot 自行修复了。但修复方式（normalize 映射）与你的实现（直接用工具名匹配）不同。

#### 提问 2：未暂停提问，但遗漏了 RunTestTool

**Copilot 做了什么：** 只实现了 ReadFileTool、WriteFileTool、RunCommandTool 三个工具，没有实现 RunTestTool。

**暴露了什么 spec 缺陷：** PLAN.md Task 8 章节只列出了三个内置工具，而 SPEC.md 功能规约表（§3.3）列出了 5 个工具含 un_test。Copilot 可能只读了 Task 8 的章节，没有回溯 SPEC.md 的完整工具清单。说明 PLAN 和 SPEC 之间的信息存在重复但不一致的风险。

**你的回答：** 无需回答。

### 理解偏差

#### 偏差 1：action_type 的语义分歧（核心偏差）

**Copilot 的实现：** 在 engine.py 中新增 _normalize_action_type 静态方法，将 un_command 映射为 "command"，然后在匹配时同时检查 
ormalized_type 和 ction.tool。这是一个"动作类别标签"语义。

**你的原意（Codex 实现）：** 在 engine.py 中用 _match_action_type 方法，直接比较 ule_type == tool 或 nmatch(tool, rule_type)。测试中 GuardRule 使用 ction_type="run_command"（工具名语义）。没有 normalize 层。

**原因分析：** 是 PLAN.md 写错了。PLAN.md 的测试用例中 GuardRule 使用了 ction_type="command" 这个语义标签，但实际工具名是 un_command。Codex 在实现时修正了测试用例（改为 ction_type="run_command"），但没有回写 PLAN.md。Copilot 严格按 PLAN.md 原文实现，导致了另一套设计。

#### 偏差 2：工具数量不一致

**Copilot 的实现：** 3 个内置工具（read_file, write_file, run_command）
**你的原意：** 4 个内置工具（read_file, write_file, run_command, run_test）
**原因分析：** PLAN.md Task 8 只列出了 3 个工具，但 SPEC.md §3.3 列出了 5 个。Copilot 只读了 Task 8 章节。SPEC 和 PLAN 之间的信息不对称。

### 产出对比

| 维度 | Copilot 的产出 | 你的实现（Codex） | 差异分析 |
|------|---------------|---------|---------|
| 代码结构 | models.py + engine.py | models.py + engine.py | 一致 |
| 匹配算法 | 有 normalize 层，支持语义标签 | 直接用工具名匹配 + fnmatch | Copilot 的方案更灵活但多了一层间接 |
| 工具数量 | 3 个 | 4 个（含 RunTestTool） | PLAN 信息不完整 |
| 测试覆盖 | 10 个 guardrail 测试 + 4 个 tool 测试，14 passed | 10 个 guardrail 测试 + 6 个 tool 测试 | Copilot 的 tool 测试更少 |
| 错误处理 | 基本一致 | 基本一致 | 无显著差异 |
| 边界条件 | 基本一致 | 基本一致 | 无显著差异 |

### 对 SPEC / PLAN 的修订

#### 修订 1：PLAN.md Task 5 测试用例中 action_type 的写法

**修订前的原文（PLAN.md Task 5 Step 1）：**
`
GuardRule(pattern="rm -rf *", action_type="command", verdict="block", reason="Dangerous")
`

**修订后：**
`
GuardRule(pattern="rm -rf *", action_type="run_command", verdict="block", reason="Dangerous")
`

**修订原因：** ction_type 字段应与工具名一致（un_command），而非语义标签（command）。冷启动验证中 Copilot 按原文的 "command" 实现了一套 normalize 映射层，与主实现的"工具名直接匹配"不一致。统一为工具名语义，消除歧义。

#### 修订 2：PLAN.md Task 8 应明确列出所有内置工具

**修订原因：** Copilot 只实现了 3 个工具，遗漏了 RunTestTool。PLAN.md Task 8 的工具列表应与 SPEC.md §3.3 保持一致，明确列出 read_file、write_file、edit_file、run_command、run_test 五个工具。

### 冷启动验证结论

**总体结论：** SPEC 和 PLAN 的质量足够让一个陌生 agent 独立完成核心实现，但存在两处可修复的歧义。

**最重要的发现：** ction_type 字段的语义在整个文档体系中不一致——PLAN.md 混用了"语义标签"（command）和"工具名"（run_command），而实际的 Codex 实现选择了"工具名"语义并悄悄修正了测试。这个不一致在单人开发中不会被发现，只有冷启动验证才暴露出来。这也印证了 §4.5 的设计意图：主 agent 和开发者之间沉淀的隐性上下文（"action_type 就是工具名"）会让人高估 spec 的清晰度。

**Copilot 能否独立完成：** 可以。14 个测试全部通过，核心逻辑正确。遇到 PLAN.md 的歧义时，Copilot 选择了自行修复而非暂停提问——这既是优点（自主性强）也是缺点（没有暴露 spec 问题给人类）。

