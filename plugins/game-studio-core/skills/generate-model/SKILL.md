---
name: generate-model
description: "AI 3D建模工作流 — 使用 Tripo3D API 从立绘生成3D模型。引导完成配置检查、立绘选择、参数配置、模型生成、质量审核的完整流程。"
argument-hint: "[角色名] (例: warrior, mage, npc_merchant)"
user-invocable: true
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, mcp__tripo-ai__tripo_validate_config, mcp__tripo-ai__tripo_img2model, mcp__tripo-ai__tripo_text2model, mcp__tripo-ai__tripo_multiview2model, mcp__tripo-ai__tripo_check_status, mcp__tripo-ai__tripo_list_outputs, mcp__tripo-ai__tripo_approve_model, mcp__tripo-ai__tripo_archive_failed, mcp__tripo-ai__tripo_clean_outputs, mcp__tripo-ai__tripo_list_approved_illustrations
---

# /generate-model — AI 3D 建模工作流

## 概述

引导式图生3D流程，覆盖从立绘选择到模型入库的完整链路。
对应 `art/` 管线的 **阶段 2: 3D建模 (02_Modeling)**。

**核心工具**: Tripo3D API — 图片/文字 → 3D 模型 (GLB/FBX)

## 工作流

### 阶段 1: 配置验证

1. 调用 `tripo_validate_config` 检查 API Key 是否可用
2. 如果失败：
   - 提示用户将 `tools/tripo/config.example.json` 复制为 `tools/tripo/config.json`
   - 引导填入 API Key（从 https://platform.tripo3d.ai 获取，以 `tsk_` 开头）
   - 重新验证
3. 如果成功：显示"API 连接正常"和余额信息，继续下一步

### 阶段 2: 角色上下文

1. 解析参数中的角色名（如 `warrior`）
2. 读取 `art/asset-registry.md` 检查该角色当前进度。**该文件不存在时不报错**：
   `art/` 整棵目录不在 harness 项目契约里（project-template 不建、project-init 不建），
   属项目自定美术管线。跳过进度检查，在阶段 7 再问用户是否新建。
3. 读取 `art/style-guide/` 下的风格规范（如有）
4. 调用 `tripo_list_approved_illustrations` 列出上游已审核立绘
5. 检查该角色是否有多个角度的立绘（front/side/back）
6. 调用 `tripo_clean_outputs` (action=list) 检查是否有待处理的模型
7. **如果有未审核模型，必须先处理** —— 未审核产物堆积会让后续批次无法判断哪个是最新
   有效版本，所以先走完审核/归档再生成新模型
8. 向用户展示收集到的上下文信息

### 阶段 3: 生成方式选择

使用 AskUserQuestion 询问用户：

**选择输入方式：**
- 单图生3D (img2model) — 从单张立绘生成（最常用）
- 多视角生3D (multiview2model) — 从 2~4 张不同角度立绘生成（质量最高）
- 文生3D (text2model) — 从文字描述直接生成（无需立绘）

如果选择 img2model 或 multiview2model：
- 列出 `art/01_Illustration/approved/` 中与该角色相关的立绘文件（目录不存在则说明
  项目尚未建立美术管线，请用户直接给出立绘路径）
- 让用户选择要使用的图片

如果选择 text2model：
- 引导用户编写英文3D描述

### 阶段 4: 参数配置

使用 AskUserQuestion 确认参数：

**模型版本选择：**
- default — 自动最新稳定版（推荐新手）
- smart_mesh — Smart Mesh P1.0（推荐游戏资产，干净拓扑）
- v2.5 — Tripo v2.5（经典版本）

**核心参数**（提供推荐默认值，用户可调）：

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| face_limit | 50000 | 游戏角色推荐 10K~100K |
| texture | true | 生成纹理 |
| pbr | true | PBR 材质 (Albedo + Normal + Roughness) |
| texture_quality | standard | standard / detailed |
| geometry_quality | standard | standard / detailed |
| quad | true | 四边面（推荐，利于后续绑骨） |
| smart_low_poly | false | 智能低模优化 |

**快捷预设**:
- 🎮 游戏角色: face_limit=50000, quad=true, geometry_quality=detailed
- ⚡ 快速原型: face_limit=10000, texture_quality=standard
- 🎨 高质量展示: face_limit=200000, geometry_quality=detailed, texture_quality=detailed

展示完整参数摘要，请求用户确认。

### 阶段 5: 模型生成

1. 根据选择调用对应 MCP 工具：
   - 单图 → `tripo_img2model`（自动上传图片 + 生成 + 轮询 + 下载）
   - 多视角 → `tripo_multiview2model`（自动上传多张图片）
   - 文生3D → `tripo_text2model`
2. 告知用户"正在生成3D模型，通常需要 1-5 分钟..."
3. 工具内部自动轮询直到完成，返回下载的文件列表
4. 告知用户结果：
   - 模型文件路径 (`.glb`)
   - PBR 模型路径 (`.glb`)
   - 预览渲染图路径 (`.webp`)

### 阶段 6: 结果审核

1. 调用 `tripo_list_outputs` 展示生成的模型文件
2. 如果有预览图 (`.webp`)，用 Read 工具展示给用户
3. 提示用户可在 3D 查看器中打开 `.glb` 文件检查质量
4. 使用 AskUserQuestion 让用户选择：
   - **通过** — 对所有关联文件调用 `tripo_approve_model` 移入 `approved/`
   - **归档失败** — `tripo_archive_failed`，记录原因（如拓扑差、纹理错误等）
   - **调整参数重试** — 返回阶段 4 修改参数（如增加面数、换版本等）
   - **换立绘重试** — 返回阶段 3 选择其他输入
5. 批量处理同一次生成的所有文件（model + pbr_model + preview 一起通过或拒绝）

### 阶段 7: 资源注册

1. 读取 `art/asset-registry.md`。不存在就问用户「是否新建 `art/asset-registry.md`？」，
   同意则先写表头：`| 角色 | Illustration | Model | Rigging | Animation | 备注 |`。
2. 询问用户是否更新资源注册表
3. 如同意，更新该角色的 Model 列：
   - 状态: `OK` / `WIP`
   - 工具: `Tripo3D`
   - 详细记录: 模型版本、面数、参数、输入/输出文件名、日期
4. 写入文件

### 阶段 8: 下一步建议

根据完成情况提供建议：
- "3D 模型已通过审核。下一步可以进行 **骨骼绑定** (03_Rigging 阶段)"
- 如果需要调整："是否需要重新生成一个更高面数/不同版本的模型？"
- 如果需要其他角色："是否为另一个角色生成3D模型？"

## 输出命名规范

使用 `output_prefix` 参数构建完整文件名：
```
model_{角色名}_v{版本号}_base.glb      — 标准模型
model_{角色名}_v{版本号}_pbr.glb       — PBR 材质版本
model_{角色名}_v{版本号}_preview.webp  — 预览渲染图
```

示例: `output_prefix = "model_warrior_v01"` 生成：
- `model_warrior_v01_base.glb`
- `model_warrior_v01_pbr.glb`
- `model_warrior_v01_preview.webp`

## 注意事项

- 模型下载链接有效期 **24 小时**，MCP 工具会自动下载到本地
- 建议使用 **quad=true** 如果模型后续需要绑骨和动画
- 多视角 (multiview) 比单图质量更高，优先推荐
- Smart Mesh P1.0 版本专为游戏资产优化拓扑
- Tripo 免费计划每月 300 积分，image_to_model 约 30-50 积分/次
- 遵循项目协作协议：每一步都征求用户确认后再执行
