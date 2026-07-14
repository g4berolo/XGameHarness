---
managed-by: XGameHarness/unreal-pack
paths:
  - "client/Source/clientTests/**"
  - "tests/**"
---

# Test Standards

适用于 RichLethe `client/Source/clientTests/**` 自动化测试代码（`UAutomationTest` 模块，UBT 只扫 `<项目>/Source` — 见 directory-structure.md）。

> **2026-06-11 path 激活** — 原 `tests/**` 占位指向仓库根 legacy 目录，真实测试模块自 S3-T5 起落在 `client/Source/clientTests/`（`BattleSimulatorTest.cpp` / `EnemyRegistryTest.cpp` 等），规则从未触发过。现以 `clientTests` 为主 path；`tests/**` 保留兜底。

- 测试命名: `Test_[System]_[Scenario]_[ExpectedResult]` 模式
- 每个测试明确 **Arrange / Act / Assert** 三段
- Unit test 不依赖外部状态（文件系统 / 网络 / DB / Editor）
- Integration test 自清理（teardown 还原所有副作用）
- Performance test 指定可接受阈值 + 超阈 fail
- 测试数据写在测试内或专门 fixture，**不共享 mutable state**
- Mock 外部依赖 — 测试必须快 + 确定性
- 每个 bug fix 必有 regression test（能在 fix 前 catch 该 bug）

## Examples

**Correct** (UE5 `UAutomationTest` with Arrange/Act/Assert):

```cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTest_HealthSystem_TakeDamage_ReducesHealth,
    "RichLethe.Combat.Health.TakeDamage_ReducesHealth",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::SmokeFilter)

bool FTest_HealthSystem_TakeDamage_ReducesHealth::RunTest(const FString& Parameters)
{
    // Arrange
    UHealthComponent* Health = NewObject<UHealthComponent>();
    Health->SetMaxHealth(100.f);
    Health->SetCurrentHealth(100.f);

    // Act
    Health->TakeDamage(25.f);

    // Assert
    TestEqual(TEXT("Health reduced by 25"), Health->GetCurrentHealth(), 75.f);
    return true;
}
```

**Incorrect** (no descriptive name / no AAA / imprecise assertion):

```cpp
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTest1, "Test1", EAutomationTestFlags::SmokeFilter)
bool FTest1::RunTest(const FString&)
{
    UHealthComponent* H = NewObject<UHealthComponent>();
    H->TakeDamage(25.f);                                       // VIOLATION: 无 Arrange
    TestTrue(TEXT("less than 100"), H->GetCurrentHealth() < 100.f);  // VIOLATION: 命名 + 不精确断言
    return true;
}
```
