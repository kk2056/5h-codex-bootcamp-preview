# 目录说明

## 现在这份样机里有什么

| 位置 | 谁会用 | 负责什么 | 当前状态 |
|---|---|---|---|
| `.agents/skills/codex-coach/SKILL.md` | Codex 项目内预览 | 提供教练流程和课程引导；适合直接打开仓库体验。 | 如需独立安装，请使用 plugin/ 内的 Plugin 包。 |
| `curriculum/levels.md` | 学员、教练 | 课程内容的主要说明：五小时安排、每段学习点、动手任务、产物与通过条件。 | 已细化为可审阅课程稿。 |
| `progress/progress.json` | 网页、计时脚本、Skill | 保存课程时间、当前关卡和完成记录。 | 网页与命令行共用；默认数据目前是空白学员记录。 |
| `plugin/5h-codex-bootcamp/` | Codex 桌面版/CLI | 可安装 Plugin 包，含 manifest、Coach Skill、课程、计时脚本和页面资源。 | 已完成本地包装；正式发布流程及 Windows 实机未验证。 |
| `plugin/.agents/plugins/marketplace.json` | Codex Plugin 浏览器/CLI | 让本仓库中的 Plugin 可作为本地市场安装和测试。 | 本地测试用，不是公开 marketplace。 |
| Plugin 运行时的学员工作区 progress/progress.json | 学员、Plugin 内脚本 | 保存学员自己的计时和关卡状态；不写进 Plugin 缓存。 | Plugin 包已按工作区路径设计，需 Windows 实机复核。 |
| `docs/plugin-install.md` | Windows/Mac 试跑者 | 说明如何安装本地 Plugin、建立训练工作区和开课。 | 按本文件步骤操作；Windows 实机仍待确认。 |
| `scripts/course_timer.py` | 学员、Skill | 在命令行开始、暂停、继续、查询或确认重置课程时间。 | 可运行。 |
| `scripts/ensure_timer.py` | Coach Skill | 检查 127.0.0.1:4173；若本地预览未启动，则用当前 Python 在后台启动。 | 跨平台实现已写；需在 Windows PowerShell 环境复核。 |
| `scripts/start_timer.sh` | macOS/Linux 学员 | 从终端手动启动本地计时页。 | 可在当前 macOS 主机使用。 |
| `scripts/start_timer.ps1` | Windows PowerShell 学员 | 从终端手动启动本地计时页。 | 已编写；当前测试主机没有 PowerShell。 |
| `timer/state.py` | 计时网页和命令行脚本 | 读取和更新唯一进度文件，计算已经用掉和剩下的秒数。 | 可运行。 |
| `timer/server.py` | 本地预览 | 只在 `127.0.0.1:4173` 提供页面和同源计时接口。 | 可运行；不接受任意文件路径或外部网络连接。 |
| `timer/index.html` | 学员 | 显示倒计时、开始/暂停/继续、课程路线和每关详细说明。 | 交互样机；页面课程细节与课程稿是人工同步的。 |
| `docs/directory-map.md` | 产品制作人和接手开发的人 | 解释每个目录职责、真源和未做的模块。 | 本文件。 |
| `README.md` | 学员和安装者 | 告诉用户如何启动、五小时怎么算、当前版本做到哪。 | 已更新。 |

## 几条重要关系

1. **课程内容以 `curriculum/levels.md` 为主。**它解释用户要学什么和如何过关。
2. **个人状态只保存在 `progress/progress.json`。**网页和命令行都操作同一份计时，不各存一份。
3. **Skill 负责带教，脚本负责确定动作。**Skill 不应口头猜测时间，也不能把“学员说做完”当作通过。
4. **网页只做可见的计时和课程导航。**它不读取学员其他项目，不把代码或聊天发到外部服务。
5. **系统差异留在启动层。**课程 Skill 用 macOS/Linux 的 `python3`，或 Windows PowerShell 的 `py -3` / `python` 启动同一 Python 脚本；产品路径由 pathlib 解析。

## 正式版再增加的目录

下列内容目前没有实现，等课程稿和体验验证后再添加：

```text
validators/                   # 每关检查文件、运行结果的脚本
tests/                         # 对计时、关卡验收和 Skill 行为的自动检查
```

先逐关确认哪些能力真的需要自动检查，再新增对应脚本。不要先建空目录来暗示功能已经存在。
