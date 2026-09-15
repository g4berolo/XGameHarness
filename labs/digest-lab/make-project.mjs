/**
 * 把实验项目铺出来 —— 每次跑之前都重建，两次跑的起点是同一批字节。
 *
 *   node labs/digest-lab/make-project.mjs <目标目录>
 *       生成 / 重置实验项目（fixtures + 当前 harness 的 rules 和 stage 模板 + git init + seed 提交）
 *
 *   node labs/digest-lab/make-project.mjs <目标目录> --qa <runs/某次目录> [--mode digest|gdd]
 *       生成只有一份文档的答题项目：默认只放 design/digest/stamina.md（只读读本答题），
 *       `--mode gdd` 只放 design/gdd/stamina.md（对照组）。题目一起放进去，答案不放。
 *
 * 安全：目标目录已存在时，只有里面有 `.digest-lab` 标记才会被整个删掉重建；
 * 没有标记就拒绝 —— 这个脚本唯一能造成真损失的地方就是删错目录。
 */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..', '..');
const PLUGIN = path.join(ROOT, 'plugins', 'game-studio-core');
const FIXTURES = path.join(HERE, 'fixtures');
const MARK = '.digest-lab';
const GDD_FILE = 'stamina.md';

const args = process.argv.slice(2);
const target = args[0] && !args[0].startsWith('--') ? path.resolve(args[0]) : null;
const opt = (k, d = null) => {
  const i = args.indexOf(k);
  return i >= 0 && args[i + 1] !== undefined ? args[i + 1] : d;
};
if (!target) {
  console.error('用法：node labs/digest-lab/make-project.mjs <目标目录> [--qa <runs/某次目录> [--mode digest|gdd]]');
  process.exit(2);
}

const git = (cwd, ...a) => execFileSync('git', a, { cwd, stdio: 'pipe', encoding: 'utf8' }).trim();
const harnessSha = (() => { try { return git(ROOT, 'rev-parse', '--short', 'HEAD'); } catch { return 'unknown'; } })();

// ── 目标目录：有标记才敢删 ─────────────────────────────────────────────────
if (fs.existsSync(target)) {
  if (!fs.existsSync(path.join(target, MARK))) {
    console.error(`拒绝：${target} 已存在，而且里面没有 ${MARK} 标记 —— 它不是这个脚本建的，不删。`);
    process.exit(1);
  }
  fs.rmSync(target, { recursive: true, force: true });
  console.log(`已删掉上一次的 ${target}`);
}
fs.mkdirSync(target, { recursive: true });

const qaFrom = opt('--qa');
if (qaFrom) {
  makeQa(path.resolve(qaFrom), opt('--mode', 'digest'));
} else {
  makeLab();
}

// ── 实验项目 ────────────────────────────────────────────────────────────────
function makeLab() {
  fs.cpSync(FIXTURES, target, { recursive: true });

  // rules 和 stage 模板从当前 harness 拿，不放夹具里 —— 夹具里那份迟早会旧
  const rulesDir = path.join(target, '.claude', 'rules');
  fs.mkdirSync(rulesDir, { recursive: true });
  for (const f of fs.readdirSync(path.join(PLUGIN, 'rules'))) {
    if (f.endsWith('.md')) fs.copyFileSync(path.join(PLUGIN, 'rules', f), path.join(rulesDir, f));
  }
  fs.mkdirSync(path.join(target, 'plan'), { recursive: true });
  fs.copyFileSync(path.join(PLUGIN, 'docs', 'templates', 'stage.md'), path.join(target, 'plan', 'stage.md'));
  fs.mkdirSync(path.join(target, 'design', 'digest'), { recursive: true });
  fs.writeFileSync(path.join(target, 'design', 'digest', '.gitkeep'), '');

  const cfgFile = path.join(target, '.claude', 'harness-config.json');
  const cfg = JSON.parse(fs.readFileSync(cfgFile, 'utf8'));
  cfg.syncedHarnessCommit = harnessSha;
  fs.writeFileSync(cfgFile, JSON.stringify(cfg, null, 2) + '\n');

  writeMark({ kind: 'lab' });
  seedGit(`lab: seed (harness ${harnessSha})`);

  console.log(`实验项目已铺好：${target}`);
  console.log(`  harness ${harnessSha} · rules ${fs.readdirSync(rulesDir).join(', ')}`);
  console.log(`  下一步：客户端本地模式打开它，新开对话，贴 brief/P1-design-system.md`);
}

// ── 答题项目：只有一份文档 ─────────────────────────────────────────────────
function makeQa(runDir, mode) {
  if (!['digest', 'gdd'].includes(mode)) {
    console.error('--mode 只认 digest 或 gdd');
    process.exit(2);
  }
  const src = path.join(runDir, mode === 'digest' ? 'digest.md' : 'gdd.md');
  if (!fs.existsSync(src)) {
    console.error(`读不到 ${src} —— 先跑 collect.mjs 把这次的产物收进 runs/`);
    process.exit(1);
  }
  const dest = path.join(target, 'design', mode === 'digest' ? 'digest' : 'gdd', GDD_FILE);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
  fs.mkdirSync(path.join(target, 'qa'), { recursive: true });
  fs.copyFileSync(path.join(HERE, 'qa', 'questions.md'), path.join(target, 'qa', 'questions.md'));
  fs.writeFileSync(path.join(target, 'CLAUDE.md'), [
    '# 答题项目（读本实验室）',
    '',
    `这个目录里只有一份文档（\`design/${mode === 'digest' ? 'digest' : 'gdd'}/${GDD_FILE}\`）和一份题目（\`qa/questions.md\`）。`,
    '**只读那份文档作答。** 文档里没说的写「读本没说」，不许用常识补，不要问人。',
    '',
    '默认中文输出。',
    '',
  ].join('\n'));
  fs.writeFileSync(path.join(target, '.gitignore'), `${MARK}\n`);

  writeMark({ kind: 'qa', mode, from: runDir });
  seedGit(`qa: ${mode} from ${path.basename(runDir)}`);

  console.log(`答题项目已铺好：${target}（只有 ${mode} 那一份）`);
  console.log(`  下一步：客户端本地模式打开它，新开对话，贴 brief/P4-qa.md`);
}

function writeMark(extra) {
  fs.writeFileSync(path.join(target, MARK), JSON.stringify({ madeAt: new Date().toISOString(), harness: harnessSha, ...extra }, null, 2) + '\n');
}

function seedGit(msg) {
  git(target, 'init', '-q', '-b', 'main');
  // 身份跟 team.json 对得上，子 agent 才认得出是谁（它拿 git config user.name 去比）
  let name = '', email = '';
  try { name = git(ROOT, 'config', 'user.name'); email = git(ROOT, 'config', 'user.email'); } catch { /* 下面兜 */ }
  if (!name) { name = 'g4berolo'; email = 'gaberzxy@163.com'; }
  git(target, 'config', 'user.name', name);
  git(target, 'config', 'user.email', email);
  git(target, 'config', 'core.autocrlf', 'false');
  git(target, 'add', '-A');
  git(target, 'commit', '-qm', msg);
}
