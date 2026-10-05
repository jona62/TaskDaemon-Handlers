const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

if (process.argv.length !== 3) {
  throw new Error('Usage: node scripts/check-artifact.cjs ARCHIVE.tgz');
}
const archive = path.resolve(process.argv[2]);
const project = path.resolve(__dirname, '..');
const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'taskdaemon-node-artifact-'));
const options = { cwd: directory, stdio: 'inherit' };

try {
  fs.writeFileSync(path.join(directory, 'package.json'), JSON.stringify({
    name: 'taskdaemon-installed-smoke', version: '1.0.0', private: true,
  }));
  execFileSync('npm', ['install', '--omit=dev', '--ignore-scripts', '--no-audit', '--no-fund', archive], options);
  const installed = JSON.parse(fs.readFileSync(path.join(directory, 'node_modules/@taskdaemon/handler/package.json'), 'utf8'));
  const source = JSON.parse(fs.readFileSync(path.join(project, 'package.json'), 'utf8'));
  assert.equal(installed.name, '@taskdaemon/handler');
  assert.equal(installed.version, source.version);
  const test = fs.readFileSync(path.join(project, 'test/protocol.cjs'), 'utf8');
  const original = "const sdk = path.resolve(__dirname, '../dist/index.js');";
  assert.ok(test.includes(original));
  fs.writeFileSync(path.join(directory, 'protocol.cjs'), test.replace(original, "const sdk = require.resolve('@taskdaemon/handler');"));
  execFileSync(process.execPath, ['--test', 'protocol.cjs'], options);
  execFileSync(process.execPath, ['--input-type=module', '-e', `
    import { run, success, error } from '@taskdaemon/handler';
    if (typeof run !== 'function' || success(1).result !== 1 || !error('x', true).retryable) {
      throw new Error('ESM exports failed');
    }
  `], options);
  fs.writeFileSync(path.join(directory, 'consumer.ts'), `
    import { run, success, error, Task, Handler, Result } from '@taskdaemon/handler';
    const handler: Handler = (task: Task): Result => success({ id: task.task_id, attempt: task.attempt });
    run(handler);
    error('try again', true);
  `);
  execFileSync(process.execPath, [path.join(project, 'node_modules/typescript/bin/tsc'),
    '--strict', '--target', 'ES2020', '--module', 'commonjs', '--noEmit', 'consumer.ts'], options);
  console.log('Installed npm archive passed protocol, CommonJS, ESM, and TypeScript checks.');
} finally {
  fs.rmSync(directory, { recursive: true, force: true });
}
