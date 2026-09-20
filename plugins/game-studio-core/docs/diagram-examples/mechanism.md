# 机制图：用对象和变化解释规则

下面示范“扩容不自动补满”的画法。只有源 GDD 明确规定这条行为时才能采用。
其他系统应换成自己的对象、条件和结果，不把示例规则带进设计。

左右两幅都从同一位置开始画体力，已有体力长度相同，容量轮廓变长。
因此读者可以直接看出“上限变了，已有体力没变”。文字仍负责说明补给结算顺序和例外。

```svg
<svg viewBox="0 0 520 200">
  <title>扩容增加上限，已有体力保持不变</title>
  <rect class="box" x="12" y="12" width="230" height="150" rx="12"/>
  <rect class="box" x="278" y="12" width="230" height="150" rx="12"/>
  <text class="name" x="28" y="38">扩容前</text>
  <text class="name key" x="294" y="38">只提高上限后</text>
  <rect class="line" x="28" y="62" width="140" height="30" rx="6"/>
  <rect class="box ok" x="32" y="66" width="72" height="22" rx="3"/>
  <rect class="line key" x="294" y="62" width="196" height="30" rx="6"/>
  <rect class="box ok" x="298" y="66" width="72" height="22" rx="3"/>
  <line class="line dashed" x1="434" y1="56" x2="434" y2="98"/>
  <path class="line key" d="M248 77 H272" marker-end="url(#arrow-key)"/>
  <text class="label" x="28" y="118">填充：已有体力</text>
  <text class="label" x="28" y="140">轮廓：当前上限</text>
  <text class="label" x="294" y="118">虚线：扩容前的上限</text>
  <text class="name ok" x="294" y="140">容量变大，体力没有补满</text>
  <text class="label" x="260" y="186" text-anchor="middle">示意，非数值比例；只展示扩容，不包含回复</text>
</svg>
```

其他构图的选择：

| 要解释的问题 | 适合的画面 | 保留的参照 |
|---|---|---|
| 什么动作消耗、保持或回复资源 | 动作图标与资源条配对，标明变化方向及条件 | 相同容量、方向和语义色 |
| 耗尽后角色发生什么 | 按时间排列动作分镜，画出松手、下落、落地等源文档行为 | 同一角色与地面位置 |
| 两个条件共同满足才可重试 | 两个独立条件标记汇合到可用动作 | 各条件的未满足与满足状态 |

避免为了装饰添加无关图标。先检查规则和箭头，再检查对齐、留白、文字遮挡及明暗主题。
图形通过客户端白名单只能说明可以渲染，最终需要看实际画面。
