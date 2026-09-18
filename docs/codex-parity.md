# Codex 那一侧现在有什么

> **这份是给改 XGameHarness 的人看的，不随插件分发。**
> 用 harness 做游戏时不需要读它 —— 那些内容在
> plugins/game-studio-core/docs/HANDBOOK.md。
>
> 放在这里的判据：**一条知识如果只在「维护 harness 本身」时才用得上，
> 它就不该占用每个游戏项目的手册篇幅。** 这份文件原来是 HANDBOOK 的 § 7，
> 2026-09-18 挪出来。

**2026-09-18 在本机实测记录**（读 `~/.codex/` 下的真实安装，不是照文档抄）。
起因：有人问 XGameHarness 能不能同步上 Codex 的插件市场。

**结论：机制都有了，卡在清单格式和版本模型。**

### 两边的对照

| 层 | Claude Code | Codex | 差多少 |
|---|---|---|---|
| **市场清单** | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json` | 路径不同、字段不同。`source` 那格 Claude 是字符串，Codex 是对象 `{"source":"local","path":"./plugins/x"}`，另外多 `policy` 和 `category` |
| **插件清单** | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | 结构几乎一样。Codex 多 `skills: "./skills/"` 指向技能目录，**而且 `version` 必填** |
| **市场目录布局** | `plugins/<插件名>/` | `plugins/<插件名>/` | **一模一样** |
| **技能** | `skills/<名>/SKILL.md`，frontmatter 要 `name` + `description` | 同左，必填字段也是这两个 | **几乎白送** |
| **子 agent** | `agents/*.md`，markdown + frontmatter | `~/.codex/agents/*.toml` 或 `.codex/agents/*.toml`，必填 `name` / `description` / `developer_instructions` | 要转格式，而且 Codex 那份**按账号目录装，不跟插件走** |
| **hooks** | `hooks/hooks.json` + 脚本 | **同一个位置**：插件里的 `hooks/hooks.json`，也可以写进 `plugin.json` 的 `hooks` 项 | 事件名要改，见下 |
| **path-scoped rules** | `.claude/rules/*.md` + 注入 hook | 没有对等物 | 靠 `AGENTS.md` 兜（UI 仓的 `parity.mjs` 在做这件事） |

### hooks：事件对得上，位置也对得上

读本机四个带 hooks 的已装插件（browser / chrome / computer-use / unified-computer-use）
加官方文档，确认下来：

- **事件覆盖了 harness 这 8 个 hook 需要的全部** —— `SessionStart` / `SessionEnd` /
  `UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `PermissionRequest` /
  `PreCompact` / `PostCompact` / `SubagentStart` / `SubagentStop` / `Stop` / `Interrupt`
- **支持 `type: "command"`**，跑 shell 脚本，工作目录是 session 的 cwd
- 声明位置认**插件里的 `hooks/hooks.json`** —— 和 Claude 那边同一个路径

结构也同构，Codex 那边长这样（本机 `unified-computer-use` 的真实内容）：

```json
"hooks": { "hooks": { "Stop": [ { "hooks": [ { "type": "mcp_tool", "server": "…", "tool": "…" } ] } ] } }
```

所以**这不是「那边没有」，是「我们没搬」**。

**逐条比过之后，差距比想的小**。harness 这份 `hooks/hooks.json` 用了 6 个事件，
handler 全是 `command`：

| harness 用的事件 | Codex | |
|---|---|---|
| `SessionStart` | 有 | ✓ |
| `UserPromptSubmit` | 有 | ✓ |
| `PreToolUse` | 有 | ✓ |
| `PostToolUse` | 有 | ✓ |
| `PreCompact` | 有 | ✓ |
| `SessionEnd` | 有 | ✓ |
| `type: "command"` | 支持 | ✓ |
| 条目结构 | 同构 | ✓ |

**六个事件一个不缺，类型也对。**

⚠ **这里原来写着「真正会炸的只有一处：`${CLAUDE_PLUGIN_ROOT}`」——那句也是错的**
（2026-09-18 当天先写错再更正）。Codex 给插件内的 hook 设这几个环境变量：

| 变量 | 说明 |
|---|---|
| `PLUGIN_ROOT` | 装好的插件根目录 |
| `PLUGIN_DATA` | 插件可写的数据目录 |
| `CLAUDE_PLUGIN_ROOT` / `CLAUDE_PLUGIN_DATA` | **兼容别名** |

也就是说 harness 这 8 个 hook 的命令：

```json
{ "type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh\"", "timeout": 20 }
```

**大概率一个字都不用改。** 但注意 Codex 的配置层只替换 `${session_id}` 和 `${cwd}`
两个，别的原样交给 shell —— 所以这条命令能不能跑，取决于 shell 展开那个环境变量，
**而这一步没有实测过**。新设备上第一件要验的就是它。

搬之前 Codex 下的上下文继续靠 `AGENTS.md`（UI 仓的 `sidecar/src/parity.mjs` 在守这件事）。

### 版本号：2026-09-18 改了

Codex 的插件缓存路径是 `~/.codex/plugins/cache/<市场>/<插件>/<版本>/` ——
**版本号就是目录名**，所以 `version` 不是可选的。

原来两个插件都不写 `version`（commit 即版本，推一次更新一次）。
**现在都写了 `1.0.0`。** 换掉是为了同一个仓库也能当 Codex 的市场。

代价要记清楚，它是反方向的：

| | 不写 version（原来） | 写 version（现在） |
|---|---|---|
| 推一次 | 所有项目下个 session 自动拿到 | **没变化**，除非版本号也动了 |
| 忘了操作 | 不可能忘 —— 没有要操作的东西 | 忘了 bump = 全员静默停在旧版本 |
| 失败长什么样 | —— | **没有任何报错**，看起来像"推上去了但没生效" |

Claude Code 官方对内部插件的建议本来就是**不写** version。这次是拿这个便利换
Codex 兼容，不是升级。**改 harness 必须同时 bump**，写进 README「修改 harness 的规范」了。

⚠ 只在 `plugin.json` 里写，**别在 `marketplace.json` 的条目里也写** ——
两处都有时 Claude Code 静默取前者，后者会掩盖你以为改了的那个版本号。

### 两份清单可以并存

它们在不同路径（`.claude-plugin/` vs `.agents/plugins/`），互不干扰。
所以**同一个仓库可以同时是两边的市场**，不用拆仓、不用分支。

### 已经铺好的（2026-09-18，**都没实测**）

仓库里加了三份 Codex 侧的清单，跟 Claude 那份并存、互不干扰：

| 文件 | 作用 |
|---|---|
| `.agents/plugins/marketplace.json` | 市场清单，登记两个插件 |
| `plugins/game-studio-core/.codex-plugin/plugin.json` | 插件清单，`skills: "./skills/"` |
| `plugins/unreal-pack/.codex-plugin/plugin.json` | 同上 |

装的命令（**还没人跑成功过**）：

```bash
codex plugin marketplace add D:/work/GameStudio/XGameHarness
codex plugin add game-studio-core@XGameHarness
codex plugin list
```

⚠ **两处 version 必须一致**（`.claude-plugin` 和 `.codex-plugin` 各一份）。
一个数字放两个文件正是会烂的形状，所以 `validate-git` hook 在提交时比对它们，
不一致当场告警。别靠记。

### 还没验的

**按新设备上该验的顺序排**：

1. **`codex plugin marketplace add` 认不认这个仓** —— 上面那三份清单全是照本机
   已装插件的真实结构抄的，没有一条跑通过。policy 那格只写了 `installation`，
   本机样本还有 `authentication: "ON_INSTALL"`，省略会不会报错不知道
2. **hooks 认不认插件里的 `hooks/hooks.json`** —— 文档说认，但也可能要在
   `plugin.json` 里显式声明 `hooks`（本机四个样本都是内联写的，没有用路径引用的）
3. **`${CLAUDE_PLUGIN_ROOT}` 在命令里展不展得开** —— 见上面 hooks 那节。
   失败是静默的，所以要主动查：开一个 session 看横幅出没出来，而不是等报错
4. **skill 里那句 `${CLAUDE_PLUGIN_ROOT}` 的兜底**（「读不到就当本 SKILL.md 上两级」）
   在 Codex 下走哪个分支
5. 自定义市场怎么注册进 `~/.codex/config.toml`：格式是
   `[marketplaces.<名>]` + `source_type = "local"` + `source = '<路径>'`，
   但本机那个 `personal` 市场没写在 config 里，说明还有一条别的注册路径

**结构性的，不用验也知道补不上**：

- 13 个 agent 是 Claude 插件里的 `.md`，Codex 读 `~/.codex/agents/*.toml`，
  **而且按账号目录装、不跟插件走** —— 就算清单认了，agent 也不会跟过去
- Codex 没有 path-scoped rules 的对等物，只能继续靠 `AGENTS.md` 并进去
