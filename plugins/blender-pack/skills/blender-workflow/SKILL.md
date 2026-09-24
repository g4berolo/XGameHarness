---
name: blender-workflow
description: "用本机 Blender 创建和修改游戏模型、参考图重建、材质与多视角预览、GLB/FBX 导出验收；支持实时场景和后台脚本，保留已有模型的人工修改。"
---

# Blender 建模工作流

插件根目录为本 SKILL.md 的上两级，不依赖宿主展开 `${CLAUDE_PLUGIN_ROOT}`。
Claude 与 Codex 使用同一工具和流程；模型随当前宿主，不固定 GPT 版本。
本 pack 的 Python 3.11+ 执行器在 `scripts/runner.py`；Blender 内部使用它自己的 Python。

## 先定位真实环境与任务

调用 `blender_doctor`；没有该 MCP 工具时用 shell：
`python <pack>/scripts/runner.py doctor`。没有 Blender 就报告缺失，不把安装 pack 当作已能建模。
路径优先级：`--blender`、`BLENDER_BIN`、`~/.xgh/blender.json` 的 `executable`、PATH / 常规安装位置。
本地配置方法和实时操作看 [连接说明](../../docs/connection.md)。不改用户个人模型或权限设置。

每个资产使用独立目录，如 `art/blender/<asset>/`。先按 [资产 brief](../../templates/brief.md)
记录用途、单位和已知尺寸、面数预算（未知留空）、目标引擎、参考图路径、来源模式与验收视角。
已有 `.blend` 是有效输入，先检查再局部改；不得以“可复现”为由重建并抹掉人工修改。
参考图片要实际打开观察；区分看得见的结构、推测的背面、用户确认的尺寸。
缺少关键信息才问；不影响进行的选择写明假设继续。

## 三种来源必须分清

- 自行建模：Python / 修改器 / Geometry Nodes 等。保留脚本和参数。
- 现有素材：用户已有文件或获准使用的素材库；记录来源和许可证，不能冒充自行建模。
- 图生 3D：只有当前任务授权使用对应服务且工具可用才调用。没有服务就用前两种；
  不能把概念图当成实际网格、不能擅自上传项目资产。pack 本身不绑定收费服务。

导入/生成后在网格对象上设 `xgh_source_kind`（`modeled` / `imported` / `generated`），
`xgh_source_uri`、`xgh_source_license`。逐资产维护 `sources.json`；未知许可明确记为 unknown。
参考流程、UV、建模和引擎注意事项按需看 [建模参考](../../docs/modeling.md)。

## 制作 → 看图 → 改

1. 先粗模验证轮廓、比例和空间；再细化、UV 与材质。先用参考图固定视觉目标，
   无参考时可以用当前可用的图像技能生成概念图，但不是必需依赖。
2. 脚本写入资产目录。后台调用 `blender_job`（action=build），或
   `python <pack>/scripts/runner.py build --workspace <asset-dir> --script <script.py>`。
   修改现有模型加 `--blend <input.blend>`。脚本可用 `XGH_OUTPUT`、`XGH_WORKSPACE`；
   输出自动保存到全新的 `runs/<revision>/scene.blend`，执行日志和源码快照同目录。
   脚本是本地代码执行，不是沙箱；遵守宿主原有审批，不替用户永久放行。
3. 对本轮准确的 `.blend` 运行 inspect 和 preview（同上 CLI / MCP action）。预览输出
   front/side/back/top/hero 五个必查视角及 hero-left 补充图。必须实际看图：MCP `blender_image` 或宿主图片工具。
   预览灯光是评审灯光，不改源文件；成品灯光另按任务制作。
4. 当前任务允许委派、且宿主有可用子 agent 时，交给独立 `asset-reviewer`：
   brief、参考图、五视图、检查报告、导出回读证据；不交作者自评结论。
   Claude：`blender-pack:asset-reviewer`；Codex：已安装的 `blender-pack--asset-reviewer`，
   或将 `agents/asset-reviewer.md` 正文传给可用通用子 agent。主执行角色是 `blender-artist`。
   不存在的角色不能直接调用。需要项目 Codex 角色时定位已启用的 core，运行：
   `python <core>/scripts/harness.py sync --project <project> --blender-root <pack>`。
5. 评审按 [评审模板](../../templates/review.md) 给有证据的优先级问题。默认最多三轮修正；
   用户可更改预算。不要降低面数预算/删除必查视角来使结果通过；预算不足或仍不达标时
   交付当前版本并列出问题。无子 agent 时做同样检查，但报告“未独立评审”，不冒充独立验收。

## 实时修改

用户需要边看边改时用 `blender_live_start` 打开独立工作副本，之后 `blender_live_command`
进行 status/exec/save/stop。exec 的 script 是 Python 源码；batch 的 script 是磁盘路径。
同一资产目录在 live 存活期间由一个任务独占；不要偷用别人的 owner ID 或删锁。
这是新工作窗口，不接管用户已经打开且尚未保存的场景。
实时每次脚本也留快照；对可复现资产将确认的修改整理回构建脚本，对于人工资产保留输入
版本与补丁脚本，不强制从空场景重建。结束时 stop 会先另存一个版本再关闭；超时后先检查，
不自动重试。批量预览/导出前先 stop 释放占用，或在另一个评审目录读取已保存副本。

## 交付与引擎边界

用 export action 生成 GLB 或 FBX 并实际重新导入 Blender；比较尺寸、网格、材质与贴图，
运行成功只表示回读成功，不保证所有材质/动画语义保持。源文件、导出文件和预览都要交付。
UE 项目再用已启用的 unreal-pack 做真正引擎导入、材质、碰撞、单位和运行检查；无 UE 环境
标明“UE 未验证”。`.blend`/GLB/FBX 属于游戏资产，不进 plan/design/team 文档分发通道。
记录实际版本、输入、来源、检查和未验证项。没有分母不填 0，没有看到图片不说视觉通过。
