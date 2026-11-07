# Coach Skill 插件安装与首次开课

这份说明给 Windows 和 Mac 的本地试跑使用。Plugin 文件装进 Codex；学员的计时和作品放在另建的训练项目中。

## 第一步：课前检查

学员自己安装 Codex。打开解压后的产品仓库目录，确认能运行 Python 3.9 或更新版本。

Windows PowerShell：

```powershell
py -3 --version
```

Mac 终端：

```sh
python3 --version
```

如果 Windows 没有 `py`，改用下面命令检查：

```powershell
python --version
```

课前检查不消耗五小时。

## 第二步：安装 Coach Plugin

在终端中切换到解压后的产品仓库根目录，从那里运行：

```text
codex plugin marketplace add ./plugin
codex plugin add 5h-codex-bootcamp@5h-bootcamp-local
```

安装完成后，重新打开 Codex 或新建 Codex 对话，让新 Skill 进入可用列表。这个本地市场只用于测试，不需要发布到公共插件目录。

若当前电脑没有 `codex` 命令，可以在 Codex 桌面版的插件界面添加本地市场目录 `plugin/` 并安装同名插件；该图形界面步骤尚需在 Windows 实机确认。

## 第三步：在单独目录开课

在下载的产品仓库**外面**建一个空文件夹，例如“5h-codex-training”，然后在 Codex 中把它作为项目打开。不要直接在产品源码目录开课；源码目录原本已有一个同名项目级 Skill，会和插件 Skill 一起出现。

在这个新项目的 Codex 对话里输入：

```text
$codex-coach 先介绍课程路线
```

教练会介绍五关，学员说“开始训练”后才启动计时。学员的状态存到这个训练项目的 `progress/progress.json`；插件目录只存程序和课程资料。

## 计时页打不开时

先让教练查看错误。端口 4173 如果已经运行另一份课程，先关闭旧计时器，不要复用旧进度。Windows 原生 Codex 沙箱可能在后台命令退出时停止计时服务；这时让教练提供插件中 `start_timer.ps1` 的实际路径，并在普通 PowerShell 窗口以训练项目为当前目录运行，保持窗口打开。无需关闭沙箱。

## 这版的范围

这次交付可用来检查安装、课程引导和本地计时；逐关自动文件验收还没做完。Windows 原生 Codex 安装仍需在用户的 Windows 电脑确认。
