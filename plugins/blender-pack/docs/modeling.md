# 按需建模参考

## 参考图到模型

先看正侧背视图的轮廓、部件数量、尺度锚点和连接关系。单张透视图无法确定背面和深度，
用用户要求与对称/结构常识提出假设；不承诺一比一还原看不见的部分。优先完成主轮廓，
用简单材质渲染确认比例，再处理小倒角、螺丝等细节。参考图本身不等于获得素材分发许可。

## Blender Python 的实际坑

- 先读 `bpy.app.version_string`，通过 `hasattr`/RNA 枚举查真实 API；参考文档必须匹配版本。
- `bpy.ops` 依赖 mode、active object、selection 和上下文。后台模式没有 UI area，优先
  `bpy.data` 和 `bmesh`；确需 operator 时先明确 OBJECT/EDIT 模式和选中对象。
- 非均匀缩放会改变倒角等修改器结果；在合理的阶段应用缩放，负缩放检查面朝向。
- 统计 evaluated mesh 而非只数基网格。实例化、几何节点和动画需针对导出另测，不从单帧
  网格报告推断完整运动行为。布料/流体等模拟需要明确缓存与帧区间。
- Principled BSDF 输入名称、Geometry Nodes socket 接口会随版本变化，先枚举再写。
- `bpy` 只在 Blender 内导入；宿主 Python 负责启动进程，不要求在宿主 pip 安装 bpy。

## 游戏资产

先确定用途、观察距离和预算。低模用轮廓表达大形，法线/贴图表达小尺度细节。硬表面道具
优先可控的镜像、阵列、倒角；角色关节拓扑、权重与变形需专门测试，不靠静态好看过关。
开放面不是自动错误；封闭实体才检查意外破洞。UV 需要按任务区分：平铺材质、独立烘焙、
图集和光照 UV 约束不同；不要把“存在一个 UV 层”写成“UV 合格”。
纹理生成只产生颜色图时不要冒充完整 PBR。检查背面、侧壁、封口的贴图覆盖，防止只贴正面。
保留素材来源、作者、许可和服务输出条件；本 pack 不自动下载付费/外部模型。

## 导出和 UE

Blender 工作单位、对象变换与导出设置一起决定实际尺寸。选一个已知尺寸物体在引擎里量，
不要仅靠写“米转厘米”。GLB 支持的材质与 Blender 节点并不等价；FBX 的材质也需引擎重建。
检查坐标轴、原点、贴图、骨架、碰撞命名、LOD、动画帧率。导出后的 Blender 回读是中间检查，
真正交给 UE 使用时调用 unreal-pack 或实际编辑器工具完成导入与运行验证。

## 参考来源（研究日期 2026-09-24）

- Blender 官方 [Python API](https://docs.blender.org/api/current/) 与
  [命令行](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)：按本机版本选择。
- [Simon Willison 实践](https://github.com/simonw/til/blob/main/llms/blender-coding-agents-macos.md)：保留脚本和可编辑产物。
- [Codex-and-Blender](https://github.com/danielsobrado/Codex-and-Blender)：配置、重建、多视图和有界修正。
- [独立 critic 流程分享](https://www.reddit.com/r/aigamedev/comments/1wbzneq/gpt6_astra_blenderhoudini_a_3d_workflow_with_a/)：作者报告，未在本 pack 重现其作品。
- [GPTblender 平面图实验](https://gptblender.com/turn-floor-plan-into-3d-model-gpt6-astra/)：粗模先行，区分自行建模与素材组装。

本 pack 的代码为本仓新实现；上述项目仅为流程参考，不包含拷贝的第三方实现或资产。
