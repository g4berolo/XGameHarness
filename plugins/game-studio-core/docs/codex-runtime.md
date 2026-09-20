# Codex 项目运行约定

这是 XGameHarness 的 Codex 入口。共享文档里 `/skill-name` 在 Codex 对应
`$skill-name`（或直接请求使用该技能）；没有 Skill 工具时读取对应 SKILL.md 执行。
`${CLAUDE_PLUGIN_ROOT}` 表示当前技能所属插件根目录，按实际 SKILL.md 向上两级定位，
不要把占位符原样交给终端。hook 中 Codex 提供 `PLUGIN_ROOT` 及兼容别名。

## 任务与专家

- 按任务实际需要选 skill，不因关键词命中就强制进入整套立项或审批流程。
- 共享文本中的 Read/Glob/Grep/Bash/AskUserQuestion 表示能力，映射到宿主现有工具。
  Claude 的 `allowed-tools`、`memory: user`、`skills` agent 元数据不作为 Codex 配置。
- `.codex/agents/<pack>--<role>.toml` 是项目级专家；不硬编码模型，不放宽沙箱。
  自定义类型不可用时读取角色指令，用现有通用子 agent（已有委派授权时）或主 agent 执行。
- 同目录并行时明确文件归属；禁止多个 agent 同时编辑 `.uasset`、`.umap`、同一场景或同一记忆文件。
- 普通修复直接实现并验证。范围、玩法方向等真正未定的问题才需要用户作决策。

## 规则、状态和记忆

- `.claude/team.json`、`.claude/rules/`、`.claude/harness-config.json` 是兼容现有
  Claude 和 Studio 的共享项目契约；Codex 可以独立使用，不需要安装 Claude。
- 规则编辑前按 frontmatter `paths` 加载；hooks 是补充提醒，不是安全边界。
  没有 hooks 时仍遵守 AGENTS.md。删除 `managed-by` 可保留项目定制规则。
- `plan/stage.md` 是阶段事实源；ADR、GDD 和测试记录是持久知识。先查索引，再读相关文件。
- 用 `.claude/team.json` 的 `git_users`／`git_emails` 解析身份；未映射时先配置，
  禁止多个用户共写 `unknown/active.md`。不自动收录邮箱。
- `team/session-state/{identity}/active.md` 是人工维护的恢复摘要，不是自动生成的事实。
  同时运行多个任务时各自写 `sessions/{session_id}.md`，由用户指定的负责人合并 active.md。
- 重要阶段完成、切换任务和压缩前，记录目标、已完成、文件、验证命令及结果、阻碍和下一步。
  每条长期决策给文件／commit 证据；恢复时重新核验，不照抄陈旧待办。
- hook 仅记录机械检查点（Git HEAD、工作区状态、时间和恢复路径），不伪造语义总结，
  不读取完整聊天记录，不修改 Codex 个人记忆目录。非正常退出无法保证 SessionEnd，
  所以语义摘要在工作中及时保存，不能等关闭程序。

## 游戏开发验证

代码完成不等于玩法验证完成。报告分别列出编译／自动测试、引擎运行、真机性能和真人试玩证据。
未启动引擎或未实测时写「未验证」。UE 二进制资产通过可用的编辑器／受信 MCP 操作，
没有工具时交付明确的编辑器步骤，不用文本编辑伪造资产。
每个玩法改动至少明确：可复現步骤、期望结果、回归场景和所需设备／引擎版本。

## 初始化和升级

从当前安装的 core 插件运行 `scripts/harness.py init --project <项目根>`；已有项目用
`sync`，只同步规则用 `sync-rules`，检查用 `doctor`。可先加 `--dry-run`。
UE 另传当前启用的 `--unreal-root <unreal-pack根>`，不按缓存目录时间猜版本。
脚本只改项目文件；不会安装全局 agent、修改个人 config、信任 hooks、提交或推送。
自定义 AGENTS.md 内容与手改 agent 被保留。升级后在 Codex 新任务中确认技能加载，
用 `/hooks` 审阅并信任变更的 hook 定义；安装插件不会自动完成此步骤。
