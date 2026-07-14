---
paths:
  - "client/Source/**/UI/**"
---

# UI Code Rules

适用于 RichLethe UMG / Common UI C++ 代码（`client/Source/**/UI/**`）。

> **当前 path 占位** — UI 主要在 BP（`W_*.uasset`），C++ 子目录尚未建立。当 UI C++ 代码 land 时本规则自动激活。

- UI **从不持有或直接修改游戏状态** — display only；通过 GameplayMessage / Delegate / `UGameStateSubsystem` 请求变更
- 所有 user-facing 文本通过 `FText::FromStringTable()` / 本地化系统 — 禁止硬编码 `FString` 给玩家看
- 所有交互元素同时支持键鼠 + 手柄（`Common UI` input routing；`UCommonUserWidget` 优先）
- 所有动画 / VFX 可 skip + 尊重 motion / accessibility 偏好
- UI 音效通过 audio event 系统触发，不直接 `UGameplayStatics::PlaySound2D`
- UI 不得 block game thread — 复杂逻辑用 `AsyncTask` / `FAsyncWorker`
- 可缩放字体 + 色盲模式必须实现 — 不是 optional
- 所有 screen 在最小 + 最大支持分辨率下截图测试
