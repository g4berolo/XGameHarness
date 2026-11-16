# 多人候选评审起草 — core 1.3.4

2026-11-16：新增共享proposal-draft技能，供Claude/Codex生成GDD、系统、Sprint候选JSON。读本和技术原文分开，Sprint的AI执行与人工审核分开；XGS导入检查后由用户发布。AI不能伪造评论、作者或采纳，不能直接修改team/reviews绕过负责人采纳。

两宿主插件版本均为1.3.4。python scripts/validate.py通过（3插件、30技能）；unittest执行33项，3项按环境跳过，其余通过。XGS隔离浏览器已验JSON导入发布及双模拟身份讨论/采纳；真实模型起草、安装与hook触发未验收，不将源码测试当作引擎实测。分发以Git仓库更新为准；不包含work目录中的既有项目数据。


## 发行回执

发行提交e05f0e3已推送origin/main。git archive生成整个市场分发包tmp/release-1.3.4/XGameHarness-core-1.3.4.zip（不包含work及.git），2430348字节，SHA256：15cd09022dc761e2c3483a7eda6406564dff76df443fa936fedcfdbb3a65ddd2。解包结构校验通过，常规插件分发仍通过Git市场更新。未自动修改具体游戏项目或个人配置。
