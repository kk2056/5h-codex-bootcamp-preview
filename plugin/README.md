# 5H Codex Bootcamp 插件预览包

这个目录可以作为 Codex 的本地插件市场。里面的 Plugin 包含 Coach Skill、五关课程、计时页和本地脚本。学员的进度写在**自己的训练项目**里，不写进插件安装缓存。

## 在 Mac 或 Windows 安装

先在终端进入解压后的仓库根目录，再执行：

```text
codex plugin marketplace add ./plugin
codex plugin add 5h-codex-bootcamp@5h-bootcamp-local
```

安装后，在 Codex 中新建一个对话。请在下载仓库**外面**创建一个空的训练项目，并在 Codex 中打开它；下载仓库里的项目级 Skill 与已安装 Plugin 同名，直接在源码目录开课会出现两个候选。

在新的训练项目对话中输入：

```text
$codex-coach 先介绍课程路线
```

看完路线后再说“开始训练”，这时才启动五小时计时。Mac 的计时脚本使用 Python 3.9+；Windows 原生 PowerShell 使用 `py -3`，没有 Python Launcher 时使用 `python`。这些准备放在正式计时之前。

如果本地计时服务启动失败，不要关闭 Codex 沙箱。Windows 可以在单独的 PowerShell 窗口、以训练项目为当前目录运行插件自带的 `start_timer.ps1`，并让那个窗口保持打开。若端口 4173 已被另一份课程占用，先关闭旧计时器，再继续。

## 包内文件

```text
plugin/
├── .agents/plugins/marketplace.json
└── 5h-codex-bootcamp/
    ├── plugin.json
    ├── .codex-plugin/plugin.json
    └── skills/codex-coach/
        ├── SKILL.md
        ├── references/levels.md
        ├── scripts/course_timer.py
        ├── scripts/ensure_timer.py
        ├── scripts/state.py
        ├── scripts/start_timer.sh
        ├── scripts/start_timer.ps1
        └── assets/timer/
            ├── index.html
            └── server.py
```

这是可安装预览包。逐关自动验收尚未做完，Windows Codex Plugin 安装流程仍需要在 Windows 实机复核。

更细的 Mac/Windows 步骤见 [插件安装说明](../docs/plugin-install.md)。
