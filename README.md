# Perspectives

把一本书、一个人、或一套方法论的**思维方式**，蒸馏成能被 AI 直接调用的视角；以及把反复出现的手工活，固化成能被 AI 直接调用的工具。

不是角色扮演，不是语录合集，不是提示词收藏。这里的东西都是一份**可加载的认知结构**——怎么想、怎么判断、什么不做、以及做不到什么。

## 收录什么

两类，都是标准 Skill 目录，都能被 WorkBuddy / Claude Code / Codex CLI 等 agent harness 直接加载：

| 类型 | 命名 | 是什么 |
|---|---|---|
| **视角 perspective** | `[name]-perspective` | 一套思维方式。用第一人称以该框架回应，用于分析、审视、复盘 |
| **工具 tool** | 按功能命名 | 一个可复用的处理流程。输入一段材料，输出一个可验证的结果 |

一个 Skill 的目录结构：

```
[name]/
├── SKILL.md          触发时加载：身份/原理 + 判断规则 + 加载路由
├── references/       按需展开：清单 / 手册 / 分场景档位
└── scripts/          可选：确定性执行的脚本（零依赖优先）
```

平时只占几百 token（frontmatter 常驻，正文触发才读，references 用到才展开）——这样它能在你每次提问时自动挂载，而不会挤占对话空间。

## 已收录

### 视角

| 视角 | 来源材料 | 内容 |
|---|---|---|
| [sunzi-perspective](sunzi-perspective/) | 《孙子兵法》十三篇原文 + 清华《珍藏版》 | 7 个心智模型（各含失效条件）、12 条决策启发式、3 份失败清单、5 组内在矛盾、46 案战例复核、8 条用法反模式、6 条验证判据 |

### 工具

| 工具 | 解决什么 | 内容 |
|---|---|---|
| [zh-humanizer](zh-humanizer/) | 中文文本去 AI 味 / 发布前自查 | 18 类 AI 味分级清单（T1 一眼定罪 / T2 组合判定 / T3 统计层）、6 项量化阈值、4 种改写手法、8 个文体档位、8 条反模式、6 条验证判据 |
| [ui-humanizer](ui-humanizer/) | 界面 / 前端去 AI 味：紫色渐变、emoji 当图标、英文报错直出 | 3 类硬指纹（AI 默认色板 / emoji 图标 / 技术信息泄漏）+ 3 类软指纹、色相密度判据、修复映射表、L1–L3 强度分档、7 条失效条件、8 条反模式、**零依赖扫描脚本**（`--gate` 可接 CI） |
| [github-skill-teardown](github-skill-teardown/) | 拆解 GitHub 上的热门 Agent Skill 生态 | 候选池建立 → 结构清单 → 正文抓取 → 中文覆盖扫描 → 统计分档，附 5 个可复用脚本与「可直接抄 / 必须换 / 不能抄」三档改造意见 |
| [clawhub-publish](clawhub-publish/) | 把本地 skill 发布到 ClawHub 并托管到 GitHub | 发布前 5 步检查（含分发面竞争格局检索）、沙箱内 device flow 自助登录、内容审查 pattern、4 个实测陷阱、git refs 静默失败修复脚本 |
| [codex-archive-to-obsidian](codex-archive-to-obsidian/) | 把 Codex 会话记录归档进 Obsidian 知识库 | rollout jsonl 结构解析、双源扫描去重、注入噪声剥离（7 类）、自动生成索引 |
| [openclaw-codex-reinstall](openclaw-codex-reinstall/) | Windows 下干净卸载重装 OpenClaw / Codex，并接入第三方模型 | 只读扫描清单、隔离备份替代回收站、三个 npm 安装坑、WSL 网关、桌面版模型名报错的三个独立根因、中文界面 |

## 安装

**方式一：ClawHub**

```bash
npm i -g clawhub
clawhub install sunzi-perspective
clawhub install zh-humanizer
clawhub install ui-humanizer
```

**方式二：手动**

```bash
git clone https://github.com/junci003/perspectives.git
cp -r perspectives/*-perspective ~/.workbuddy/skills/
cp -r perspectives/zh-humanizer perspectives/ui-humanizer ~/.workbuddy/skills/
```

## 怎么用

不需要记命令，说到点子上就会自动挂载。

**sunzi-perspective：**
- 「用兵法看看这件事」「这仗怎么打」「要不要正面硬刚」
- 「切换到孙子视角」

**zh-humanizer：**
- 「帮我去一下 AI 味」「这段是不是太像 AI 写的」
- 「改成像人话」「发之前帮我过一遍」

**ui-humanizer：**
- 「这个页面一看就是 AI 做的」「紫色渐变太 AI 了」
- 「emoji 当图标很廉价」「报错直接把英文甩给用户」
- 也可以直接跑：`python scripts/scan_ui_ai_tells.py <项目目录>`

想退出视角时说「切回正常」即可。

## 设计原则

1. **每个心智模型都写失效条件**，不能只写应用。只写应用的视角会让你到处用它，然后翻车。
2. **三重验证**：跨域复现 / 有生成力 / 有排他性。三条全过才算心智模型，只过一条降级为决策启发式。
3. **保留矛盾，不修复**。矛盾是人格特征，不是 Bug。
4. **诚实边界**。明确写出它答不了什么。一个不告诉你局限在哪的视角，不值得信任。
5. **不美化、不洗白**。如实呈现批评者视角与争议，不替原作者做价值观背书。
6. **每个 skill 都要有反模式表和验证判据**。只写「怎么做」而不写「怎么算做错了」和「怎么算做完了」，是半成品。
7. **有脚本的，用脚本；需要判断的，交给人。** 确定性部分不该由模型每次重新推理，判断性部分不该被硬编码规则替代。
8. **不做检测规避**。`zh-humanizer` / `ui-humanizer` 是改善内容与设计，不是把作品伪装成「人类产出」以骗过某个检测器。

## 关于证据层级

以 `sunzi-perspective` 为例。材料分四层，**越往上越要打折扣**：

| 层 | 内容 | 可信度 |
|---|---|---|
| 文本层 | 十三篇原文 | 最高，可直接引用 |
| 训诂层 | 注释、异文、版本差异 | 需标注版本 |
| 验证层 | 战例 | **只可当提问，不可当证明**——全部是事后归因 |
| 转译层 | 现代案例 | 仅作素材；实测附会率极高 |

这个分层不是学术洁癖。它决定了一件实际的事：**当你用这个视角给自己的决策找依据时，哪一层的话可以信。**

同样的诚实标准适用于工具：`zh-humanizer` 的清单是经验归纳，英文对应物 `humanizer` 背后有 Wikipedia「Signs of AI writing」这样的社区共识语料，中文这边没有——**证据层级低于英文版本，这一点写在它的 SKILL.md 里。**

## 同步

本机新增视角或工具后，跑一次：

```powershell
.\sync.ps1
```

它会把 `~/.workbuddy/skills/` 下所有 `*-perspective` 目录，加上 `sync.ps1` 里 `$ExtraSkills` 列出的工具类 skill，同步到本仓库。

> 若提示「在此系统上禁止运行脚本」，用：
> `powershell -ExecutionPolicy Bypass -File .\sync.ps1`

## 致谢

视角蒸馏方法论来自 **女娲 · Skill 造人术**（[花叔 Huashu](https://github.com/alchaincyf/nuwa-skill)，MIT 许可）。

`ui-humanizer` 的问题域由 ClawHub `@moan19921019-code/remove-ai-sence` 最先公开界定（AI 常用色 / emoji 图标 / 英文报错暴露）。

## 版权说明

本仓库收录的是**框架性与方法性内容**（认知结构、判断规则、文本特征的提炼），可依 MIT 许可使用。

其中引用的第三方在版书籍内容（如清华大学出版社《孙子兵法（珍藏版）》的注释与解读）版权归原出版方所有，本仓库仅作学术性引用与评论，不构成对其内容的再授权。引用时请自行标注来源。
