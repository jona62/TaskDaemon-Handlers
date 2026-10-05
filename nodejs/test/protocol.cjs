const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const { test } = require('node:test');

test('runner flushes responses, preserves attempts and continues after handler errors', async () => {
  const sdk = path.resolve(__dirname, '../dist/index.js');
  const process = spawn(global.process.execPath, ['-e', `
    const { run, success, error } = require(${JSON.stringify(sdk)});
    run(async task => {
      if (task.task_type === 'retry') return error('try again', true);
      if (task.task_type === 'exception') throw new Error('failed');
      return success({ task_id: task.task_id, attempt: task.attempt });
    });
  `]);
  let stderr = '';
  process.stderr.on('data', data => { stderr += data; });
  let buffer = '';
  const responses = [];
  const readers = [];
  process.stdout.on('data', data => {
    buffer += data;
    let newline;
    while ((newline = buffer.indexOf('\n')) >= 0) {
      const response = JSON.parse(buffer.slice(0, newline));
      buffer = buffer.slice(newline + 1);
      if (readers.length) readers.shift()(response);
      else responses.push(response);
    }
  });
  const read = () => new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('response was not flushed')), 3000);
    const receive = value => { clearTimeout(timeout); resolve(value); };
    if (responses.length) receive(responses.shift());
    else readers.push(receive);
  });
  try {
    for (const [index, type] of ['echo', 'retry', 'exception', 'echo'].entries()) {
      process.stdin.write(JSON.stringify({ task_id: String(index + 1), task_type: type, task_data: {}, attempt: index + 1 }) + '\n');
      const response = await read();
      if (type === 'echo') assert.deepEqual(response, { status: 'success', result: { task_id: String(index + 1), attempt: index + 1 } });
      else if (type === 'retry') assert.deepEqual(response, { status: 'error', error: 'try again', retryable: true });
      else assert.deepEqual(response, { status: 'error', error: 'Error: failed', retryable: false });
    }
    const exited = new Promise(resolve => process.once('exit', resolve));
    process.stdin.end();
    assert.equal(await exited, 0);
    assert.equal(stderr, '');
  } finally {
    if (process.exitCode === null) process.kill();
  }
});
