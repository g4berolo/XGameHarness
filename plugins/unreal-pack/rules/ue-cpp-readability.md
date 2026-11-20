---
managed-by: XGameHarness/unreal-pack
paths:
  - "**/Source/**/*.h"
  - "**/Source/**/*.cpp"
  - "**/Source/**/*.hpp"
  - "**/Source/**/*.inl"
---

# UE C++ 可读性

适用于项目和自有插件中手写的 C++，包括测试。修改时只整理本次新增或改动的代码，跳过生成文件和第三方源码。项目有明确的格式约定或 `.clang-format` 时，按该文件所在目录实际生效的配置排版。其余按以下约定。

- **一行一个独立操作。** 取值、修改状态和调用下一步各写一行。函数、条件分支和循环的大括号独占一行。单句的 `return`、`break`、`continue` 也放在所属分支的大括号内。常规 `for` 头和简短的初始化列表可以保持一行。
- **按算法步骤分段。** 用空行分开输入检查、计算和写回。中间量写明含义，例如 `NearestPlateIndex` 和 `NearestDistanceSquared`。抽取函数时，以能描述这一步职责的名字为依据。
- **让声明和表达式能从上到下读。** `UPROPERTY`、`UFUNCTION` 等反射标记独占声明上方一行。过长的参数列表在参数之间换行，复合条件按含义换行或用具名布尔量。缩进遵循项目约定，缺省按 Epic 风格使用 Tab，显示宽度为 4。

例如，更新最近和次近板块时，先保留旧结果，再写入新结果。顺序和数据含义都能从代码里看出来。

```cpp
if (CandidateDistanceSquared < NearestDistanceSquared)
{
	SecondNearestPlateIndex = NearestPlateIndex;
	SecondNearestDistanceSquared = NearestDistanceSquared;

	NearestPlateIndex = CandidatePlateIndex;
	NearestDistanceSquared = CandidateDistanceSquared;
}
```

交付前查看本次差异，重点检查分支内的多条操作、跨阶段的长表达式和紧贴在一起的声明。项目已配置 clang-format 时，可用 `git clang-format --diff` 检查变更行；新文件也应逐段检查。参考 [Epic C++ 编码规范](https://dev.epicgames.com/documentation/en-us/unreal-engine/epic-cplusplus-coding-standard-for-unreal-engine)。
