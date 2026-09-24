# 本机连接与安装

本 pack 由 XGameHarness 自维护，执行器只用 Python 标准库；不下载最新第三方 MCP、不带遥测，
不需要 Tripo/Meshy/BlenderKit 账号。Blender 和 Python 3.11+ 需已安装。没有 Blender 时技能能被
发现，但不能声称建模可用。代码路径来自当前已启用插件根，不从缓存修改时间猜版本。

## 安装

与 unreal-pack 一样从 XGameHarness 市场安装：

```text
codex plugin add blender-pack@XGameHarness
claude plugin install blender-pack@XGameHarness --scope user
```

市场未注册时先添加实际仓库根或 `https://github.com/g4berolo/XGameHarness.git`；不要给同名市场
混用两个来源。更新后重新安装并开新任务。插件包含 `.mcp.json` 与同一套 shell 执行器。
若宿主没加载 MCP，skill 明确使用 CLI，不假装能调用不存在的工具。
XGameHarnessUI 当前的 extraRoots 路线能发现 skill；独立账号中的 MCP/专家装载要另查实际
宿主状态，不能拿个人 Codex 插件安装代替 UI 账号安装。CLI 路线不依赖账号 MCP 配置。

使用 `python <pack>/scripts/configure.py --blender <blender.exe>` 保存本机路径到
`~/.xgh/blender.json`，先检查版本再写入，保留其他字段。它不改模型、账号或审批配置。
路径也可每次传 `--blender` 或用 `BLENDER_BIN`。MCP 默认使用 PATH 上的 `python`。
MCP 启动器兼容两种路径解析：Claude 展开传入的插件绝对路径，Codex 将 `cwd: "."`
定位到插件根。2026-09-24 本机 Codex 0.155.0-alpha.16.3 不展开 MCP args 中的
`${CLAUDE_PLUGIN_ROOT}` / `${PLUGIN_ROOT}`，所以不能把变量直接拼成 Python 文件路径。

## 批量模式

```text
python <pack>/scripts/runner.py doctor
python <pack>/scripts/runner.py build --workspace <asset> --script <build.py>
python <pack>/scripts/runner.py build --workspace <asset> --script <edit.py> --blend <input.blend>
python <pack>/scripts/runner.py inspect --workspace <asset> --blend <output.blend> --max-triangles 5000
python <pack>/scripts/runner.py preview --workspace <asset> --blend <output.blend> --timeout 300
python <pack>/scripts/runner.py export --workspace <asset> --blend <output.blend> --format glb
```

每个任务返回 JSON 回执和准确产物路径。build 保存输入脚本快照；外部参数/素材仍需随资产保存，
不是把脚本复制一份就证明可复现。inspect 检查求值后网格、单位、三角面、非流形边、UV、负缩放、
缺失贴图和来源标签；预算未知返回 null。export 实际读回导出文件，不代表 UE 验证。
失败/超时返回非零，日志留在本轮目录；不会自动无限重试。

## 实时模式

```text
python <pack>/scripts/runner.py live-start --workspace <asset> --owner <task-id> --blend <input.blend>
python <pack>/scripts/runner.py live-status --workspace <asset> --owner <task-id>
python <pack>/scripts/runner.py live-exec --workspace <asset> --owner <task-id> --script <edit.py>
python <pack>/scripts/runner.py live-save --workspace <asset> --owner <task-id>
python <pack>/scripts/runner.py live-stop --workspace <asset> --owner <task-id>
```

省略输入则从默认场景开始。启动专用可见窗口并立即另存 working.blend；不接管用户已有窗口。
由同一 task-id 使用，其他任务不能借 ID。MCP 会自动生成自己的 owner，无需用户填写。
重启 MCP 后不能认领旧窗口；用户可在 Blender 内保存关闭，原 owner 的 CLI 也可关闭。

bridge 只监听 127.0.0.1 随机端口，需随机 token，拒绝网页 Origin；命令排队后在 Blender
主线程执行。它不是操作系统安全沙箱：exec 中的 Python 和后台脚本都具有本地用户权限，
遵守宿主工具审批。任意 Python 可绕过应用级文件规则，因此不能向不受信任代码开放它。
token 元数据 `.xgh-live.json` 只留本机；与 `.xgh-blender.lock` 一起加入资产项目 .gitignore。
进程崩溃后 OS 自动释放锁；不删除锁文件来“解锁”。超时可能已有部分修改，先检查后决定。
stop 会另存副本后退出。直接关闭窗口按 Blender 原生保存行为处理。
