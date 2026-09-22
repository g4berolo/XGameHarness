# 美术资产目录与审查契约（v1）

项目整体美术资产登记表为 `design/art/assets.json`，schemaVersion 为 1。它是可评审元数据，随 design 文档仓下发；二进制源文件仍由工程仓、Git LFS 或团队资产存储管理，不通过文档下发接口传输。登记总览不等于全磁盘自动发现；缺本地源文件只代表本机不可用。

## 默认目录

```
design/art/assets.json                  # 全项目资产登记
design/art/reviews/<id>/<revision>.md  # 审查证据
art/source/<category>/<id>/<revision>/  # PSD、Blend 等可编辑源文件
art/export/<category>/<id>/<revision>/  # FBX、PNG 等交付文件
art/previews/<id>/<revision>.png        # 小尺寸预览；不替代源文件
```

category 建议 character/environment/prop/ui/vfx/animation/material。稳定 ID 使用小写字母、数字、下划线；revision 每次实质改动必须更新，已审版本不可原地覆盖。已有 `art/01_Illustration` 等目录继续兼容，不自动搬迁；在登记表填写实际项目相对路径。

UE 引擎资产留在 `<engine-root>/Content/<Project>/...`，Unity 留在 `<engine-root>/Assets/<Project>/...`，按玩法域或资产集合组织，共享材质单列 Shared。engine-root 可以是 client 或工程根，必须使用项目实际路径，不硬编码 client。第三方资源保留供应商结构及许可文件。

UE 迁移通过编辑器处理引用/重定向器；Unity 保留 GUID 与 .meta 并通过编辑器移动。禁止为了通过目录检查直接移动正在使用的引擎资产。缓存、DerivedDataCache、Library、Intermediate、临时渲染不纳入资产登记。

## 登记格式

参见 `templates/art-assets.json`。每条资产包含 id/name/category/owner/revision/source/export/engine/preview/license/usage/review。路径均为项目相对文件路径，不允许绝对路径、父目录跳转或符号链接越界。未知值用空字符串；不得用猜测填满。

usage 为用途/场景的人工声明，不是引用扫描结果。engine 文件存在只说明本地文件存在，不证明导入配置、场景引用、打包或性能合格。

review 包含 status（draft/in-review/approved/changes-requested）、revision、reviewer（team identity）、evidence（项目相对报告路径）。approved 必须有同版本、真人 reviewer、报告；旧版本结论保留，但新版本必须重新 review。报告分别记录视觉一致性、技术规格、许可来源、引擎引用、目标平台性能及验证方式；未实际运行的项写“未验证”，AI 建议不自动替代真人批准。

审查证据应记录源文件/导出物 SHA-256 或版本库 commit/LFS OID。客户端首版对 revision 和证据路径做检查，不会散列大型资产，也不解析 UE/Unity 引用；原地覆盖且不更新 revision 的变更不能自动检出，不能据此宣称内容验证通过。

## 接入与升级

有美术资产的项目按实际内容填写登记表；空模板不会伪造资产。新项目可复制空表，老项目先盘点和映射旧注册表，不覆盖 `art/asset-registry.md` 或定制路径。只读盘点先列覆盖范围与缺口，不创建假 review；后续整理以独立任务执行。

参考：[UE 目录结构](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-directory-structure)、[Unity 资产元数据](https://docs.unity.com/en-us/engine/6000.3/manual/assets-and-media/import-assets/asset-metadata)。

## 一条资产记录示例（仅格式，不自动导入项目）

```json
{
  "id": "hero_01", "name": "主角", "category": "character", "owner": "artist_identity",
  "revision": "r003", "source": "art/source/character/hero_01/r003/hero.blend",
  "export": "art/export/character/hero_01/r003/hero.fbx",
  "engine": "client/Content/MyGame/Characters/Hero/SK_Hero.uasset",
  "preview": "art/previews/hero_01/r003.png", "license": "原创，作者与权利记录见审查报告",
  "usage": "计划用于主角；尚未核验场景引用",
  "review": { "status": "in-review", "revision": "r003", "reviewer": "", "evidence": "" }
}
```

将记录加入空模板的 assets 数组。source/export/engine 当前各记录主文件；多文件交付的附属纹理、材质和动画清单写入审查报告，后续可扩展 schema，不伪造单文件涵盖全部依赖。登记覆盖范围应在项目 Art Bible 说明；未登记资产不参与客户端统计。
