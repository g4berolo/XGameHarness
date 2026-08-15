---
managed-by: XGameHarness/unreal-pack
paths:
  - "client/Source/**"
---

# Gameplay Code Rules

适用于本项目所有 C++ 游戏代码（默认 `client/Source/**`，按项目结构调整
frontmatter 的 `paths:`）— UE5 + Blueprint 项目。

- 所有 gameplay 数值必须来自外部 config / data asset（DataTable / `UPrimaryDataAsset`，或项目 ADR 约定的等价方案），**禁止硬编码**
- 所有 time-dependent 计算使用 `DeltaSeconds`（`Tick(float DeltaSeconds)`）— frame-rate independent
- C++ 代码 **不得直接引用 UMG / Widget** — 通过 Delegate / Multicast / GameplayMessage Subsystem 等事件机制做跨系统通信
- 每个 gameplay 系统必须有清晰 Interface（`UInterface` 或 abstract base）— 便于测试与依赖反转
- 状态机使用 `UStateTreeComponent` 或显式 transition table 文档化 states + transitions
- 所有 gameplay 逻辑必须可单元测试 — 用 `UAutomationTest` 把逻辑与表现分离（见 `tests/` 规则）
- 代码注释标注本特性实现的 design doc（如 `// Implements: design/gdd/permadeath.md §3.2`）
- **禁止 static singleton 持有游戏状态** — 用 `UGameInstanceSubsystem` / `UWorldSubsystem` + 构造时注入

## Examples

**Correct** (data-driven + DeltaSeconds + Subsystem):

```cpp
void APlayerCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    const FStatsRow* Stats = StatsTable->FindRow<FStatsRow>(StatRowName, TEXT("Tick"));
    if (!Stats) return;
    const float Speed = Stats->MovementSpeed * DeltaSeconds;
    AddMovementInput(GetActorForwardVector(), Speed);
}
```

**Incorrect** (hardcoded + no delta + direct UI ref):

```cpp
void APlayerCharacter::Tick(float DeltaSeconds)
{
    const float Speed = 5.0f;  // VIOLATION: 硬编码 gameplay 数值
    AddMovementInput(GetActorForwardVector(), Speed);  // VIOLATION: 未使用 DeltaSeconds
    HUD_Widget->UpdateHealth(Health);  // VIOLATION: 直接引用 UI
}
```
