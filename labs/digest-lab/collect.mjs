/**
 * 跑完一次，把产物收进 runs/<run-id>/，顺手跑尺子和客户端截图。
 *
 *   node labs/digest-lab/collect.mjs <run-id> --project <实验项目目录> [--gdd stamina.md] [--ui <XGameHarnessUI 目录>] [--shots]
 *
 * 收：gdd.md · digest.md · systems-index.md（跑完之后的样子）· session-state · lint.json / lint.txt
 *     · notes.md（模板，已有就不动）· shots/dark · shots/light（要 --shots，而且 UI 仓要先构建过）
 *
 * **不替你抓对话。** 评审（P3）和答题（P4）的原文要手动拷进 review.md / qa.md。
 * 最后印一行 RUNLOG 的骨架，红黄和图数已经填好，剩下的手填。
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const args = process.argv.slice(2);
const runId = args[0] && !args[0].startsWith('--') ? args[0] : null;
const opt = (k, d = null) => { const i = args.indexOf(k); return i >= 0 && args[i + 1] !== undefined ? args[i + 1] : d; };
const project = opt('--project') ? path.resolve(opt('--project')) : null;
const GDD_FILE = opt('--gdd', 'stamina.md');
const UI = path.resolve(opt('--ui', path.join(ROOT, '..', 'XGameHarnessUI')));
const SHOTS = args.includes('--shots');
if (!runId || !project) {
  console.error('用法：node labs/digest-lab/collect.mjs <run-id> --project <实验项目目录> [--gdd stamina.md] [--ui <UI 目录>] [--shots]');
  process.exit(2);
}
if (!/^r\d{2}-/.test(runId)) console.warn(`⚠ run-id 不像 r01-B0-claude-main-0916a 那个样子：${runId}`);

const runDir = path.join(HERE, 'runs', runId);
fs.mkdirSync(runDir, { recursive: true });
const copy = (rel, as) => {
  const src = path.join(project, rel);
  if (!fs.existsSync(src)) { console.log(`  没有 ${rel}`); return false; }
  fs.copyFileSync(src, path.join(runDir, as));
  console.log(`  收了 ${rel} → ${as}`);
  return true;
};
console.log(`收进 ${runDir}`);
const gotGdd = copy(`design/gdd/${GDD_FILE}`, 'gdd.md');
const gotDigest = copy(`design/digest/${GDD_FILE}`, 'digest.md');
copy('design/gdd/systems-index.md', 'systems-index.md');
const ssDir = path.join(project, 'team', 'session-state');
if (fs.existsSync(ssDir)) {
  for (const id of fs.readdirSync(ssDir)) copy(`team/session-state/${id}/active.md`, `session-state-${id}.md`);
}
const notes = path.join(runDir, 'notes.md');
if (!fs.existsSync(notes)) {
  fs.writeFileSync(notes, [
    `# ${runId} —— 跑的人的记录`,
    '',
    '## 变量',
    '',
    '- 引擎：',
    '- 执笔：主 agent / systems-designer / game-designer',
    '- 读本路径：design-system 内嵌 / 单独 write-digest',
    `- harness：${sha()}`,
    '',
    '## 它选了什么（answers.md 要求记的）',
    '',
    '- 2f 第一版前提：',
    '- 建议档位：',
    '- 各节选项：',
    '- 想开的子 agent：',
    '',
    '## 跑的人说了话的地方（只允许两种）',
    '',
    '- ',
    '',
    '## 在客户端里读完读本的一句话',
    '',
    '- ',
    '',
    '## 花费 · 时间',
    '',
    '- ',
    '',
  ].join('\n'));
  console.log('  写了 notes.md 模板');
}

// 尺子
let lint = null;
if (gotGdd) {
  const r = spawnSync(process.execPath, [path.join(HERE, 'lint.mjs'), project, '--gdd', GDD_FILE, '--ui', UI, '--out', path.join(runDir, 'lint.json')], { encoding: 'utf8' });
  fs.writeFileSync(path.join(runDir, 'lint.txt'), (r.stdout ?? '') + (r.stderr ?? ''));
  process.stdout.write(r.stdout ?? '');
  if (r.stderr) process.stderr.write(r.stderr);
  try { lint = JSON.parse(fs.readFileSync(path.join(runDir, 'lint.json'), 'utf8')); } catch { /* 尺子没跑成，下面骨架里留空 */ }
}

// 客户端截图（docshot 是 UI 仓的工具，它自己起边车 + 无头 Chrome，全在临时目录）
let drawn = null;
if (SHOTS && gotGdd) {
  const dist = path.join(UI, 'app', 'dist', 'index.html');
  if (!fs.existsSync(dist)) {
    console.log(`  截图跳过：${dist} 不在 —— 先 cd app; node node_modules/vite/bin/vite.js build`);
  } else {
    drawn = { total: 0, ok: 0 };
    for (const [theme, port] of [['dark', 9420], ['light', 9421]]) {
      const out = path.join(runDir, 'shots', theme);
      fs.mkdirSync(out, { recursive: true });
      console.log(`  截图 ${theme}…（约一分钟）`);
      const r = spawnSync(process.execPath, [path.join(UI, 'sidecar', 'tools', 'docshot.mjs'), path.join(project, 'design', 'gdd', GDD_FILE), out, theme, String(port)], { encoding: 'utf8', cwd: UI, timeout: 240000 });
      const log = (r.stdout ?? '') + (r.stderr ?? '');
      fs.writeFileSync(path.join(runDir, 'shots', `${theme}.txt`), log);
      const total = (log.match(/一共 (\d+) 张图/) ?? [])[1];
      const ok = (log.match(/画出来了/g) ?? []).length;
      if (theme === 'dark' && total !== undefined) { drawn.total = Number(total); drawn.ok = ok; }
      console.log(`  ${theme}：${total ?? '?'} 张图，${ok} 张画出来了${/提示：没有/.test(log) ? '，读本没有提示' : ''}`);
    }
  }
}

// RUNLOG 骨架
const figs = lint ? `${(lint.nums.mermaid ?? 0) + (lint.nums.svg ?? 0)}` : '?';
const drawnCol = drawn ? `${drawn.ok}/${drawn.total}` : `?/${figs}`;
console.log('\nRUNLOG 那一行（拷去手填剩下的）：');
console.log(`| ${runId} | — | ${sha()} | ${lint ? lint.red.length : '?'} | ${lint ? lint.yellow.length : '?'} | ${drawnCol} | ? / ? / ? | ? | ? · ? | ${gotDigest ? '' : '（没有读本）'} |`);

function sha() { try { return execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: ROOT, encoding: 'utf8' }).trim(); } catch { return '?'; } }
