# XGameHarness 游戏开发适用性审查

审查日期：2026-09-19（项目本地时区）。范围：本仓库流程、skills、rules、记忆脚本，以及三个开源项目的一手文档和 skill 源码。外部链接读取的是当日主分支，后续可能变化。

**结论：适合继续发展成 Codex 游戏开发 harness。现有优势是策划、阶段管理、团队知识交接；最需要补的是实现与验证的闭环，而不是继续增加角色数量。** Codex 的接入应保持同一份游戏流程和项目事实，通过运行时适配层解决工具、事件和安装差异。

本报告是静态审查与联网对比，**没有实际启动 Unreal、Unity 或 Godot，也没有运行消费方游戏、测量帧率或完成打包**。下文“已有”指审查时读取到的文件；“建议”均不是已交付能力。本轮同时进行的 Codex 适配，以对应迁移文档和测试结果为准，本报告不替它声明客户端端到端通过。

## 1. 已有能力及适用边界

| 工作 | 适用判断 | 仓库依据与边界 |
|---|---|---|
| GDD、系统设计、ADR、Sprint 与阶段评审 | 适合 | 已有 `design-system`、`design-review`、`sprint-plan`、`gate-check`；阶段 SoT 和 Critical 子阶段规则可保留 |
| 文本代码、配置、工具脚本、测试编写和缺陷定位 | 适合，但需要项目提供执行入口 | `code-review` 和 UE `test-standards.md` 有规则；有规则不等于已有可运行的构建测试服务 |
| 原型与玩法迭代 | 适合协作 | `prototype` 有假设、时间盒、数据和继续/转向/停止结论；实际观察仍需可启动环境或真人反馈 |
| Blueprint、关卡、动画、材质和其他编辑器资产 | 有条件 | UE 专家提示可帮助推理，不能证明具有编辑器访问或二进制资产编辑能力；需引擎脚本/API/已验证连接器及可回读的结果 |
| 手感、美术质量、可读性与趣味性 | 需要真人参与 | `playtest-report` 可以结构化真实反馈；文档完整或截图正常不能证明“好玩” |
| 发布和目标平台性能 | 当前流程不足以独立完成 | `gate-check` 已明确无性能剖析 skill、发布清单 skill；需要真实目标设备和构建产物 |

值得保留的设计：`plan/stage.md` 单一阶段事实源、通用门槛与项目自定义子阶段分离、rules 分发源与项目定制分离、`team/` 文件记忆、设计文档与试玩报告固定落盘。不要为迁移 Codex 再建第二套阶段状态或第二份 GDD。

## 2. 优先处理的问题

### P0：补全“实现完成”的证据定义

`gate-check` 已要求实际运行测试且不可对未知项判 PASS，这个原则正确。但 gate 多发生在阶段边界，普通实现任务缺少统一的“构建 → 测试 → 核心流程启动 → 证据归档”入口；`playtest-report` 也只是记录与分析流程。建议新增 `verify-game-change`：

- 从项目配置读取引擎版本、工程路径、平台、构建/测试/打包命令，不根据引擎名字猜测命令。
- 输出 `PASS / FAIL / NOT_RUN / STALE`；缺引擎、许可证、设备或 runner 就记录 NOT_RUN，不能变成通过。
- 每次记录 commit、工作区内容指纹、引擎版本、平台、命令、退出码、日志、测试数量与失败项、运行时间；避免旧日志冒充本次结果。
- GDD 验收条件和 Sprint ID 指向对应证据；代码或数据变化后，旧证据必须失效或明确覆盖范围。
- 分开记录“编译通过”“测试通过”“打包通过”“真人试玩通过”，不相互代替。

可借鉴 Superpowers 的“先执行并读取验证结果，再声明完成”流程；这里建议按修改风险选择验证，不把每次文档调整都变成全量引擎构建。[verification-before-completion 源码](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md)

GSD Core 的验证文档进一步使用内容指纹识别陈旧验证报告，这适合避免游戏配置和资产更新后仍引用旧 PASS。[verify-and-ship](https://github.com/open-gsd/gsd-core/blob/main/docs/how-to/verify-and-ship.md)

### P0：跨运行时能力必须真实可查

迁移前技能普遍依赖 `CLAUDE.md`、`.claude/`、`${CLAUDE_PLUGIN_ROOT}` 和 Claude 工具名。插件可被市场发现、skill 可被加载、hook 可触发、hook 能阻断动作，是四个不同验收项。应在兼容表里逐项写清楚；无原生事件时，用明确的项目指令/显式检查降级，不宣称等价强制执行。

建议保留统一流程源，生成或适配安装入口；对更新、路径解析、项目定制保留和 hook payload 做回归。客户端实际安装、启用和重启后的 smoke test 也应独立记录，不能由 JSON 合法性代替。

### P1：记忆按任务隔离，并保证快照真实

`resolve-identity.sh` 将一个开发者所有工作定位到 `team/session-state/{identity}/active.md`。同一 checkout 内同时开两个任务，会相互覆盖；两个 worktree 合并时也可能产生同一路径冲突。建议在该目录下引入任务状态文件，`active.md` 只作索引；记录 task ID、branch/worktree、更新时间、来源文件和下一步，写入采用临时文件加原子替换。

另一个具体风险：审查时 `session-stop.sh` 只写 `active.md @ HEAD` 指针。如果当前记忆未提交，`git show HEAD:...` 返回的是旧状态，甚至路径不存在。应记录 dirty 状态并保存内容哈希/有界快照，不能声称 HEAD 可恢复未提交内容。用两个并发任务和一次未提交退出场景验证。

GSD 的文件状态和紧凑任务上下文值得借鉴；不必引入第二套 `.planning/`，可继续使用现有 `plan/` 和 `team/`。也不应照搬其文档中对特定上下文大小及子代理能力的假设。[context-engineering](https://github.com/open-gsd/gsd-core/blob/main/docs/explanation/context-engineering.md)

### P1：让 Sprint 任务直接通向可执行工作

现有 Sprint 模板已有依赖、验收条件和状态，但缺少统一的实现交接工件。建议补充：目标行为、允许修改范围、相关 GDD/ADR、复现步骤、验证入口、证据链接、阻塞原因。`implement-task` 按这些字段完成一个小任务，调用 `verify-game-change`，通过后再更新状态；失败则保留失败证据和下一步。

调试流程建议为“稳定复现 → 定位边界 → 单一假设 → 最小修复 → 回归”，特别适合输入、存档、联机与资源加载问题；不要让 agent 连续尝试多个无依据补丁。[Superpowers systematic-debugging 源码](https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md)

### P1：把游戏专属验证提到日常开发

现有 UE 测试 rules 已覆盖确定性、隔离、回归和性能阈值；缺口主要是执行与产物。建议第一批只做：

| 验证类型 | 最小证据 | 适用触发 |
|---|---|---|
| 核心流程 smoke | 启动、进入关卡、完成一次核心循环、退出的结果与日志 | 核心玩法、流程、资源加载改动 |
| 存档兼容 | 旧版本 fixture、读写往返、错误存档行为 | 存档结构改动 |
| 数据/资产 | 引用有效性、命名/目录、缺失资源、来源与许可记录 | 新资产、资源移动、配置改动 |
| 性能 | 固定场景/seed、分辨率、设备、构建类型、帧时间分位数、内存峰值 | 热路径和资源预算变化 |
| 联机（项目需要时） | 多客户端、延迟/丢包条件、权威状态一致性 | 复制、预测和网络协议变化 |
| 视觉/手感 | 关联 build 的视频/截图与真人观察，区分观察和推测 | 动画、镜头、UI、反馈调整 |

这些是建议的能力包，不代表所有项目都要启用。对 UE 二进制资产的并行修改要有明确所有者与锁定/交接规则；Git worktree 隔离文本修改并不自动解决资产冲突。

### P2：降低不必要的流程成本

`sprint-plan`、`playtest-report` 等技能要求在写普通报告前再次询问；`code-review` 把 40 行函数、复杂度阈值和接口化视为通用标准，容易把引擎惯例与具体正确性混在一起。建议：

- 用户已明确要求产出文件时，直接完成可逆写入；只对真正未授权的外部发布、破坏性动作或关键产品决策再确认。
- 小修复走轻流程；跨系统功能走完整设计/实现/验证；阶段晋级保留明确决策。
- 审查优先报可复现缺陷、回归、线程/生命周期、存档和性能风险；风格阈值作为项目可配置建议。
- 原型允许基于明确证据决定“丢弃重写”或“审查后提升”；当前一律从零重写可能浪费已验证工作，但不得未经审查直接投入生产。

GSD 文档本身明确承认完整阶段循环对微小任务过重，并提供轻量路径；这是可借鉴的取舍，而非所有任务都要多代理。[context-engineering 的 trade-offs](https://github.com/open-gsd/gsd-core/blob/main/docs/explanation/context-engineering.md)

## 3. 开源对比：借机制，不按角色数量判断成熟度

| 项目及实际读取范围 | 值得借鉴 | 不直接照搬 |
|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers)：README、验证与调试 skills | 验证后再声明完成、根因调试、独立代码审查、插件基础设施与行为评测分开 | 所有改动强制相同 TDD 仪式；游戏视觉和手感仍需真实反馈 |
| [GSD Core](https://github.com/open-gsd/gsd-core)：README、上下文与验证文档 | 文件状态、任务依赖、失败后补缺、证据失效检测、轻重流程分流 | 为接入再造目录事实源；固定上下文尺寸；把用户空答当验收通过 |
| [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios)：README、smoke-check 与 test-evidence-review 源码 | QA handoff、按 Logic/Integration/Visual 等类型检查证据质量，而非只数测试文件 | 直接复制 Claude 专属工具/模型/路径；把 NOT_RUN 包装为通过；仅凭测试文件存在判断覆盖 |

上游 Game Studios 的 `test-evidence-review` 专门检查断言与验收条件是否匹配，这比“找到了测试文件”更可靠。[源码](https://github.com/Donchitos/Claude-Code-Game-Studios/blob/main/.claude/skills/test-evidence-review/SKILL.md) 但其 `smoke-check` 对未执行测试的处理偏宽松，因此建议只借鉴结构，并保留明确 NOT_RUN 状态。[源码](https://github.com/Donchitos/Claude-Code-Game-Studios/blob/main/.claude/skills/smoke-check/SKILL.md)

调研时原 [gsd-build/get-shit-done README](https://github.com/gsd-build/get-shit-done/blob/main/README.md) 已指向 `open-gsd/gsd-core`，故使用新仓库资料。外部项目数量、宣传和 README 不构成效果实测；本报告未运行它们，也未验证它们所有平台承诺。

## 4. 建议交付顺序与验收

1. **先完成本轮 Codex 接入**：市场能发现两个插件；skill 能运行；规则/记忆能定位；支持的 hook 有真实触发记录；降级项清楚；旧 Claude 安装继续可用。
2. **接一个真实 UE 消费项目做垂直验证**：配置一个 build 和一组快速自动化测试；引入一个已知失败再修复；保存两份可追溯证据；没有引擎时明确 NOT_RUN。
3. **补任务与记忆闭环**：实现一个 Sprint 任务并关联证据；同时开两个任务验证状态不串写；未提交记忆退出后可恢复。
4. **按实际需要增加资产/性能/发布能力**：先覆盖消费项目高频失败，后扩展 Unity/Godot，避免只有提示词没有可执行适配器。

现有 `labs/digest-lab` 是良好起点，但 README 明确限定为读本可读性实验，并非整个 harness 的质量评测。建议新增固定场景：错误 skill 路由、陈旧记忆、跨运行时恢复、测试失败不可报成功、修改后证据过期、项目定制升级不覆盖。分别记录首次成功率、人工追问次数、恢复正确率、耗时和失败原因，不以文档篇数或 agent 数量作质量指标。
