# XGameHarness Blender Pack

把本机 Blender 变成 Claude / Codex 可以操作和验收的建模工具。与 unreal-pack 一样从
XGameHarness 市场独立安装，可组合使用，不锁定模型、不带外部生成服务、无遥测。

四项设计：参考图和尺寸先行；建模/独立评审分工；保留可复现过程及人工改动；明确自行建模、
现成素材、图生 3D 三种来源。源码与角色共用，权限仍由各自宿主管。

## 开始

```text
codex plugin add blender-pack@XGameHarness
claude plugin install blender-pack@XGameHarness --scope user
python <installed-pack>/scripts/configure.py --blender <blender-executable>
```

开新任务使用 `$blender-workflow`（Claude：`/blender-pack:blender-workflow`），或直接说
“用 Blender 做一个低多边形补给箱，先给我看多视角，再导出 GLB”。
安装 pack 不等于下载 Blender；先用 doctor 检查实际版本。详细入口见 [连接说明](docs/connection.md)。

| 入口 | 能力 |
|---|---|
| `blender_doctor` | 定位本机程序、报告真实版本 |
| `blender_job` | build / inspect / preview / export，独立版本、日志、脚本快照 |
| `blender_live_start` | 新建专用 Blender 工作窗口，原文件先另存副本 |
| `blender_live_command` | status / exec / save / stop；同一任务独占 |
| `blender_image` | 返回 PNG 供模型实际看图 |

无 MCP 的宿主使用同一个 `scripts/runner.py`，不会退化成只提供建议。
实时 Python 和批量脚本属于本地代码执行，不是受限 DSL 或安全沙箱；保留宿主审批。

## 专家与客户端

Claude 插件自动发现 `agents/`。Codex 项目沿用 core 安装器：
`python <core>/scripts/harness.py sync --project <project> --blender-root <pack>`。
也可显式运行 `scripts/install_agents.py --home <CODEX_HOME>` 安装仅这两个本机专家；保留手改版本。
角色继承当前模型和权限。没有可用子 agent 时流程仍可做，但必须报告“未独立评审”。

XGameHarnessUI 项目需在 `.claude/settings.json` 的 `enabledPlugins` 中启用
`"blender-pack@XGameHarness": true`，并确保客户端读取的市场 clone 已更新；新开对话重扫。
可用 `scripts/configure.py --blender <exe> --project <project>` 做保留其他键的配置合并。
客户端的技能扫描不代表其隔离账号加载了 MCP：Codex extraRoots 路线可用 CLI 完成全部操作。
本次分发不改客户端界面或审批逻辑，不需要 Electron 出包。

## 验证

```text
python -m unittest discover -s tests -v
python scripts/validate.py
```

仓根设置 `BLENDER_BIN` 后测试会真实调用 Blender：建模、输入保留、GLB/FBX 回读、错误/超时、
实时执行和占用互斥；未设置时明确跳过实际 Blender 项。例子在 `examples/crate.py`，
对应 [验收 brief](examples/crate-brief.md)。预览需人工或独立 agent 实际看图。

验收记录见 [首版验证](docs/validation.md)。源码测试、宿主加载、模型看图和 UE 实测分别报告，
不把 Blender 回读说成 UE 兼容通过。Windows 5.2.2 LTS 是本次实测基线，其他平台/版本未实测。
