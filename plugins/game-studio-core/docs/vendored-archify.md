# vendored: archify

`plugins/game-studio-core/skills/archify/` 是**第三方技能包**，不是本 harness 写的。
本文件是它的收录记录：来源、边界、校验方法、升级步骤、以及两条要知道的注意事项。

harness 自研的 25 个 skill 归我们维护；这一个不改，只整包换版本。

---

## 1. 它做什么

把系统描述或仓库代码变成**可交互的单文件 HTML 架构图**。五种图：

| 类型 | 用于 |
|---|---|
| `architecture` | 组件、服务、云/安全边界、基础设施 |
| `workflow` | 流程、审批关卡、工具调用、CI/CD、runbook |
| `sequence` | API 调用链、请求生命周期、异步链路 |
| `dataflow` | 数据管线、ETL、血缘、下游消费者 |
| `lifecycle` | 状态机、重试、等待态、终态 |

核心设计是**不让模型画图**：模型只产出一份带 schema 的 JSON 中间表示(IR)，
坐标、路由、配色由确定性渲染器算，交付前必须过校验闸门。校验失败返回的是
带 `subject` / `evidence` / `supportedFixes` 的结构化诊断，不是堆栈。

对本 harness 的直接用处：`/reverse-document` 反推架构、ADR 配图、GDD 里的状态机和
流程图、读本(digest)里那张「读者真的看得见」的图。

## 2. 来源与版本

| 项 | 值 |
|---|---|
| 上游 | https://github.com/tt-a1i/archify |
| 许可证 | MIT |
| 收录版本 | **v2.16.0**（上游 2026-08-30 发布） |
| 收录来源 | 该 release 的官方资产 `archify.zip`，**不是** clone 主线 |
| 包 SHA-256 | `4c59fa6557a2385beaaef8c7219cc414573acc9f0c30a932d5053b0b20689a46` |
| 包大小 | 1,318,273 bytes（解压 76 个文件 / 5.62 MB） |
| 收录日期 | 2026-09-17 |

收录当天上游主线已经是 `2.17.0-dev.1`。**故意收 stable 而不是主线** —— 主线每天都在
合 PR，没有可对账的版本号。

## 3. 收录边界

`skills/archify/` 里的 76 个文件**与官方 release 逐字节一致，一个文件都没加**。

所以：
- 收录记录（本文件）放在 `docs/`，不放进那个目录
- `.gitattributes` 里给该路径设了 `-text`，关掉行尾转换 —— 否则仓库的
  `*.json text eol=lf` / `*.md text eol=lf` 会在检出时改写它的字节，校验就永远对不上
- 想改行为**不要直接改包里的文件**。真有需求就在外面包一层，或者把改动提给上游

### 校验它没被动过

```powershell
# 1) 重新下载官方包并核对哈希
$zip = "$env:TEMP\archify-2160.zip"
Invoke-WebRequest "https://github.com/tt-a1i/archify/releases/download/v2.16.0/archify.zip" -OutFile $zip
(Get-FileHash $zip -Algorithm SHA256).Hash   # 应等于上表的 SHA-256

# 2) 解压后逐文件对比
Expand-Archive $zip -DestinationPath "$env:TEMP\archify-check" -Force
$src = "$env:TEMP\archify-check\archify"
$dst = "plugins\game-studio-core\skills\archify"
Get-ChildItem -Recurse -File $src | ForEach-Object {
  $rel = $_.FullName.Substring((Get-Item $src).FullName.Length + 1)
  $a = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
  $b = (Get-FileHash (Join-Path $dst $rel) -Algorithm SHA256).Hash
  if ($a -ne $b) { "DIFF $rel" }
}
```

收录时这两步都跑过：76/76 一致。

## 4. 怎么升级

不做增量 diff，**整包替换**：

1. 到 https://github.com/tt-a1i/archify/releases 看新的 stable tag
2. 读那一版的 release notes，确认没有破坏性的 IR 变更（上游承诺 2.x 内
   「今天能通过校验的文件，在其声明的 schema 版本内必须继续通过」）
3. 下载新 `archify.zip`，记下 SHA-256
4. 删掉 `skills/archify/` 整个目录，解压新包进去
5. 回来更新本文件的版本 / SHA-256 / 日期
6. 单独一个提交，标题写清版本跨度，别和别的改动混在一起

## 5. 两条注意事项

### 5.1 它会低频联网检查新版本

装好后技能包内的 `scripts/check-update.mjs` 会定期请求上游的版本清单：

```
https://tt-a1i.github.io/archify/skill-updates/archify/stable.json
```

上游声明：只做**提示**，绝不自行下载或安装；不发送本地版本、agent、项目数据、
用户输入或设备标识。但对方的服务器自然会拿到 IP、请求时间和常规 HTTP 元数据。
一次成功后约 72 小时（±20%）再查一次。

**我们没有默认关掉它。** 理由是 vendored 版本是钉死的，这个提示正好用来提醒
该升级了。不想要就在 agent 环境里设：

```
ARCHIFY_UPDATE_CHECK_DISABLED=1
```

（放项目 `.claude/settings.json` 的 `env` 里即可，会连网络请求带提示状态写入一起关。）

如果下游项目对外网请求有硬性约束，这条应该在接入时就设上。

### 5.2 品牌图标的第三方声明不在包里

archify 自身是 MIT，`LICENSE` 在包内。但它内置了 107 个产品品牌图标
（多数来自 Simple Icons，CC0；另有 Angular / Kafka / Jenkins / Rust / Vue 等
各带自己的许可与商标条款），这些的完整声明 **v2.16.0 的包里没有带** ——
只在上游仓库根目录的
[THIRD_PARTY_NOTICES.md](https://github.com/tt-a1i/archify/blob/main/THIRD_PARTY_NOTICES.md)，
包内只有 `brand-marks/README.md` 里的简要说明。

实际影响很小：`brand` 字段**默认就是省略的**，不写就完全不涉及第三方商标。
只有在图里显式给节点挂品牌徽标、且那张图要对外发布时，才需要去看上面那份声明。

## 6. 怎么用

skill 名就是 `archify`，在会话里直接说要画什么即可，例如：

```
用 archify 画一下这个仓库的运行时架构，8-12 个核心组件，突出一条主路径
用 archify 把这个系统的状态机画成 lifecycle 图
```

命令行自己跑（cwd 必须在技能包根目录）：

```bash
node bin/archify.mjs doctor                          # 自检环境
node bin/archify.mjs demo <输出目录>                  # 生成一组样例看效果
node bin/archify.mjs guide "<场景描述>"               # 不确定该用哪种图时问它
node bin/archify.mjs validate <type> <in.json> --quality showcase --json
node bin/archify.mjs deliver  <type> <in.json> <out.html> --quality showcase --json
```

要求 Node >= 18（`package.json` 声明）。**运行时零依赖** —— schema 校验器和品牌图标
都是上游预编译后提交进包的，不装 npm 包也不联网。

不在范围内的：自动 Mermaid 解析、通用自动布局、托管分享、所见即所得编辑器。
Mermaid 输入是「读懂语义后重新创作」，不是机械转换。

上游契约文档在包内：`SKILL.md`（总契约）、`references/authoring-contract.md`
（字段枚举 / 间距数学 / 几何修复）、`schemas/README.md`（五份 IR schema 说明）。
