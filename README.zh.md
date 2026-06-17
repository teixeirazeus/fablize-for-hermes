<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh.md"><strong>简体中文</strong></a> ·
  <a href="README.pt.md">Português (BR)</a>
</p>

# fablize-for-hermes — 在 Hermes Agent 上，像寓言一样执行到底
![Banner](banner.png)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

[fablize](https://github.com/fivetaku/fablize) 针对 [Hermes Agent](https://hermes-agent.nousresearch.com/)
生态系统的移植版本。本项目将 fablize 已验证的程序——验证接地、多故事证据门控、
调查协议和提前停止预防——从 Claude Code 的插件系统迁移到 Hermes Agent 的技能系统。

**fablize** 让任何智能体 **把任务执行到底——带着证据和验证——作为程序，而非运气。**

## 起源

[fablize](https://github.com/fivetaku/fablize) 诞生于 Claude Opus 和 "Fable 5" 之间
的一场受控对比实验（19 次 A/B 测试 + 26 次真实会话，约 1,500 次工具调用）。
发现：在封闭的、有确定答案的工作（代码、逻辑、构建）上，两个模型基本持平。
差距在于*深度*——把隐含意义多推进一步——而这被证明是**模型能力**，无法注入。

但优秀工作的**程序**——真正运行你构建的东西、用证据检查点分解多步骤任务、
系统地调查错误——*确实可以迁移*。fablize 只提供那些效果已被验证的程序。

## 什么可以迁移，什么不可以

| 特质 | 可迁移？ | fablize-for-hermes 的做法 |
|---|---|---|
| 验证接地（运行并观察产出物） | ✅ | 技能第 3 节——在真实的渲染器中运行，观察输出，修复，重新运行 |
| 多故事完成 + 证据门控 | ✅ | `scripts/goals.py`——分解任务，检查点，拒绝无证据的完成 |
| 系统化调查（复现 → 假设 → 因果链） | ✅ | 技能第 2 节 + `packs/investigation-protocol.txt` |
| 提前停止预防 | ✅ | 技能基础规则：没有工具调用就不算承诺 |
| 超出预期的缺陷发现 | ❌ 不可能 | 能力问题——模型能找到就能，不能就不能 |
| 开放式创意细节 | ❌ 不可能 | 能力问题——只有在没有固定答案时才会显现 |
| 自我驱动的传播深度 | ❌ 不可能 | 能力问题——定向传播可以迁移；自我启动的深度不行 |

## 包含内容

### 1. Hermes Agent 技能 (`skills/fablize/SKILL.md`)

核心行为规则集，以 Hermes Agent 技能格式结构化（YAML 前置元数据 + Markdown）。
涵盖：

- **基础规则**——始终生效：以结果为导向，用工具结果支撑声明，禁止提前停止，
  确认破坏性操作
- **多故事循环**——分解 2 个以上故事的任务 → 带着证据完成 → 最后一个故事
  必须有验证门控
- **深度调查**——复现 → 3 个以上竞争性假设 → 追踪因果链 → 修改前后验证 →
  报告被否定的假设
- **验证接地**——运行可渲染/可执行的产出物，观察，修复，重新运行，
  然后才能宣布完成
- **能力天花板**——当模型的能力成为瓶颈时，诚实地升级

### 2. 目标引擎 (`scripts/goals.py`)

一个自包含、仅使用标准库的 Python 脚本，用于多故事分解和验证门控。
状态持久化在 `~/.hermes/fablize/` 中，跨会话存活。

```bash
goals.py create --brief "构建一个仪表板" \
  --goal "design::创建 HTML 布局" \
  --goal "implement::添加图表可视化" \
  --goal "verify::运行并验证仪表板正确渲染"
goals.py next
# ... 处理这个故事 ...
goals.py checkpoint --id G001 --status complete --evidence "布局已创建，包含侧边栏和主面板"
goals.py status
```

### 3. Packs——上下文纪律文件

- **`packs/verification-grounding-pack.txt`**——验证接地循环：运行、观察、修复、
  重新运行。适用于 HTML、SVG、游戏、UI、图表、动画。
- **`packs/investigation-protocol.txt`**——系统性调试协议：复现、竞争性假设、
  因果链、修改前后验证。

### 4. 安装脚本 (`setup/`)

- `setup.sh [--skill-only|--local|--global]`——将技能安装到 Hermes 中，
  并可选择将操作块注入 `AGENTS.md` 或 `CLAUDE.md`
- `uninstall.sh [--skill-only|--local|--global|--all]`——撤销安装

## 与原始 fablize 的差异

| 方面 | fablize（原始） | fablize-for-hermes |
|---|---|---|
| 平台 | Claude Code 插件 | Hermes Agent 技能 |
| 路由 | 通过 `hooks.json` 的 `UserPromptSubmit` 钩子 | 技能内容——智能体加载并应用匹配的纪律 |
| 提前停止 | `finish-the-work.sh` 停止钩子（JSON 转录） | 技能中的基础规则——智能体自我执行 |
| 状态目录 | `./.fablize/`（每个项目） | `~/.hermes/fablize/`（Hermes 全局，跨会话存活） |
| 脚本 | 在 `scripts/` 中——从仓库根目录运行 | 相同脚本，适配 Hermes 路径 |
| 安装 | 注入 `CLAUDE.md` | 安装为 Hermes 技能 + 可选择注入操作块 |

## 安装

### 快速安装（仅技能）

```bash
git clone https://github.com/teixeirazeus/fablize-for-hermes.git
cd fablize-for-hermes
bash setup/setup.sh --skill-only
```

然后在你的 Hermes 会话中加载技能：

```
skill_view(name='fablize')
```

### 完整安装（技能 + 始终激活的操作块）

```bash
bash setup/setup.sh --local    # 将操作块注入 ./AGENTS.md
bash setup/setup.sh --global   # 将操作块注入 ~/.claude/CLAUDE.md
```

### 卸载

```bash
bash setup/uninstall.sh --all
```

## 行为说明

- **触发方式：** 加载 `fablize` 技能，或当智能体检测到 2 个以上故事、
  调试任务或可渲染产出物时内联触发
- **2 个以上故事** → 通过 `goals.py` 分解 + 验证门控
- **调试** → 调查协议（复现 → 假设 → 因果链）
- **可渲染产出物** → 验证接地（运行 → 观察 → 修复 → 重新运行）
- **困难任务** → 自适应思考 + 卡住时升级到更强模型
- **能力天花板** → 诚实地升级（框架不会伪装能力）

## 诚实的局限性

- 它无法提升模型能力。开放式创意质量和自我驱动的发现超出了它的范围——
  这是模型选择的问题，不是框架能解决的。
- 效果数据来自原始 fablize 在小范围内的自我测量。方向是可靠的，
  但具体数字不保证精确。
- 提前停止规则依赖智能体的自我执行，而不是确定性的钩子。
  这是一个指导原则，而非绝对的保障。

## 许可证

MIT——与原始 fablize 相同。fivetaku 的原始 fablize 使用 MIT 许可证。
本移植版将设计和程序适配到 Hermes Agent 生态系统。
