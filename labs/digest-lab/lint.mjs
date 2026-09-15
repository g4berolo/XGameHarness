/**
 * 尺子 —— 一篇 GDD + 它的读本，不花钱，每次都跑。
 *
 *   node labs/digest-lab/lint.mjs <项目目录> [--gdd stamina.md] [--ui <XGameHarnessUI 目录>] [--out lint.json]
 *
 * 判据只从两份正本抄：`rules/design-docs.md` 的「读本怎么写」+「三条硬规矩」，
 * 和 `write-digest` 第 5.5 步那五条收尾核查。**这里不另立规矩** —— 规矩改了，这里跟着改。
 *
 * 三档：
 *   红   硬规矩，违反一条就是一条
 *   黄   要人判的（数字灰区、排版、疑似实现细节）
 *   数字 篇幅、图数、字数 —— 只记录，不评判
 *
 * 「读本旧没旧」那条判据**借客户端的**（`sidecar/src/board.mjs` 的 `readGddDoc`），
 * 不另写一份 —— 两份判据的下场是客户端说旧、这里说不旧，而两边都不报错。
 * 借不到（UI 仓不在旁边）就退回自己那份简陋的解析，并在输出里说一声。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const args = process.argv.slice(2);
const projectDir = args[0] && !args[0].startsWith('--') ? path.resolve(args[0]) : null;
const opt = (k, d = null) => { const i = args.indexOf(k); return i >= 0 && args[i + 1] !== undefined ? args[i + 1] : d; };
const GDD_FILE = opt('--gdd', 'stamina.md');
const UI = path.resolve(opt('--ui', path.join(ROOT, '..', 'XGameHarnessUI')));
const OUT = opt('--out');
if (!projectDir) {
  console.error('用法：node labs/digest-lab/lint.mjs <项目目录> [--gdd stamina.md] [--ui <UI 目录>] [--out lint.json]');
  process.exit(2);
}

const red = [], yellow = [], notes = [];
const nums = {};
let rigor = null;
let borrowed = false;
const R = (code, msg, where = '') => red.push({ code, msg, where });
const Y = (code, msg, where = '') => yellow.push({ code, msg, where });

// ── 规定的十三节 / 五节（标题原文来自 rules/design-docs.md「十三节」）────────
function T(label, re) { return Object.assign(re ?? new RegExp(`^${label}$`), { label }); }
const FULL_TITLES = [
  T('一句话'), T('打个比方'), T('没有它，游戏会缺什么'), T('玩家在里面经历什么'),
  T('它怎么运转'), T('它明确不做的事'), T('N 个关键决定', /^.+个关键决定$/), T('最容易搞错的 N 件事', /^最容易搞错的.+件事$/),
  T('一个完整的例子'), T('名词对照'), T('旋钮速查'), T('如果你要跟它对接'), T('只记三句话'),
];
const LITE_TITLES = [T('一句话'), T('打个比方'), T('它怎么运转'), T('最容易搞错的 N 件事', /^最容易搞错的.+件事$/), T('只记三句话')];

// ── 正则 ──────────────────────────────────────────────────────────────────
const IMPL_PATTERNS = [
  { code: 'class', re: /\b[A-Z][a-z]+[A-Z][A-Za-z0-9]+\b/g },          // 两个驼峰以上：ActionRequest / OnStaminaDepleted
  { code: 'ue', re: /\b[UAF][A-Z][A-Za-z0-9]{2,}\b/g },                // UE 风格：URoomBase / FRoomEvent
  { code: 'call', re: /\b[A-Za-z_]\w*\(\)/g },                          // CalcDamage()
  { code: 'file', re: /\b[\w.-]+\.(cpp|h|hpp|cs|mjs|ts|tsx|py|json|md)\b/g },
  { code: 'path', re: /\b(design|docs|team|plan|client|src)\/[\w./-]+/g },
];
const DIGEST_ID_PATTERNS = [
  { code: 'sysid', re: /#\d+\b/g },                                     // #22
  { code: 'code', re: /\b[A-Z]{1,3}-[A-Z]?\d+[A-Z]?(-[A-Z0-9]+)?\b/g },  // PP-D5 / BF-22-B / ADR-0001
  { code: 'rule', re: /\bR\d+\b|§\s*\d/g },                              // R7 / §3.3
];
const SKIP_PATTERNS = [
  { code: 'skip', re: /详见|见下文|见下面|见上文|具体规则见|见\s*Detailed|见第?\s*\d+\.\d+/g },
];
const NUM_PATTERNS = [
  { code: 'unit', re: /\d+(\.\d+)?\s*(%|％|秒|格|点|次|倍|米|帧|层|级|个|下|口|ms|s\b|m\b)/g },
  { code: 'op', re: /[=×÷≈]/g },
  { code: 'range', re: /\d+\s*[-–~]\s*\d+/g },
  { code: 'decimal', re: /\d+\.\d+/g },                                  // 2.5 这种，多半是倍率
  { code: 'num', re: /(?<![A-Za-z#.\d])\d{2,}(?![\d.])/g },              // 两位以上的裸数字
];
const CN = { 零: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 };

// ── 读文件：能借客户端的就借 ───────────────────────────────────────────────
let doc = null;
try {
  const board = await import(pathToFileURL(path.join(UI, 'sidecar', 'src', 'board.mjs')).href);
  const r = board.readGddDoc(projectDir, GDD_FILE);
  if (r.ok) { doc = r; borrowed = true; } else { R('G-READ', `读不到 GDD：${r.why}`); }
} catch (e) {
  notes.push(`没借到客户端的 readGddDoc（${String(e.message).split('\n')[0]}）—— 「读本旧没旧」按这里自己的简陋解析判，结果可能跟客户端不一致`);
  doc = readOwn(projectDir, GDD_FILE);
}
if (!doc) finish();

// ── GDD 那半 ───────────────────────────────────────────────────────────────
// 客户端给的 body 已经切掉了头部块；前面补回同样多的空行，报出来的行号才跟文件对得上
const gddBody = padToFile(path.join(projectDir, 'design', 'gdd', GDD_FILE), doc.body);
const field = (...names) => {
  for (const n of names) {
    const v = doc.fields?.[n] ?? doc.extra?.[n];
    if (v !== undefined && v !== null && String(v).trim() !== '') return String(v).trim();
  }
  return null;
};
const rigorRaw = field('rigor', 'Rigor', '档位');
rigor = /lite/i.test(rigorRaw ?? '') ? 'Lite' : /full/i.test(rigorRaw ?? '') ? 'Full' : null;
if (!field('status', 'Status', '状态')) R('G-HEADER', '头部缺 Status');
if (!rigor) R('G-HEADER', '头部缺 Rigor（Lite / Full）');
if (!field('updated', 'Last Updated', '最后更新')) R('G-HEADER', '头部缺 Last Updated —— 读本旧没旧全靠它');
if (rigor === 'Full' && !field('升 Full 的理由')) R('G-HEADER', 'Full 文档头部缺「升 Full 的理由」');

const gddH2 = headings(gddBody, 2).map((h) => h.text);
const has2 = (re) => gddH2.some((t) => re.test(t));
for (const s of ['设计前提', '已定决策摘要', '本篇用到的新词']) {
  if (!has2(new RegExp(`^${s}`))) R('G-OPEN', `缺开场那节：## ${s}`);
}
const termsSec = sectionBody(gddBody, 2, /^本篇用到的新词/);
if (termsSec !== null && tableRows(termsSec) === 0 && !/无/.test(termsSec)) {
  R('G-TERMS', '「本篇用到的新词」既没有表格行也没写「无」—— 不许留空');
}
const need = rigor === 'Lite'
  ? [/^意图/, /^(改动|构成)/, /^非目标/, /^验收/]
  : [/^Detailed (Design|Rules)/i, /^Formulas/i, /^Edge Cases/i, /^Dependencies/i, /^Tuning Knobs/i, /^Acceptance Criteria/i];
for (const re of need) if (!has2(re)) R('G-REQ', `缺必需节：${re.source}`);
const tbd = (gddBody.match(/\[To be designed\]/g) ?? []).length;
if (tbd) R('G-TBD', `还剩 ${tbd} 处 [To be designed]`);
if (doc.digestInline) R('G-INLINE', 'GDD 正文里还留着 ## 读本 —— 读本该在 design/digest/ 里单独一个文件');

// 「已定决策摘要」那节按规矩要写出处文件，路径出现在那儿是对的，不数
const decisions = headings(gddBody, 2).find((h) => /^已定决策摘要/.test(h.text));
const gddProse = proseLines(gddBody).filter((l) => !decisions || l.line <= decisions.line || l.line >= decisions.endLine);
const implHits = scan(gddProse, IMPL_PATTERNS);
nums.gddImplHits = implHits.length;
if (implHits.length) Y('G-IMPL', `GDD 里 ${implHits.length} 处疑似实现细节（类名 / 函数 / 路径）`, sample(implHits));
const numRows = gddBody.split('\n').filter((l) => {
  const t = l.trim();
  if (!/^\|/.test(t) || /^\|[\s\-:|]+\|$/.test(t)) return false;
  const cells = t.replace(/^\||\|$/g, '').split('|').map((c) => c.trim()).filter(Boolean);
  return cells.length >= 2 && cells.every((c) => /^[\d.%％\-–~+\s]+$/.test(c));
});
nums.gddNumericRows = numRows.length;
if (numRows.length) Y('G-NUMROW', `GDD 里 ${numRows.length} 行整行都是数字的表格行（数值表本体该在数据表里）`);
nums.gddBytes = Buffer.byteLength(gddBody, 'utf8');
nums.gddLines = gddBody.split('\n').length;

// ── 读本那半 ───────────────────────────────────────────────────────────────
const dg = doc.digest;
if (!dg) {
  R('D-MISSING', `没有 design/digest/${GDD_FILE}`);
  finish();
}
const digestPath = path.join(projectDir, 'design', 'digest', GDD_FILE);
const digestSrc = fs.readFileSync(digestPath, 'utf8').replace(/\r\n/g, '\n');
const dLines = digestSrc.split('\n');
const dBody = padToFile(digestPath, dg.body);

// 头部
if (!/^#\s+.+\s[—-]\s*读本\s*$/.test(dLines[0] ?? '')) R('D-H1', '第一行不是「# <跟 GDD 一样的标题> — 读本」', dLines[0]);
const headExtra = readHeaderBlock(digestSrc);
const docRef = headExtra['文档'];
if (!docRef) R('D-HEAD', '头部缺「**文档**：design/gdd/<文件名>.md」那一行');
else if (docRef.trim() !== `design/gdd/${GDD_FILE}`) R('D-HEAD', `头部「文档」指错了：${docRef}`);
if (!headExtra['最后更新']) R('D-HEAD', '头部缺「**最后更新**：<今天>」');
if (dg.basedOn == null) R('D-STALE', '头部缺「写于文档的最后更新」—— 客户端永远判不出读本旧没旧，而且不报错');
else if (dg.stale === true) R('D-STALE', `读本写在文档上次改动之前：GDD 是「${dg.gddUpdated}」，读本记的是「${dg.basedOn}」`);
else if (dg.stale === null) R('D-STALE', '「写于文档的最后更新」和 GDD 的 Last Updated 缺一边 —— 不知道，不许当成不旧');
if (!borrowed) notes.push('stale 那条是自己算的，不是客户端那份判据');

// 标题层级 + 编号
const dH = headings(dBody, [2, 3, 4]);
for (const h of dH.filter((x) => x.depth === 2)) R('D-H2', '读本里不许用 ##（客户端目录会多一层空壳）', `第 ${h.line} 行：${h.text}`);
const h3 = dH.filter((x) => x.depth === 3);
const expected = rigor === 'Lite' ? LITE_TITLES : FULL_TITLES;
nums.digestSections = h3.length;
if (h3.length !== expected.length) R('D-SECTIONS', `三级标题 ${h3.length} 节，${rigor ?? 'Full'} 应该是 ${expected.length} 节`);
h3.forEach((h, i) => {
  const m = /^(\d+)\.\s+(.+)$/.exec(h.text);
  if (!m) { R('D-NUM', `三级标题没编号：${h.text}`, `第 ${h.line} 行`); return; }
  const n = Number(m[1]);
  if (n !== i + 1) R('D-NUM', `三级标题编号断了：第 ${i + 1} 个标题写的是 ${n}.`, `第 ${h.line} 行：${h.text}`);
  const want = expected[i];
  if (want && !want.test(norm(m[2]))) R('D-TITLE', `第 ${i + 1} 节标题不是规定的那个（要「${want.label}」）`, `第 ${h.line} 行：${m[2]}`);
});
let parent = null, sub = 0;
for (const h of dH) {
  if (h.depth === 3) { parent = /^(\d+)\./.exec(h.text)?.[1] ?? null; sub = 0; continue; }
  if (h.depth !== 4) continue;
  const m = /^(\d+)\.(\d+)\s+(.+)$/.exec(h.text);
  if (!m) { R('D-NUM4', `四级标题没编号：${h.text}`, `第 ${h.line} 行`); continue; }
  sub += 1;
  if (m[1] !== parent) R('D-NUM4', `四级标题 ${m[1]}.${m[2]} 没跟父节号（父节是 ${parent}）`, `第 ${h.line} 行`);
  if (Number(m[2]) !== sub) R('D-NUM4', `四级标题 ${m[1]}.${m[2]} 编号断了（该是 ${parent}.${sub}）`, `第 ${h.line} 行`);
}
// 标题里的数目 = 读者看到的条目数（四级标题 / 列表项 / 表格行 / 段落，哪种承载的数哪种）
for (const h of dH.filter((x) => x.depth >= 3)) {
  const count = countInTitle(h.text);
  if (count == null) continue;
  const body = sectionAt(dBody, h);
  const kids = dH.filter((x) => x.depth === h.depth + 1 && x.line > h.line && x.line < h.endLine).length;
  const li = listItems(body), tr = tableRows(body), pa = paragraphs(body).length;
  const [items, carrier] = kids ? [kids, '四级标题'] : li ? [li, '列表项'] : tr ? [tr, '表格行'] : [pa, '段落'];
  if (items !== count) {
    const msg = `标题说 ${count} 条，数到 ${items} 条（按${carrier}数的）`;
    if (/^```(mermaid|svg)/m.test(body)) Y('D-COUNT', `${msg} —— 这节有图，条目可能在图里，要人数`, `第 ${h.line} 行：${h.text}`);
    else R('D-COUNT', msg, `第 ${h.line} 行：${h.text}`);
  }
}
if (rigor !== 'Lite' && h3[11] && !/^####\s+12\.\d+\s+还没定/m.test(sectionAt(dBody, h3[11]))) {
  R('D-OPEN', '第 12 节末尾缺「还没定、但会影响你的事」那一小节');
}

// 三条硬规矩：正文里不许出现（名词对照那节豁免标识符；数值没有豁免）
const gloss = h3[9] ? { from: h3[9].line, to: h3[9].endLine } : null;
const proseAll = proseLines(dBody);
const proseNoGloss = gloss ? proseAll.filter((l) => l.line <= gloss.from || l.line >= gloss.to) : proseAll;
const idHits = scan(proseNoGloss, [...IMPL_PATTERNS, ...DIGEST_ID_PATTERNS]);
if (idHits.length) R('D-IDENT', `正文 ${idHits.length} 处系统编号 / 类名 / 路径 / 代号（只有「名词对照」那节可以放）`, sample(idHits));
const skipHits = scan(proseAll.map((l) => ({ ...l, text: l.text.replace(/具体数值见规则表/g, '') })), SKIP_PATTERNS);
if (skipHits.length) R('D-SKIP', `正文 ${skipHits.length} 处「详见 / 见下文 / 见 7.1」这类省略（唯一允许的是「具体数值见规则表」）`, sample(skipHits));
const numHits = scan(proseAll.map((l) => ({ ...l, text: l.text.replace(/第\s*\d+\s*(节|条|句|步)/g, '') })), NUM_PATTERNS);
nums.digestNumberHits = numHits.length;
if (numHits.length) Y('D-NUMS', `正文 ${numHits.length} 处数字 / 公式 —— 结构常数（「四个格子」）还是旋钮数值，要人判`, sample(numHits, 8));
if (/<svg[\s>]/i.test(stripFences(dBody))) R('D-RAWSVG', '围栏外面有 <svg> —— 客户端会把它转义成一屏尖括号');

// 排版：黄
const paras = paragraphs(dBody);
nums.digestParagraphs = paras.length;
const longP = paras.filter((p) => p.lines > 6);
if (longP.length) Y('D-LONGPARA', `${longP.length} 段超过六行（一段一件事，拆不动就是两件事）`, longP.slice(0, 3).map((p) => `第 ${p.line} 行`).join('，'));
nums.digestBoldStartRatio = paras.length ? Number((paras.filter((p) => p.bold).length / paras.length).toFixed(2)) : 0;
for (const h of h3) {
  const n = paragraphs(sectionAt(dBody, h)).length;
  const hasSub = dH.some((x) => x.depth === 4 && x.line > h.line && x.line < h.endLine);
  if (n > 10 && !hasSub) Y('D-WALL', `「${h.text}」有 ${n} 段却没有 #### 小节`, `第 ${h.line} 行`);
}

// 图：数字 + 颜色
const fences = [...dBody.matchAll(/^```(mermaid|svg)[^\n]*\n([\s\S]*?)^```/gm)].map((m) => ({ lang: m[1], code: m[2] }));
nums.mermaid = fences.filter((f) => f.lang === 'mermaid').length;
nums.svg = fences.filter((f) => f.lang === 'svg').length;
let dropped = 0;
let strip = null;
try {
  const drawing = await import(pathToFileURL(path.join(UI, 'app', 'src', 'lib', 'drawing.ts')).href);
  strip = drawing.stripMermaidColors;
} catch { notes.push('没借到客户端的 stripMermaidColors，mermaid 里写死的颜色按正则数的'); }
for (const f of fences) {
  if (f.lang === 'mermaid') {
    dropped += strip ? strip(f.code).dropped : (f.code.match(/^\s*(style|classDef|linkStyle)\b.*(#[0-9a-fA-F]{3,8}|fill:|stroke:)/gm) ?? []).length;
  } else {
    dropped += (f.code.match(/\b(fill|stroke)="#|\bstyle=|<style\b/g) ?? []).length;
    if (!/<title[\s>]/.test(f.code)) R('D-SVGTITLE', '图解没有 <title> —— 它是图注，也是读屏念的名字');
  }
}
nums.hardcodedColors = dropped;
if (dropped) Y('D-COLORS', `图里 ${dropped} 处写死的颜色 / 样式，客户端会拿掉并提示 —— 颜色要用词表里的名字`);
if (nums.svg) Y('D-SVG', `有 ${nums.svg} 张 \`\`\`svg 图解 —— 体力系统没有空间内容，看看是不是硬塞的`);
notes.push('「讲位置的小节有没有图解」这篇不适用（体力没有空间内容）；倒过来看，出现 ```svg 多半是硬塞的');

nums.digestBytes = Buffer.byteLength(dBody, 'utf8');
nums.digestChars = dBody.replace(/\s/g, '').length;
finish();

// ── 输出 ──────────────────────────────────────────────────────────────────
function finish() {
  const out = { project: projectDir, gdd: GDD_FILE, rigor, borrowedClientJudge: borrowed, red, yellow, nums, notes };
  console.log(`\n${GDD_FILE} · ${rigor ?? '档位未知'} · 红 ${red.length} · 黄 ${yellow.length}`);
  for (const r of red) console.log(`  🔴 ${r.code}  ${r.msg}${r.where ? `\n      ${r.where}` : ''}`);
  for (const y of yellow) console.log(`  🟡 ${y.code}  ${y.msg}${y.where ? `\n      ${y.where}` : ''}`);
  console.log('  数字 ' + Object.entries(nums).map(([k, v]) => `${k}=${v}`).join(' · '));
  for (const n of notes) console.log(`  ℹ ${n}`);
  if (OUT) { fs.mkdirSync(path.dirname(path.resolve(OUT)), { recursive: true }); fs.writeFileSync(OUT, JSON.stringify(out, null, 2) + '\n'); }
  process.exit(0);
}

// ── 解析小工具 ────────────────────────────────────────────────────────────
function padToFile(file, body) {
  const b = String(body).replace(/\r\n/g, '\n');
  const full = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n') : b;
  const offset = Math.max(0, full.split('\n').length - b.split('\n').length);
  return '\n'.repeat(offset) + b;
}
function norm(s) { return s.replace(/\s+/g, ' ').replace(/,/g, '，').trim(); }
function stripFences(md) { return md.replace(/^```[\s\S]*?^```[^\n]*$/gm, ''); }
function headings(md, depths) {
  const want = Array.isArray(depths) ? depths : [depths];
  const lines = md.split('\n');
  const out = [];
  let inFence = false;
  lines.forEach((l, i) => {
    if (/^```/.test(l)) { inFence = !inFence; return; }
    if (inFence) return;
    const m = /^(#{1,6})\s+(.+?)\s*$/.exec(l);
    if (m && want.includes(m[1].length)) out.push({ depth: m[1].length, text: m[2], line: i + 1 });
  });
  out.forEach((h, i) => {
    const next = out.slice(i + 1).find((x) => x.depth <= h.depth);
    h.endLine = next ? next.line : lines.length + 1;
  });
  return out;
}
function sectionAt(md, h) { return md.split('\n').slice(h.line, h.endLine - 1).join('\n'); }
function sectionBody(md, depth, re) {
  const h = headings(md, depth).find((x) => re.test(x.text));
  return h ? sectionAt(md, h) : null;
}
function proseLines(md) {
  const out = [];
  let inFence = false;
  md.split('\n').forEach((l, i) => {
    if (/^```/.test(l)) { inFence = !inFence; return; }
    if (inFence || /^#{1,6}\s/.test(l)) return;
    out.push({ line: i + 1, text: l });
  });
  return out;
}
function scan(lines, patterns) {
  const hits = [];
  for (const { line, text } of lines) {
    for (const { code, re } of patterns) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(text))) hits.push({ line, code, hit: m[0] });
    }
  }
  return hits;
}
function sample(hits, n = 5) { return hits.slice(0, n).map((h) => `第 ${h.line} 行 ${h.code}「${h.hit}」`).join('；') + (hits.length > n ? ` …共 ${hits.length}` : ''); }
function listItems(body) {
  let inFence = false, n = 0;
  for (const l of body.split('\n')) {
    if (/^```/.test(l)) { inFence = !inFence; continue; }
    if (!inFence && /^([-*+]|\d+\.)\s+/.test(l)) n += 1;
  }
  return n;
}
function tableRows(body) {
  const rows = body.split('\n').filter((l) => /^\|/.test(l.trim()) && !/^\|[\s\-:|]+\|$/.test(l.trim()));
  return Math.max(0, rows.length - 1);
}
function paragraphs(md) {
  const out = [];
  let buf = [], start = 0, inFence = false;
  const flush = () => { if (buf.length) out.push({ line: start, lines: buf.length, bold: /^\*\*/.test(buf[0]) }); buf = []; };
  md.split('\n').forEach((l, i) => {
    if (/^```/.test(l)) { flush(); inFence = !inFence; return; }
    if (inFence) return;
    const t = l.trim();
    if (!t || /^#{1,6}\s/.test(t) || /^([-*+]|\d+\.)\s+/.test(t) || /^\|/.test(t) || /^>/.test(t)) { flush(); return; }
    if (!buf.length) start = i + 1;
    buf.push(t);
  });
  flush();
  return out;
}
function countInTitle(text) {
  const m = /(\d+|[零一二两三四五六七八九十]+)\s*(个|件|条|种|步|句|类|样|道)/.exec(text.replace(/^\d+(\.\d+)?\s+/, ''));
  if (!m) return null;
  const s = m[1];
  let n;
  if (/^\d+$/.test(s)) n = Number(s);
  else if (s === '十') n = 10;
  else {
    const [a, b] = s.split('十');
    n = b === undefined ? (CN[a] ?? null) : (a ? CN[a] : 1) * 10 + (b ? CN[b] : 0);
  }
  return n === 1 ? null : n; // 「一个完整的例子」不是在报数
}
function readHeaderBlock(src) {
  const extra = {};
  for (const l of src.split('\n').slice(1, 12)) {
    const m = /^>\s*\*\*(.+?)\*\*\s*[:：]\s*(.*)$/.exec(l.trim());
    if (m) extra[m[1].trim()] = m[2].trim();
  }
  return extra;
}
function readOwn(dir, file) {
  const p = path.join(dir, 'design', 'gdd', file);
  if (!fs.existsSync(p)) { R('G-READ', `读不到 ${p}`); return null; }
  const src = fs.readFileSync(p, 'utf8').replace(/\r\n/g, '\n');
  const extra = readHeaderBlock(src);
  const bodyStart = src.split('\n').findIndex((l, i) => i > 0 && /^##\s/.test(l));
  const dp = path.join(dir, 'design', 'digest', file);
  let digest = null;
  if (fs.existsSync(dp)) {
    const ds = fs.readFileSync(dp, 'utf8').replace(/\r\n/g, '\n');
    const dx = readHeaderBlock(ds);
    const basedOn = dx['写于文档的最后更新'] ?? null;
    const updated = extra['Last Updated'] ?? extra['最后更新'] ?? null;
    const dStart = ds.split('\n').findIndex((l, i) => i > 0 && /^###?\s/.test(l));
    digest = { body: ds.split('\n').slice(dStart < 0 ? 1 : dStart).join('\n'), basedOn, gddUpdated: updated, stale: basedOn && updated ? basedOn.trim() !== updated.trim() : null };
  }
  return { ok: true, fields: { rigor: extra['Rigor'], status: extra['Status'], updated: extra['Last Updated'] }, extra, body: src.split('\n').slice(bodyStart < 0 ? 1 : bodyStart).join('\n'), digest, digestInline: /^##\s+读本/m.test(src) };
}
