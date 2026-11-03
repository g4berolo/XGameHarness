# Sprint 与 XGS 格式核对（2026-10-30）

NineHundred-Civ7 的四份现有计划使用 SNN-名称.md，任务分布在中文标题和独立
Must Have 下。XGS 原先只发现 sprint-N.md，只读取 Tasks 段，因此返回零期零任务。
项目迁移元数据记录 Core 1.3.1，与本次修改前源码版本一致；未取得生成对话证据，
不能断言是旧技能或未调用技能造成。当前 skill 已规定规范文件名和 Tasks，实际文件
偏离该约定；但共享模板和 fallback 都只有整轮 DoD，未满足 XGS 的逐任务状态关联。

修正 Core 至 1.3.2，两宿主清单保持一致：sprint-plan 增加 XGS 格式契约与写后检查，
模板逐任务 DoD 示例与稳定 ID 对应；producer 要求读取技能和模板。更新原计划须保留
文件名、ID、证据和状态，不能自动补验收批准。未编辑 vendored archify、个人配置或
项目原文件。技能与模板共享，因此 Claude 与 Codex 使用同一约定。

配套 XGS 源码兼容旧文件及表头、明确提示未识别文件、保留状态说明；验收判据仍为
关联 DoD。实际读取四期共 39 个去重任务，缺逐任务 DoD 的状态保持未知。

验证：Python 3.12 环境补齐 PATH 后 unittest 33 项，30 通过、3 跳过；validate.py
通过（3 插件、29 skills、双宿主版本与 hooks）。XGS 专项回归用实际模板替换期号后
确认四个示例任务均关联 DoD，源码构建和组件渲染通过。skill-creator 的 quick_validate.py
因运行环境缺 PyYAML 未执行成功，仓库打包验证及人工 frontmatter 检查已完成。
插件安装、hook 实际触发及游戏实测不属于这些验证结论；未提交、推送或发布。


## 2026-11-03：Core 1.3.3 任务执行类型分离

按用户决定，新增共享docs/task-execution.md：任务标题[AI]/[HUMAN]，制作、人工操作、人工审核使用独立ID与DoD；人工项集中在Tasks末尾Human Actions & Review，前置人工依赖仍须及时完成。AI通过不替人批准，不阻塞已完成AI子任务的独立状态，也不把AI全完成当作Sprint完成。迁移保留父子ID及证据，不随插件升级自动重写项目。

sprint-plan技能、正式模板、fallback、producer、通用流程、项目模板、estimate/scope-check/milestone-review入口同步；双宿主Core清单版本一致为1.3.3。未编辑vendored archify、真实项目或共享记忆。XGS仅同步跨仓模板测试，原有未提交的搜索/跳底修改保留。

验证：unittest共33项，30通过、3个真实Blender测试因未配置BLENDER_BIN跳过；validate.py通过。实际XGS readSprints读取临时模板得到5项（4 AI、1 HUMAN），逐任务DoD全部关联、零warning；跨仓回归额外验证AI勾选完成时人工项仍未完成。现有XGS按标题保留标签，未增加专用筛选或自动执行能力。源码/格式验证不等于安装、hook触发或游戏实测。未提交推送发布。


### 1.3.3 推送与出包回执（2026-11-03）

用户授权推送并出包。发行提交e0d229f已推送origin/main；按该提交git archive生成整个插件市场ZIP，包含Core 1.3.3及其余pack的原版本，不包含未跟踪work/、真实项目或.git目录。解包后validate.py通过，两个Core清单均为1.3.3，新规则文件完整。ZIP大小2435598字节，SHA256为471700ad28187a330e3b95a177f17f9560f49027e9aaac66b13198a6d666672d。插件常规分发仍走仓库市场更新，ZIP为本次源码分发包；未替用户升级具体游戏项目，未做新设备真实插件安装。XGS既有搜索/跳底改动与跨仓模板测试修改仍保留，未混入此ZIP。
